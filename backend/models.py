from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Interview(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    resume_path = db.Column(db.String(256))
    questions = db.Column(db.JSON)
    created_at = db.Column(db.DateTime, default=db.func.now())