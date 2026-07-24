#!/usr/bin/env python3
"""
Enterprise C2 Detection Lab - Automated Beacon Analyzer
Description: Parses network connection logs to identify potential C2 beaconing activity
             based on recurring time intervals and jitter patterns.
"""

import csv
import re
from datetime import datetime
from collections import defaultdict

# Configuration: Target parameters for Sliver mTLS Beacon
TARGET_PORT = "8888"
EXPECTED_INTERVAL = 30  # seconds
JITTER_ALLOWANCE = 10   # seconds

def analyze_beacon_logs(log_file):
    print(f"[*] Initializing SOC Log File Analyzer for: {log_file}")
    print(f"[*] Hunting for beacon intervals: ~{EXPECTED_INTERVAL}s (Jitter: {JITTER_ALLOWANCE}s)")
    print("-" * 60)
    
    # Dictionary to store connection timestamps between IP pairs
    connections = defaultdict(list)
    
    try:
        with open(log_file, 'r') as file:
            # Assuming a standard Zeek/CSV log format: ts, uid, id.orig_h, id.orig_p, id.resp_h, id.resp_p
            reader = csv.reader(file, delimiter='\t')
            for row in reader:
                # Skip comments or headers in logs
                if row[0].startswith('#') or len(row) < 6:
                    continue
                
                timestamp, src_ip, src_port, dst_ip, dst_port = row[0], row[2], row[3], row[4], row[5]
                
                # Filter for our specific suspect port
                if dst_port == TARGET_PORT:
                    connections[(src_ip, dst_ip)].append(float(timestamp))
                    
    except FileNotFoundError:
        print("[!] Error: Log file not found. Please provide a valid Zeek conn.log file.")
        return

    # Analyze the time deltas for beaconing patterns
    for (src, dst), timestamps in connections.items():
        if len(timestamps) < 3:
            continue # Need at least 3 connections to establish a pattern
            
        print(f"[+] Analyzing traffic from {src} -> {dst} on port {TARGET_PORT}")
        timestamps.sort()
        
        beacon_hits = 0
        for i in range(1, len(timestamps)):
            delta = timestamps[i] - timestamps[i-1]
            
            # Check if the time difference falls within our expected beacon + jitter window
            if (EXPECTED_INTERVAL - JITTER_ALLOWANCE) <= delta <= (EXPECTED_INTERVAL + JITTER_ALLOWANCE):
                beacon_hits += 1
                
        # If multiple consistent intervals are found, flag it!
        if beacon_hits >= 2:
            print(f"[!] SOC ALERT: High confidence mTLS Beaconing detected!")
            print(f"    - Source: {src}")
            print(f"    - Destination: {dst}")
            print(f"    - Consistent Interval Hits: {beacon_hits}")
            print(f"    - Action Required: Initiate containment via endpoint process termination.\n")
        else:
            print(f"[-] No consistent beaconing pattern found for {src}.\n")

if __name__ == "__main__":
    # Example usage (Point this to your generated Zeek conn.log)
    # analyze_beacon_logs("zeek_logs/conn.log")
    print("[*] Script ready. Uncomment the function call to run against live logs.")
