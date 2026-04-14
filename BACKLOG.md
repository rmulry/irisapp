# Iris — Product Backlog

## In Progress
- [ ] Vendor search via Tavily (live)
- [ ] Supabase persistent sessions (live)
- [ ] Email auth / account creation (live)

## Up Next
- [ ] Profile extraction — parse structured data (date, budget, city, guest count) from onboarding conversation and save to wedding_profiles table
- [ ] Deploy to Streamlit Cloud so other users can access it

## Backlog

### Features
- [ ] Wedding timeline generator — after onboarding, Iris generates a full end-to-end planning timeline based on wedding date, including optional pre-wedding events (engagement party, bridal shower, bachelorette, rehearsal dinner). Each milestone has a recommended completion date and is dynamically ordered by urgency.
- [ ] Pinterest board integration — OAuth connection to read couple's board and infer aesthetic automatically (V2)
- [ ] Optional inspo image upload — let users upload 1-5 inspiration photos during onboarding; Iris analyzes the aesthetic and factors it into recommendations
- [ ] Vendor email draft generator — Iris writes a personalized inquiry email to a vendor; user reviews and sends
- [ ] Gmail OAuth — send vendor emails directly from the user's own account
- [ ] Contract summarizer — paste in a vendor contract, Iris flags key clauses and red flags
- [ ] Budget tracker — updates automatically as vendors are booked
- [ ] Proactive notifications — daily job that checks planning progress and surfaces the right nudge at the right time
- [ ] Vendor response tracker — tracks who replied, who didn't, drafts follow-ups

### Infrastructure
- [ ] User auth email confirmation flow
- [ ] Row-level security (RLS) on Supabase tables
- [ ] Switch from Streamlit to Next.js for public launch

## Completed
- [x] Onboarding conversation (MVP)
- [x] Supabase schema and session persistence
- [x] Tavily vendor search with agentic tool loop
- [x] Email auth (sign up / sign in / sign out)
- [x] Vendor search (Tavily) — Google Places on backlog for V2
