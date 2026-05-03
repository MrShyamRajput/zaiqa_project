# 🍽️ Zaiqa Restaurant – Django Version

A QR-based restaurant ordering system built with Django.

## 📁 Project Structure
```
zaiqa_django/
├── manage.py
├── requirements.txt
├── db.sqlite3              ← auto-created on first run
├── media/                  ← uploaded images & QR codes
├── zaiqa_django/           ← Django project settings
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
└── restaurant/             ← Main app
    ├── models.py           ← MenuItem, Order models
    ├── views.py            ← All API + page views
    ├── urls.py             ← URL routing
    ├── admin.py            ← Django admin registration
    ├── migrations/
    └── templates/restaurant/
        ├── menu.html       ← Customer-facing menu page
        └── admin.html      ← Admin panel
```

## 🚀 Setup & Run

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Run migrations (creates SQLite DB)
```bash
python manage.py migrate
```

### 3. (Optional) Create Django superuser for /admin/
```bash
python manage.py createsuperuser
```

### 4. Start the server
```bash
python manage.py runserver
```

## 🌐 URLs

| URL | Description |
|-----|-------------|
| `http://127.0.0.1:8000/` | Customer menu page |
| `http://127.0.0.1:8000/menu/` | Customer menu page |
| `http://127.0.0.1:8000/admin-panel/` | Restaurant admin panel |
| `http://127.0.0.1:8000/admin/` | Django built-in admin |

## 📡 API Endpoints

| Method | URL | Description |
|--------|-----|-------------|
| GET | `/api/menu/` | Get all menu items |
| POST | `/api/menu/` | Add menu item (multipart/form-data) |
| DELETE | `/api/menu/<id>/` | Delete menu item |
| GET | `/api/orders/` | Get all orders |
| POST | `/api/order/` | Place an order (requires JWT token) |
| PATCH | `/api/orders/<id>/status/` | Update order status |
| GET | `/api/generate-qr/?table=1` | Generate QR code for a table |
| GET | `/api/decode/?token=<jwt>` | Decode JWT table token |

## 📱 How QR Ordering Works

1. Go to **Admin Panel** → click **QR Codes** tab
2. Enter table number → click **Generate QR**
3. Download and print the QR code for that table
4. Customer scans QR → lands on `/menu/?token=<jwt>`
5. Customer browses menu, adds to cart, places order
6. Admin sees live orders in the **Orders** tab (auto-refreshes every 5s)
7. Admin clicks **Mark Done** when order is delivered

## ⚙️ Settings

- **JWT Secret**: Change `JWT_SECRET` in `zaiqa_django/settings.py` for production
- **Database**: SQLite by default. Change `DATABASES` in settings for PostgreSQL/MySQL
- **Media files**: Uploaded images saved in `/media/` folder
- **Debug**: Set `DEBUG = False` in production
