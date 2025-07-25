# 🚀 Nimble Streamer Log Analyzer

A powerful Python tool for analyzing large Nimble Streamer log files with advanced web interface and comprehensive reporting capabilities.

## ✨ Key Features

- **Multi-Format Support**: JSON logs, traditional HTTP access logs, and Nimble application logs
- **Large File Processing**: Efficiently handles 130+ MB files with chunked reading and progress tracking
- **Enhanced Web Interface**: Feature-rich Dash web GUI with 8 specialized analysis tabs
- **HTTP Error Analysis**: Extract and analyze HTTP error codes with server IP and stream name detection
- **IP & Stream Extraction**: Parse URLs like `http://SERVER_IP:PORT/stream/STREAM_NAME/playlist.m3u8` to extract server IPs and stream names
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
Extracts: Error code `404`, Server IP `SERVER_IP`, Stream name `cinecanal`

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
- **NEW: IPinfo Integration** - Geographic and ISP analysis
- Country distribution with pie charts
- ISP/Organization identification
- Private IP detection and labeling
- IP-based filtering and analysis

### 🚨 HTTP Errors & Streaming
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
- **HTTP Error Intelligence**: Server IP and stream name extraction from error URLs
- **Advanced Filtering**: Filter by date range, status codes, protocols, IPs, and streams

## 🛠 Core Components

- `json_log_analyzer.py` - Enhanced multi-format analyzer with JSON support
- `nimble_app_log_parser.py` - Specialized parser for Nimble application logs with HTTP error extraction  
- `web_gui.py` - Feature-rich Dash web interface with 8 analysis tabs
- `log_analyzer.py` - Traditional log format analyzer
- `start_web_gui.bat` - Easy launcher with threading fixes and port detection

## 📋 Requirements

- Python 3.7+
- pandas, matplotlib, plotly, dash
- openpyxl, tqdm, regex
- See `requirements.txt` for complete list

## 🌍 NEW: IPinfo Integration

### Enhanced Geographic Analysis
- **Country Distribution**: Visual pie charts showing traffic by country
- **ISP Analysis**: Identify top internet service providers and organizations
- **Enhanced IP Tables**: IP addresses now include country, city, and ISP data
- **Smart Caching**: Efficient API usage with local caching
- **Private IP Detection**: Automatically identifies internal/private networks

### Setup IPinfo (Optional)
1. Get free API token at [https://ipinfo.io](https://ipinfo.io) (50,000 requests/month free)
2. In the web interface, enter your token in the "🌍 IP Geolocation Configuration" section
3. Enable "IP Geolocation Analysis" checkbox

See `IPINFO_SETUP.md` for detailed configuration instructions.

## 📁 Project Structure

```
nimble-streamer-log-analyzer/
├── web_gui.py                    # Main web interface with 8 analysis tabs
├── json_log_analyzer.py          # Multi-format log analyzer
├── nimble_app_log_parser.py      # Nimble app log parser with HTTP error extraction
├── log_analyzer.py               # Traditional log format analyzer
├── ipinfo_service.py             # NEW: IPinfo API integration
├── requirements.txt              # Python dependencies
├── start_web_gui.bat            # Windows launcher
├── launch_web_gui.ps1           # PowerShell launcher
├── IPINFO_SETUP.md              # IPinfo configuration guide
├── logs/                        # Upload log files here
└── reports/                     # Generated reports (CSV, Excel, PNG)
```

## 🎯 Use Cases

- **Server Monitoring**: Track HTTP errors and identify problematic streams
- **Performance Analysis**: Analyze request patterns and peak usage times
- **Geographic Analysis**: NEW - Understand traffic sources by country and ISP
- **Troubleshooting**: Extract server IPs and stream names from error messages
- **Capacity Planning**: Understand traffic patterns and bandwidth usage
- **Content Performance**: Identify popular streams and content success rates

## 🎉 Ready to Analyze!

Upload your Nimble Streamer log files and get instant insights with smart format detection, HTTP error analysis, and comprehensive reporting including server IP and stream name extraction.
