"""
Iris — AI Wedding Planning Assistant
MVP: Onboarding conversation that builds a wedding profile
"""

import os
import json
from datetime import date
import streamlit as st
from anthropic import Anthropic
from supabase import create_client
from tavily import TavilyClient
from firecrawl import FirecrawlApp
from dotenv import load_dotenv
from this_or_that import CATEGORIES, VENDOR_CATEGORIES, get_filtered_categories, preload_images, build_extraction_prompt

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), ".env"))

client = Anthropic()
supabase = create_client(os.environ["SUPABASE_URL"], os.environ["SUPABASE_ANON_KEY"])
tavily = TavilyClient(api_key=os.environ["TAVILY_API_KEY"])
firecrawl = FirecrawlApp(api_key=os.environ["FIRECRAWL_API_KEY"])

TODAY = date.today().strftime("%B %d, %Y")

SYSTEM_PROMPT = f"""Today's date is {TODAY}. Always use this date for any timeline calculations.

You are Iris, a warm and confident AI wedding planning assistant.
Your job right now is to have a natural onboarding conversation to understand this couple
and build their wedding profile. You are not a form — you are a friend who happens to know
everything about weddings.

Ask questions conversationally, one or two at a time. Don't overwhelm.
Be warm, occasionally playful, and always reassuring. When someone seems stressed,
acknowledge it before moving on.

After asking for names, ask where they are in the planning process. Adapt your approach based on their answer:
- Just got engaged → start from the very beginning, build everything fresh
- A few months in → first ask what's already booked or decided before making recommendations
- Further along / overwhelmed → start by taking inventory of what exists, identify gaps, bring calm and order

You need to learn (in a natural conversational order, not as a list):

STAGE & EXISTING BOOKINGS (if not starting from scratch):
- What's already booked or decided? Never recommend something they already have.

THE BASICS:
- Their first name (and their partner's name)
- Phone number (so vendor emails can include real contact info)
- Wedding date and location (city/state)
- Approximate guest count
- Total budget

BUDGET ALLOCATION (do this immediately after they give you a total budget):
Once you have their total budget, walk them through how you'd split it across the main
categories — don't wait until vendor search to do this math. Make it feel like a planner
pulling out a notepad and showing them the picture.

Use these standard allocations to calculate:
- Venue + catering: 40-50% (the biggest line item — often non-negotiable)
- Photography: 10-12%
- Florals: 8-10%
- Videography: 6-8%
- Music (DJ or band): 4-5% (band runs higher, 10-15%)
- Hair + makeup: 2-3%
- Cake: 1-2%
- Invitations + stationery: 2-3%
- Transportation: 2%
- Remaining: attire, favors, day-of coordinator, misc

Show them the top 5-6 line items with specific dollar amounts based on their number.
Then ask: "Is there anything you want to put more toward — or anything you'd rather save on?"
Their answer adjusts your recommendations throughout the rest of planning.
Always use "dollars" not "$" to avoid formatting issues.
Do this math in the conversation — never say "depending on your budget" when you have the number.

THE DEEPER STUFF (what separates a real planner from a checklist):
- Who's involved in decisions — is it just the two of you, or are family members or financial
  contributors who expect a say? This changes everything about how Iris helps.
- What part of planning are you most dreading? (This tells Iris where to carry the most weight.)
- Any prior commitments — have you already told people a date, promised a venue to family,
  or accepted money with strings attached?

CEREMONY:
- Ceremony type (religious, civil, cultural traditions to incorporate)

DELEGATION:
- What would they happily hand off and not think about again? Common answers: cake, florals,
  invitations, transportation, linens, stationery. Make clear that Iris will handle these
  and only check in before anything is booked.

The delegation question is important — it tells you where to focus their energy and what you
can take off their plate entirely.

Once you have all of this, summarize their wedding profile back to them warmly and clearly,
including which categories they've delegated to Iris. End the summary with the exact phrase:
"Your Iris profile is ready."

Then tell them exactly what to focus on first and why — but DO NOT search yet. Present the
recommendation and ask for a green light. For example:
"You're 10 months out, which means venue is the first thing we need to lock in — it sets
your date, guest count, and almost every other vendor. Ready for me to find options?"

Wait for their confirmation before using the search tool. Once they say yes, search and
present results. Iris leads, but does not overwhelm.

VENDOR SEARCH:
You have a search_vendors tool. Use it only when:
- The user has explicitly said yes, they're ready to look
- The user directly asks to find or see vendors for a category
Never search automatically after onboarding. Always get a green light first.

When you get search results back, they are already filtered to the best 1-3 matches with
reasoning specific to this couple. Present them as your recommendations — not a list of options.
Lead with your top pick ("I'd start with X — here's why"), then mention the others as alternatives.
Add your voice: be warm, be direct, tell them what you'd do.
Always end by offering to draft the inquiry email for the top pick immediately.

If search results are thin or off-topic, acknowledge it and suggest the user search
Instagram hashtags (e.g. #[city]weddingphotographer) for additional options.

Never make up vendor names. Only present vendors that appear in actual search results.

TONE WHEN REDIRECTING:
Never apologize or say "I should have" or "I'm sorry." Just be confident and helpful.
If you can't do something, pivot immediately to what you CAN do.

BUDGET GUIDANCE:
Always reference their specific budget allocation in every vendor recommendation — never use
generic ranges. If their total budget is 60,000 dollars and they haven't adjusted photography,
say "your photography budget is approx. 6,000-7,200 dollars" — always calculated from their number.
Same for wedding date — always calculate exactly how many months away it is. Never say
"depending on your timeline."
Never use dollar signs ($) in your responses — write out "dollars" or use "approx. 6,000 dollars"
to avoid formatting issues.

Never mention The Knot, WeddingWire, or Zola.

VENDOR EMAIL DRAFTING & TRACKING:
After presenting vendor options, always offer to draft the inquiry email.
Use the draft_vendor_email tool when the user wants to reach out to a specific vendor.
After drafting, tell them to copy it and send from their own email — the contact info is in the draft.
Never tell the user to "find the website" or "look up the contact" themselves. The contact line in the
email draft always has what they need — a direct email or a link to the contact form.
Then ask: who else on the list do you want to reach out to?

When the user tells you a vendor responded, use update_vendor_status to log it.
When they schedule a tour or meeting, update to "meeting_scheduled".
When they complete a tour or site visit, update to "toured".
When they want to go back for a second look or revisit a vendor, update to "second_look".
When they're actively negotiating price or contract terms, update to "negotiating".
When they say a vendor is unavailable, update to "unavailable".
When they book someone, update to "booked" and offer to draft "no thank you" emails to others in that category.
When they decide to pass on a vendor, update to "passed".
If they mention a price quoted, capture it in quoted_price.
Always acknowledge the update conversationally — don't just silently call the tool.
After a tour, always ask how it went and whether they want to move forward, go back for a second look, or keep looking.

Keep responses concise — 2-4 sentences max unless summarizing the profile or presenting vendors.
Never ask more than two questions at once.
Start by warmly welcoming them and asking for their name and their partner's name — this should always be the very first thing you ask. Use their names naturally throughout the conversation from that point on.

INCLUSIVITY: Never assume gender, sexuality, or relationship structure. Do not use "bride and groom", "husband and wife", "bride", or any gendered terms unless the user uses them first. Use "you and [partner's name]", "the two of you", "the couple", or "your wedding" instead. Iris is welcoming to all couples and all identities."""

