"""
Nimble Streamer Application Log Parser
Handles Nimble Streamer's application log format with timestamps in square brackets.
"""

import re
from datetime import datetime
import pandas as pd

class NimbleApplicationLogParser:
    """Parser specifically for Nimble Streamer application logs."""
    
    def __init__(self):
        self.patterns = self.create_patterns()
    
    def create_patterns(self):
        """Create regex patterns for different Nimble log types."""
        return {
            # Main pattern: [timestamp PID-TID] [component] Level: message
            'main': r'^\[(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2})\s+([^\]]+)\]\s+\[([^\]]+)\]\s+([A-Z]):\s*(.*)',
            
            # Alternative pattern without component
            'simple': r'^\[(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2})\s+([^\]]+)\]\s+([A-Z]):\s*(.*)',
            
            # HTTP error patterns
            'http_error': r'http\s+error\s+code=(\d+)\s+for\s+url=\'([^\']+)\'',
            
            # URL parsing patterns - enhanced for better stream detection
            'stream_url': r'https?://[^/]+/stream/([^/]+)/[^?]*(?:\?.*)?',
            'stream_url_with_ip': r'https?://([^:/]+)(?::\d+)?/stream/([^/]+)/[^?]*(?:\?.*)?',
            
            # IP address extraction from URLs
            'url_ip': r'https?://([0-9]+\.[0-9]+\.[0-9]+\.[0-9]+)(?::\d+)?',
            
            # Connection/streaming specific patterns
            'connection': r'.*(?:connect|disconnect|play|publish|stream).*',
            'error': r'.*(?:error|fail|invalid|denied).*',
            'warning': r'.*(?:warn|warning).*',
            'info': r'.*(?:info|started|stopped|listening).*',
        }
    
    def parse_line(self, line):
        """
        Parse a single Nimble Streamer application log line.
        
        Args:
            line (str): Log line to parse
            
        Returns:
            dict: Parsed log entry
        """
        line = line.strip()
        if not line:
            return None
            
        # Try main pattern first
        match = re.match(self.patterns['main'], line)
        if match:
            timestamp_str, process_info, component, level, message = match.groups()
            
            # Parse additional details from message
            error_details = self.extract_http_error_details(message)
            url_details = self.extract_url_details(message)
            
            base_entry = {
                'timestamp': self.parse_timestamp(timestamp_str),
                'timestamp_raw': timestamp_str,
                'process_info': process_info,
                'component': component,
                'level': level,
                'message': message,
                'raw_line': line,
                'parsed': True,
                'format': 'nimble_app_log',
                'log_type': self.categorize_message(message, level),
                'severity': self.get_severity_level(level)
            }
            
            # Add HTTP error details if found
            if error_details:
                base_entry.update(error_details)
                
            # Add URL details if found  
            if url_details:
                base_entry.update(url_details)
                
            return base_entry
        
        # Try simple pattern
        match = re.match(self.patterns['simple'], line)
        if match:
            timestamp_str, process_info, level, message = match.groups()
            
            # Parse additional details from message
            error_details = self.extract_http_error_details(message)
            url_details = self.extract_url_details(message)
            
            base_entry = {
                'timestamp': self.parse_timestamp(timestamp_str),
                'timestamp_raw': timestamp_str,
                'process_info': process_info,
                'component': 'unknown',
                'level': level,
                'message': message,
                'raw_line': line,
                'parsed': True,
                'format': 'nimble_app_log',
                'log_type': self.categorize_message(message, level),
                'severity': self.get_severity_level(level)
            }
            
            # Add HTTP error details if found
            if error_details:
                base_entry.update(error_details)
                
            # Add URL details if found  
            if url_details:
                base_entry.update(url_details)
                
            return base_entry
        
        # If no pattern matches, create basic entry
        return {
            'timestamp': datetime.now(),
            'raw_line': line,
            'parsed': False,
            'format': 'nimble_app_log',
            'error': 'No pattern matched'
        }
    
    def parse_timestamp(self, timestamp_str):
        """Parse Nimble timestamp format."""
        try:
            return datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S')
        except ValueError:
            return datetime.now()
    
    def extract_http_error_details(self, message):
        """
        Extract HTTP error code and URL from log message.
        
        Args:
            message (str): Log message to parse
            
        Returns:
            dict: Dictionary with error details or None
        """
        match = re.search(self.patterns['http_error'], message)
        if match:
            error_code = int(match.group(1))
            full_url = match.group(2)
            
            return {
                'has_http_error': True,
                'http_error_code': error_code,
                'error_url': full_url,
                'error_type': self.classify_http_error(error_code)
            }
        
        return None
    
    def extract_url_details(self, message):
        """
        Extract IP address and stream name from streaming URLs.
        
        Args:
            message (str): Log message containing URL
            
        Returns:
            dict: Dictionary with IP and stream details or None
        """
        # Look for URLs in the message
        url_match = re.search(r'https?://[^\s\'\"]+', message)
        if not url_match:
            return None
            
        url = url_match.group(0)
        result = {'has_url': True, 'full_url': url}
        
        # Extract IP address from URL
        ip_match = re.search(self.patterns['url_ip'], url)
        if ip_match:
            server_ip = ip_match.group(1)
            result['server_ip'] = server_ip
            result['has_server_ip'] = True
        
        # Extract stream details from URL pattern with IP
        stream_ip_match = re.search(self.patterns['stream_url_with_ip'], url)
        if stream_ip_match:
            server_ip = stream_ip_match.group(1)
            stream_name = stream_ip_match.group(2)
            
            result.update({
                'has_stream_info': True,
                'server_ip': server_ip,
                'stream_name': stream_name,
                'has_server_ip': True
            })
            return result
        
        # Fallback: Extract stream name only (without IP)
        stream_match = re.search(self.patterns['stream_url'], url)
        if stream_match:
            stream_name = stream_match.group(1)
            
            result.update({
                'has_stream_info': True,
                'stream_name': stream_name
            })
            return result
        
        return result if result.get('has_server_ip') else None
    
    def classify_http_error(self, error_code):
        """Classify HTTP error codes by type."""
        if 400 <= error_code < 500:
            error_types = {
                400: 'Bad Request',
                401: 'Unauthorized', 
                403: 'Forbidden',
                404: 'Not Found',
                408: 'Request Timeout',
                429: 'Too Many Requests'
            }
            return error_types.get(error_code, 'Client Error')
        elif 500 <= error_code < 600:
            error_types = {
                500: 'Internal Server Error',
                502: 'Bad Gateway',
                503: 'Service Unavailable',
                504: 'Gateway Timeout'
            }
            return error_types.get(error_code, 'Server Error')
        else:
            return f'HTTP {error_code}'
    
    def categorize_message(self, message, level):
        """Categorize the log message type."""
        message_lower = message.lower()
        
        if level == 'E':
            return 'error'
        elif level == 'W':
            return 'warning'
        elif 'connect' in message_lower or 'disconnect' in message_lower:
            return 'connection'
        elif 'stream' in message_lower or 'play' in message_lower or 'publish' in message_lower:
            return 'streaming'
        elif 'listen' in message_lower or 'start' in message_lower or 'stop' in message_lower:
            return 'system'
        elif 'config' in message_lower or 'setting' in message_lower:
            return 'configuration'
        else:
            return 'general'
    
    def get_severity_level(self, level):
        """Convert log level to numeric severity."""
        severity_map = {
            'E': 4,  # Error
            'W': 3,  # Warning  
            'I': 2,  # Info
            'D': 1,  # Debug
        }
        return severity_map.get(level, 0)
    
    def analyze_logs(self, log_data):
        """Analyze parsed log data for insights."""
        if not log_data:
            return {}
        
        df = pd.DataFrame(log_data)
        
        # Basic analysis
        analysis = {
            'total_entries': len(df),
            'parsed_entries': len(df[df['parsed'] == True]),
            'date_range': {
                'start': df['timestamp'].min(),
                'end': df['timestamp'].max()
            } if 'timestamp' in df.columns else None,
            'log_levels': df['level'].value_counts().to_dict() if 'level' in df.columns else {},
            'components': df['component'].value_counts().to_dict() if 'component' in df.columns else {},
            'log_types': df['log_type'].value_counts().to_dict() if 'log_type' in df.columns else {},
            'errors': len(df[df['level'] == 'E']) if 'level' in df.columns else 0,
            'warnings': len(df[df['level'] == 'W']) if 'level' in df.columns else 0,
        }
        
        # HTTP Error Analysis
        http_errors_df = df[df.get('has_http_error', False) == True]
        if not http_errors_df.empty:
            analysis['http_errors'] = {
                'total_http_errors': len(http_errors_df),
                'error_codes': http_errors_df['http_error_code'].value_counts().to_dict(),
                'error_types': http_errors_df['error_type'].value_counts().to_dict(),
                'top_error_urls': http_errors_df['error_url'].value_counts().head(10).to_dict()
            }
        
        # Server IP Analysis (from URLs)
        server_ips_df = df[df.get('has_server_ip', False) == True]
        if not server_ips_df.empty:
            analysis['server_ips'] = {
                'total_server_requests': len(server_ips_df),
                'unique_servers': server_ips_df['server_ip'].nunique(),
                'top_servers': server_ips_df['server_ip'].value_counts().head(20).to_dict(),
                'server_usage': server_ips_df['server_ip'].value_counts().to_dict()
            }
        
        # Streaming Analysis
        streaming_df = df[df.get('has_stream_info', False) == True]
        if not streaming_df.empty:
            analysis['streaming'] = {
                'total_stream_events': len(streaming_df),
                'unique_streams': streaming_df['stream_name'].nunique(),
                'top_streams': streaming_df['stream_name'].value_counts().head(20).to_dict(),
                'stream_usage': streaming_df['stream_name'].value_counts().to_dict()
            }
        
        # Error + Streaming Combined Analysis
        error_streaming_df = df[(df.get('has_http_error', False) == True) & (df.get('has_stream_info', False) == True)]
        if not error_streaming_df.empty:
            analysis['error_streaming'] = {
                'total_stream_errors': len(error_streaming_df),
                'error_streams': error_streaming_df['stream_name'].value_counts().to_dict(),
                'error_servers': error_streaming_df['server_ip'].value_counts().to_dict() if 'server_ip' in error_streaming_df.columns else {},
                'error_codes_by_stream': error_streaming_df.groupby('stream_name')['http_error_code'].value_counts().to_dict(),
                'problematic_streams': error_streaming_df['stream_name'].value_counts().head(10).to_dict(),
                'problematic_servers': error_streaming_df['server_ip'].value_counts().head(10).to_dict() if 'server_ip' in error_streaming_df.columns else {}
            }
        
        # Server + Stream Combinations  
        server_stream_df = df[(df.get('has_server_ip', False) == True) & (df.get('has_stream_info', False) == True)]
        if not server_stream_df.empty:
            # Create server:stream combinations
            server_stream_df['server_stream'] = server_stream_df['server_ip'] + ':' + server_stream_df['stream_name']
            analysis['server_stream_combinations'] = {
                'total_combinations': len(server_stream_df),
                'unique_combinations': server_stream_df['server_stream'].nunique(),
                'top_server_stream_pairs': server_stream_df['server_stream'].value_counts().head(15).to_dict()
            }
        
        return analysis

def test_parser():
    """Test the Nimble application log parser."""
    test_lines = [
        "[2025-02-25 04:05:46 P5059-T5059] [nimble] I: *** Nimble Streamer v3.7",
        "[2025-02-25 04:05:46 P5060-T5060] [nimble] I: listening '*:8081' (plain)",
        "[2025-02-25 04:05:46 P5060-T5066] [sync] I: panel_uuid is empty, stopping",
        "[2025-02-25 04:05:46 P5060-T5060] E: Failed to connect to server"
    ]
    
    parser = NimbleApplicationLogParser()
    
    print("🧪 TESTING NIMBLE APPLICATION LOG PARSER")
    print("=" * 60)
    
    for i, line in enumerate(test_lines, 1):
        result = parser.parse_line(line)
        print(f"\nTest {i}: {line[:50]}...")
        print(f"   Parsed: {'✅' if result.get('parsed') else '❌'}")
        if result.get('parsed'):
            print(f"   Timestamp: {result.get('timestamp')}")
            print(f"   Component: {result.get('component')}")
            print(f"   Level: {result.get('level')}")
            print(f"   Type: {result.get('log_type')}")
            print(f"   Message: {result.get('message', '')[:50]}...")

if __name__ == "__main__":
    test_parser()
