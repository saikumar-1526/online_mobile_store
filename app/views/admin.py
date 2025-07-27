from urllib import request

from flask import Blueprint, render_template, redirect, url_for, jsonify, request
from flask_login import current_user, login_required
from .auth import role_required
from ..models.app_models import Category, Subcategory, Product, db, Model, User, Orders, Payment, Address, AdminNotification
import base64
from ..utils.constants import OrderStatus
from ..utils.email_util import order_email

admin_bp = Blueprint('admin', __name__)

@admin_bp.route("/")
@login_required
@role_required('admin')
def index():
    return render_template('admin/index.html',
                           stats = {
                               'categories': len(Category.query.all()),
                               'subcategories': len(Subcategory.query.all()),
                               'products': len(Product.query.all()),
                               'users': len(User.query.filter_by(role='customer').all()),
                               'orders': len(Orders.query.all()),
                               'payments': len(Payment.query.all())
                           }, user=current_user, notifications = AdminNotification.query.all())

@admin_bp.route("/auth/login/")
def login():
    return render_template('admin/login.html')

@admin_bp.route("/auth/register/")
def register():
    return render_template('admin/register.html')

@admin_bp.route("/categories/add/", methods=['GET', 'POST'])
@login_required
@role_required('admin')
def add_category():
    if(request.method == 'POST'):
        name = request.form["category_name"]
        description = request.form["category_description"]
        is_popular = request.form["is_popular"]
        category = Category(name=name, description=description, is_popular = is_popular)
        try:
            db.session.add(category)
            db.session.commit()
            return redirect(url_for('admin.categories'))
        except Exception as e:
            return jsonify({"message": f"Error: {str(e)}"}), 500
    return render_template('admin/add_category.html', user = current_user)

@admin_bp.route("/categories/view/")
@login_required
@role_required('admin')
def categories():
    categories = Category.query.all()
    return render_template('admin/categories.html', categories=categories, user = current_user)

@admin_bp.route("/categories/sub-categories/add/", methods=['GET', 'POST'])
@login_required
@role_required('admin')
def add_scategory():
    categories = Category.query.all()
    if(request.method == 'POST'):
        name = request.form["sub_category_name"]
        description = request.form["sub_category_description"]
        category_id = request.form["category"]
        is_popular = request.form["is_popular"]
        scategory = Subcategory(name=name, description=description, category_id=category_id)
        try:
            db.session.add(scategory)
            db.session.commit()
            return redirect(url_for('admin.scategories'))
        except Exception as e:
            return jsonify({"message": f"Error: {str(e)}"}), 500
    return render_template('admin/add_scategory.html', categories=categories, user = current_user)

@admin_bp.route("/categories/sub-categories/view/")
@login_required
@role_required('admin')
def scategories():
    scategories = Subcategory.query.all()
    return render_template('admin/scategories.html', scategories = scategories, user = current_user)

@admin_bp.route("/categories/sub-categories/models/add/", methods=['GET', 'POST'])
@login_required
@role_required('admin')
def add_model():
    scategories = Subcategory.query.all()
    if(request.method == 'POST'):
        name = request.form["model_name"]
        description = request.form["model_description"]
        scategory_id = request.form["scategory"]
        is_popular = request.form["is_popular"]
        model = Model(name=name, description=description, sub_category_id=scategory_id)
        try:
            db.session.add(model)
            db.session.commit()
            return redirect(url_for('admin.models'))
        except Exception as e:
            return jsonify({"message": f"Error: {str(e)}"}), 500
    return render_template('admin/add_model.html', scategories=scategories, user = current_user)

@admin_bp.route("/categories/sub-categories/models/view/")
@login_required
@role_required('admin')
def models():
    models = Model.query.all()
    return render_template('admin/models.html', models = models, user = current_user)

