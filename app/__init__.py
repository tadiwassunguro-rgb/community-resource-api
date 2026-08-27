import logging
import os

from flask import Flask

from .config import Config
from .db import init_db
from .routes import api


def create_app(test_config=None):
    app = Flask(__name__)
    app.config.from_object(Config)

    if test_config:
        app.config.update(test_config)

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )

    os.makedirs(os.path.dirname(app.config["DATABASE_PATH"]), exist_ok=True)
    init_db(app.config["DATABASE_PATH"])

    app.register_blueprint(api)

    return app
