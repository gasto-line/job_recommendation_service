#!/bin/bash

# --- Update and install packages ---
dnf update -y
dnf install -y python3 python3-devel python3-pip awscli git 

# Fetch environment variables from SSM Parameter Store
SUPABASE_URL=$(aws ssm get-parameter \
  --name "/job_reco/supabase/url" \
  --query "Parameter.Value" \
  --output text)

SUPABASE_SERVICE_ROLE_KEY=$(aws ssm get-parameter \
  --name "/job_reco/supabase/service-role-key" \
  --with-decryption \
  --query "Parameter.Value" \
  --output text)

OPENAI_API_KEY=$(aws ssm get-parameter \
  --name "/job_reco/openai/API/key" \
  --query "Parameter.Value" \
  --output text)

ADZUNA_API_ID=$(aws ssm get-parameter \
  --name "/job_reco/adzuna/API/ID" \
  --query "Parameter.Value" \
  --output text)

ADZUNA_API_KEY=$(aws ssm get-parameter \
  --name "/job_reco/adzuna/API/key" \
  --query "Parameter.Value" \
  --output text)

cat << EOF > /etc/job_reco.env
SUPABASE_URL=$SUPABASE_URL
SUPABASE_SERVICE_ROLE_KEY=$SUPABASE_SERVICE_ROLE_KEY
OPENAI_API_KEY=$OPENAI_API_KEY
ADZUNA_API_ID=$ADZUNA_API_ID
ADZUNA_API_KEY=$ADZUNA_API_KEY
EOF

chmod 600 /etc/job_reco.env

# Clone repository and set up the application
sudo -i -u ec2-user bash << END

cd /home/ec2-user
echo "Cloning inference server..."
git clone -b dev --single-branch https://github.com/gasto-line/job_recommendation_service.git job_recommendation_service
chmod +x inference_VM/VM_config.sh
cd job_recommendation_service/ETL_job
python3 -m venv venv
source venv/bin/activate

echo "Installing dependencies..."
pip install -r requirements.txt

END


# Create systemd service
cat << 'EOF' > /etc/systemd/system/boot-api.service
[Unit]
Description=Boot Workflow API Service
After=network.target

[Service]
User=ec2-user
WorkingDirectory=/home/ec2-user/job_recommendation_service/ETL_job
EnvironmentFile=/etc/job_reco.env
ExecStart=/home/ec2-user/job_recommendation_service/ETL_job/venv/bin/uvicorn endpoint:app --host 0.0.0.0 --port 8080
Restart=always

[Install]
WantedBy=multi-user.target
EOF



systemctl daemon-reload
systemctl start boot-api
systemctl enable boot-api