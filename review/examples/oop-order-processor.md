# Example: OOP Review — Order Processing (single file)

## Input

```python
def process_order(order_id, user_id, items, coupon_code, shipping_address, billing_address):
    user = db.query(f"SELECT * FROM users WHERE id = {user_id}")
    if not user:
        return {"error": "user not found"}

    order_items = []
    total = 0
    for item in items:
        product = db.query(f"SELECT * FROM products WHERE id = {item['id']}")
        if product['stock'] < item['quantity']:
            return {"error": f"insufficient stock for {product['name']}"}
        price = product['price'] * item['quantity']
        if coupon_code == "SAVE10":
            price = price * 0.9
        elif coupon_code == "SAVE20":
            price = price * 0.8
        total += price
        order_items.append({"product_id": item['id'], "quantity": item['quantity'], "price": price})

    order = db.execute(
        "INSERT INTO orders (user_id, total, shipping_address, billing_address) VALUES (?, ?, ?, ?)",
        user_id, total, shipping_address, billing_address
    )
    for oi in order_items:
        db.execute("INSERT INTO order_items ...", oi)

    email_body = f"Dear {user['name']}, your order total is {total}."
    send_email(user['email'], "Order Confirmed", email_body)

    return {"order_id": order.id, "total": total}
```

---

## Output

<review>
REVIEW: process_order — single file
CORE CHANGE: The complete order lifecycle — validation, pricing, persistence,
             and customer notification — in a single function.

─── PHASE 1 — SCOPE AND SAFETY ───────────────────────────────

Test confidence: None
What tests communicate: No tests provided.
Test gaps: SQL injection is untested and exploitable. Stock validation, coupon
           logic, and persistence paths have no coverage.
Scope discipline: on-target
Safety signal: Red
Verdict: SQL injection via string interpolation in user_id and item['id'] queries
         is a correctness violation (Beck Rule 1) and a security issue. This must
         be fixed before anything else. Proceeding to depth review to document
         the full picture, but do not ship until the injection is resolved.

─── PHASE 2 — DEPTH REVIEW ────────────────────────────────────

This is an object-oriented Python codebase operating without objects. The function
carries every responsibility in the order lifecycle — validation, pricing,
persistence, and notification — in a single 30-line procedure. The foundation is
salvageable: the business intent is clear and the logic is mostly correct. What
follows is the path toward a design that can grow without accumulating debt.

The SQL injection (string-interpolated user_id and item['id']) violates correctness
before any structural concern can be raised. This is the only Red finding and the
only blocking issue. Everything else is structural.

The most visible structural problem is that `process_order` has four independent
reasons to change: pricing policy, database schema, notification channel, and
validation rules. This is a textbook God Function — the procedural equivalent of
a God Class. Each responsibility is a future maintenance burden waiting to surface
as a bug in an unrelated code path.

Beneath the structure lies Primitive Obsession. The coupon logic is a string
compared against hardcoded constants to determine discount rates. There is no
`Coupon` or `DiscountPolicy` in this codebase — just literals scattered through
the flow. When a third coupon type arrives, this conditional grows. The business
concept exists; it has no home.

The two inline section comments — `# save order to database` and
`# send confirmation email` — are DHH smells compensating for the function's
refusal to name its own intentions. Extracting those blocks into `_persist_order`
and `_notify_customer` makes the comments redundant and reveals the structure
already implicit in the code.

**Refactoring plan**

Step 1 — Fix SQL injection (Beck Rule 1 — Correctness)
Replace all string-interpolated queries with parameterized queries. This is a
precondition for everything else.

Step 2 — Extract a Coupon value object (Primitive Obsession)
Create a `Coupon` class that knows its own discount rate. The conditional
`if coupon_code == "SAVE10"` disappears. New coupon types are added by registering
new instances, not by editing the processing function.

Step 3 — Extract `_validate_stock` and `_calculate_line_price` (Metz: Lines per Method)
The loop body handles validation and pricing simultaneously. Extract each into a
named method. The loop body becomes two readable calls.

Step 4 — Extract `_persist_order` and `_notify_customer` (DHH: Comments as Smells)
Move database writes and email dispatch into private methods. The top-level function
becomes an orchestrator that reads like a domain narrative.

Step 5 — Inject dependencies (Dependency Inversion)
Pass `db` and `email_service` as constructor arguments. This makes the class
testable without a live database or mail server.

**Refactored**

```python
from dataclasses import dataclass
from decimal import Decimal
from typing import Optional

COUPONS = {
    "SAVE10": Decimal("0.90"),
    "SAVE20": Decimal("0.80"),
}

@dataclass(frozen=True)
class Coupon:
    multiplier: Decimal

    @classmethod
    def from_code(cls, code: Optional[str]) -> "Coupon":
        return cls(multiplier=COUPONS.get(code, Decimal("1.0")))

    def apply(self, price: Decimal) -> Decimal:
        return price * self.multiplier


class OrderProcessor:
    def __init__(self, db, email_service):
        self.db = db
        self.email_service = email_service

    def process(self, user_id, items, coupon_code, shipping_address, billing_address):
        user = self._find_user(user_id)
        coupon = Coupon.from_code(coupon_code)
        order_items, total = self._build_order_items(items, coupon)
        order = self._persist_order(user_id, total, order_items, shipping_address, billing_address)
        self._notify_customer(user, total)
        return {"order_id": order.id, "total": total}

    def _find_user(self, user_id):
        user = self.db.query("SELECT * FROM users WHERE id = ?", user_id)
        if not user:
            raise ValueError(f"User {user_id} not found")
        return user

    def _build_order_items(self, items, coupon):
        order_items, total = [], Decimal("0")
        for item in items:
            product = self.db.query("SELECT * FROM products WHERE id = ?", item["id"])
            self._validate_stock(product, item["quantity"])
            price = coupon.apply(product["price"] * item["quantity"])
            total += price
            order_items.append({"product_id": item["id"], "quantity": item["quantity"], "price": price})
        return order_items, total

    def _validate_stock(self, product, quantity):
        if product["stock"] < quantity:
            raise ValueError(f"Insufficient stock for {product['name']}")

    def _persist_order(self, user_id, total, items, shipping_address, billing_address):
        order = self.db.execute(
            "INSERT INTO orders (user_id, total, shipping_address, billing_address) VALUES (?, ?, ?, ?)",
            user_id, total, shipping_address, billing_address,
        )
        for item in items:
            self.db.execute("INSERT INTO order_items ...", item)
        return order

    def _notify_customer(self, user, total):
        self.email_service.send(
            to=user["email"],
            subject="Order Confirmed",
            body=f"Dear {user['name']}, your order total is {total}.",
        )
```

─── SUMMARY ────────────────────────────────────────────────────

Overall: Red
Must fix before merge: SQL injection via string interpolation — both queries.
Consider: Full structural refactor as described. Coupon as value object is the
          highest-leverage change after the injection fix.
Looks good: Business logic is correct. The intent of each step is legible even
            in the current form. The refactor reveals structure that is already
            implicit — nothing is being invented.
</review>
