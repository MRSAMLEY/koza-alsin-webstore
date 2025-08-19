# Shop Website Starter (FastAPI + HTMX + Tailwind CDN)

A minimal full‑stack shop: FastAPI backend with SQLite + server‑rendered HTML using Jinja2 and HTMX.
Includes products, cart, checkout, and a lightweight admin panel.

## Features
- Product listing & detail pages
- Add to cart (HTMX partial updates, no heavy JS build step)
- Session‑based cart
- Checkout creates Orders + OrderItems
- Admin page to add products (password protected)
- SQLite database auto-creates on first run

## Quick Start

```bash
# 1) Create & activate a virtual environment (recommended)
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
# source .venv/bin/activate

# 2) Install dependencies
pip install -r requirements.txt

# 3) (Optional) Set admin password
# If not set, default is "admin"
# Windows PowerShell:
$env:ADMIN_PASSWORD="your-strong-password"
# macOS/Linux:
# export ADMIN_PASSWORD="your-strong-password"

# 4) Run the app
uvicorn main:app --reload

# 5) Open your browser
# http://127.0.0.1:8000
```

## Admin
- Visit **/admin** to add products.
- Default password: `admin` (change via `ADMIN_PASSWORD` env var).

## Notes
- Images are URLs stored per product. You can use any public image URL (e.g., product photos hosted elsewhere).
- Tailwind is loaded via CDN for simplicity. For production, consider bundling assets.
- This starter aims to be readable and hackable rather than feature‑complete.
