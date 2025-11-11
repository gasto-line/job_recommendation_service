# minimum t3.medium to download fasttext model.bin
aws ec2 run-instances \
  --image-id ami-0c814f1cf8f298648 \
  --count 1 \
  --instance-type t3.medium \
  --key-name my-debug-key \
  --associate-public-ip-address \
  --iam-instance-profile Name=EC2-get-model-role \
  --instance-initiated-shutdown-behavior terminate \
  --user-data file://fetch_model_VM/user_data.sh \
  --region eu-west-3

