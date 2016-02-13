import os

basedir = os.path.abspath(os.path.dirname(__file__))

class BaseConfiguration(object):
    DEBUG = False
    TESTING = False

    ADMINS = frozenset(['youremail@yourdomain.com'])
    SECRET_KEY = None

    THREADS_PER_PAGE = 8

    SECURITY_PASSWORD_HASH = 'sha512_crypt'
    SECURITY_PASSWORD_SALT = 'SuPeRsEcReTsAlT'
    SECURITY_POST_LOGIN_VIEW = '/profile'
    SECURITY_CHANGEABLE = True
    SECURITY_REGISTERABLE = True
    SECURITY_TRACKABLE = True

    SECURITY_SEND_REGISTER_EMAIL = False
    SECURITY_SEND_PASSWORD_CHANGE_EMAIL = False
    SECURITY_SEND_PASSWORD_RESET_NOTICE_EMAIL = False

    MAIL_DEBUG = 0
    MAIL_SUPPRESS_SEND = True 

class DockerConfiguration(BaseConfiguration):
    DEBUG = str(os.environ.get('DEBUG')).lower() == "true"
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
    MAIL_USE_TLS = True
    MAIL_SERVER = os.environ.get("MAIL_SERVER")
    MAIL_USERNAME = os.environ.get("MAIL_USERNAME")
    MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD")
    MAIL_DEFAULT_SENDER = os.environ.get("MAIL_DEFAULT_SENDER")

class TestConfiguration(BaseConfiguration):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    SECRET_KEY = "justfortesting"
