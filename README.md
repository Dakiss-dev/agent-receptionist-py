# agent-receptionist-py

Minimal **Python agent receptionist**: Claude tool-use loop over a booking calendar.

This is the non-voice core of the receptionists I ship on Twilio + ElevenLabs + Claude. Same loop: check availability, book a slot, answer in the caller's language. Swap the CLI for a media stream and you have the production shape.

Built as a 1-day portfolio demo for the [Contract Engine](https://github.com/Dakiss-dev) Phase 0. Not a framework. ~150 lines.

## What it shows

- **Claude tool-use loop** in pure Python (`anthropic` SDK): `stop_reason == "tool_use"` -> execute -> append `tool_result` -> loop
- **JSON-schema tools** with a real side effect (JSON-file calendar store)
- **TDD**: booking tools have pytest coverage before the agent loop was written
- **Bilingual** FR/EN answers (mirrors the multilingual voice-receptionist niche)

## Run

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

export ANTHROPIC_API_KEY=sk-ant...   # or ANTHROPIC_AUTH_TOKEN / ANTHROPIC_TOKEN
python agent.py "Bonjour, je voudrais un rendez-vous le 15 juillet"
python agent.py "Hi, what times are open on July 16?"
```

## Test

```bash
pytest -v
# 2 passed: availability list + booking removes the slot
```

## Layout

```
agent.py              # Claude tool-use loop + CLI
tools.py              # check_availability / book_appointment
calendar_store.json   # seed slots (tests use a throwaway copy)
tests/test_tools.py   # pytest, written first
requirements.txt      # anthropic, pytest
```

## Related

- [VoiceForge](https://github.com/Dakiss-dev/voiceforge) - production voice-agent framework (TypeScript, provider-agnostic)
- [nafolo](https://github.com/Dakiss-dev/nafolo) - Telegram-to-Claude-Code agent harness with persistent memory

## Status

Shipped. Working demo with tests. Not maintained as a product. Portfolio exhibit for AI Agent Engineer contract work.

Author: [Ali Dakissaga](https://github.com/Dakiss-dev)
