"""
Nimble Streamer Log Analyzer
A Python application for analyzing large log files and generating comprehensive reports.
"""

# Fix matplotlib backend issues on Windows
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import re
import os
import sys
from tqdm import tqdm
import json
from collections import defaultdict, Counter
import warnings
warnings.filterwarnings('ignore')

class NimbleLogAnalyzer:
    def __init__(self, log_file_path):
        """
        Initialize the log analyzer with the path to the log file.
        
        Args:
            log_file_path (str): Path to the log file to analyze
        """
        self.log_file_path = log_file_path
        self.data = None
        self.parsed_logs = []
        self.reports = {}
        
    def read_log_file(self, chunk_size=10000):
        """
        Read large log file in chunks to handle memory efficiently.
        
        Args:
            chunk_size (int): Number of lines to read at once
        """
        print(f"Reading log file: {self.log_file_path}")
        
        if not os.path.exists(self.log_file_path):
            raise FileNotFoundError(f"Log file not found: {self.log_file_path}")
        
        file_size = os.path.getsize(self.log_file_path)
        print(f"File size: {file_size / (1024*1024):.2f} MB")
        
        logs = []
        with open(self.log_file_path, 'r', encoding='utf-8', errors='ignore') as file:
            chunk = []
            for line_num, line in enumerate(file, 1):
                chunk.append(line.strip())
                
                if len(chunk) >= chunk_size:
                    logs.extend(self.parse_log_chunk(chunk))
                    chunk = []
                    
                    # Show progress for large files
                    if line_num % (chunk_size * 10) == 0:
                        print(f"Processed {line_num:,} lines...")
            
            # Process remaining lines
            if chunk:
                logs.extend(self.parse_log_chunk(chunk))
        
        self.parsed_logs = logs
        self.data = pd.DataFrame(logs)
        print(f"Successfully parsed {len(logs):,} log entries")
        
    def parse_log_chunk(self, chunk):
        """
        Parse a chunk of log lines into structured data.
        
        Args:
            chunk (list): List of log lines to parse
            
        Returns:
            list: List of parsed log dictionaries
        """
        parsed_chunk = []
        
        for line in chunk:
            if not line.strip():
                continue
                
            log_entry = self.parse_log_line(line)
            if log_entry:
                parsed_chunk.append(log_entry)
        
        return parsed_chunk
    
    def parse_log_line(self, line):
        """
        Parse a single log line. Adapt this method based on your log format.
        
        Args:
            line (str): Single log line
            
        Returns:
            dict: Parsed log entry or None if parsing fails
        """
        try:
            # Common log patterns - adapt based on your log format
            patterns = [
                # Apache/Nginx style: IP - - [timestamp] "method url protocol" status size
                r'(\d+\.\d+\.\d+\.\d+)\s+-\s+-\s+\[([^\]]+)\]\s+"([^"]+)"\s+(\d+)\s+(\d+)',
                
                # Custom format: timestamp level message
                r'(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2})\s+(\w+)\s+(.*)',
                
                # IIS style: date time ip method uri status
                r'(\d{4}-\d{2}-\d{2})\s+(\d{2}:\d{2}:\d{2})\s+(\d+\.\d+\.\d+\.\d+)\s+(\w+)\s+([^\s]+)\s+(\d+)',
            ]
            
            for pattern in patterns:
                match = re.match(pattern, line)
                if match:
                    return self.extract_log_data(match, line)
            
            # If no pattern matches, create basic entry
            return {
                'timestamp': datetime.now(),
                'raw_line': line,
                'parsed': False
            }
            
        except Exception as e:
            return {
                'timestamp': datetime.now(),
                'raw_line': line,
                'error': str(e),
                'parsed': False
            }
    
    def extract_log_data(self, match, line):
        """
        Extract structured data from regex match.
        
        Args:
            match: Regex match object
            line: Original log line
            
        Returns:
            dict: Structured log data
        """
        groups = match.groups()
        
        # Basic structure - adapt based on your log format
        log_data = {
            'raw_line': line,
            'parsed': True
        }
        
        # Try to parse timestamp from first group
        try:
            timestamp_str = groups[0]
            # Handle different timestamp formats
            timestamp_formats = [
                '%Y-%m-%d %H:%M:%S',
                '%d/%b/%Y:%H:%M:%S %z',
                '%Y-%m-%d',
            ]
            
            for fmt in timestamp_formats:
                try:
                    log_data['timestamp'] = datetime.strptime(timestamp_str, fmt)
                    break
                except ValueError:
                    continue
            else:
                log_data['timestamp'] = datetime.now()
                
        except:
            log_data['timestamp'] = datetime.now()
        
        # Add other fields based on available groups
        if len(groups) > 1:
            log_data['ip_address'] = groups[0] if self.is_ip_address(groups[0]) else None
            log_data['method'] = groups[2] if len(groups) > 2 else None
            log_data['status_code'] = groups[3] if len(groups) > 3 else None
            log_data['size'] = groups[4] if len(groups) > 4 else None
        
        return log_data
    
    def is_ip_address(self, text):
        """Check if text is a valid IP address."""
        ip_pattern = r'^\d+\.\d+\.\d+\.\d+$'
        return bool(re.match(ip_pattern, text))
    
    def generate_summary_report(self):
        """Generate a comprehensive summary report."""
        if self.data is None or self.data.empty:
            print("No data available for analysis")
            return
        
        print("\n" + "="*50)
        print("NIMBLE STREAMER LOG ANALYSIS SUMMARY")
        print("="*50)
        
        # Basic statistics
        total_entries = len(self.data)
        parsed_entries = len(self.data[self.data['parsed'] == True])
        
        print(f"Total log entries: {total_entries:,}")
        print(f"Successfully parsed: {parsed_entries:,}")
        print(f"Parse success rate: {(parsed_entries/total_entries)*100:.2f}%")
        
        # Time range analysis
        if 'timestamp' in self.data.columns:
            timestamps = pd.to_datetime(self.data['timestamp'])
            print(f"Log time range: {timestamps.min()} to {timestamps.max()}")
            print(f"Log duration: {timestamps.max() - timestamps.min()}")
        
        # IP address analysis
        if 'ip_address' in self.data.columns:
            unique_ips = self.data['ip_address'].nunique()
            top_ips = self.data['ip_address'].value_counts().head(10)
            print(f"\nUnique IP addresses: {unique_ips:,}")
            print("\nTop 10 IP addresses:")
            for ip, count in top_ips.items():
                if ip:
                    print(f"  {ip}: {count:,} requests")
        
        # Status code analysis
        if 'status_code' in self.data.columns:
            status_counts = self.data['status_code'].value_counts()
            print(f"\nStatus code distribution:")
            for status, count in status_counts.items():
                if status:
                    print(f"  {status}: {count:,} ({(count/total_entries)*100:.2f}%)")
        
        self.reports['summary'] = {
            'total_entries': total_entries,
            'parsed_entries': parsed_entries,
            'parse_rate': (parsed_entries/total_entries)*100,
            'analysis_timestamp': datetime.now()
        }
    
    def generate_time_analysis(self):
        """Generate time-based analysis and visualizations."""
        if 'timestamp' not in self.data.columns:
            print("No timestamp data available for time analysis")
            return
        
        print("\n" + "="*50)
        print("TIME-BASED ANALYSIS")
        print("="*50)
        
        # Convert to datetime if not already
        self.data['timestamp'] = pd.to_datetime(self.data['timestamp'])
        self.data['hour'] = self.data['timestamp'].dt.hour
        self.data['day_of_week'] = self.data['timestamp'].dt.day_name()
        
        # Hourly distribution
        hourly_counts = self.data['hour'].value_counts().sort_index()
        print("\nHourly request distribution:")
        for hour, count in hourly_counts.items():
            print(f"  {hour:02d}:00 - {count:,} requests")
        
        # Daily distribution
        daily_counts = self.data['day_of_week'].value_counts()
        print(f"\nDaily request distribution:")
        for day, count in daily_counts.items():
            print(f"  {day}: {count:,} requests")
    
    def create_visualizations(self, output_dir="reports"):
        """Create visualizations and save them to files."""
        if self.data is None or self.data.empty:
            print("No data available for visualization")
            return
        
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        
        plt.style.use('default')
        
        # 1. Hourly request distribution
        if 'hour' in self.data.columns:
            plt.figure(figsize=(12, 6))
            hourly_counts = self.data['hour'].value_counts().sort_index()
            plt.bar(hourly_counts.index, hourly_counts.values)
            plt.title('Request Distribution by Hour')
            plt.xlabel('Hour of Day')
            plt.ylabel('Number of Requests')
            plt.xticks(range(0, 24))
            plt.grid(True, alpha=0.3)
            plt.tight_layout()
            plt.savefig(f'{output_dir}/hourly_distribution.png', dpi=300, bbox_inches='tight')
            plt.close()
        
        # 2. Status code distribution
        if 'status_code' in self.data.columns:
            plt.figure(figsize=(10, 6))
            status_counts = self.data['status_code'].value_counts()
            plt.pie(status_counts.values, labels=status_counts.index, autopct='%1.1f%%')
            plt.title('Status Code Distribution')
            plt.axis('equal')
            plt.tight_layout()
            plt.savefig(f'{output_dir}/status_code_distribution.png', dpi=300, bbox_inches='tight')
            plt.close()
        
        # 3. Timeline plot
        if 'timestamp' in self.data.columns:
            plt.figure(figsize=(14, 6))
            daily_requests = self.data.groupby(self.data['timestamp'].dt.date).size()
            plt.plot(daily_requests.index, daily_requests.values, marker='o')
            plt.title('Daily Request Volume Over Time')
            plt.xlabel('Date')
            plt.ylabel('Number of Requests')
            plt.xticks(rotation=45)
            plt.grid(True, alpha=0.3)
            plt.tight_layout()
            plt.savefig(f'{output_dir}/timeline.png', dpi=300, bbox_inches='tight')
            plt.close()
        
        print(f"Visualizations saved to '{output_dir}' directory")
    
    def export_reports(self, output_dir="reports"):
        """Export detailed reports to Excel and CSV files."""
        if self.data is None or self.data.empty:
            print("No data available for export")
            return
        
        os.makedirs(output_dir, exist_ok=True)
        
        # Export to CSV
        csv_file = f"{output_dir}/log_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        self.data.to_csv(csv_file, index=False)
        
        # Export to Excel with multiple sheets
        excel_file = f"{output_dir}/log_analysis_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        
        with pd.ExcelWriter(excel_file, engine='openpyxl') as writer:
            # Main data
            self.data.to_excel(writer, sheet_name='Raw Data', index=False)
            
            # Summary statistics
            if 'ip_address' in self.data.columns:
                ip_summary = self.data['ip_address'].value_counts().head(50)
                ip_summary.to_excel(writer, sheet_name='Top IPs')
            
            if 'status_code' in self.data.columns:
                status_summary = self.data['status_code'].value_counts()
                status_summary.to_excel(writer, sheet_name='Status Codes')
            
            if 'hour' in self.data.columns:
                hourly_summary = self.data['hour'].value_counts().sort_index()
                hourly_summary.to_excel(writer, sheet_name='Hourly Distribution')
        
        print(f"Reports exported:")
        print(f"  CSV: {csv_file}")
        print(f"  Excel: {excel_file}")
    
    def run_full_analysis(self, output_dir="reports"):
        """Run complete analysis pipeline."""
        print("Starting Nimble Streamer Log Analysis...")
        
        # Read and parse log file
        self.read_log_file()
        
        # Generate reports
        self.generate_summary_report()
        self.generate_time_analysis()
        
        # Create visualizations
        self.create_visualizations(output_dir)
        
        # Export reports
        self.export_reports(output_dir)
        
        print(f"\nAnalysis complete! All reports saved to '{output_dir}' directory")

def main():
    """Main function to run the log analyzer."""
    print("Nimble Streamer Log Analyzer")
    print("=" * 40)
    
    # Get log file path from user or use default
    log_file = input("Enter the path to your log file (or press Enter for 'logs/access.log'): ").strip()
    if not log_file:
        log_file = "logs/access.log"
    
    try:
        # Create analyzer instance
        analyzer = NimbleLogAnalyzer(log_file)
        
        # Run analysis
        analyzer.run_full_analysis()
        
    except FileNotFoundError:
        print(f"Error: Log file '{log_file}' not found.")
        print("Please check the file path and try again.")
    except Exception as e:
        print(f"Error during analysis: {str(e)}")
        print("Please check your log file format and try again.")

if __name__ == "__main__":
    main()
