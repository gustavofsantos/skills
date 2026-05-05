# OOP Evaluation Criteria

## SOLID — Priority Checks

### Single Responsibility
- Does the class have more than one reason to change?
- Does its name accurately describe everything it does?
- If you can't name it without using "and" or "or", it has multiple responsibilities.

### Open-Closed
- Can new behavior be added without modifying existing classes?
- Are conditionals dispatching on type the primary extension mechanism? If yes — polymorphism is missing.

### Liskov Substitution
- Can subclasses be used anywhere the parent is used without breaking behavior?
- Do subclasses throw exceptions the parent doesn't? Override methods with incompatible contracts?

### Interface Segregation
- Are classes forced to implement methods they don't use?
- Are interfaces too broad — serving multiple unrelated consumers?

### Dependency Inversion
- Do high-level modules depend on concrete implementations?
- Are dependencies injected or constructed internally? (Internal construction = hidden coupling)

---

## Law of Demeter

A method should only call methods on:
- `self`
- Objects it created
- Objects passed as parameters
- Objects held as instance variables

**Violation signal:** More than one `.` in a chain that traverses object boundaries (not fluent builder APIs).

**Fix:** Apply Tell, Don't Ask. Move the behavior to where the data lives, or introduce a delegation method.

---

## Encapsulation Audit

- Are instance variables exposed via unrestricted setters?
- Can external code reconstruct or modify internal state without going through domain methods?
- Does the public interface reveal implementation details, or just capabilities?

**Target:** Minimal public surface. Constructors enforce valid initial state. Mutation only through meaningful domain methods.

---

## Inheritance vs. Composition

Inheritance is appropriate when:
- The "is-a" relationship is genuine and stable
- The subclass extends behavior without replacing it
- The hierarchy is shallow (≤ 2 levels)

Prefer composition when:
- Behavior needs to vary independently along multiple axes
- The hierarchy is growing to accommodate variation
- You find yourself overriding methods to neutralize parent behavior
