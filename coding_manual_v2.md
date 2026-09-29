# Coding Manual — AI Incident → Listed Company Event Screening

**Purpose.** This manual defines the exact rules two independent coders use to screen the
497 candidate events (449 incidents × listed companies) down to the clean event-study
sample. It exists so that (a) coding is reproducible and (b) inter-rater agreement
(Cohen's κ) can be computed and reported. This document is intended for the paper's appendix.

---

## 1. Unit of analysis

**One row = one `(incident, listed-company)` pair = one candidate event.**

A single AIID incident that names two listed firms (e.g., GOOGL *and* META) appears as **two
rows** and is coded **separately for each firm** — because the event study treats each firm's
stock reaction as a distinct observation, and responsibility can differ by firm within the
same incident.

## 2. What is pre-filled vs. what you code

**Pre-filled (objective, do NOT edit):**
`incident_id, source, pilot, title, ticker, company, matched_entity, match_kind,
aiid_incident_date, earliest_report_date, date_flag, earliest_report_source,
earliest_report_url, n_reports, n_listed_in_incident, incident_url`

**You fill (independently, blank on arrival — purple headers):**
`responsibility_type, correct_ticker, duplicate_of, corrected_event_date, keep, reason`

- **`source`** — `primary` = matched on the developer/deployer field; `recall` = the firm
  was named only in the title and recovered by the recall pass. Give `recall` rows extra
  scrutiny (confirm the firm is really the AI developer/deployer, not a bystander).
- **`pilot`** — `Y` marks the 50-row pilot set. Code these **first** (Round 1, see §9).

Always open `incident_url` (and skim `earliest_report_url`) before coding a row. Code from the
incident's actual facts, not from the title alone.

---

## 3. `responsibility_type`  (values: 1 / 2 / 3)

This is the study's key editorial variable. Decide **from the firm's point of view in this row**.

> **Decision question:** *Whose AI is it, and how is the firm connected to the harm?*

### Type 1 — The firm's OWN AI system failed / behaved harmfully
The listed company **built or operated** the AI system, and that system is what produced the
harm. The market could plausibly re-price the firm on the news.
- **#4 Uber** — Uber's own self-driving car killed a pedestrian.
- **#6 Microsoft** — Microsoft's own Tay chatbot posted abusive content.
- **#3 Boeing** — Boeing's own MCAS flight-control system implicated in crashes.
- **#10 Starbucks** — Starbucks' own use of the Kronos scheduling algorithm harmed its staff.
- Amazon's own résumé-screening bias; a Tesla Autopilot crash; Cruise (→GM) dragging a pedestrian.

### Type 2 — The firm's TOOL was misused by a third party
The listed company merely **supplied a general-purpose tool** (an LLM, image generator, cloud
API, map, ad platform) that **someone unrelated** used to cause harm. The firm did not deploy
the system in the harmful context and is not the actor.
- **#1302 Google** — a stranger made a fake image of a politician *with* Gemini.
- **#1557 Google** — a former council candidate used AI (Gemini) to create false content.
- **#1679 Google** — a Lyft driver used a Gemini-generated image.
- **#1588 / #1589 Google** — scam platforms built on top of Google tools.
- Heuristic: if the sentence is "*X used [firm]'s AI to …*" and X is not the firm, it is **Type 2**.

### Type 3 — Research finding / general multi-firm study
Not a datable, firm-specific "event." Includes academic audits, benchmark studies, and
findings that implicate several firms at once with **no single news-break moment**.
- **#12** — "Common Biases of Vector Embeddings" (a word2vec research paper: no product, no
  news-break date → Type 3).
- **#102** — "Voice assistants struggle with Black voices" (names ~5 firms at once).
- Any row where `n_listed_in_incident` is high AND the incident is a study, not an event.

> **Caution — a study *of a firm's shipped product* is not automatically Type 3.** #13 and #14
> ("Biased Sentiment Analysis") concern Google's *deployed* Perspective API and Cloud Natural
> Language sentiment service, so they are arguably **Type 1** (the firm's own live product
> misbehaved). Type 3 is for findings with no specific shipped system / no datable release.
> Decide per row; use `reason`.

