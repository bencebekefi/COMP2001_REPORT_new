from . import db

class TrailInfo(db.Model):
    __tablename__ = 'TrailInfo'
    __table_args__ = {'schema': 'CW2'}

    TrailID = db.Column(db.Integer, db.ForeignKey('CW2.Trail.TrailID'), primary_key=True)
    InfoID = db.Column(db.Integer, db.ForeignKey('CW2.Info.InfoID'), primary_key=True)
    AdditionalInfo = db.Column(db.String(255), nullable=True)

    # Relationships
    trail = db.relationship('Trail', backref='trail_info_associations')
    info = db.relationship('Info', backref='trail_info_associations')
