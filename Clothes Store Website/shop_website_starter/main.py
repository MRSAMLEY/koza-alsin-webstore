from fastapi import FastAPI, Request, Form, Depends, HTTPException, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
from sqlmodel import SQLModel, Field, Session, create_engine, select, Relationship
from typing import Optional, List
from jinja2 import Environment, FileSystemLoader, select_autoescape
import os
from datetime import datetime

# ------------------------------------------------------
# Config
# ------------------------------------------------------
DATABASE_URL = "sqlite:///./shop.db"
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin")
SECRET_KEY = os.getenv("SECRET_KEY", "change-me-please")

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

# ------------------------------------------------------
# Models
# ------------------------------------------------------
class Product(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    description: str = ""
    price_cents: int = 0
    image_url: str = ""

class OrderItem(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    order_id: int = Field(foreign_key="order.id")
    product_id: int = Field(foreign_key="product.id")
    quantity: int = 1
    unit_price_cents: int = 0

class Order(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    total_cents: int = 0

# ------------------------------------------------------
# App + Templates
# ------------------------------------------------------
app = FastAPI(title="Shop Website Starter")
app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
templates_dir = os.path.join(BASE_DIR, "templates")
static_dir = os.path.join(BASE_DIR, "static")

os.makedirs(templates_dir, exist_ok=True)
os.makedirs(static_dir, exist_ok=True)

app.mount("/static", StaticFiles(directory=static_dir), name="static")

env = Environment(
    loader=FileSystemLoader(templates_dir),
    autoescape=select_autoescape(["html", "xml"]),
)

def render(template_name: str, **context) -> HTMLResponse:
    template = env.get_template(template_name)
    html = template.render(**context)
    return HTMLResponse(html)

# ------------------------------------------------------
# DB init
# ------------------------------------------------------
def init_db():
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        # Seed sample products if empty
        count = session.exec(select(Product)).all()
        if not count:
            samples = [
                Product(
                    name="Canvas Backpack",
                    description="Durable 20L backpack great for everyday carry.",
                    price_cents=4999,
                    image_url="https://images.unsplash.com/photo-1514477917009-389c76a86b68?q=80&w=1200",
                ),
                Product(
                    name="Stainless Water Bottle",
                    description="Insulated 750ml keeps drinks cold or hot for hours.",
                    price_cents=2499,
                    image_url="https://images.unsplash.com/photo-1558640469-76b1d33f11d6?q=80&w=1200",
                ),
                Product(
                    name="Wireless Earbuds",
                    description="Compact case, long battery life, crisp sound.",
                    price_cents=7999,
                    image_url="https://images.unsplash.com/photo-1585386959984-a41552231658?q=80&w=1200",
                ),
            ]
            for p in samples:
                session.add(p)
            session.commit()

@app.on_event("startup")
def on_startup():
    init_db()

# ------------------------------------------------------
# Utilities
# ------------------------------------------------------
def cents_to_price(cents: int) -> str:
    return f"€{cents/100:.2f}"

def get_cart(request: Request) -> dict:
    cart = request.session.get("cart", {})
    # cart = { product_id (str): quantity (int) }
    return cart

def save_cart(request: Request, cart: dict):
    request.session["cart"] = cart

def cart_items_with_totals(cart: dict):
    items = []
    subtotal = 0
    with Session(engine) as session:
        for pid_str, qty in cart.items():
            pid = int(pid_str)
            product = session.get(Product, pid)
            if not product:
                continue
            line_total = product.price_cents * qty
            subtotal += line_total
            items.append({
                "product": product,
                "qty": qty,
                "line_total": line_total,
            })
    return items, subtotal

def require_admin(password: str):
    if password != ADMIN_PASSWORD:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid admin password")

# ------------------------------------------------------
# Routes
# ------------------------------------------------------
@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    with Session(engine) as session:
        products = session.exec(select(Product)).all()
    cart = get_cart(request)
    cart_qty = sum(cart.values())
    return render("index.html",
                  products=products,
                  price=cents_to_price,
                  cart_qty=cart_qty)

@app.get("/product/{product_id}", response_class=HTMLResponse)
def product_detail(request: Request, product_id: int):
    with Session(engine) as session:
        product = session.get(Product, product_id)
        if not product:
            raise HTTPException(404, "Product not found")
    cart = get_cart(request)
    cart_qty = sum(cart.values())
    return render("product.html", product=product, price=cents_to_price, cart_qty=cart_qty)

@app.post("/cart/add/{product_id}", response_class=HTMLResponse)
def cart_add(request: Request, product_id: int, qty: int = Form(1)):
    cart = get_cart(request)
    key = str(product_id)
    cart[key] = cart.get(key, 0) + int(qty)
    save_cart(request, cart)
    # Return cart bubble for HTMX swap
    items, subtotal = cart_items_with_totals(cart)
    return render("_cart_bubble.html", cart_qty=sum(cart.values()))

@app.post("/cart/update/{product_id}", response_class=HTMLResponse)
def cart_update(request: Request, product_id: int, qty: int = Form(...)):
    cart = get_cart(request)
    key = str(product_id)
    if int(qty) <= 0:
        cart.pop(key, None)
    else:
        cart[key] = int(qty)
    save_cart(request, cart)
    items, subtotal = cart_items_with_totals(cart)
    return render("_cart_table.html", items=items, subtotal=subtotal, price=cents_to_price)

@app.get("/cart", response_class=HTMLResponse)
def view_cart(request: Request):
    cart = get_cart(request)
    items, subtotal = cart_items_with_totals(cart)
    return render("cart.html", items=items, subtotal=subtotal, price=cents_to_price)

@app.post("/checkout", response_class=HTMLResponse)
def checkout(request: Request):
    cart = get_cart(request)
    items, subtotal = cart_items_with_totals(cart)
    if not items:
        return RedirectResponse(url="/cart", status_code=303)
    with Session(engine) as session:
        order = Order(total_cents=subtotal)
        session.add(order)
        session.commit()
        session.refresh(order)
        for it in items:
            oi = OrderItem(
                order_id=order.id,
                product_id=it["product"].id,
                quantity=it["qty"],
                unit_price_cents=it["product"].price_cents
            )
            session.add(oi)
        session.commit()
    # Clear cart
    save_cart(request, {})
    return render("thanks.html", order_id=order.id, total=subtotal, price=cents_to_price)

# ---------------- Admin ----------------
@app.get("/admin", response_class=HTMLResponse)
def admin(request: Request):
    return render("admin.html")

@app.post("/admin/login", response_class=HTMLResponse)
def admin_login(password: str = Form(...)):
    require_admin(password)
    return RedirectResponse(url="/admin/products", status_code=303)

@app.get("/admin/products", response_class=HTMLResponse)
def admin_products(request: Request, password: Optional[str] = None):
    # Allow password via query for demo simplicity
    pw = password or request.query_params.get("password") or "admin"  # fallback for quick demo
    require_admin(pw)
    with Session(engine) as session:
        products = session.exec(select(Product)).all()
    return render("admin_products.html", products=products, price=cents_to_price)

@app.post("/admin/products", response_class=HTMLResponse)
def admin_add_product(
    request: Request,
    name: str = Form(...),
    description: str = Form(""),
    price_eur: float = Form(...),
    image_url: str = Form(""),
    password: str = Form(...),
):
    require_admin(password)
    price_cents = int(round(price_eur * 100))
    with Session(engine) as session:
        p = Product(name=name, description=description, price_cents=price_cents, image_url=image_url)
        session.add(p)
        session.commit()
    return RedirectResponse(url="/admin/products?password="+password, status_code=303)
