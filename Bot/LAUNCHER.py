import subprocess
import sys
import time
import psutil
from Server import kill_api_server

CPU_THRESHOLD = 80  # in percent
MEMORY_THRESHOLD = 80  # in percent

def monitor_resources(process):
    try:
        if process.poll() is None:  # Process is still running
            proc_info = psutil.Process(process.pid)
            cpu_usage = proc_info.cpu_percent(interval=1) / psutil.cpu_count()
            memory_usage = proc_info.memory_percent()
            if cpu_usage > CPU_THRESHOLD or memory_usage > MEMORY_THRESHOLD:
                return True
        return False
    except psutil.NoSuchProcess:
        return False

def run_and_monitor(script_name, *args):
    while True:
        process = subprocess.Popen([sys.executable, script_name] + list(args))
        print(f"Started {script_name} with PID {process.pid}")
        while process.poll() is None:  # Process is still running
            if monitor_resources(process):
                kill_api_server()
                process.kill()
                print(f"{script_name} was restarted due to high resource usage.")
                break
            time.sleep(2)  # Check resource usage every 2 seconds
        print(f"{script_name} exited with code {process.returncode}. Restarting...")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python LAUNCHER.py [is_alternate_bot (int)]")
        sys.exit(1)
    script_args = sys.argv[1:]
    run_and_monitor("COOKIEBOT.py", *script_args)
