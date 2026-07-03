import os
import json
from flask import Flask, request, jsonify, render_template, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import SQLAlchemyError
from werkzeug.utils import secure_filename
from config import Config
from models import db, Customer, Product, Order, OrderItem
from utils import save_invoice_pdf, notify_owner_and_customer, send_status_update

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)

# Ensure folders exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['INVOICE_FOLDER'], exist_ok=True)

# ============================
# HOME & PRODUCT PAGES
# ============================

@app.template_filter('pad')
def pad_filter(value, width=4, char='0'):
    """Pad a number with leading zeros."""
    return str(value).rjust(width, char)


@app.route('/')
def index():
    # Fetch all products for new arrivals (limit 4)
    new_arrivals = Product.query.order_by(Product.id.desc()).limit(4).all()
    # For seasonal tabs, we can pass all products and filter in JS, or pass them as JSON
    db_products = Product.query.all()
    all_products = []
    for p in db_products:
        all_products.append({
            'id': p.id,
            'title': p.title,
            'price': float(p.price),  # Decimal ko float mein convert kiya ta k JSON read kar sake
            'category': p.category,
            'stock': p.stock,
            'image_path': p.image_path
        })
    return render_template('index.html', new_arrivals=new_arrivals, all_products=all_products)


@app.route('/products')
def all_products():
    products = Product.query.all()
    return render_template('category.html', products=products, category_name='All Products')




@app.route('/mens')
def mens_collection():
    products = Product.query.filter_by(category='Men').all()
    return render_template('category.html', products=products, category_name='Men')

@app.route('/womens')
def womens_collection():
    products = Product.query.filter_by(category='Women').all()
    return render_template('category.html', products=products, category_name='Women')

@app.route('/product/<int:product_id>')
def product_detail(product_id):
    product = Product.query.get_or_404(product_id)
    return render_template('product.html', product=product)

# ============================
# CART & CHECKOUT
# ============================

@app.route('/cart')
def cart_page():
    return render_template('cart.html')

@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    if request.method == 'POST':
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Invalid data'}), 400

        name = data.get('name')
        whatsapp = data.get('whatsapp')
        address = data.get('address')
        city = data.get('city')
        payment_method = data.get('payment_method')
        cart_items = data.get('cart_items')

        if not all([name, whatsapp, address, city, payment_method, cart_items]):
            return jsonify({'error': 'Missing required fields'}), 400

        try:
            # Customer
            customer = Customer.query.filter_by(whatsapp_number=whatsapp).first()
            if not customer:
                customer = Customer(name=name, whatsapp_number=whatsapp, address=address, city=city)
                db.session.add(customer)
                db.session.flush()

            # Order
            total_amount = 0
            order = Order(customer_id=customer.id, total_amount=0, payment_method=payment_method, order_status='Pending')
            db.session.add(order)
            db.session.flush()

            order_items = []
            for item in cart_items:
                product = Product.query.get(item['product_id'])
                if not product:
                    raise ValueError(f"Product {item['product_id']} not found")
                if product.stock < item['quantity']:
                    raise ValueError(f"Insufficient stock for {product.title}")
                product.stock -= item['quantity']
                total_amount += product.price * item['quantity']
                order_item = OrderItem(order_id=order.id, product_id=product.id, quantity=item['quantity'], price=product.price)
                order_items.append(order_item)
                db.session.add(order_item)

            order.total_amount = total_amount
            db.session.commit()

            # Generate PDF
            pdf_path = save_invoice_pdf(order, customer, order_items)

            # Send WhatsApp notifications
            notify_owner_and_customer(order, customer, order_items, pdf_path)

            return jsonify({'success': True, 'order_id': order.id}), 200

        except (SQLAlchemyError, ValueError) as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 500
        except Exception as e:
            db.session.rollback()
            app.logger.error(f"Checkout error: {e}")
            return jsonify({'error': 'Internal server error'}), 500

    return render_template('checkout.html')

@app.route('/confirmation/<int:order_id>')
def confirmation(order_id):
    order = Order.query.get_or_404(order_id)
    return render_template('confirmation.html', order=order)

# ============================
# ADMIN ROUTES
# ============================

