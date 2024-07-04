import subprocess
import sys

def run_and_monitor(script_name, *args):
    while True:
        process = subprocess.Popen([sys.executable, script_name] + list(args))
        process.wait()
        print(f"{script_name} exited with code {process.returncode}. Restarting...")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python LAUNCHER.py [isBombot]")
        sys.exit(1)
    script_to_run = "COOKIEBOT.py"
    script_args = sys.argv[1:]
    run_and_monitor(script_to_run, *script_args)