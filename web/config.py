import os

basedir = os.path.abspath(os.path.dirname(__file__))

class BaseConfiguration(object):
    DEBUG = False
    TESTING = False

    ADMINS = frozenset(['youremail@yourdomain.com'])
    SECRET_KEY = 'SecretKeyForSessionSigning'

    THREADS_PER_PAGE = 8

    DATABASE = 'app.db'
    DATABASE_PATH = os.path.join(basedir, DATABASE)
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + DATABASE_PATH

    SECURITY_PASSWORD_HASH = 'sha512_crypt'
    SECURITY_PASSWORD_SALT = 'SuPeRsEcReTsAlT'
    SECURITY_POST_LOGIN_VIEW = '/ViewProfile'
    SECURITY_CHANGEABLE = True
    SECURITY_REGISTERABLE = True
    SECURITY_TRACKABLE = True

    SECURITY_SEND_REGISTER_EMAIL = False
    SECURITY_SEND_PASSWORD_CHANGE_EMAIL = False
    SECURITY_SEND_PASSWORD_RESET_NOTICE_EMAIL = False

    MAIL_SUPPRESS_SEND = True 

class DockerConfig(BaseConfiguration):
    SECRET_KEY = os.environ.get('SECRET_KEY')

    DB_NAME = os.environ.get('DB_NAME')
    DB_USER = os.environ.get('DB_USER')
    DB_PASS = os.environ.get('DB_PASS')
    DB_SERVICE = os.environ.get('DB_SERVICE')
    DB_PORT = os.environ.get('DB_PORT')
    SQLALCHEMY_DATABASE_URI = 'postgresql://{0}:{1}@{2}:{3}/{4}'.format(
        DB_USER, DB_PASS, DB_SERVICE, DB_PORT, DB_NAME
    )

    RQ_DEFAULT_HOST="redis_1"
    RQ_DEFAULT_PORT=6379

    MAIL_SERVER = "smtp_server.usgo.org"
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = "noreply@usgo.org"
    MAIL_PASSWORD = "password"
    MAIL_DEFAULT_SENDER = "noreply@usgo.org"

class DebugConfiguration(DockerConfig):
    DEBUG = True

class TestConfiguration(BaseConfiguration):
    TESTING = True

    DATABASE = 'tests.db'
    DATABASE_PATH = os.path.join(basedir, DATABASE)
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + DATABASE_PATH
