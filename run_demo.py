"""
demo/run_demo.py — Show a client-#1 agent to a prospect in 60 seconds.

    python run_demo.py --simulate                       # dental, canned, $0
    python run_demo.py --business salon --simulate      # salon, canned, $0
    python run_demo.py --business auto --simulate       # auto shop, canned, $0
    python run_demo.py --business salon                 # live (needs OPENAI_API_KEY)

In live mode you play the customer: type messages, watch the agent answer
FAQs, check availability, and book. Great for a screen-share with a prospect.
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

BUSINESSES = {
    "dental": {"module": "dental_agent", "label": "Bright Smile AI"},
    "salon": {"module": "salon_agent", "label": "Radiant Roots AI"},
    "auto": {"module": "autorepair_agent", "label": "Main Street AI"},
}

SIMULATED_TRANSCRIPTS = {
    "dental": [
        ("customer", "Hi! Do you guys do whitening and how much is it?"),
        ("agent", "Hi there! Yes — in-office whitening is $299 and takes about an hour. "
                  "We also have take-home kits for $149. Want me to book you in?"),
        ("customer", "The $299 one. Do you have anything Friday afternoon?"),
        ("agent", "Let me check Friday for whitening…"),
        ("tool:check_availability", "Open slots for whitening on Friday, Oct 2: 1:30 PM, 4:00 PM."),
        ("agent", "I have Friday at 1:30 PM or 4:00 PM. Which works for you?"),
        ("customer", "4pm. Name's Priya, number 812-555-8890"),
        ("tool:book_appointment", "Booked. Confirmation BSD-1001-4821."),
        ("agent", "You're booked, Priya! Whitening on Friday, Oct 2 at 4:00 PM — "
                  "confirmation BSD-1001-4821. Arrive 15 min early, and just give us "
                  "24h notice here if you need to move it. See you then!"),
    ],
    "salon": [
        ("customer", "Hey! How much for balayage?"),
        ("agent", "Hi! Balayage starts at $160 and takes 2–3 hours — includes toner + style. "
                  "There's a $25 deposit to hold your slot. Want me to check openings?"),
        ("customer", "Yes, Saturday morning if you have it"),
        ("agent", "Let me check Saturday for balayage…"),
        ("tool:check_availability", "Open slots for balayage on Saturday, Oct 3: 9:00 AM, 10:30 AM, 12:00 PM."),
        ("agent", "I have Saturday at 9:00 AM, 10:30 AM, or 12:00 PM. Which works for you?"),
        ("customer", "10:30. Maya, 502-555-0143"),
        ("tool:book_appointment", "Booked. Confirmation RRS-1001-7734."),
        ("agent", "You're in, Maya! Balayage Saturday, Oct 3 at 10:30 AM — "
                  "confirmation RRS-1001-7734. $25 deposit holds the slot, and just give us "
                  "24h notice here if you need to move it!"),
    ],
    "auto": [
        ("customer", "Hi, my brakes are squeaking. How much for brake pads?"),
        ("agent", "Hey! Sorry to hear that — brake pads are $189 per axle, rotors extra if "
                  "needed. We do a free brake inspection with any service. What do you drive?"),
        ("customer", "2019 Camry. Can I come Friday morning?"),
        ("agent", "Let me check Friday for a brake inspection…"),
        ("tool:check_availability", "Open slots for brake inspection on Friday, Oct 2: 8:00 AM, 9:30 AM, 11:00 AM, 1:00 PM, 3:00 PM."),
        ("agent", "I have Friday at 8:00, 9:30, or 11:00 AM. Which works for you?"),
        ("customer", "9:30. Dan, 812-555-0277"),
        ("tool:book_appointment", "Booked. Confirmation MSA-1001-2290."),
        ("agent", "Booked, Dan! Brake inspection for your 2019 Camry Friday, Oct 2 at 9:30 AM — "
                  "confirmation MSA-1001-2290. Bring it 10 min early; 2h notice here if you need to move it."),
    ],
}

def pick_business() -> str:
    if "--business" in sys.argv:
        idx = sys.argv.index("--business")
        try:
            name = sys.argv[idx + 1].lower()
        except IndexError:
            name = ""
        if name not in BUSINESSES:
            print(f"Unknown business '{name}'. Choose from: {', '.join(BUSINESSES)}")
            sys.exit(1)
        return name
    return "dental"

def main() -> None:
    business = pick_business()
    cfg = BUSINESSES[business]
    label = cfg["label"]

    if "--simulate" in sys.argv:
        print(f"=== SIMULATED demo transcript ({business}, no API calls) ===\n")
        for role, text in SIMULATED_TRANSCRIPTS[business]:
            who = {"customer": "Customer", "agent": label}.get(role, role)
            print(f"{who}: {text}")
        print("\n=== end — run without --simulate for the live agent ===")
        return

    # Live mode: needs a real model key.
    from dotenv import load_dotenv
    load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env"))
    if not os.environ.get("OPENAI_API_KEY"):
        print("Live mode needs OPENAI_API_KEY. Either:")
        print("  1. add it to ../.env, or")
        print(f"  2. run: python run_demo.py --business {business} --simulate   (canned transcript, free)")
        sys.exit(1)

    import importlib
    agent = importlib.import_module(cfg["module"])
    print(f"=== LIVE demo ({business}) — you play the customer. Type 'quit' to exit. ===\n")
    user_id = "demo-prospect"
    while True:
        try:
            text = input("Customer: ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if text.lower() in {"quit", "exit"}:
            break
        if not text:
            continue
        print(f"{label}:", agent.run_agent(user_id, text))

if __name__ == "__main__":
    main()
