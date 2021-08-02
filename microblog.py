from app import create_app, db, fcm
from app.models import User, FCMKey, Song, Message

app = create_app()


@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'FCMKey': FCMKey, 'fcm': fcm, 'Song': Song, 'Message': Message}