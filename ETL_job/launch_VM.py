import subprocess, time, requests
from requests.exceptions import RequestException

def launch_instance(VM_provisioning_script_path: str, user_data_path: str, instance_type: str):
    print("🚀 Launching inference instance")

    # Step 1: Launch instance
    result = subprocess.run(
        ["bash", VM_provisioning_script_path, user_data_path, instance_type],
        capture_output=True,
        text=True,
        check=True,
        timeout=60,
    )

    public_ip, instance_id = result.stdout.strip().split()
    if not public_ip or not instance_id:
        raise RuntimeError("Provisioning script returned empty identifiers")
    print(f"✅ Public IP: {public_ip}")

    # Step 2: Wait for the app
    url = f"http://{public_ip}:8080/health"
    start = time.time()
    max_wait = 600  # 10 minutes

    while time.time() - start < max_wait:
        try:
            r = requests.get(url, timeout=3)
            if r.status_code == 200:
                print("✅ App is ready!")
                return public_ip, instance_id
        except RequestException:
            pass

        print("Waiting for the app to be ready...")
        time.sleep(30)

    raise TimeoutError("Inference app did not become ready in time")

if __name__ == "__main__":
    launch_instance("workflow_VM/VM_config.sh","workflow_VM/user_data.sh", "t3.micro") 