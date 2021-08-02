from app import s3, s3_resource
from app.api import bp
from app.api.auth import token_auth
from flask import send_file, current_app, abort, redirect
import os
import io


@bp.route('/cdn/am-key', methods=['GET'])
def get_am_key():
    # key = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJFUzI1NiIsImtpZCI6Ik4yNTM0NlFYNzYifQ.eyJpc3MiOiJQMzZBMzJXQjZLIiwiaWF0IjoxNTg2MDkzMjY0LCJleHAiOjE2MDE2NDUyNjR9.ydWJ0eWUtOzSW_FmXOveMJOBBakhdE-LusLPCGpVoy-3tsyh920HKMRHr5FRHHhOUurYR0UgsYh9-wzsTb8Avw'
    key = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJFUzI1NiIsImtpZCI6Ik4yNTM0NlFYNzYifQ.eyJpc3MiOiJQMzZBMzJXQjZLIiwiaWF0IjoxNjE4ODQ0ODQzLCJleHAiOjE2MzQzOTY4NDN9.67LNuf-PcI5VaSfOjj7m8PNmmFNNKgvRhSPq9ClCKcccJikvDeXp4EzVhkeZXsPuAuFieh2i_JAuSslv3LzTNQ'
    return key


@bp.route('/cdn/<filename>', methods=['GET'])
def get_file(filename):
    # folder = current_app.config['UPLOAD_FOLDER'][4:]
    try:
        a_file = io.BytesIO()
        s3_object = s3_resource.Bucket(current_app.config['S3_BUCKET']).Object(filename)
        s3_object.download_fileobj(a_file)
        a_file.seek(0)
        return send_file(a_file, mimetype=s3_object.content_type)
        # bucket = current_app.config['S3_BUCKET']
        # url = f'https://{bucket}.s3.amazonaws.com/{filename}'
        # return redirect(url, code=302)
        # return send_file(os.path.join(folder, filename))
    except FileNotFoundError:
        abort(404)  # return send_file(os.path.join(folder, 'pbzvlsiscbwehykkzbpq.png'))


'''@bp.route('/cdn/sync')
def sync_s3():
    files = os.listdir('app/upload')
    for f in files:
        print(s3.upload_file('app/upload/' + f, current_app.config['S3_BUCKET'], f))'''


def upload_file_to_s3(file, bucket_name, acl="public-read"):
    try:
        s3.upload_fileobj(
            file,
            bucket_name,
            file.filename,
            ExtraArgs={
                "ACL": acl,
                "ContentType": file.content_type
            }
        )
    except Exception as e:
        print("Something Happened: ", e)
        return e

    return "{}{}".format(current_app.config["S3_LOCATION"], file.filename)