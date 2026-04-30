---
name: thinking-lenses
description: A set of structured lenses for going deeper during a thinking session. Use when the thinking   partner skill signals that a lens would help, or when the user explicitly asks to apply one. Do NOT run all lenses automatically — apply one at a time, only when invited or when the   situation clearly calls for it. Each lens is a short protocol, not a full interrogation.   Activate on phrases like "let's go deeper", "why does this keep happening", "check my   reasoning", "am I missing something structural", "what if we don't change anything",   "what is this coupling", "what's braided here", or when a thinking session seems stuck at the surface.
---
 
# Thinking Lenses
 
Lenses are not a checklist. They are tools to reach for when the thinking needs
a specific kind of depth. Apply one at a time. Stop when the lens has done its job.
 
---
 
## Lens 1 — The Iceberg
 
**When to use:** The problem keeps recurring. The proposed solution feels like a
patch. The conversation is stuck on symptoms. Something feels like "we've been here
before."
 
**What it does:** Moves thinking from the visible surface to the underlying causes.
Events are the easiest layer to see and the least useful to act on. Leverage lives deeper.
 
**Protocol:**
 
```
1. EVENT — What is the observable problem right now?
   "What are the signs that something is wrong?"
 
2. PATTERN — Is this a one-time event or has this happened before?
   "What does this look like over time? What trends lead here?"
 
3. STRUCTURE — What relationships, decisions, or constraints produce this pattern?
   "What keeps this pattern in place? What architectural or organizational forces
   encourage or prevent change here?"
 
4. MENTAL MODEL — What beliefs or assumptions underpin those structures?
   "What would have to be believed for this structure to seem reasonable?
   What assumptions is the current design acting on?"
```
 
The deeper you go, the more leverage the intervention has. A fix at the event level
patches. A fix at the mental model level changes the system.
 
**Prompt to user:** "We seem to be working at the event level. Want to go deeper
with the Iceberg and see if there's something structural underneath this?"
 
---
 
## Lens 2 — Systemic Reasoning Check
 
**When to use:** Before flushing. When evaluating a proposition — yours or someone
else's. When reasoning feels thin or is being resisted and you're not sure why.
 
**What it does:** Tests whether the reasons supporting a conclusion are actually
load-bearing. Weak reasons produce fragile decisions.
 
**Protocol — four dimensions:**
 
```
RELIABLE — Are the reasons true?
  "Do we actually know this is the case, or are we assuming it?
  What evidence supports this? What would falsify it?"
 
RELEVANT — Are the reasons connected to this specific context?
  "Why does this apply here and now? 'Netflix does it' is not a reason.
  What makes this relevant to our circumstances, not someone else's?"
 
COHESIVE — Do the reasons hang together?
  "Do they build on each other toward the conclusion, or are they
  a loose pile? Is there a gap between any two of them?"
 
COGENT — If all the reasons are true, does the conclusion follow?
  "Read the reasons in order, then 'therefore...' the conclusion.
  Does it land? If the reasons are sound, how likely is it that
  the conclusion is still wrong?"
```
 
**Prompt to user:** "Before we flush this, want to run a quick reasoning check?
It takes five minutes and tends to catch what confidence hides."
 
---
 
## Lens 3 — What If We Do Nothing?
 
**When to use:** Change is being assumed necessary without examining the cost of
not changing. The urgency feels reactive. The status quo hasn't been seriously
considered as an option.
 
**What it does:** Forces the null hypothesis. Surfaces unstated assumptions about
why action is required. Often reveals that the real problem is different from the
stated one, or that the timeline has more slack than it appears.
 
**Protocol:**
 
```
1. Follow the status quo to its end.
   "If we change nothing — not now, not in six months — what happens?
   Walk it out concretely."
 
2. What does that reveal?
   "Does that outcome actually matter? By when? To whom?"
 
3. Compare the cost of action vs. inaction.
   "Is the cost of this change — time, risk, disruption — justified by
   what we avoid or gain? Or are we moving because movement feels better
   than stillness?"
 
4. What does this tell us about the real problem?
   "Sometimes 'do nothing' being genuinely bad reveals what the
   actual constraint is. Sometimes it reveals the urgency was
   manufactured. Which is it here?"
```
 
**Prompt to user:** "We've been treating change as given. Want to spend a few
minutes on 'what if we do nothing?' — it often shifts what we think the real
problem is."
 
---
 
