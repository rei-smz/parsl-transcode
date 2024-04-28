import parsl
from parsl import python_app, bash_app, join_app
from parsl.data_provider.files import File
from minio import Minio

@python_app
def download_video(minio_client: Minio, bucket_name: str, object_path: str, outputs=[]) -> str:
    local_path = outputs[0].filepath

    minio_client.fget_object(bucket_name, object_path, local_path)

    return "Success"

@bash_app
def run_ffmpeg(args: dict[str, str], inputs=[], outputs=[]) -> str:
    resolution = args.get('resolution', '1280x720')
    acodec = args.get('acodec', 'copy')
    vcodec = args.get('vcodec', '')
    if resolution != 'no':
        resolution_cmd = f'-s {resolution}'
    else:
        resolution_cmd = ''
    codec = ''
    if acodec != '':
        codec += ' -acodec ' + acodec
    if vcodec != '':
        codec += ' -vcodec ' + vcodec
    cmd = f'ffmpeg -hide_banner -loglevel warning -y -i {inputs[0].filepath} {resolution_cmd} {codec} {outputs[0]}'
    return cmd

@python_app
def upload_video(minio_client: Minio, bucket_name: str, object_path: str, inputs=[]) -> str:
    local_path = inputs[0].filepath

    minio_client.fput_object(bucket_name, object_path, local_path)

    return "Success"

@join_app
def transcode(req_str: str):
    import json
    import time
    import os
    from minio import Minio
    import shutil

    try:
        body = json.loads(req_str)
    except json.JSONDecodeError:
        return {"statusCode": 400, "body": "Invalid JSON"}
    
    path = body.get('path')
    obj_name = body.get('object')
    args = body.get('args', {})
    video_format = args.get('format', 'mp4')
    current_time = time.strftime("%Y-%m-%d-%H%M%S", time.localtime())

    if not path:
        return {"statusCode": 400, "body": "Path is required"}
    
    MINIO_ENDPOINT = os.getenv('MINIO_ENDPOINT')
    MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY")
    MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY")
    BUCKET_NAME = os.getenv('BUCKET_NAME')

    minio_client = Minio(
        MINIO_ENDPOINT,
        access_key=MINIO_ACCESS_KEY,
        secret_key=MINIO_SECRET_KEY,
        secure=False
    )

    tmp_path = path + "-" + current_time
    os.mkdir(tmp_path)

    download_future = download_video(minio_client,
                   BUCKET_NAME, 
                   os.path.join(path, obj_name), 
                   [File(os.path.join(tmp_path, obj_name))])
    
    transcoding_future = run_ffmpeg(args, 
                                    [download_future.output[0]], 
                                    [File(os.path.join(tmp_path, "output." + video_format))])
    
    upload_future = upload_video(minio_client, 
                                 BUCKET_NAME, 
                                 os.path.join(path, "output." + video_format), 
                                 [transcoding_future.output[0]])
    
    
    if upload_future.done():
        shutil.rmtree(tmp_path)

    if upload_future.result() == "Success":
        return {"statusCode": 200, "body": "Success"}
    else:
        return {"statusCode": 500, "body": "Failed"}
