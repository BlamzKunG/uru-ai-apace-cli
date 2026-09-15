# URU AI CLI

Uttaradit Rajabhat University (URU AI Space) Terminal Coding Agent

An experimental AI assistant and terminal CLI designed to test and explore the URU AI Space API. This project serves as a playground for experimenting with terminal-based agentic workflows capable of reading files, writing code, executing commands, and monitoring API quota usage.

---

## About The Project

This is an experimental project created for testing and exploring the URU AI Space API platform. The goal is to build an interactive AI coding agent for the terminal that can:

- Read, create, and modify project files.
- Execute shell commands and Python scripts locally with real-time feedback.
- Dynamically discover and switch between models provided by URU AI Space.
- Monitor token consumption and daily quota utilization with visual progress indicators.

---

## Features

- Terminal AI Pair Programmer: Run interactive conversations or one-off tasks directly in your command line.
- File System Operations: Read files, create new scripts, and make targeted edits using diff/patch mechanisms.
- Local Execution: Safely execute bash commands, run test suites, and execute Python code directly.
- Dynamic Model Selection: Automatically query the URU AI Space API for available models (Gemini, Claude, DeepSeek, GPT-5, Qwen, Grok, Llama).
- Interactive Model Switcher: Use the `/model` command to browse and select models using keyboard arrow keys.
- Real-Time Token and Quota Tracking:
  - Automatic inline token summary after each AI response turn.
  - Dedicated `/usage` command displaying daily token quota, used tokens, remaining tokens, and a progress bar.

---

## Installation

### Prerequisites

- Python 3.10 or higher
- Git

### Steps

1. Clone the repository:

```bash
git clone https://github.com/BlamzKunG/uru-ai-apace-cli.git
cd uru-ai-apace-cli
```

2. Install the package in editable mode:

```bash
pip install -e . --break-system-packages
```

*(Note: On Debian/Ubuntu environments with externally managed Python, include `--break-system-packages` or use a virtual environment).*

---

## Configuration

### Interactive Setup (Recommended)

Run the interactive setup wizard to validate your API key and select your preferred model:

```bash
uru-setup
```

### Manual Configuration

Create a `.env` file in the project directory or configure environment variables:

```bash
URU_API_KEY="sk_xxxxxxxxxxxxxxxxxxxxxxxxxxxx"
URU_BASE_URL="https://gen.ai.kku.ac.th/uruacth/api/v1"
```

---

## Usage

### Interactive Mode

Start an interactive chat session:

```bash
uru
```

Or using the alias:

```bash
aiuru
```

### One-Off Command Execution

Pass instructions directly as command-line arguments:

```bash
uru "List all Python files in the current directory and check for syntax errors"
```

### Specifying a Model

Choose a specific model from URU AI Space when launching:

```bash
uru -m uru/gemini-3.8-flash "Write a unit test for auth.py"
uru -m uru/claude-sonnet-5 "Refactor database queries for performance"
```

---

## Interactive Chat Commands

Inside an interactive session, the following slash commands are available:

| Command | Description | Aliases |
| :--- | :--- | :--- |
| `/model` | Show current model or interactively switch models with arrow keys | - |
| `/models` | List all available models from URU AI Space | - |
| `/usage` | Show daily token quota, used tokens, and session breakdown | `/quota`, `/tokens`, `/cost` |
| `/context` | Show current conversation token count and role breakdown | - |
| `/tools` | List loaded tools or load additional tools (`/tools load <name>`) | - |
| `/undo` | Revert the last turn or action | - |
| `/clear` | Clear the terminal display | - |
| `/help` | Show all available commands | - |
| `/exit` | Exit the CLI session | - |

---

## Token and Quota Monitoring

The CLI automatically tracks usage from the URU AI Space API response:

- **Inline Output:** After each assistant response, a summary line is shown:
  ```text
  [tokens: 15 in / 85 out | quota: 144,352/200,000 (72.2%)]
  ```
- **Usage Command:** Running `/usage` renders a detailed quota breakdown:
  ```text
  Daily Quota (URU AI Space):
    Limit:      200,000 tokens
    Used:       144,352 tokens (72.18%)
    Remaining:  55,648 tokens
    Progress:   [█████████████████░░░░░░░] 72.18%
  ```

---

## Disclaimer

This repository is an experimental project for research, learning, and testing the URU AI Space API platform.
