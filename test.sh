#!/bin/bash

aws ec2 run-instances \
  --image-id ami-0c814f1cf8f298648 \
  --count 1 \
  --instance-type t3.large \
  --associate-public-ip-address \
  --key-name my-debug-key \
  --iam-instance-profile Name=EC2-get-model-role \
  --user-data file://inference_VM/user_data.sh \
  --security-group-ids 	sg-0ccbd2405bff7b168 \
  --region eu-west-3 \
  --query 'Instances[0].InstanceId' \
  --output text

  