# JUTTA LAGANI - E-Commerce Fashion Website

![JUTTA LAGANI](https://via.placeholder.com/1200x400/8B0000/FFFFFF?text=JUTTA+LAGANI)

Modern Ethno-Urban Fashion E-Commerce Website built with Flask, Bootstrap 5, and modern web technologies.

## 📋 Project Overview

**JUTTA LAGANI** is a full-featured e-commerce platform specializing in ethnic footwear (shoes) and clothing with a modern ethno-urban fusion theme. The application includes complete shopping functionality, user authentication, admin panel, and responsive design.

### Key Features

- 🛍️ **Product Catalog** - Browse shoes and clothing with categories, filtering, and search
- 👤 **User Authentication** - Registration, login, logout with session management
- 🛒 **Shopping Cart** - Add/remove items, quantity management
- 💳 **Checkout System** - Order placement with address and payment selection
- 👑 **Admin Panel** - Product management, order management, dashboard
- 📱 **Responsive Design** - Works on mobile, tablet, and desktop
- 🎨 **Modern UI** - Beautiful Bootstrap 5 design with custom styling

## 🛠️ Technology Stack

### Frontend
- HTML5
- CSS3 (Custom + Bootstrap 5)
- JavaScript (jQuery)
- Bootstrap 5

### Backend
- Python 3.x
- Flask Framework
- Flask-SQLAlchemy
- Flask-Login
- Flask-Bcrypt
- Jinja2 Templating

### Database
- SQLite (default)

## 📁 Project Structure

```
JUTTA_LAGANI/
├── app.py                  # Main Flask application
├── config.py               # Configuration settings
├── models.py               # Database models
├── requirements.txt        # Python dependencies
├── README.md               # Project documentation
├── templates/              # HTML templates
│   ├── base.html           # Base template
│   ├── index.html          # Home page
│   ├── shop.html           # Product listing
│   ├── product_detail.html # Product details
│   ├── cart.html           # Shopping cart
│   ├── checkout.html       # Checkout page
│   ├── login.html          # Login page
│   ├── register.html       # Registration page
│   ├── profile.html        # User profile
│   ├── admin_dashboard.html # Admin dashboard
│   ├── admin_products.html # Admin products
│   ├── admin_product_add.html # Add/Edit product
│   └── ...                 # Other templates
└── static/                 # Static files
    ├── css/
    │   ├── style.css       # Main styles
    │   └── responsive.css  # Responsive styles
    └── js/
        ├── main.js         # Main JavaScript
        └── validation.js   # Form validation
```

## 🚀 Getting Started

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

### Installation

1. **Clone the repository**
   
```
bash
   git clone <repository-url>
   cd JUTTA_LAGANI
   
```

2. **Create virtual environment**
   
```
bash
   python -m venv venv
   
```

3. **Activate virtual environment**
   - Windows: `venv\Scripts\activate`
   - Linux/Mac: `source venv/bin/activate`

4. **Install dependencies**
   
```
bash
   pip install -r requirements.txt
   
```

5. **Initialize the database**
   
```
bash
   flask init-db
   
```
   Or run:
   
```
bash
   python -c "from app import create_app, db; app = create_app(); app.app_context().push(); db.create_all()"
   
```

6. **Run the application**
   
```
bash
   python app.py
   
```

7. **Open in browser**
   Navigate to: `http://localhost:5000`

### Default Admin Credentials

After running `flask init-db`:
- Email: `admin@jutta-lagani.com`
- Password: `admin123`

## 📱 Pages

### Customer Pages
1. **Home** (`/`) - Hero section, featured products, categories
2. **Shop** (`/shop`) - Product listing with filters
3. **Product Details** (`/product/<id>`) - Single product view
4. **Cart** (`/cart`) - Shopping cart
5. **Checkout** (`/checkout`) - Order placement
6. **Login** (`/login`) - User login
7. **Register** (`/register`) - User registration
8. **Profile** (`/profile`) - User account
9. **My Orders** (`/my_orders`) - Order history
10. **About** (`/about`) - About page
11. **Contact** (`/contact`) - Contact page

### Admin Pages
1. **Dashboard** (`/admin`) - Statistics and overview
2. **Products** (`/admin/products`) - Product listing
3. **Add Product** (`/admin/product/add`) - Add new product
4. **Edit Product** (`/admin/product/edit/<id>`) - Edit product
5. **Orders** (`/admin/orders`) - Order management

## 🎨 Design

### Color Scheme
- Primary: Deep Maroon (#8B0000)
- Secondary: Gold (#D4AF37)
- Accent: Charcoal (#333333)
- Background: Off-white (#F5F5F5)

### Typography
- Headings: Playfair Display
- Body: Roboto

## 🔧 Configuration

Edit `config.py` to customize:
- Database URI
- Secret key
- Upload folder
- Session settings

## 📝 License

This project is for educational purposes.

## 👨‍💻 Author

Developed for JUTTA LAGANI - Modern Ethno-Urban Fashion Brand

## 🙏 Acknowledgments

- Bootstrap 5
- Flask Documentation
- Font Awesome
- Google Fonts
