import os
import boto3
from datetime import datetime, timezone
from supabase import create_client

ec2 = boto3.client("ec2")
ssm = boto3.client("ssm")

PROJECT_TAG = "job-reco"
THRESHOLD_MINUTES = 10


def get_parameter(name):
    return ssm.get_parameter(Name=name, WithDecryption=True)["Parameter"]["Value"]


def get_last_activity():
    url = get_parameter("/job_reco/supabase/url")
    key = get_parameter("/job_reco/supabase/service_role_key")

    supabase = create_client(url, key)

    response = (
        supabase
        .table("app_activity")
        .select("last_activity")
        .eq("id", 1)
        .execute()
    )

    return datetime.fromisoformat(response.data[0]["last_activity"])


def find_instance():
    response = ec2.describe_instances(
        Filters=[
            {"Name": "tag:ManagedBy", "Values": ["lambda-job-reco"]},
            {"Name": "instance-state-name", "Values": ["pending", "running"]}
        ]
    )

    for reservation in response["Reservations"]:
        for instance in reservation["Instances"]:
            return instance["InstanceId"], instance["State"]["Name"]

    return None, None


def launch_instance():
    ec2.run_instances(
        ImageId=os.environ["AMI_ID"],
        InstanceType="t3.micro",
        MinCount=1,
        MaxCount=1,
        TagSpecifications=[
            {
                "ResourceType": "instance",
                "Tags": [
                    {"Key": "Name", "Value": "job-api-instance"},
                    {"Key": "ManagedBy", "Value": "lambda-job-reco"}
                ]
            }
        ]
    )


def terminate_instance(instance_id):
    ec2.terminate_instances(InstanceIds=[instance_id])


def lambda_handler(event, context):

    last_activity = get_last_activity()
    now = datetime.now(timezone.utc)

    delta_minutes = (now - last_activity).total_seconds() / 60

    instance_id, state = find_instance()

    if delta_minutes < THRESHOLD_MINUTES:
        if not instance_id:
            launch_instance()
    else:
        if instance_id:
            terminate_instance(instance_id)

    return {"status": "done"}
