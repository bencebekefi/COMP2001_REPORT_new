from . import db
from .location import Location

class Trail(db.Model):
    __tablename__ = 'Trail'
    __table_args__ = {'schema': 'CW2'}

    TrailID = db.Column(db.Integer, primary_key=True)
    TrailName = db.Column(db.String(100), nullable=False)
    TrailRating = db.Column(db.Numeric(5, 3), nullable=True)
    TrailDifficulty = db.Column(db.String(10), nullable=False)
    TrailDistance = db.Column(db.Numeric(5, 2), nullable=False)
    TrailEstTime = db.Column(db.String(10), nullable=False)
    TrailRouteType = db.Column(db.String(10), nullable=False)
    TrailDescription = db.Column(db.Text, nullable=False)
    LocationID = db.Column(db.Integer, db.ForeignKey('CW2.Location.LocationID'), nullable=False)

    # Define relationship with Location
    location = db.relationship('Location', backref=db.backref('trails', lazy=True))
