from . import db

class Location(db.Model):
    __tablename__ = 'Location'
    __table_args__ = {'schema': 'CW2'}

    LocationID = db.Column(db.Integer, primary_key=True)
    TrailLocation = db.Column(db.String(100), nullable=False)

    # Relationships
    trails = db.relationship('Trail', backref='location', cascade="all, delete-orphan")
