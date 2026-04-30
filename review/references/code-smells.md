# Code Smells Catalog — Kerievsky / Fowler

For each smell: what it looks like, why it hurts, and the refactoring path.

---

## Primitive Obsession

**Looks like:** Business concepts modeled as raw strings, integers, or floats instead of typed domain objects.

```
# Smells like this
def apply_discount(price: float, discount: float) -> float: ...

order = {"total": 149.99, "currency": "USD", "discount_pct": 0.1}
```

**Why it hurts:** No validation boundary, no behavior attached to the concept, no single place to put business rules about it.

**Refactoring path:** Extract a Value Object. Move validation and behavior into it.

```
# Target direction
class Money:
    def __init__(self, amount: Decimal, currency: str): ...
    def apply_discount(self, rate: DiscountRate) -> Money: ...
```

---

## Feature Envy

**Looks like:** A method in class A that spends most of its time calling getters on class B to do a calculation that belongs to B.

```
# Smells like this — Order reaching into LineItem's data
def calculate_total(order):
    return sum(
        item.unit_price * item.quantity * (1 - item.discount_rate)
        for item in order.items
    )
```

**Why it hurts:** The behavior is separated from the data it operates on. When LineItem changes, calculate_total breaks.

**Refactoring path:** Move the method (or extract the logic) to the class that owns the data.

```
# Target direction
class LineItem:
    def subtotal(self) -> Money: ...

class Order:
    def total(self) -> Money:
        return sum(item.subtotal() for item in self.items)
```

---

## Data Clumps

**Looks like:** The same group of parameters appearing together repeatedly across multiple method signatures.

```
# Smells like this
def book_meeting(start_date, start_time, end_date, end_time, location): ...
def reschedule(start_date, start_time, end_date, end_time): ...
def conflicts_with(start_date, start_time, end_date, end_time): ...
```

**Why it hurts:** The group has implicit cohesion that isn't expressed in the type system. It's a domain concept waiting to be named.

**Refactoring path:** Extract a class (DateRange, TimeSlot, etc.) that encapsulates the cluster.

---

## Message Chains

**Looks like:** Deep navigation through a collaborator's internals to reach the actual data needed.

```
# Smells like this
discount = order.customer.loyalty_program.tier.discount_rate
```

**Why it hurts:** This code is tightly coupled to the entire object graph. Any structural change in any link breaks the chain.

**Refactoring path:** Apply the Law of Demeter. Introduce delegation or a method that hides the traversal.

```
# Target direction
discount = order.applicable_discount_rate()
```

---

## Inappropriate Intimacy

**Looks like:** Two classes that know too much about each other's internals — accessing private fields, calling implementation methods, or bidirectionally depending on each other.

**Why it hurts:** Creates invisible coupling. Changes in one class require changes in the other. Testing either in isolation becomes painful.

**Refactoring path:** Extract a shared concept into a third class, or move behavior to the class that owns the relevant data.

---

## Speculative Generality

**Looks like:** Abstract classes with one implementation, parameters that are never varied, hooks that are never called, or interfaces created "for future flexibility."

**Why it hurts:** Adds cognitive overhead with zero present value. Future requirements rarely match speculative abstractions — they require different abstractions.

**Refactoring path:** Inline the abstraction. Delete the unused hooks. Design for what is known now (Beck Rule 4).

---

## Long Method with Mixed Abstraction Levels

**Looks like:** A method that mixes high-level orchestration with low-level implementation details in the same body.

```
# Smells like this — mixes "what" with "how"
def process_order(order):
    # validate
    if not order.items:
        raise ValueError("empty order")
    for item in order.items:
        if item.quantity <= 0:
            raise ValueError(f"invalid quantity: {item.id}")
    # calculate
    subtotal = sum(i.unit_price * i.quantity for i in order.items)
    tax = subtotal * TAX_RATE
    total = subtotal + tax
    # persist
    db.session.add(order)
    db.session.commit()
    # notify
    email.send(order.customer.email, f"Order confirmed: {total}")
```

**Refactoring path:** Extract each abstraction level into a named method. The top-level method becomes a readable narrative.
