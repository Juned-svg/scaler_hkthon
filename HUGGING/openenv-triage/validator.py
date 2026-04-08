import subprocess
import re
import requests
import time

def validate_service():
    print("--- 1. Testing Service Ping ---")
    try:
        r = requests.get("http://localhost:7860/health") # Ensure you have a health endpoint
        if r.status_code == 200:
            print("SUCCESS: Service is alive.")
    except Exception as e:
        print(f"FAILED: Could not connect to localhost:7860 - {e}")

def validate_logs():
    print("\n--- 2. Testing Inference Logs ---")
    process = subprocess.Popen(['python', 'inference.py'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    stdout, stderr = process.communicate()

    # Check for Mandatory Tags
    start_tags = re.findall(r"\[START\]", stdout)
    step_tags = re.findall(r"\[STEP\]", stdout)
    end_tags = re.findall(r"\[END\]", stdout)

    if len(start_tags) >= 3 and len(step_tags) > 0 and len(end_tags) >= 3:
        print(f"SUCCESS: Found {len(start_tags)} tasks with valid [STEP] logs.")
        # Print logs so user can see it works
        print("\n=== Output snippet ===")
        lines = stdout.split('\n')
        for i in range(min(5, len(lines))): print(lines[i])
        print("...\n" + lines[-2])
    else:
        print(f"FAILED: Log format is incorrect. Found Start: {len(start_tags)}, Steps: {len(step_tags)}")
        print(stdout)
        print(stderr)

if __name__ == "__main__":
    validate_service()
    validate_logs()
