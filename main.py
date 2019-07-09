from apps import create_app
from config import Config

app = create_app(__name__, Config)

from apps.seckill.view import *
from apps.user.view import *

if __name__ == "__main__":
    app.run('0.0.0.0',8000)
