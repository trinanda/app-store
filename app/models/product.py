from app import db


class Category(db.Model):
    __tablename__ = 'category'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(),
                           onupdate=db.func.current_timestamp())

    def __str__(self):
        return self.name


class Product(db.Model):
    __tablename__ = 'product'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True)
    color = db.Column(db.String(100))
    size = db.Column(db.Float())
    barcode = db.Column(db.String(100), unique=True)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'))
    description = db.Column(db.String(100))
    image = db.Column(db.Unicode(128))
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())
    category = db.relationship("Category", foreign_keys=[category_id])

    def __str__(self):
        return self.name
