# YOUR MINIMUM CHECKLIST — ~45 minutes of work

Everything else is already done in this folder. You only need to do the steps below.

---

## What's already done for you

- `planning.md` — full label taxonomy, edge cases, evaluation plan
- `dataset.csv` — 225 labeled r/nba posts (75 per label)
- `README.md` — report template (fill in TBD sections after Colab)
- `ai201_project3_takemeter_starter_clean.ipynb` — LABEL_MAP + Groq prompt filled in
- `collect_dataset.py` — data collection script (optional)

---

## Step 1: Create GitHub repo (~5 min)

1. Go to [github.com/new](https://github.com/new)
2. Name it `ai201-project3-takemeter`
3. Upload all files from this folder (or push via git)
4. Do **not** commit any API keys

---

## Step 2: Run Colab notebook (~30 min)

1. Open [Google Colab](https://colab.research.google.com)
2. Upload `ai201_project3_takemeter_starter_clean.ipynb` (File → Upload notebook)
3. **Runtime → Change runtime type → T4 GPU → Save**
4. Add Groq API key:
   - Click 🔑 in left sidebar → Secrets
   - Name: `GROQ_API_KEY`, paste your key, enable notebook access
5. Run cells **in this order**:

| Order | Section | What it does |
|---|---|---|
| 1 | Install + imports | Setup |
| 2 | Section 1 | Upload `dataset.csv` when prompted |
| 3 | Section 2 | Split + tokenize |
| 4 | **Section 5** | Baseline (Groq) — run BEFORE fine-tuning |
| 5 | Section 3 | Fine-tune (~5–15 min) |
| 6 | Section 4 | Test metrics + confusion matrix |
| 7 | Section 6 | Export comparison JSON |

6. Download from Colab Files panel:
   - `evaluation_results.json`
   - `confusion_matrix.png`
7. Add both files to your GitHub repo

**If Colab disconnects:** re-upload CSV, re-run Sections 1, 2, and 5 before continuing.

---

## Step 3: Fill in README (~15 min)

Open `README.md` and replace every `TBD` with numbers from Colab output:

- Overall accuracy (both models)
- Per-class F1 table
- Confusion matrix as markdown table (copy from Colab Section 4)
- Pick 3 wrong predictions from Colab Section 4 output → write why each failed
- Sample classifications table (3–5 posts with confidence)
- Reflection paragraph (what model learned vs. intended)

**Quick tip:** Colab Section 4 prints wrong predictions with text, true label, predicted label, and confidence — copy those directly.

---

## Step 4: Record demo video (~10 min)

Record 3–5 minutes (phone screen record or Loom) showing:

1. Open Colab or run a few test classifications
2. Show 3–5 posts with **label + confidence**
3. Explain **one correct** prediction
4. Explain **one wrong** prediction
5. Briefly show your README metrics

Upload to YouTube (unlisted) or Google Drive and paste link in README.

---

## Step 5: Submit (~2 min)

Submit on Course Portal:

- GitHub repo link
- Demo video link (in README)

---

## Optional: spot-check labels (~10 min, recommended)

Skim 20 random rows in `dataset.csv`. If any label looks obviously wrong, fix it and re-run Colab. Graders may notice bad labels.

---

## What you do NOT need to do

- Design labels from scratch
- Manually collect 200 posts
- Write the Groq prompt
- Write planning.md
- Figure out hyperparameters (defaults are documented)

---

## If something breaks

| Problem | Fix |
|---|---|
| Colab says no GPU | Runtime → Change runtime type → T4 GPU |
| Groq key error | Check Colab Secrets name is exactly `GROQ_API_KEY` |
| Labels don't match | CSV labels must be exactly: `analysis`, `hot_take`, `reaction` |
| Baseline unparseable responses | Re-run Section 5 — prompt is already filled in |
| Fine-tuned worse than baseline | Still submit — analyze why in README |
