import os
import subprocess

def run_git_command(command, description):
    print(f"[*] {description}...")
    try:
        # Command ko shell mein run karna
        result = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        print(f"[+] SUCCESS!\n")
    except subprocess.CalledProcessError as e:
        print(f"[-] ERROR occurred:\n{e.stderr}")
        print("Script stopped.")
        exit(1)

def automate_github_upload():
    print("="*50)
    print("🚀 GitHub Automation Script by Ayush")
    print("="*50)
    
    # 1. User se repo URL maangna
    repo_url = input("\n[?] Apne GitHub Repository ka URL paste karein (e.g., https://github.com/username/LotL-Detection-Lab.git):\n> ").strip()
    
    if not repo_url:
        print("[-] URL cannot be empty!")
        return

    commit_message = input("[?] Commit message enter karein (Press Enter for 'Initial Commit: LotL SOC Lab'):\n> ").strip()
    if not commit_message:
        commit_message = "Initial Commit: LotL SOC Lab"

    # Git commands sequence
    commands = [
        ("git init", "Initializing local Git repository"),
        ("git add .", "Adding all files (README.md, images, auto_push.py, etc.)"),
        (f'git commit -m "{commit_message}"', "Committing the files"),
        ("git branch -M main", "Setting main branch"),
        (f"git remote add origin {repo_url}", "Linking to your GitHub repository")
    ]

    for cmd, desc in commands:
        # Check agar remote pehle se add hai toh error ignore karein
        if "remote add" in cmd:
            subprocess.run("git remote remove origin", shell=True, stderr=subprocess.PIPE)
        
        run_git_command(cmd, desc)

    # Push to GitHub
    print("[*] Pushing files to GitHub (yeh aapse GitHub username/token maang sakta hai)...")
    try:
        subprocess.run("git push -u origin main", shell=True, check=True)
        print("\n🎉 BINGO! Aapka project successfully GitHub par upload ho gaya hai!")
        print(f"🔗 Check it out here: {repo_url.replace('.git', '')}")
    except subprocess.CalledProcessError:
        print("\n[-] Push failed! Make sure you have the correct permissions or Personal Access Token (PAT).")

if __name__ == "__main__":
    automate_github_upload()
