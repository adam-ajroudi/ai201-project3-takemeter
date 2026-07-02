# TakeMeter — r/nba Discourse Classifier

**Author:** Adam Ajroudi  
**Course:** AI201 — Applications of AI Engineering  
**Project:** TakeMeter (Project 3)

TakeMeter is a fine-tuned text classifier that labels r/nba comments as **analysis**, **hot_take**, or **reaction** based on discourse quality patterns common in NBA Reddit communities.

---

## Community Choice

**Community:** r/nba

NBA Reddit is one of the most active sports communities online. Posts range from deep statistical breakdowns to emotional game reactions and bold unsupported claims. Fans regularly distinguish "real analysis" from "hot takes" in everyday discussion, making this a natural fit for a discourse-quality classifier.

---

## Label Taxonomy

| Label | Definition |
|---|---|
| **analysis** | Structured argument backed by specific, verifiable evidence (stats, comparisons, tactical observations). |
| **hot_take** | Bold opinion stated without meaningful supporting evidence — asserts rather than argues. |
| **reaction** | Immediate emotional response to an event with little or no argumentative structure. |

### Examples

**analysis:** "Denver's half-court offense ranks 4th in efficiency but 22nd in transition. When Jokic sits, their ORtg drops from 118 to 104."

**hot_take:** "The Lakers are never winning another championship with this roster. LeBron should have retired two years ago."

**reaction:** "WHAT A BLOCK. I literally jumped off my couch."

See `planning.md` for full definitions, edge-case rules, and additional examples.

---

## Dataset

