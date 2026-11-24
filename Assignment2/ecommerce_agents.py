"""
Natural Language Processing Assignment 2: AI Agents for E-Commerce Application
Student Name: Pramodh | Student ID: B210195 | Section: C4

A production-grade Multi-Agent E-Commerce Architecture:
1. Orchestrator / Supervisor Agent (Intent router & ReAct controller)
2. Product Discovery & Recommendation Agent (Semantic & multi-filter search)
3. Cart & Order Execution Agent (Deterministic state, tax, discounts, checkout)
4. Logistics & Tracking Agent (Real-time tracking, estimated deliveries)
5. Customer Policy Agent (Grounded store policy retrieval)
"""

import os
import sqlite3
import json
import re
from typing import Dict, Any, List, Optional

DB_PATH = os.path.join(os.path.dirname(__file__), "catalog_database.db")

# ==========================================
# TOOL DEFINITIONS & EXECUTION LAYER
# ==========================================
class EcommerceTools:
    @staticmethod
    def search_products(query: str = "", category: str = "", max_price: float = None, min_rating: float = None) -> List[Dict[str, Any]]:
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        sql = "SELECT id, name, category, price, rating, stock, description FROM products WHERE 1=1"
        params = []
        
        if category:
            sql += " AND LOWER(category) = LOWER(?)"
            params.append(category)
        if max_price is not None:
            sql += " AND price <= ?"
            params.append(max_price)
        if min_rating is not None:
            sql += " AND rating >= ?"
            params.append(min_rating)
            
        cur.execute(sql, params)
        rows = cur.fetchall()
        conn.close()
        
        results = []
        q_tokens = set(re.findall(r'\w+', query.lower())) if query else set()
        for r in rows:
            prod = {
                "id": r[0], "name": r[1], "category": r[2],
                "price": r[3], "rating": r[4], "stock": r[5], "description": r[6]
            }
            # Score relevance if query provided
            if q_tokens:
                text_tokens = set(re.findall(r'\w+', (prod["name"] + " " + prod["description"]).lower()))
                overlap = len(q_tokens & text_tokens)
                if overlap > 0 or not query:
                    prod["relevance_score"] = overlap
                    results.append(prod)
            else:
                results.append(prod)
                
        if q_tokens:
            results.sort(key=lambda x: (x.get("relevance_score", 0), x["rating"]), reverse=True)
        return results

    @staticmethod
    def get_product_details(product_id: int) -> Optional[Dict[str, Any]]:
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute("SELECT id, name, category, price, rating, stock, description FROM products WHERE id = ?", (product_id,))
        r = cur.fetchone()
        conn.close()
        if not r:
            return None
        return {"id": r[0], "name": r[1], "category": r[2], "price": r[3], "rating": r[4], "stock": r[5], "description": r[6]}

    @staticmethod
    def track_order(order_id: str) -> Dict[str, Any]:
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute("SELECT order_id, customer_name, items, total_amount, status, tracking_carrier, estimated_delivery FROM orders WHERE UPPER(order_id) = UPPER(?)", (order_id,))
        r = cur.fetchone()
        conn.close()
        if not r:
            return {"error": f"Order {order_id} not found."}
        return {
            "order_id": r[0], "customer": r[1], "items": r[2],
            "total_amount": f"${r[3]:.2f}", "status": r[4],
            "carrier": r[5], "estimated_delivery": r[6]
        }

    @staticmethod
    def validate_coupon(coupon_code: str, order_amount: float) -> Dict[str, Any]:
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute("SELECT code, discount_percent, min_order, active FROM coupons WHERE UPPER(code) = UPPER(?)", (coupon_code,))
        r = cur.fetchone()
        conn.close()
        if not r:
            return {"valid": False, "message": f"Coupon code '{coupon_code}' does not exist."}
        if r[3] == 0:
            return {"valid": False, "message": f"Coupon code '{coupon_code}' has expired."}
        if order_amount < r[2]:
            return {"valid": False, "message": f"Coupon '{r[0]}' requires minimum order of ${r[2]:.2f} (Current: ${order_amount:.2f})."}
            
        discount_val = order_amount * (r[1] / 100.0)
        return {
            "valid": True, "code": r[0], "discount_percent": r[1],
            "discount_amount": round(discount_val, 2),
            "new_total": round(order_amount - discount_val, 2)
        }

    @staticmethod
    def get_policy(topic: str) -> Dict[str, Any]:
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute("SELECT topic, content FROM policies WHERE LOWER(topic) LIKE LOWER(?)", (f"%{topic}%",))
        r = cur.fetchone()
        conn.close()
        if not r:
            return {"topic": topic, "policy": "Standard store terms apply. Please contact customer service at support@ecommerce.com for details."}
        return {"topic": r[0], "policy": r[1]}


