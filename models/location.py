from . import db

class Location(db.Model):
    __tablename__ = 'Location'
    __table_args__ = {'schema': 'CW2'}

    LocationID = db.Column(db.Integer, primary_key=True)
    LocationName = db.Column(db.String(100), nullable=False)

    
