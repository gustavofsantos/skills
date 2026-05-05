# Example: FP Review — Data Pipeline (single file)

## Input

```javascript
function processTransactions(transactions) {
  let result = [];
  for (let i = 0; i < transactions.length; i++) {
    let t = transactions[i];
    if (t.status === 'completed') {
      let amount = t.amount;
      if (t.currency !== 'USD') {
        // convert to USD
        amount = amount * getExchangeRate(t.currency);
      }
      if (amount > 1000) {
        t.flagged = true;  // mutating input
        result.push({ id: t.id, amount: amount, flagged: true, category: t.category });
      } else {
        result.push({ id: t.id, amount: amount, flagged: false, category: t.category });
      }
    }
  }
  return result;
}
```

---

## Output

<review>
REVIEW: processTransactions — single file
CORE CHANGE: A transaction processing pipeline that filters, normalizes currency,
             and flags high-value items.

─── PHASE 1 — SCOPE AND SAFETY ───────────────────────────────

Test confidence: None
What tests communicate: No tests provided.
Test gaps: Currency conversion behavior, flagging threshold, mutation side effects,
           empty input, non-completed transactions — none covered.
Scope discipline: on-target
Safety signal: Yellow
Verdict: Proceeding to depth review. Tests should be written before shipping —
         the mutation bug in particular needs a regression test.

─── PHASE 2 — DEPTH REVIEW ────────────────────────────────────

This is JavaScript operating in a functional context — a data transformation
pipeline over a collection — written with an imperative mindset. The logic is
correct and the intent is legible. The structural issues are about paradigm
mismatch: the code uses the idioms of a language without the practices that make
those idioms safe and composable. The refactoring path is mechanical and low-risk.

The most significant issue is input mutation. `t.flagged = true` modifies the
original transaction object. Any other code holding a reference to the same objects
now sees the mutation — a classic action-at-a-distance bug. This violates the
foundational FP constraint of immutability and also fails Beck's Rule 1: it changes
behavior for callers who don't expect it.

The manual `for` loop names the mechanics of iteration without expressing the intent
of the transformation. Three distinct things are happening — filtering, currency
normalization, and flagging — each of which maps cleanly to a declarative pipeline
stage. Written as `filter` → `map` → `map`, each stage is independently readable,
testable, and replaceable.

The inline comment `// convert to USD` is a DHH smell: a named concept left
anonymous. It belongs in a function called `normalizeToUSD`. Once extracted, the
comment becomes redundant and disappears.

The two branches of the final conditional produce objects with identical shapes but
different values for `flagged`. This is a Data Clump hiding a simpler solution:
derive `flagged` directly from `amount` without branching.

**Refactoring plan**

Step 1 — Eliminate mutation (Immutability, Beck Rule 1)
Replace `t.flagged = true` with spread syntax. Never modify the input.

Step 2 — Extract `normalizeToUSD` (DHH: Comments as Smells)
Move currency conversion to a named function. It now has a single responsibility
and can be tested independently.

Step 3 — Extract `isFlagged` predicate (Minimalism + Clarity)
Replace the conditional branch with `const isFlagged = amount => amount > 1000`.
The branching disappears.

Step 4 — Replace the loop with a declarative pipeline (FP: Declarative over Imperative)
Compose `filter` → `map` to express the two transformation stages. The structure
of the pipeline mirrors the structure of the business logic.

**Refactored**

const normalizeToUSD = (amount, currency) =>
  currency === 'USD' ? amount : amount * getExchangeRate(currency);

const isFlagged = amount => amount > 1000;

const toProcessedTransaction = transaction => {
  const amount = normalizeToUSD(transaction.amount, transaction.currency);
  return {
    id: transaction.id,
    amount,
    flagged: isFlagged(amount),
    category: transaction.category,
  };
};

function processTransactions(transactions) {
  return transactions
    .filter(t => t.status === 'completed')
    .map(toProcessedTransaction);
}

─── SUMMARY ────────────────────────────────────────────────────

Overall: Yellow
Must fix before merge: Input mutation (t.flagged = true). Write at least one
                       regression test for this before shipping.
Consider: Full declarative pipeline refactor as described above.
Looks good: Intent is clear, business logic is correct, transformation shape is
            already implicit in the code — the refactor reveals what's already there.
</review>
