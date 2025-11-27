#!/bin/bash
result = subprocess.run(
            ["bash", "inference_VM/EC2_provisioning.sh"]
            , capture_output=True
            , text=True
            , check=True
            , timeout=30
        )