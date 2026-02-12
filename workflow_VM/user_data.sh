#!/bin/bash
set -e

# --- Update and install packages ---
dnf update -y
dnf install -y python3 python3-devel python3-pip awscli git docker

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

# Update DNS
HOSTED_ZONE_ID="Z0473277P8MLN06IBV8F"
RECORD_NAME="api.silkworm.cloud"

TOKEN=$(curl -sX PUT "http://169.254.169.254/latest/api/token" \
  -H "X-aws-ec2-metadata-token-ttl-seconds: 21600")

PUBLIC_IP=$(curl -s \
  -H "X-aws-ec2-metadata-token: $TOKEN" \
  http://169.254.169.254/latest/meta-data/public-ipv4)

cat << EOF > /tmp/route53.json
{
  "Changes": [{
    "Action": "UPSERT",
    "ResourceRecordSet": {
      "Name": "$RECORD_NAME",
      "Type": "A",
      "TTL": 60,
      "ResourceRecords": [{ "Value": "$PUBLIC_IP" }]
    }
  }]
}
EOF

aws route53 change-resource-record-sets \
  --hosted-zone-id "$HOSTED_ZONE_ID" \
  --change-batch file:///tmp/route53.json

# Activate docker
systemctl start docker
systemctl enable docker
# Pull the image from docker hub and run the container
docker pull gastoline/job_api:latest
docker run -d -p 8080:8080 --name job_api --env-file /etc/job_reco.env gastoline/job_api:v1