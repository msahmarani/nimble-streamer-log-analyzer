# Changelog

## v2.0.0 - HTTP Error Analysis & Stream Intelligence (2025-07-22)

### 🆕 New Features
- **HTTP Error Analysis Tab**: Comprehensive analysis of HTTP error codes from Nimble application logs
- **Server IP Extraction**: Parse server IP addresses from URLs in error messages (e.g., `http://38.46.143.164:8081/...`)
- **Stream Name Detection**: Extract stream names from URL paths (e.g., "cinecanal" from `/stream/cinecanal/playlist.m3u8`)
- **Server:Stream Combinations**: Track and analyze which servers serve which streams
- **Enhanced Nimble App Log Parser**: New dedicated parser for Nimble application log format
- **Advanced URL Pattern Recognition**: Regex patterns for various URL formats and stream detection

### ✨ Enhancements
- **Web GUI Improvements**: Added new "🚨 HTTP Errors & Streaming" tab with detailed analysis
- **Memory Optimization**: Better handling of large files (130MB+) with chunked processing
- **Error Intelligence**: Sample error messages display with extracted server IPs and stream names
- **Enhanced Filtering**: Advanced filters for date ranges, status codes, protocols, IPs, and streams
- **Better Error Handling**: Improved exception handling and user feedback

### 🔧 Technical Improvements
- **Modular Architecture**: Separated Nimble application log parsing into dedicated module
- **Enhanced Regex Patterns**: Multiple URL pattern recognition for different log formats
- **Data Structure Optimization**: Added fields for `server_ip`, `stream_name`, `has_http_error`, `has_stream_info`, etc.
- **Code Organization**: Better separation of concerns between parsers and web interface

### 🐛 Bug Fixes
- **Threading Issues**: Resolved web GUI threading problems on Windows
- **Port Management**: Automatic port detection and conflict resolution
- **Data Type Handling**: Better handling of mixed data types in analysis
- **Memory Leaks**: Fixed potential memory issues with large file processing

### 📊 Analysis Features Added
- HTTP error code statistics with error type classification
- Server IP analysis with request count and percentages  
- Stream popularity analysis with viewership metrics
- Combined error+streaming analysis for troubleshooting
- Server:Stream combination tracking for infrastructure insights
- Sample error message display with parsed details

### 🎯 Use Case Improvements
- **Network Troubleshooting**: Identify problematic server IPs and streams
- **Content Performance**: Track stream popularity and error rates
- **Infrastructure Monitoring**: Monitor server:stream relationships
- **Error Analysis**: Deep dive into HTTP error patterns with context

## v1.0.0 - Initial Release
- Basic log file analysis
- Web interface with core tabs
- Multi-format log support (JSON, HTTP access logs)
- Basic reporting and visualization
