# Khoutwa E-commerce Platform | Backend API ⚙️

A production-ready, highly optimized backend built with **Django** and **Django REST Framework (DRF)**. Designed to seamlessly serve the Khoutwa React strictly via API, prioritizing clean architecture, security, and scalability.

---

## 🎯 Key Features & Architecture

- **Custom Authentication Security:** Uses Djoser and `rest_framework_simplejwt` for secure, stateless token-based authentication designed specifically for robust frontend integration.
- **Database Optimization:** Implements advanced query optimization utilizing Django's `select_related`, `prefetch_related`, and `bulk_create` (e.g., Order creation) to strictly avoid N+1 query problems.
- **Dynamic E-Commerce Logic:** Handles complex Cart synchronization across local states, Wishlist management, and dynamic pricing rules (e.g., Wholesale discounts).
- **Scalable Product Catalog:** Capable of handling complex nested filtering via `django-filter` (price mapping, category slugs, search parameters).
- **Docker-Ready:** Fully containerized environment orchestrating Django, PostgreSQL, and Gunicorn.

---

## 📂 Project Structure & App Responsibilities

Our backend is strictly separated into modular Django applications to respect the Single Responsibility Principle:

```text
backend/
├── khoutwa_backend/       # ⚙️ Core Configuration (settings.py, urls.py, wsgi, asgi)
├── accounts/              # 👤 Users & Profiles (Custom Auth Model, Role-Based Access)
├── products/              # 🛍️ Catalog (Products, Categories, Filtering, Cloudinary integration)
├── orders/                # 🛒 Commerce (Cart, CartItems, Orders, OrderItems, Wishlists, Bulk Logic)
├── analytics/             # 📊 Data & Stats (Admin Dashboard API for Revenue & Orders)
├── core/                  # 🛠️ Shared Utilities (Base models, Global signals, Error handlers)
├── logs/                  # 📝 System Logging output directory
├── Dockerfile             # 🐳 Container Image Definition
├── requirements.txt       # 📦 Python Dependencies
└── manage.py              # 🚀 Django Management Script
```

---

## 🔗 Frontend / Backend Integration Protocol

This backend communicates natively with the Khoutwa React Frontend. Here is how they interact securely:

### 1. Authentication (JWT lifecycle)
- The frontend acts as the client and talks to the backend via `axios` interceptors.
- Upon Login, the backend issues an `access` token (1-hour life) and a `refresh` token (30-day life).
- If the frontend receives a `401 Unauthorized` response, it automatically calls `POST /api/auth/jwt/refresh/` on the backend using the local `refresh_token` to seamlessly renew the session without logging the user out.

### 2. CORS & Security Checkpoints
- We rely on `django-cors-headers` to manage frontend access. In production, only authorized URIs (e.g., `http://localhost:5173`, `production-domain.com`) are allowed via `CORS_ALLOWED_ORIGINS`.
- Form data mapping (e.g., uploading images from React) is handled natively by `MultiPartParser` and `FormParser` in the associated ViewSets.

### 3. API Pagination & Filtering
- Standardized RESTful JSON responses.
- Pagination is enforced globally (`PAGE_SIZE = 20`).
- Advanced querying works out-of-the-box (e.g., `GET /api/products/?category=sneakers&min_price=100&max_price=500`).

---

## 📦 Quick Start & Local Development

### 1. Standard Setup
```bash
# 1. Create and activate a Virtual Environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure Environments
cp .env.example .env
# Edit .env variables (Ensure DEBUG=True strictly for local dev)

# 4. Migrate database
python manage.py migrate

# 5. Create superuser & Run server
python manage.py createsuperuser
python manage.py runserver
```
*Access API at `http://localhost:8000/api` and Admin at `http://localhost:8000/admin`*

### 2. Docker Deployment
To spin up everything (Django + PostgreSQL) magically via Docker:
```bash
cd .. # Go to project root
docker-compose up --build -d

# Interacting with the container
docker-compose exec backend python manage.py migrate
docker-compose exec backend python manage.py createsuperuser
```

---

## 🔐 Deployment & Production Checklist

Before pushing this code to a production environment (VPS, Railway, Heroku), ensure the following:

- [ ] **`.env` Configuration:** Validate that `DEBUG` evaluates to `False`.
- [ ] **Secret Key:** `SECRET_KEY` must be strong, unique, and strictly kept out of version control.
- [ ] **Database Setup:** Connect to a hosted PostgreSQL instance via `DB_HOST`, `DB_USER`, `DB_PASSWORD`.
- [ ] **Static/Media Files:** Ensure `Whitenoise` is active or a storage bucket (AWS S3 / Cloudinary) is connected.
- [ ] **CORS Restrictions:** Disable `CORS_ALLOW_ALL_ORIGINS` and explicitly whitelist the production frontend domain.
- [ ] **HTTPS Enforced:** Toggle `SECURE_SSL_REDIRECT`, `SESSION_COOKIE_SECURE`, and `CSRF_COOKIE_SECURE` to `True`.

---

## 👨‍💻 Author & Credits

**Powered by Mohamed Mady**  
*Software Engineer | Python & Django Specialist*  

> *"Building robust architectures for seamless digital experiences."*
