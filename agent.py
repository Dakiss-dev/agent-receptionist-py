"""A minimal receptionist agent: Claude + tool use over the booking tools.

Usage:
    export ANTHROPIC_API_KEY=<your-key>
    python agent.py "Bonjour, je voudrais un rendez-vous le 15 juillet"

The agent answers in the caller's language, checks real availability, and
books appointments through the same tools the test suite covers. This is the
non-voice core of the receptionists I ship on Twilio + ElevenLabs: swap the
CLI for a media stream and the loop is the same.
"""

import json
import os
import sys
from datetime import date

import anthropic

import tools

MODEL = "claude-sonnet-4-5"

SYSTEM_PROMPT = """
You are a phone receptionist for a small service business. You help callers
check availability and book appointments.

Rules:
- Answer in the caller's language (French or English). Match their register.
- Always check real availability with the check_availability tool before offering times.
  Never invent open slots.
- To book, you need date, time, name, and phone. Ask for whatever is missing.
  Only call book_appointment after the caller has confirmed all four.
- Keep replies short. This is a phone conversation, not an email.
- If a slot is taken, offer the next open ones for that day.
- Dates must be YYYY-MM-DD when calling tools. Resolve relative phrases
  like "mardi" / "Tuesday" / "demain" from today's date.
- Do not discuss anything outside booking and availability.
"""

TOOL_DEFS = [
    {
        "name": "check_availability",
        "description": "List the open appointment slots for a given date (YYYY-MM-DD).",
        "input_schema": {
            "type": "object",
            "properties": {"date": {"type": "string", "description": "Date in YYYY-MM-DD format"}},
            "required": ["date"],
        },
    },
    {
        "name": "book_appointment",
        "description": "Book an open slot. Only call after the caller confirmed date, time, name, and phone number.",
        "input_schema": {
            "type": "object",
            "properties": {
                "date": {"type": "string", "description": "Date in YYYY-MM-DD format"},
                "time": {"type": "string", "description": "Time slot, e.g. 14:00"},
                "name": {"type": "string", "description": "Caller's name"},
                "phone": {"type": "string", "description": "Caller's phone number with country code"},
            },
            "required": ["date", "time", "name", "phone"],
        },
    },
]


def _run_tool(name: str, tool_input: dict) -> str:
    try:
        if name == "check_availability":
            return json.dumps({"open_slots": tools.check_availability(**tool_input)})
        if name == "book_appointment":
            return json.dumps(tools.book_appointment(**tool_input))
        return json.dumps({"error": f"unknown tool {name}"})
    except (ValueError, TypeError) as e:
        return json.dumps({"error": str(e)})


def run(user_message: str) -> str:
    # Prefer API key; fall back to OAuth/setup-token style auth (ANTHROPIC_AUTH_TOKEN
    # or ANTHROPIC_TOKEN) so Claude Max / hermes-style logins also work.
    api_key = os.environ.get("ANTHROPIC_API_KEY") or None
    auth_token = (
        os.environ.get("ANTHROPIC_AUTH_TOKEN")
        or os.environ.get("ANTHROPIC_TOKEN")
        or None
    )
    if api_key == "":
        api_key = None
    client = anthropic.Anthropic(api_key=api_key, auth_token=auth_token)
    system = SYSTEM_PROMPT.strip() + f"\n\nToday is {date.today().isoformat()}."
    messages = [{"role": "user", "content": user_message}]

    while True:
        response = client.messages.create(
            model=MODEL,
            max_tokens=1024,
            system=system,
            tools=TOOL_DEFS,
            messages=messages,
        )
        messages.append({"role": "assistant", "content": response.content})

        if response.stop_reason != "tool_use":
            return "".join(block.text for block in response.content if block.type == "text")

        results = []
        for block in response.content:
            if block.type == "tool_use":
                print(f"  [tool] {block.name}({json.dumps(block.input, ensure_ascii=False)})")
                results.append(
                    {
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": _run_tool(block.name, block.input),
                    }
                )
        messages.append({"role": "user", "content": results})


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print('usage: python agent.py "your message"')
        sys.exit(1)
    print(run(" ".join(sys.argv[1:])))
