#!/bin/bash
set -e

HOSTED_ZONE_ID="Z0473277P8MLN06IBV8F"
RECORD_NAME="api.silkworm.cloud"

PUBLIC_IP=$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4)

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
