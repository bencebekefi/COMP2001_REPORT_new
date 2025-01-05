from . import db

class Activity(db.Model):
    __tablename__ = 'Activity'
    __table_args__ = {'schema': 'CW2'}

    ActivityID = db.Column(db.Integer, primary_key=True)  # Primary Key
    ActivityName = db.Column(db.String(20), nullable=False)  # Required Field

    # Relationships
    trail_activities = db.relationship('TrailActivity', backref='activity', cascade="all, delete-orphan")
