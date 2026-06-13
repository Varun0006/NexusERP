from app.extensions import db
from app.models.inventory import Inventory


class ReservationService:
    @staticmethod
    def reserve_for_order(order):
        from app.services.inventory.stock_service import StockService
        results = []
        for line in order.lines.all():
            success, data = StockService.reserve_stock(line.product_id, line.quantity)
            results.append({"product_id": line.product_id, "success": success, "message": str(data)})
        return results

    @staticmethod
    def release_for_order(order):
        from app.services.inventory.stock_service import StockService
        results = []
        for line in order.lines.all():
            success, data = StockService.unreserve_stock(line.product_id, line.quantity)
            results.append({"product_id": line.product_id, "success": success})
        return results
