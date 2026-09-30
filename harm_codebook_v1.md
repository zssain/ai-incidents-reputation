# Harm-type codebook v1 (frozen before any returns are computed)

Unit: each unique incident among the final events (for merged events, the retained earliest
incident). Codes are mapped back to every ticker sharing the incident.

Fields
- harm_primary: exactly one of SAFE, FAIR, PRIV, DECEPT, SEC, ACCT
- harm_secondary: one other code, or blank
- reason: one factual sentence

Question: What kind of harm does the news report say the firm's AI caused or risked?
Code the harm itself, not the technology.

SAFE   - Physical or psychological harm: crashes, injuries, deaths, medical or safety errors,
         weapons misfires, content pushing self-harm or suicide, threats to a user.
         Examples: Autopilot crash; robot injures worker; chatbot encourages self-harm.
FAIR   - Discrimination or bias: unequal treatment or performance by race, gender, age,
         disability, religion, region; stereotyped outputs.
         Examples: hiring tool penalizes women; photo labeling of Black people.
PRIV   - Privacy or surveillance: collecting, storing, exposing or inferring personal data
         without consent; biometrics; tracking; leaks of personal information.
         Examples: facial data collected without consent; Echo sends private conversation.
DECEPT - False or misleading content: hallucination, misinformation, defamation, deepfakes,
         fabricated citations or quotes, misleading claims about AI capability.
         Examples: Bard demo error; chatbot falsely accuses a journalist.
SEC    - Security failure: vulnerabilities, jailbreaks, prompt injection, unauthorized system
         access, model escaping constraints, malicious code in AI tools.
         Examples: prompt injection reveals system prompt; Copilot audit-log bypass.
ACCT   - Accountability, economic or rights harms: opaque automated decisions (firings,
         deactivations, claim denials), worker exploitation, copyright/IP, anti-competitive
         self-preferencing, algorithmic price coordination, moderation that wrongly removes
         lawful speech.
         Examples: automated driver deactivation; training on pirated books; search rigged
         to favor own products.

Decision rules
1. Pick the harm the headline and first reports emphasize.
2. If two harms are equally emphasized, use this priority for harm_primary:
   SAFE > FAIR > PRIV > SEC > DECEPT > ACCT, and put the other in harm_secondary.
3. Wrongful content removal or account bans -> ACCT, unless the removal is explicitly biased
   against a protected group (-> FAIR).
4. Failure to remove harmful content -> code the harm of that content
   (e.g. hate speech inciting violence -> SAFE; scam ads -> DECEPT).
5. Privacy leak caused by a security flaw -> PRIV if personal data was exposed; otherwise SEC.
6. If genuinely unsure, start reason with "UNCERTAIN:".

Procedure: an LLM coder codes all unique incidents under this frozen codebook and a fixed
prompt. The author independently codes a random sample of 25 without seeing the AI's codes;
agreement (raw %, kappa, PABAK) is reported; disagreements and UNCERTAIN rows are adjudicated
under the codebook and logged. All before any returns are computed.
