from flask import Flask, request, render_template, redirect, url_for
import pandas as pd
import os
import json

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Hardcoded false positive filter: list of (message, user) tuples to ignore as anomalies
FALSE_POSITIVES = [
    ("Failed login", "bob"),  # Example: ignore failed login by bob
]

def parse_log_file(filepath, ext):
    if ext == '.csv':
        df = pd.read_csv(filepath)
        filetype = 'CSV'
    elif ext == '.json':
        # Try to read as list of dicts or line-delimited JSON
        with open(filepath, 'r', encoding='utf-8') as f:
            try:
                data = json.load(f)
                df = pd.DataFrame(data)
            except json.JSONDecodeError:
                # Try line-delimited JSON
                f.seek(0)
                lines = [json.loads(line) for line in f if line.strip()]
                df = pd.DataFrame(lines)
        filetype = 'JSON'
    elif ext in ['.log', '.txt']:
        # Assume space-separated: timestamp level message user
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = [line.strip() for line in f if line.strip()]
        # Split lines into columns
        rows = []
        for line in lines:
            parts = line.split(None, 3)  # Split into 4 parts max
            if len(parts) == 4:
                rows.append({
                    'timestamp': parts[0] + ' ' + parts[1],
                    'level': parts[2],
                    'message': parts[3].rsplit(' ', 1)[0],
                    'user': parts[3].rsplit(' ', 1)[-1],
                })
        df = pd.DataFrame(rows)
        filetype = 'Cleartext (space-separated)'
    else:
        raise ValueError('Unsupported file type')
    return df, filetype

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    file = request.files['logfile']
    if not file:
        return 'Please upload a log file.', 400
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in ['.csv', '.json', '.log', '.txt']:
        return 'Unsupported file type. Please upload a CSV, JSON, or cleartext log file.', 400
    filepath = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(filepath)
    try:
        df, filetype = parse_log_file(filepath, ext)
    except Exception as e:
        return f'Error parsing file: {e}', 400
    if df.empty:
        return 'No valid log entries found.', 400
    # Remove duplicates
    df_filtered = df.drop_duplicates()
    # Simple anomaly detection: flag rows where 'level' == 'ERROR' or 'CRITICAL'
    anomalies = df_filtered[df_filtered['level'].isin(['ERROR', 'CRITICAL'])]
    # False positive filtering
    def is_false_positive(row):
        return (row.get('message'), row.get('user')) in FALSE_POSITIVES
    anomalies_filtered = anomalies[~anomalies.apply(is_false_positive, axis=1)]
    anomaly_list = anomalies_filtered.to_dict('records')
    anomaly_msgs = [str(a) for a in anomaly_list]

    # --- New logic: Detect 3 consecutive failed logins for the same user ---
    # Sort by timestamp if possible
    if 'timestamp' in df_filtered.columns:
        try:
            df_filtered['timestamp'] = pd.to_datetime(df_filtered['timestamp'])
            df_sorted = df_filtered.sort_values('timestamp')
        except Exception:
            df_sorted = df_filtered
    else:
        df_sorted = df_filtered
    # For each user, look for 3 consecutive failed logins
    if all(col in df_sorted.columns for col in ['user', 'level', 'message', 'timestamp']):
        for user, group in df_sorted.groupby('user'):
            group = group.reset_index(drop=True)
            fail_mask = (group['level'] == 'ERROR') & (group['message'] == 'Failed login')
            # Find runs of 3 consecutive True in fail_mask
            for i in range(len(group) - 2):
                if fail_mask.iloc[i] and fail_mask.iloc[i+1] and fail_mask.iloc[i+2]:
                    times = [str(group.loc[i+j, 'timestamp']) for j in range(3)]
                    anomaly_msgs.append(f"User '{user}' had 3 consecutive failed logins at {', '.join(times)}")
                    # Optionally, skip overlapping runs
                    # break
    # --- End new logic ---

    return render_template(
        'results.html',
        columns=df_filtered.columns,
        rows=df_filtered.to_dict('records'),
        anomalies=anomaly_msgs,
        filetype=filetype
    )

if __name__ == '__main__':
    app.run(debug=True) 