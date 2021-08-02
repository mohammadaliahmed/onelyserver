import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    # SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
    #                         'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://admin:mcdonalds91@onely-dev1.cm5bmcadhdl1.us-east-2.rds.amazonaws.com/onely'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAIL_SERVER = 'smtp.googlemail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = 1
    MAIL_USERNAME = 'onelydemo'
    MAIL_PASSWORD = 'STARBUCKS@123'
    ADMINS = ['nikolailic02@gmail.com']
    POSTS_PER_PAGE = 25
    UPLOAD_FOLDER = 'app/upload'
    FCM_API_KEY = "AAAAG9n7I6s:APA91bG-WhJXj1DwOQ-5Rhah0Ijjn9rYuUcpE5qgUrpEAHfdTNpaYd5c_yvFb4ehs5IBp9bnjCSV-A_" \
                  "UvcF_hQeX8xineMy_cNLKTdEbfyOsCvQ8ODsLiESDAvsvL3r7TUiYXv0vgemP"
    S3_BUCKET = 'onely-s3'
    S3_KEY = 'AKIAIGQRUWIDXXAB37XA'
    S3_SECRET = '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'
    S3_LOCATION = 'http://{}.s3.amazonaws.com/'.format(S3_BUCKET)
