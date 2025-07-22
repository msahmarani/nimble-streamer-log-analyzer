"""
Enhanced Nimble Streamer Log Analyzer with JSON Support
Handles both traditional log formats and JSON-formatted Nimble Streamer logs.
"""

import pandas as pd
import numpy as np
import json
import re
from datetime import datetime
import os
from log_analyzer import NimbleLogAnalyzer
from nimble_app_log_parser import NimbleApplicationLogParser

# Try to import tqdm, fall back to a dummy version if not available
try:
    from tqdm import tqdm
except ImportError:
    # Create a dummy tqdm class for when it's not available
    class tqdm:
        def __init__(self, iterable=None, total=None, desc=None):
            self.iterable = iterable
            self.total = total
            self.desc = desc
            self.n = 0
            
        def __enter__(self):
            if self.desc:
                print(f"{self.desc}...")
            return self
            
        def __exit__(self, exc_type, exc_val, exc_tb):
            pass
            
        def update(self, n):
            self.n += n
            if self.total and self.n % max(1, self.total // 10) == 0:
                progress = (self.n / self.total) * 100
                print(f"Progress: {progress:.1f}% ({self.n}/{self.total})")

class JSONNimbleLogAnalyzer(NimbleLogAnalyzer):
    """Extended log analyzer with JSON format support for Nimble Streamer."""
    
    def __init__(self, log_file_path):
        super().__init__(log_file_path)
        self.json_logs = []
        self.format_detected = None
        self.nimble_app_parser = NimbleApplicationLogParser()
    
    def detect_log_format(self, sample_lines=50):
        """
        Detect if the log file is JSON format or traditional format.
        
        Args:
            sample_lines (int): Number of lines to sample for detection
            
        Returns:
            str: 'json', 'traditional', or 'unknown'
        """
        json_count = 0
        traditional_count = 0
        sample_lines_analyzed = 0
        sample_content = []
        
        with open(self.log_file_path, 'r', encoding='utf-8', errors='ignore') as file:
            for i, line in enumerate(file):
                if i >= sample_lines:
                    break
                    
                line = line.strip()
                if not line:
                    continue
                
                sample_lines_analyzed += 1
                sample_content.append(line[:200])  # Store first 200 chars for debugging
                
                # Try to parse as JSON
                try:
                    json.loads(line)
                    json_count += 1
                except json.JSONDecodeError:
                    # Check if it matches traditional log patterns
                    if self.is_traditional_log_line(line):
                        traditional_count += 1
        
        # Determine format based on results
        nimble_app_lines = 0
        for line in sample_content:
            if re.search(r'^\[\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2}.*?\].*?\[.*?\].*?[A-Z]:', line):
                nimble_app_lines += 1
        
        if json_count > 0 and json_count >= max(traditional_count, nimble_app_lines):
            self.format_detected = 'json'
        elif nimble_app_lines > 0 and nimble_app_lines >= traditional_count:
            self.format_detected = 'nimble_app'
        elif traditional_count > 0:
            self.format_detected = 'traditional'
        else:
            self.format_detected = 'unknown'
        
        print(f"🔍 Log format detection results:")
        print(f"   Sample lines analyzed: {sample_lines_analyzed}")
        print(f"   JSON lines found: {json_count}")
        print(f"   Nimble App log lines: {nimble_app_lines}")
        print(f"   Traditional pattern matches: {traditional_count}")
        print(f"   Format detected: {self.format_detected.upper()}")
        
        # If format is unknown, show sample lines for debugging
        if self.format_detected == 'unknown' and sample_content:
            print(f"📝 Sample log lines (first 3):")
            for i, sample in enumerate(sample_content[:3]):
                print(f"   Line {i+1}: {sample}")
        
        return self.format_detected
    
    def is_traditional_log_line(self, line):
        """Check if a line matches traditional log patterns with more comprehensive patterns."""
        patterns = [
            # Nimble Streamer Application Log Format (PRIORITY)
            r'^\[\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2}\s+[^\]]+\]\s+\[[^\]]+\]\s+[A-Z]:',
            r'^\[\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2}\s+[^\]]+\]\s+[A-Z]:',
            
            # Apache/Nginx Common Log Format
            r'^\d+\.\d+\.\d+\.\d+\s+\S+\s+\S+\s+\[.*?\]\s+".*?"\s+\d+\s+\d+',
            # Apache/Nginx Combined Log Format  
            r'^\d+\.\d+\.\d+\.\d+.*?\[.*?\].*?".*?".*?\d+.*?".*?".*?".*?"',
            # IIS Log Format
            r'^\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2}\s+\d+\.\d+\.\d+\.\d+',
            # Nimble Streamer Access Log Format
            r'^\d{4}/\d{2}/\d{2}\s+\d{2}:\d{2}:\d{2}',
            # General IP address at start
            r'^\d+\.\d+\.\d+\.\d+',
            # Timestamp patterns
            r'\d{4}-\d{2}-\d{2}[T\s]\d{2}:\d{2}:\d{2}',
            r'\d{2}/\w{3}/\d{4}:\d{2}:\d{2}:\d{2}',
            # HTTP request patterns
            r'"[A-Z]+\s+[^"]+\s+HTTP/[\d\.]+"',
            # Status code patterns  
            r'\s\d{3}\s',
            # Square bracket patterns (timestamps)
            r'\[[^\]]+\]',
        ]
        
        # Check if any pattern matches
        for pattern in patterns:
            if re.search(pattern, line):
                return True
        
        return False
    
    def read_log_file(self, chunk_size=10000):
        """
        Enhanced log file reader that handles both JSON and traditional formats.
        
        Args:
            chunk_size (int): Number of lines to read at once
        """
        print(f"📖 Reading log file: {self.log_file_path}")
        
        if not os.path.exists(self.log_file_path):
            raise FileNotFoundError(f"Log file not found: {self.log_file_path}")
        
        file_size = os.path.getsize(self.log_file_path)
        print(f"📏 File size: {file_size / (1024*1024):.2f} MB")
        
        # Detect format first
        log_format = self.detect_log_format()
        
        logs = []
        total_lines = 0
        
        with open(self.log_file_path, 'r', encoding='utf-8', errors='ignore') as file:
            chunk = []
            
            # Count total lines for progress bar
            print("🔢 Counting total lines...")
            total_lines = sum(1 for _ in file)
            file.seek(0)  # Reset to beginning
            
            with tqdm(total=total_lines, desc="Processing lines") as pbar:
                for line_num, line in enumerate(file, 1):
                    chunk.append(line.strip())
                    
                    if len(chunk) >= chunk_size:
                        parsed_chunk = self.parse_log_chunk_enhanced(chunk, log_format)
                        logs.extend(parsed_chunk)
                        pbar.update(len(chunk))
                        chunk = []
                
                # Process remaining lines
                if chunk:
                    parsed_chunk = self.parse_log_chunk_enhanced(chunk, log_format)
                    logs.extend(parsed_chunk)
                    pbar.update(len(chunk))
        
        self.parsed_logs = logs
        self.data = pd.DataFrame(logs)
        
        # Post-processing for JSON logs
        if log_format == 'json':
            self.process_json_specific_fields()
        
        print(f"✅ Successfully parsed {len(logs):,} log entries")
        
        if not logs:
            print("⚠️  No valid log entries were parsed. Check log format.")
        
        return self.data
    
    def parse_log_chunk_enhanced(self, chunk, log_format):
        """
        Enhanced chunk parser that handles different log formats.
        
        Args:
            chunk (list): List of log lines to parse
            log_format (str): Detected log format
            
        Returns:
            list: List of parsed log dictionaries
        """
        parsed_chunk = []
        
        for line in chunk:
            if not line.strip():
                continue
            
            log_entry = None
            
            if log_format == 'json':
                log_entry = self.parse_json_log_line(line)
            elif log_format == 'nimble_app':
                log_entry = self.parse_nimble_app_line(line)
            elif log_format == 'traditional':
                log_entry = self.parse_log_line(line)  # Use parent class method
            else:  # unknown format - try everything
                # Try JSON first
                log_entry = self.parse_json_log_line(line)
                
                # If JSON parsing failed, try Nimble app format
                if not log_entry or not log_entry.get('parsed', False):
                    log_entry = self.parse_nimble_app_line(line)
                
                # If Nimble app parsing failed, try traditional
                if not log_entry or not log_entry.get('parsed', False):
                    log_entry = self.parse_log_line(line)
                
                # If traditional parsing also failed, create a basic entry
                if not log_entry or not log_entry.get('parsed', False):
                    log_entry = self.parse_unknown_format_line(line)
            
            if log_entry:
                parsed_chunk.append(log_entry)
        
        return parsed_chunk
    
    def parse_nimble_app_line(self, line):
        """
        Parse a Nimble Streamer application log line.
        
        Args:
            line (str): Nimble app log line
            
        Returns:
            dict: Parsed log entry
        """
        try:
            result = self.nimble_app_parser.parse_line(line)
            if result and result.get('parsed'):
                # Add additional fields for compatibility with web interface
                result['ip_address'] = None  # App logs don't have IP addresses
                result['status_code'] = None  # App logs don't have HTTP status codes
                result['url'] = None  # App logs don't have URLs
                
                # Map level to status_code for visualization compatibility
                level_mapping = {'E': 500, 'W': 400, 'I': 200, 'D': 100}
                if 'level' in result:
                    result['status_code'] = level_mapping.get(result['level'], 200)
                
                # Add hour for time analysis
                if 'timestamp' in result:
                    result['hour'] = result['timestamp'].hour
                    result['date'] = result['timestamp'].date()
            
            return result
        except Exception as e:
            return {
                'timestamp': datetime.now(),
                'raw_line': line,
                'error': str(e),
                'parsed': False,
                'format': 'nimble_app_error'
            }
    
    def parse_unknown_format_line(self, line):
        """
        Parse lines from unknown format - extracts basic information.
        
        Args:
            line (str): Log line to parse
            
        Returns:
            dict: Basic log entry with extracted information
        """
        try:
            log_entry = {
                'raw_line': line,
                'parsed': True,
                'format': 'unknown'
            }
            
            # Try to extract timestamp (various formats)
            timestamp_patterns = [
                r'(\d{4}-\d{2}-\d{2}[T\s]\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:?\d{2})?)',
                r'(\d{2}/\w{3}/\d{4}:\d{2}:\d{2}:\d{2})',
                r'(\d{4}/\d{2}/\d{2}\s+\d{2}:\d{2}:\d{2})',
                r'(\d{1,2}-\d{1,2}-\d{4}\s+\d{1,2}:\d{2}:\d{2})',
            ]
            
            for pattern in timestamp_patterns:
                match = re.search(pattern, line)
                if match:
                    try:
                        timestamp_str = match.group(1)
                        log_entry['timestamp'] = self.parse_timestamp(timestamp_str)
                        log_entry['timestamp_raw'] = timestamp_str
                        break
                    except:
                        continue
            else:
                log_entry['timestamp'] = datetime.now()
            
            # Try to extract IP address
            ip_pattern = r'\b(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})\b'
            ip_match = re.search(ip_pattern, line)
            if ip_match:
                log_entry['ip_address'] = ip_match.group(1)
            
            # Try to extract status codes
            status_pattern = r'\b((?:[1-5]\d{2})|(?:200|404|500|301|302))\b'
            status_match = re.search(status_pattern, line)
            if status_match:
                log_entry['status_code'] = int(status_match.group(1))
            
            # Try to extract URLs/paths
            url_patterns = [
                r'"[A-Z]+\s+([^"]+)\s+HTTP',  # HTTP request format
                r'GET|POST|PUT|DELETE\s+([^\s]+)',  # Simple method format
                r'\s(/[^\s]*)\s',  # Simple path format
            ]
            
            for pattern in url_patterns:
                url_match = re.search(pattern, line)
                if url_match:
                    log_entry['url'] = url_match.group(1)
                    break
            
            # Try to extract HTTP method
            method_pattern = r'\b(GET|POST|PUT|DELETE|HEAD|OPTIONS|PATCH)\b'
            method_match = re.search(method_pattern, line)
            if method_match:
                log_entry['method'] = method_match.group(1)
            
            # Extract quoted strings (might be user agents, referers)
            quoted_strings = re.findall(r'"([^"]*)"', line)
            if quoted_strings:
                # First quoted string might be the request
                if len(quoted_strings) >= 1 and not log_entry.get('url'):
                    if 'HTTP' in quoted_strings[0]:
                        parts = quoted_strings[0].split()
                        if len(parts) >= 2:
                            log_entry['method'] = parts[0]
                            log_entry['url'] = parts[1]
                
                # Last quoted string might be user agent
                if len(quoted_strings) >= 2:
                    log_entry['user_agent'] = quoted_strings[-1]
            
            return log_entry
            
        except Exception as e:
            return {
                'timestamp': datetime.now(),
                'raw_line': line,
                'error': str(e),
                'parsed': False,
                'format': 'unknown_error'
            }
    
    def parse_json_log_line(self, line):
        """
        Parse a JSON-formatted log line from Nimble Streamer.
        
        Args:
            line (str): JSON log line
            
        Returns:
            dict: Parsed log entry or None if parsing fails
        """
        try:
            json_data = json.loads(line)
            
            # Extract and normalize fields based on your JSON format
            log_entry = {
                'raw_line': line,
                'parsed': True,
                'format': 'json'
            }
            
            # Handle timestamp - support various field names
            timestamp_fields = ['timestamp', 'time', 'datetime', 'date']
            for field in timestamp_fields:
                if field in json_data:
                    log_entry['timestamp'] = self.parse_timestamp(json_data[field])
                    break
            else:
                log_entry['timestamp'] = datetime.now()
            
            # Map JSON fields to standard fields
            field_mapping = {
                # Nimble Streamer specific fields
                'client_ip': ['client_ip', 'ip', 'ip_address', 'remote_ip'],
                'stream_name': ['stream_name', 'stream_alias', 'stream'],
                'protocol': ['protocol', 'proto'],
                'status': ['status', 'event_type', 'action'],
                'session_id': ['session_id', 'session', 'sid'],
                'user_agent': ['user_agent', 'ua', 'agent'],
                'bytes_sent': ['bytes_sent', 'bytes', 'size'],
                'duration': ['duration', 'time_duration'],
                'url': ['url', 'uri', 'request_uri'],
                'method': ['method', 'http_method'],
                'status_code': ['status_code', 'http_status', 'code'],
                'referer': ['referer', 'referrer'],
            }
            
            # Extract fields using mapping
            for standard_field, possible_names in field_mapping.items():
                for name in possible_names:
                    if name in json_data:
                        log_entry[standard_field] = json_data[name]
                        break
            
            # Add any additional fields that aren't mapped
            for key, value in json_data.items():
                if key not in log_entry:
                    log_entry[f'json_{key}'] = value
            
            return log_entry
            
        except json.JSONDecodeError as e:
            # Not a valid JSON line
            return {
                'timestamp': datetime.now(),
                'raw_line': line,
                'error': f'JSON decode error: {str(e)}',
                'parsed': False,
                'format': 'json_error'
            }
        except Exception as e:
            return {
                'timestamp': datetime.now(),
                'raw_line': line,
                'error': str(e),
                'parsed': False,
                'format': 'json_error'
            }
    
    def parse_timestamp(self, timestamp_value):
        """
        Parse various timestamp formats.
        
        Args:
            timestamp_value: Timestamp in various formats
            
        Returns:
            datetime: Parsed datetime object
        """
        if isinstance(timestamp_value, (int, float)):
            # Unix timestamp
            return datetime.fromtimestamp(timestamp_value)
        
        if isinstance(timestamp_value, str):
            # Try various string formats
            formats = [
                '%Y-%m-%dT%H:%M:%SZ',  # ISO format with Z
                '%Y-%m-%dT%H:%M:%S',   # ISO format
                '%Y-%m-%d %H:%M:%S',   # Standard format
                '%d/%b/%Y:%H:%M:%S',   # Apache format
                '%Y-%m-%d',            # Date only
            ]
            
            for fmt in formats:
                try:
                    return datetime.strptime(timestamp_value, fmt)
                except ValueError:
                    continue
        
        # If all else fails, return current time
        return datetime.now()
    
    def process_json_specific_fields(self):
        """Process JSON-specific fields for enhanced analysis."""
        if self.data is None or self.data.empty:
            return
        
        # Add derived fields for streaming analysis
        if 'timestamp' in self.data.columns:
            self.data['hour'] = pd.to_datetime(self.data['timestamp']).dt.hour
            self.data['date'] = pd.to_datetime(self.data['timestamp']).dt.date
            self.data['day_of_week'] = pd.to_datetime(self.data['timestamp']).dt.day_name()
        
        # Standardize status/event types
        if 'status' in self.data.columns:
            self.data['event_category'] = self.data['status'].apply(self.categorize_event)
        
        # Add streaming-specific metrics
        if 'protocol' in self.data.columns:
            self.data['is_streaming_protocol'] = self.data['protocol'].apply(
                lambda x: x.upper() in ['HLS', 'DASH', 'RTMP', 'RTSP', 'UDP'] if pd.notna(x) else False
            )
        
        print(f"📊 Processed {len(self.data)} entries with JSON-specific enhancements")
    
    def categorize_event(self, status):
        """Categorize streaming events."""
        if pd.isna(status):
            return 'unknown'
        
        status_lower = str(status).lower()
        
        if 'connect' in status_lower:
            return 'connection'
        elif 'disconnect' in status_lower:
            return 'disconnection'
        elif 'play' in status_lower:
            return 'playback'
        elif 'publish' in status_lower:
            return 'publishing'
        elif 'error' in status_lower or 'fail' in status_lower:
            return 'error'
        elif 'success' in status_lower:
            return 'success'
        else:
            return 'other'
    
    def generate_streaming_analytics(self):
        """Generate analytics specific to streaming data."""
        if self.data is None or self.data.empty:
            print("No data available for streaming analytics")
            return
        
        print("\n" + "="*50)
        print("STREAMING ANALYTICS (JSON LOG FORMAT)")
        print("="*50)
        
        # Session analysis
        if 'session_id' in self.data.columns:
            unique_sessions = self.data['session_id'].nunique()
            avg_events_per_session = len(self.data) / unique_sessions if unique_sessions > 0 else 0
            print(f"🎯 Total unique sessions: {unique_sessions:,}")
            print(f"📊 Average events per session: {avg_events_per_session:.2f}")
        
        # Stream analysis
        if 'stream_name' in self.data.columns:
            unique_streams = self.data['stream_name'].nunique()
            popular_streams = self.data['stream_name'].value_counts().head(10)
            print(f"\n🎬 Total unique streams: {unique_streams:,}")
            print("🔥 Most popular streams:")
            for stream, count in popular_streams.items():
                if pd.notna(stream):
                    print(f"   {stream}: {count:,} events")
        
        # Protocol analysis
        if 'protocol' in self.data.columns:
            protocol_dist = self.data['protocol'].value_counts()
            print(f"\n🌐 Protocol distribution:")
            for protocol, count in protocol_dist.items():
                if pd.notna(protocol):
                    percentage = (count / len(self.data)) * 100
                    print(f"   {protocol}: {count:,} ({percentage:.1f}%)")
        
        # Event analysis
        if 'event_category' in self.data.columns:
            event_dist = self.data['event_category'].value_counts()
            print(f"\n📈 Event category distribution:")
            for event, count in event_dist.items():
                percentage = (count / len(self.data)) * 100
                print(f"   {event}: {count:,} ({percentage:.1f}%)")
        
        # Success rate analysis
        if 'status' in self.data.columns:
            success_events = len(self.data[self.data['status'] == 'success'])
            total_events = len(self.data)
            success_rate = (success_events / total_events) * 100 if total_events > 0 else 0
            print(f"\n✅ Overall success rate: {success_rate:.2f}%")
        
        # Client analysis
        if 'client_ip' in self.data.columns:
            unique_clients = self.data['client_ip'].nunique()
            top_clients = self.data['client_ip'].value_counts().head(5)
            print(f"\n👥 Unique client IPs: {unique_clients:,}")
            print("🔝 Top client IPs:")
            for ip, count in top_clients.items():
                if pd.notna(ip):
                    print(f"   {ip}: {count:,} events")
    
    def export_enhanced_reports(self):
        """Export enhanced reports with JSON-specific data."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        reports_dir = "reports"
        os.makedirs(reports_dir, exist_ok=True)
        
        if self.data is None or self.data.empty:
            print("No data to export")
            return
        
        # Enhanced CSV export with all fields
        csv_filename = f"{reports_dir}/nimble_json_analysis_{timestamp}.csv"
        self.data.to_csv(csv_filename, index=False)
        print(f"📄 Enhanced CSV report saved: {csv_filename}")
        
        # Create summary report
        summary_data = []
        
        if 'session_id' in self.data.columns:
            summary_data.append({
                'Metric': 'Total Sessions',
                'Value': self.data['session_id'].nunique()
            })
        
        if 'stream_name' in self.data.columns:
            summary_data.append({
                'Metric': 'Total Streams',
                'Value': self.data['stream_name'].nunique()
            })
        
        if 'client_ip' in self.data.columns:
            summary_data.append({
                'Metric': 'Unique Clients',
                'Value': self.data['client_ip'].nunique()
            })
        
        if 'protocol' in self.data.columns:
            summary_data.append({
                'Metric': 'Protocols Used',
                'Value': self.data['protocol'].nunique()
            })
        
        if summary_data:
            summary_df = pd.DataFrame(summary_data)
            summary_filename = f"{reports_dir}/nimble_streaming_summary_{timestamp}.csv"
            summary_df.to_csv(summary_filename, index=False)
            print(f"📊 Streaming summary saved: {summary_filename}")

def main():
    """Main function to demonstrate JSON log analysis."""
    import sys
    
    if len(sys.argv) != 2:
        print("Usage: python json_log_analyzer.py <log_file_path>")
        sys.exit(1)
    
    log_file = sys.argv[1]
    
    try:
        analyzer = JSONNimbleLogAnalyzer(log_file)
        analyzer.read_log_file()
        
        # Generate traditional reports
        analyzer.generate_summary_report()
        analyzer.generate_time_analysis()
        
        # Generate streaming-specific analytics
        analyzer.generate_streaming_analytics()
        
        # Create visualizations
        analyzer.create_visualizations()
        
        # Export enhanced reports
        analyzer.export_enhanced_reports()
        
    except Exception as e:
        print(f"❌ Error analyzing log file: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
