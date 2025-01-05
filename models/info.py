from . import db

class Info(db.Model):
    __tablename__ = 'Info'
    __table_args__ = {'schema': 'CW2'}

    InfoID = db.Column(db.Integer, primary_key=True)
    InfoName = db.Column(db.String(255), nullable=False)

    # Relationships
    trail_info = db.relationship('TrailInfo', backref='info', cascade="all, delete-orphan")
