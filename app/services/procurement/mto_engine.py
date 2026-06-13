from app.extensions import db
from app.models.sales_order_line import SalesOrderLine
from app.models.procurement_request import ProcurementRequest
from datetime import datetime


class MtoEngine:
    def evaluate(self):
        requests = []
        unfulfilled_lines = (
            SalesOrderLine.query.join(SalesOrderLine.order)
            .filter(
                SalesOrderLine.delivered_qty < SalesOrderLine.quantity,
                SalesOrder.status == "confirmed",
            )
            .all()
        )
        for line in unfulfilled_lines:
            remaining = line.quantity - line.delivered_qty
            requests.append(
                {
                    "product": line.product,
                    "quantity": remaining,
                    "sales_order_id": line.sales_order_id,
                }
            )
        return requests
