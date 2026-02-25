"""
JUTTA LAGANI - Configuration Settings
E-Commerce Fashion Website - Modern Ethno-Urban Fusion
"""

import os
from datetime import timedelta

class Config:
    # Secret key for session management and flash messages
    SECRET_KEY = 'jutta-lagani-secret-key-2024'
    
    # Database Configuration
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(BASE_DIR, 'instance', 'jutta_lagani.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False
    
    # Session Configuration
    SESSION_COOKIE_SECURE = False
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)
    
    # Upload Configuration
    UPLOAD_FOLDER = 'static/images'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
    
    # Pagination
    PRODUCTS_PER_PAGE = 12
    
    # Application Info
    APP_NAME = 'JUTTA LAGANI'
    APP_TAGLINE = 'Modern Ethno-Urban Fashion'
    
    # Nepal Contact Info
    CONTACT_ADDRESS = 'Thali, Kageshwori Manohara Ward No.5, Kathmandu, Nepal'
    CONTACT_PHONE = '9745946999'
    CONTACT_EMAIL = 'ghimirehimal777@gmail.com'
    
    # Currency
    CURRENCY = 'NPR'
    CURRENCY_SYMBOL = 'Rs'
    
    # Delivery
    FREE_SHIPPING_AMOUNT = 1000
    SHIPPING_COST = 150
    
    # Admin Configuration
    ADMIN_EMAIL = 'admin@jutta-lagani.com'
    NOTIFICATION_EMAIL = 'ghimirehimal777@gmail.com'
