"""
System Log (Syslog) Parser for Nimble Streamer Log Analyzer
Handles system logs, security logs, and other traditional syslog formats.
"""

import pandas as pd
import re
from datetime import datetime, timedelta
import os
from typing import Dict, List, Optional

class SyslogParser:
    """
    Parser for system logs (syslog format) including security logs, SSH logs, etc.
    
    Supports formats like:
    Jul 22 03:46:42 s7 perl[2527651]: pam_unix(webmin:auth): authentication failure
    Jul 22 03:47:01 s7 CRON[2527725]: pam_unix(cron:session): session opened
    """
    
    def __init__(self):
        self.format_detected = "syslog"
        
        # Common syslog patterns
        self.syslog_pattern = re.compile(
            r'^(?P<month>\w+)\s+(?P<day>\d+)\s+(?P<time>\d+:\d+:\d+)\s+'
            r'(?P<hostname>\S+)\s+'
            r'(?P<service>\w+)(?:\[(?P<pid>\d+)\])?\:\s*'
            r'(?P<message>.*)$'
        )
        
        # IP address extraction pattern
        self.ip_pattern = re.compile(r'\b(?:\d{1,3}\.){3}\d{1,3}\b')
        
        # Authentication patterns
        self.auth_patterns = {
            'ssh_connection': re.compile(r'Connection (?:closed|reset) by (\d+\.\d+\.\d+\.\d+)'),
            'ssh_invalid': re.compile(r'Invalid user \w+ from (\d+\.\d+\.\d+\.\d+)'),
            'pam_failure': re.compile(r'authentication failure.*rhost=(\d+\.\d+\.\d+\.\d+)'),
            'webmin_invalid': re.compile(r'Invalid login as \w+ from (\d+\.\d+\.\d+\.\d+)'),
            'blocked_host': re.compile(r'Host (\d+\.\d+\.\d+\.\d+) blocked'),
            'ssh_preauth': re.compile(r'from (\d+\.\d+\.\d+\.\d+) port \d+ \[preauth\]')
        }
        
    def parse_log_file(self, file_path: str, chunk_size: int = 10000) -> pd.DataFrame:
        """
        Parse syslog file and return structured DataFrame.
        
        Args:
            file_path: Path to the syslog file
            chunk_size: Number of lines to process at once
            
        Returns:
            DataFrame with parsed syslog entries
        """
        print(f"🔍 Parsing syslog file: {file_path}")
        
        parsed_entries = []
        total_lines = 0
        parsed_count = 0
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
                chunk = []
                for line_num, line in enumerate(file, 1):
                    total_lines += 1
                    chunk.append(line.strip())
                    
                    if len(chunk) >= chunk_size:
                        chunk_results = self._parse_chunk(chunk, line_num - len(chunk) + 1)
                        parsed_entries.extend(chunk_results)
                        parsed_count += len(chunk_results)
                        chunk = []
                        
                        if line_num % (chunk_size * 10) == 0:
                            print(f"📊 Processed {line_num:,} lines, parsed {parsed_count:,} entries")
                
                # Process remaining lines
                if chunk:
                    chunk_results = self._parse_chunk(chunk, total_lines - len(chunk) + 1)
                    parsed_entries.extend(chunk_results)
                    parsed_count += len(chunk_results)
        
        except Exception as e:
            print(f"❌ Error reading file: {e}")
            raise
        
        print(f"✅ Parsing complete: {parsed_count:,} entries from {total_lines:,} lines")
        
        if not parsed_entries:
            print("⚠️ No valid syslog entries found")
            return pd.DataFrame()
            
        df = pd.DataFrame(parsed_entries)
        
        # Add derived columns
        df['parsed'] = True
        df['log_type'] = 'syslog'
        
        return df
    
    def _parse_chunk(self, chunk: List[str], start_line: int) -> List[Dict]:
        """Parse a chunk of log lines."""
        parsed_entries = []
        
        for i, line in enumerate(chunk):
            try:
                entry = self._parse_syslog_line(line, start_line + i)
                if entry:
                    parsed_entries.append(entry)
            except Exception as e:
                # Continue parsing even if individual lines fail
                continue
                
        return parsed_entries
    
    def _parse_syslog_line(self, line: str, line_num: int) -> Optional[Dict]:
        """Parse a single syslog line."""
        if not line.strip():
            return None
            
        # Try to match standard syslog format
        match = self.syslog_pattern.match(line)
        
        if not match:
            # Fallback: try to extract basic info
            parts = line.split(None, 4)
            if len(parts) < 5:
                return None
            
            return {
                'line_number': line_num,
                'raw_line': line,
                'timestamp': f"{parts[0]} {parts[1]} {parts[2]}",
                'hostname': parts[3] if len(parts) > 3 else '',
                'service': 'unknown',
                'pid': None,
                'message': ' '.join(parts[4:]) if len(parts) > 4 else '',
                'ip_address': self._extract_ip(line),
                'event_type': self._classify_event(line),
                'severity': self._determine_severity(line),
                'parsed': True
            }
        
        # Extract data from regex match
        groups = match.groupdict()
        
        # Create timestamp (assume current year if not specified)
        try:
            current_year = datetime.now().year
            timestamp_str = f"{current_year} {groups['month']} {groups['day']} {groups['time']}"
            timestamp = datetime.strptime(timestamp_str, "%Y %b %d %H:%M:%S")
        except Exception as e:
            # If parsing fails, keep the original format and let the caller handle it
            timestamp_str = f"{groups['month']} {groups['day']} {groups['time']}"
            # Try parsing without year as fallback
            try:
                # Use current year
                current_year = datetime.now().year
                timestamp = datetime.strptime(f"{current_year} {timestamp_str}", "%Y %b %d %H:%M:%S")
            except:
                timestamp = None
        
        # Extract IP address from message
        ip_address = self._extract_ip(groups['message'])
        
        # Classify event type
        event_type = self._classify_event(groups['message'])
        
        # Determine severity
        severity = self._determine_severity(groups['message'])
        
        return {
            'line_number': line_num,
            'raw_line': line,
            'timestamp': timestamp_str,
            'datetime': timestamp,
            'hostname': groups['hostname'],
            'service': groups['service'],
            'pid': int(groups['pid']) if groups['pid'] else None,
            'message': groups['message'],
            'ip_address': ip_address,
            'event_type': event_type,
            'severity': severity,
            'parsed': True
        }
    
    def _extract_ip(self, text: str) -> Optional[str]:
        """Extract IP address from log message."""
        # Try specific patterns first
        for pattern_name, pattern in self.auth_patterns.items():
            match = pattern.search(text)
            if match:
                return match.group(1)
        
        # Fallback to general IP pattern
        match = self.ip_pattern.search(text)
        return match.group(0) if match else None
    
    def _classify_event(self, message: str) -> str:
        """Classify the type of event based on message content."""
        message_lower = message.lower()
        
        # Authentication events
        if any(keyword in message_lower for keyword in ['authentication failure', 'invalid login', 'login failed']):
            return 'auth_failure'
        elif any(keyword in message_lower for keyword in ['blocked', 'banned']):
            return 'security_block'
        elif any(keyword in message_lower for keyword in ['connection closed', 'connection reset']):
            return 'connection_end'
        elif any(keyword in message_lower for keyword in ['session opened']):
            return 'session_start'
        elif any(keyword in message_lower for keyword in ['session closed']):
            return 'session_end'
        elif any(keyword in message_lower for keyword in ['preauth']):
            return 'auth_attempt'
        elif any(keyword in message_lower for keyword in ['error', 'failed']):
            return 'error'
        elif any(keyword in message_lower for keyword in ['cron']):
            return 'scheduled_task'
        else:
            return 'general'
    
    def _determine_severity(self, message: str) -> str:
        """Determine severity level based on message content."""
        message_lower = message.lower()
        
        if any(keyword in message_lower for keyword in ['blocked', 'security alert', 'banned']):
            return 'critical'
        elif any(keyword in message_lower for keyword in ['authentication failure', 'invalid login', 'error']):
            return 'warning'
        elif any(keyword in message_lower for keyword in ['connection closed', 'session opened', 'session closed']):
            return 'info'
        else:
            return 'info'
    
    def get_statistics(self, df: pd.DataFrame) -> Dict:
        """Generate statistics for syslog data."""
        if df.empty:
            return {}
        
        stats = {
            'total_entries': len(df),
            'unique_hosts': df['hostname'].nunique() if 'hostname' in df.columns else 0,
            'unique_services': df['service'].nunique() if 'service' in df.columns else 0,
            'unique_ips': df['ip_address'].nunique() if 'ip_address' in df.columns else 0,
            'date_range': {
                'start': df['timestamp'].min() if 'timestamp' in df.columns else None,
                'end': df['timestamp'].max() if 'timestamp' in df.columns else None
            }
        }
        
        # Event type distribution
        if 'event_type' in df.columns:
            stats['event_types'] = df['event_type'].value_counts().to_dict()
        
        # Severity distribution
        if 'severity' in df.columns:
            stats['severity_levels'] = df['severity'].value_counts().to_dict()
        
        # Top IP addresses
        if 'ip_address' in df.columns:
            top_ips = df[df['ip_address'].notna()]['ip_address'].value_counts().head(10)
            stats['top_ips'] = top_ips.to_dict()
        
        # Top services
        if 'service' in df.columns:
            stats['top_services'] = df['service'].value_counts().head(10).to_dict()
        
        return stats
