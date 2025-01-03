from dotenv import load_dotenv
import os
import boto3
import pandas as pd
import argparse
from io import BytesIO

load_dotenv()


def download_file_from_s3(bucket, object_name):
    s3 = boto3.client(
        "s3",
        endpoint_url="http://localhost:9000",
        aws_access_key_id=os.getenv("MINIO_ROOT_USER"),
        aws_secret_access_key=os.getenv("MINIO_ROOT_PASSWORD"),
    )
    file_stream = BytesIO()
    s3.download_fileobj(bucket, object_name, file_stream)
    file_stream.seek(0)
    return file_stream


def process_data(input_data):
    df = pd.read_csv(input_data)
    df["Survived"] = df["Survived"].apply(lambda x: "Yes" if x == 1 else "No")
    return df


def save_data_to_s3(dataframe, bucket, output_path):
    csv_buffer = BytesIO()
    dataframe.to_csv(csv_buffer, index=False)
    csv_buffer.seek(0)
    s3 = boto3.client(
        "s3",
        endpoint_url="http://localhost:9000",
        aws_access_key_id=os.getenv("MINIO_ROOT_USER"),
        aws_secret_access_key=os.getenv("MINIO_ROOT_PASSWORD"),
    )
    s3.upload_fileobj(csv_buffer, bucket, output_path)
    print(f"Processed data saved to S3 bucket {bucket} as {output_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process data from S3 and save back to S3")
    parser.add_argument("--bucket", required=True, help="S3 bucket name")
    parser.add_argument("--input_path", required=True, help="Path of the input file in S3")
    parser.add_argument(
        "--output_path", required=True, help="Path to save the processed file in S3"
    )
    args = parser.parse_args()

    file_stream = download_file_from_s3(args.bucket, args.input_path)
    processed_data = process_data(file_stream)
    save_data_to_s3(processed_data, args.bucket, args.output_path)
