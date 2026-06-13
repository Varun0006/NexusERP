PRODUCT_TYPES = [
    ("finished_goods", "Finished Goods"),
    ("raw_material", "Raw Material"),
    ("semi_finished", "Semi-Finished"),
    ("service", "Service"),
]

ORDER_STATUSES = ["draft", "confirmed", "in_progress", "delivered", "received", "closed", "cancelled"]

MOVEMENT_TYPES = [
    "purchase_receipt",
    "sales_delivery",
    "production_output",
    "production_consumption",
    "stock_adjustment",
    "transfer_out",
    "transfer_in",
    "initial_stock",
]

PAYMENT_METHODS = ["cash", "card", "upi", "credit", "bank_transfer"]
