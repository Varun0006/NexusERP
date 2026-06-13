from flask import Blueprint, render_template
from flask_login import login_required
from app.models.product import Product
from app.models.sales_order import SalesOrder
from app.models.purchase_order import PurchaseOrder
from app.models.inventory import Inventory
from app.models.manufacturing_order import ManufacturingOrder
from app.extensions import db
from sqlalchemy import func

dashboard_bp = Blueprint("dashboard", __name__, template_folder="../templates/dashboard")


@dashboard_bp.route("/")
@login_required
def index():
    total_products = Product.query.count()
    total_sales = SalesOrder.query.count()
    total_purchases = PurchaseOrder.query.count()
    low_stock_items = Inventory.query.filter(
        Inventory.on_hand_qty <= Inventory.reserved_qty + 10
    ).count()
    pending_mos = ManufacturingOrder.query.filter(
        ManufacturingOrder.status.in_(["draft", "confirmed", "in_progress"])
    ).count()
    recent_sales = (
        SalesOrder.query.order_by(SalesOrder.created_at.desc()).limit(5).all()
    )
    recent_purchases = (
        PurchaseOrder.query.order_by(PurchaseOrder.created_at.desc()).limit(5).all()
    )
    return render_template(
        "dashboard.html",
        total_products=total_products,
        total_sales=total_sales,
        total_purchases=total_purchases,
        low_stock_items=low_stock_items,
        pending_mos=pending_mos,
        recent_sales=recent_sales,
        recent_purchases=recent_purchases,
    )