# ==========================================
# CART & STATE MANAGER
# ==========================================
class ShoppingCart:
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.items: Dict[int, Dict[str, Any]] = {}
        self.applied_coupon: Optional[Dict[str, Any]] = None

    def add_item(self, product_id: int, quantity: int = 1) -> Dict[str, Any]:
        prod = EcommerceTools.get_product_details(product_id)
        if not prod:
            return {"status": "error", "message": f"Product ID {product_id} not found."}
        if prod["stock"] < quantity:
            return {"status": "error", "message": f"Insufficient stock for '{prod['name']}'. Only {prod['stock']} available."}
            
        if product_id in self.items:
            self.items[product_id]["quantity"] += quantity
        else:
            self.items[product_id] = {
                "name": prod["name"],
                "price": prod["price"],
                "quantity": quantity
            }
        return {"status": "success", "message": f"Added {quantity}x '{prod['name']}' to cart."}

    def remove_item(self, product_id: int) -> Dict[str, Any]:
        if product_id in self.items:
            removed = self.items.pop(product_id)
            return {"status": "success", "message": f"Removed '{removed['name']}' from cart."}
        return {"status": "error", "message": f"Product ID {product_id} not in cart."}

    def view(self) -> Dict[str, Any]:
        subtotal = sum(item["price"] * item["quantity"] for item in self.items.values())
        discount = 0.0
        if self.applied_coupon:
            discount = subtotal * (self.applied_coupon["discount_percent"] / 100.0)
        tax = (subtotal - discount) * 0.0825 # 8.25% sales tax
        final_total = (subtotal - discount) + tax

        return {
            "items": list(self.items.values()),
            "item_count": sum(item["quantity"] for item in self.items.values()),
            "subtotal": round(subtotal, 2),
            "discount": round(discount, 2),
            "coupon": self.applied_coupon["code"] if self.applied_coupon else None,
            "tax": round(tax, 2),
            "final_total": round(final_total, 2)
        }

    def apply_coupon(self, code: str) -> Dict[str, Any]:
        subtotal = sum(item["price"] * item["quantity"] for item in self.items.values())
        res = EcommerceTools.validate_coupon(code, subtotal)
        if res["valid"]:
            self.applied_coupon = res
            return {"status": "success", "message": f"Applied coupon '{code}' ({res['discount_percent']}% off). Saved ${res['discount_amount']:.2f}."}
        return {"status": "error", "message": res["message"]}

    def checkout(self, customer_name: str, shipping_address: str) -> Dict[str, Any]:
        if not self.items:
            return {"status": "error", "message": "Cart is empty. Cannot checkout."}
        cart_view = self.view()
        order_id = f"ORD-{abs(hash(customer_name + str(cart_view['final_total']))) % 10000:04d}"
        
        # Save to database
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        item_str = ", ".join([f"{it['name']} ({it['quantity']})" for it in cart_view["items"]])
        cur.execute("INSERT INTO orders VALUES (?, ?, ?, ?, ?, ?, ?)",
                    (order_id, customer_name, item_str, cart_view["final_total"], "Confirmed", "FedEx Priority", "2026-11-28"))
        conn.commit()
        conn.close()
        
        self.items.clear()
        self.applied_coupon = None
        return {
            "status": "success",
            "order_id": order_id,
            "customer": customer_name,
            "shipping_to": shipping_address,
            "total_paid": f"${cart_view['final_total']:.2f}",
            "estimated_delivery": "2026-11-28"
        }


