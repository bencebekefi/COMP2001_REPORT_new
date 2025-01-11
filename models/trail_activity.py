from . import db

class TrailActivity(db.Model):
    __tablename__ = 'TrailActivity'
    __table_args__ = {'schema': 'CW2'}

    TrailID = db.Column(db.Integer, db.ForeignKey('CW2.Trail.TrailID'), primary_key=True)
    ActivityID = db.Column(db.Integer, db.ForeignKey('CW2.Activity.ActivityID'), primary_key=True)

    # Relationships
    trail = db.relatioanship('Trail', backref='activities')
