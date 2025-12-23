#!/bin/bash

# --- Update and install packages ---
dnf update -y
dnf install -y python3 python3-devel python3-pip awscli git 

# Write systemd service file
cat << 'EOF' > /etc/systemd/system/boot-api.service
[Unit]
Description=Boot Workflow API Service
After=network.target

[Service]
User=ec2-user
WorkingDirectory=/home/ec2-user/job_recommendation_service/ETL_job
ExecStart=/home/ec2-user/job_recommendation_service/ETL_job/venv/bin/uvicorn app:app --host 0.0.0.0 --port 8080
Restart=always

[Install]
WantedBy=multi-user.target
EOF

sudo -i -u ec2-user bash << END

cd /home/ec2-user

echo "Cloning inference server..."
git clone -b dev --single-branch https://github.com/gasto-line/job_recommendation_service.git job_recommendation_service

cd job_recommendation_service/ETL_job
python3 -m venv venv
source venv/bin/activate

echo "Installing dependencies..."
pip install -r requirements.txt

echo "Starting worflow API..."
nohup uvicorn endpoint:app --host 0.0.0.0 --port 8080

END

systemctl daemon-reload
systemctl start boot-api
systemctl enable boot-api