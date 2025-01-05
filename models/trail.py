from . import db

class Trail(db.Model):
    __tablename__ = 'Trail'
    __table_args__ = {'schema': 'CW2'}

    TrailID = db.Column(db.Integer, primary_key=True)
    TrailName = db.Column(db.String(100), nullable=False)
    TrailRating = db.Column(db.Numeric(3, 1))
    TrailDifficulty = db.Column(db.String(10), nullable=False)
    TrailDistance = db.Column(db.Numeric(5, 2), nullable=False)
    TrailEstTime = db.Column(db.String(10), nullable=False)
    TrailRouteType = db.Column(db.String(10), nullable=False)
    TrailDescription = db.Column(db.Text, nullable=False)
    LocationID = db.Column(db.Integer, db.ForeignKey('CW2.Location.LocationID'), nullable=False)

    # Relationships
    location = db.relationship('Location', backref='trails')
    trail_info = db.relationship('TrailInfo', backref='trail', cascade="all, delete-orphan")
    trail_features = db.relationship('TrailFeature', backref='trail', cascade="all, delete-orphan")
