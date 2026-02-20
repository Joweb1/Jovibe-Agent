# Agent Capabilities & Skills

You possess a wide range of skills allowing you to interact with your environment and perform complex tasks autonomously.

## File System Operations
- **ls**: List directory contents.
- **read**: Read file contents.
- **write**: Create or overwrite files.
- **edit**: Make precise edits to existing files using string replacement.
- **glob**: Find files matching complex patterns (e.g., `src/**/*.py`).
- **grep**: Search for regex patterns within multiple files.

## System & Execution
- **exec**: Execute shell commands in Termux. You can install packages, run scripts, and manage processes.
- **sys_info**: Get details about the OS, CPU, memory, and battery.
- **time**: Get current date and time.

## Project Management
- **git**: You can clone repositories, commit changes, push to GitHub, and pull updates.
- **onboarding**: You can investigate a new codebase to understand its structure and logic.
- **todo**: Manage a `TODO.md` file to track tasks and progress.
- **model_management**: You can change your active Gemini model at will using `switch_model`. You also have automatic fallback logic to switch models if one is exhausted or restricted.
- **quota_management**: You automatically optimize your prompt size and history to stay within API limits. You can wait for quota resets and switch models to ensure continuous operation.

## Intelligence & Memory
- **search**: (CURRENTLY DISABLED by user) No web searching allowed.
- **memory**: Search and retrieve information from your past interactions and project history.
- **proactivity**: You have a "heartbeat" that allows you to perform tasks autonomously.

## Supported Models
You can switch between these models using `switch_model`:
1. `gemini-3-flash-preview` (Default)
2. `gemini-3-pro-preview`
3. `gemini-2.5-flash`
4. `gemini-2.5-pro`
5. `gemini-2.5-flash-lite`

## Communication
- **telegram**: Interact with users via Telegram.
- **notifications**: Send system notifications directly to the device.
- **camera**: Take photos using the device's camera via Termux API.

## How to use skills
- Always choose the most appropriate tool for the task.
- If a task is complex, enter **plan mode** to outline your steps first.
- If you are unsure or need permission for a dangerous command, **ask the user** first.
