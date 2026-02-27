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
from datetime import datetime
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
        is_available = BooleanField('Available for Sale')
    
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
        # Get featured products (random 8 products)
        featured_products = Product.query.filter_by(is_available=True).order_by(
            func.random()
        ).limit(8).all()
        
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
                             clothing_count=clothing_count)
    
    @app.route('/about')
    def about():
        """About Us Page"""
        return render_template('about.html')
    
    @app.route('/contact')
    def contact():
        """Contact Us Page"""
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
    # CLI COMMANDS
    # ============================================================
    
    @app.cli.command('init-db')
    def init_db_command():
        """Initialize the database with sample data"""
        db.create_all()
        
        # Check if data already exists
        if User.query.first():
            print('Database already initialized!')
            return
        
        # Create admin user
        admin = User(
            username='admin',
            email='admin@jutta-lagani.com',
            full_name='Admin User',
            is_admin=True
        )
        admin.set_password('admin123')
        db.session.add(admin)
        db.session.commit()

        print('Database initialized successfully!')
        print('Admin login: admin@jutta-lagani.com / admin123')
    
    @app.cli.command('create-master-admin')
    def create_master_admin():
        """Create master admin user"""
        db.create_all()
        
        # Check if master admin already exists
        existing = User.query.filter_by(email='ghimirehimal72@gmail.com').first()
        if existing:
            print('Master admin already exists!')
            return
        
        # Create master admin
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
        
        # Create sample products - Shoes
        shoes_products = [
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
                image='shoe1.jpg'
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
                image='shoe2.jpg'
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
                image='shoe3.jpg'
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
                image='shoe4.jpg'
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
                image='shoe5.jpg'
            ),
        ]
        
        # Create sample products - Clothing
        clothing_products = [
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
                image='cloth1.jpg'
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
                image='cloth2.jpg'
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
                image='cloth3.jpg'
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
                image='cloth4.jpg'
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
                image='cloth5.jpg'
            ),
        ]
        
        # Add all products to database
        for product in shoes_products + clothing_products:
            db.session.add(product)
        
        db.session.commit()
        
        print('Database initialized with sample data!')
        print('Admin login: admin@jutta-lagani.com / admin123')
    
    return app


# ============================================================
# MAIN ENTRY POINT
# ============================================================

if __name__ == '__main__':
    app = create_app()
    
    # Create database tables
    with app.app_context():
        db.create_all()
    
    # Run the application
    port = int(os.environ.get('PORT', 5000))
    debug_mode = os.environ.get('FLASK_DEBUG', '1') == '1'
    app.run(debug=debug_mode, host='0.0.0.0', port=port)
