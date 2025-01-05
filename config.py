import os

class Config:
    SQLALCHEMY_DATABASE_URI = 'mssql+pyodbc://BBekefi:AqrM335*@DIST-6-505.uopnet.plymouth.ac.uk/COMP2001_BBekefi?driver=ODBC+Driver+17+for+SQL+Server'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SWAGGER_URL = '/api/docs'
    API_URL = '/swagger.json'

