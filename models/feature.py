from . import db

class Feature(db.Model):
    __tablename__ = 'Feature'
    __table_args__ = {'schema': 'CW2'}

    FeatureID = db.Column(db.Integer, primary_key=True)
    FeatureName = db.Column(db.String(50), nullable=False)

    trail_features = db.relationship('TrailFeature', backref='feature', lazy=True)
