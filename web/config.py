import os

basedir = os.path.abspath(os.path.dirname(__file__))

class BaseConfiguration(object):
    DEBUG = False
    TESTING = False

    ADMINS = os.environ.get('ADMINS', '').split(',')
    SECRET_KEY = None

    THREADS_PER_PAGE = 8

    SECURITY_PASSWORD_HASH = 'sha512_crypt'
    SECURITY_PASSWORD_SALT = os.environ.get('SECURITY_PASSWORD_SALT', 'defaultsalt')
    SECURITY_POST_LOGIN_VIEW = '/profile'
    SECURITY_CHANGEABLE = True
    SECURITY_RECOVERABLE = True
    SECURITY_REGISTERABLE = True
    SECURITY_TRACKABLE = True

    MAIL_DEBUG = 0
    GAME_FETCH_HTTP_TIMEOUT = 10

class DockerConfiguration(BaseConfiguration):
    DEBUG = False
    SECRET_KEY = os.environ.get('SECRET_KEY')

    DB_NAME = os.environ.get('DB_NAME')
    DB_USER = os.environ.get('DB_USER')
    DB_PASS = os.environ.get('POSTGRES_PASSWORD')
    DB_SERVICE = os.environ.get('DB_SERVICE')
    DB_PORT = os.environ.get('DB_PORT')
    SQLALCHEMY_DATABASE_URI = 'postgresql://{0}:{1}@{2}:{3}/{4}'.format(
        DB_USER, DB_PASS, DB_SERVICE, DB_PORT, DB_NAME
    )

    MAIL_PORT = 587
    MAIL_DEBUG = os.environ.get("MAIL_DEBUG")
    MAIL_USE_TLS = True
    MAIL_SERVER = os.environ.get("MAIL_SERVER")
    MAIL_USERNAME = os.environ.get("MAIL_USERNAME")
    MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD")
    MAIL_DEFAULT_SENDER = os.environ.get("MAIL_DEFAULT_SENDER")
    SECURITY_EMAIL_SENDER = os.environ.get("MAIL_DEFAULT_SENDER")

class TestConfiguration(BaseConfiguration):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    SECURITY_PASSWORD_HASH = 'plaintext'
    WTF_CSRF_ENABLED = False
    SECRET_KEY = "justfortesting"
    MAIL_SUPPRESS_SEND = True
