# Iris — Jobs to Be Done Framework

*Last updated: April 2026*

---

## The User

**Who:** The primary wedding planner — almost always the bride. One person carrying the majority of planning decisions and communication.

**When they come to Iris:**
- Day one of engagement (ideal — longest subscription window, most time to help)
- Mid-planning, overwhelmed — hitting a wall on vendors, decisions piling up, behind on timeline

**What they have in common regardless of entry point:** They are making high-stakes decisions with incomplete information, under time pressure, often without professional support, and usually while working a full-time job.

---

## The Main Job

> **"Help me get my wedding planned without it consuming my life."**

This is the job. Everything else is a supporting job or a struggling moment underneath it.

The bride is not hiring Iris to learn about weddings. She's hiring Iris to carry the load so she doesn't have to carry it alone.

---

## Supporting Jobs (in priority order)

### 1. "Help me figure out where to start"
The first week of engagement is overwhelming. There are 50 things to do and no obvious order. The bride needs a clear starting point and a sequence she can trust.

**What Iris does:** Planning timeline generator, priority/delegation framework, staged recommendation ("here's what to lock in first and why").

**Success signal:** User leaves the first session knowing exactly what to do next.

---

### 2. "Help me find vendors I can actually trust"
Not just a list — a recommendation. "Here are three photographers who fit your vibe and your budget, and here's why I'd start with this one." The internet gives you 500 options. Iris gives you three.

**What Iris does:** Vendor search filtered by budget, location, and aesthetic. Eventually: shortlist engine with ranked recommendations tied to aesthetic profile.

**Success signal:** User contacts a vendor Iris recommended.

---

### 3. "Help me do the communication I hate"
Reaching out to vendors cold is awkward. Following up feels pushy. Writing a professional email when you've never done this before is stressful. This is work the bride will procrastinate on indefinitely if left alone.

**What Iris does:** First-touch availability email drafted automatically. Eventually: follow-up drafts, "no thank you" emails, response handling.

**Success signal:** User sends an email Iris drafted.

---

### 4. "Help me make decisions without second-guessing myself"
Decision fatigue is the #1 pain point surfaced in user research (Reddit). Every vendor category requires 10+ micro-decisions. The bride needs confidence, not more options.

**What Iris does:** Aesthetic profile (This or That), budget allocation by category, shortlist with recommendation reasoning. Eventually: "here's what I'd do" framing on every recommendation.

**Success signal:** User books a vendor without feeling like they missed something better.

---

### 5. "Help me feel less alone in this"
Planning a wedding is isolating. Partners are often less engaged. Family adds pressure instead of relief. Friends have opinions but not expertise. The bride wants someone in her corner who knows what they're doing and isn't emotionally invested in the outcome.

**What Iris does:** Warm, confident conversational tone. Iris remembers everything. Iris doesn't judge the budget or the guest list. Iris is always available.

**Success signal:** User comes back to Iris proactively, not just when they need something.

---

## The North Star Metric

**Vendors booked through Iris** — specifically vendors where Iris played a direct role in the decision (recommendation) or the outreach (email draft).

This is the metric that proves Iris is doing the job, not just being used. A user who browses and never contacts a vendor hasn't gotten value. A user who books their photographer because Iris found them, recommended them, and drafted the first email — that's the product working.

---

## What Makes a User Stop

In order of likelihood:

1. **Recommendations don't feel relevant** — wrong budget range, wrong aesthetic, wrong location. If Iris doesn't feel like she knows the user, the user stops trusting her.

2. **The tone feels robotic or generic** — "I hope this message finds you well." One AI-sounding response breaks the illusion. The bride needs to feel like she's talking to a smart friend, not a chatbot.

3. **Nothing actually happens** — if the user has conversations but never takes action (contacts a vendor, books something), Iris isn't doing the job. She's just another app on their phone.

4. **The email drafts don't feel like them** — if the bride reads the draft and thinks "I would never say this," she won't send it and won't ask for another one.

5. **They forget Iris exists** — no proactive touchpoints, no reminders, no reason to come back between planning sessions. Passive tools die quietly.

---

## The Real Vendor Journey

Vendor booking is not linear. The actual lifecycle is:

**Contacted → Responded → Tour/Meeting Scheduled → Toured → Second Look → Negotiating → Booked**

A single category (especially venue) can take weeks or months with multiple back-and-forths. Iris needs to support this — not assume one email leads to a booking. The tracker needs to hold the full story of each vendor relationship, including notes from tours, what was quoted, what the sticking points are, and where things stand at any given moment.

---

## What This Means for What to Build

| Job | Current State | Gap |
|-----|--------------|-----|
| Where to start | Timeline generator ✓ | Needs to be more directive — "do this first" not just a list |
| Find trusted vendors | Search exists ✓ | Missing shortlist/recommendation layer (V2) |
| Communication | First-touch email ✓, no thank you email ✓, vendor tracker ✓ | Missing follow-up drafts, richer status model (toured, negotiating) |
| Make decisions | This or That exists ✓ | Aesthetic data too thin to drive real recommendations yet |
| Feel less alone | Conversational tone ✓, proactive follow-up nudge ✓ | Missing vendor status dashboard — user shouldn't have to ask Iris what's happening |

**Vendor status dashboard (priority for V1):** The user should be able to see at a glance — without asking Iris — where every vendor stands across every category. Contacted, toured, negotiating, booked, passed. This is the command center. Right now it lives as a small sidebar panel; it needs to be a first-class view the user can open anytime.

**The biggest gap right now:** The tracker status model is too simple. "Contacted" and "booked" don't capture the real journey. Toured, second look, and negotiating are real states that matter for knowing what to do next.

**The biggest gap after that:** Nothing brings the user back. Iris is reactive. She answers when asked. The next major unlock is a proactive layer — timeline reminders, follow-up nudges, "you toured Gotham Hall last week, how did it go?" That's what turns a tool into a planner.

---

## V1 Definition (Streamlit prototype)

Iris does the job if:
- User completes onboarding and gets a planning timeline
- User finds at least one vendor Iris recommended
- User sends at least one email Iris drafted
- User comes back at least once after their first session

## V2 Definition (Next.js launch)

Iris does the job if:
- User books at least one vendor with Iris's direct involvement
- Iris proactively surfaces the right next step without being asked
- User describes Iris as "my wedding planner" not "an app I use"
