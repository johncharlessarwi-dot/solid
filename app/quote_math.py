"""Bounded integer-unit quote calculations without floating point rounding."""
MAX_AMOUNT = 100_000_000


def calculate_quote_total(items, discount=0):
    if not isinstance(items, list) or not 1 <= len(items) <= 20:
        raise ValueError("Expected 1 to 20 items")
    if type(discount) is not int or not 0 <= discount <= MAX_AMOUNT:
        raise ValueError("Invalid discount")
    total = 0
    for item in items:
        if not isinstance(item, dict):
            raise ValueError("Invalid quote item")
        if "unit_price" not in item or "quantity" not in item:
            raise ValueError("Quote item is incomplete")
        amount = item.get("unit_price")
        quantity = item.get("quantity")
        if type(amount) is not int or type(quantity) is not int:
            raise ValueError("Quote values must be integers")
        if not 0 <= amount <= MAX_AMOUNT or not 1 <= quantity <= 100:
            raise ValueError("Invalid quantity or price")
        total += amount * quantity
        if total > MAX_AMOUNT:
            raise ValueError("Quote exceeds supported limit")
    if discount > total:
        raise ValueError("Discount exceeds total")
    return {"subtotal": total, "discount": discount, "total": total - discount}