TOOLS = [
    {
        "name": "search_vendors",
        "description": "Search for real local wedding vendors. Use this when the user is ready to see options for a vendor category, or when recommending next steps after onboarding.",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Search query, e.g. 'wedding photographers in Austin Texas' or 'outdoor wedding venues Nashville TN'"
                },
                "category": {
                    "type": "string",
                    "description": "Vendor category, e.g. 'photographer', 'venue', 'florist', 'DJ', 'caterer'"
                }
            },
            "required": ["query", "category"]
        }
    },
    {
        "name": "draft_vendor_email",
        "description": "Draft a personalized inquiry email to a wedding vendor. Use this when the user wants to reach out to a specific vendor.",
        "input_schema": {
            "type": "object",
            "properties": {
                "vendor_name": {
                    "type": "string",
                    "description": "Name of the vendor or business"
                },
                "vendor_category": {
                    "type": "string",
                    "description": "Type of vendor, e.g. 'photographer', 'venue', 'florist', 'DJ'"
                },
                "vendor_url": {
                    "type": "string",
                    "description": "Vendor website URL if available"
                }
            },
            "required": ["vendor_name", "vendor_category"]
        }
    },
    {
        "name": "draft_no_thank_you_email",
        "description": "Draft a polite no thank you email to a vendor the user has decided not to book. Use this when the user books one vendor and wants to let others in the same category know.",
        "input_schema": {
            "type": "object",
            "properties": {
                "vendor_name": {
                    "type": "string",
                    "description": "Name of the vendor to decline"
                },
                "vendor_category": {
                    "type": "string",
                    "description": "Type of vendor, e.g. 'photographer', 'venue'"
                }
            },
            "required": ["vendor_name", "vendor_category"]
        }
    },
    {
        "name": "update_vendor_status",
        "description": "Update the status of a vendor the user has been tracking. Use this when the user reports back on a vendor response, books someone, or decides to pass.",
        "input_schema": {
            "type": "object",
            "properties": {
                "vendor_name": {
                    "type": "string",
                    "description": "Name of the vendor to update"
                },
                "status": {
                    "type": "string",
                    "enum": ["researching", "contacted", "responded", "meeting_scheduled", "toured", "second_look", "negotiating", "booked", "passed", "unavailable"],
                    "description": "New status for the vendor"
                },
                "notes": {
                    "type": "string",
                    "description": "Notes about their response, what they said, etc."
                },
                "quoted_price": {
                    "type": "number",
                    "description": "Price quoted by the vendor if they provided one"
                }
            },
            "required": ["vendor_name", "status"]
        }
    }
]



# ── Supabase helpers ───────────────────────────────────────────────────────────

def log_vendor(user_id: str, name: str, category: str, url: str,
               contact_email: str, contact_form_url: str):
    """Insert or update a vendor record. If vendor already exists, just update contacted_at."""
    existing = supabase.table("vendors") \
        .select("id") \
        .eq("session_id", user_id) \
        .ilike("name", name) \
        .execute()
    if existing.data:
        return  # Already logged
    supabase.table("vendors").insert({
        "session_id": user_id,
        "name": name,
        "category": category,
        "url": url,
        "contact_email": contact_email,
        "contact_form_url": contact_form_url,
        "status": "contacted",
        "contacted_at": date.today().isoformat(),
    }).execute()


def load_vendors(user_id: str) -> list:
    result = supabase.table("vendors") \
        .select("*") \
        .eq("session_id", user_id) \
        .order("created_at") \
        .execute()
    return result.data or []


def update_vendor(user_id: str, name: str, status: str,
                  notes: str = None, quoted_price: float = None):
    update = {"status": status}
    if notes:
        update["notes"] = notes
    if quoted_price:
        update["quoted_price"] = quoted_price
    if status == "responded":
        update["responded_at"] = date.today().isoformat()
    if status == "toured":
        update["toured_at"] = date.today().isoformat()
    if status == "booked":
        update["booked_at"] = date.today().isoformat()
    supabase.table("vendors") \
        .update(update) \
        .eq("session_id", user_id) \
        .ilike("name", name) \
        .execute()


def load_messages(user_id: str) -> list:
    result = supabase.table("messages") \
        .select("role, content") \
        .eq("session_id", user_id) \
        .order("created_at") \
        .execute()
    return result.data or []


def save_message(user_id: str, role: str, content: str):
    supabase.table("messages").insert({
        "session_id": user_id,
        "role": role,
        "content": content,
    }).execute()


def ensure_session(user_id: str):
    supabase.table("sessions").upsert({"id": user_id}).execute()


def get_profile_complete(messages: list) -> bool:
    for m in messages:
        if m["role"] == "assistant" and "Your Iris profile is ready." in m["content"]:
            return True
    return False


def profile_already_saved(user_id: str) -> bool:
    result = supabase.table("wedding_profiles") \
        .select("session_id") \
        .eq("session_id", user_id) \
        .execute()
    return len(result.data) > 0


def timeline_already_saved(user_id: str) -> bool:
    result = supabase.table("wedding_profiles") \
        .select("timeline") \
        .eq("session_id", user_id) \
        .execute()
    return bool(result.data and result.data[0].get("timeline"))


def load_timeline(user_id: str) -> dict | None:
    result = supabase.table("wedding_profiles") \
        .select("timeline") \
        .eq("session_id", user_id) \
        .execute()
    if result.data and result.data[0].get("timeline"):
        return result.data[0]["timeline"]
    return None