### Tie-breakers
- **Own-brand consumer product that misbehaves = Type 1**, even if end-users prompted it
  (e.g., Microsoft Tay is Type 1: Microsoft ran the bot). The Type 1/2 line is *who operated
  the system*, not *who typed the input*.
- **Platform moderation failures** (harmful content the platform's own recommender surfaced,
  e.g., YouTube Kids #1) = **Type 1** for the platform (its own system curated the content).
- **Tool + deployer both listed, different firms:** code each row on its own. The tool-maker
  row is Type 2; the deployer row may be Type 1.
- If genuinely torn between 1 and 2, default to **2** and explain in `reason` (conservative:
  keeps the main sample "own-system" pure).

**Main event-study sample = Type 1.** Types 2 and 3 are retained in the file for the
tool-misuse vs. own-failure comparison the paper makes, but excluded from the primary test.

---

## 4. `correct_ticker`  (values: Y / N)

> **Decision question:** *Is THIS listed company genuinely the AI developer or deployer named
> in THIS incident?*

- **Y** — the ticker correctly identifies the firm whose AI is at issue (incl. a correct
  parent-for-subsidiary map: `match_kind = subsid`, e.g., Waymo→GOOGL, Cruise→GM, Zoox→AMZN).
- **N** — the match is wrong or too weak. Put the correction (or "no listed firm") in `reason`.

Mark **N** when:
- **Wrong entity collision** — the name matched an unrelated SEC filer.
  *#1304* now has **two** rows — **OMC (Omnicom)** and **WHR (Whirlpool)** — because the recall
  fix added Whirlpool. This is a genuine judgment, not a pre-set answer: AIID lists **DM9, an
  Omnicom agency**, as the entity that produced the AI-altered ad, while Whirlpool is the
  advertiser. Decide which (if either) is the AI developer/deployer and record your reasoning in
  `reason`. Do **not** assume OMC is wrong.
- **Firm is only a supplier/venue, not the AI actor**, and the real operator is someone else.
  *#1393 Woolworths' Olive chatbot* → the deployer is **Woolworths (ASX-listed, not in our US
  SEC universe)**; **Google** is just an infrastructure supplier → GOOGL row = **N**.
- **Doubtful / speculative link** — the firm is mentioned in passing.
  *#574 G/O Media → GOOGL*, *#189 UK DWP → PATH (UiPath)*: if the connection is not clearly
  "this firm's AI," code **N** and say why.
- **Foreign listing not in the US SEC universe** — if the true firm trades only on a non-US
  exchange (e.g., Woolworths AU, Tencent HK), code **N** (out of price-data scope); note the
  real ticker/exchange in `reason` for a possible extension.

> Do **not** silently fix tickers in the sheet. Record the problem via `correct_ticker=N` +
> `reason`; corrections are applied after adjudication so both coders see the same input.

## 5. `duplicate_of`

If this incident is the same real-world event as another incident in the pool, put the
**lower `incident_id`** of the pair here (leave blank otherwise).
- *#1436 and #1528* are both the "AI-Enabled TruDi Navigation System" stroke incident →
  on #1528's rows put `duplicate_of = 1436`.
Judge duplication on the **event**, not the wording: same system + same harm + overlapping
dates ⇒ duplicate, even if titles differ.

## 6. `keep`  (values: Y / N)

Your recommendation for the **main sample**. Code **Y** only if **all** hold:
1. `responsibility_type = 1`, **and**
2. `correct_ticker = Y`, **and**
3. `duplicate_of` is blank (this is the primary row of the event).

Otherwise **N**. (Downstream date/listing/earnings/price-history filters may still drop a `keep=Y`
row — that is expected and is not your call here.) Put a one-line justification in `reason`.

## 7. `reason`

One short free-text line: why you coded the type as you did, the ticker correction, or the
duplicate. Required whenever `correct_ticker=N`, `keep=N`, or the type call is non-obvious.

---

## 8. Dates (context you rely on, do not edit)

- **Use `earliest_report_date` as the event date** — the earliest report *publication* date
  across the incident's linked reports (pulled from the AIID API). It approximates when the
  news could first move the stock.
