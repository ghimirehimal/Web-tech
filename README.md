# JUTTA LAGANI - E-Commerce Fashion Website

## GitHub Repository (Mandatory)
Repository URL: https://github.com/ghimirehimal/Web-tech

## Live Deployment URL (Mandatory)
Deployed Website URL: Add your Render public URL here (example: https://jutta-lagani-web.onrender.com)
Local Development URL: http://127.0.0.1:5000

## Project Overview
JUTTA LAGANI is a Flask-based e-commerce platform for ethnic footwear and clothing. It includes customer flows (browse, cart, checkout, profile, wishlist, orders) and admin flows (dashboard, products, orders, product management).

## Academic Integrity and External Resources
- This project submission is original coursework.
- No copied template project has been used as final submission.
- External references used for learning/implementation:
  - Flask documentation: https://flask.palletsprojects.com/
  - Flask-Login documentation: https://flask-login.readthedocs.io/
  - Flask-SQLAlchemy documentation: https://flask-sqlalchemy.palletsprojects.com/
  - Bootstrap documentation: https://getbootstrap.com/docs/5.0/getting-started/introduction/
  - Font Awesome icons: https://fontawesome.com/

## Core Features
- User registration, login, logout, and profile management
- Product browsing by category (shoes, clothing)
- Wishlist and shopping cart functionality
- Checkout and order placement flow
- User order history and order detail views
- Admin dashboard and product/order management
- Responsive UI for desktop and mobile screens

## Latest Fixes (February 27, 2026)
- Landing page featured products now show 5 items at a time.
- Navigation links for Home, Shop, Categories, About, and Contact are wired correctly.
- Contact form now handles POST submission and returns a success flash message.
- Product image rendering now uses local static images with safe fallbacks, reducing external image dependency.
- Placeholder images were removed across key pages (home, shop, product detail, cart, checkout, wishlist, orders, profile, admin products).
- Product seed data was expanded and now includes additional shoes and clothing products.
- Startup and seed flows were hardened so products reliably appear after app start/deploy.

## Tech Stack
- Backend: Python, Flask, Flask-SQLAlchemy, Flask-Login, Flask-Bcrypt
- Frontend: HTML, CSS, JavaScript, Bootstrap 5, Jinja2
- Database: SQLite (local), PostgreSQL (Render production)

## Project Structure
```text
Assignment Python Code/
|- app.py
|- config.py
|- models.py
|- wsgi.py
|- requirements.txt
|- Procfile
|- render.yaml
|- README.md
|- templates/
|- static/
|- instance/
`- ss/
```

## Setup and Run Instructions
1. Clone repository
```bash
git clone https://github.com/ghimirehimal/Web-tech.git
cd "Assignment Python Code"
```

2. Create and activate virtual environment
```bash
python -m venv venv
venv\Scripts\activate
```

3. Install dependencies
```bash
pip install -r requirements.txt
```

4. Run the application
```bash
python app.py
```

5. Open browser
```text
http://127.0.0.1:5000
```

## Render Deployment (Production)
This repository is now prepared for Render with:
- `wsgi.py` production entrypoint
- `Procfile` using Gunicorn (`wsgi:app`)
- `render.yaml` blueprint for web service + PostgreSQL
- PostgreSQL driver included in `requirements.txt`

### Deploy Steps on Render
1. Push latest code to GitHub (already done).
2. In Render dashboard, click `New +` then `Blueprint`.
3. Connect repo `ghimirehimal/Web-tech`.
4. Select this project folder and apply the `render.yaml` config.
5. Wait for build and deploy to complete.
6. Copy Render public URL and paste it in this README under `Deployed Website URL`.

### First Run Note
- Database tables are auto-created on startup via `wsgi.py`.
- Set a strong `SECRET_KEY` in Render environment (blueprint generates one).

## Admin Login
- Email: admin@jutta-lagani.com
- Password: admin123

## Testing Notes
- Validate all major user flows: register/login, browse, cart, checkout, orders
- Validate admin flows: dashboard, products, add/edit/delete product, orders
- Test responsive layout on mobile viewport
- Test in multiple browsers before final submission

## Version Control Status
- Git is used for version control with `.gitignore` included.
- Assignment requires 15-20 commits with clear development history.
- Current branch history should be increased to meet final submission requirement.

## Screenshots (Mandatory)
All screenshots are stored in the `ss/` folder and embedded below.

### Desktop Screenshots

#### 1. Homepage - Hero Section
![Homepage Hero](ss/Screenshot%202026-02-27%20142456.png)

#### 2. Homepage - Category Section
![Homepage Categories](ss/Screenshot%202026-02-27%20142507.png)

#### 3. Homepage - Service Highlights and Featured Products
![Homepage Services Featured](ss/Screenshot%202026-02-27%20142520.png)

#### 4. Homepage - Why Choose Section
![Homepage Why Choose](ss/Screenshot%202026-02-27%20142533.png)

#### 5. Homepage - Newsletter Section
![Homepage Newsletter](ss/Screenshot%202026-02-27%20142543.png)

#### 6. Homepage - Footer Section
![Homepage Footer](ss/Screenshot%202026-02-27%20142550.png)

#### 7. Shop Page
![Shop Page Desktop](ss/Screenshot%202026-02-27%20142601.png)

#### 8. About Page
![About Page Desktop](ss/Screenshot%202026-02-27%20142619.png)

#### 9. Contact Page
![Contact Page Desktop](ss/Screenshot%202026-02-27%20142626.png)

#### 10. My Orders Page
![My Orders Desktop](ss/Screenshot%202026-02-27%20142638.png)

#### 11. Wishlist Page
![Wishlist Desktop](ss/Screenshot%202026-02-27%20142646.png)

#### 12. User Account Dropdown Menu
![User Menu Desktop](ss/Screenshot%202026-02-27%20142655.png)

#### 13. Admin Dashboard
![Admin Dashboard Desktop](ss/Screenshot%202026-02-27%20142703.png)

#### 14. Admin Products Page
![Admin Products Desktop](ss/Screenshot%202026-02-27%20142716.png)

#### 15. Admin Add Product - Top Form Section
![Admin Add Product Top](ss/Screenshot%202026-02-27%20142724.png)

#### 16. Admin Add Product - Bottom Form Section
![Admin Add Product Bottom](ss/Screenshot%202026-02-27%20142731.png)

### Mobile Responsive Screenshots

#### 17. Mobile Homepage - Hero
![Mobile Homepage Hero](ss/Screenshot%202026-02-27%20142829.png)

#### 18. Mobile Homepage - Categories
![Mobile Homepage Categories](ss/Screenshot%202026-02-27%20142835.png)

#### 19. Mobile Homepage - Service Highlights
![Mobile Homepage Services](ss/Screenshot%202026-02-27%20142840.png)

#### 20. Mobile Homepage - Why Choose Section
![Mobile Homepage Why Choose](ss/Screenshot%202026-02-27%20142846.png)

#### 21. Mobile Homepage - Newsletter and Footer Top
![Mobile Homepage Newsletter](ss/Screenshot%202026-02-27%20142850.png)

#### 22. Mobile Footer - Quick Links and Contact
![Mobile Footer Contact](ss/Screenshot%202026-02-27%20142855.png)

#### 23. Mobile Shop Page
![Mobile Shop Page](ss/Screenshot%202026-02-27%20142903.png)

#### 24. Mobile Contact Page
![Mobile Contact Page](ss/Screenshot%202026-02-27%20142917.png)

#### 25. Mobile Navigation Menu
![Mobile Navigation Menu](ss/Screenshot%202026-02-27%20142926.png)

#### 26. Mobile Admin Dashboard
![Mobile Admin Dashboard](ss/Screenshot%202026-02-27%20142934.png)

## Submission Checklist
- Public GitHub repository provided
- README.md included with setup steps
- Screenshots included in README and labeled
- Mobile responsive screenshots included
- Deployment URL section included (update with live URL)
- Ready to include repository URL on documentation cover page

## Author
Himal Ghimire