def generate_and_save_timeline(user_id: str, messages: list):
    conversation = "\n".join(
        f"{m['role'].upper()}: {m['content']}" for m in messages
    )
    prompt = f"""Based on this wedding planning conversation, generate a complete planning timeline.
Today's date is {TODAY}.

Conversation:
{conversation}

Generate a full end-to-end wedding planning timeline. Return ONLY valid JSON:
{{
  "wedding_date": "YYYY-MM-DD or null",
  "months_until_wedding": number or null,
  "milestones": [
    {{
      "category": "Venue",
      "task": "Book wedding venue",
      "due_date": "YYYY-MM-DD",
      "urgency": "urgent|upcoming|future",
      "note": "brief reason this timing matters",
      "delegated": false
    }}
  ],
  "pre_wedding_events": [
    {{
      "event": "Engagement Party",
      "optional": true,
      "suggested_date": "YYYY-MM-DD",
      "note": "brief note"
    }}
  ]
}}

Urgency rules based on today's date:
- urgent: due within 60 days
- upcoming: due within 6 months
- future: due more than 6 months away

Standard lead times from wedding date:
- Venue: book 12-18 months before
- Photographer/videographer: 12 months before
- Band/DJ: 10-12 months before
- Caterer (if separate from venue): 9-12 months before
- Florist: 6-9 months before
- Hair & makeup: 6-9 months before
- Officiant: 6-9 months before
- Cake: 4-6 months before
- Invitations: design 4-5 months before, send 8-10 weeks before
- Transportation: 3-6 months before
- Rehearsal dinner venue: 6 months before

Pre-wedding events to include if relevant (all optional):
- Engagement party: 1-6 months after engagement
- Bridal shower: 1-3 months before wedding
- Bachelorette: 1-3 months before wedding
- Rehearsal dinner: night before wedding

Mark milestones as delegated:true if the user said they want Iris to handle that category.
Order milestones by due_date ascending.
If wedding date is unknown, use placeholder dates relative to "12 months from today"."""

    try:
        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=2000,
            messages=[{"role": "user", "content": prompt}],
        )
        text = response.content[0].text.strip()
        if text.startswith("```"):
            text = text.split("```")[1]
            if text.startswith("json"):
                text = text[4:]
        data = json.loads(text.strip())
        supabase.table("wedding_profiles").upsert({
            "session_id": user_id,
            "timeline": data,
        }).execute()
        return data
    except Exception:
        return None


def extract_and_save_profile(user_id: str, messages: list):
    conversation = "\n".join(
        f"{m['role'].upper()}: {m['content']}" for m in messages
    )
    extraction_prompt = f"""Extract the wedding profile from this conversation and return ONLY valid JSON.
Use null for any field not mentioned.

Conversation:
{conversation}

Return this exact JSON structure:
{{
  "wedding_date": "YYYY-MM-DD or null",
  "city": "city name or null",
  "state": "state name or null",
  "guest_count": number or null,
  "total_budget": number or null,
  "ceremony_type": "description or null",
  "priorities": ["list of top priorities"],
  "dont_cares": ["list of delegated categories"],
  "user_name": "first name of the person planning (not their partner) or null",
  "partner_name": "first name of their partner or null",
  "user_phone": "their phone number or null"
}}"""

    try:
        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=500,
            messages=[{"role": "user", "content": extraction_prompt}],
        )
        import json
        text = response.content[0].text.strip()
        # Strip markdown code fences if present
        if text.startswith("```"):
            text = text.split("```")[1]
            if text.startswith("json"):
                text = text[4:]
        data = json.loads(text.strip())
        supabase.table("wedding_profiles").upsert({
            "session_id": user_id,
            "wedding_date": data.get("wedding_date"),
            "city": data.get("city"),
            "state": data.get("state"),
            "guest_count": data.get("guest_count"),
            "total_budget": data.get("total_budget"),
            "ceremony_type": data.get("ceremony_type"),
            "priorities": data.get("priorities", []),
            "dont_cares": data.get("dont_cares", []),
            "user_name": data.get("user_name"),
            "partner_name": data.get("partner_name"),
            "user_phone": data.get("user_phone"),
            "profile_complete": True,
        }).execute()
    except Exception:
        pass  # Silent fail — don't break the chat


# ── Profile loader ─────────────────────────────────────────────────────────────

def load_wedding_profile(user_id: str) -> dict:
    result = supabase.table("wedding_profiles") \
        .select("wedding_date, city, state, guest_count, total_budget, user_name, partner_name, user_phone, priorities, aesthetic_profile") \
        .eq("session_id", user_id) \
        .execute()
    return result.data[0] if result.data else {}


# ── Vendor email draft ─────────────────────────────────────────────────────────

BUDGET_PCTS = {
    "photographer": 0.11, "videographer": 0.07, "venue": 0.45,
    "florist": 0.09, "dj": 0.045, "band": 0.10, "caterer": 0.45,
    "hair": 0.025, "makeup": 0.025, "cake": 0.015,
    "officiant": 0.01, "transportation": 0.02,
}

import re as _re
EMAIL_PATTERN = _re.compile(r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}")
JUNK_DOMAINS = {"example.com", "sentry.io", "wixpress.com", "squarespace.com",
                "wordpress.com", "googleapis.com", "schema.org"}


PHONE_PATTERN = _re.compile(r'\(?\d{3}\)?[\s.\-]?\d{3}[\s.\-]?\d{4}')

def lookup_vendor_contact_cache(name: str) -> dict | None:
    """Check the global vendor_contacts table before hitting Tavily/Firecrawl."""
    from datetime import date, timedelta
    try:
        result = supabase.table("vendor_contacts") \
            .select("contact_email, contact_form_url, phone, url, last_verified") \
            .ilike("name", name) \
            .limit(1) \
            .execute()
        if not result.data:
            return None
        row = result.data[0]
        # Treat as stale after 60 days
        last_verified = row.get("last_verified")
        if last_verified:
            age = date.today() - date.fromisoformat(str(last_verified))
            if age.days > 60:
                return None
        return row
    except Exception:
        return None


def save_vendor_contact_cache(name: str, url: str, contact_email: str,
                               contact_form_url: str, phone: str):
    """Upsert a vendor contact into the global vendor_contacts table."""
    try:
        existing = supabase.table("vendor_contacts") \
            .select("id") \
            .ilike("name", name) \
            .limit(1) \
            .execute()
        data = {
            "name": name,
            "url": url or "",
            "contact_email": contact_email or "",
            "contact_form_url": contact_form_url or "",
            "phone": phone or "",
            "last_verified": date.today().isoformat(),
        }
        if existing.data:
            supabase.table("vendor_contacts") \
                .update(data) \
                .eq("id", existing.data[0]["id"]) \
                .execute()
        else:
            supabase.table("vendor_contacts").insert(data).execute()
    except Exception:
        pass


