from sqlalchemy.sql import func
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()

class User(db.Model, UserMixin):

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(1000))
    role = db.Column(db.Enum('admin', 'customer'), nullable=False)
    first_name = db.Column(db.String(150))
    last_name = db.Column(db.String(150))
    orders = db.relationship('Orders', backref='user')
    ratings = db.relationship('Ratings', backref='user')
    address = db.relationship('Address', backref='user')
    is_verified = db.Column(db.Integer, nullable=False, default=0)
    cart = db.relationship('Cart', backref='user')
    verifier = db.Column(db.String(150))
    created_time = db.Column(db.DateTime(timezone=True), default=func.now())
    updated_time = db.Column(db.DateTime(timezone=True), default=func.now())

    def __repr__(self):
        return f'<User {self.username}>'

class Address(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    street = db.Column(db.String(150))
    city = db.Column(db.String(150))
    state = db.Column(db.String(150))
    zip = db.Column(db.String(150))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    created_time = db.Column(db.DateTime(timezone=True), default=func.now())
    updated_time = db.Column(db.DateTime(timezone=True), default=func.now())

    def __repr__(self):
        return f'<Address {self.street} {self.city} {self.state} {self.zip}>'

class Category(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150))
    description = db.Column(db.String(1000))
    is_popular = db.Column(db.Boolean, default=False)
    subcategories = db.relationship('Subcategory', backref='category')
    created_time = db.Column(db.DateTime(timezone=True), default=func.now())
    updated_time = db.Column(db.DateTime(timezone=True), default=func.now())

    def __repr__(self):
        return f'<Category {self.name}>'

class Subcategory(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150))
    description = db.Column(db.String(1000))
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'))
    models = db.relationship('Model', backref='subcategory')
    created_time = db.Column(db.DateTime(timezone=True), default=func.now())
    updated_time = db.Column(db.DateTime(timezone=True), default=func.now())

    def __repr__(self):
        return f'<SubCategory {self.name}>'

class Model(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150))
    description = db.Column(db.String(1000))
    sub_category_id = db.Column(db.Integer, db.ForeignKey('subcategory.id'))
    products = db.relationship('Product', backref='model')
    created_time = db.Column(db.DateTime(timezone=True), default=func.now())
    updated_time = db.Column(db.DateTime(timezone=True), default=func.now())

    def __repr__(self):
        return f'<SubCategory {self.name}>'

class Product(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150))
    description = db.Column(db.String(1000))
    image = db.Column(db.Text, nullable=False)
    price = db.Column(db.Float)
    available_qty = db.Column(db.Integer)
    model_id = db.Column(db.Integer, db.ForeignKey('model.id'))
    created_time = db.Column(db.DateTime(timezone=True), default=func.now())
    updated_time = db.Column(db.DateTime(timezone=True), default=func.now())

    def __repr__(self):
        return f'<Product {self.name}>'

    def get_category(self):
        return Category.query.filter_by(
            id=Subcategory.query.filter_by(
                id=Model.query.filter_by(
                    id=self.model_id).first()
                .sub_category_id).first()
            .category_id).first()

class Ratings(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    score = db.Column(db.Integer)
    description = db.Column(db.String(255))
    likes = db.Column(db.Integer)
    dislikes = db.Column(db.Integer)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    created_time = db.Column(db.DateTime(timezone=True), default=func.now())
    updated_time = db.Column(db.DateTime(timezone=True), default=func.now())

    def getUser(self):
        return User.query.filter_by(id = self.user_id).first()

class Cartitem(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'))
    cart_id = db.Column(db.Integer, db.ForeignKey('cart.id'))
    quantity = db.Column(db.Integer)
    price = db.Column(db.Float)
    is_wishlisted = db.Column(db.Boolean, default=False)

    def get_product(self):
        return Product.query.filter_by(id=self.product_id).first()

class Cart(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    cartitems = db.relationship('Cartitem', backref='cart')

    def get_items(self, type="cart"):
        if type == "cart":
            return [item for item in self.cartitems if(not item.is_wishlisted)]
        return [item for item in self.cartitems if(item.is_wishlisted)]

    def get_item_ids(self, type="cart", pid=False):
        if(pid):
            return [item.product_id for item in self.get_items(type)]
        return [item.id for item in self.get_items(type)]

    def get_cart_total(self):
        return sum([item.quantity * item.get_product().price for item in self.get_items()])

    def check_and_get_qty(self, pid):
        items = [item.quantity for item in self.cartitems if(item.product_id == pid)]
        return items[0] if len(items) == 1 else 1

class Orderitem(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    quantity = db.Column(db.Integer)
    total_price = db.Column(db.Float)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'))
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'))
    created_time = db.Column(db.DateTime(timezone=True), default=func.now())
    updated_time = db.Column(db.DateTime(timezone=True), default=func.now())

    def __repr__(self):
        return f'<Orderitem {self.quantity} of {self.total_price}>'

    def get_product(self):
        return Product.query.filter_by(id=self.product_id).first()

class Orders(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.String(100))
    order_status = db.Column(db.String(100))
    user_email = db.Column(db.String(100))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'))
    date = db.Column(db.DateTime(timezone=True))
    billing_address = db.Column(db.Integer, db.ForeignKey('address.id'))
    shipping_address = db.Column(db.Integer, db.ForeignKey('address.id'))
    notes = db.Column(db.Text)
    payments = db.relationship('Payment', backref='orders')
    cartitems = db.relationship('Orderitem', backref='orders')
    created_time = db.Column(db.DateTime(timezone=True), default=func.now())
    updated_time = db.Column(db.DateTime(timezone=True), default=func.now())

    def get_total_price(self):
        return sum([item.total_price for item in self.cartitems])

class Payment(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float)
    status = db.Column(db.String(2550))
    type = db.Column(db.String(2550))
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'))
    created_time = db.Column(db.DateTime(timezone=True), default=func.now())
    updated_time = db.Column(db.DateTime(timezone=True), default=func.now())

class AdminNotification(db.Model):

    id = db.Column(db.Integer, primary_key = True)
    url = db.Column(db.String(100))
    type = db.Column(db.String(100))
    status = db.Column(db.String(100))
    created_time = db.Column(db.DateTime(timezone=True), default=func.now())
    updated_time = db.Column(db.DateTime(timezone=True), default=func.now())