from app import db


class Transaction(db.Model):
    __tablename__ = 'transaction'
    id = db.Column(db.Integer, primary_key=True)
    receipt_code = db.Column(db.String(10), unique=True)
    name = db.Column(db.String(100))
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'))
    total = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())

    def __str__(self):
        return self.name
