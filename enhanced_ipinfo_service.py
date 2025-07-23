"""
Enhanced IPinfo Service with Offline Database Support
Combines offline MMDB databases with online API for comprehensive IP analysis.
Optimized for performance and reliability.
"""

import os
import json
import time
import requests
from datetime import datetime, timedelta
from typing import Dict, Optional, List, Tuple
import maxminddb
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

# Import our local IP database
from local_ip_database import LocalIPDatabase

class EnhancedIPinfoService:
    """Enhanced IPinfo service with offline database support for faster lookups."""
    
    def __init__(self):
        self.token: Optional[str] = None
        self.cache: Dict[str, Dict] = {}
        self.cache_file = 'ipinfo_cache.json'
        self.cache_duration = timedelta(days=7)  # Cache for 7 days
        self._cache_lock = threading.Lock()  # Thread safety for cache
        
        # Initialize local IP database
        self.local_db = LocalIPDatabase()
        
        # Offline database paths
        self.lite_db_path = 'ipinfo_data/ipinfo_lite.mmdb'  # Complete database
        self.country_db_path = 'ipinfo_data/country.mmdb'   # Fallback
        self.city_db_path = 'ipinfo_data/city.mmdb'         # Fallback
        
        # Database readers
        self.lite_reader: Optional[maxminddb.Reader] = None
        self.country_reader: Optional[maxminddb.Reader] = None
        self.city_reader: Optional[maxminddb.Reader] = None
        
        # Statistics
        self.stats = {
            'offline_hits': 0,
            'online_hits': 0,
            'cache_hits': 0,
            'local_db_hits': 0,
            'errors': 0
        }
        
        # Load cache and initialize databases
        self._load_cache()
        self._initialize_databases()
    
    def _initialize_databases(self) -> None:
        """Initialize the MMDB database readers with better error handling."""
        try:
            # Try the comprehensive lite database first
            if os.path.exists(self.lite_db_path):
                self.lite_reader = maxminddb.open_database(self.lite_db_path)
                print(f"✅ Loaded IPinfo Lite database: {self.lite_db_path}")
            else:
                print(f"⚠️  IPinfo Lite database not found: {self.lite_db_path}")
            
            # Load individual databases as fallback
            if os.path.exists(self.country_db_path):
                self.country_reader = maxminddb.open_database(self.country_db_path)
                print(f"✅ Loaded country database: {self.country_db_path}")
            else:
                print(f"⚠️  Country database not found: {self.country_db_path}")
                
            if os.path.exists(self.city_db_path):
                self.city_reader = maxminddb.open_database(self.city_db_path)
                print(f"✅ Loaded city database: {self.city_db_path}")
            else:
                print(f"⚠️  City database not found: {self.city_db_path}")
                
        except Exception as e:
            print(f"❌ Error initializing databases: {e}")
            self.stats['errors'] += 1
    
    def set_ipinfo_token(self, token: str):
        """Set the IPinfo API token for online lookups."""
        self.token = token
        print(f"🔑 IPinfo token configured")
    
    def _load_cache(self) -> None:
        """Load cached IP information from file with better error handling."""
        if not os.path.exists(self.cache_file):
            return
            
        try:
            with open(self.cache_file, 'r', encoding='utf-8') as f:
                cache_data = json.load(f)
                
            # Convert string timestamps back to datetime objects
            for ip, data in cache_data.items():
                if 'timestamp' in data and isinstance(data['timestamp'], str):
                    try:
                        data['timestamp'] = datetime.fromisoformat(data['timestamp'])
                    except ValueError:
                        # Remove invalid cache entry
                        continue
                        
            self.cache = cache_data
            print(f"📂 Loaded {len(self.cache)} cached IP entries")
            
        except (json.JSONDecodeError, OSError, KeyError) as e:
            print(f"⚠️ Error loading cache: {e}")
            self.cache = {}
            self.stats['errors'] += 1
    
    def _save_cache(self) -> None:
        """Save cached IP information to file with atomic write."""
        temp_file = f"{self.cache_file}.tmp"
        
        try:
            # Convert datetime objects to strings for JSON serialization
            cache_to_save = {}
            for ip, data in self.cache.items():
                cache_entry = data.copy()
                if 'timestamp' in cache_entry and isinstance(cache_entry['timestamp'], datetime):
                    cache_entry['timestamp'] = cache_entry['timestamp'].isoformat()
                cache_to_save[ip] = cache_entry
                
            # Atomic write: write to temp file first, then rename
            with open(temp_file, 'w', encoding='utf-8') as f:
                json.dump(cache_to_save, f, indent=2)
                
            # Rename temp file to actual cache file (atomic on most systems)
            os.replace(temp_file, self.cache_file)
            
        except (OSError, ValueError) as e:
            print(f"⚠️ Error saving cache: {e}")
            if os.path.exists(temp_file):
                try:
                    os.remove(temp_file)
                except OSError:
                    pass
            self.stats['errors'] += 1
    
    def _extract_db_value(self, data, key: str, default: str = 'Unknown') -> str:
        """Safely extract value from MMDB data."""
        if data is None:
            return default
        if isinstance(data, dict):
            return str(data.get(key, default))
        return default
    
    def _is_private_ip(self, ip: str) -> bool:
        """Check if IP is private/internal."""
        try:
            parts = list(map(int, ip.split('.')))
            
            # Private IP ranges
            if parts[0] == 10:  # 10.0.0.0/8
                return True
            elif parts[0] == 172 and 16 <= parts[1] <= 31:  # 172.16.0.0/12
                return True
            elif parts[0] == 192 and parts[1] == 168:  # 192.168.0.0/16
                return True
            elif parts[0] == 127:  # 127.0.0.0/8 (localhost)
                return True
            
            return False
        except (ValueError, IndexError):
            return False
    
    def _get_offline_info(self, ip: str) -> Optional[Dict]:
        """Get IP information from offline databases with improved error handling."""
        if self._is_private_ip(ip):
            return {
                'ip': ip,
                'country': 'Private',
                'country_name': 'Private Network',
                'country_code': 'PRIVATE',
                'region': 'Private Network',
                'city': 'Private Network',
                'org': 'Private Network',
                'asn': 'Private',
                'as_name': 'Private Network',
                'as_domain': 'private',
                'continent': 'Private',
                'continent_code': 'PRIVATE',
                'timezone': 'Unknown',
                'source': 'offline_private'
            }
        
        info = {'ip': ip, 'source': 'offline'}
        
        try:
            # Try the comprehensive lite database first
            if self.lite_reader:
                lite_data = self.lite_reader.get(ip)
                if lite_data:
                    # Extract available IPinfo Lite fields (country-level only)
                    info['country'] = self._extract_db_value(lite_data, 'country')
                    info['country_name'] = self._extract_db_value(lite_data, 'country')  # Same as country in lite DB
                    info['country_code'] = self._extract_db_value(lite_data, 'country_code')
                    info['continent'] = self._extract_db_value(lite_data, 'continent')
                    info['continent_code'] = self._extract_db_value(lite_data, 'continent_code')
                    info['asn'] = self._extract_db_value(lite_data, 'asn')
                    info['as_name'] = self._extract_db_value(lite_data, 'as_name')
                    info['as_domain'] = self._extract_db_value(lite_data, 'as_domain')
                    
                    # Map AS info to org field for compatibility
                    if info.get('as_name') != 'Unknown':
                        info['org'] = f"{info['as_name']} ({info['asn']})"
                    else:
                        info['org'] = 'Unknown'
                    
                    # IPinfo Lite doesn't have city/region data - mark as not available
                    info['region'] = 'Not Available (Lite DB)'
                    info['city'] = 'Not Available (Lite DB)'
                    info['timezone'] = 'Unknown'
                    
                    # Check if we got meaningful data
                    if any(k in info and info[k] not in ['Unknown', 'Not Available (Lite DB)'] for k in ['country', 'asn', 'as_name']):
                        return info
            
            # Fallback to separate databases if lite database didn't work
            if self.country_reader:
                country_data = self.country_reader.get(ip)
                if country_data:
                    info['country'] = self._extract_db_value(country_data, 'country')
                    info['country_name'] = self._extract_db_value(country_data, 'country_name')
                    info['country_code'] = self._extract_db_value(country_data, 'country_code', 'XX')
            
            if self.city_reader:
                city_data = self.city_reader.get(ip)
                if city_data:
                    info['region'] = self._extract_db_value(city_data, 'region')
                    info['city'] = self._extract_db_value(city_data, 'city')
                    info['timezone'] = self._extract_db_value(city_data, 'timezone')
            
            # Fill in defaults for missing fields if not set
            for field in ['asn', 'as_name', 'as_domain', 'continent', 'continent_code']:
                if field not in info:
                    info[field] = 'Unknown'
            
            # Set defaults for city-level data if not available from fallback databases
            if 'region' not in info:
                info['region'] = 'Unknown'
            if 'city' not in info:
                info['city'] = 'Unknown' 
            if 'org' not in info:
                info['org'] = 'Unknown'
            
            # Only return if we got meaningful data
            return info if any(k in info and info[k] not in ['Unknown', 'Not Available (Lite DB)'] for k in ['country', 'city', 'asn']) else None
            
        except Exception as e:
            print(f"⚠️ Error reading offline database for {ip}: {e}")
            self.stats['errors'] += 1
            return None
    
    def _get_online_info(self, ip: str) -> Optional[Dict]:
        """Get IP information from IPinfo API."""
        if not self.token:
            return None
            
        try:
            headers = {'Authorization': f'Bearer {self.token}'}
            response = requests.get(f'https://ipinfo.io/{ip}/json', headers=headers, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                data['source'] = 'online'
                return data
            else:
                print(f"⚠️ API request failed for {ip}: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"⚠️ Error fetching online info for {ip}: {e}")
            return None
    
    def get_ip_info(self, ip: str) -> Dict:
        """
        Get comprehensive IP information using local database first, then offline database, then API.
        
        Args:
            ip (str): IP address to lookup
            
        Returns:
            dict: IP information including location, ISP, etc.
        """
        if not ip:
            return {}
        
        # Step 1: Check local database first (fastest)
        local_info = self.local_db.get_ip_info(ip)
        if local_info and local_info.get('country') != 'Unknown':
            self.stats['local_db_hits'] += 1
            return local_info
        
        # Step 2: Check cache
        if ip in self.cache:
            cached_data = self.cache[ip]
            cache_age = datetime.now() - cached_data.get('timestamp', datetime.min)
            
            if cache_age < self.cache_duration:
                self.stats['cache_hits'] += 1
                return cached_data
            else:
                # Cache expired, remove it
                del self.cache[ip]
        
        # Step 3: Try offline database
        ip_info = self._get_offline_info(ip)
        
        # Step 4: If offline lookup didn't provide enough info, try online API
        if not ip_info or (ip_info.get('source') == 'offline' and not ip_info.get('org')):
            online_info = self._get_online_info(ip)
            if online_info:
                # Merge offline and online data, preferring online for detailed info
                if ip_info:
                    ip_info.update(online_info)
                else:
                    ip_info = online_info
        
        # Step 5: Fallback if no info found
        if not ip_info:
            ip_info = {
                'ip': ip,
                'country': 'Unknown',
                'country_name': 'Unknown',
                'country_code': 'XX',
                'region': 'Unknown',
                'city': 'Unknown',
                'org': 'Unknown',
                'asn': 'Unknown',
                'as_name': 'Unknown',
                'as_domain': 'Unknown',
                'continent': 'Unknown',
                'continent_code': 'XX',
                'timezone': 'Unknown',
                'source': 'fallback'
            }
        
        # Step 6: Store in local database for future use
        if ip_info and ip_info.get('source') != 'fallback':
            self.local_db._store_ip_data(ip, ip_info)
        
        # Step 7: Cache the result
        ip_info['timestamp'] = datetime.now().isoformat()
        with self._cache_lock:
            self.cache[ip] = ip_info
            self._save_cache()
        
        return ip_info
    
    def bulk_lookup(self, ip_list: List[str], max_workers: int = 10) -> Dict[str, Dict]:
        """
        Perform bulk IP lookups efficiently with local database first, then threading for online lookups.
        
        Args:
            ip_list: List of IP addresses to lookup
            max_workers: Maximum number of threads for concurrent online lookups
            
        Returns:
            dict: Mapping of IP addresses to their information
        """
        if not ip_list:
            return {}
            
        results = {}
        online_ips = []  # IPs that need online lookup
        
        print(f"🔍 Starting bulk lookup for {len(ip_list)} IPs...")
        
        # First pass: try local database, then cache, then offline databases
        for i, ip in enumerate(ip_list):
            if i % 100 == 0:
                print(f"   Progress: {i}/{len(ip_list)} ({i/len(ip_list)*100:.1f}%)")
            
            # Step 1: Check local database first (fastest)
            local_info = self.local_db.get_ip_info(ip)
            if local_info and local_info.get('country') != 'Unknown':
                results[ip] = local_info
                self.stats['local_db_hits'] += 1
                continue
            
            # Step 2: Check cache
            with self._cache_lock:
                if ip in self.cache:
                    cached_data = self.cache[ip]
                    cache_age = datetime.now() - cached_data.get('timestamp', datetime.min)
                    
                    if cache_age < self.cache_duration:
                        results[ip] = cached_data
                        self.stats['cache_hits'] += 1
                        continue
                    else:
                        del self.cache[ip]
            
            # Step 3: Try offline lookup
            offline_info = self._get_offline_info(ip)
            if offline_info and (offline_info.get('source') == 'offline_private' or 
                                offline_info.get('country', 'Unknown') != 'Unknown'):
                offline_info['timestamp'] = datetime.now()
                results[ip] = offline_info
                self.stats['offline_hits'] += 1
                
                # Store in local database
                self.local_db._store_ip_data(ip, offline_info)
                
                # Cache offline results
                with self._cache_lock:
                    self.cache[ip] = offline_info
            else:
                # Need online lookup
                online_ips.append(ip)
        
        # Second pass: concurrent online lookups for remaining IPs
        if online_ips and self.token:
            print(f"   Online lookups needed: {len(online_ips)}")
            
            def fetch_online(ip):
                info = self._get_online_info(ip)
                if info:
                    info['timestamp'] = datetime.now()
                    self.stats['online_hits'] += 1
                    # Store in local database
                    self.local_db._store_ip_data(ip, info)
                    return ip, info
                return ip, None
            
            with ThreadPoolExecutor(max_workers=min(max_workers, len(online_ips))) as executor:
                future_to_ip = {executor.submit(fetch_online, ip): ip for ip in online_ips}
                
                for future in as_completed(future_to_ip):
                    ip, info = future.result()
                    if info:
                        results[ip] = info
                        with self._cache_lock:
                            self.cache[ip] = info
                    else:
                        # Fallback for failed lookups
                        fallback_info = {
                            'ip': ip,
                            'country': 'Unknown',
                            'country_name': 'Unknown',
                            'country_code': 'XX',
                            'region': 'Unknown',
                            'city': 'Unknown',
                            'org': 'Unknown',
                            'asn': 'Unknown',
                            'as_name': 'Unknown',
                            'as_domain': 'Unknown',
                            'continent': 'Unknown',
                            'continent_code': 'XX',
                            'timezone': 'Unknown',
                            'source': 'fallback',
                            'timestamp': datetime.now()
                        }
                        results[ip] = fallback_info
        
        # Fill in any missing IPs with fallback data
        for ip in ip_list:
            if ip not in results:
                results[ip] = {
                    'ip': ip,
                    'country': 'Unknown',
                    'country_name': 'Unknown',
                    'country_code': 'XX',
                    'region': 'Unknown',
                    'city': 'Unknown',
                    'org': 'Unknown',
                    'asn': 'Unknown',
                    'as_name': 'Unknown',
                    'as_domain': 'Unknown',
                    'continent': 'Unknown',
                    'continent_code': 'XX',
                    'timezone': 'Unknown',
                    'source': 'fallback',
                    'timestamp': datetime.now()
                }
        
        # Save cache after bulk operation
        self._save_cache()
        
        print(f"✅ Completed bulk lookup: {len(results)} IPs processed")
        print(f"   Local DB: {self.stats['local_db_hits']}, Cache: {self.stats['cache_hits']}, Offline: {self.stats['offline_hits']}, Online: {self.stats['online_hits']}")
        
        return results
    
    def get_statistics(self) -> Dict:
        """Get comprehensive service statistics."""
        offline_count = sum(1 for data in self.cache.values() if data.get('source') == 'offline')
        online_count = sum(1 for data in self.cache.values() if data.get('source') == 'online')
        private_count = sum(1 for data in self.cache.values() if data.get('source') == 'offline_private')
        fallback_count = sum(1 for data in self.cache.values() if data.get('source') == 'fallback')
        
        # Check database file sizes
        lite_size = os.path.getsize(self.lite_db_path) if os.path.exists(self.lite_db_path) else 0
        country_size = os.path.getsize(self.country_db_path) if os.path.exists(self.country_db_path) else 0
        city_size = os.path.getsize(self.city_db_path) if os.path.exists(self.city_db_path) else 0
        
        return {
            'total_cached': len(self.cache),
            'offline_lookups': offline_count,
            'online_lookups': online_count,
            'private_ips': private_count,
            'fallback_entries': fallback_count,
            'session_stats': self.stats.copy(),
            'databases_loaded': {
                'lite': self.lite_reader is not None,
                'country': self.country_reader is not None,
                'city': self.city_reader is not None
            },
            'database_sizes': {
                'lite_mb': round(lite_size / 1024 / 1024, 2),
                'country_mb': round(country_size / 1024 / 1024, 2),
                'city_mb': round(city_size / 1024 / 1024, 2)
            },
            'cache_file_size_kb': round(os.path.getsize(self.cache_file) / 1024, 2) if os.path.exists(self.cache_file) else 0
        }
    
    def clear_cache(self, older_than_days: Optional[int] = None) -> int:
        """
        Clear cache entries, optionally only those older than specified days.
        
        Args:
            older_than_days: Only clear entries older than this many days. If None, clear all.
            
        Returns:
            int: Number of entries cleared
        """
        if older_than_days is None:
            cleared = len(self.cache)
            self.cache.clear()
        else:
            cutoff_date = datetime.now() - timedelta(days=older_than_days)
            to_remove = []
            
            for ip, data in self.cache.items():
                if data.get('timestamp', datetime.min) < cutoff_date:
                    to_remove.append(ip)
            
            for ip in to_remove:
                del self.cache[ip]
            
            cleared = len(to_remove)
        
        self._save_cache()
        print(f"🧹 Cleared {cleared} cache entries")
        return cleared
    
    def close(self) -> None:
        """Properly close database connections and save cache."""
        self._save_cache()
        
        if self.lite_reader:
            self.lite_reader.close()
            self.lite_reader = None
            
        if self.country_reader:
            self.country_reader.close()
            self.country_reader = None
            
        if self.city_reader:
            self.city_reader.close()
            self.city_reader = None
        
        print("🔐 Enhanced IPinfo service closed")
    
    def __del__(self):
        """Cleanup: save cache and close databases safely."""
        try:
            if hasattr(self, 'cache') and self.cache:
                self._save_cache()
            
            if hasattr(self, 'lite_reader') and self.lite_reader:
                self.lite_reader.close()
            
            if hasattr(self, 'country_reader') and self.country_reader:
                self.country_reader.close()
            
            if hasattr(self, 'city_reader') and self.city_reader:
                self.city_reader.close()
        except Exception:
            # Silently handle cleanup errors
            pass


# Global enhanced service instance
enhanced_ipinfo_service = EnhancedIPinfoService()

def get_enhanced_ip_info(ip: str) -> Dict:
    """Convenience function to get IP info."""
    return enhanced_ipinfo_service.get_ip_info(ip)

def set_enhanced_ipinfo_token(token: str):
    """Convenience function to set IPinfo token."""
    enhanced_ipinfo_service.set_ipinfo_token(token)