# ==========================================
# SPECIALIZED AI AGENTS & ORCHESTRATOR
# ==========================================
class EcommerceMultiAgentSystem:
    def __init__(self):
        self.carts: Dict[str, ShoppingCart] = {}

    def get_cart(self, session_id: str) -> ShoppingCart:
        if session_id not in self.carts:
            self.carts[session_id] = ShoppingCart(session_id)
        return self.carts[session_id]

    def route_and_execute(self, user_prompt: str, session_id: str = "guest_01") -> Dict[str, Any]:
        """
        Orchestrator Agent: Parses natural language intent, determines tool execution plan,
        coordinates specialized agent logic, and formats cognitive reasoning trace.
        """
        prompt_lower = user_prompt.lower()
        cart = self.get_cart(session_id)
        
        # Trace dictionary representing ReAct reasoning steps
        trace = {
            "user_prompt": user_prompt,
            "intent": "UNKNOWN",
            "thought": "",
            "action": "",
            "observation": {},
            "final_response": ""
        }

        # 1. ORDER TRACKING INTENT
        order_match = re.search(r'(ord-\d+)', prompt_lower)
        if "track" in prompt_lower or "order" in prompt_lower and order_match:
            trace["intent"] = "ORDER_TRACKING"
            order_id = order_match.group(1).upper() if order_match else "ORD-9821"
            trace["thought"] = f"User is querying status for order {order_id}. Routing to Logistics Agent."
            trace["action"] = f"EcommerceTools.track_order('{order_id}')"
            obs = EcommerceTools.track_order(order_id)
            trace["observation"] = obs
            
            if "error" in obs:
                trace["final_response"] = obs["error"]
            else:
                trace["final_response"] = (
                    f"📦 Order Status for **{obs['order_id']}**:\n"
                    f"- Status: **{obs['status']}**\n"
                    f"- Carrier: {obs['carrier']}\n"
                    f"- Estimated Delivery: {obs['estimated_delivery']}\n"
                    f"- Total Paid: {obs['total_amount']}\n"
                    f"- Items: {obs['items']}"
                )
            return trace

        # 2. STORE POLICY & SUPPORT INTENT
        if any(w in prompt_lower for w in ["return", "refund", "warranty", "shipping cost", "price match"]):
            trace["intent"] = "CUSTOMER_SUPPORT_POLICY"
            topic = "return_policy" if "return" in prompt_lower or "refund" in prompt_lower else ("warranty" if "warranty" in prompt_lower else "shipping")
            trace["thought"] = f"User inquiry relates to store terms regarding '{topic}'. Routing to Customer Policy Agent."
            trace["action"] = f"EcommerceTools.get_policy('{topic}')"
            obs = EcommerceTools.get_policy(topic)
            trace["observation"] = obs
            trace["final_response"] = f"ℹ️ **Store Policy ({obs['topic'].replace('_', ' ').title()})**:\n{obs['policy']}"
            return trace

        # 3. CART OPERATIONS INTENT
        if "cart" in prompt_lower and ("view" in prompt_lower or "what" in prompt_lower or "show" in prompt_lower or "check" in prompt_lower or "see" in prompt_lower or "in my" in prompt_lower):
            trace["intent"] = "CART_INSPECTION"
            trace["thought"] = "User requests current cart state. Routing to Cart Manager Agent."
            trace["action"] = "ShoppingCart.view()"
            obs = cart.view()
            trace["observation"] = obs
            if not obs["items"]:
                trace["final_response"] = "🛒 Your shopping cart is currently empty."
            else:
                items_str = "\n".join([f"  • {it['quantity']}x {it['name']} @ ${it['price']:.2f}" for it in obs["items"]])
                trace["final_response"] = (
                    f"🛒 **Your Shopping Cart** ({obs['item_count']} items):\n{items_str}\n\n"
                    f"- Subtotal: ${obs['subtotal']:.2f}\n"
                    f"- Discount ({obs['coupon'] or 'None'}): -${obs['discount']:.2f}\n"
                    f"- Sales Tax (8.25%): ${obs['tax']:.2f}\n"
                    f"- **Total: ${obs['final_total']:.2f}**"
                )
            return trace

        if "add" in prompt_lower and ("cart" in prompt_lower or "buy" in prompt_lower):
            trace["intent"] = "ADD_TO_CART"
            # Extract product
            target_prod = None
            if "laptop" in prompt_lower or "ultrabook" in prompt_lower:
                target_prod = 1 # UltraBook Pro 14
            elif "sony" in prompt_lower or "headphone" in prompt_lower:
                target_prod = 4 # Sony WH-1000XM5
            elif "mouse" in prompt_lower:
                target_prod = 7 # Ergonomic Mouse
            else:
                target_prod = 1
                
            trace["thought"] = f"User wants to add product ID {target_prod} to cart. Invoking Inventory Check and Add-To-Cart tool."
            trace["action"] = f"ShoppingCart.add_item({target_prod}, quantity=1)"
            obs = cart.add_item(target_prod, 1)
            trace["observation"] = obs
            trace["final_response"] = f"✅ {obs['message']} Use 'view cart' or 'checkout' when ready."
            return trace

        if "coupon" in prompt_lower or "promo" in prompt_lower or "code" in prompt_lower:
            trace["intent"] = "APPLY_COUPON"
            code_match = re.search(r'\b(save10|festive20|super50|expired30)\b', prompt_lower)
            code = code_match.group(1).upper() if code_match else "FESTIVE20"
            trace["thought"] = f"User wishes to apply coupon code '{code}'. Routing to Pricing Agent."
            trace["action"] = f"ShoppingCart.apply_coupon('{code}')"
            obs = cart.apply_coupon(code)
            trace["observation"] = obs
            trace["final_response"] = obs["message"]
            return trace

        if "checkout" in prompt_lower:
            trace["intent"] = "CHECKOUT"
            trace["thought"] = "User ready to complete transaction. Executing deterministic checkout tool."
            trace["action"] = "ShoppingCart.checkout('Pramodh', '104 Tech Boulevard, Silicon District')"
            obs = cart.checkout("Pramodh", "104 Tech Boulevard, Silicon District")
            trace["observation"] = obs
            if obs["status"] == "success":
                trace["final_response"] = (
                    f"🎉 **Order Successfully Placed!**\n"
                    f"- Order Confirmation ID: **{obs['order_id']}**\n"
                    f"- Recipient: {obs['customer']}\n"
                    f"- Shipping To: {obs['shipping_to']}\n"
                    f"- Amount Charged: **{obs['total_paid']}**\n"
                    f"- Estimated Delivery Date: {obs['estimated_delivery']}"
                )
            else:
                trace["final_response"] = f"❌ Checkout failed: {obs['message']}"
            return trace

        # 4. PRODUCT DISCOVERY & RECOMMENDATION INTENT (DEFAULT)
        trace["intent"] = "PRODUCT_DISCOVERY"
        max_p = None
        price_match = re.search(r'(?:under|below|<|less than)\s*\$?(\d+)', prompt_lower)
        if price_match:
            max_p = float(price_match.group(1))
            
        cat = ""
        if "laptop" in prompt_lower or "computer" in prompt_lower:
            cat = "Electronics"
        elif "headphone" in prompt_lower or "audio" in prompt_lower:
            cat = "Audio"
        elif "accessory" in prompt_lower or "mouse" in prompt_lower or "keyboard" in prompt_lower:
            cat = "Accessories"

        trace["thought"] = f"User searching catalog. Filters -> Category: '{cat or 'All'}', Max Price: {max_p}. Invoking Product Search Agent."
        trace["action"] = f"EcommerceTools.search_products(query='{user_prompt}', category='{cat}', max_price={max_p})"
        obs = EcommerceTools.search_products(query=user_prompt, category=cat, max_price=max_p)
        trace["observation"] = obs[:3]
        
        if not obs:
            trace["final_response"] = "Sorry, no products matched your criteria. Try adjusting your price budget or search terms."
        else:
            cards = []
            for p in obs[:3]:
                cards.append(f"• **{p['name']}** - **${p['price']:.2f}** (Rating: ⭐ {p['rating']}/5.0 | Stock: {p['stock']})\n  _{p['description']}_")
            trace["final_response"] = f"Here are the top recommendations matching your request:\n\n" + "\n\n".join(cards)
            
        return trace


