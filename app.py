"""
JUTTA LAGANI - Main Flask Application
E-Commerce Fashion Website - Modern Ethno-Urban Fusion

This is the main application file that handles:
- Application configuration
- Database models
- User authentication
- All route handlers
- Template context processors
"""

from flask import Flask, render_template, redirect, url_for, flash, request, session, jsonify
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, SelectField, FloatField, IntegerField, BooleanField
from wtforms.validators import DataRequired, Email, Length, EqualTo, Optional, NumberRange
from werkzeug.utils import secure_filename
from sqlalchemy import func, desc
from datetime import datetime, timedelta
import os
import random
import string

# Import configuration and models
from config import Config
from models import db, User, Product, Order, OrderItem, CartItem, WishlistItem


# ============================================================
# FLASK APPLICATION FACTORY
# ============================================================

def create_app(config_class=Config):
    """
    Application Factory - Creates and configures the Flask application
    """
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Initialize extensions
    db.init_app(app)
    
    # Setup Flask-Login
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'info'
    
    @login_manager.user_loader
    def load_user(user_id):
        """Load user by ID for Flask-Login"""
        return User.query.get(int(user_id))
    
    # ============================================================
    # WTForms Classes
    # ============================================================
    
    class RegistrationForm(FlaskForm):
        """User Registration Form"""
        username = StringField('Username', validators=[
            DataRequired(message='Username is required'),
            Length(min=3, max=80, message='Username must be between 3 and 80 characters')
        ])
        email = StringField('Email', validators=[
            DataRequired(message='Email is required'),
            Email(message='Please enter a valid email address')
        ])
        full_name = StringField('Full Name', validators=[
            Optional()
        ])
        phone = StringField('Phone Number', validators=[
            Optional()
        ])
        password = PasswordField('Password', validators=[
            DataRequired(message='Password is required'),
            Length(min=6, message='Password must be at least 6 characters')
        ])
        confirm_password = PasswordField('Confirm Password', validators=[
            DataRequired(message='Please confirm your password'),
            EqualTo('password', message='Passwords must match')
        ])
    
    class LoginForm(FlaskForm):
        """User Login Form"""
        email = StringField('Email', validators=[
            DataRequired(message='Email is required'),
            Email(message='Please enter a valid email address')
        ])
        password = PasswordField('Password', validators=[
            DataRequired(message='Password is required')
        ])
        remember = BooleanField('Remember Me')
    
    class ProfileForm(FlaskForm):
        """User Profile Update Form"""
        username = StringField('Username', validators=[
            DataRequired(),
            Length(min=3, max=80)
        ])
        email = StringField('Email', validators=[
            DataRequired(),
            Email()
        ])
        full_name = StringField('Full Name', validators=[Optional()])
        phone = StringField('Phone Number', validators=[Optional()])
        address = TextAreaField('Address', validators=[Optional()])
    
    class ProductForm(FlaskForm):
        """Product Management Form (Admin)"""
        name = StringField('Product Name', validators=[
            DataRequired(message='Product name is required'),
            Length(max=200)
        ])
        description = TextAreaField('Description', validators=[
            DataRequired(message='Description is required')
        ])
        price = FloatField('Price', validators=[
            DataRequired(message='Price is required'),
            NumberRange(min=0, message='Price must be positive')
        ])
        original_price = FloatField('Original Price (for discount)', validators=[
            Optional(),
            NumberRange(min=0)
        ])
        category = SelectField('Category', choices=[
            ('shoes', 'Shoes'),
            ('clothing', 'Clothing')
        ], validators=[DataRequired()])
        subcategory = StringField('Subcategory', validators=[Optional()])
        brand = StringField('Brand', validators=[Optional()])
        color = StringField('Color', validators=[Optional()])
        size = StringField('Size', validators=[Optional()])
        material = StringField('Material', validators=[Optional()])
        stock = IntegerField('Stock Quantity', validators=[
            DataRequired(),
            NumberRange(min=0, message='Stock must be positive')
        ])
        is_available = BooleanField('Available for Sale', default=True)
    
    class CheckoutForm(FlaskForm):
        """Checkout Form"""
        shipping_name = StringField('Full Name', validators=[
            DataRequired(message='Name is required')
        ])
        shipping_address = TextAreaField('Address', validators=[
            DataRequired(message='Address is required')
        ])
        shipping_city = StringField('City', validators=[
            DataRequired(message='City is required')
        ])
        shipping_phone = StringField('Phone Number', validators=[
            DataRequired(message='Phone number is required')
        ])
        payment_method = SelectField('Payment Method', choices=[
            ('cod', 'Cash on Delivery'),
            ('card', 'Credit/Debit Card')
        ], validators=[DataRequired()])
    
    # ============================================================
    # TEMPLATE CONTEXT PROCESSORS
    # ============================================================
    
    @app.context_processor
    def inject_cart_count():
        """Inject cart count into all templates"""
        cart_count = 0
        if current_user.is_authenticated:
            cart_count = CartItem.query.filter_by(user_id=current_user.id).count()
        elif 'cart' in session:
            cart_count = len(session.get('cart', []))
        return dict(cart_count=cart_count)
    
    @app.context_processor
    def inject_categories():
        """Inject product categories into templates"""
        return dict(categories=['shoes', 'clothing'])
    
    @app.context_processor
    def inject_template_helpers():
        """Expose helper utilities to templates."""
        def product_image_url(product):
            """Return a safe image URL for a product with category fallback."""
            image_name = getattr(product, 'image', None)
            if image_name:
                if str(image_name).startswith(('http://', 'https://')):
                    return image_name
                local_path = os.path.join(app.static_folder, 'images', image_name)
                if os.path.exists(local_path):
                    return url_for('static', filename=f'images/{image_name}')
            fallback = 'images/product-shoes.svg' if getattr(product, 'category', '') == 'shoes' else 'images/product-clothing.svg'
            return url_for('static', filename=fallback)
        
        return dict(product_image_url=product_image_url)
    
    # ============================================================
    # HELPER FUNCTIONS
    # ============================================================
    
    def get_cart_items():
        """Get cart items for current user or session"""
        cart_items = []
        
        if current_user.is_authenticated:
            # Get cart from database
            cart_db = CartItem.query.filter_by(user_id=current_user.id).all()
            for item in cart_db:
                cart_items.append({
                    'id': item.id,
                    'product': item.product,
                    'quantity': item.quantity,
                    'size': item.size,
                    'color': item.color,
                    'total_price': item.total_price
                })
        else:
            # Get cart from session
            cart_session = session.get('cart', [])
            for item in cart_session:
                product = Product.query.get(item['product_id'])
                if product:
                    cart_items.append({
                        'id': item['id'],
                        'product': product,
                        'quantity': item['quantity'],
                        'size': item.get('size'),
                        'color': item.get('color'),
                        'total_price': product.price * item['quantity']
                    })
        
        return cart_items
    
    def get_cart_total():
        """Calculate total price of cart"""
        items = get_cart_items()
        return sum(item['total_price'] for item in items)
    
    def save_cart_to_session(cart_items):
        """Save cart items to session"""
        session['cart'] = [
            {
                'id': item['id'],
                'product_id': item['product'].id,
                'quantity': item['quantity'],
                'size': item.get('size'),
                'color': item.get('color')
            }
            for item in cart_items
        ]
    
    # ============================================================
    # ROUTES - HOME & GENERAL
    # ============================================================
    
    @app.route('/')
    def index():
        """
        Home Page - Displays featured products and hero section
        """
        # Get featured products (random 5 products)
        featured_products = Product.query.filter_by(is_available=True).order_by(
            func.random()
        ).limit(5).all()
        
        # Get new arrivals (latest 4 products)
        new_arrivals = Product.query.filter_by(is_available=True).order_by(
            Product.created_at.desc()
        ).limit(4).all()
        
        # Get categories with product counts
        shoes_count = Product.query.filter_by(category='shoes', is_available=True).count()
        clothing_count = Product.query.filter_by(category='clothing', is_available=True).count()
        
        return render_template('index.html',
                             featured_products=featured_products,
                             new_arrivals=new_arrivals,
                             shoes_count=shoes_count,
                             clothing_count=clothing_count,
                             datetime=datetime,
                             timedelta=timedelta)
    
    @app.route('/about')
    def about():
        """About Us Page"""
        return render_template('about.html')
    
    @app.route('/contact', methods=['GET', 'POST'])
    def contact():
        """Contact Us Page"""
        if request.method == 'POST':
            flash('Thank you for contacting us. We will get back to you soon.', 'success')
            return redirect(url_for('contact'))
        return render_template('contact.html')
    
    # ============================================================
    # ROUTES - SHOP & PRODUCTS
    # ============================================================
    
    @app.route('/shop')
    @app.route('/shop/<category>')
    def shop(category=None):
        """
        Shop Page - Displays all products with filtering
        """
        # Get query parameters
        page = request.args.get('page', 1, type=int)
        per_page = 12
        sort_by = request.args.get('sort', 'newest')
        search = request.args.get('search', '')
        
        # Build query
        query = Product.query.filter_by(is_available=True)
        
        # Filter by category
        if category and category in ['shoes', 'clothing']:
            query = query.filter_by(category=category)
        
        # Search filter
        if search:
            query = query.filter(
                (Product.name.ilike(f'%{search}%')) |
                (Product.description.ilike(f'%{search}%')) |
                (Product.brand.ilike(f'%{search}%'))
            )
        
        # Sort products
        if sort_by == 'price_low':
            query = query.order_by(Product.price.asc())
        elif sort_by == 'price_high':
            query = query.order_by(Product.price.desc())
        elif sort_by == 'name':
            query = query.order_by(Product.name.asc())
        else:  # newest
            query = query.order_by(Product.created_at.desc())
        
        # Paginate
        products = query.paginate(page=page, per_page=per_page, error_out=False)
        
        # Get category counts
        shoes_count = Product.query.filter_by(category='shoes', is_available=True).count()
        clothing_count = Product.query.filter_by(category='clothing', is_available=True).count()
        
        return render_template('shop.html',
                             products=products,
                             current_category=category,
                             sort_by=sort_by,
                             search=search,
                             shoes_count=shoes_count,
                             clothing_count=clothing_count)
    
    @app.route('/product/<int:product_id>')
    def product_detail(product_id):
        """
        Product Detail Page - Displays single product details
        """
        product = Product.query.get_or_404(product_id)
        
        # Get related products from same category
        related_products = Product.query.filter(
            Product.id != product_id,
            Product.category == product.category,
            Product.is_available == True
        ).limit(4).all()
        
        return render_template('product_detail.html',
                             product=product,
                             related_products=related_products)
    
    # ============================================================
    # ROUTES - WISHLIST
    # ============================================================
    
    @app.route('/wishlist')
    @login_required
    def wishlist():
        wishlist_items = WishlistItem.query.filter_by(user_id=current_user.id).all()
        return render_template('wishlist.html', wishlist_items=wishlist_items)
    
    @app.route('/add_to_wishlist/<int:product_id>')
    @login_required
    def add_to_wishlist(product_id):
        product = Product.query.get_or_404(product_id)
        existing = WishlistItem.query.filter_by(user_id=current_user.id, product_id=product_id).first()
        if existing:
            flash(f'{product.name} is already in your wishlist!', 'info')
        else:
            wishlist_item = WishlistItem(user_id=current_user.id, product_id=product_id)
            db.session.add(wishlist_item)
            db.session.commit()
            flash(f'Added {product.name} to wishlist!', 'success')
        return redirect(url_for('wishlist'))
    
    @app.route('/remove_from_wishlist/<int:wishlist_id>')
    @login_required
    def remove_from_wishlist(wishlist_id):
        wishlist_item = WishlistItem.query.get_or_404(wishlist_id)
        if wishlist_item.user_id == current_user.id:
            product_name = wishlist_item.product.name
            db.session.delete(wishlist_item)
            db.session.commit()
            flash(f'Removed {product_name} from wishlist!', 'success')
        return redirect(url_for('wishlist'))
    
    # ============================================================
    # ROUTES - CART
    # ============================================================
    
    @app.route('/cart')
    def cart():
        """
        Shopping Cart Page
        """
        cart_items = get_cart_items()
        cart_total = get_cart_total()
        
        # Calculate shipping (free over Rs. 1000)
        shipping = 0 if cart_total >= 1000 else 100
        final_total = cart_total + shipping
        
        return render_template('cart.html',
                             cart_items=cart_items,
                             cart_total=cart_total,
                             shipping=shipping,
                             final_total=final_total)
    
    @app.route('/add_to_cart', methods=['POST'])
    @app.route('/add_to_cart/<int:product_id>', methods=['GET', 'POST'])
    def add_to_cart(product_id=None):
        """
        Add Product to Cart
        """
        if request.method == 'POST':
            product_id = request.form.get('product_id', type=int)
            quantity = request.form.get('quantity', 1, type=int)
            size = request.form.get('size')
            color = request.form.get('color')
        else:
            quantity = request.args.get('quantity', 1, type=int)
            size = request.args.get('size')
            color = request.args.get('color')
        
        product = Product.query.get_or_404(product_id)
        
        # Check stock
        if product.stock < quantity:
            flash(f'Sorry, only {product.stock} items available in stock!', 'warning')
            return redirect(url_for('product_detail', product_id=product_id))
        
        if current_user.is_authenticated:
            # Add to database cart
            existing_item = CartItem.query.filter_by(
                user_id=current_user.id,
                product_id=product_id
            ).first()
            
            if existing_item:
                existing_item.quantity += quantity
                db.session.commit()
                flash(f'Updated {product.name} quantity in cart!', 'success')
            else:
                cart_item = CartItem(
                    user_id=current_user.id,
                    product_id=product_id,
                    quantity=quantity,
                    size=size,
                    color=color
                )
                db.session.add(cart_item)
                db.session.commit()
                flash(f'Added {product.name} to cart!', 'success')
        else:
            # Add to session cart
            cart = session.get('cart', [])
            
            # Check if product already in cart
            found = False
            for item in cart:
                if item['product_id'] == product_id:
                    item['quantity'] += quantity
                    found = True
                    break
            
            if not found:
                cart.append({
                    'id': len(cart) + 1,
                    'product_id': product_id,
                    'quantity': quantity,
                    'size': size,
                    'color': color
                })
            
            session['cart'] = cart
            flash(f'Added {product.name} to cart!', 'success')
        
        return redirect(url_for('cart'))
    
    @app.route('/update_cart/<int:cart_item_id>', methods=['POST'])
    def update_cart(cart_item_id):
        """Update cart item quantity"""
        quantity = request.form.get('quantity', 1, type=int)
        
        if current_user.is_authenticated:
            cart_item = CartItem.query.get_or_404(cart_item_id)
            if cart_item.user_id == current_user.id:
                if quantity > 0:
                    cart_item.quantity = quantity
                else:
                    db.session.delete(cart_item)
                db.session.commit()
                flash('Cart updated!', 'success')
        else:
            cart = session.get('cart', [])
            for item in cart:
                if item['id'] == cart_item_id:
                    if quantity > 0:
                        item['quantity'] = quantity
                    else:
                        cart.remove(item)
                    break
            session['cart'] = cart
            flash('Cart updated!', 'success')
        
        return redirect(url_for('cart'))
    
    @app.route('/remove_from_cart/<int:cart_item_id>')
    def remove_from_cart(cart_item_id):
        """Remove item from cart"""
        if current_user.is_authenticated:
            cart_item = CartItem.query.get_or_404(cart_item_id)
            if cart_item.user_id == current_user.id:
                product_name = cart_item.product.name
                db.session.delete(cart_item)
                db.session.commit()
                flash(f'Removed {product_name} from cart!', 'success')
        else:
            cart = session.get('cart', [])
            for item in cart:
                if item['id'] == cart_item_id:
                    cart.remove(item)
                    break
            session['cart'] = cart
            flash('Item removed from cart!', 'success')
        
        return redirect(url_for('cart'))
    
    @app.route('/clear_cart')
    def clear_cart():
        """Clear all cart items"""
        if current_user.is_authenticated:
            CartItem.query.filter_by(user_id=current_user.id).delete()
            db.session.commit()
        else:
            session.pop('cart', None)
        
        flash('Cart cleared!', 'info')
        return redirect(url_for('shop'))
    
    # ============================================================
    # ROUTES - CHECKOUT & ORDERS
    # ============================================================
    
    @app.route('/checkout', methods=['GET', 'POST'])
    @login_required
    def checkout():
        """
        Checkout Page - Process orders
        """
        cart_items = get_cart_items()
        
        if not cart_items:
            flash('Your cart is empty!', 'warning')
            return redirect(url_for('shop'))
        
        # Calculate totals
        cart_total = get_cart_total()
        shipping = 0 if cart_total >= 1000 else 100
        tax = cart_total * 0.10  # 10% tax
        final_total = cart_total + shipping + tax
        
        form = CheckoutForm()
        
        if form.validate_on_submit():
            # Create order
            order = Order(
                order_number=Order.generate_order_number(),
                user_id=current_user.id,
                subtotal=cart_total,
                shipping_cost=shipping,
                tax=tax,
                total_amount=final_total,
                shipping_name=form.shipping_name.data,
                shipping_address=form.shipping_address.data,
                shipping_city=form.shipping_city.data,
                shipping_phone=form.shipping_phone.data,
                payment_method=form.payment_method.data,
                status='pending'
            )
            db.session.add(order)
            db.session.flush()  # Get order ID
            
            # Create order items
            for item in cart_items:
                order_item = OrderItem(
                    order_id=order.id,
                    product_id=item['product'].id,
                    quantity=item['quantity'],
                    unit_price=item['product'].price,
                    total_price=item['total_price'],
                    product_name=item['product'].name,
                    product_image=item['product'].image
                )
                db.session.add(order_item)
                
                # Update product stock
                product = item['product']
                product.stock -= item['quantity']
            
            db.session.commit()
            
            # Clear cart
            CartItem.query.filter_by(user_id=current_user.id).delete()
            db.session.commit()
            
            flash(f'Order placed successfully! Order number: {order.order_number}', 'success')
            return redirect(url_for('order_confirmation', order_id=order.id))
        
        # Pre-fill form with user data
        if request.method == 'GET':
            form.shipping_name.data = current_user.full_name or ''
            form.shipping_phone.data = current_user.phone or ''
        
        return render_template('checkout.html',
                             form=form,
                             cart_items=cart_items,
                             cart_total=cart_total,
                             shipping=shipping,
                             tax=tax,
                             final_total=final_total)
    
    @app.route('/order_confirmation/<int:order_id>')
    @login_required
    def order_confirmation(order_id):
        """Order Confirmation Page"""
        order = Order.query.get_or_404(order_id)
        
        if order.user_id != current_user.id and not current_user.is_admin:
            flash('Unauthorized access!', 'danger')
            return redirect(url_for('index'))
        
        return render_template('order_confirmation.html', order=order)
    
    @app.route('/my_orders')
    @login_required
    def my_orders():
        """User's Order History"""
        orders = Order.query.filter_by(user_id=current_user.id).order_by(
            Order.created_at.desc()
        ).all()
        
        return render_template('my_orders.html', orders=orders)
    
    @app.route('/order/<int:order_id>')
    @login_required
    def order_detail(order_id):
        """Order Details Page"""
        order = Order.query.get_or_404(order_id)
        
        if order.user_id != current_user.id and not current_user.is_admin:
            flash('Unauthorized access!', 'danger')
            return redirect(url_for('index'))
        
        return render_template('order_detail.html', order=order)
    
    # ============================================================
    # ROUTES - AUTHENTICATION
    # ============================================================
    
    # Separate Admin Login Portal
    @app.route('/admin/login', methods=['GET', 'POST'])
    def admin_login():
        """Admin Login Page - Separate from user login"""
        if current_user.is_authenticated and current_user.is_admin:
            return redirect(url_for('admin_dashboard'))
        
        form = LoginForm()
        
        if form.validate_on_submit():
            user = User.query.filter_by(email=form.email.data).first()
            
            if user and user.check_password(form.password.data) and user.is_admin:
                login_user(user, remember=form.remember.data)
                flash(f'Welcome to Admin Panel, {user.username}!', 'success')
                return redirect(url_for('admin_dashboard'))
            else:
                flash('Invalid admin credentials!', 'danger')
        
        return render_template('admin_login.html', form=form)
    
    @app.route('/login', methods=['GET', 'POST'])
    def login():
        """User Login Page"""
        if current_user.is_authenticated:
            return redirect(url_for('index'))
        
        form = LoginForm()
        
        if form.validate_on_submit():
            user = User.query.filter_by(email=form.email.data).first()
            
            if user and user.check_password(form.password.data):
                login_user(user, remember=form.remember.data)
                
                # Redirect to intended page or home
                next_page = request.args.get('next')
                flash(f'Welcome back, {user.username}!', 'success')
                return redirect(next_page) if next_page else redirect(url_for('index'))
            else:
                flash('Login failed! Please check your email and password.', 'danger')
        
        return render_template('login.html', form=form)
    
    @app.route('/register', methods=['GET', 'POST'])
    def register():
        """User Registration Page"""
        if current_user.is_authenticated:
            return redirect(url_for('index'))
        
        form = RegistrationForm()
        
        if form.validate_on_submit():
            # Check if email already exists
            existing_user = User.query.filter(
                (User.email == form.email.data) |
                (User.username == form.username.data)
            ).first()
            
            if existing_user:
                if existing_user.email == form.email.data:
                    flash('Email already registered!', 'danger')
                else:
                    flash('Username already taken!', 'danger')
                return redirect(url_for('register'))
            
            # Create new user
            user = User(
                username=form.username.data,
                email=form.email.data,
                full_name=form.full_name.data,
                phone=form.phone.data
            )
            user.set_password(form.password.data)
            
            # Regular users cannot be admin - admin must be created manually
            user.is_admin = False
            
            db.session.add(user)
            db.session.commit()
            
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('login'))
        
        return render_template('register.html', form=form)
    
    @app.route('/logout')
    @login_required
    def logout():
        """User Logout"""
        logout_user()
        flash('You have been logged out!', 'info')
        return redirect(url_for('index'))
    
    @app.route('/profile', methods=['GET', 'POST'])
    @login_required
    def profile():
        """User Profile Page"""
        form = ProfileForm()
        
        if form.validate_on_submit():
            current_user.username = form.username.data
            current_user.email = form.email.data
            current_user.full_name = form.full_name.data
            current_user.phone = form.phone.data
            current_user.address = form.address.data
            
            db.session.commit()
            flash('Profile updated successfully!', 'success')
            return redirect(url_for('profile'))
        
        # Pre-fill form
        if request.method == 'GET':
            form.username.data = current_user.username
            form.email.data = current_user.email
            form.full_name.data = current_user.full_name or ''
            form.phone.data = current_user.phone or ''
            form.address.data = current_user.address or ''
        
        # Get recent orders
        recent_orders = Order.query.filter_by(
            user_id=current_user.id
        ).order_by(Order.created_at.desc()).limit(5).all()
        
        return render_template('profile.html',
                             form=form,
                             recent_orders=recent_orders)
    
    # ============================================================
    # ROUTES - ADMIN
    # ============================================================
    
    @app.route('/admin')
    @login_required
    def admin_dashboard():
        """Admin Dashboard"""
        if not current_user.is_admin:
            flash('Admin access required!', 'danger')
            return redirect(url_for('index'))
        
        # Check if user is master admin
        is_master = hasattr(current_user, 'is_master_admin') and current_user.is_master_admin
        
        # Statistics
        total_products = Product.query.count()
        total_orders = Order.query.count()
        total_users = User.query.count()
        total_revenue = db.session.query(func.sum(Order.total_amount)).scalar() or 0
        
        # Recent orders
        recent_orders = Order.query.order_by(Order.created_at.desc()).limit(10).all()
        
        # Low stock products
        low_stock = Product.query.filter(Product.stock < 10).limit(5).all()
        
        return render_template('admin_dashboard.html',
                             total_products=total_products,
                             total_orders=total_orders,
                             total_users=total_users,
                             total_revenue=total_revenue,
                             recent_orders=recent_orders,
                             low_stock=low_stock)
    
    @app.route('/admin/products')
    @app.route('/admin/products/<category>')
    @login_required
    def admin_products(category=None):
        """Admin Product Management"""
        if not current_user.is_admin:
            flash('Admin access required!', 'danger')
            return redirect(url_for('index'))
        
        page = request.args.get('page', 1, type=int)
        per_page = 20
        
        query = Product.query
        if category and category in ['shoes', 'clothing']:
            query = query.filter_by(category=category)
        
        products = query.order_by(Product.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return render_template('admin_products.html',
                             products=products,
                             current_category=category)
    
    @app.route('/admin/product/add', methods=['GET', 'POST'])
    @login_required
    def admin_product_add():
        """Add New Product (Admin)"""
        if not current_user.is_admin:
            flash('Admin access required!', 'danger')
            return redirect(url_for('index'))
        
        form = ProductForm()
        if request.method == 'GET':
            form.is_available.data = True
        
        if form.validate_on_submit():
            product = Product(
                name=form.name.data,
                description=form.description.data,
                price=form.price.data,
                original_price=form.original_price.data,
                category=form.category.data,
                subcategory=form.subcategory.data,
                brand=form.brand.data,
                color=form.color.data,
                size=form.size.data,
                material=form.material.data,
                stock=form.stock.data,
                is_available=form.is_available.data,
                image='default-product.jpg'  # Default image
            )
            
            db.session.add(product)
            db.session.commit()
            
            flash(f'Product "{product.name}" added successfully!', 'success')
            return redirect(url_for('admin_products'))
        
        return render_template('admin_product_add.html', form=form, product=None)
    
    @app.route('/admin/product/edit/<int:product_id>', methods=['GET', 'POST'])
    @login_required
    def admin_product_edit(product_id):
        """Edit Product (Admin)"""
        if not current_user.is_admin:
            flash('Admin access required!', 'danger')
            return redirect(url_for('index'))
        
        product = Product.query.get_or_404(product_id)
        form = ProductForm(obj=product)
        
        if form.validate_on_submit():
            product.name = form.name.data
            product.description = form.description.data
            product.price = form.price.data
            product.original_price = form.original_price.data
            product.category = form.category.data
            product.subcategory = form.subcategory.data
            product.brand = form.brand.data
            product.color = form.color.data
            product.size = form.size.data
            product.material = form.material.data
            product.stock = form.stock.data
            product.is_available = form.is_available.data
            
            db.session.commit()
            
            flash(f'Product "{product.name}" updated successfully!', 'success')
            return redirect(url_for('admin_products'))
        
        return render_template('admin_product_add.html', form=form, product=product)
    
    @app.route('/admin/product/delete/<int:product_id>')
    @login_required
    def admin_product_delete(product_id):
        """Delete Product (Admin)"""
        if not current_user.is_admin:
            flash('Admin access required!', 'danger')
            return redirect(url_for('index'))
        
        product = Product.query.get_or_404(product_id)
        product_name = product.name
        
        # Delete related cart items first
        CartItem.query.filter_by(product_id=product_id).delete()
        
        db.session.delete(product)
        db.session.commit()
        
        flash(f'Product "{product_name}" deleted successfully!', 'success')
        return redirect(url_for('admin_products'))
    
    @app.route('/admin/orders')
    @login_required
    def admin_orders():
        """Admin Order Management"""
        if not current_user.is_admin:
            flash('Admin access required!', 'danger')
            return redirect(url_for('index'))
        
        page = request.args.get('page', 1, type=int)
        per_page = 20
        
        status_filter = request.args.get('status')
        
        query = Order.query
        if status_filter:
            query = query.filter_by(status=status_filter)
        
        orders = query.order_by(Order.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return render_template('admin_orders.html', orders=orders, status_filter=status_filter)
    
    @app.route('/admin/order/<int:order_id>')
    @login_required
    def admin_order_detail(order_id):
        """Admin Order Detail"""
        if not current_user.is_admin:
            flash('Admin access required!', 'danger')
            return redirect(url_for('index'))
        
        order = Order.query.get_or_404(order_id)
        
        return render_template('admin_order_detail.html', order=order)
    
    @app.route('/admin/order/update_status/<int:order_id>', methods=['POST'])
    @login_required
    def admin_update_order_status(order_id):
        """Update Order Status (Admin)"""
        if not current_user.is_admin:
            flash('Admin access required!', 'danger')
            return redirect(url_for('index'))
        
        order = Order.query.get_or_404(order_id)
        new_status = request.form.get('status')
        
        order.status = new_status
        db.session.commit()
        
        flash(f'Order status updated to "{new_status}"', 'success')
        return redirect(url_for('admin_order_detail', order_id=order_id))
    
    # ============================================================
    # ERROR HANDLERS
    # ============================================================
    
    @app.errorhandler(404)
    def not_found_error(error):
        """404 Error Page"""
        return render_template('error.html', error_code=404, 
                             error_message='Page not found'), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        """500 Error Page"""
        db.session.rollback()
        return render_template('error.html', error_code=500,
                             error_message='Internal server error'), 500
    
    # ============================================================
    # DATA SEEDING HELPERS
    # ============================================================
    
    def _build_sample_products():
        """Build the default sample products list."""
        return [
            Product(
                name='Traditional Mojari',
                description='Handcrafted leather mojaris with traditional embroidery. Perfect for weddings and festive occasions.',
                price=2499,
                original_price=2999,
                category='shoes',
                subcategory='Mojari',
                brand='JUTTA LAGANI',
                color='Maroon',
                size='6,7,8,9,10',
                material='Genuine Leather',
                stock=50,
                is_available=True,
                image='https://images.unsplash.com/photo-1542291026-7eec264c27ff?auto=format&fit=crop&w=900&q=80'
            ),
            Product(
                name='Urban Jutti',
                description='Modern fusion juttis with contemporary design. Comfortable for daily wear.',
                price=1899,
                original_price=2299,
                category='shoes',
                subcategory='Jutti',
                brand='JUTTA LAGANI',
                color='Gold',
                size='6,7,8,9,10,11',
                material='Synthetic Leather',
                stock=35,
                is_available=True,
                image='https://images.unsplash.com/photo-1514996937319-344454492b37?auto=format&fit=crop&w=900&q=80'
            ),
            Product(
                name='Kolhapuri Chappal',
                description='Traditional Kolhapuri chappals handcrafted by skilled artisans. Durable and stylish.',
                price=1599,
                category='shoes',
                subcategory='Kolhapuri',
                brand='JUTTA LAGANI',
                color='Brown',
                size='7,8,9,10,11',
                material='Leather',
                stock=40,
                is_available=True,
                image='https://images.unsplash.com/photo-1460353581641-37baddab0fa2?auto=format&fit=crop&w=900&q=80'
            ),
            Product(
                name='Loafers Party Wear',
                description='Elegant loafers for party wear. Features embroidered traditional motifs.',
                price=3299,
                original_price=3999,
                category='shoes',
                subcategory='Loafers',
                brand='JUTTA LAGANI',
                color='Black',
                size='7,8,9,10,11',
                material='Premium Leather',
                stock=25,
                is_available=True,
                image='https://images.unsplash.com/photo-1491553895911-0055eca6402d?auto=format&fit=crop&w=900&q=80'
            ),
            Product(
                name='Sports Sneakers',
                description='Comfortable sneakers with ethnic prints. Perfect for casual outings.',
                price=2199,
                category='shoes',
                subcategory='Sneakers',
                brand='JUTTA LAGANI',
                color='Multi',
                size='6,7,8,9,10',
                material='Canvas',
                stock=60,
                is_available=True,
                image='https://images.unsplash.com/photo-1525966222134-fcfa99b8ae77?auto=format&fit=crop&w=900&q=80'
            ),
            Product(
                name='Royal Velvet Jutti',
                description='Premium velvet jutti with detailed zari embroidery for festive wear.',
                price=2799,
                original_price=3399,
                category='shoes',
                subcategory='Jutti',
                brand='JUTTA LAGANI',
                color='Navy',
                size='6,7,8,9,10',
                material='Velvet',
                stock=28,
                is_available=True,
                image='https://images.unsplash.com/photo-1528701800489-20be9c5f6f3a?auto=format&fit=crop&w=900&q=80'
            ),
            Product(
                name='Classic Ethnic Loafers',
                description='Slip-on loafers with handcrafted finish, suitable for formal occasions.',
                price=3599,
                original_price=4299,
                category='shoes',
                subcategory='Loafers',
                brand='JUTTA LAGANI',
                color='Tan',
                size='7,8,9,10,11',
                material='Genuine Leather',
                stock=22,
                is_available=True,
                image='https://images.unsplash.com/photo-1549298916-b41d501d3772?auto=format&fit=crop&w=900&q=80'
            ),
            Product(
                name='Festive Kolhapuri Premium',
                description='Traditional Kolhapuri with cushioned sole and artisan-crafted straps.',
                price=2399,
                category='shoes',
                subcategory='Kolhapuri',
                brand='JUTTA LAGANI',
                color='Brown',
                size='6,7,8,9,10',
                material='Leather',
                stock=34,
                is_available=True,
                image='https://images.unsplash.com/photo-1494496195158-c3becb4f2475?auto=format&fit=crop&w=900&q=80'
            ),
            Product(
                name='Handwoven Bridal Mojari',
                description='Wedding-ready mojari with handwoven detailing and cushioned insole for comfort.',
                price=3899,
                original_price=4599,
                category='shoes',
                subcategory='Mojari',
                brand='JUTTA LAGANI',
                color='Ivory',
                size='6,7,8,9,10',
                material='Leather',
                stock=18,
                is_available=True,
                image='https://images.unsplash.com/photo-1573100925118-870b8efc799d?auto=format&fit=crop&w=900&q=80'
            ),
            Product(
                name='Embroidered Slip-On Jutti',
                description='Elegant slip-on jutti with floral embroidery, ideal for festive occasions.',
                price=2599,
                original_price=3099,
                category='shoes',
                subcategory='Jutti',
                brand='JUTTA LAGANI',
                color='Wine',
                size='6,7,8,9,10',
                material='Textile',
                stock=30,
                is_available=True,
                image='https://images.unsplash.com/photo-1600185365483-26d7a4cc7519?auto=format&fit=crop&w=900&q=80'
            ),
            Product(
                name='Heritage Peshawari Sandal',
                description='Traditional peshawari sandal with reinforced sole and artisan finish.',
                price=2999,
                original_price=3599,
                category='shoes',
                subcategory='Sandal',
                brand='JUTTA LAGANI',
                color='Brown',
                size='7,8,9,10,11',
                material='Genuine Leather',
                stock=26,
                is_available=True,
                image='https://images.unsplash.com/photo-1531312267126-822c7d45d6a4?auto=format&fit=crop&w=900&q=80'
            ),
            Product(
                name='Desert Craft Loafers',
                description='Hand-finished loafers with stitched detailing and soft padded sole.',
                price=3499,
                original_price=4099,
                category='shoes',
                subcategory='Loafers',
                brand='JUTTA LAGANI',
                color='Camel',
                size='7,8,9,10,11',
                material='Leather',
                stock=24,
                is_available=True,
                image='https://images.unsplash.com/photo-1560769629-975ec94e6a86?auto=format&fit=crop&w=900&q=80'
            ),
            Product(
                name='Regal Wedding Mojari',
                description='Premium wedding mojari with antique zari and comfort insole.',
                price=4299,
                original_price=5099,
                category='shoes',
                subcategory='Mojari',
                brand='JUTTA LAGANI',
                color='Gold',
                size='6,7,8,9,10',
                material='Leather',
                stock=16,
                is_available=True,
                image='https://images.unsplash.com/photo-1608256246200-53e635b5b65f?auto=format&fit=crop&w=900&q=80'
            ),
            Product(
                name='Heritage Thread Jutti',
                description='Thread-embroidered jutti inspired by classic North Indian motifs.',
                price=2699,
                original_price=3199,
                category='shoes',
                subcategory='Jutti',
                brand='JUTTA LAGANI',
                color='Rust',
                size='6,7,8,9,10',
                material='Textile',
                stock=29,
                is_available=True,
                image='https://images.unsplash.com/photo-1543163521-1bf539c55dd2?auto=format&fit=crop&w=900&q=80'
            ),
            Product(
                name='Urban Ethnic Slip-On',
                description='Everyday slip-on with ethnic pattern band and lightweight feel.',
                price=2199,
                original_price=2699,
                category='shoes',
                subcategory='Slip-On',
                brand='JUTTA LAGANI',
                color='Grey',
                size='7,8,9,10',
                material='Canvas',
                stock=38,
                is_available=True,
                image='https://images.unsplash.com/photo-1465453869711-7e174808ace9?auto=format&fit=crop&w=900&q=80'
            ),
            Product(
                name='Comfort Fusion Sneakers',
                description='Fusion sneakers with breathable upper and extra arch support.',
                price=3199,
                original_price=3899,
                category='shoes',
                subcategory='Sneakers',
                brand='JUTTA LAGANI',
                color='White',
                size='6,7,8,9,10,11',
                material='Mesh',
                stock=42,
                is_available=True,
                image='https://images.unsplash.com/photo-1542291026-7eec264c27ff?auto=format&fit=crop&w=900&q=80'
            ),
            Product(
                name='Artisan Leather Mule',
                description='Backless leather mule with hand-burnished finish for quick wear.',
                price=2899,
                original_price=3399,
                category='shoes',
                subcategory='Mule',
                brand='JUTTA LAGANI',
                color='Tan',
                size='7,8,9,10',
                material='Leather',
                stock=21,
                is_available=True,
                image='https://images.unsplash.com/photo-1582588678413-dbf45f4823e9?auto=format&fit=crop&w=900&q=80'
            ),
            Product(
                name='Midnight Party Loafers',
                description='Gloss-finish party loafers with elegant silhouette for evening events.',
                price=3899,
                original_price=4599,
                category='shoes',
                subcategory='Loafers',
                brand='JUTTA LAGANI',
                color='Black',
                size='7,8,9,10,11',
                material='Patent Leather',
                stock=19,
                is_available=True,
                image='https://images.unsplash.com/photo-1614252369475-531eba835eb1?auto=format&fit=crop&w=900&q=80'
            ),
            Product(
                name='Classic Brown Brogues',
                description='Traditional brogue detailing blended with modern comfort.',
                price=3599,
                original_price=4299,
                category='shoes',
                subcategory='Brogues',
                brand='JUTTA LAGANI',
                color='Brown',
                size='7,8,9,10,11',
                material='Leather',
                stock=27,
                is_available=True,
                image='https://images.unsplash.com/photo-1614252235316-8c857d38b5f4?auto=format&fit=crop&w=900&q=80'
            ),
            Product(
                name='Gold Festive Khussa',
                description='Festive khussa with metallic detailing for traditional occasions.',
                price=3099,
                original_price=3699,
                category='shoes',
                subcategory='Khussa',
                brand='JUTTA LAGANI',
                color='Gold',
                size='6,7,8,9,10',
                material='Synthetic Leather',
                stock=23,
                is_available=True,
                image='https://images.unsplash.com/photo-1525966222134-fcfa99b8ae77?auto=format&fit=crop&w=900&q=80'
            ),
            Product(
                name='Printed Canvas Jutti',
                description='Colorful printed jutti for everyday ethnic-casual styling.',
                price=1999,
                original_price=2499,
                category='shoes',
                subcategory='Jutti',
                brand='JUTTA LAGANI',
                color='Multi',
                size='6,7,8,9,10',
                material='Canvas',
                stock=44,
                is_available=True,
                image='https://images.unsplash.com/photo-1463100099107-aa0980c362e6?auto=format&fit=crop&w=900&q=80'
            ),
            Product(
                name='Kurta Set - Festive',
                description='Beautiful kurta set with dupatta. Perfect for festive occasions.',
                price=3499,
                original_price=4299,
                category='clothing',
                subcategory='Kurta Set',
                brand='JUTTA LAGANI',
                color='Maroon',
                size='S,M,L,XL,XXL',
                material='Silk Blend',
                stock=30,
                is_available=True,
                image='https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?auto=format&fit=crop&w=900&q=80'
            ),
            Product(
                name='Indo-Western Sherwani',
                description='Modern sherwani with traditional touch. Ideal for groom wear.',
                price=8999,
                original_price=10999,
                category='clothing',
                subcategory='Sherwani',
                brand='JUTTA LAGANI',
                color='Cream',
                size='S,M,L,XL,XXL',
                material='Silk',
                stock=15,
                is_available=True,
                image='https://images.unsplash.com/photo-1593030761757-71fae45fa0e7?auto=format&fit=crop&w=900&q=80'
            ),
            Product(
                name='Palazzo Suit',
                description='Elegant palazzo suit with printed design. Comfortable and stylish.',
                price=2799,
                category='clothing',
                subcategory='Palazzo',
                brand='JUTTA LAGANI',
                color='Blue',
                size='S,M,L,XL',
                material='Cotton',
                stock=45,
                is_available=True,
                image='https://images.unsplash.com/photo-1483985988355-763728e1935b?auto=format&fit=crop&w=900&q=80'
            ),
            Product(
                name='Anarkali Dress',
                description='Royal anarkali dress with heavy work. Perfect for celebrations.',
                price=4599,
                original_price=5499,
                category='clothing',
                subcategory='Anarkali',
                brand='JUTTA LAGANI',
                color='Red',
                size='S,M,L,XL',
                material='Georgette',
                stock=20,
                is_available=True,
                image='https://images.unsplash.com/photo-1496747611176-843222e1e57c?auto=format&fit=crop&w=900&q=80'
            ),
            Product(
                name='Lehenga Choli',
                description='Traditional lehenga with embroidered blouse. Bridal collection.',
                price=6999,
                original_price=8999,
                category='clothing',
                subcategory='Lehenga',
                brand='JUTTA LAGANI',
                color='Pink',
                size='S,M,L,XL',
                material='Silk',
                stock=10,
                is_available=True,
                image='https://images.unsplash.com/photo-1529139574466-a303027c1d8b?auto=format&fit=crop&w=900&q=80'
            ),
            Product(
                name='Printed Cotton Kurti',
                description='Daily-wear cotton kurti with breathable fabric and minimal prints.',
                price=1899,
                original_price=2299,
                category='clothing',
                subcategory='Kurti',
                brand='JUTTA LAGANI',
                color='Mustard',
                size='S,M,L,XL',
                material='Cotton',
                stock=52,
                is_available=True,
                image='https://images.unsplash.com/photo-1434389677669-e08b4cac3105?auto=format&fit=crop&w=900&q=80'
            ),
            Product(
                name='Embroidered Waistcoat Set',
                description='Festive waistcoat set with subtle embroidery for weddings and parties.',
                price=4299,
                original_price=4999,
                category='clothing',
                subcategory='Waistcoat',
                brand='JUTTA LAGANI',
                color='Olive',
                size='M,L,XL,XXL',
                material='Silk Blend',
                stock=18,
                is_available=True,
                image='https://images.unsplash.com/photo-1445205170230-053b83016050?auto=format&fit=crop&w=900&q=80'
            ),
            Product(
                name='Contemporary Pathani Suit',
                description='Modern pathani suit with comfort fit and premium texture.',
                price=5199,
                original_price=6099,
                category='clothing',
                subcategory='Pathani',
                brand='JUTTA LAGANI',
                color='Charcoal',
                size='M,L,XL,XXL',
                material='Rayon Blend',
                stock=20,
                is_available=True,
                image='https://images.unsplash.com/photo-1469334031218-e382a71b716b?auto=format&fit=crop&w=900&q=80'
            ),
            Product(
                name='Silk Festive Kurta',
                description='Premium silk kurta with subtle patterns for festive gatherings.',
                price=3799,
                original_price=4499,
                category='clothing',
                subcategory='Kurta',
                brand='JUTTA LAGANI',
                color='Royal Blue',
                size='M,L,XL,XXL',
                material='Silk',
                stock=24,
                is_available=True,
                image='https://images.unsplash.com/photo-1489987707025-afc232f7ea0f?auto=format&fit=crop&w=900&q=80'
            ),
            Product(
                name='Linen Nehru Jacket',
                description='Lightweight linen Nehru jacket that pairs well with kurtas and shirts.',
                price=2899,
                original_price=3499,
                category='clothing',
                subcategory='Jacket',
                brand='JUTTA LAGANI',
                color='Beige',
                size='M,L,XL',
                material='Linen',
                stock=32,
                is_available=True,
                image='https://images.unsplash.com/photo-1591047139829-d91aecb6caea?auto=format&fit=crop&w=900&q=80'
            ),
            Product(
                name='Embroidered Anarkali Gown',
                description='Floor-length embroidered anarkali gown for weddings and celebrations.',
                price=6299,
                original_price=7599,
                category='clothing',
                subcategory='Anarkali',
                brand='JUTTA LAGANI',
                color='Emerald',
                size='S,M,L,XL',
                material='Georgette',
                stock=14,
                is_available=True,
                image='https://images.unsplash.com/photo-1464863979621-258859e62245?auto=format&fit=crop&w=900&q=80'
            ),
            Product(
                name='Handblock Printed Kurta',
                description='Soft handblock-printed kurta designed for all-day comfort.',
                price=2499,
                original_price=2999,
                category='clothing',
                subcategory='Kurta',
                brand='JUTTA LAGANI',
                color='Indigo',
                size='S,M,L,XL',
                material='Cotton',
                stock=36,
                is_available=True,
                image='https://images.unsplash.com/photo-1503342217505-b0a15ec3261c?auto=format&fit=crop&w=900&q=80'
            ),
            Product(
                name='Festive Chikankari Kurta',
                description='Elegant chikankari kurta crafted for celebrations and family events.',
                price=3299,
                original_price=3899,
                category='clothing',
                subcategory='Kurta',
                brand='JUTTA LAGANI',
                color='Off White',
                size='M,L,XL,XXL',
                material='Cotton Silk',
                stock=22,
                is_available=True,
                image='https://images.unsplash.com/photo-1524504388940-b1c1722653e1?auto=format&fit=crop&w=900&q=80'
            ),
            Product(
                name='Velvet Sherwani Set',
                description='Royal velvet sherwani set with premium buttons and contrast stole.',
                price=10999,
                original_price=12999,
                category='clothing',
                subcategory='Sherwani',
                brand='JUTTA LAGANI',
                color='Burgundy',
                size='M,L,XL,XXL',
                material='Velvet',
                stock=12,
                is_available=True,
                image='https://images.unsplash.com/photo-1592878849122-5c3ad22e1a6b?auto=format&fit=crop&w=900&q=80'
            ),
            Product(
                name='Casual Cotton Pathani',
                description='Relaxed-fit cotton pathani with clean lines and breathable fabric.',
                price=2999,
                original_price=3599,
                category='clothing',
                subcategory='Pathani',
                brand='JUTTA LAGANI',
                color='Slate',
                size='M,L,XL',
                material='Cotton',
                stock=28,
                is_available=True,
                image='https://images.unsplash.com/photo-1475180098004-ca77a66827be?auto=format&fit=crop&w=900&q=80'
            ),
            Product(
                name='Zari Border Saree',
                description='Classic saree with shimmering zari border for festive elegance.',
                price=5599,
                original_price=6699,
                category='clothing',
                subcategory='Saree',
                brand='JUTTA LAGANI',
                color='Magenta',
                size='Free Size',
                material='Silk Blend',
                stock=17,
                is_available=True,
                image='https://images.unsplash.com/photo-1610030469983-98e550d6193c?auto=format&fit=crop&w=900&q=80'
            ),
            Product(
                name='Embroidered Palazzo Set Plus',
                description='Premium embroidered palazzo set with matching dupatta.',
                price=4999,
                original_price=5899,
                category='clothing',
                subcategory='Palazzo',
                brand='JUTTA LAGANI',
                color='Teal',
                size='S,M,L,XL',
                material='Georgette',
                stock=20,
                is_available=True,
                image='https://images.unsplash.com/photo-1487412947147-5cebf100ffc2?auto=format&fit=crop&w=900&q=80'
            ),
            Product(
                name='Asymmetric Indo Jacket',
                description='Asymmetric Indo-western jacket for modern ceremonial looks.',
                price=4699,
                original_price=5599,
                category='clothing',
                subcategory='Jacket',
                brand='JUTTA LAGANI',
                color='Navy',
                size='M,L,XL',
                material='Silk Blend',
                stock=15,
                is_available=True,
                image='https://images.unsplash.com/photo-1617137968427-85924c800a22?auto=format&fit=crop&w=900&q=80'
            ),
            Product(
                name='Pastel Kurta Pajama',
                description='Pastel kurta pajama set designed for daytime functions and comfort.',
                price=3199,
                original_price=3899,
                category='clothing',
                subcategory='Kurta Set',
                brand='JUTTA LAGANI',
                color='Mint',
                size='S,M,L,XL',
                material='Cotton Linen',
                stock=30,
                is_available=True,
                image='https://images.unsplash.com/photo-1509631179647-0177331693ae?auto=format&fit=crop&w=900&q=80'
            ),
            Product(
                name='Royal Banarasi Lehenga',
                description='Luxury banarasi lehenga set with rich weaving and festive shine.',
                price=12999,
                original_price=15499,
                category='clothing',
                subcategory='Lehenga',
                brand='JUTTA LAGANI',
                color='Royal Red',
                size='S,M,L,XL',
                material='Banarasi Silk',
                stock=8,
                is_available=True,
                image='https://images.unsplash.com/photo-1610189020986-6f6f0baf45fd?auto=format&fit=crop&w=900&q=80'
            ),
            Product(
                name='Threadwork Waistcoat Premium',
                description='Detailed threadwork waistcoat for weddings and festive layering.',
                price=3599,
                original_price=4299,
                category='clothing',
                subcategory='Waistcoat',
                brand='JUTTA LAGANI',
                color='Maroon',
                size='M,L,XL,XXL',
                material='Jacquard',
                stock=19,
                is_available=True,
                image='https://images.unsplash.com/photo-1487222477894-8943e31ef7b2?auto=format&fit=crop&w=900&q=80'
            ),
        ]
    
    def seed_sample_products():
        """
        Insert sample products if missing and upgrade invalid legacy image refs.
        Uses product name uniqueness to keep the operation idempotent.
        """
        sample_products = _build_sample_products()
        sample_by_name = {product.name: product for product in sample_products}
        sample_names = list(sample_by_name.keys())
        
        existing_products = Product.query.filter(Product.name.in_(sample_names)).all()
        existing_by_name = {product.name: product for product in existing_products}
        
        products_to_add = []
        images_updated = 0
        
        for sample in sample_products:
            existing = existing_by_name.get(sample.name)
            if not existing:
                products_to_add.append(sample)
                continue
            
            # Upgrade old local placeholders (shoe1.jpg/cloth1.jpg/default image)
            # to valid URL images only when the current image reference is invalid.
            current_image = (existing.image or '').strip()
            current_is_url = current_image.startswith(('http://', 'https://'))
            current_local_exists = bool(current_image) and os.path.exists(
                os.path.join(app.static_folder, 'images', current_image)
            )
            should_upgrade_image = (
                not current_image
                or current_image == 'default-product.jpg'
                or (not current_is_url and not current_local_exists)
            )
            
            if should_upgrade_image and sample.image:
                existing.image = sample.image
                images_updated += 1
        
        for product in products_to_add:
            db.session.add(product)
        
        if products_to_add or images_updated:
            db.session.commit()
        
        return len(products_to_add), images_updated
    
    # ============================================================
    # CLI COMMANDS
    # ============================================================
    
    @app.cli.command('init-db')
    def init_db_command():
        """Initialize database tables, default admin, and sample products."""
        db.create_all()
        
        admin = User.query.filter_by(email='admin@jutta-lagani.com').first()
        if not admin:
            admin = User(
                username='admin',
                email='admin@jutta-lagani.com',
                full_name='Admin User',
                is_admin=True
            )
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.commit()
            print('Default admin created: admin@jutta-lagani.com / admin123')
        else:
            print('Default admin already exists.')
        
        added_count, updated_images = seed_sample_products()
        if added_count:
            print(f'Added {added_count} sample products.')
        if updated_images:
            print(f'Updated images for {updated_images} existing products.')
        if not added_count and not updated_images:
            print('Sample products already up to date.')
    
    @app.cli.command('seed-products')
    def seed_products_command():
        """Insert sample products if missing."""
        db.create_all()
        added_count, updated_images = seed_sample_products()
        if added_count:
            print(f'Added {added_count} sample products.')
        if updated_images:
            print(f'Updated images for {updated_images} existing products.')
        if not added_count and not updated_images:
            print('No new sample products were added.')
    
    @app.cli.command('create-master-admin')
    def create_master_admin():
        """Create master admin user and ensure sample products exist."""
        db.create_all()
        
        existing = User.query.filter_by(email='ghimirehimal72@gmail.com').first()
        if existing:
            print('Master admin already exists!')
        else:
            master_admin = User(
                username='master_admin',
                email='ghimirehimal72@gmail.com',
                full_name='Master Admin',
                is_admin=True,
                is_master_admin=True
            )
            master_admin.set_password('Prasad@06128@$')
            db.session.add(master_admin)
            db.session.commit()
            
            print('Master admin created successfully!')
            print('Email: ghimirehimal72@gmail.com')
            print('Password: Prasad@06128@$')
        
        added_count, updated_images = seed_sample_products()
        if added_count:
            print(f'Added {added_count} sample products.')
        if updated_images:
            print(f'Updated images for {updated_images} existing products.')
        if not added_count and not updated_images:
            print('Sample products already up to date.')
    
    # Expose helper for startup scripts (wsgi/main entrypoint).
    app.seed_sample_products = seed_sample_products
    
    return app


# ============================================================
# MAIN ENTRY POINT
# ============================================================

if __name__ == '__main__':
    app = create_app()
    
    # Create database tables
    with app.app_context():
        db.create_all()
        app.seed_sample_products()
    
    # Run the application
    port = int(os.environ.get('PORT', 5000))
    debug_mode = os.environ.get('FLASK_DEBUG', '1') == '1'
    app.run(debug=debug_mode, host='0.0.0.0', port=port)
