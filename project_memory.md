# Project Memory: Jovibe Agent

## 1. Project Identity
*   **Name**: Jovibe Agent
*   **Goal**: A secure, local-first Python-based AI agent that uses Google Gemini as its primary intelligence. It proactively manages tasks via a periodic "Heartbeat" mechanism and interacts with users through Telegram and Discord.
*   **Core Philosophy**: Local-first memory, secure authentication, and proactive utility.

## 2. The Tech Stack
*   **Language**: Python 3.10+ (Strictly typed with `typing` and `mypy` for reliability).
*   **Database**: SQLite via **SQLAlchemy** (Core & ORM) for long-term memory, session storage, and RAG indexing.
*   **Intelligence**: **Google Gemini API** (`google-generativeai`).
*   **Authentication**: **Google OAuth 2.0**. Ported from the Gemini CLI's TypeScript implementation to Python using `google-auth-oauthlib`.
*   **Channels**:
    *   **Telegram**: `python-telegram-bot` (Async).
    *   **Discord**: `discord.py` (Async).
*   **Infrastructure**: `asyncio` for concurrent channel management and heartbeat loops.

## 3. Architecture Blueprint (The Magical 4 Components)

### I. Memory System (The "Soul")
Inspired by OpenClaw's architecture:
*   **Persona (`soul.md`)**: A markdown file defining the agent's core identity, tone, and behavioral constraints. Injected into the system prompt.
*   **User Context (`user.md`)**: A persistent record of user-specific facts, preferences, and long-term history.
*   **RAG (Retrieval-Augmented Generation)**:
    *   SQLite-based indexing of interactions and project context.
    *   Implementation of hybrid search (keyword + semantic) using `sqlite-vss` or a similar Python-native approach.
    *   Chunking logic: 400 tokens per chunk with 80-token overlap (matching OpenClaw defaults).

### II. Heartbeat (The "Pulse")
A proactive execution loop:
*   **Mechanism**: An `asyncio` task running every 30 minutes.
*   **Logic**:
    1.  Read `HEARTBEAT.md` (the proactive task list).
    2.  Query Gemini with a specific "Heartbeat Prompt" to determine if any tasks require immediate action.
    3.  If action is needed, the agent initiates the task (e.g., sending a notification, checking a status).
    4.  If nothing is needed, it returns `HEARTBEAT_OK` to conserve tokens/bandwidth.

### III. Adapters (The "Limbs")
*   **Concurrent Execution**: Using `asyncio.gather()` to run the Telegram Bot, Discord Bot, and Heartbeat Loop simultaneously.
*   **Unified Message Interface**: An abstraction layer that translates platform-specific events (Telegram messages vs. Discord messages) into a standard `AgentEvent` for the core brain.

### IV. Skills (The "Tools")
*   **SkillRegistry Class**: A dynamic loader that scans a `skills/` directory for Python modules.
*   **Tool Specification**: Uses Python function docstrings and type hints to automatically generate Gemini function-call schemas (similar to how OpenClaw uses TypeScript types).
*   **Dynamic Loading**: Allows adding new capabilities without restarting the core agent process.

## 4. Special Research: Google OAuth Flow
Based on analysis of `gemini-cli/packages/core/src/code_assist/oauth2.ts`:
*   **OAuth Strategy**:
    *   Uses an embedded `CLIENT_ID` and `CLIENT_SECRET` for "Installed Applications".
    *   **Interactive Flow**: Starts a temporary local HTTP server (typically on a random free port) to handle the `redirect_uri` (e.g., `http://localhost:<port>`).
    *   **Scopes**: `https://www.googleapis.com/auth/cloud-platform`, `https://www.googleapis.com/auth/userinfo.email`, `https://www.googleapis.com/auth/userinfo.profile`.
*   **Python Implementation**:
    *   Utilize `google_auth_oauthlib.flow.InstalledAppFlow`.
    *   Store `credentials.json` locally (encrypted or restricted permissions).
    *   Implement token refreshing via `google.auth.transport.requests.Request`.

## 5. Development Roadmap

### Phase 1: Project Setup & OAuth Implementation (The "Brain")
*   Scaffold Python project structure.
*   Implement the `AuthManager` to handle the Google OAuth 2.0 flow.
*   Establish connection to Gemini API.

### Phase 2: The Memory System (The "Soul")
*   Implement SQLite/SQLAlchemy schema for memory.
*   Create logic to read/inject `soul.md` and `user.md`.
*   Set up basic RAG for indexing local text files.

### Phase 3: The Heartbeat & Proactive Loop (The "Pulse")
*   Develop the `HeartbeatManager` using `asyncio`.
*   Implement `HEARTBEAT.md` parsing and proactive reasoning logic.

### Phase 4: Channel Adapters (Telegram/Discord)
*   Integrate `python-telegram-bot` and `discord.py`.
*   Implement the unified message handler.
*   Final integration and multi-platform testing.
