# Iris — Product Backlog

*Last updated: April 2026*

## Bugs
- [ ] **Vendor contact finding is unreliable** — shortlist engine changed how URLs are passed to draft_vendor_email; Firecrawl is returning fabricated URLs for some venues and nothing for others. Yesterday it worked reliably. Need to debug the URL pipeline from shortlist → contact finder → email draft and restore previous accuracy. Priority: high, fix before next tester session.

## V1 Remaining
- [ ] Wait for tester feedback — two testers have the link, no feedback yet

## V2 — Next.js Launch

### Aesthetic & Vendor Discovery (the big redesign)
- [ ] **Pinterest intake** — Firecrawl scrapes user's Pinterest wedding board; Claude analyzes pins to build real aesthetic profile (photo style, venue type, color palette, formality, floral density). Replaces stock photo This or That entirely.
- [ ] **Instagram vendor game** — per category, Iris pulls Instagram grids of top vendor candidates and runs a real This or That using actual vendor work. Venue format: tournament bracket (8 → top 3). Game IS vendor selection — shortlist is set by the end.
- [ ] Full flow: Pinterest → aesthetic profile → vendor search → Instagram game → shortlist → email

### Communication
- [ ] Follow-up email drafts — after first-touch, Iris drafts a follow-up if no response
- [ ] Gmail OAuth — inbox scanning to auto-detect vendor responses, update tracker automatically

### People Management
- [ ] Guest SMS number (Twilio) — dedicated number guests text instead of the couple; Iris answers from wedding profile, flags unknowns to the planner
- [ ] Bride-facing people scripts — language for hard conversations (mom, FMIL, disengaged partner)

### Proactive Layer
- [ ] AI pre-wedding confirmation calls (Bland.ai or Vapi) — Iris calls vendors 2 weeks out to confirm all details
- [ ] Streak / gamification — weekly streak for real planning actions (send an email, update a vendor status), not vanity opens

### Infrastructure
- [ ] Next.js migration
- [ ] Row-level security (RLS) on Supabase tables
- [ ] Contract summarizer — paste in a vendor contract, Iris flags key clauses and red flags
- [ ] Budget tracker — updates automatically as vendors are booked

## Completed
- [x] Conversational onboarding (names, planning stage, wedding basics, budget, delegation)
- [x] Budget allocation walkthrough in session 1
- [x] Planning timeline generator (saved to Supabase, not regenerated on reload)
- [x] Tavily vendor search with agentic tool loop
- [x] Shortlist engine — top 3 picks with profile-specific reasoning per category
- [x] Firecrawl contact finder (homepage → /contact → /contact-us → Tavily fallback)
- [x] First-touch vendor email draft (auto-logs vendor to tracker)
- [x] No thank you email draft (auto-marks vendor as passed)
- [x] Vendor tracker with full status lifecycle (researching → contacted → responded → meeting_scheduled → toured → second_look → negotiating → booked / passed / unavailable)
- [x] Vendor dashboard tab (summary bar, by-category cards, inline status update)
- [x] Proactive follow-up nudge (5 days no response; 3 days post-tour)
- [x] Partner name saved and used in email sign-offs
- [x] LGBTQ+ inclusive — no gendered assumptions
- [x] Test mode (?tester=name URL param)
- [x] Email auth (sign up / sign in / sign out)
- [x] Supabase persistent sessions
- [x] Streamlit Cloud deploy (auto-deploys on push to main)
- [x] JOBS_TO_BE_DONE.md framework
