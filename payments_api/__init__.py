from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.migrate import Migrate, MigrateCommand

app = Flask(__name__)

app.config.from_pyfile("config.py")

db = SQLAlchemy(app)
migrate = Migrate(app, db)

from payments_api import models
from payments_api.blueprints import register_blueprints
from payments_api.exceptions import register_exception_handlers

register_exception_handlers(app)
register_blueprints(app)
