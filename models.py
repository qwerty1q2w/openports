from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class ScanTask(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    ip_range = db.Column(db.String(100), nullable=False)
    scan_interval = db.Column(db.Integer, nullable=False)  # in minutes
    scan_type = db.Column(db.String(10), nullable=False)  # TCP, UDP, BOTH
    notifications = db.Column(db.JSON, nullable=False)  # {discord: [webhooks], slack: [webhooks], telegram: [chat_ids]}
    active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class ScanResult(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.Integer, db.ForeignKey('scan_task.id'), nullable=False)
    ip_address = db.Column(db.String(39), nullable=False)
    port = db.Column(db.Integer, nullable=False)
    protocol = db.Column(db.String(10), nullable=False)
    status = db.Column(db.String(20), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    ignored = db.Column(db.Boolean, default=False)
