"""
IPinfo Integration Module for Nimble Streamer Log Analyzer

This module provides IP geolocation and ISP information using IPinfo Lite API.
It includes caching to minimize API calls and batch processing for efficiency.
"""

import requests
import json
import time
from typing import Dict, List, Optional
import pandas as pd
from tqdm import tqdm
import os
from datetime import datetime, timedelta

class IPInfoService:
    """
    Service class for fetching IP information from IPinfo Lite API.
    
    Features:
    - API rate limiting and error handling
    - Local caching to reduce API calls
    - Batch processing for multiple IPs
    - Support for both free and paid IPinfo plans
    """
    
    def __init__(self, api_token: Optional[str] = None, cache_file: str = "ip_cache.json"):
        """
        Initialize IPinfo service.
        
        Args:
            api_token: IPinfo API token (optional for basic usage)
            cache_file: Path to cache file for storing IP data
        """
        self.api_token = api_token
        self.cache_file = cache_file
        self.cache = self._load_cache()
        self.base_url = "https://ipinfo.io"
        self.lite_url = "https://api.ipinfo.io/lite"
        self.rate_limit_delay = 1.0  # Delay between requests (seconds)
        self.max_retries = 3
        
    def _load_cache(self) -> Dict:
        """Load IP cache from file."""
        try:
            if os.path.exists(self.cache_file):
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    cache_data = json.load(f)
                    # Clean old entries (older than 7 days)
                    cutoff_time = datetime.now() - timedelta(days=7)
                    cleaned_cache = {}
                    for ip, data in cache_data.items():
                        if 'cached_at' in data:
                            cached_at = datetime.fromisoformat(data['cached_at'])
                            if cached_at > cutoff_time:
                                cleaned_cache[ip] = data
                    return cleaned_cache
        except Exception as e:
            print(f"Warning: Could not load IP cache: {e}")
        return {}
    
    def _save_cache(self):
        """Save IP cache to file."""
        try:
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(self.cache, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Warning: Could not save IP cache: {e}")
    
    def _is_private_ip(self, ip: str) -> bool:
        """Check if IP is private/internal."""
        try:
            parts = ip.split('.')
            if len(parts) != 4:
                return True  # Invalid format, treat as private
            
            first_octet = int(parts[0])
            second_octet = int(parts[1])
            
            # Private IP ranges
            if first_octet == 10:
                return True
            elif first_octet == 172 and 16 <= second_octet <= 31:
                return True
            elif first_octet == 192 and second_octet == 168:
                return True
            elif first_octet == 127:  # Localhost
                return True
            elif ip.startswith('169.254'):  # Link-local
                return True
            
            return False
        except:
            return True
    
    def get_ip_info(self, ip: str, use_lite: bool = True) -> Dict:
        """
        Get information for a single IP address.
        
        Args:
            ip: IP address to lookup
            use_lite: Whether to use IPinfo Lite API (country/ASN only)
            
        Returns:
            Dictionary containing IP information
        """
        # Check if IP is private
        if self._is_private_ip(ip):
            return {
                'ip': ip,
                'country': 'Private/Internal',
                'region': 'Private Network',
                'city': 'Private Network',
                'org': 'Private Network',
                'postal': '',
                'timezone': '',
                'loc': '',
                'hostname': '',
                'anycast': False,
                'is_private': True,
                'cached_at': datetime.now().isoformat()
            }
        
        # Check cache first
        if ip in self.cache:
            return self.cache[ip]
        
        # Make API request
        try:
            if use_lite and self.api_token:
                # Use IPinfo Lite API
                url = f"{self.lite_url}/{ip}"
                params = {'token': self.api_token}
            else:
                # Use regular API (limited free tier)
                url = f"{self.base_url}/{ip}/json"
                params = {'token': self.api_token} if self.api_token else {}
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                data['ip'] = ip
                data['is_private'] = False
                data['cached_at'] = datetime.now().isoformat()
                
                # Cache the result
                self.cache[ip] = data
                self._save_cache()
                
                # Rate limiting
                time.sleep(self.rate_limit_delay)
                
                return data
            else:
                print(f"IPinfo API error for {ip}: {response.status_code}")
                return self._get_fallback_info(ip)
                
        except Exception as e:
            print(f"Error fetching IP info for {ip}: {e}")
            return self._get_fallback_info(ip)
    
    def _get_fallback_info(self, ip: str) -> Dict:
        """Get fallback info when API fails."""
        return {
            'ip': ip,
            'country': 'Unknown',
            'region': 'Unknown',
            'city': 'Unknown',
            'org': 'Unknown',
            'postal': '',
            'timezone': '',
            'loc': '',
            'hostname': '',
            'anycast': False,
            'is_private': False,
            'cached_at': datetime.now().isoformat()
        }
    
    def batch_lookup(self, ip_list: List[str], use_lite: bool = True) -> pd.DataFrame:
        """
        Perform batch lookup for multiple IP addresses.
        
        Args:
            ip_list: List of IP addresses to lookup
            use_lite: Whether to use IPinfo Lite API
            
        Returns:
            DataFrame with IP information
        """
        results = []
        unique_ips = list(set(ip_list))  # Remove duplicates
        
        print(f"🌐 Looking up information for {len(unique_ips)} unique IP addresses...")
        
        for ip in tqdm(unique_ips, desc="Fetching IP info"):
            try:
                info = self.get_ip_info(ip, use_lite)
                results.append(info)
            except Exception as e:
                print(f"Error processing {ip}: {e}")
                results.append(self._get_fallback_info(ip))
        
        return pd.DataFrame(results)
    
    def enrich_dataframe(self, df: pd.DataFrame, ip_column: str = 'ip_address') -> pd.DataFrame:
        """
        Enrich a dataframe with IP information.
        
        Args:
            df: Input dataframe containing IP addresses
            ip_column: Name of the column containing IP addresses
            
        Returns:
            Enriched dataframe with IP information
        """
        if ip_column not in df.columns:
            print(f"Warning: Column '{ip_column}' not found in dataframe")
            return df
        
        # Get unique IPs from the dataframe
        valid_ips = df[df[ip_column].notna() & (df[ip_column] != '')]
        if valid_ips.empty:
            print("No valid IP addresses found for enrichment")
            return df
        
        unique_ips = valid_ips[ip_column].unique().tolist()
        
        # Batch lookup
        ip_info_df = self.batch_lookup(unique_ips)
        
        # Merge with original dataframe
        ip_info_df = ip_info_df.rename(columns={'ip': ip_column})
        enriched_df = df.merge(ip_info_df, on=ip_column, how='left')
        
        return enriched_df
    
    def get_country_stats(self, df: pd.DataFrame) -> pd.DataFrame:
        """Get country statistics from enriched dataframe."""
        if 'country' not in df.columns:
            return pd.DataFrame()
        
        country_stats = df.groupby('country').agg({
            'ip_address': 'count',
            'country': 'first'
        }).rename(columns={'ip_address': 'request_count'})
        
        country_stats['percentage'] = (country_stats['request_count'] / len(df) * 100).round(2)
        
        return country_stats.sort_values('request_count', ascending=False)
    
    def get_org_stats(self, df: pd.DataFrame) -> pd.DataFrame:
        """Get organization/ISP statistics from enriched dataframe."""
        if 'org' not in df.columns:
            return pd.DataFrame()
        
        org_stats = df.groupby('org').agg({
            'ip_address': 'count',
            'org': 'first'
        }).rename(columns={'ip_address': 'request_count'})
        
        org_stats['percentage'] = (org_stats['request_count'] / len(df) * 100).round(2)
        
        return org_stats.sort_values('request_count', ascending=False)

# Global instance
_ipinfo_service = None

def get_ipinfo_service(api_token: Optional[str] = None) -> IPInfoService:
    """Get global IPinfo service instance."""
    global _ipinfo_service
    if _ipinfo_service is None:
        _ipinfo_service = IPInfoService(api_token)
    return _ipinfo_service

def set_ipinfo_token(token: str):
    """Set IPinfo API token."""
    global _ipinfo_service
    _ipinfo_service = IPInfoService(token)
