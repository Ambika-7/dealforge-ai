from typing import Dict, Any

def calculate_vendor_price(quote: Dict[str, Any]) -> Dict[str, Any]:
    unit_price = quote.get("unit_price", 0.0)
    quantity = quote.get("quantity", 0)
    discount_percentage = quote.get("discount_percentage", 0.0)
    
    base_cost = unit_price * quantity
    discount_amount = base_cost * (discount_percentage / 100.0)
    
    # Assume a standard 10% tax
    taxes = (base_cost - discount_amount) * 0.10
    shipping_cost = 0.0 # Assuming free shipping
    
    total_cost = base_cost - discount_amount + taxes + shipping_cost
    
    # Calculate a score for payment terms (e.g. 30 days > 15 days)
    payment_days = quote.get("payment_terms_days", 0)
    payment_terms_score = min(10, payment_days // 5)
    
    return {
        "vendor_id": quote["vendor_id"],
        "base_cost": base_cost,
        "discount_amount": discount_amount,
        "taxes": taxes,
        "shipping_cost": shipping_cost,
        "total_cost": total_cost,
        "unit_cost_after_discount": total_cost / quantity if quantity > 0 else 0.0,
        "payment_terms_score": payment_terms_score
    }
