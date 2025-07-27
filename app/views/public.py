from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from .auth import role_required
from ..models.app_models import Category, db, User, Product, Cartitem, Cart, Address, Orders, Orderitem, AdminNotification, Model, Subcategory
from ..utils.email_util import verify_email, order_email
from ..utils.constants import OrderStatus, AdminNotifications, NotificationStatus
import uuid
from datetime import datetime

public_bp = Blueprint('public', __name__)

@public_bp.route("/")
def index():
    if(current_user.is_authenticated and not current_user.is_verified):
        return redirect(url_for('public.verify_account'))
    categories = Category.query.all()
    pdcts = Product.query.all()
    return render_template('public/index.html', categories=categories, user=current_user, pdcts = pdcts)

@public_bp.route("/verify_account/", methods=['GET', 'POST'])
@login_required
@role_required('customer')
def verify_account():
    categories = Category.query.all()
    return render_template('public/verify_account.html', user=current_user, categories=categories)

@public_bp.route("/verification/", methods=['GET', 'POST'])
@login_required
@role_required('customer')
def verification():
    if(request.method == 'POST'):
        verifier = f"{uuid.uuid4()}_{uuid.uuid4()}"
        user = current_user
        user.verifier = verifier
        db.session.add(user)
        db.session.commit()
        verify_email(user.username, user.first_name + user.last_name, f"Account Verification for {user.first_name}", verifier, request.base_url.replace('/verification/', '/'))
        flash('Verification mail sent !')
    return redirect(url_for('public.verify_account'))

@public_bp.route("/checkout/")
@login_required
@role_required('customer')
def checkout():
    if(current_user.is_verified):
        categories = Category.query.all()
        return render_template('public/checkout.html', user=current_user, categories=categories)
    return redirect(url_for('public.verify_account'))

@public_bp.route("/product/<pid>/")
def product(pid):
    if(current_user.is_authenticated and not current_user.is_verified):
        return redirect(url_for('public.verify_account'))
    product = Product.query.get(pid)
    categories = Category.query.all()
    products = Product.query.all()
    return render_template('public/product.html', user=current_user, product=product, categories=categories, products=products)

@public_bp.route("/store/")
def store():
    if(current_user.is_authenticated and not current_user.is_verified):
        return redirect(url_for('public.verify_account'))
    categories = Category.query.all()
    products = Product.query.all()
    return render_template('public/store.html', categories=categories, user=current_user, products = products)

@public_bp.route("/mproducts/<int:mid>/")
def mproducts(mid):
    if(current_user.is_authenticated and not current_user.is_verified):
        return redirect(url_for('public.verify_account'))
    categories = Category.query.all()
    model = Model.query.filter_by(id=mid).first()
    return render_template('public/mproducts.html', categories=categories, user=current_user, model = model)

@public_bp.route("/scproducts/<int:scid>/")
def scproducts(scid):
    if(current_user.is_authenticated and not current_user.is_verified):
        return redirect(url_for('public.verify_account'))
    categories = Category.query.all()
    sub_category = Subcategory.query.filter_by(id=scid).first()
    return render_template('public/scproducts.html', categories=categories, user=current_user, scategory = sub_category)

@public_bp.route("/cart/")
@login_required
def cart():
    if(current_user.is_verified):
        categories = Category.query.all()
        return render_template("public/cart.html", user = current_user, categories=categories)
    return redirect(url_for('public.verify_account'))

@public_bp.route("/wishlist/")
@login_required
def wishlist():
    if(current_user.is_verified):
        categories = Category.query.all()
        return render_template("public/wishlist.html", user = current_user, categories=categories)
    return redirect(url_for('public.verify_account'))

@public_bp.route("/add_to_cart/", methods=['GET', 'POST'])
@login_required
def add_to_cart():
    item_id = request.json["pid"]
    cart = Cart.query.filter_by(user_id=current_user.id).first()
    product = Product.query.filter_by(id=item_id).first()
    quantity = float(request.json["quantity"])
    print(quantity, product.price, item_id)
    cart_item = Cartitem.query.filter_by(product_id=item_id, cart_id=cart.id).first()
    if(not cart_item):
        cart_item = Cartitem(product_id=product.id, cart_id=cart.id, quantity=quantity, price = product.price * quantity)
    else:
        cart_item.quantity = quantity
        cart_item.price = quantity * product.price
        cart_item.is_wishlisted = False
    db.session.add(cart_item)
    db.session.commit()
    return jsonify({"msg" : "success"})

