from . import db

class TrailLog(db.Model):
    __tablename__ = 'TrailLog'
    __table_args__ = {'schema': 'CW2'}

    LogID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    TrailID = db.Column(db.Integer, db.ForeignKey('CW2.Trail.TrailID'), nullable=True)
    AddedBy = db.Column(db.String(100), nullable=True)
    AddedOn = db.Column(db.DateTime, default=db.func.current_timestamp())

    # Relationships
    trail = db.relationship('Trail', backref='logs')