**Source:** Public r/nba comments and post titles collected via the [PullPush](https://github.com/pullpush-io/pullpush) Reddit archive API.

**File:** [`dataset.csv`](dataset.csv) — 225 labeled examples

**Labeling process:**
1. Fetched 250+ raw comments/posts from r/nba
2. Applied rule-based pre-labeling (stat density, emotional markers, hot-take phrases)
3. Manually reviewed borderline cases and corrected obvious mislabels
4. Balanced to 75 examples per label

**Label distribution:**

| Label | Count | % |
|---|---|---|
| analysis | 75 | 33.3% |
| hot_take | 75 | 33.3% |
| reaction | 75 | 33.3% |

### Difficult Labeling Examples

1. **"Curry is the greatest shooter ever and it's not even debatable."** — Could be hot_take or reaction. Labeled **hot_take** because it makes a debatable ranking claim, not just emotional praise.

2. **"They shot 38% from three tonight vs 34% season average — that's the whole story."** — One stat with minimal context. Labeled **hot_take** per our edge-case rule: single stat used decoratively, not as structured analysis.

3. **"Refs were horrible tonight, absolutely robbed us."** — Emotional but implies a claim. Labeled **reaction** because the primary purpose is venting, not building an argument.

---

## Fine-Tuning Approach

| Setting | Value |
|---|---|
| **Base model** | `distilbert-base-uncased` (HuggingFace) |
| **Platform** | Google Colab (T4 GPU) |
| **Epochs** | 3 |
| **Learning rate** | 2e-5 |
| **Batch size** | 16 |
| **Max sequence length** | 256 tokens |
| **Train/val/test split** | 70% / 15% / 15% (stratified) |

**Hyperparameter decision:** Kept 3 epochs and learning rate 2e-5 (defaults). With only ~157 training examples, higher epochs risk overfitting on a 3-class subjective task. Three epochs is the standard starting point for DistilBERT fine-tuning on small datasets — enough passes for the model to learn label boundaries without memorizing individual posts. Given that `hot_take` recall collapsed to 0.08, the issue appears to be label ambiguity rather than under-training; increasing epochs would likely widen the analysis/reaction split rather than fix hot_take detection.

---

## Baseline Comparison

**Model:** Groq `llama-3.3-70b-versatile` (zero-shot)  
**Prompt:** System prompt with label definitions, one example per label, and instruction to output only the label name (see notebook Section 5).  
**Evaluation:** Same locked 15% test split as the fine-tuned model.

---

## Evaluation Report

**Test set size:** 34 examples (15% of 225, stratified split)

### Overall Accuracy

| Model | Accuracy |
|---|---|
| Zero-shot baseline (Groq) | 0.382 |
| Fine-tuned DistilBERT | 0.588 |
| Improvement | +0.206 |

Fine-tuning beat the zero-shot baseline by over 20 percentage points on the same locked test set, confirming that task-specific training helped — though absolute performance remains modest for a 3-class subjective task.

### Per-Class Metrics (Fine-Tuned)

| Label | Precision | Recall | F1 |
|---|---|---|---|
| analysis | 0.67 | 0.91 | 0.77 |
| hot_take | 0.50 | 0.08 | 0.14 |
| reaction | 0.53 | 0.82 | 0.64 |

### Per-Class Metrics (Baseline)

| Label | Precision | Recall | F1 |
|---|---|---|---|
| analysis | 0.38 | 0.27 | 0.32 |
| hot_take | 0.33 | 0.42 | 0.37 |
| reaction | 0.45 | 0.45 | 0.45 |

The baseline performed near random-chance (~33% for 3 classes). The fine-tuned model improved sharply on `analysis` and `reaction`, but nearly failed to detect `hot_take` at all (recall 0.08).

### Confusion Matrix (Fine-Tuned, Test Set)

|  | Pred: analysis | Pred: hot_take | Pred: reaction |
|---|---|---|---|
| **True: analysis** | 10 | 0 | 1 |
| **True: hot_take** | 4 | 1 | 7 |
| **True: reaction** | 1 | 1 | 9 |

The dominant error pattern is **hot_take → reaction** (7 of 12 hot takes misclassified). The model rarely predicts `hot_take` (only 2 times total), suggesting it learned to split "substantive-looking" vs. "emotional" text but not the narrower hot_take boundary.

See also: [`evaluation_results.json`](evaluation_results.json)

### Sample Classifications

| Text | Predicted Label | Confidence | Correct? |
|---|---|---|---|
| "In 21st century, there are only two seasons where the west only have two 50-win teams: 2022-2023 season and 2017-2018 season..." | analysis | 0.37 | Yes |
| "Western Conference Finals Matchup AI Art" | reaction | 0.35 | Yes |
| "Next hell want neck pillows while theyre sitting on the bench 🙄 okc played the same series you whiny lurch." | reaction | 0.35 | No (true: hot_take) |
| "I'm only counting this series.. yeah data is out there. Most of OKC's starters are actually negative on on/off in this series..." | analysis | 0.36 | Yes |
| "Remove Scott Foster from the NBA, Please Help and Sign this petition" | hot_take | 0.34 | No (true: reaction) |

**Why the first example is reasonable:** The post cites specific historical win totals and compares seeding rules across seasons — multiple verifiable data points used as part of an argument. That matches the `analysis` definition even though the tone is informal.

### Wrong Predictions (3 analyzed)

**1. "Next hell want neck pillows while theyre sitting on the bench 🙄 okc played the same series you whiny lurch."**  
- True: hot_take / Predicted: reaction (confidence: 0.35)  
- **Analysis:** The post is sarcastic and insulting ("whiny lurch"), which reads emotionally. The model likely keyed on the dismissive tone and emoji rather than the underlying debatable claim about OKC's performance. This is a hot_take/reaction boundary failure — the opinion is embedded in venting language.

**2. "Then jokic will never post a guy up or Get any rebounds . He uses his elbows n pushing for both"**  
- True: hot_take / Predicted: analysis (confidence: 0.36)  
- **Analysis:** The post makes a bold claim about Jokic's play style without citing stats or structured evidence, but it describes specific basketball behavior (post-ups, rebounding, elbows). The model appears to treat any post mentioning concrete on-court actions as `analysis`, even when the post is really an unsupported accusation.

**3. "So, do the opposite then. If it's a \"magical pretense\" then, by all means, they should add more games..."**  
- True: analysis / Predicted: reaction (confidence: 0.34)  
- **Analysis:** This post uses sarcasm and rhetorical framing ("do the opposite then") to argue about schedule length. The model likely associated the sarcastic tone with `reaction`, missing that the post is building a logical counterargument rather than just venting. Short argumentative posts with emotional delivery are a systematic weak point.

### Reflection: Intended vs. Learned Behavior

I intended the model to learn three distinct discourse modes: evidence-backed argument, unsupported bold opinion, and pure emotional response. What it actually learned is closer to a **two-way split between "looks substantive" and "looks emotional."**

Evidence: `analysis` recall is 0.91 and `reaction` recall is 0.82, but `hot_take` recall is only 0.08. The confusion matrix shows 7 of 12 true hot_takes routed to `reaction`, and 4 routed to `analysis` — the model almost never outputs `hot_take` itself. This suggests DistilBERT picked up on surface features (stats, exclamation marks, insults) rather than the subtler distinction between "asserted opinion" and "emotional venting."

The gap likely stems from two sources: (1) hot_take is the hardest boundary in our taxonomy — many hot takes look like reactions or thin analysis in isolation; and (2) with only ~157 training examples, the model saw relatively few clear hot_take patterns compared to the other classes after splitting. The model overfit to the easier analysis/reaction split rather than the intended three-way distinction.

---

## Spec Reflection

**How the spec helped:** The milestone structure forced label design before data collection. Writing edge-case decision rules in `planning.md` before annotating prevented inconsistent labels on borderline posts.

**Where implementation diverged:** The spec suggested manual copy-paste annotation; we used PullPush API + rule-based pre-labeling with manual review to speed collection. All pre-labels were reviewed, and AI assistance is disclosed below.

---

## AI Usage

1. **Label stress-testing (Claude/Cursor):** Asked AI to generate boundary posts between analysis and hot_take. Used output to refine the single-stat decision rule in `planning.md`.

2. **Annotation assistance (Cursor):** Used rule-based heuristics scripted with AI assistance to pre-label 250+ raw r/nba posts. Manually reviewed and corrected borderline cases. Pre-labeling was disclosed here; final labels were verified before export.

3. **Failure analysis (Cursor):** Pasted all 14 misclassified test examples into Cursor and asked for systematic patterns. It flagged sarcasm, insult-driven tone, and "behavior description without stats" as hot_take/analysis confusions. Verified against the confusion matrix — hot_take→reaction was the largest single error bucket (7 cases), confirming the pattern.

---

## How to Run

### 1. Colab Notebook

1. Upload [`ai201_project3_takemeter_starter_clean.ipynb`](ai201_project3_takemeter_starter_clean.ipynb) to Google Colab (or open your saved copy)
2. Set runtime to **T4 GPU**
3. Add `GROQ_API_KEY` in Colab Secrets (🔑 sidebar)
4. Run Sections 1–2, then **Section 5 (baseline)**, then Sections 3–4–6
5. Download `evaluation_results.json` and `confusion_matrix.png` and add to this repo

### 2. Local Dataset Collection (optional re-run)

```bash
python3 collect_dataset.py
```

---

## Repository Structure

```
├── planning.md
├── README.md
├── dataset.csv
├── collect_dataset.py
├── ai201_project3_takemeter_starter_clean.ipynb
└── evaluation_results.json   ← from Colab
```
