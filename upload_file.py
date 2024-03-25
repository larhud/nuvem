from minio import Minio
from minio.error import S3Error


def main():
    # Create a client with the MinIO server playground, its access key
    # and secret key.
    client = Minio(
        "a2r.ibict.br",
        access_key="oAer6zWmcj54P7nicR7t",
        secret_key="iwDWvNkJQc5iLVqCsuHpF6gWsBy4Skuf0ilbuzwR",
        secure=True
    )

    print('Logged')
    bucket_name = "enacin"
    found = client.bucket_exists(bucket_name)
    if not found:
        client.make_bucket(bucket_name)
    else:
        print(f"Bucket {bucket_name} found")

    client.fput_object(
        bucket_name, "nuvem.png",
        "/home/josir/bitbucket/nuvem3/media/output/72c63916-711b-425f-b.png",
    )
    print('Sucesso!')


if __name__ == "__main__":
    try:
        main()
    except S3Error as exc:
        print("error occurred.", exc)