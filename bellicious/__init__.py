from flask import Flask
from . import register
from . import auth
from . import admin
from . import database
from . import bookmarks
from . import main_page
from . import search
from flask_mysqldb import MySQL
import os
from . import config
from flask_wtf.csrf import CSRFProtect
from flask_mail import Mail

mysql = MySQL()
mail = Mail()
csrf = CSRFProtect()

def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    csrf.init_app(app)
    app.config.from_mapping(
        SECRET_KEY=config.secret,
        MYSQL_USER=config.user,
        MYSQL_PASSWORD=config.password,
        MYSQL_HOST=config.host,
        MYSQL_DB=config.dbname,
        MYSQL_CURSORCLASS='DictCursor',
        MYSQL_CHARSET='utf8',
        MAIL_SERVER=config.mailserver,
        MAIL_PORT=config.mailport,
        MAIL_USE_TLS=config.usetls,
        MAIL_USE_SSL=config.usessl,
        MAIL_USERNAME=config.mailusr,
        MAIL_PASSWORD=config.mailpass
    )
    mail = Mail(app)
    if test_config is None:
        app.config.from_pyfile('config.py', silent=True)
    else:
        app.config.from_mapping(test_config)

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    mysql.init_app(app)
    
    app.register_blueprint(register.bp)
    app.register_blueprint(database.bp)
    app.register_blueprint(auth.auth)
    app.register_blueprint(admin.bp)
    app.register_blueprint(bookmarks.bookmark_bp)
    app.register_blueprint(main_page.mainpage_bp)
    app.register_blueprint(search.search_bp)

    return app