def find_vendor_contact(vendor_url: str, vendor_name: str = "") -> tuple:
    """Returns (email_or_None, contact_url_or_None, phone_or_None)."""

    # ── Check global vendor contacts cache first ───────────────────────────────
    if vendor_name:
        cached = lookup_vendor_contact_cache(vendor_name)
        if cached:
            return (
                cached.get("contact_email") or None,
                cached.get("contact_form_url") or None,
                cached.get("phone") or None,
            )

    def clean_emails(text: str) -> list:
        found = EMAIL_PATTERN.findall(text)
        return [e for e in found if e.split("@")[-1].lower() not in JUNK_DOMAINS]

    def clean_phones(text: str) -> list:
        return PHONE_PATTERN.findall(text)

    def scrape(url: str) -> str:
        try:
            result = firecrawl.scrape_url(url, formats=["markdown"])
            return result.get("markdown", "") or ""
        except Exception:
            return ""

    def extract_contact_links(content: str) -> list:
        """Pull any contact/inquiry/booking/event URLs out of scraped markdown."""
        CONTACT_KEYWORDS = ["contact", "inquiry", "enquiry", "event", "booking",
                            "request", "party_request", "quote", "book"]
        urls = _re.findall(r'https?://[^\s\)\]\"\']+', content)
        return [u for u in urls if any(kw in u.lower() for kw in CONTACT_KEYWORDS)
                and not is_aggregator(u)]

    # ── Step 1: Tavily search for the contact page directly ────────────────────
    # Search engines already know where each venue's inquiry form lives.
    # This handles cases like Gotham Hall (tripleseat.com) where the form
    # is on a completely different domain than the main website.
    def cache_and_return(email, form_url, phone):
        save_vendor_contact_cache(vendor_name, vendor_url, email, form_url, phone)
        return email, form_url, phone

    contact_page_url = None
    try:
        results = tavily.search(
            query=f"{vendor_name} wedding event inquiry contact form",
            max_results=7,
            search_depth="advanced",
        )
        for r in results.get("results", []):
            url = r.get("url", "")
            content = r.get("content", "") or ""
            if not url or is_aggregator(url):
                continue
            url_lower = url.lower()
            is_contact_page = any(kw in url_lower for kw in
                ["contact", "inquiry", "enquiry", "event-inquiry", "party_request",
                 "booking", "request", "quote", "book-event"])
            emails = clean_emails(content)
            phones = clean_phones(content)
            if emails:
                return cache_and_return(emails[0], url if is_contact_page else None, phones[0] if phones else None)
            if is_contact_page and not contact_page_url:
                contact_page_url = url
    except Exception:
        pass

    if contact_page_url:
        content = scrape(contact_page_url)
        emails = clean_emails(content)
        phones = clean_phones(content)
        return cache_and_return(
            emails[0] if emails else None,
            contact_page_url,
            phones[0] if phones else None,
        )

    # ── Step 2: Firecrawl the vendor homepage ──────────────────────────────────
    from urllib.parse import urlparse

    if not vendor_url and vendor_name:
        vendor_url = find_official_url(vendor_name) or ""
    if vendor_url and is_aggregator(vendor_url):
        vendor_url = find_official_url(vendor_name) or vendor_url

    if vendor_url:
        parsed = urlparse(vendor_url)
        base_url = f"{parsed.scheme}://{parsed.netloc}"
        if base_url and base_url != "://":
            content = scrape(base_url)
            emails = clean_emails(content)
            phones = clean_phones(content)
            if emails:
                return cache_and_return(emails[0], None, phones[0] if phones else None)

            # Look for contact/inquiry links embedded in the homepage
            links = extract_contact_links(content)
            if links:
                contact_content = scrape(links[0])
                emails = clean_emails(contact_content)
                phones = clean_phones(contact_content)
                return cache_and_return(
                    emails[0] if emails else None,
                    links[0],
                    phones[0] if phones else None,
                )

            # Try /contact and /event-inquiry
            for path in ["/contact", "/event-inquiry", "/contact-us", "/inquire"]:
                page = scrape(base_url + path)
                if page:
                    emails = clean_emails(page)
                    phones = clean_phones(page)
                    return cache_and_return(
                        emails[0] if emails else None,
                        base_url + path,
                        phones[0] if phones else None,
                    )

    return None, None, None


def draft_no_thank_you_email(vendor_name: str, vendor_category: str, user_id: str) -> str:
    profile = load_wedding_profile(user_id)
    user_name = profile.get("user_name") or "your name"
    partner_name = profile.get("partner_name") or ""
    sign_off = f"{user_name} & {partner_name}" if partner_name else user_name
    user_phone = profile.get("user_phone") or ""

    prompt = f"""Draft a short, warm "no thank you" email to a wedding vendor we've decided not to book.

Vendor: {vendor_name}
Vendor type: {vendor_category}
Sender name: {sign_off}

Rules:
- Warm and appreciative but brief — under 75 words
- Don't over-explain or apologize excessively
- Don't mention who we booked instead
- Sound like a real person, not a form letter
- No words like: genuinely, truly, delighted, pleased
- Sign off with the sender's real name

Format exactly as:
Subject: [subject line]

[email body]"""

    try:
        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=300,
            messages=[{"role": "user", "content": prompt}],
        )
        email_text = response.content[0].text.strip()
        try:
            update_vendor(user_id, vendor_name, "passed")
        except Exception:
            pass
        return f"IRIS_EMAIL_DRAFT_START\n{email_text}\nIRIS_EMAIL_DRAFT_END"
    except Exception as e:
        return f"Could not draft email: {str(e)}"


def draft_vendor_email(vendor_name: str, vendor_category: str, vendor_url: str, user_id: str) -> str:
    profile = load_wedding_profile(user_id)
    wedding_date = profile.get("wedding_date", "")
    guest_count = profile.get("guest_count", "")
    user_name = profile.get("user_name") or "your name"
    partner_name = profile.get("partner_name") or ""
    sign_off = f"{user_name} & {partner_name}" if partner_name else user_name
    user_phone = profile.get("user_phone") or ""

    # Look up the resolved URL from cache — more reliable than what Iris passes
    # after it's been through the shortlist Claude call
    cache = st.session_state.get("vendor_url_cache", {})
    name_lower = vendor_name.lower()
    cached_url = cache.get(name_lower)
    if not cached_url:
        # Fuzzy match: find any cache key that contains the vendor name or vice versa
        for key, val in cache.items():
            if name_lower in key or key in name_lower:
                cached_url = val
                break
    if cached_url:
        vendor_url = cached_url

    # Find contact info by crawling the vendor's site
    contact_email, contact_form_url, vendor_phone = find_vendor_contact(vendor_url, vendor_name)

    contact_line = ""
    if contact_email:
        contact_line = f"\n\nSend to: {contact_email}"
    elif contact_form_url:
        contact_line = f"\n\nNo email found — paste this into their contact form: {contact_form_url}"
    else:
        contact_line = f"\n\nNo email found — search '{vendor_name} contact' to find their inquiry form."

    if vendor_phone:
        contact_line += f"\nPhone: {vendor_phone}"

    prompt = f"""Draft a short, casual first-touch email to a wedding vendor checking availability.

Vendor: {vendor_name}
Vendor type: {vendor_category}
Wedding date: {wedding_date}
Guest count: {guest_count}
Sender name: {sign_off}
Sender phone: {user_phone if user_phone else "not provided"}

Rules:
- Sound like a real person, not a business letter
- No bullet points. Flowing sentences only.
- No words like: genuinely, truly, excited, thrilled, delighted, reach out, celebration, inquire, pleased
- No "I hope this finds you well" or any filler opener
- Keep it simple: mention the date and guest count, ask if they're available, and ask what the next step is if they are
- Do NOT ask about pricing, packages, or logistics — this is just a first check-in
- Keep it under 100 words
- Sign off with the sender's real name
- If a phone number is provided, include it in the sign-off

Format exactly as:
Subject: [subject line]

[email body]"""

    try:
        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=600,
            messages=[{"role": "user", "content": prompt}],
        )
        email_text = response.content[0].text.strip()
        try:
            log_vendor(user_id, vendor_name, vendor_category, vendor_url,
                       contact_email or "", contact_form_url or "")
        except Exception:
            pass
        return f"IRIS_EMAIL_DRAFT_START\n{email_text}{contact_line}\nIRIS_EMAIL_DRAFT_END"
    except Exception as e:
        return f"Could not draft email: {str(e)}"


