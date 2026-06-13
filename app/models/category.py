from app.extensions import db
from datetime import datetime


class Category(db.Model):
    __tablename__ = "categories"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text)
    parent_id = db.Column(db.Integer, db.ForeignKey("categories.id"))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    children = db.relationship("Category", backref=db.backref("parent", remote_side=[id]))

    def __repr__(self):
        return f"<Category {self.name}>"
