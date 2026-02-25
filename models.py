"""
JUTTA LAGANI - Database Models
E-Commerce Fashion Website - Modern Ethno-Urban Fusion

Models:
- User: Authentication and user information
- Product: Products catalog (shoes and clothing)
- Order: Customer orders
- OrderItem: Individual items in an order
- CartItem: Shopping cart items
"""

from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

# Initialize SQLAlchemy
db = SQLAlchemy()


class User(UserMixin, db.Model):
    """
    User Model - Handles user authentication and profile information
    """
    __tablename__ = 'users'
    
    # Primary Key
    id = db.Column(db.Integer, primary_key=True)
    
    # User Information
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    full_name = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    address = db.Column(db.Text)
    
    # Role Management
    is_admin = db.Column(db.Boolean, default=False)
    is_master_admin = db.Column(db.Boolean, default=False)  # Only one master admin
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    orders = db.relationship('Order', backref='user', lazy=True, cascade='all, delete-orphan')
    cart_items = db.relationship('CartItem', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def set_password(self, password):
        """Hash and set the user password"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Verify the user password"""
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<User {self.username}>'


class Product(db.Model):
    """
    Product Model - Handles products catalog (Shoes and Clothing)
    """
    __tablename__ = 'products'
    
    # Primary Key
    id = db.Column(db.Integer, primary_key=True)
    
    # Product Information
    name = db.Column(db.String(200), nullable=False, index=True)
    description = db.Column(db.Text, nullable=False)
    price = db.Column(db.Float, nullable=False)
    original_price = db.Column(db.Float)  # For showing discounts
    
    # Category Management
    category = db.Column(db.String(50), nullable=False)  # 'shoes' or 'clothing'
    subcategory = db.Column(db.String(50))  # More specific category
    
    # Product Details
    brand = db.Column(db.String(100))
    color = db.Column(db.String(50))
    size = db.Column(db.String(50))
    material = db.Column(db.String(100))
    
    # Stock Management
    stock = db.Column(db.Integer, default=0)
    is_available = db.Column(db.Boolean, default=True)
    
    # Product Images
    image = db.Column(db.String(200), default='default-product.jpg')
    images = db.Column(db.JSON)  # Multiple images for gallery
    
    # SEO and Tags
    tags = db.Column(db.String(500))
    meta_title = db.Column(db.String(200))
    meta_description = db.Column(db.Text)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    order_items = db.relationship('OrderItem', backref='product', lazy=True)
    cart_items = db.relationship('CartItem', backref='product', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Product {self.name}>'
    
    @property
    def discount_percentage(self):
        """Calculate discount percentage"""
        if self.original_price and self.original_price > self.price:
            return int(((self.original_price - self.price) / self.original_price) * 100)
        return 0


class Order(db.Model):
    """
    Order Model - Handles customer orders
    """
    __tablename__ = 'orders'
    
    # Primary Key
    id = db.Column(db.Integer, primary_key=True)
    
    # Order Information
    order_number = db.Column(db.String(50), unique=True, nullable=False, index=True)
    status = db.Column(db.String(50), default='pending')  # pending, processing, shipped, delivered, cancelled
    
    # Financial Information
    subtotal = db.Column(db.Float, nullable=False)
    shipping_cost = db.Column(db.Float, default=0)
    tax = db.Column(db.Float, default=0)
    total_amount = db.Column(db.Float, nullable=False)
    
    # Shipping Information
    shipping_name = db.Column(db.String(100))
    shipping_address = db.Column(db.Text)
    shipping_city = db.Column(db.String(100))
    shipping_phone = db.Column(db.String(20))
    
    # Payment Information
    payment_method = db.Column(db.String(50))
    payment_status = db.Column(db.String(50), default='pending')
    transaction_id = db.Column(db.String(100))
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Foreign Keys
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Relationships
    items = db.relationship('OrderItem', backref='order', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Order {self.order_number}>'
    
    @staticmethod
    def generate_order_number():
        """Generate unique order number"""
        from time import strftime
        import random
        return f'JL-{strftime("%Y%m%d")}-{random.randint(1000, 9999)}'


class OrderItem(db.Model):
    """
    OrderItem Model - Individual items in an order
    """
    __tablename__ = 'order_items'
    
    # Primary Key
    id = db.Column(db.Integer, primary_key=True)
    
    # Item Details
    quantity = db.Column(db.Integer, nullable=False)
    unit_price = db.Column(db.Float, nullable=False)  # Price at time of order
    total_price = db.Column(db.Float, nullable=False)  # quantity * unit_price
    
    # Product Info (stored for historical records)
    product_name = db.Column(db.String(200))
    product_image = db.Column(db.String(200))
    
    # Foreign Keys
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    
    def __repr__(self):
        return f'<OrderItem {self.product_name}>'


class CartItem(db.Model):
    """
    CartItem Model - Shopping cart items
    """
    __tablename__ = 'cart_items'
    
    # Primary Key
    id = db.Column(db.Integer, primary_key=True)
    
    # Item Details
    quantity = db.Column(db.Integer, default=1)
    size = db.Column(db.String(20))
    color = db.Column(db.String(50))
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Foreign Keys
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    
    def __repr__(self):
        return f'<CartItem Product:{self.product_id} Quantity:{self.quantity}>'
    
    @property
    def total_price(self):
        """Calculate total price for this cart item"""
        if self.product:
            return self.product.price * self.quantity
        return 0


class WishlistItem(db.Model):
    """
    WishlistItem Model - User wishlist items
    """
    __tablename__ = 'wishlist_items'
    
    # Primary Key
    id = db.Column(db.Integer, primary_key=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Foreign Keys
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    
    # Relationships
    product = db.relationship('Product', backref='wishlist_items')
    
    def __repr__(self):
        return f'<WishlistItem Product:{self.product_id} User:{self.user_id}>'
