# 🚀 Nimble Streamer Log Analyzer v2.0

A powerful Python tool for analyzing large Nimble Streamer log files with advanced web interface and comprehensive reporting capabilities.

## ✨ Key Features

- **Multi-Format Support**: JSON logs, traditional HTTP access logs, and Nimble application logs
- **Large File Processing**: Efficiently handles 130+ MB files with chunked reading and progress tracking
- **Enhanced Web Interface**: Feature-rich Dash web GUI with 8 specialized analysis tabs
- **HTTP Error Analysis**: **NEW!** Extract and analyze HTTP error codes with server IP and stream name detection
- **IP & Stream Extraction**: **NEW!** Parse URLs like `http://38.46.143.164:8081/stream/cinecanal/playlist.m3u8` to extract server IPs and stream names
- **Comprehensive Reports**: CSV, Excel files with multi-sheet reports, charts and PNG visualizations
- **Smart Detection**: Automatically detects log format and optimizes parsing
- **Memory Efficient**: Processes large files without memory issues using pandas chunking
- **Advanced Filtering**: Date range, status codes, protocols, IP addresses, and stream filtering

## 🎯 Supported Log Formats

### 1. JSON Format (Nimble Streamer JSON Logs)
```json
{"timestamp": "2024-07-22T14:30:00Z", "client_ip": "192.168.1.10", "stream_name": "my_stream", "protocol": "HLS", "status": "success"}
```

### 2. Traditional HTTP Access Logs
```
192.168.1.10 - - [22/Jul/2024:14:30:00 +0000] "GET /stream.m3u8 HTTP/1.1" 200 1234
```

### 3. Nimble Application Logs (with HTTP Error Detection)
```
[2024-07-22 14:30:00.123 12345-67890] [StreamManager] E: http error code=404 for url='http://SERVER_IP:8081/stream/cinecanal/playlist.m3u8' hls camera s=
```
**NEW!** Extracts: Error code `404`, Server IP `SERVER_IP`, Stream name `cinecanal`

## � Web Interface Analysis Tabs

### 📊 Summary Report
- Total entries and parsing statistics
- Status code distribution with percentages
- Parse success rate metrics

### 📈 Time Analysis  
- Hourly request distribution charts
- Daily timeline visualization
- Peak usage patterns

### 🌐 IP Analysis
- Top IP addresses by request count
- Geographic insights and user engagement metrics
- IP-based filtering and analysis

### 🚨 HTTP Errors & Streaming (**NEW!**)
- **HTTP Error Code Analysis**: Complete breakdown of 4xx/5xx errors
- **Server IP Extraction**: Identifies server IPs from error URLs
- **Stream Name Detection**: Extracts stream names like "cinecanal" from URLs
- **Server:Stream Combinations**: Tracks which servers serve which streams
- **Error Timeline**: When errors occur by hour/day
- **Sample Error Messages**: Real examples with extracted data

### ❌ Error Analysis
- 4xx/5xx error distribution
- Error patterns by time
- Top error sources

### 📱 User Behavior
- Device type detection (Mobile/Desktop)
- Bandwidth usage patterns
- User engagement metrics

### 🎬 Content Performance
- Most requested content/streams
- Content success rates
- File type distribution

### 📋 Data Table
- Interactive data browser with filtering
- Sort and search capabilities
- Export functionality

## �🚀 Quick Start

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

- **Real-time Analysis**: Progress tracking with live statistics and memory-efficient processing
- **Visual Reports**: Timeline graphs, hourly distributions, status code analysis, error trends
- **Export Options**: CSV, Excel with multiple sheets, PNG visualizations
- **Detailed Insights**: IP analysis, error patterns, streaming performance, server metrics
- **HTTP Error Intelligence**: **NEW!** Server IP and stream name extraction from error URLs
- **Advanced Filtering**: Filter by date range, status codes, protocols, IPs, and streams

## 🛠 Core Components

- `json_log_analyzer.py` - Enhanced multi-format analyzer with JSON support
- `nimble_app_log_parser.py` - **NEW!** Specialized parser for Nimble application logs with HTTP error extraction  
- `web_gui.py` - Feature-rich Dash web interface with 8 analysis tabs
- `log_analyzer.py` - Traditional log format analyzer
- `start_web_gui.bat` - Easy launcher with threading fixes and port detection

## 🆕 What's New in v2.0

- **HTTP Error Analysis**: Extract error codes, server IPs, and stream names from Nimble log messages
- **Enhanced Web GUI**: New "HTTP Errors & Streaming" tab with comprehensive analysis
- **URL Pattern Recognition**: Parse URLs like `http://SERVER_IP:PORT/stream/STREAM_NAME/playlist.m3u8`
- **Server:Stream Mapping**: Track which servers serve which streams
- **Improved Memory Handling**: Better chunked processing for 130MB+ files
- **Advanced Filtering**: Filter analysis results by multiple criteria

## 📋 Requirements

- Python 3.7+
- pandas, matplotlib, plotly, dash
- openpyxl, tqdm, regex
- See `requirements.txt` for complete list

## 📁 Project Structure

```
ns_log_analayzer/
├── web_gui.py                    # Main web interface with 8 analysis tabs
├── json_log_analyzer.py          # Multi-format log analyzer
├── nimble_app_log_parser.py      # NEW! Nimble app log parser with HTTP error extraction
├── log_analyzer.py               # Traditional log format analyzer  
├── requirements.txt              # Python dependencies
├── start_web_gui.bat            # Windows launcher
├── launch_web_gui.ps1           # PowerShell launcher
├── logs/                        # Upload log files here
└── reports/                     # Generated reports (CSV, Excel, PNG)
```

## 🎯 Use Cases

- **Server Monitoring**: Track HTTP errors and identify problematic streams
- **Performance Analysis**: Analyze request patterns and peak usage times
- **Troubleshooting**: Extract server IPs and stream names from error messages
- **Capacity Planning**: Understand traffic patterns and bandwidth usage
- **Content Performance**: Identify popular streams and content success rates

## 🎉 Ready to Analyze!

Upload your Nimble Streamer log files and get instant insights with smart format detection, HTTP error analysis, and comprehensive reporting including server IP and stream name extraction.
