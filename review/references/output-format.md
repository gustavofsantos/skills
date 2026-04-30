# Output Format

Every review delivers exactly four sections in this order.

---

## Section 1 — Executive Architectural Summary

One paragraph. State:
- The detected paradigm (OOP / FP / hybrid)
- The overall health signal (strong foundation, improvable, needs structural attention)
- The tone anchor: encouraging, framed as iterative improvement

Do not list findings here. This is the framing paragraph.

---

## Section 2 — Deep Structural Diagnosis

Narrative paragraphs — no bullet laundry lists. Each violation is explained in prose:
- What the smell or violation is
- Where exactly it appears in the submitted code
- Which pillar it violates and why that matters
- How it degrades clarity, cohesion, or substitutability in practice

Use a comparison table only when multiple violations benefit from side-by-side structure (e.g., "three methods all exceed the line limit for the same reason").

---

## Section 3 — Operational Refactoring Plan

Ordered steps. Each step:
- Names the transformation (e.g., "Extract Value Object for Money", "Apply Flocking Rules to the discount branches")
- Cites the theoretical basis (e.g., "eliminates Primitive Obsession", "moves toward Open-Closed via polymorphism")
- Describes the practical mechanical action

Steps must be safe and sequential. No leaps. No "just use Strategy Pattern here" without showing the path to get there.

---

## Section 4 — Refactored Code

The complete refactored snippet in the original language.

Requirements:
- No inline comments explaining what the code does
- No section markers or annotations
- Self-evident structure — names carry all the meaning
- Demonstrates Programmer Happiness: reading it should feel easy

If the refactoring is large, deliver it in logical chunks with brief bridging prose between them. Do not compress it to the point of hiding the improvements.
