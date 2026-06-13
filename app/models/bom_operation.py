from app.extensions import db


class BomOperation(db.Model):
    __tablename__ = "bom_operations"

    id = db.Column(db.Integer, primary_key=True)
    bom_id = db.Column(db.Integer, db.ForeignKey("boms.id"), nullable=False)
    name = db.Column(db.String(200), nullable=False)
    work_center_id = db.Column(db.Integer, db.ForeignKey("work_centers.id"))
    sequence = db.Column(db.Integer, default=0)
    duration_minutes = db.Column(db.Float, default=0.0)
    cost = db.Column(db.Float, default=0.0)
    notes = db.Column(db.Text)

    def __repr__(self):
        return f"<BomOperation {self.name}>"