@app.route('/admin/dashboard')
def admin_dashboard():
    total_sales = db.session.query(db.func.sum(Order.total_amount)).scalar() or 0
    pending_orders = Order.query.filter_by(order_status='Pending').count()
    total_products = Product.query.count()
    recent_orders = Order.query.order_by(Order.created_at.desc()).limit(10).all()
    return render_template('admin/dashboard.html',
                           total_sales=total_sales,
                           pending_orders=pending_orders,
                           total_products=total_products,
                           recent_orders=recent_orders)


@app.route('/admin/orders')          # <-- Add this
def admin_orders():
    orders = Order.query.order_by(Order.created_at.desc()).all()
    return render_template('admin/orders.html', orders=orders)



@app.route('/admin/products')
def admin_products():
    products = Product.query.all()
    return render_template('admin/products.html', products=products)

@app.route('/admin/add-product', methods=['POST'])
def add_product():
    title = request.form.get('title')
    price = request.form.get('price')
    category = request.form.get('category')
    stock = request.form.get('stock')
    image = request.files.get('image')

    if not all([title, price, stock]):
        return jsonify({'error': 'Title, Price, and Stock are required'}), 400

    image_path = None
    if image and image.filename:
        filename = secure_filename(image.filename)
        # Add timestamp to avoid collisions
        import time
        filename = f"{int(time.time())}_{filename}"
        image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        image_path = f"uploads/{filename}"

    product = Product(
        title=title,
        price=float(price),
        category=category,
        stock=int(stock),
        image_path=image_path
    )
    db.session.add(product)
    db.session.commit()
    return jsonify({'success': True, 'product_id': product.id})

@app.route('/admin/delete-product/<int:product_id>', methods=['DELETE'])
def delete_product(product_id):
    product = Product.query.get(product_id)
    if not product:
        return jsonify({'error': 'Product not found'}), 404
    # Optionally delete image file
    if product.image_path:
        try:
            os.remove(os.path.join(app.config['UPLOAD_FOLDER'], os.path.basename(product.image_path)))
        except:
            pass
    db.session.delete(product)
    db.session.commit()
    return jsonify({'success': True})

@app.route('/admin/update-order/<int:order_id>', methods=['POST'])
def update_order_status(order_id):
    new_status = request.form.get('status')
    if new_status not in ['Pending', 'Shipped', 'Delivered']:
        return jsonify({'error': 'Invalid status'}), 400
    order = Order.query.get(order_id)
    if not order:
        return jsonify({'error': 'Order not found'}), 404
    order.order_status = new_status
    db.session.commit()

    # Customer ko message bhejo (agar status Pending se change ho)
    if new_status != 'Pending':
        send_status_update(order, new_status)

    return jsonify({'success': True, 'new_status': new_status})


@app.route('/admin/delete-order/<int:order_id>', methods=['DELETE'])
def delete_order(order_id):
    order = Order.query.get(order_id)
    if not order:
        return jsonify({'error': 'Order not found'}), 404
    OrderItem.query.filter_by(order_id=order.id).delete()
    db.session.delete(order)
    db.session.commit()
    return jsonify({'success': True})


@app.route('/admin/edit-product/<int:product_id>', methods=['POST'])
def edit_product(product_id):
    product = Product.query.get_or_404(product_id)
    
    title = request.form.get('title')
    price = request.form.get('price')
    category = request.form.get('category')
    stock = request.form.get('stock')
    image = request.files.get('image')
    
    if not all([title, price, stock]):
        return jsonify({'error': 'Title, Price, and Stock are required'}), 400
    
    product.title = title
    product.price = float(price)
    product.category = category
    product.stock = int(stock)
    
    if image and image.filename:
        # Delete old image if exists
        if product.image_path:
            try:
                old_path = os.path.join(app.config['UPLOAD_FOLDER'], os.path.basename(product.image_path))
                if os.path.exists(old_path):
                    os.remove(old_path)
            except:
                pass
        # Save new image
        filename = secure_filename(image.filename)
        import time
        filename = f"{int(time.time())}_{filename}"
        image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        product.image_path = f"uploads/{filename}"
    
    db.session.commit()
    return jsonify({'success': True})



# ============================
# RUN
# ============================

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, host='0.0.0.0', port=5000)