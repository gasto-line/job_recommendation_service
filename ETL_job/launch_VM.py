import subprocess, time, requests
from requests.exceptions import RequestException

def launch_inference_instance(VM_provisioning_script_path: str, instance_type: str):
    """Run full EC2 provisioning and inference workflow, returning job embeddings."""
    print("running the launch_function")
    # Step 1: Launch instance
    try:
        print("running the bash script through subprocess")
        result = subprocess.run(
            ["bash", VM_provisioning_script_path, instance_type]
            , capture_output=True
            , text=True
            , check=True
            , timeout=60
        )
        public_ip = result.stdout.strip().split("\n")[0]
        instance_id = result.stdout.strip().split("\n")[1]
        print(f"✅ Public IP: {public_ip}")
        print("STDOUT:", result.stdout)
        print("STDERR:", result.stderr)
    
    except subprocess.CalledProcessError as e:
        print("❌ EC2 provisioning script failed!")
        print("Return code:", e.returncode)
        print("STDOUT:", e.stdout)
        print("STDERR:", e.stderr)
        raise  # important: re-raise to fail the workflow

    # Step 2: Wait for the app
    url = f"http://{public_ip}:8080/health"
    while True:
        try:
            r = requests.get(url, timeout=3)
            if r.status_code == 200:
                print("✅ App is ready!")
                break
        except RequestException:
            pass
        time.sleep(30)
        print("Waiting for the app to be ready...")
    return (public_ip,instance_id)

if __name__ == "__main__":
    launch_inference_instance("workflow_VM/VM_config.sh", "t3.micro") 