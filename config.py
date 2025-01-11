import os

class Config:
    # General Configuration
    SECRET_KEY = os.environ.get('SECRET_KEY', 'your_default_secret_key')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SWAGGER_URL = '/api/docs'
    API_URL = '/swagger.json'

    # Database Configuration
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URI',
        'mssql+pyodbc://BBekefi:AqrM335*@DIST-6-505.uopnet.plymouth.ac.uk/COMP2001_BBekefi?driver=ODBC+Driver+17+for+SQL+Server'
    )


class DevelopmentConfig(Config):
    DEBUG = True


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'TEST_DATABASE_URI',
        'sqlite:///:memory:'  
    )


class ProductionConfig:
    DEBUG = False
    TESTING = False
    SQLALCHEMY_DATABASE_URI = 'mssql+pyodbc://BBekefi:AqrM335*@DIST-6-505.uopnet.plymouth.ac.uk/COMP2001_BBekefi?driver=ODBC+Driver+17+for+SQL+Server'
    SQLALCHEMY_TRACK_MODIFICATIONS = False  
