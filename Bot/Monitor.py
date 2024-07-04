import subprocess
import time
import sys

def start_main_script(args):
    return subprocess.Popen([sys.executable, 'COOKIEBOT.py'] + args)

def main():
    print("Monitor script started.")
    args = sys.argv[1:]
    process = start_main_script(args)
    while True:
        if process.poll() is not None:
            print("Main script terminated, restarting...")
            process = start_main_script(args)
        time.sleep(5)

if __name__ == "__main__":
    main()