@admin_bp.route("/products/add/", methods=['GET', 'POST'])
@login_required
@role_required('admin')
def add_product():
    if(request.method == 'POST'):
        name = request.form["product_name"]
        description = request.form["product_description"]
        image = request.files.get("product_image")
        model_id = request.form["model_id"]
        price = request.form["product_price"]
        quantity = request.form["product_qty"]
        is_popular = request.form["is_popular"]
        print(request.files)
        encoded_img = base64.b64encode(image.read()).decode('utf-8')
        product = Product(name=name, description=description, model_id=model_id, price=price, image=encoded_img, available_qty=quantity)
        try:
            db.session.add(product)
            db.session.commit()
            return redirect(url_for('admin.products'))
        except Exception as e:
            return jsonify({"message": f"Error: {str(e)}"}), 500
    models = Model.query.all()
    return render_template('admin/add_product.html', models=models, user = current_user)

@admin_bp.route("/edit_product/<int:product_id>", methods=['GET', 'POST'])
@login_required
@role_required("admin")
def edit_product(product_id):
    product = Product.query.filter_by(id=product_id).first()
    if(request.method == 'POST'):
        product.name = request.form["product_name"]
        product.description = request.form["product_description"]
        product.model_id = request.form["model_id"]
        product.price = request.form["product_price"]
        product.quantity = request.form["product_qty"]
        product.is_popular = request.form["is_popular"]
        db.session.add(product)
        db.session.commit()
        return redirect(url_for('admin.products'))
    return render_template('admin/edit_product.html', product = product, user = current_user)


@admin_bp.route("/products/view/")
@login_required
@role_required('admin')
def products():
    products = Product.query.all()
    return render_template('admin/products.html', products = products, user = current_user)

@admin_bp.route("/orders/")
@login_required
@role_required('admin')
def orders():
    orders = Orders.query.all()
    return render_template('admin/orders.html', user = current_user, orders=orders)

def get_order_statuses(order_status):
    if(order_status == OrderStatus.PENDING.name):
        return [OrderStatus.ACCEPTED, OrderStatus.DECLINED]
    if(order_status == OrderStatus.ACCEPTED.name):
        return [OrderStatus.DISPATCHED, OrderStatus.DECLINED]
    if(order_status == OrderStatus.DISPATCHED.name):
        return [OrderStatus.SHIPPED, OrderStatus.DECLINED]
    if(order_status == OrderStatus.SHIPPED.name):
        return [OrderStatus.ARRIVED_AT_LOCAL_DP, OrderStatus.DECLINED]
    if(order_status == OrderStatus.ARRIVED_AT_LOCAL_DP.name):
        return [OrderStatus.OUT_FOR_DELIVERY, OrderStatus.DECLINED]
    if(order_status == OrderStatus.OUT_FOR_DELIVERY.name):
        return [OrderStatus.DELIVERED, OrderStatus.DECLINED]
    return [order_status]

@admin_bp.route("/order_detail/<order_id>/")
@login_required
@role_required('admin')
def order_detail(order_id):
    order = Orders.query.filter_by(order_id=order_id).first()
    saddress = Address.query.filter_by(id=order.shipping_address).first()
    baddress = Address.query.filter_by(id=order.billing_address).first()
    return render_template('admin/order_detail.html', user = current_user, order = order,
                           order_statuses = get_order_statuses(order.order_status), saddress=saddress, baddress=baddress)

@admin_bp.route("/payments/")
@login_required
@role_required('admin')
def payments():
    return render_template('admin/payments.html', user = current_user)

@admin_bp.route("/update_status/", methods=['GET', 'POST'])
@login_required
@role_required('admin')
def update_order_status():
    order_id = request.form["order_id"]
    order = Orders.query.filter_by(order_id=order_id).first()
    order.order_status = request.form["status"]
    db.session.add(order)
    db.session.commit()
    order_email(order.user_email, "User", f"Order Status Updated - {order_id}", {
        "order_id" : str(order_id),
        "order_status" : order.order_status,
        "order_details" : f"{request.base_url.replace('/admin/update_status/', '/')}order_detail/{order_id}/"
    })
    return redirect(url_for('admin.order_detail', order_id = order_id))