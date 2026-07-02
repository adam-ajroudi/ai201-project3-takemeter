# TakeMeter Planning Document — r/nba Discourse Classifier

## Community

**Community:** r/nba (Reddit's primary NBA discussion subreddit)

**Why this community:** r/nba is one of the most active sports communities on Reddit, with thousands of daily posts and comments during the season and offseason. Discourse quality varies widely — some comments break down film and statistics, others are bold unsupported claims, and many are pure emotional reactions to highlights or trade news. NBA fans on Reddit regularly distinguish between "real analysis" and "hot takes" in everyday conversation, so the label boundaries reflect how participants already talk about post quality. The community is public, text-heavy, and produces more than enough content to collect 200+ examples.

---

## Labels

Three mutually exclusive labels grounded in r/nba norms:

### 1. `analysis`
**Definition:** The post makes a structured argument supported by specific, verifiable evidence such as statistics, historical comparisons, or tactical observations — the claim would still hold some weight even if you removed the opinion framing.

**Example 1:** "Denver's half-court offense ranks 4th in half-court efficiency this season but 22nd in transition. When Jokic sits, their ORtg drops from 118 to 104 — that's a 14-point swing, which explains why their bench minutes are the real problem."

**Example 2:** "Comparing Luka's usage rate (35.2%) to other primary ball-handlers in the playoffs, he's taking on a heavier creation burden than Curry in 2016 or LeBron in 2018. The assist-to-turnover ratio under that load is actually comparable, which suggests the criticism about decision-making is overstated."

### 2. `hot_take`
**Definition:** The post states a bold, confident opinion without meaningful supporting evidence — it asserts a conclusion rather than building an argument, even if the claim might be true.

**Example 1:** "The Lakers are never winning another championship with this roster. LeBron should have retired two years ago."

**Example 2:** "Wembanyama is already a top-5 defender in the league and it's not close. People are sleeping on him because they don't watch Spurs games."

### 3. `reaction`
**Definition:** The post is an immediate emotional response to a specific event with little or no argumentative structure — it expresses a feeling in the moment rather than making a claim to be evaluated.

**Example 1:** "WHAT A BLOCK. I literally jumped off my couch."

**Example 2:** "This trade deadline was a disaster. I'm so done with this front office."

---

## Hard Edge Cases

**Ambiguous type:** A post with one cherry-picked stat wrapped in accusatory framing.

**Example:** "LeBron is overrated — his playoff win rate against top-seeded opponents is below .500."

**Could be:** `analysis` (cites a specific stat) or `hot_take` (bold claim, stat selected for effect).

**Decision rule:** If the post provides specific, verifiable evidence that would support the claim as part of a broader argument — multiple stats, contextual comparison, or tactical explanation — label it `analysis`. If the post uses a single stat as decoration for an opinion without building reasoning around it, label it `hot_take`. The example above uses one stat to punch up an accusation without context → `hot_take`.

**Additional edge case:** Sarcastic reactions that sound like hot takes ("Yeah sure, the refs definitely weren't biased 🙄"). Label as `reaction` if the primary purpose is venting/expressing emotion, not making a debatable claim.

---

## Data Collection Plan

**Source:** Public comments from r/nba collected via the PullPush Reddit archive API (comments only — no private content).

**Target:** 225 total examples, ~75 per label (33% each).

**Process:**
1. Fetch comments from r/nba (varied threads, recent months).
2. Filter: 40–600 characters, exclude [removed]/[deleted], deduplicate.
3. Initial labeling via rule-based heuristics (stat density, emotional markers, hot-take phrases).
4. Manual review of borderline cases and correction of obvious mislabels.
5. Balance to ~75 per label before final export.

**If a label is underrepresented after 200 examples:** Continue fetching from additional r/nba threads and apply stricter filters for the underrepresented class (e.g., for `analysis`, require posts with 2+ stats; for `reaction`, prioritize short exclamatory comments).

---

## Evaluation Metrics

**Primary metrics:**
- **Overall accuracy** — quick sanity check, but misleading with class imbalance.
- **Per-class F1 score** — balances precision and recall; most useful for a 3-class subjective task where we care about each label boundary.
- **Confusion matrix** — shows directional errors (e.g., analysis → hot_take) which maps directly to label boundary problems.

**Why not accuracy alone:** With ~33% per class, a model could score ~33% by guessing randomly. We need to know whether it learns each boundary, especially analysis vs. hot_take which is the hardest distinction.

**Baseline comparison:** Zero-shot Groq (llama-3.3-70b-versatile) on the same locked test set — if fine-tuning doesn't beat baseline meaningfully, labels may be too noisy or the dataset too small.

---

## Definition of Success

**Good enough for deployment:** Fine-tuned model achieves **≥0.60 F1 on all three classes** and **beats the zero-shot baseline by ≥0.10 overall accuracy** on the test set.

**Acceptable for this project:** Fine-tuned model beats baseline on overall accuracy and shows no class with F1 below 0.45 — meaning every label boundary is at least partially learned.

**Failure signal:** Fine-tuned model performs worse than baseline, or one class has F1 ≈ 0 — indicates label inconsistency or insufficient examples for that class.

---

## AI Tool Plan

### Label stress-testing
Before finalizing labels, ask an LLM to generate 10 posts sitting on the analysis/hot_take boundary. Review whether each post can be classified cleanly with our decision rule. If not, tighten definitions before annotating.

### Annotation assistance
Use rule-based heuristics + LLM pre-labeling for initial pass on 250+ raw comments. Every pre-labeled example is reviewed and corrected manually before inclusion in the final CSV. Track which rows were pre-labeled in the `notes` column where corrections were made.

### Failure pattern analysis
After fine-tuning, paste all misclassified test examples into an LLM and ask it to identify systematic patterns (sarcasm, single-stat posts, very short text). Verify each pattern manually against the confusion matrix before writing the evaluation report.

---

## Difficult Labeling Decisions (filled during annotation)

1. **"Curry is the greatest shooter ever and it's not even debatable."** — Could be hot_take (bold assertion) or reaction (fan praise). Decided `hot_take` because it makes a debatable claim about ranking, not just emotional expression.

2. **"They shot 38% from three tonight vs 34% season average — that's the whole story."** — One stat with explanatory framing. Decided `hot_take` because a single stat summary without deeper comparison is decorative, not structured analysis.

3. **"Refs were horrible tonight, absolutely robbed us."** — Emotional but also a claim. Decided `reaction` because the post vents frustration without offering evidence or argument — primary purpose is emotional expression.