- `aiid_incident_date` is AIID's editorial incident date; it can be set in hindsight and
  **differs from `earliest_report_date` by >7 days in ~41% of rows**, which is why it is *not*
  the event date. It is shown only so you can spot oddities.
- If `earliest_report_date` is blank (e.g., **#141**), open `incident_url`, find the earliest
  dated report yourself, and note it in `reason`.

**`date_flag` (yellow cells) — the "earliest report" may be the WRONG date.** AIID sometimes
attaches an old background article, so the earliest linked report predates the event or comes
from a non-news source. A row is flagged when the earliest report is dated *before* the AIID
incident date, or its source is **arXiv / SSRN / a PDF / Twitter-X / a personal blog**. Values:
`before_incident, arxiv, ssrn, pdf, twitter/x, blog`. A wrong event date is worse than none.
- **For every flagged row:** open `incident_url`, find the first *real news article* about the
  event, and put its date in **`corrected_event_date`** (+ a note in `reason`).
- **`corrected_event_date`** overrides `earliest_report_date` downstream. Fill it only when you
  are overriding a wrong date; leave blank to accept `earliest_report_date`.
- ~19% of rows are flagged. Examples: #71 (2008 article on a 2016 incident), #53 (2012 PDF),
  #528 (2011 blog), #321 (report dated before the crash), #251 (older ProPublica piece).

---

## 9. Inter-rater reliability procedure — two rounds

Both coders read this manual and agree on it **before** starting. Never let anyone (or an AI)
pre-fill labels: if you see someone else's answer first, your coding is no longer independent
and κ becomes meaningless. Use AI only *afterward*, as a check on disagreements.

**Round 1 — pilot (the 50 `pilot=Y` rows):**
1. Each coder labels the pilot rows in `screening_coder_A.xlsx` / `screening_coder_B.xlsx`,
   **independently, no discussion**.
2. Run `python step5_kappa.py screening_coder_A.xlsx screening_coder_B.xlsx --pilot`
   → Cohen's κ + `disagreements.csv`.
3. Sit together, resolve every disagreement, and **update this manual** wherever a rule was
   unclear (that's the point of the pilot).

**Round 2 — the rest (~460 rows):**
4. Both code the remaining rows independently using the improved manual.
5. Run `step5_kappa.py` (no `--pilot`) for the **final κ** — target ≥ 0.6, ideally ≥ 0.7.
6. Adjudicate remaining disagreements together (or with a third reader); record each
   resolution. Save the agreed labels as **`screening_final.csv`** (keep the `keep` column).

**Then** run `python step4_filters.py` — it reads `screening_final.csv`, applies the mechanical
filters (listing-on-date, ±10-td event merge, earnings ±5 td, ≥250 td pre-event prices) and
writes `final_sample.csv` — your real final N.

*Pace:* ~1–2 min/row → ~8–15 h per coder; split across sessions (tired coding lowers κ).
Report `responsibility_type` κ (headline), plus `correct_ticker` and `keep` κ, in the paper.

---

## 10. Rules added after pilot round 1

Round 1 exposed four recurring ambiguities (pilot κ: `responsibility_type` 0.21, `keep`
0.49, `correct_ticker` 88% raw agreement — κ degenerate because one coder marked Y on
every row). These rules refine §3–§4 and are **binding for round 2**.

**Rule 1 — A study/audit that covers several firms at once is Type 3; `correct_ticker` stays Y for any firm actually named.**
An audit, benchmark, or investigation that tests or implicates multiple companies in one
piece, with no single firm-specific news-break, is a research finding — not a datable event —
even though each named product is real. Code **Type 3** and keep `correct_ticker = Y`.
*Example:* #587 — a *New York Times* test of Google, Apple, Amazon **and** Microsoft image
labelling together → Type 3, `correct_ticker = Y`, `keep = N`.

**Rule 2 — Type 2 needs a named outside party who deliberately used the firm's tool to cause harm; a product that merely works badly is Type 1.**
"Misuse" ≠ "anything that went wrong." If no identifiable third party intentionally turned the
tool to a harmful end, then a malfunction, a bad output, or the firm's own moderation failure
is **Type 1**.
*Example:* #1218 (Microsoft 365 Copilot audit-log flaw) → Type 1 (own-product defect, no
outside actor); contrast #1534, where the *Outsider Enterprise* group deliberately used Gemini
to build phishing sites → Type 2.

**Rule 3 — Supplier vs. deployer: if the supplier's product itself malfunctioned → supplier = Type 1; if it worked as designed and the customer used it harmfully → supplier = Type 2.**
When the AI's maker and the party that placed it in the harmful context differ, ask whether the
AI **failed at its job**. A failure of the supplier's system → supplier **Type 1**; a
correctly-working tool applied harmfully by the customer → supplier **Type 2** (and the
deployer, if listed, is Type 1). This replaces the earlier blanket "tool-maker row is Type 2"
tie-breaker.
*Example:* #475 — IBM's drive-thru ordering AI mis-took orders (the product malfunctioned) →
IBM **Type 1**; contrast #261, where Knightscope's robot worked as designed and the SPCA
deployed it to shoo away homeless people → Knightscope **Type 2**.

**Rule 4 — Own AI involved but not at fault is still Type 1, with a "not at fault" note.**
If the firm's AI was a party to the incident but another actor caused it, keep **Type 1** (the
market reacts to the headline) and write "not at fault" in `reason`.
*Example:* #293 — a Cruise robotaxi hit in a collision **another driver caused** → Type 1,
`reason` notes "not at fault."