@public_bp.route("/add_to_wishlist/", methods=['GET', 'POST'])
@login_required
def add_to_wishlist():
    item_id = request.json["pid"]
    cart = Cart.query.filter_by(user_id=current_user.id).first()
    product = Product.query.filter_by(id=item_id).first()
    quantity = float(request.json["quantity"])
    print(quantity, product.price, item_id)
    cart_item = Cartitem.query.filter_by(product_id=item_id, cart_id=cart.id).first()
    if(not cart_item):
        cart_item = Cartitem(product_id=product.id, cart_id=cart.id, quantity=quantity, price = product.price * quantity, is_wishlisted=True)
    else:
        cart_item.quantity = quantity
        cart_item.price = quantity * product.price
        cart_item.is_wishlisted = True
    db.session.add(cart_item)
    db.session.commit()
    return jsonify({"msg" : "success"})

@public_bp.route("/place_order/", methods=['GET', 'POST'])
@login_required
def place_order():
    billing_address = request.form["billing_address"]
    shipping_address = request.form["shipping_address"]
    notes = request.form["order_notes"]
    order_id = uuid.uuid4()
    order = Orders(order_id=order_id, order_status=OrderStatus.PENDING, user_email=current_user.username,
                   user_id=current_user.id,product_id=1,
                   date=datetime.now(), billing_address=billing_address, shipping_address=shipping_address, notes=notes)
    db.session.add(order)
    db.session.commit()
    for cartitem in current_user.cart[0].get_items():
        order_item = Orderitem(quantity=cartitem.quantity, total_price=cartitem.price, product_id=cartitem.product_id, order_id=order.id)
        db.session.add(order_item)
        db.session.delete(cartitem)
        db.session.commit()
    notification = AdminNotification(url=url_for("admin.order_detail", order_id=order.order_id),
                                      type=AdminNotifications.ORDER_PLACED,
                                      status=NotificationStatus.ACTIVE)
    db.session.add(notification)
    db.session.commit()
    order_email(current_user.username, f"{current_user.first_name} {current_user}", f"Order Notification - {order_id}", {
        "order_id" : str(order_id),
        "order_status" : OrderStatus.PENDING.name,
        "order_details" : f"{request.base_url.replace('/place_order/', '/')}order_detail/{order_id}/"
    })
    categories = Category.query.all()
    return render_template("public/order_success.html", user=current_user, order_id = order_id, categories = categories)

@public_bp.route("/profile/")
@login_required
def profile():
    categories = Category.query.all()
    return render_template("public/profile.html", user=current_user, categories = categories)

@public_bp.route("/add_address/", methods=['GET', 'POST'])
@login_required
def add_address():
    if(request.method == 'POST'):
        street = request.form["address"]
        city = request.form["city"]
        state = request.form["state"]
        zip_code = request.form["zip-code"]
        address = Address(street=street, city=city, state=state, zip=zip_code, user_id=current_user.id)
        db.session.add(address)
        db.session.commit()
        return redirect(url_for('public.profile'))

@public_bp.route("/myorders/")
@login_required
def my_orders():
    categories = Category.query.all()
    return render_template("public/my_orders.html", user=current_user, categories = categories)

@public_bp.route("/order_detail/<order_id>/")
@login_required
def order_detail(order_id):
    order = Orders.query.filter_by(order_id=order_id).first()
    saddress = Address.query.filter_by(id=order.shipping_address).first()
    baddress = Address.query.filter_by(id=order.billing_address).first()
    categories = Category.query.all()
    return render_template("public/order_detail.html", user=current_user, order=order, saddress=saddress, baddress=baddress, categories = categories)

@public_bp.route("/cancel_order/")
def cancel_order():
    order_id = request.form["order_id"]
    order = Orders.query.filter_by(order_id=order_id).first()
    if(order.order_status == OrderStatus.PENDING.name):
        order.order_status = OrderStatus.CANCELLED
        db.session.commit()
        return jsonify({"msg" : "order cancelled successfully !"})
    return jsonify({"msg" : "Unable to cancel the order"})