# ── Vendor search ──────────────────────────────────────────────────────────────

AGGREGATOR_DOMAINS = {
    "theknot.com", "weddingwire.com", "yelp.com", "zola.com",
    "weddingly.com", "junebugweddings.com", "stylemepretty.com",
    "brides.com", "weddingspot.com", "perfectweddingguide.com",
    "thumbtack.com", "gigsalad.com", "bark.com",
}

def is_aggregator(url: str) -> bool:
    from urllib.parse import urlparse
    domain = urlparse(url).netloc.lower().lstrip("www.")
    return any(agg in domain for agg in AGGREGATOR_DOMAINS)

def find_official_url(vendor_name: str) -> str | None:
    """Find a vendor's official website via targeted Tavily search."""
    try:
        results = tavily.search(
            query=f"{vendor_name} official website",
            max_results=5,
            search_depth="advanced"
        )
        for r in results.get("results", []):
            url = r.get("url", "")
            if url and not is_aggregator(url):
                from urllib.parse import urlparse
                parsed = urlparse(url)
                return f"{parsed.scheme}://{parsed.netloc}"
    except Exception:
        pass
    return None

def build_shortlist(raw_results: str, profile: dict, category: str) -> str:
    """Run a secondary Claude call to pick the best 1-3 vendors with profile-specific reasoning."""
    wedding_date = profile.get("wedding_date", "not set")
    budget = profile.get("total_budget", "not specified")
    city = profile.get("city") or ""
    state = profile.get("state") or ""
    location = f"{city}, {state}".strip(", ") or "not specified"
    aesthetic = profile.get("aesthetic_profile") or {}
    priorities = profile.get("priorities") or []
    user_name = profile.get("user_name", "")

    prompt = f"""You are helping a couple find a wedding {category}.

Their profile:
- Wedding date: {wedding_date}
- Total budget: {budget}
- Location: {location}
- Top priorities: {', '.join(priorities) if priorities else 'not specified'}
- Aesthetic: {json.dumps(aesthetic) if aesthetic else 'not captured yet'}

Here are the raw search results:
{raw_results}

Pick the best 1-3 vendors from these results that genuinely fit this couple. Skip any that are clearly a bad match on budget, location, or style.

For each pick, output exactly this format:

**[Vendor Name]**
[URL]
Why this fits: [2-3 sentences specific to THIS couple — reference their budget range, aesthetic, location, or priorities. Be concrete, not generic. Never say "this vendor is great" — say WHY it fits them specifically.]

After listing the picks, add one final line:
START HERE: [Vendor Name] — [one sentence on why to contact this one first]

Do not invent vendors. Only use vendors from the search results. Do not mention vendors that are a poor fit."""

    try:
        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=800,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.content[0].text.strip()
    except Exception:
        return raw_results


def search_vendors(query: str, category: str, user_id: str = "") -> str:
    try:
        results = tavily.search(query=query, max_results=7, search_depth="advanced")
        items = results.get("results", [])
        if not items:
            return "No results found for this search."
        lines = []
        seen_domains = set()
        for r in items:
            title = r.get("title", "").strip()
            url = r.get("url", "").strip()
            snippet = r.get("content", "").strip()[:300]

            if is_aggregator(url):
                resolved = find_official_url(title)
                if resolved and not is_aggregator(resolved):
                    url = resolved

            from urllib.parse import urlparse
            domain = urlparse(url).netloc
            if domain in seen_domains:
                continue
            seen_domains.add(domain)

            # Cache the resolved URL by vendor name for reliable lookup later
            if "vendor_url_cache" in st.session_state:
                st.session_state.vendor_url_cache[title.lower()] = url

            lines.append(f"**{title}**\n{url}\n{snippet}")

        if not lines:
            return "No results found for this search."

        raw_results = "\n\n---\n\n".join(lines)

        if user_id:
            profile = load_wedding_profile(user_id)
            if profile:
                return build_shortlist(raw_results, profile, category)

        return raw_results
    except Exception as e:
        return f"Search unavailable: {str(e)}"


# ── Agentic chat loop ──────────────────────────────────────────────────────────

def chat(messages: list, current_user_id: str = "") -> str:
    # Work on a local copy so tool-use intermediate steps don't pollute stored messages
    api_messages = list(messages)

    while True:
        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=2048,
            system=SYSTEM_PROMPT,
            tools=TOOLS,
            messages=api_messages,
        )

        if response.stop_reason == "tool_use":
            tool_results = []
            for block in response.content:
                if block.type == "tool_use":
                    if block.name == "search_vendors":
                        result_text = search_vendors(
                            block.input["query"],
                            block.input["category"],
                            current_user_id,
                        )
                        tool_results.append({
                            "type": "tool_result",
                            "tool_use_id": block.id,
                            "content": result_text,
                        })
                    elif block.name == "draft_vendor_email":
                        result_text = draft_vendor_email(
                            block.input["vendor_name"],
                            block.input["vendor_category"],
                            block.input.get("vendor_url", ""),
                            current_user_id,
                        )
                        tool_results.append({
                            "type": "tool_result",
                            "tool_use_id": block.id,
                            "content": result_text,
                        })
                    elif block.name == "draft_no_thank_you_email":
                        result_text = draft_no_thank_you_email(
                            block.input["vendor_name"],
                            block.input["vendor_category"],
                            current_user_id,
                        )
                        tool_results.append({
                            "type": "tool_result",
                            "tool_use_id": block.id,
                            "content": result_text,
                        })
                    elif block.name == "update_vendor_status":
                        try:
                            update_vendor(
                                current_user_id,
                                block.input["vendor_name"],
                                block.input["status"],
                                block.input.get("notes"),
                                block.input.get("quoted_price"),
                            )
                            result_text = f"Updated {block.input['vendor_name']} to {block.input['status']}."
                        except Exception as e:
                            result_text = f"Could not update vendor: {str(e)}"
                        tool_results.append({
                            "type": "tool_result",
                            "tool_use_id": block.id,
                            "content": result_text,
                        })

            # Append assistant turn + tool results and loop
            api_messages.append({"role": "assistant", "content": response.content})
            api_messages.append({"role": "user", "content": tool_results})

        else:
            # Final response — extract text
            for block in response.content:
                if hasattr(block, "text"):
                    return block.text
            return ""


