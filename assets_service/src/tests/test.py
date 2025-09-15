import boto3
from botocore.config import Config

s3 = boto3.client(
    "s3",
    endpoint_url="http://127.0.0.1:9000",
    aws_access_key_id="minio",
    aws_secret_access_key="minio123",
    region_name="us-east-1",
    config=Config(s3={"addressing_style": "path"})
)

bucket = "demo"
# create bucket (idempotent)
try: s3.head_bucket(Bucket=bucket)
except s3.exceptions.ClientError: s3.create_bucket(Bucket=bucket)

# upload object
s3.put_object(Bucket=bucket, Key="folder/file.txt", Body=b"hello", ContentType="text/plain")

# download object
obj = s3.get_object(Bucket=bucket, Key="folder/file.txt")
print(obj["Body"].read())

# presigned URL (GET for 1 hour)
url = s3.generate_presigned_url(
    "get_object",
    Params={"Bucket": bucket, "Key": "folder/file.txt"},
    ExpiresIn=3600
)
print("URL:", url)