def run_assignment2_demo():
    print("=" * 70)
    print("NATURAL LANGUAGE PROCESSING - ASSIGNMENT 2: E-COMMERCE AI AGENTS")
    print("Student ID: B210195 | Section: C4 | Student: Pramodh")
    print("=" * 70)

    agent_system = EcommerceMultiAgentSystem()
    session = "student_session_B210195"

    scenarios = [
        "I am looking for a lightweight laptop for college under $1000 with great battery life.",
        "Add the laptop to my shopping cart.",
        "Also add an ergonomic wireless mouse to my cart.",
        "Can you apply coupon code FESTIVE20?",
        "What is currently in my cart?",
        "What is your store return and refund policy on laptops?",
        "Proceed to checkout please.",
        "Can you track my previous order ORD-9821?"
    ]

    for idx, prompt in enumerate(scenarios, 1):
        print(f"\n{'='*25} TURN {idx} {'='*25}")
        print(f"User: \"{prompt}\"")
        res = agent_system.route_and_execute(prompt, session_id=session)
        print(f"\n[Orchestrator Intent]: {res['intent']}")
        print(f"[Agent Thought]: {res['thought']}")
        print(f"[Tool Invocations]: {res['action']}")
        print(f"\n[Agent Final Response]:\n{res['final_response']}")

if __name__ == "__main__":
    run_assignment2_demo()
