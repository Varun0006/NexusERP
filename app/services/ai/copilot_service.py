import os
import re
from datetime import datetime

from sqlalchemy import func

from app.extensions import db
from app.models.bom import Bom
from app.models.inventory import Inventory
from app.models.manufacturing_order import ManufacturingOrder
from app.models.product import Product
from app.models.purchase_order import PurchaseOrder
from app.models.sales_order import SalesOrder
from app.models.sales_order_line import SalesOrderLine


class CopilotService:
    def _extract_intent(self, message):
        normalized = (message or "").strip().lower()

        if any(token in normalized for token in ["running low", "low stock", "reorder", "stock alert"]):
            return "low_stock"
        if any(token in normalized for token in ["manufacture today", "produce today", "what should i manufacture", "production priority"]):
            return "manufacture_today"
        if any(token in normalized for token in ["inventory shortage", "shortage", "stockout"]):
            return "inventory_shortages"
        if any(token in normalized for token in ["delayed", "delay", "late order", "why is this order delayed"]):
            return "delayed_order"
        return "general"

    def _extract_order_number(self, message):
        match = re.search(r"\bSO-[A-Z0-9-]+\b", (message or "").upper())
        return match.group(0) if match else None

    def get_snapshot(self):
        now = datetime.utcnow()

        low_stock_items = (
            db.session.query(Product, Inventory)
            .join(Inventory, Inventory.product_id == Product.id)
            .filter(Product.is_active.is_(True))
            .filter(Inventory.on_hand_qty <= func.coalesce(Product.safety_stock, 0))
            .order_by((func.coalesce(Product.safety_stock, 0) - Inventory.on_hand_qty).desc())
            .limit(8)
            .all()
        )

        open_sales = SalesOrder.query.filter(SalesOrder.status.in_(["draft", "confirmed"])).count()
        delayed_sales = (
            SalesOrder.query.filter(SalesOrder.status.in_(["draft", "confirmed"]))
            .filter(SalesOrder.expected_date.isnot(None))
            .filter(SalesOrder.expected_date < now)
            .count()
        )
        active_mos = ManufacturingOrder.query.filter(
            ManufacturingOrder.status.in_(["draft", "in_progress"])
        ).count()
        open_pos = PurchaseOrder.query.filter(
            PurchaseOrder.status.in_(["draft", "confirmed", "partially_received"])
        ).count()

        return {
            "open_sales_orders": open_sales,
            "delayed_sales_orders": delayed_sales,
            "active_manufacturing_orders": active_mos,
            "open_purchase_orders": open_pos,
            "low_stock_items_count": len(low_stock_items),
            "low_stock_items": [
                {
                    "product": product.name,
                    "sku": product.sku,
                    "on_hand": float(inventory.on_hand_qty or 0),
                    "safety_stock": float(product.safety_stock or 0),
                    "gap": float((product.safety_stock or 0) - (inventory.on_hand_qty or 0)),
                }
                for product, inventory in low_stock_items
            ],
        }

    def _format_low_stock(self):
        snapshot = self.get_snapshot()
        items = snapshot["low_stock_items"]
        if not items:
            return "No products are currently below safety stock."

        lines = ["Low stock products (top priority):"]
        for item in items:
            lines.append(
                f"- {item['product']} ({item['sku']}): on hand {item['on_hand']:.0f}, "
                f"safety stock {item['safety_stock']:.0f}, gap {item['gap']:.0f}"
            )
        return "\n".join(lines)

    def _manufacturing_priorities(self):
        # Aggregate shortage-driven demand from open sales orders.
        rows = (
            db.session.query(
                Product.id.label("product_id"),
                Product.name.label("product_name"),
                Product.sku.label("sku"),
                func.sum(SalesOrderLine.quantity - func.coalesce(SalesOrderLine.delivered_qty, 0)).label("demand_qty"),
                func.min(SalesOrder.expected_date).label("earliest_due"),
            )
            .join(SalesOrderLine, SalesOrderLine.product_id == Product.id)
            .join(SalesOrder, SalesOrder.id == SalesOrderLine.sales_order_id)
            .filter(SalesOrder.status.in_(["draft", "confirmed"]))
            .group_by(Product.id, Product.name, Product.sku)
            .all()
        )

        priorities = []
        for row in rows:
            inv = Inventory.query.filter_by(product_id=row.product_id).first()
            free_qty = inv.free_to_use_qty if inv else 0
            shortage_qty = max((row.demand_qty or 0) - free_qty, 0)
            if shortage_qty <= 0:
                continue

            wip_qty = (
                db.session.query(
                    func.sum(ManufacturingOrder.quantity - func.coalesce(ManufacturingOrder.produced_qty, 0))
                )
                .filter(ManufacturingOrder.product_id == row.product_id)
                .filter(ManufacturingOrder.status.in_(["draft", "in_progress"]))
                .scalar()
                or 0
            )

            priorities.append(
                {
                    "product": row.product_name,
                    "sku": row.sku,
                    "shortage": float(shortage_qty),
                    "due": row.earliest_due,
                    "in_progress": float(max(wip_qty, 0)),
                }
            )

        priorities.sort(key=lambda item: ((item["due"] is None), item["due"], -item["shortage"]))
        return priorities[:5]

    def _format_manufacture_today(self):
        priorities = self._manufacturing_priorities()
        if not priorities:
            return "No immediate manufacturing shortages were detected from current open sales orders."

        lines = ["Recommended manufacturing priority for today:"]
        for idx, item in enumerate(priorities, start=1):
            due_label = item["due"].strftime("%Y-%m-%d") if item["due"] else "No due date"
            lines.append(
                f"{idx}. {item['product']} ({item['sku']}): shortage {item['shortage']:.0f}, "
                f"WIP {item['in_progress']:.0f}, earliest due {due_label}"
            )
        return "\n".join(lines)

    def _delay_reasons_for_order(self, order):
        reasons = []
        for line in order.lines:
            pending_qty = max((line.quantity or 0) - (line.delivered_qty or 0), 0)
            if pending_qty <= 0:
                continue

            product = line.product
            inv = Inventory.query.filter_by(product_id=product.id).first()
            free_qty = inv.free_to_use_qty if inv else 0

            if free_qty < pending_qty:
                reasons.append(
                    f"Stock shortage for {product.name}: pending {pending_qty:.0f}, available {free_qty:.0f}."
                )

            if product.procurement_type == "mto":
                bom = Bom.query.filter_by(product_id=product.id, is_active=True).first()
                if not bom:
                    reasons.append(f"No active BOM is configured for {product.name}.")

                wip_qty = (
                    db.session.query(
                        func.sum(ManufacturingOrder.quantity - func.coalesce(ManufacturingOrder.produced_qty, 0))
                    )
                    .filter(ManufacturingOrder.product_id == product.id)
                    .filter(ManufacturingOrder.status.in_(["draft", "in_progress"]))
                    .scalar()
                    or 0
                )
                if wip_qty < pending_qty:
                    reasons.append(
                        f"Manufacturing capacity gap for {product.name}: pending {pending_qty:.0f}, WIP {wip_qty:.0f}."
                    )

        if not reasons:
            reasons.append("No material shortage detected; review dispatch or operational processing delays.")

        return reasons

    def _format_delayed_orders(self, message):
        now = datetime.utcnow()
        order_number = self._extract_order_number(message)
        if order_number:
            order = SalesOrder.query.filter_by(order_number=order_number).first()
            if not order:
                return f"Order {order_number} was not found."
            reasons = self._delay_reasons_for_order(order)
            lines = [f"Delay analysis for {order.order_number}:"]
            lines.extend(f"- {reason}" for reason in reasons)
            return "\n".join(lines)

        delayed_orders = (
            SalesOrder.query.filter(SalesOrder.status.in_(["draft", "confirmed"]))
            .filter(SalesOrder.expected_date.isnot(None))
            .filter(SalesOrder.expected_date < now)
            .order_by(SalesOrder.expected_date.asc())
            .limit(3)
            .all()
        )

        if not delayed_orders:
            return "There are currently no delayed sales orders."

        lines = ["Top delayed sales orders and likely blockers:"]
        for order in delayed_orders:
            reasons = self._delay_reasons_for_order(order)
            lines.append(f"- {order.order_number}: {reasons[0]}")
        lines.append("Provide an order number (example: SO-00012) for a detailed delay diagnosis.")
        return "\n".join(lines)

    def _format_inventory_shortages(self):
        shortages = self._manufacturing_priorities()
        if not shortages:
            return "No sales-driven inventory shortages were detected."

        lines = ["Inventory shortages impacting order fulfillment:"]
        for item in shortages:
            lines.append(
                f"- {item['product']} ({item['sku']}): shortage {item['shortage']:.0f}, "
                f"current WIP {item['in_progress']:.0f}"
            )
        return "\n".join(lines)

    def _build_llm_context(self):
        snapshot = self.get_snapshot()
        context = [
            "You are NexusERP AI Operations Copilot.",
            "Answer with concise, practical, execution-ready business advice.",
            f"Open Sales Orders: {snapshot['open_sales_orders']}",
            f"Delayed Sales Orders: {snapshot['delayed_sales_orders']}",
            f"Active Manufacturing Orders: {snapshot['active_manufacturing_orders']}",
            f"Open Purchase Orders: {snapshot['open_purchase_orders']}",
            f"Low Stock Items: {snapshot['low_stock_items_count']}",
        ]
        return "\n".join(context)

    def _ask_gemini(self, user_message):
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            return None

        try:
            from google import genai

            client = genai.Client(api_key=api_key)
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=f"{self._build_llm_context()}\n\nUser question: {user_message}",
            )
            return response.text
        except Exception:
            return None

    def respond(self, user_message):
        intent = self._extract_intent(user_message)

        if intent == "low_stock":
            return {"intent": intent, "response": self._format_low_stock(), "source": "erp"}
        if intent == "manufacture_today":
            return {"intent": intent, "response": self._format_manufacture_today(), "source": "erp"}
        if intent == "inventory_shortages":
            return {"intent": intent, "response": self._format_inventory_shortages(), "source": "erp"}
        if intent == "delayed_order":
            return {"intent": intent, "response": self._format_delayed_orders(user_message), "source": "erp"}

        llm_response = self._ask_gemini(user_message)
        if llm_response:
            return {"intent": intent, "response": llm_response, "source": "gemini"}

        summary = (
            "I can answer live ERP questions on low stock, manufacturing priorities, delayed orders, "
            "and inventory shortages. Try one of the suggested prompts above."
        )
        return {"intent": intent, "response": summary, "source": "erp"}