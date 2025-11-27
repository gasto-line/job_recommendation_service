#!/bin/bash

INSTANCE_ID=$(aws ec2 run-instances \
  --image-id ami-0c814f1cf8f298648 \
  --count 1 \
  --instance-type t3.xlarge \
  --associate-public-ip-address \
  --key-name my-debug-key \
  --iam-instance-profile Name=EC2-get-model-role \
  --user-data file://inference_VM/VM_user_data.sh \
  --security-group-ids 	sg-059648096d13c1a36 \
  --region eu-west-3 \
  --query 'Instances[0].InstanceId' \
  --output text
)

aws ec2 wait instance-running --instance-ids "$INSTANCE_ID"

PUBLIC_IP=$(aws ec2 describe-instances \
  --instance-ids "$INSTANCE_ID" \
  --query 'Reservations[0].Instances[0].PublicIpAddress' \
  --output text)

echo "$PUBLIC_IP"