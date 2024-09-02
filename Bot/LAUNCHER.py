import subprocess
import sys

def run_and_monitor(script_name, *args):
    while True:
        process = subprocess.Popen([sys.executable, script_name] + list(args))
        process.wait()
        print(f"{script_name} exited with code {process.returncode}. Restarting...")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python LAUNCHER.py [is_alternate_bot (int)]")
        sys.exit(1)
    script_args = sys.argv[1:]
    run_and_monitor("COOKIEBOT.py", *script_args)
