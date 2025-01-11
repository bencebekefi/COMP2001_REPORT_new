from . import db

class User(db.Model):
    __tablename__ = 'User'
    __table_args__ = {'schema': 'CW2'}

    UserID = db.Column(db.Integer, primary_key=True)
    EmailAddress = db.Column(db.String(255), nullable=False, unique=True)
    Role = db.Column(db.String(50), nullable=False)
