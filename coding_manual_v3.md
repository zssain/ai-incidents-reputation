# Coding Manual v3 — AI Incident → Listed Company Event Screening

> **Version 3 — frozen 2026-09-25.** Used for all coding after pilot round 3.
> Supersedes v1 (initial) and v2 (v1 + post-pilot rules 1–5). Earlier versions are archived
> as `coding_manual_v1.md` and `coding_manual_v2.md`. See Appendix B for the version history.
> **This manual must not be changed while any coding round is in progress.**

---

## 1. Purpose

This manual defines the rules coders use to classify AI incidents involving publicly listed
companies, so that coding is **consistent, reproducible, independent**, and suitable for
inter-rater reliability testing (Cohen's κ). Coders use **only this manual** while coding.
If two rules seem to conflict, the more specific rule (§8–§11) overrides the general definition.

## 2. Unit of analysis

**One row = one AI incident × one listed company.** If an incident involves several listed
companies, each has its own row, and each row is judged **from the point of view of that row's
ticker**. Do not assume every company in an incident gets the same answer.

## 3. Fields

**Pre-filled (do not edit):** `incident_id, source, pilot, title, ticker, company,
matched_entity, match_kind, aiid_incident_date, earliest_report_date, date_flag,
earliest_report_source, earliest_report_url, n_reports, n_listed_in_incident, incident_url`

- `source = recall` means the firm was found only in the incident title. Check carefully that
  the firm is really the AI developer or deployer, not a bystander.
- `match_kind = subsid` means the AI belongs to a subsidiary mapped to its listed parent
  (e.g., Waymo → GOOGL, Cruise → GM, Zoox → AMZN, Instagram → META).

**Coder fills:** `correct_ticker, responsibility_type, duplicate_of, corrected_event_date, keep, reason`

## 4. Required source review

Before coding any row:
1. Open `incident_url` and read the incident description.
2. Read enough linked reports to know: what happened, whose AI system was involved, who
   operated it, whether an outside actor deliberately misused it, whether it is a study/audit,
   and (if `date_flag` is set) the correct date.
3. **Never code from the title alone.**

If the incident cannot be opened or read: `reason = UNREADABLE`, leave all other fields blank.
Do not guess.

## 5. Coding order

Code every row in this order: **1** `correct_ticker` → **2** `responsibility_type` →
**3** `duplicate_of` → **4** `corrected_event_date` → **5** `keep` → **6** `reason`.

---

## 6. `correct_ticker` (Y / N)

> **Question:** Did the company represented by this ticker genuinely **build, operate, deploy,
> or own** the AI system that is central to this incident?

**Y** when the company (or its subsidiary): built the AI; operated it; deployed it; or its
product is genuinely one of the systems tested in a multi-company study.

**N** when the company is: only mentioned; merely a venue or host (see §11); merely a customer,
advertiser or victim; an unrelated infrastructure provider; not the firm that developed or
deployed the AI; or a name collision with an unrelated SEC filer.

**US listing rule.** If the firm whose AI is actually at issue trades only on a non-US exchange
(e.g., Woolworths on the ASX, Tencent in Hong Kong), the US ticker in this row is **N**. Name the
real firm and exchange in `reason`.

**Special case — #1304 (Omnicom / Whirlpool).** AIID lists DM9, an Omnicom agency, as the
producer of the AI-altered ad, while Whirlpool is the advertiser. This is a genuine judgment
call: decide which firm (if either) developed or deployed the AI and explain in `reason`.

> **`correct_ticker` is NOT about blame.** Do not answer N because someone else caused the harm,
> the company was attacked, the company was "not at fault", or other companies were also involved.
> If this firm's own AI is the system involved, the answer is **Y**.

Do not silently fix tickers. Record problems with N + `reason`.

---

## 7. `responsibility_type` (1 / 2 / 3)

Apply the three questions **in this order**.

### 7.1 Type 3 — Multi-company study, audit or research finding (ask first)

Is this primarily a **research paper, audit, benchmark, investigation or structured test that
covers several companies at once**, with no single firm-specific news event?
→ **Type 3.** For every company genuinely included: `correct_ticker = Y`, `keep = N`.

Also Type 3: a research paper with **no product and no news event** (e.g., a paper on general
model behaviour).

**Exception:** a study of **one** firm's **deployed** product that finds the product itself
defective is usually **Type 1**, not Type 3.
- general multi-company research → **Type 3**
- firm-specific defect in a deployed product → **Type 1**

### 7.2 Type 2 — Deliberate outside misuse

Use Type 2 **only** when a separate outside person, group, customer, developer, criminal or
organization **deliberately used the firm's tool inside their own operation** to cause harm.
You should be able to complete the sentence:

> "**[Outside actor]** used **[company's tool]** to **[harmful purpose]**."

Examples: a scammer used an image generator to make fraudulent images; outside developers used
an open-source model to build harmful bots; attackers embedded an LLM inside their own malware.

> **Type 2 does NOT mean "not their fault."** Do not choose Type 2 merely because someone else
> contributed, the company was attacked, a user typed the harmful prompt, or the company was not
> blamed. There must be an identifiable outside actor using the tool in **their own** harmful
> activity.

### 7.3 Type 1 — Firm's own AI system

Type 1 when the firm's own AI, algorithm, model, recommender, autonomous system, chatbot,
moderation system or deployed AI service: malfunctioned; behaved unexpectedly; produced harmful
output; made an unsafe decision; discriminated; leaked information; failed at moderation;
recommended harmful material; had a security or privacy defect; was successfully manipulated
while being operated by the firm (§9); or was involved even though another party caused the
final harm (§10).

Examples: an Autopilot crash; a company's own chatbot producing abusive output; a platform's
recommender surfacing harmful content; a company's hiring algorithm discriminating.

**If still unsure after §7–§11:** follow the decision tree (§17), choose the best-supported
type, and start `reason` with **"UNCERTAIN:"** so the adjudicator reviews it.

---

## 8. Supplier vs. customer

When one company makes the AI and another deploys it, ask: **did the supplier's AI itself fail
at what it was supposed to do?**
- **Yes** → supplier = **Type 1** (e.g., a restaurant uses a supplier's ordering AI and the AI
  repeatedly mishears orders).
- **No** — it worked as designed but the customer used it harmfully → supplier = **Type 2**.
  The customer, if listed in another row, is judged separately (usually Type 1).

## 9. Attacks and exploits

Ask: **where did the harmful action happen?**
- **Attack ON the firm's own live service** (tricked, jailbroken, prompt-injected, exploited,
  subverted — e.g., attackers exploit the firm's own support chatbot) → **Type 1**.
- **Firm's tool used INSIDE the attacker's own operation** (phishing, malware, scams, fraud,
  disinformation built with the firm's model) → **Type 2**.

> Memory rule: attack **on** the firm's service → 1 · firm's tool used **in** the attacker's
> operation → 2.

## 10. "Not at fault"

If the firm's AI was genuinely involved but another actor caused the incident (e.g., a
self-driving car hit by a human driver): **Type 1, `correct_ticker = Y`**, and `reason` must
contain the words **"not at fault"**. Do not change it to Type 2 or to N.

## 11. Platforms and venues

A company is **not** automatically Y just because harmful AI content appeared on its platform.
Ask: **did any of the platform's own AI systems play a part?**

- **Platform only hosted** content made elsewhere, and none of its AI systems (ads, moderation,
  recommendation, search) played a role in the incident → `correct_ticker = N`, reason: "only a
  host/venue".
- **Platform's own AI systems** — ad review/targeting, content moderation, recommendation,
  search — **approved, failed to catch, distributed or amplified** the harmful content →
  `correct_ticker = Y`, **Type 1** (the platform's own system failed).

If the incident text says the platform's systems approved, ran, targeted, recommended or failed
to remove the content, that counts as the platform's AI being involved.

---

## 12. `duplicate_of`

Only when two incident IDs describe **the same underlying real-world event**: same system,
same harm, same or overlapping occurrence and dates. Enter the **lower** incident ID
(e.g., #1528 → `duplicate_of = 1436`).

Not enough on their own: same company; same product; same type of harm; similar stories;
same general controversy.

## 13. Dates — `corrected_event_date`

- The event date is normally `earliest_report_date` (earliest publication date of the linked
  reports). `aiid_incident_date` is set in hindsight and is shown only to spot oddities.
- **`date_flag` empty** → leave `corrected_event_date` blank.
- **`date_flag` set** (`before_incident, arxiv, ssrn, pdf, twitter/x, blog`) → find the
  **earliest real news article specifically reporting this incident**.
  - If `earliest_report_date` is already correct → leave blank.
  - If it is wrong → enter the correct date (YYYY-MM-DD) and explain in `reason`.
- Do not use: the physical accident date, an old background article, an unrelated earlier
  story, or arXiv / SSRN / PDF / Twitter-X / blog dates.
- **`earliest_report_date` blank** (e.g., #141) → find the earliest dated news report yourself,
  enter it in `corrected_event_date`, and note it in `reason`.

A wrong event date is worse than none.

## 14. `keep` (calculated mechanically)

`keep = Y` only when **all** hold: `responsibility_type = 1` **and** `correct_ticker = Y`
**and** `duplicate_of` is blank. Otherwise `keep = N`. Never decide `keep` by importance or
gut feeling.

## 15. `reason`

One short factual sentence stating **what happened**, not just repeating the label.
Required whenever `correct_ticker = N`, `keep = N`, a date is corrected, the type call is not
obvious, the case is "not at fault", or the row is a duplicate.

**Good:** "Several chatbots were tested together in one audit." · "Outside developers used the
firm's open model in their own harmful bots." · "The subsidiary's own autonomous vehicle was
involved but not at fault." · "Attackers exploited the firm's own live support bot." · "The firm
is only mentioned; another company's AI was involved."

**Too vague:** "bad", "their fault", "not them", "misused", "other companies", "wrong".

---

## 16. Final consistency check (every row)

1. **Type 2?** Can I name an outside actor who deliberately used the tool in their own
   operation? If not → reconsider Type 1.
2. **Type 3?** Is it really a multi-company study/audit or a no-event research paper? If not →
   reconsider 1 or 2.
3. **Ticker N?** Can I clearly say why this firm's AI is not the relevant AI (and not just "not
   to blame")? If not → reconsider Y.
4. **Ticker Y?** Did the firm genuinely build, run, deploy, own, or have its product tested?
5. **keep** matches §14 exactly.
6. **Corrected date** filled only if `date_flag` is set (or the report date was blank) **and**
   the original date was actually wrong.
7. **Duplicate** only if both IDs describe the same real-world event.

## 17. Decision tree

```
START
 ├─ Did this ticker's firm build / run / deploy / own the AI (or have its product tested)?
 │     NO → correct_ticker = N          YES → correct_ticker = Y
 ├─ Is this a multi-company study / audit / benchmark, or a no-event research paper?
 │     YES → Type 3
 ├─ Did an identifiable outside actor deliberately use the firm's tool
 │  inside their OWN harmful operation?
 │     YES → Type 2
 ├─ Otherwise: the firm's own AI / product / service malfunctioned, produced harm,
 │  failed moderation, was exploited while the firm ran it, or was involved not at fault
 │     → Type 1
 ├─ Check duplicate (§12) → check date (§13) → calculate keep (§14) → write reason (§15)
END
```

## 18. Three-sentence shortcut

- **Type 1** — the company's own AI or service was the system that went wrong or was attacked.
- **Type 2** — someone outside the company used the company's tool in their own harmful operation.
- **Type 3** — researchers or investigators tested several companies together, rather than
  reporting one company-specific event.

---

## 19. Coding and reliability procedure (from v3 onward)

**Coders.** Main coding is done by an AI coder (model name, version and run date recorded), using
this frozen manual and a fixed prompt (`coderB_prompt_v3.txt`). A human coder independently codes
a validation sample. The lead author adjudicates.

1. **Freeze** this manual and the prompt before coding starts. No rule changes during a round.
2. **AI main run:** the AI coder codes all remaining rows in batches, in one session, and
   never sees any human coder's answers.
3. **Human validation sample:** draw a random sample of **≥ 50** AI-coded rows (fixed seed,
   stratified by ticker, excluding Appendix A incidents). The human coder codes them
   **independently, without seeing the AI's answers**.
4. **Compute** Cohen's κ (human vs AI) for `responsibility_type`, `correct_ticker` and `keep`,
   plus raw % agreement and a prevalence-adjusted statistic (PABAK or Gwet's AC1).
   Report all three rounds of pilot results as well.
5. **Adjudicate** every disagreement and every `UNCERTAIN:` row using this manual; record each
   resolution. Do not change any coder's original answers to raise κ.
6. **Dates:** a human verifies the event date of every `keep = Y` row that has a `date_flag`.
7. Save the agreed labels as `screening_final.csv`, then run `step4_filters.py`.

Target: κ ≥ 0.6 on `responsibility_type`. Report the result honestly whatever it is.

## 20. Output format

```
incident_id,ticker,responsibility_type,correct_ticker,duplicate_of,corrected_event_date,keep,reason
```
One row per input row, original order, no extra columns, blank means blank, dates as YYYY-MM-DD,
type ∈ {1,2,3}, ticker and keep ∈ {Y,N}.

---

## Appendix A — Worked examples

| incident | firm (ticker) | type | correct_ticker | note |
|---|---|---|---|---|
| #4 Uber AV kills pedestrian | Uber (UBER) | 1 | Y | own self-driving system |
| #6 Microsoft Tay | Microsoft (MSFT) | 1 | Y | own chatbot, even though users prompted it |
| #3 Boeing MCAS | Boeing (BA) | 1 | Y | own flight-control system |
| #10 Starbucks/Kronos scheduling | Starbucks (SBUX) | 1 | Y | own deployment of the algorithm |
| #1 YouTube Kids content | Alphabet (GOOGL) | 1 | Y | own recommender surfaced harm |
| #13/#14 biased sentiment (Perspective API, Cloud NL) | Alphabet (GOOGL) | 1 | Y | defect in Google's own deployed product |
| #1218 Microsoft 365 Copilot audit-log flaw | Microsoft (MSFT) | 1 | Y | own-product defect, no outside actor |
| #475 IBM drive-thru ordering AI | IBM (IBM) | 1 | Y | supplier's product malfunctioned (§8) |
| #293 Cruise robotaxi in collision caused by another driver | GM (GM) | 1 | Y | "not at fault" (§10) |
| #1510 attackers exploited Meta's own AI support bot | Meta (META) | 1 | Y | attack on firm's own service (§9) |
| #1302 fake politician image via Gemini | Alphabet (GOOGL) | 2 | Y | outsider used the tool |
| #1679 Lyft driver used a Gemini image | Alphabet (GOOGL) | 2 | Y | outsider used the tool |
| #1588/#1589 scam platforms on Google tools | Alphabet (GOOGL) | 2 | Y | outsider used the tool |
| #1534 phishing group used Gemini | Alphabet (GOOGL) | 2 | Y | named outside group |
| #1210/#1220 model embedded in attackers' malware | GOOGL / BABA | 2 | Y | tool used in attackers' operation (§9) |
| #261 Knightscope robot deployed by SPCA against homeless people | Knightscope (KSCP) | 2 | Y | worked as designed; customer used it harmfully (§8) |
| #587 NYT test of Google, Apple, Amazon, Microsoft image labelling | GOOGL / MSFT … | 3 | Y | multi-company study |
| #102 voice assistants struggle with Black voices | AAPL / AMZN / GOOGL / IBM / MSFT | 3 | Y | multi-company study |
| #12 vector-embedding bias (word2vec paper) | Alphabet (GOOGL) | 3 | Y | research paper, no event |
| #1393 Woolworths "Olive" chatbot | Alphabet (GOOGL) | — | N | Google is a supplier; deployer Woolworths is ASX-listed |
| #574 G/O Media AI articles | Alphabet (GOOGL) | — | N | link to Google doubtful |
| #189 UK DWP fraud algorithm | UiPath (PATH) | — | N | weak / indirect link |
| #1304 Whirlpool AI-altered ad | Omnicom (OMC) / Whirlpool (WHR) | ? | ? | judgment call (§6); coders decide |
| #1528 TruDi navigation (same event as #1436) | Integra (IART) | 1 | Y | `duplicate_of = 1436` |

> **All incidents listed in this appendix are excluded from every κ calculation**, because
> coders may remember the manual's answer. `step5_kappa.py` drops them automatically; state
> this exclusion in the paper's methods.

## Appendix B — Version history

| version | date | change | reason |
|---|---|---|---|
| v1 | 2026-09-24 | initial manual (Types 1–3, ticker, duplicates, dates, keep) | — |
| v2 | 2026-09-25 | added Rules 1–5 (multi-company study → 3; narrow Type 2; supplier malfunction → 1; not at fault → 1; attack on service vs tool in attacker's operation) | pilot rounds 1–2 (κ 0.21, 0.27) showed recurring disagreements |
| v3 | 2026-09-25 | consolidated rewrite; coding order; decision tree; consistency checks; platform/venue rule (§11); UNCERTAIN flag replaces "default to Type 2"; AI-coder + human-validation procedure (§19) | pilot round 3 (κ −0.14) showed "Type 2 = not their fault" and "N = not responsible" misreadings persisted |
