# JUTTA LAGANI - E-Commerce Fashion Brand Website

## Project Overview
- **Project Name**: JUTTA LAGANI
- **Type**: E-commerce Fashion Website (Shoes & Clothing)
- **Theme**: Modern Ethno-Urban Fusion
- **Target Audience**: Fashion-conscious urban customers looking for ethnic-inspired modern footwear and apparel

## Technical Stack
- **Frontend**: HTML5, CSS3, Bootstrap 5, JavaScript, jQuery
- **Backend**: Flask (Python), Jinja2 Templating
- **Database**: SQLite with Flask-SQLAlchemy
- **Authentication**: User sessions with Flask-Login

---

## Documentation Requirements

### 1. Project Proposal (4 marks)
- **Project Title**: JUTTA LAGANI - Modern Ethno-Urban Fashion
- **Description**: An e-commerce platform for selling ethnic-inspired urban footwear and clothing
- **Target Audience**: Urban youth and fashion enthusiasts
- **Problem Statement**: Need for modern ethnic fashion in online retail
- **Objectives**: Online product catalog, shopping cart, user authentication, order management
- **Scope**: Single vendor e-commerce with admin panel

### 2. Information Architecture (3 marks)
- **Sitemap**:
  1. Home
  2. Shop (All Products)
  3. Product Details
  4. Cart
  5. Checkout
  6. User Account (Login/Register)
  7. Admin Dashboard

### 3. UI/UX Design
- **Color Scheme**: 
  - Primary: Deep Maroon (#8B0000)
  - Secondary: Gold (#D4AF37)
  - Accent: Charcoal (#333333)
  - Background: Off-white (#F5F5F5)
- **Typography**: 
  - Headings: Playfair Display
  - Body: Roboto

---

## Website Structure (5+ Pages)

### Pages Required:
1. **index.html** - Home page with hero section and featured products
2. **shop.html** - Product listing with filters
3. **product_detail.html** - Individual product view
4. **cart.html** - Shopping cart
5. **checkout.html** - Order placement
6. **login.html** - User login
7. **register.html** - User registration
8. **profile.html** - User profile and order history
9. **admin_dashboard.html** - Admin product management
10. **admin_products.html** - Add/Edit products

---

## Features List

### Customer Features:
- Browse products by category (Shoes, Clothing)
- View product details
- Add to cart
- Checkout and place orders
- User registration and login
- View order history
- Update profile

### Admin Features:
- Add new products
- Edit existing products
- Delete products
- View all orders
- Manage inventory

---

## File Structure
```
JUTTA_LAGANI/
├── app.py                  # Main Flask application
├── config.py               # Configuration settings
├── models.py               # Database models
├── requirements.txt        # Python dependencies
├── static/
│   ├── css/
│   │   ├── style.css       # Custom styles
│   │   └── responsive.css  # Responsive styles
│   ├── js/
│   │   ├── main.js         # JavaScript functionality
│   │   └── validation.js   # Form validation
│   └── images/             # Product images
├── templates/
│   ├── base.html           # Base template
│   ├── index.html          # Home page
│   ├── shop.html           # Shop page
│   ├── product_detail.html # Product details
│   ├── cart.html           # Cart page
│   ├── checkout.html       # Checkout page
│   ├── login.html          # Login page
│   ├── register.html       # Register page
│   ├── profile.html        # User profile
│   ├── admin_dashboard.html # Admin dashboard
│   └── admin_product.html  # Admin product management
└── README.md               # Project documentation
```

---

## Implementation Steps

### Phase 1: Backend Setup
1. Create Flask application structure
2. Set up database models (User, Product, Order, Cart)
3. Configure authentication
4. Create routes and views

### Phase 2: Frontend Development
1. Create base template with navigation
2. Build home page with hero section
3. Create product listing page
4. Build product detail page
5. Create cart functionality
6. Build checkout page

### Phase 3: Authentication
1. User registration system
2. Login/logout functionality
3. Session management
4. Password hashing

### Phase 4: Admin Panel
1. Admin dashboard
2. Product CRUD operations
3. Order management

### Phase 5: JavaScript & Interactivity
1. Form validation
2. Dynamic cart updates
3. Interactive UI elements

---

## Acceptance Criteria

### Frontend (10 marks)
- [ ] Responsive design works on mobile, tablet, desktop
- [ ] At least 5 interconnected pages
- [ ] Form validation on all forms
- [ ] Modern UI with Bootstrap
- [ ] Interactive features (modals, dropdowns, cart updates)

### Backend (12 marks)
- [ ] Flask routes working correctly
- [ ] Database operations (CRUD)
- [ ] User authentication functioning
- [ ] Session management
- [ ] Flash messages for feedback

### Code Quality (6 marks)
- [ ] Clean, commented code
- [ ] Proper file structure
- [ ] Consistent naming conventions

### GitHub (4 marks)
- [ ] Well-organized repository
- [ ] 15-20 meaningful commits
- [ ] Complete README.md
- [ ] .gitignore file
