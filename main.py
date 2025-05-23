import os
import time
import requests
import json
from datetime import datetime

class CloudflareDDNS:
    def __init__(self):
        self.api_token = os.getenv('CLOUDFLARE_API_TOKEN')
        self.zone_id = os.getenv('CLOUDFLARE_ZONE_ID')
        self.record_name = os.getenv('RECORD_NAME')
        self.record_id = os.getenv('RECORD_ID', '')
        self.update_interval = int(os.getenv('UPDATE_INTERVAL', '300'))  # 5 minutes default
        
        self.headers = {
            'Authorization': f'Bearer {self.api_token}',
            'Content-Type': 'application/json'
        }
        
    def get_public_ip(self):
        """Get current public IP address"""
        try:
            response = requests.get('https://api.ipify.org?format=json', timeout=10)
            return response.json()['ip']
        except Exception as e:
            print(f"Error getting public IP: {e}")
            return None
    
    def get_dns_record(self):
        """Get current DNS record from Cloudflare"""
        try:
            url = f'https://api.cloudflare.com/client/v4/zones/{self.zone_id}/dns_records'
            params = {'name': self.record_name, 'type': 'A'}
            
            response = requests.get(url, headers=self.headers, params=params, timeout=10)
            data = response.json()
            
            if data['success'] and data['result']:
                record = data['result'][0]
                self.record_id = record['id']
                return record['content']
            else:
                print(f"Error getting DNS record: {data.get('errors', 'Unknown error')}")
                return None
        except Exception as e:
            print(f"Error getting DNS record: {e}")
            return None
    
    def update_dns_record(self, new_ip):
        """Update DNS record with new IP"""
        try:
            url = f'https://api.cloudflare.com/client/v4/zones/{self.zone_id}/dns_records/{self.record_id}'
            data = {
                'type': 'A',
                'name': self.record_name,
                'content': new_ip,
                'ttl': 300
            }
            
            response = requests.put(url, headers=self.headers, json=data, timeout=10)
            result = response.json()
            
            if result['success']:
                print(f"✅ DNS record updated successfully: {self.record_name} -> {new_ip}")
                return True
            else:
                print(f"❌ Error updating DNS record: {result.get('errors', 'Unknown error')}")
                return False
        except Exception as e:
            print(f"❌ Error updating DNS record: {e}")
            return False
    
    def run(self):
        """Main loop to check and update IP"""
        print(f"🚀 Starting Cloudflare DDNS updater for {self.record_name}")
        print(f"⏰ Update interval: {self.update_interval} seconds")
        
        last_ip = None
        
        while True:
            try:
                current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                print(f"\n[{current_time}] Checking IP address...")
                
                # Get current public IP
                public_ip = self.get_public_ip()
                if not public_ip:
                    print("⚠️ Failed to get public IP, retrying in 60 seconds...")
                    time.sleep(60)
                    continue
                
                print(f"🌐 Current public IP: {public_ip}")
                
                # Check if IP changed
                if public_ip != last_ip:
                    # Get current DNS record
                    dns_ip = self.get_dns_record()
                    if not dns_ip:
                        print("⚠️ Failed to get DNS record, retrying...")
                        time.sleep(60)
                        continue
                    
                    print(f"📋 Current DNS record: {dns_ip}")
                    
                    # Update if different
                    if public_ip != dns_ip:
                        print(f"🔄 IP changed from {dns_ip} to {public_ip}, updating...")
                        if self.update_dns_record(public_ip):
                            last_ip = public_ip
                    else:
                        print("✅ DNS record already up to date")
                        last_ip = public_ip
                else:
                    print("✅ IP unchanged, no update needed")
                
                # Wait before next check
                print(f"⏳ Waiting {self.update_interval} seconds until next check...")
                time.sleep(self.update_interval)
                
            except KeyboardInterrupt:
                print("\n👋 Shutting down gracefully...")
                break
            except Exception as e:
                print(f"❌ Unexpected error: {e}")
                print("⏳ Retrying in 60 seconds...")
                time.sleep(60)

def main():
    # Check required environment variables
    required_vars = ['CLOUDFLARE_API_TOKEN', 'CLOUDFLARE_ZONE_ID', 'RECORD_NAME']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print("❌ Missing required environment variables:")
        for var in missing_vars:
            print(f"   - {var}")
        print("\nPlease set these environment variables and try again.")
        return
    
    # Start the DDNS updater
    ddns = CloudflareDDNS()
    ddns.run()

if __name__ == "__main__":
    main()