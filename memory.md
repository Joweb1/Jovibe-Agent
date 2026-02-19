# Project Memory & State

This file tracks the long-term context of the Jovibe Agent project and your ongoing work.

## Current Project: Jovibe Agent
- **Goal**: Build a high-quality, local-first Python agent.
- **Tech Stack**: Python, asyncio, Google Gemini (`google-genai`), SQLAlchemy, Telegram Bot API.
- **Environment**: Termux on Android.

## Key Decisions
- [2026-02-19] Switched to the new `google-genai` SDK for better performance and future-proofing.
- [2026-02-19] Implemented `CodeAssistTransport` to mimic Gemini CLI and bypass quota/key issues using personal OAuth tokens.
- [2026-02-19] Integrated OpenClaw principles for a more robust and self-aware agent architecture.

## Interaction History
You maintain a SQLite database (`storage/jovibe.sqlite`) for detailed message history. Use the `search_memory` skill to query it.

## User Preferences
- Prefers concise, action-oriented communication.
- Values security and local execution.
- Wants the agent to be proactive and self-sufficient.