# ── Page config ───────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="Iris — Wedding Planning",
    page_icon="🌸",
    layout="centered",
)

st.markdown("""
<style>
    .main { max-width: 700px; margin: 0 auto; }
    .stChatMessage { padding: 0.5rem 0; }
    h1 { color: #6B4C8A; }
    .iris-tagline { color: #9B7AB8; font-size: 1rem; margin-top: -1rem; margin-bottom: 2rem; }
</style>
""", unsafe_allow_html=True)

st.title("🌸 Iris")
st.markdown('<p class="iris-tagline">Make confident decisions faster.</p>', unsafe_allow_html=True)

# ── Pre-auth session state ────────────────────────────────────────────────────

if "user" not in st.session_state:
    # Try to restore session from Supabase
    try:
        session = supabase.auth.get_session()
        st.session_state.user = session.user if session else None
    except Exception:
        st.session_state.user = None

if "auth_mode" not in st.session_state:
    st.session_state.auth_mode = "signup"

if "planning_stage" not in st.session_state:
    st.session_state.planning_stage = True

# ── Auth screen ───────────────────────────────────────────────────────────────

# TEST MODE: bypass auth using ?tester=name in the URL
TEST_MODE = True

if TEST_MODE and st.session_state.user is None:
    params = st.query_params
    tester = params.get("tester", "").strip().lower().replace(" ", "-")
    if tester:
        test_id = f"test-user-{tester}"
        st.session_state.user = type("User", (), {"id": test_id, "email": f"{tester}@irisplanner.app"})()

if st.session_state.user is None:
    st.markdown("**Create a free account to save your progress.**")
    if st.session_state.auth_mode == "signup":
        email = st.text_input("Email", key="signup_email")
        password = st.text_input("Password (min 6 characters)", type="password", key="signup_password")

        if st.button("Get started", use_container_width=True, type="primary"):
            try:
                result = supabase.auth.sign_up({"email": email, "password": password})
                st.session_state.user = result.user
                st.rerun()
            except Exception:
                st.error("Something went wrong. Try again.")

        if st.button("Already have an account? Sign in", use_container_width=True):
            st.session_state.auth_mode = "login"
            st.rerun()
    else:
        email = st.text_input("Email", key="login_email")
        password = st.text_input("Password", type="password", key="login_password")

        if st.button("Sign in", use_container_width=True, type="primary"):
            try:
                result = supabase.auth.sign_in_with_password({"email": email, "password": password})
                st.session_state.user = result.user
                st.rerun()
            except Exception:
                st.error("Invalid email or password.")

        if st.button("Create an account", use_container_width=True):
            st.session_state.auth_mode = "signup"
            st.rerun()

    st.stop()

# ── Logged in — load session ──────────────────────────────────────────────────

user_id = st.session_state.user.id

if "messages" not in st.session_state:
    ensure_session(user_id)
    st.session_state.messages = load_messages(user_id)

if "profile_complete" not in st.session_state:
    st.session_state.profile_complete = False

if "tot_complete" not in st.session_state:
    st.session_state.tot_complete = False

if "tot_selections" not in st.session_state:
    st.session_state.tot_selections = []

if "tot_cat_idx" not in st.session_state:
    st.session_state.tot_cat_idx = 0

if "tot_pair_idx" not in st.session_state:
    st.session_state.tot_pair_idx = 0

if "user_priorities" not in st.session_state:
    st.session_state.user_priorities = []

if "user_delegated" not in st.session_state:
    st.session_state.user_delegated = []

if "filtered_categories" not in st.session_state:
    st.session_state.filtered_categories = None

if "timeline" not in st.session_state:
    st.session_state.timeline = None

if "vendors" not in st.session_state:
    st.session_state.vendors = None

if "vendor_url_cache" not in st.session_state:
    st.session_state.vendor_url_cache = {}

if "followup_checked" not in st.session_state:
    st.session_state.followup_checked = False

# ── Sign out + Timeline sidebar ───────────────────────────────────────────────

# Load timeline and vendors from DB on return visits
if st.session_state.timeline is None and st.session_state.profile_complete:
    st.session_state.timeline = load_timeline(user_id)

if st.session_state.vendors is None:
    st.session_state.vendors = load_vendors(user_id)

with st.sidebar:
    st.caption(f"Signed in as {st.session_state.user.email}")
    if st.button("Sign out"):
        supabase.auth.sign_out()
        for key in ["user", "messages", "profile_complete", "auth_mode", "timeline",
                    "user_priorities", "user_delegated",
                    "filtered_categories", "tot_complete", "tot_selections",
                    "tot_cat_idx", "tot_pair_idx"]:
            st.session_state.pop(key, None)
        st.rerun()

    timeline = st.session_state.timeline
    if timeline and timeline.get("milestones"):
        st.divider()
        months = timeline.get("months_until_wedding")
        wedding_date = timeline.get("wedding_date", "")
        if months:
            st.markdown(f"**{months} months until your wedding**")
        if wedding_date:
            st.caption(wedding_date)

        st.markdown("**Your Planning Timeline**")
        for m in timeline.get("milestones", []):
            urgency = m.get("urgency", "future")
            icon = "🔴" if urgency == "urgent" else "🟡" if urgency == "upcoming" else "🟢"
            delegated_tag = "  \n*Iris handling*" if m.get("delegated") else ""
            due = m.get("due_date", "")
            st.markdown(f"{icon} **{m['task']}**{delegated_tag}  \n*by {due}*")

        pre = timeline.get("pre_wedding_events", [])
        if pre:
            st.divider()
            st.markdown("**Pre-wedding events**")
            for e in pre:
                optional = " *(optional)*" if e.get("optional") else ""
                suggested = e.get("suggested_date", "TBD")
                st.markdown(f"• {e['event']}{optional}  \n*{suggested}*")


# ── This or That helpers ──────────────────────────────────────────────────────

