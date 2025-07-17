<h1 align="center">🛡️ Alert Filtering and Anomaly Detection Tool</h1>
<hr/>

<h2>📄 Project Motivation</h2>
<p>
  The creation and design of this project were motivated by a white paper I wrote at NJIT addressing a common problem among security analysts was the work fatigue/burnout of SOC analysts due to things like repetitive tasks and having to deal with lots of false positives. Top suggested solutions were to implement automation to streamline workflows and reduce cognitive overload. This tool does just that by:
</p>
<ul>
  <li>Filtering the amount of logs an analyst has to look at and returning the most important logs that may be needed to investigate an incident.</li>
  <li>Showing the anomalies detected throughout the logs and removing duplicate entries.</li>
  <li>Providing easy tuning for false positives, anomaly detection, and log filtering rules; making this very <strong>scalable</strong> and most importantly reducing the repetitive tasks like manual triaging, log sorting and dealing with false positives.</li>
</ul>
<hr/>

<h2>🎥 Demo & Web App</h2>
  <p>
    Explore the Alert Filtering and Anomaly Detection Tool in action:
  </p>
  <ul>
    <li>
      <a href="https://youtu.be/y83ytWBb1W8" >▶️ Watch the Demo on YouTube</a>
    </li>
    <li>
      <a href="https://logsentry.onrender.com" >🌐 Visit the Live Website</a>
    </li>
  </ul>
</div>
<hr/>
<h2>📘 Project Overview</h2>

<p>
This project is a web-based log anomaly detection tool designed for security and operations use cases. It allows users to upload log files in various formats (CSV, JSON, cleartext), processes them to:
</p>

<ul>
  <li>Remove duplicate entries.</li>
  <li>Detect anomalous behavior (e.g., <code>ERROR</code>/<code>CRITICAL</code> log levels).</li>
  <li>Tune out false positives using customizable rules.</li>
  <li>Detect and flag suspicious patterns, such as 3 consecutive failed login attempts for the same user.</li>
</ul>

<p>
The <code>app.py</code> script is the core of this log anomaly detection web application tool, and it is built using Flask. It defines two main routes: the root route (<code>/</code>) renders the upload form, and the <code>/upload</code> route handles file uploads and log processing.
</p>

<p>
When a user uploads a log file (CSV, JSON, or cleartext), the app detects the file type, parses it into a pandas DataFrame, and removes duplicate entries. Uploads also get logged into the uploads folder.
</p>

<p>
It then performs anomaly detection by flagging entries only with log levels of <code>ERROR</code> or <code>CRITICAL</code>, but filters out known false positives based on a hardcoded list of (message, user) pairs. This can be configured by adding or removing certain log levels to filter.
</p>

<p>
Additionally, the script analyzes the logs for each user to detect and flag any occurrence of three consecutive failed login attempts, regardless of false positive rules. This can also be easily configured, allowing more or less failed logins to flag as an anomaly.
</p>

<p>
The results—including the filtered log table, detected anomalies, and the log format used—are rendered using external HTML templates, allowing for a clean separation of logic and presentation. The app is structured for extensibility, with clear functions for parsing, filtering, and anomaly detection, and is ready for further enhancements such as advanced rules or user-driven configurations.
</p>

<hr/>
