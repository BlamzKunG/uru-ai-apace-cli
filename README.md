# AIURU CLI

AIURU CLI is a command-line interface client for URU AI Space (Uttaradit Rajabhat University's AI platform, powered by KKU IntelSphere). It provides quick completions, file attachments, code assistant capabilities (local file editing with unified diff review and backups), and quota tracking in formatted terminal tables.

## Features

- **CLI Commands**: Standard CLI arguments layout (`setup`, `quota`, `models`, `edit`, `ask`, `chat`, `update`).
- **Streaming response**: AI answers stream live token by token.
- **Quota Tracking**: Displays daily limit, used tokens, and remaining tokens in formatted ASCII tables.
- **Code Assistant**: Modify local code directly using `aiuru edit <file> "<instruction>"`. Displays a colored Unified Diff for review, prompts for confirmation, and creates `.bak` backups before modifying files.
- **Terminal Pipes**: Integrates with shell pipelines (e.g. `cat log.txt | aiuru "explain"`). Output metadata goes to stderr to keep stdout clean.
- **Interactive Chat**: REPL session with history tracking and Tab autocompletion for commands.
- **Self-Update**: Keep the tool updated directly from GitHub.

## Installation

You can install AIURU CLI directly from this GitHub repository using pip:

```bash
pip install git+https://github.com/BlamzKunG/uru-ai-apace-cli.git
```

This will automatically configure the `aiuru` executable and add it to your PATH.

## Configuration

Run the setup command first to configure your URU AI Space API Key (obtainable from https://aispace.uru.ac.th):

```bash
aiuru setup
```

## Basic Usage

### Ask a quick question
```bash
aiuru ask "Write a short summary of the theory of relativity"
# Or using legacy short syntax
aiuru "What is relativity?"
```

### Pipe command output
```bash
cat error.log | aiuru "Summarize this stacktrace"
```

### Attach a local file
```bash
aiuru ask -f config.json "Explain the structure of this file"
```

### Code Assistant Mode (Edit local files)
```bash
aiuru edit app.py "Wrap the main logic in a try-except block"
```
It will display the proposed unified diff in red/green, ask for confirmation, and write changes after backup.

### Check Quota and switch models
```bash
# Check daily token quota
aiuru quota

# List models and change default
aiuru models
```

### Interactive Chat Mode
```bash
aiuru chat
# Or simply
aiuru
```
Type `/help` in the chat to see all available commands. Press `Tab` to autocomplete.

## License
MIT License
