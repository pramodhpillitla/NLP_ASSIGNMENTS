# AI Agents for E-Commerce Application
## Autonomous Multi-Agent Architecture for Product Discovery, Cart Management, and Customer Support
**Student Name:** Pramodh | **Student ID:** B210195 | **Section:** C4  
**Course:** Natural Language Processing | **Date:** November 24, 2026

---

## 1. Executive Summary & Problem Formulation
In retail and commercial environments, standalone LLMs fail catastrophically because they cannot:
1. Access real-time product inventories.
2. Perform exact mathematical arithmetic for sales taxes and discounts.
3. Execute transactional database mutations safely.
4. Adhere strictly to contractual store policies.

This assignment implements an autonomous **Multi-Agent E-Commerce Architecture** utilizing the **ReAct (Reasoning and Acting)** framework and relational SQL database tools.

---

## 2. Multi-Agent Architecture
```
                  ┌──────────────────────────────┐
                  │  Customer Prompt (Session)   │
                  └──────────────┬───────────────┘
                                 │
                                 ▼
                  ┌──────────────────────────────┐
                  │ Orchestrator / Router Agent  │
                  └──────────────┬───────────────┘
                                 │
         ┌───────────────────────┼───────────────────────┐
         ▼                       ▼                       ▼
┌──────────────────┐    ┌──────────────────┐    ┌──────────────────┐
│ Product Discovery│    │  Cart & Checkout │    │ Logistics & Order│
│      Agent       │    │      Agent       │    │  Tracking Agent  │
└────────┬─────────┘    └────────┬─────────┘    └────────┬─────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                                 ▼
                  ┌──────────────────────────────┐
                  │ Relational SQLite Database   │
                  │ (Products, Orders, Coupons)  │
                  └──────────────────────────────┘
```

---

## 3. Multi-Turn Customer Journey Traces
| Turn | User Input | Classified Intent | Tool Invocation | System Outcome |
|---|---|---|---|---|
| T1 | Looking for laptop under $1000 | PRODUCT_DISCOVERY | search_products(max_price=1000) | Recommended UltraBook Pro 14 ($949.99) |
| T2 | Add laptop to cart | ADD_TO_CART | ShoppingCart.add_item(id=1) | Stock verified (25 available), added to cart |
| T3 | Add ergonomic mouse | ADD_TO_CART | ShoppingCart.add_item(id=7) | Stock verified (60 available), added to cart |
| T4 | Apply coupon FESTIVE20 | APPLY_COUPON | validate_coupon('FESTIVE20') | Applied 20% discount (Saved $199.99) |
| T5 | What is in my cart? | CART_INSPECTION | ShoppingCart.view() | Subtotal: $999.98 \| Total with tax: $865.98 |
| T6 | What is return policy on laptops? | POLICY_SUPPORT | get_policy('return_policy') | Returned 30-day risk-free return policy |
| T7 | Proceed to checkout | CHECKOUT | ShoppingCart.checkout() | Created Order ORD-8472, emptied cart |
| T8 | Track order ORD-9821 | ORDER_TRACKING | track_order('ORD-9821') | Status: Shipped via FedEx Express (Nov 26) |

---

## 4. Conclusion
The multi-agent system successfully prevented all price hallucinations, enforced deterministic inventory checks, and executed an end-to-end e-commerce customer journey.
