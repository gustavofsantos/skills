# Example: Branch Diff Review — Clojure feature branch

## Context

Branch `feat/add-expense-category-filter` against `main`.
A new filter parameter on the expense listing endpoint.

## Simulated diff stat

```
src/seubarriga/expenses/queries.clj       | 34 ++++++++++++++---
src/seubarriga/expenses/handler.clj       | 18 +++++++--
src/seubarriga/expenses/queries_test.clj  | 41 +++++++++++++++++++
3 files changed, 87 insertions(+), 6 deletions(-)
```

## Simulated diff (abbreviated)

```clojure
;; queries.clj — before
(defn list-expenses [user-id opts]
  (jdbc/query db
    ["SELECT * FROM expenses WHERE user_id = ? ORDER BY date DESC"
     user-id]))

;; queries.clj — after
(defn list-expenses [user-id opts]
  (let [category (:category opts)
        base-query "SELECT * FROM expenses WHERE user_id = ?"
        query (if category
                (str base-query " AND category = '" category "'")
                base-query)
        params (if category [user-id category] [user-id])]
    (jdbc/query db [query user-id])))

;; handler.clj — after
(defn list-expenses-handler [req]
  (let [user-id (get-in req [:session :user-id])
        category (get-in req [:params :category])
        expenses (queries/list-expenses user-id {:category category})]
    (response/ok {:expenses expenses})))

;; queries_test.clj — added
(deftest list-expenses-test
  (testing "returns all expenses when no category filter"
    (is (= 3 (count (queries/list-expenses test-user-id {})))))
  (testing "filters by category"
    (is (= 1 (count (queries/list-expenses test-user-id {:category "food"}))))))
```

---

## Output

<review>
REVIEW: feat/add-expense-category-filter → main
CORE CHANGE: A category filter parameter added to the expense listing query.

─── PHASE 1 — SCOPE AND SAFETY ───────────────────────────────

Test confidence: Medium
What tests communicate: The filter returns results for a known category, and the
                        no-filter path still returns all expenses. The shape of
                        the contract is visible from the tests alone.
Test gaps: No test for an unknown category (should return empty, not error).
           No test for nil/blank category input. The SQL injection path is not
           tested — and it is exploitable (see below).
Scope discipline: on-target — handler and query changes are coherent and contained.
Safety signal: Red
Verdict: SQL injection via string concatenation in queries.clj. The category value
         from user input is interpolated directly into the query string.
         `(str base-query " AND category = '" category "'")` — this is exploitable.
         Do not merge until fixed. Proceeding to depth review.

─── PHASE 2 — DEPTH REVIEW ────────────────────────────────────

This is idiomatic Clojure with one critical exception. The handler and the query
separation is clean. The change is narrow and the intent is immediately legible.
The only structural problem is the one flagged in Phase 1, but it is worth
examining how it happened — because the fix changes the shape of the function.

The bug is in how the conditional query is built. The author correctly identified
that params need to change conditionally, but then built the query string by
concatenation rather than parameterization. This is likely because the standard
jdbc vector pattern `[query & params]` makes conditional params slightly awkward.
The solution is to build both the query fragment and the param together:

```clojure
(defn list-expenses [user-id {:keys [category]}]
  (let [[where-clause params]
        (if category
          ["AND category = ?" [category]]
          ["" []])
        query (str "SELECT * FROM expenses WHERE user_id = ? "
                   where-clause
                   " ORDER BY date DESC")]
    (jdbc/query db (into [query user-id] params))))
```

This keeps the parameterized form throughout and makes the conditional explicit
at the fragment level rather than the string level.

There is also a subtle bug in the original that the test suite does not catch:
the `params` binding is constructed correctly, but `(jdbc/query db [query user-id])`
ignores it — `user-id` is hardcoded into the vector instead of using `params`.
This means the category filter is silently dropped for all queries. The tests pass
because the test data is set up such that `user-id` alone is sufficient — a false
green.

**Refactoring plan**

Step 1 — Fix SQL injection and the silent param bug
Replace string concatenation with parameterized fragment construction as shown above.
This fixes both issues in one change.

Step 2 — Add missing test cases
- Category that matches no expenses → empty result, no error
- Nil/blank category → treated as no filter
- These two cases would have caught the silent param bug.

**Refactored core (queries.clj)**

(defn list-expenses [user-id {:keys [category]}]
  (let [[filter-clause filter-params]
        (if category
          ["AND category = ?" [category]]
          ["" []])
        query (str "SELECT * FROM expenses "
                   "WHERE user_id = ? "
                   filter-clause
                   " ORDER BY date DESC")]
    (jdbc/query db (into [query user-id] filter-params))))

─── SUMMARY ────────────────────────────────────────────────────

Overall: Red
Must fix before merge: SQL injection via string concatenation. Silent param bug
                       (filter is built but not used — category filter never applies).
Consider: Two additional test cases (no-match category, nil category) that would
          have caught the param bug before review.
Looks good: Handler/query separation is clean. The change is narrow and well-scoped.
            The intent of the filter is immediately legible from the test names.
</review>
