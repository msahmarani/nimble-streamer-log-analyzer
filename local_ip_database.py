"""
Local IP Database Manager
Creates and manages a local SQLite database for IP geolocation data.
Combines data from IPinfo API, MMDB databases, and log analysis.
"""

import sqlite3
import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
import maxminddb
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

class LocalIPDatabase:
    """
    Local SQLite database for storing and managing IP geolocation data.
    Combines multiple sources: IPinfo API, MMDB databases, and log analysis.
    """
    
    def __init__(self, db_path: str = "ip_database.db"):
        self.db_path = db_path
        self.db_lock = threading.Lock()
        self.ipinfo_token: Optional[str] = None
        
        # MMDB database paths
        self.lite_db_path = 'ipinfo_data/ipinfo_lite.mmdb'
        self.lite_reader: Optional[maxminddb.Reader] = None
        
        # Initialize database and MMDB reader
        self._initialize_database()
        self._initialize_mmdb()
        
        print(f"✅ Local IP Database initialized: {db_path}")
    
    def _initialize_database(self):
        """Initialize SQLite database with IP geolocation table."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Create IP data table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS ip_data (
                    ip TEXT PRIMARY KEY,
                    country TEXT,
                    country_code TEXT,
                    country_name TEXT,
                    continent TEXT,
                    continent_code TEXT,
                    region TEXT,
                    city TEXT,
                    asn TEXT,
                    as_name TEXT,
                    as_domain TEXT,
                    org TEXT,
                    isp TEXT,
                    timezone TEXT,
                    is_private INTEGER DEFAULT 0,
                    source TEXT,
                    first_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    query_count INTEGER DEFAULT 1
                )
            ''')
            
            # Create indexes for better performance
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_country ON ip_data(country)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_asn ON ip_data(asn)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_source ON ip_data(source)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_is_private ON ip_data(is_private)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_last_updated ON ip_data(last_updated)')
            
            # Create statistics table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS ip_statistics (
                    ip TEXT PRIMARY KEY,
                    total_requests INTEGER DEFAULT 0,
                    error_requests INTEGER DEFAULT 0,
                    first_request TIMESTAMP,
                    last_request TIMESTAMP,
                    unique_status_codes TEXT,  -- JSON array of status codes
                    reputation_score REAL DEFAULT 0.0,  -- 0-100 reputation score
                    threat_level TEXT DEFAULT 'unknown',  -- low, medium, high, unknown
                    notes TEXT
                )
            ''')
            
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_reputation ON ip_statistics(reputation_score)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_threat ON ip_statistics(threat_level)')
            
            conn.commit()
    
    def _initialize_mmdb(self):
        """Initialize MMDB database reader."""
        try:
            if os.path.exists(self.lite_db_path):
                self.lite_reader = maxminddb.open_database(self.lite_db_path)
                print(f"✅ MMDB database loaded: {self.lite_db_path}")
            else:
                print(f"⚠️  MMDB database not found: {self.lite_db_path}")
        except Exception as e:
            print(f"❌ Error loading MMDB database: {e}")
    
    def set_ipinfo_token(self, token: str):
        """Set IPinfo API token for online lookups."""
        self.ipinfo_token = token
        print("🔑 IPinfo token configured for database")
    
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
    
    def _get_mmdb_data(self, ip: str) -> Optional[Dict[str, Any]]:
        """Get data from MMDB database."""
        if not self.lite_reader:
            return None
            
        try:
            data = self.lite_reader.get(ip)
            if data:
                return {
                    'country': data.get('country', 'Unknown'),
                    'country_code': data.get('country_code', 'XX'),
                    'continent': data.get('continent', 'Unknown'),
                    'continent_code': data.get('continent_code', 'XX'),
                    'asn': data.get('asn', 'Unknown'),
                    'as_name': data.get('as_name', 'Unknown'),
                    'as_domain': data.get('as_domain', 'unknown'),
                    'source': 'mmdb'
                }
            return None
        except Exception as e:
            print(f"⚠️ MMDB lookup error for {ip}: {e}")
            return None
    
    def _get_ipinfo_data(self, ip: str) -> Optional[Dict[str, Any]]:
        """Get data from IPinfo API."""
        if not self.ipinfo_token:
            return None
            
        try:
            headers = {'Authorization': f'Bearer {self.ipinfo_token}'}
            response = requests.get(f'https://ipinfo.io/{ip}/json', headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                # Parse location if available
                region, city = 'Unknown', 'Unknown'
                if 'region' in data:
                    region = data['region']
                if 'city' in data:
                    city = data['city']
                
                return {
                    'country': data.get('country_name', data.get('country', 'Unknown')),
                    'country_code': data.get('country', 'XX'),
                    'region': region,
                    'city': city,
                    'org': data.get('org', 'Unknown'),
                    'asn': data.get('asn', 'Unknown'),
                    'timezone': data.get('timezone', 'Unknown'),
                    'source': 'ipinfo_api'
                }
            return None
        except Exception as e:
            print(f"⚠️ IPinfo API error for {ip}: {e}")
            return None
    
    def get_ip_info(self, ip: str, force_refresh: bool = False) -> Dict[str, Any]:
        """
        Get comprehensive IP information from local database or external sources.
        
        Args:
            ip: IP address to lookup
            force_refresh: Force refresh from external sources
            
        Returns:
            Dict containing IP information
        """
        if not ip:
            return {}
        
        # Check if it's a private IP
        if self._is_private_ip(ip):
            private_info = {
                'ip': ip,
                'country': 'Private',
                'country_code': 'PRIVATE',
                'country_name': 'Private Network',
                'continent': 'Private',
                'continent_code': 'PRIVATE',
                'region': 'Private',
                'city': 'Private Network',
                'asn': 'Private',
                'as_name': 'Private Network',
                'as_domain': 'private',
                'org': 'Private Network',
                'isp': 'Private Network',
                'timezone': 'Unknown',
                'is_private': 1,
                'source': 'private'
            }
            # Store in database for future use
            self._store_ip_data(ip, private_info)
            return private_info
        
        # Check local database first (unless force_refresh)
        if not force_refresh:
            with self.db_lock:
                with sqlite3.connect(self.db_path) as conn:
                    cursor = conn.cursor()
                    cursor.execute('SELECT * FROM ip_data WHERE ip = ?', (ip,))
                    row = cursor.fetchone()
                    
                    if row:
                        # Get column names before UPDATE
                        columns = [desc[0] for desc in cursor.description]
                        
                        # Update query count and last access
                        cursor.execute('''
                            UPDATE ip_data 
                            SET query_count = query_count + 1, last_updated = CURRENT_TIMESTAMP 
                            WHERE ip = ?
                        ''', (ip,))
                        conn.commit()
                        
                        # Convert row to dict
                        result = dict(zip(columns, row))
                        result['from_cache'] = True
                        return result
        
        # Not in database or force refresh - get from external sources
        ip_info = {'ip': ip, 'is_private': 0}
        
        # Try MMDB first (faster)
        mmdb_data = self._get_mmdb_data(ip)
        if mmdb_data:
            ip_info.update(mmdb_data)
        
        # Try IPinfo API for additional data (city, ISP, etc.)
        ipinfo_data = self._get_ipinfo_data(ip)
        if ipinfo_data:
            # Merge data, preferring IPinfo for detailed fields
            ip_info.update(ipinfo_data)
            if mmdb_data:  # If we have MMDB data, combine sources
                ip_info['source'] = 'mmdb+ipinfo_api'
        
        # Fill in missing fields with defaults
        default_fields = {
            'country': 'Unknown',
            'country_code': 'XX',
            'country_name': 'Unknown',
            'continent': 'Unknown',
            'continent_code': 'XX',
            'region': 'Unknown',
            'city': 'Unknown',
            'asn': 'Unknown',
            'as_name': 'Unknown',
            'as_domain': 'unknown',
            'org': 'Unknown',
            'isp': 'Unknown',
            'timezone': 'Unknown',
            'source': 'unknown'
        }
        
        for field, default_value in default_fields.items():
            if field not in ip_info or ip_info[field] in ['', None]:
                ip_info[field] = default_value
        
        # Create ISP field from available data
        if ip_info['isp'] == 'Unknown' and ip_info['org'] != 'Unknown':
            ip_info['isp'] = ip_info['org']
        elif ip_info['isp'] == 'Unknown' and ip_info['as_name'] != 'Unknown':
            ip_info['isp'] = f"{ip_info['as_name']} ({ip_info['asn']})"
        
        # Store in local database
        self._store_ip_data(ip, ip_info)
        
        return ip_info
    
    def _store_ip_data(self, ip: str, data: Dict[str, Any]):
        """Store IP data in local database."""
        with self.db_lock:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Insert or update IP data
                cursor.execute('''
                    INSERT OR REPLACE INTO ip_data (
                        ip, country, country_code, country_name, continent, continent_code,
                        region, city, asn, as_name, as_domain, org, isp, timezone,
                        is_private, source, last_updated, query_count
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP, 
                              COALESCE((SELECT query_count FROM ip_data WHERE ip = ?), 0) + 1)
                ''', (
                    ip,
                    data.get('country', 'Unknown'),
                    data.get('country_code', 'XX'),
                    data.get('country_name', data.get('country', 'Unknown')),
                    data.get('continent', 'Unknown'),
                    data.get('continent_code', 'XX'),
                    data.get('region', 'Unknown'),
                    data.get('city', 'Unknown'),
                    data.get('asn', 'Unknown'),
                    data.get('as_name', 'Unknown'),
                    data.get('as_domain', 'unknown'),
                    data.get('org', 'Unknown'),
                    data.get('isp', data.get('org', 'Unknown')),
                    data.get('timezone', 'Unknown'),
                    data.get('is_private', 0),
                    data.get('source', 'unknown'),
                    ip  # For the COALESCE query
                ))
                conn.commit()
    
    def bulk_import_from_logs(self, ip_list: List[str], max_workers: int = 10) -> Dict[str, int]:
        """
        Import IP data in bulk from logs, using threading for API calls.
        
        Args:
            ip_list: List of unique IP addresses to import
            max_workers: Maximum concurrent threads for API calls
            
        Returns:
            Dict with import statistics
        """
        if not ip_list:
            return {'total': 0, 'cached': 0, 'mmdb': 0, 'api': 0, 'private': 0, 'errors': 0}
        
        stats = {'total': len(ip_list), 'cached': 0, 'mmdb': 0, 'api': 0, 'private': 0, 'errors': 0}
        
        print(f"🔄 Starting bulk import of {len(ip_list)} unique IPs...")
        
        # First pass: check what's already in database
        existing_ips = set()
        with self.db_lock:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                placeholders = ','.join(['?' for _ in ip_list])
                cursor.execute(f'SELECT ip FROM ip_data WHERE ip IN ({placeholders})', ip_list)
                existing_ips = {row[0] for row in cursor.fetchall()}
        
        # IPs that need to be fetched
        new_ips = [ip for ip in ip_list if ip not in existing_ips]
        stats['cached'] = len(existing_ips)
        
        print(f"   📂 {len(existing_ips)} IPs already in database")
        print(f"   🔍 {len(new_ips)} IPs need to be fetched")
        
        if not new_ips:
            return stats
        
        # Process new IPs with threading
        def process_ip(ip):
            try:
                info = self.get_ip_info(ip, force_refresh=False)
                source = info.get('source', 'unknown')
                
                if 'private' in source:
                    return 'private'
                elif 'mmdb' in source:
                    return 'mmdb'
                elif 'api' in source:
                    return 'api'
                else:
                    return 'unknown'
            except Exception as e:
                print(f"⚠️ Error processing {ip}: {e}")
                return 'error'
        
        # Use ThreadPoolExecutor for concurrent processing
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_ip = {executor.submit(process_ip, ip): ip for ip in new_ips}
            
            for i, future in enumerate(as_completed(future_to_ip)):
                result = future.result()
                stats[result] = stats.get(result, 0) + 1
                
                # Progress update every 50 IPs
                if (i + 1) % 50 == 0:
                    progress = (i + 1) / len(new_ips) * 100
                    print(f"   Progress: {progress:.1f}% ({i + 1}/{len(new_ips)})")
        
        print(f"✅ Bulk import completed!")
        print(f"   📊 Statistics: {stats}")
        
        return stats
    
    def update_ip_statistics(self, ip: str, status_code: int, timestamp: datetime):
        """Update IP statistics from log entries."""
        with self.db_lock:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Get existing stats
                cursor.execute('SELECT * FROM ip_statistics WHERE ip = ?', (ip,))
                row = cursor.fetchone()
                
                if row:
                    # Update existing stats
                    total_requests = row[1] + 1
                    error_requests = row[2] + (1 if status_code >= 400 else 0)
                    
                    # Parse existing status codes
                    try:
                        status_codes = json.loads(row[4] or '[]')
                    except:
                        status_codes = []
                    
                    if status_code not in status_codes:
                        status_codes.append(status_code)
                    
                    cursor.execute('''
                        UPDATE ip_statistics 
                        SET total_requests = ?, error_requests = ?, last_request = ?,
                            unique_status_codes = ?
                        WHERE ip = ?
                    ''', (total_requests, error_requests, timestamp, json.dumps(status_codes), ip))
                else:
                    # Create new stats entry
                    cursor.execute('''
                        INSERT INTO ip_statistics 
                        (ip, total_requests, error_requests, first_request, last_request, unique_status_codes)
                        VALUES (?, 1, ?, ?, ?, ?)
                    ''', (ip, 1 if status_code >= 400 else 0, timestamp, timestamp, json.dumps([status_code])))
                
                conn.commit()
    
    def get_database_stats(self) -> Dict[str, Any]:
        """Get comprehensive database statistics."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Basic counts
            cursor.execute('SELECT COUNT(*) FROM ip_data')
            total_ips = cursor.fetchone()[0]
            
            cursor.execute('SELECT COUNT(*) FROM ip_data WHERE is_private = 1')
            private_ips = cursor.fetchone()[0]
            
            # Source breakdown
            cursor.execute('SELECT source, COUNT(*) FROM ip_data GROUP BY source')
            sources = dict(cursor.fetchall())
            
            # Country breakdown
            cursor.execute('SELECT country, COUNT(*) FROM ip_data WHERE is_private = 0 GROUP BY country ORDER BY COUNT(*) DESC LIMIT 10')
            top_countries = cursor.fetchall()
            
            # ASN breakdown
            cursor.execute('SELECT as_name, COUNT(*) FROM ip_data WHERE is_private = 0 AND as_name != "Unknown" GROUP BY as_name ORDER BY COUNT(*) DESC LIMIT 10')
            top_asns = cursor.fetchall()
            
            # Statistics table info
            cursor.execute('SELECT COUNT(*) FROM ip_statistics')
            stats_count = cursor.fetchone()[0]
            
            # Database file size
            db_size = os.path.getsize(self.db_path) / 1024 / 1024  # MB
            
            return {
                'total_ips': total_ips,
                'private_ips': private_ips,
                'public_ips': total_ips - private_ips,
                'sources': sources,
                'top_countries': top_countries,
                'top_asns': top_asns,
                'statistics_entries': stats_count,
                'database_size_mb': round(db_size, 2),
                'mmdb_available': self.lite_reader is not None,
                'ipinfo_configured': self.ipinfo_token is not None
            }
    
    def search_ips(self, criteria: Dict[str, Any], limit: int = 100) -> List[Dict[str, Any]]:
        """
        Search IPs based on various criteria.
        
        Args:
            criteria: Dict with search criteria (country, asn, source, etc.)
            limit: Maximum number of results
            
        Returns:
            List of matching IP records
        """
        where_clauses = []
        params = []
        
        for field, value in criteria.items():
            if field in ['country', 'country_code', 'asn', 'as_name', 'source']:
                where_clauses.append(f"{field} = ?")
                params.append(value)
            elif field == 'is_private':
                where_clauses.append("is_private = ?")
                params.append(1 if value else 0)
        
        where_sql = " AND ".join(where_clauses) if where_clauses else "1=1"
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(f'''
                SELECT * FROM ip_data 
                WHERE {where_sql} 
                ORDER BY query_count DESC 
                LIMIT ?
            ''', params + [limit])
            
            rows = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description]
            
            return [dict(zip(columns, row)) for row in rows]
    
    def export_to_csv(self, filename: str = None) -> str:
        """Export IP database to CSV file."""
        if not filename:
            filename = f"ip_database_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        import pandas as pd
        
        with sqlite3.connect(self.db_path) as conn:
            df = pd.read_sql_query('SELECT * FROM ip_data', conn)
            df.to_csv(filename, index=False)
        
        print(f"✅ Database exported to: {filename}")
        return filename
    
    def cleanup_old_entries(self, days_old: int = 30) -> int:
        """Remove entries older than specified days."""
        cutoff_date = datetime.now() - timedelta(days=days_old)
        
        with self.db_lock:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('DELETE FROM ip_data WHERE last_updated < ?', (cutoff_date,))
                deleted_count = cursor.rowcount
                conn.commit()
        
        print(f"🧹 Cleaned up {deleted_count} old entries")
        return deleted_count
    
    def close(self):
        """Close database connections and MMDB reader."""
        if self.lite_reader:
            self.lite_reader.close()
            self.lite_reader = None
        
        print("🔐 Local IP Database closed")


# Global instance
local_ip_db = LocalIPDatabase()

def get_local_ip_info(ip: str) -> Dict[str, Any]:
    """Convenience function to get IP info from local database."""
    return local_ip_db.get_ip_info(ip)

def set_local_ipinfo_token(token: str):
    """Convenience function to set IPinfo token."""
    local_ip_db.set_ipinfo_token(token)