def extract_and_save_aesthetic(user_id: str, selections: list):
    prompt = build_extraction_prompt(selections)
    try:
        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=600,
            messages=[{"role": "user", "content": prompt}],
        )
        text = response.content[0].text.strip()
        if text.startswith("```"):
            text = text.split("```")[1]
            if text.startswith("json"):
                text = text[4:]
        data = json.loads(text.strip())
        supabase.table("wedding_profiles").upsert({
            "session_id": user_id,
            "aesthetic_profile": data,
        }).execute()
        return data
    except Exception:
        return {}


# ── This or That game (skipped — deprecated in V2) ───────────────────────────

if st.session_state.planning_stage and not st.session_state.tot_complete:
    filtered_cats = st.session_state.filtered_categories or []

    # Skip game entirely if no categories to show
    if not filtered_cats:
        st.session_state.tot_complete = True
        st.rerun()

    preload_images(st.session_state, filtered_cats)

    cat = filtered_cats[st.session_state.tot_cat_idx]
    pair = cat["pairs"][st.session_state.tot_pair_idx]
    total_pairs = sum(len(c["pairs"]) for c in filtered_cats)
    done_pairs = sum(len(filtered_cats[i]["pairs"]) for i in range(st.session_state.tot_cat_idx)) + st.session_state.tot_pair_idx

    st.markdown(f"### {cat['label']}")
    st.caption(cat["instruction"])
    st.progress(done_pairs / total_pairs)
    if st.button("Skip style quiz →", key="skip_tot"):
        st.session_state.tot_complete = True
        st.rerun()

    key_a = f"{cat['name']}_{st.session_state.tot_pair_idx}_a"
    key_b = f"{cat['name']}_{st.session_state.tot_pair_idx}_b"
    img_a = st.session_state["tot_images"].get(key_a, "")
    img_b = st.session_state["tot_images"].get(key_b, "")

    def advance(chosen, rejected, cat, filtered_cats):
        st.session_state.tot_selections.append({
            "category": cat["name"],
            "chosen_label": chosen["label"],
            "chosen_query": chosen["query"],
            "rejected_label": rejected["label"],
            "rejected_query": rejected["query"],
        })
        next_pair = st.session_state.tot_pair_idx + 1
        if next_pair >= len(cat["pairs"]):
            next_cat = st.session_state.tot_cat_idx + 1
            if next_cat >= len(filtered_cats):
                st.session_state.tot_complete = True
                extract_and_save_aesthetic(user_id, st.session_state.tot_selections)
            else:
                st.session_state.tot_cat_idx = next_cat
                st.session_state.tot_pair_idx = 0
        else:
            st.session_state.tot_pair_idx = next_pair

    col1, col2 = st.columns(2)
    with col1:
        if img_a:
            st.image(img_a, use_container_width=True)
        if st.button(pair["a"]["label"], use_container_width=True, type="primary", key="btn_a"):
            advance(pair["a"], pair["b"], cat, filtered_cats)
            st.rerun()
    with col2:
        if img_b:
            st.image(img_b, use_container_width=True)
        if st.button(pair["b"]["label"], use_container_width=True, type="primary", key="btn_b"):
            advance(pair["b"], pair["a"], cat, filtered_cats)
            st.rerun()

    st.stop()

# ── Helpers ───────────────────────────────────────────────────────────────────

STATUS_ICON = {
    "researching": "🔍",
    "contacted": "📤",
    "responded": "💬",
    "meeting_scheduled": "📅",
    "toured": "🏛️",
    "second_look": "👀",
    "negotiating": "🤝",
    "booked": "✅",
    "passed": "❌",
    "unavailable": "🚫",
}

STATUS_LABEL = {
    "researching": "Researching",
    "contacted": "Contacted",
    "responded": "Responded",
    "meeting_scheduled": "Meeting Scheduled",
    "toured": "Toured",
    "second_look": "Second Look",
    "negotiating": "Negotiating",
    "booked": "Booked",
    "passed": "Passed",
    "unavailable": "Unavailable",
}

ACTIVE_STATUSES = {"researching", "contacted", "responded", "meeting_scheduled", "toured", "second_look", "negotiating"}

def get_followup_vendors(vendors: list, days: int = 5) -> list:
    """Return vendors that need a follow-up nudge based on status and elapsed time."""
    from datetime import datetime, timedelta
    overdue = []
    for v in vendors:
        status = v.get("status")
        if status == "contacted":
            ref_date_str = v.get("contacted_at")
            cutoff = date.today() - timedelta(days=days)
        elif status == "toured":
            ref_date_str = v.get("toured_at")
            cutoff = date.today() - timedelta(days=3)
        else:
            continue
        if not ref_date_str:
            continue
        try:
            ref_date = datetime.fromisoformat(str(ref_date_str)).date()
            if ref_date <= cutoff:
                overdue.append(v)
        except Exception:
            pass
    return overdue

def render_message(content: str):
    """Render a message, detecting and styling email drafts specially."""
    if "IRIS_EMAIL_DRAFT_START" in content:
        parts = content.split("IRIS_EMAIL_DRAFT_START")
        before = parts[0].replace("$", r"\$")
        rest = parts[1].split("IRIS_EMAIL_DRAFT_END")
        draft_block = rest[0].strip()
        after = rest[1].replace("$", r"\$") if len(rest) > 1 else ""

        contact_line = ""
        form_url = None
        email_body = draft_block
        for line in draft_block.split("\n"):
            if line.startswith("Send to:"):
                contact_line = line
                email_body = draft_block.replace(line, "").strip()
            elif line.startswith("No email found"):
                import re
                urls = re.findall(r"https?://\S+", line)
                form_url = urls[0] if urls else None
                email_body = draft_block.replace(line, "").strip()
            elif line.startswith("No contact email found"):
                contact_line = line
                email_body = draft_block.replace(line, "").strip()

        if before.strip():
            st.markdown(before)
        if contact_line:
            st.markdown(f"**{contact_line}**")
        st.markdown("**📧 Copy this message:**")
        st.code(email_body, language=None)
        if form_url:
            st.markdown("**No email found — paste this message into their contact form:**")
            st.markdown(f"[Open contact form →]({form_url})")
        if after.strip():
            st.markdown(after)
    else:
        st.markdown(content.replace("$", r"\$"))

# ── Main tabs ─────────────────────────────────────────────────────────────────

tab_chat, tab_vendors = st.tabs(["💬 Chat with Iris", "📊 My Vendors"])

# ── Tab 1: Chat ───────────────────────────────────────────────────────────────