## Lens 4 — Seven Pattern Questions
 
**When to use:** The problem has a sociotechnical dimension — people and systems
are both part of the challenge. The conversation is focused on the technical side
and the human/organizational side hasn't been examined. Something feels off about
how the system is organized but it's not yet named.
 
**What it does:** Maps the current system across seven dimensions. Gaps and
misalignments between dimensions are where problems live.
 
**Protocol — work through each question, skip the ones that clearly don't apply:**
 
```
1. HOW DOES INFORMATION FLOW?
   Where does it originate, who sees it, where does it get stuck,
   what gets lost in translation?
 
2. WHAT ARE THE EVENTS?
   What triggers changes in this system? What causes what?
 
3. WHAT ARE THE BOUNDARIES?
   Where does one thing end and another begin? Are those boundaries
   where they should be, or are they historical accidents?
 
4. WHAT ARE THE BUILDING BLOCKS?
   What are the fundamental parts? Are they the right granularity
   for the problem being solved?
 
5. WHAT IS THE DELIVERY PROCESS?
   How does work move from intention to production? Where does it
   slow down or break?
 
6. HOW ARE PEOPLE ORGANIZED?
   Does the team structure match the system structure? Or are they
   fighting each other?
 
7. HOW IS DISCOURSE STRUCTURED?
   Who has voice? How are decisions made? How does disagreement
   get resolved — or not?
```
 
Gaps between answers to different questions are signal. A delivery process that
doesn't match how people are organized will produce friction. Information that
doesn't flow across boundaries produces silos.
 
**Prompt to user:** "The technical side seems reasonably clear. Want to run the
seven pattern questions to check whether the organizational side is aligned with it?"
 
---
 
## Lens 5 — What Is Braided Here?
 
**When to use:** Evaluating a design choice, a library, a pattern, or an abstraction.
When a change in one place keeps forcing changes in unrelated places. When
something feels heavyweight but you can't name why. When the team is about to
adopt a tool and the discussion is stuck on "is it good?" instead of "what does
it couple?"
 
**What it does:** Shifts evaluation from subjective quality ("is this clean?") to
objective entanglement ("what distinct concerns does this fuse together?"). Two
things braided together may each be fine on their own — the problem is that
changing one now forces you to deal with the other. The goal is to see the braid,
then decide if it's a deliberate trade-off or an accident.
 
**Protocol:**
 
```
1. NAME THE CONCERNS.
   "What are the distinct responsibilities, decisions, or dimensions
   involved here? List them. Don't group yet."
 
2. TRACE THE BRAID.
   "Which of these concerns does this choice fuse together?
   If I change concern A, does concern B have to move too?
   If yes — that's a braid."
 
3. COST OF SEPARATION.
   "What would it take to keep these concerns independent?
   Is there a known pattern that decouples them?
   What do we give up by separating?"
 
4. ACCIDENT OR TRADE-OFF?
   "Did we choose this coupling deliberately, knowing the cost?
   Or did it arrive with a tool, a convention, or a default
   we never questioned? If it's a trade-off — what are we
   getting in return, and is it still worth it?"
```
 
A braid you chose is a trade-off. A braid you inherited without noticing is
a liability. The lens doesn't say "always decouple." It says "always see the
coupling before you commit."
 
**Prompt to user:** "We're evaluating a design choice but the conversation is
about whether it's good or bad. Want to run 'What Is Braided Here?' and look
at what it actually couples together?"
 
---
 
## Using Multiple Lenses
 
Lenses are not mutually exclusive. They have natural sequences.
 
The **Iceberg** might reveal a structural problem — recurring failures caused by
an architectural decision no one revisits. **What Is Braided Here?** can then
examine that specific decision and name the coupling that produces the pattern.
The Iceberg finds *where* the leverage is; the Braiding lens finds *what* is
tangled at that point.
 
The **Systemic Reasoning Check** might expose a reliability gap — a reason that
seemed solid turns out to rest on an assumption. **What If We Do Nothing?** can
then test whether that gap actually matters or whether the urgency was manufactured.
 
**What Is Braided Here?** might reveal a coupling that everyone agrees is bad but
no one acts on. The **Seven Pattern Questions** can then check whether the reason
for inaction is organizational — maybe the team structure mirrors the coupling, and
changing the code means changing how people work.
 
But apply them sequentially, not simultaneously. One lens at a time. Let the
output of one inform whether the next is needed.
