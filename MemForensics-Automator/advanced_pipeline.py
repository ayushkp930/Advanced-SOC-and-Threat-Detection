import subprocess
import json
import os
import argparse
from datetime import datetime

# ANSI Colors for a professional terminal UI
RED = '\033[91m'
GREEN = '\033[92m'
YELLOW = '\033[93m'
CYAN = '\033[96m'
RESET = '\033[0m'

# The plugins we want to run automatically
PLUGINS = {
    "pslist": "windows.pslist.PsList",
    "malfind": "windows.malware.malfind.Malfind"
}

class AdvancedMemoryPipeline:
    def __init__(self, vol_path, dump_path, output_dir):
        self.vol_path = vol_path
        self.dump_path = dump_path
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)
        print(f"{CYAN}[*] Initializing Advanced Forensics Pipeline...{RESET}")
        print(f"{CYAN}[*] Target Dump: {self.dump_path}{RESET}\n")

    def run_plugin(self, name, plugin):
        print(f"[*] Executing Plugin: {YELLOW}{plugin}{RESET}...")
        
        cmd = ["python3", self.vol_path, "-f", self.dump_path, "-r", "json", plugin]
        
        try:
            # Run Volatility quietly and capture the JSON output
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            data = json.loads(result.stdout)
            
            # Analyze the data for threats
            self.analyze_results(name, data)
            return data
            
        except Exception as e:
            print(f"{RED}[!] Failed to run {plugin}: {e}{RESET}")
            return None

    def analyze_results(self, name, data):
        """This function makes the script 'smart' by interpreting the data."""
        if name == "pslist":
            print(f"{GREEN}[+] Extracted {len(data)} running processes.{RESET}")
            
        elif name == "malfind":
            if len(data) > 0:
                print(f"\n{RED}!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
                print(f"[!] CRITICAL THREAT DETECTED: INJECTED CODE [!]")
                print(f"!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!{RESET}")
                print(f"{RED}[!] Found {len(data)} suspicious memory segments.{RESET}")
                # Print the first threat ID
                if isinstance(data, list) and len(data) > 0:
                    first_hit = data[0]
                    print(f"[!] Example Process ID: {first_hit.get('PID', 'Unknown')} | Protection: {first_hit.get('Protection', 'Unknown')}")
            else:
                print(f"{GREEN}[+] System appears clean. No injected code found.{RESET}")
        print("-" * 50)

    def generate_report(self, results):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_path = os.path.join(self.output_dir, f"threat_report_{timestamp}.json")
        
        with open(report_path, "w") as f:
            json.dump(results, f, indent=4)
            
        print(f"\n{CYAN}[+] Triage Complete. Full evidence saved to: {report_path}{RESET}")

def main():
    parser = argparse.ArgumentParser(description="Advanced Memory Forensics Pipeline")
    parser.add_argument("-v", "--vol", required=True, help="Path to vol.py")
    parser.add_argument("-d", "--dump", required=True, help="Path to memory dump")
    args = parser.parse_args()

    pipeline = AdvancedMemoryPipeline(args.vol, args.dump, "./reports")
    all_results = {}

    for name, plugin in PLUGINS.items():
        data = pipeline.run_plugin(name, plugin)
        if data:
            all_results[name] = data

    pipeline.generate_report(all_results)

if __name__ == "__main__":
    main()
