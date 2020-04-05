import os

from flask_script import Server, Manager
from app import app

app.config.from_object(os.environ['APP_SETTINGS'])

manager = Manager(app)
manager.add_command('runserver', Server())


if __name__ == "__main__":
    manager.run()

