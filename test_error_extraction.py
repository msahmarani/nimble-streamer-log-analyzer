#!/usr/bin/env python3
"""
Test script to verify HTTP error extraction from Nimble logs
"""

from nimble_app_log_parser import NimbleApplicationLogParser

def test_error_extraction():
    """Test the new HTTP error and URL extraction features."""
    
    print("🧪 Testing Enhanced Nimble Log Parser")
    print("=" * 50)
    
    # Sample log lines based on your example
    test_lines = [
        "[2024-07-22 14:30:00 12345-67890] [mpeg2tscamera0] E: http error code=404 for url='http://116.202.233.40:333/stream/tv1/hollywoodhd/master.m3u8?u=rus&p=d7'",
        "[2024-07-22 14:31:15 12345-67891] [streaming] E: http error code=500 for url='http://server.com/stream/app2/stream123/playlist.m3u8'",
        "[2024-07-22 14:32:00 12345-67892] [connection] I: Stream started successfully",
        "[2024-07-22 14:33:00 12345-67893] [mpeg2ts] E: http error code=403 for url='http://cdn.example.com/stream/live/news/index.m3u8?token=abc'"
    ]
    
    parser = NimbleApplicationLogParser()
    
    for i, line in enumerate(test_lines, 1):
        print(f"\n📝 Test Line {i}:")
        print(f"Input: {line}")
        
        result = parser.parse_line(line)
        
        if result and result.get('parsed'):
            print("✅ Successfully parsed!")
            print(f"   Level: {result.get('level')}")
            print(f"   Component: {result.get('component')}")
            print(f"   Message: {result.get('message')}")
            
            # Check for HTTP error details
            if result.get('has_http_error'):
                print(f"🚨 HTTP Error Detected:")
                print(f"   Error Code: {result.get('http_error_code')}")
                print(f"   Error Type: {result.get('error_type')}")
                print(f"   Error URL: {result.get('error_url')}")
                
            # Check for stream details
            if result.get('has_stream_info'):
                print(f"📺 Stream Info Detected:")
                print(f"   App Name: {result.get('app_name')}")
                print(f"   Stream Name: {result.get('stream_name')}")
                print(f"   Stream Path: {result.get('stream_path')}")
                print(f"   Full URL: {result.get('full_url')}")
        else:
            print("❌ Failed to parse")
            
    print("\n" + "=" * 50)
    print("🎯 Expected Results:")
    print("- Line 1: Error 404, App: tv1, Stream: hollywoodhd")
    print("- Line 2: Error 500, App: app2, Stream: stream123") 
    print("- Line 3: No errors (info message)")
    print("- Line 4: Error 403, App: live, Stream: news")

if __name__ == "__main__":
    test_error_extraction()
