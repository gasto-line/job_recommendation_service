#!/bin/bash

# --- Update and install packages ---
dnf update -y
dnf install -y python3 python3-devel python3-pip awscli gcc gcc-c++ make git 

# Write systemd service file
cat << 'EOF' > /etc/systemd/system/boot-api.service
[Unit]
Description=Boot FastText Inference API Service
After=network.target

[Service]
User=ec2-user
WorkingDirectory=/home/ec2-user/Inference-VM
ExecStart=/home/ec2-user/Inference-VM/venv/bin/uvicorn app:app --host 0.0.0.0 --port 8080
Restart=always

[Install]
WantedBy=multi-user.target
EOF

sudo -i -u ec2-user bash << END

cd /home/ec2-user

echo "Cloning inference server..."
git clone https://github.com/gasto-line/Inference-VM.git Inference-VM

cd Inference-VM
python3 -m venv venv
source venv/bin/activate

echo "Installing dependencies..."
pip install -r requirements.txt

echo "Starting inference API..."
nohup uvicorn app:app --host 0.0.0.0 --port 8080

END

systemctl daemon-reload
systemctl start boot-api
systemctl enable boot-api