with tab_chat:

    # Proactive follow-up check
    if (st.session_state.messages
            and not st.session_state.followup_checked
            and st.session_state.vendors):
        st.session_state.followup_checked = True
        overdue = get_followup_vendors(st.session_state.vendors)
        if overdue:
            names = [v["name"] for v in overdue]
            if len(names) == 1:
                nudge = f"Hey — you reached out to **{names[0]}** and haven't heard back yet. Want me to draft a follow-up?"
            else:
                listed = ", ".join(names[:-1]) + f" and {names[-1]}"
                nudge = f"Hey — you reached out to **{listed}** and haven't heard back from any of them. Want me to draft follow-ups?"
            save_message(user_id, "assistant", nudge)
            st.session_state.messages.append({"role": "assistant", "content": nudge})

    # Start conversation if empty
    if not st.session_state.messages:
        parts = []
        if st.session_state.user_priorities:
            parts.append(f"Things I want to personally decide: {', '.join(st.session_state.user_priorities)}.")
        if st.session_state.user_delegated:
            parts.append(f"Things I'm happy to hand off to Iris: {', '.join(st.session_state.user_delegated)}.")
        if st.session_state.tot_selections:
            prefs = [f"{s['category']}: chose {s['chosen_label']} over {s['rejected_label']}"
                     for s in st.session_state.tot_selections]
            parts.append("Aesthetic preferences from style quiz: " + ", ".join(prefs) + ".")
        seed = " ".join(parts) if parts else "start"
        with st.spinner(""):
            opening = chat([{"role": "user", "content": seed}], user_id)
        save_message(user_id, "assistant", opening)
        st.session_state.messages.append({"role": "assistant", "content": opening})

    # Render chat history
    for msg in st.session_state.messages:
        with st.chat_message("assistant" if msg["role"] == "assistant" else "user",
                             avatar="🌸" if msg["role"] == "assistant" else "👤"):
            render_message(msg["content"])

    if get_profile_complete(st.session_state.messages):
        st.session_state.profile_complete = True

    # Chat input
    if prompt := st.chat_input("Tell Iris..."):
        save_message(user_id, "user", prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user", avatar="👤"):
            st.write(prompt)

        with st.chat_message("assistant", avatar="🌸"):
            with st.spinner(""):
                reply = chat(st.session_state.messages, user_id)
            render_message(reply)

        save_message(user_id, "assistant", reply)
        st.session_state.messages.append({"role": "assistant", "content": reply})
        st.session_state.vendors = load_vendors(user_id)

        if get_profile_complete(st.session_state.messages):
            if not profile_already_saved(user_id):
                extract_and_save_profile(user_id, st.session_state.messages)
            if not st.session_state.get("timeline_generated") and not timeline_already_saved(user_id):
                st.session_state.timeline_generated = True
                with st.spinner("Building your planning timeline..."):
                    st.session_state.timeline = generate_and_save_timeline(
                        user_id, st.session_state.messages
                    )
            else:
                st.session_state.timeline_generated = True

        st.rerun()

# ── Tab 2: Vendor Dashboard ───────────────────────────────────────────────────

with tab_vendors:
    vendors = st.session_state.vendors or []

    if not vendors:
        st.markdown("### Your vendor tracker")
        st.caption("Once you start searching for vendors and reaching out, they'll all show up here — organized by category, with status updates as things progress.")
        st.stop()

    # Summary bar
    booked = [v for v in vendors if v.get("status") == "booked"]
    active = [v for v in vendors if v.get("status") in ACTIVE_STATUSES]
    passed = [v for v in vendors if v.get("status") in {"passed", "unavailable"}]

    col_a, col_b, col_c = st.columns(3)
    col_a.metric("Booked", len(booked))
    col_b.metric("In Progress", len(active))
    col_c.metric("Passed", len(passed))

    st.divider()

    # Group by category
    by_category = {}
    for v in vendors:
        cat = v.get("category", "Other").title()
        by_category.setdefault(cat, []).append(v)

    # Sort categories: ones with a booked vendor first, then active, then others
    def cat_sort_key(item):
        cat, vlist = item
        statuses = {v.get("status") for v in vlist}
        if "booked" in statuses:
            return 0
        if statuses & ACTIVE_STATUSES:
            return 1
        return 2

    for cat, cat_vendors in sorted(by_category.items(), key=cat_sort_key):
        booked_in_cat = any(v.get("status") == "booked" for v in cat_vendors)
        cat_header = f"{'✅ ' if booked_in_cat else ''}{cat}"
        st.markdown(f"### {cat_header}")

        for v in cat_vendors:
            status = v.get("status", "researching")
            icon = STATUS_ICON.get(status, "🔍")
            label = STATUS_LABEL.get(status, status.title())
            name = v.get("name", "Unknown")
            quote = v.get("quoted_price")
            notes = v.get("notes", "")
            url = v.get("url", "")

            with st.container():
                left, right = st.columns([3, 1])
                with left:
                    name_display = f"[{name}]({url})" if url else name
                    st.markdown(f"**{name_display}**")
                    st.caption(f"{icon} {label}" + (f"  ·  approx. {int(quote):,} dollars" if quote else ""))
                    if notes:
                        st.caption(f"📝 {notes}")
                with right:
                    if status not in {"booked", "passed", "unavailable"}:
                        if st.button("Update", key=f"upd_{v.get('id', name)}", use_container_width=True):
                            st.session_state["update_vendor_id"] = v.get("id")
                            st.session_state["update_vendor_name"] = name
                            st.session_state["update_vendor_cat"] = cat

            st.divider()

    # Inline status update form
    if st.session_state.get("update_vendor_name"):
        vname = st.session_state["update_vendor_name"]
        vcat = st.session_state.get("update_vendor_cat", "")
        st.markdown(f"**Update: {vname}**")
        new_status = st.selectbox(
            "New status",
            options=["contacted", "responded", "meeting_scheduled", "toured", "second_look", "negotiating", "booked", "passed", "unavailable"],
            key="dashboard_new_status",
        )
        new_notes = st.text_input("Notes (optional)", key="dashboard_notes")
        new_price = st.number_input("Quoted price (optional)", min_value=0, value=0, step=100, key="dashboard_price")
        col_save, col_cancel = st.columns(2)
        with col_save:
            if st.button("Save", type="primary", use_container_width=True):
                update_vendor(
                    user_id,
                    vname,
                    new_status,
                    notes=new_notes or None,
                    quoted_price=float(new_price) if new_price else None,
                )
                st.session_state.vendors = load_vendors(user_id)
                for k in ["update_vendor_id", "update_vendor_name", "update_vendor_cat"]:
                    st.session_state.pop(k, None)
                st.rerun()
        with col_cancel:
            if st.button("Cancel", use_container_width=True):
                for k in ["update_vendor_id", "update_vendor_name", "update_vendor_cat"]:
                    st.session_state.pop(k, None)
                st.rerun()