**Rule 5 — Attackers vs. a firm's service: an exploited service is Type 1; a tool used inside the attackers' own operation is Type 2.**
If attackers tricked or exploited a service the firm **itself operates**, that is **Type 1**
(the firm's own live system was subverted). If attackers used the firm's tool or model **inside
their own operation**, that is **Type 2**.
*Example:* #1510 — attackers exploited Meta's own AI support bot to hijack accounts → **Type 1**;
contrast #1210 / #1220, where attackers embedded a firm's model in their *own* malware → **Type 2**.

---

## Appendix A — Worked examples

| incident | firm (ticker) | type | correct_ticker | note |
|---|---|---|---|---|
| #4 Uber AV kills pedestrian | Uber (UBER) | 1 | Y | own self-driving system |
| #6 Microsoft Tay | Microsoft (MSFT) | 1 | Y | own chatbot |
| #3 Boeing MCAS | Boeing (BA) | 1 | Y | own flight-control AI |
| #10 Starbucks/Kronos scheduling | Starbucks (SBUX) | 1 | Y | own deployment of algorithm |
| #1 YouTube Kids content | Alphabet (GOOGL) | 1 | Y | own recommender surfaced harm |
| #1302 fake politician image via Gemini | Alphabet (GOOGL) | 2 | Y | third party misused Google's tool |
| #1679 Lyft driver used Gemini image | Alphabet (GOOGL) | 2 | Y | tool misuse by unrelated actor |
| #1588/#1589 scam platforms on Google tools | Alphabet (GOOGL) | 2 | Y | third-party misuse |
| #1304 Whirlpool AI-altered ad | Omnicom (OMC) / Whirlpool (WHR) | ? | ? | judgment call: DM9 (Omnicom agency) made the ad vs Whirlpool the advertiser — coders decide |
| #1393 Woolworths Olive chatbot | Alphabet (GOOGL) | — | **N** | Google is supplier; actor is Woolworths (ASX) |
| #574 G/O Media AI articles | Alphabet (GOOGL) | — | **N** | link to Google doubtful |
| #189 UK DWP fraud algorithm | UiPath (PATH) | — | **N** | weak/indirect link |
| #1528 TruDi navigation (dup of #1436) | Integra (IART) | 1 | Y | `duplicate_of = 1436` |
| #12 vector-embedding bias (word2vec paper) | (various) | 3 | — | research finding, no shipped product / event date |
| #13/#14 biased sentiment (Perspective API, Cloud NL) | Alphabet (GOOGL) | 1 | Y | study of Google's **deployed** product → arguably Type 1, not 3 |

> **These worked-example incidents are excluded from the κ calculation** (coders may recall the
> manual's answer, which would inflate agreement). `step5_kappa.py` drops them automatically;
> state this exclusion in the paper's methods.
