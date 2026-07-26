# CaseNexus — 3-Minute Hackathon Pitch Script

## 0:00 – 0:30 | Problem Hook

> "Across India, over 3,000 FIRs sit in isolated station databases. A serial chain-snatcher
> operates in Koramangala — but the officer in HSR Layout has no idea the same modus operandi
> appeared in their jurisdiction last week. Data silos kill investigations. CaseNexus breaks them."

**Screen:** Dashboard overview — total cases, districts, crime categories.

---

## 0:30 – 1:30 | Core Innovation: Explainable Evidence Panel

> "Let me show you how CaseNexus links cases — not with a black box, but with evidence
> an officer can verify."

**Action sequence:**

1. Open **FIR Explorer** → search for FIR `1792`.
2. Click **"Find Related Cases"** on the case detail page.
3. Point to the top result: **FIR 2823** with 80% confidence.
4. Walk through the four scoring dimensions on screen:
   - **Narrative Match (100%):** "Both FIRs describe the same pattern — two persons on a
     motorcycle snatching gold chains near a bus stand. The engine matched this using token-level
     similarity on the Brief Facts."
   - **Geographic Score:** "These stations are in the same district, within 15 km."
   - **Crime Head Match:** "Both filed under the same IPC section."
   - **Temporal Score:** "Occurred within the same reporting window."

> "Every number on this screen maps to a real investigative signal — no magic, no opacity."

---

## 1:30 – 2:15 | Human-in-the-Loop Workflow

> "But the AI never decides. The officer decides."

**Action sequence:**

1. On the related cases panel for FIR 1792, click **"Confirm Link"** next to FIR 2823.
2. Show the status badge change from **Pending** → **CONFIRMED**.
3. Open the CSV viewer or terminal:
   ```
   head -2 server/data/processed/CaseLinkResult.csv
   ```
   Show the `OfficerDecision` column updated to `CONFIRMED` with timestamp.
4. Explain:
   > "That confirmation is persisted to disk. It's an audit trail. The AI proposes,
   > the officer disposes. We never auto-merge cases — every link requires human sign-off."

---

## 2:15 – 3:00 | Cross-Jurisdiction Impact & Wrap-up

> "Now zoom out."

**Action sequence:**

1. Open **Hotspots** page → show the geospatial map with crime clusters.
2. Navigate to **Entity Intelligence** → show "Sunita Kulkarni" appearing across 56 FIRs.
3. Point to the confidence score and evidence tags (phonetic similarity, age window overlap).
4. Close with:

> "CaseNexus turns fragmented station records into a connected intelligence graph —
> with explainable scoring, human-in-the-loop controls, and zero auto-merging.
> It's decision support, not decision-making. That's the difference between AI that
> assists officers and AI that replaces their judgment."

**Screen:** Return to dashboard. End.

---

## Key Demo IDs (for quick reference)

| Demo Element | ID |
|---|---|
| Case Link Source | FIR 1792 |
| Case Link Target | FIR 2823 |
| Cross-Jurisdiction Source | FIR 803 |
| Cross-Jurisdiction Target | FIR 2917 |
| Entity Name | Sunita Kulkarni (56 cases) |

## Pre-Demo Checklist

- [ ] Backend server running on port 8001
- [ ] Frontend dev server running on port 5173
- [ ] CSV files have fresh `Pending` statuses (reset if needed)
- [ ] Browser console clear of errors
- [ ] Map tiles loading (check internet connection)
