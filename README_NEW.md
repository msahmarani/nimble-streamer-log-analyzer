# 🚀 Nimble Streamer Log Analyzer

A powerful Python tool for analyzing large Nimble Streamer log files with web interface and comprehensive reporting.

## ✨ Key Features

- **Multi-Format Support**: JSON logs, traditional HTTP access logs, and Nimble application logs
- **Large File Processing**: Efficiently handles 100+ MB files with chunked reading
- **Web Interface**: User-friendly Dash web GUI for easy log analysis
- **Comprehensive Reports**: CSV, Excel files with charts and visualizations
- **Smart Detection**: Automatically detects log format and optimizes parsing
- **Memory Efficient**: Processes large files without memory issues

## 🎯 Supported Log Formats

### 1. JSON Format
```json
{"timestamp": "2024-07-22T14:30:00Z", "client_ip": "192.168.1.10", "stream_name": "my_stream", "protocol": "HLS", "status": "success"}
```

### 2. Traditional HTTP Access Logs
```
192.168.1.10 - - [22/Jul/2024:14:30:00 +0000] "GET /stream.m3u8 HTTP/1.1" 200 1234
```

### 3. Nimble Application Logs
```
[2024-07-22 14:30:00.123 12345-67890] [StreamManager] Info: Stream started successfully
```

## 🚀 Quick Start

### 1. Setup Environment
```cmd
# Create virtual environment
python -m venv .venv

# Install dependencies
.venv\Scripts\pip install -r requirements.txt
```

### 2. Start Web GUI
```cmd
# Double-click or run:
start_web_gui.bat
```
Then open: http://127.0.0.1:8050

### 3. Alternative - Command Line
```cmd
.venv\Scripts\python.exe json_log_analyzer.py
```

## 📊 Output Features

- **Real-time Analysis**: Progress tracking with live statistics
- **Visual Reports**: Timeline graphs, hourly distributions, status code analysis
- **Export Options**: CSV, Excel with charts, PNG visualizations
- **Detailed Insights**: IP analysis, error patterns, performance metrics

## 🛠 Core Components

- `json_log_analyzer.py` - Enhanced multi-format analyzer
- `nimble_app_log_parser.py` - Specialized Nimble application log parser
- `web_gui.py` - Dash web interface
- `start_web_gui.bat` - Easy launcher with threading fixes

## 📋 Requirements

- Python 3.7+
- pandas, matplotlib, plotly, dash
- openpyxl, tqdm
- See `requirements.txt` for complete list

## 🎉 Ready to Analyze!

Upload your Nimble Streamer log files and get instant insights with smart format detection and comprehensive reporting.
