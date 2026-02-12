"""
Quick Network Link Generator
Run this to get your shareable web app link instantly!
"""

import socket
import sys

def get_local_ip():
    """Get the local IP address of this machine"""
    try:
        # Create a socket to determine local IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # Connect to an external address (doesn't actually send data)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except Exception:
        return None

def main():
    print("\n" + "="*70)
    print("  🌐 PARKEASE - SHAREABLE NETWORK LINK GENERATOR")
    print("="*70)
    
    # Get local IP
    ip_address = get_local_ip()
    
    if ip_address:
        print(f"\n✅ Your Computer's IP Address: {ip_address}")
        print(f"\n📱 SHARE THIS LINK with anyone on the same WiFi/Network:")
        print(f"\n   🔗 http://{ip_address}:5000")
        print(f"\n" + "="*70)
        print(f"\n📋 Instructions:")
        print(f"   1. Make sure your Flask app is running (python app.py)")
        print(f"   2. Make sure they're on the same WiFi network as you")
        print(f"   3. Send them the link above")
        print(f"   4. They can access your web app from their device!")
        print(f"\n💡 Quick Test:")
        print(f"   - Open this link on your phone (same WiFi): http://{ip_address}:5000")
        print(f"\n⚠️  Firewall Note:")
        print(f"   If they can't connect, run this as Administrator:")
        print(f"   New-NetFirewallRule -DisplayName 'Flask 5000' -Direction Inbound -LocalPort 5000 -Protocol TCP -Action Allow")
        
        print(f"\n" + "="*70)
        
        # Also show all network interfaces
        print(f"\n🔍 All Network Interfaces on Your Computer:")
        print(f"   (Use the one that matches your active WiFi/Ethernet)")
        print(f"\n   - Local IP: {ip_address}")
        print(f"   - Localhost: 127.0.0.1 (only works on this computer)")
        
        hostname = socket.gethostname()
        print(f"   - Hostname: {hostname}")
        
        try:
            all_ips = socket.gethostbyname_ex(hostname)[2]
            for ip in all_ips:
                if ip != '127.0.0.1':
                    print(f"   - Alternative: {ip}")
        except:
            pass
        
        print(f"\n" + "="*70 + "\n")
        
    else:
        print("\n❌ Could not determine IP address.")
        print("   Please run 'ipconfig' manually and look for IPv4 Address\n")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
