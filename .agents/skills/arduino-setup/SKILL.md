---
name: arduino-setup
description: Set up Ventuno Q for the hackathon starters, or Uno Q for the optional classical LiteRT example. Use for first connection, board identification, Python environments, model downloads, or the first smoke check. Use arduino-debug for an existing failure.
---

# Arduino setup

Read [AGENTS.md](../../../AGENTS.md) and guide the user through the [README journey](../../../README.md#follow-the-examples). Each example's README contains its setup and tested requirements. Paths are relative to this skill directory. For a plan only, use supplied inventory and label unknowns; do not connect or install.

1. Ask which computer and board are involved and how to access the board if unspecified. Never supply a guessed IP, password, or SSH alias. Clarify whether setup changes are authorized.
2. Inspect before installing: board identity, OS/architecture, Python/pip, RAM/swap, free disk on the actual workspace/model filesystem, App CLI version, and active apps. Run read-only checks on the board, not the developer computer; query App CLI only for App Lab work.
3. Compare live state to the tested baseline. Ventuno Q is the primary platform; Uno Q supports the Interpreter CPU classifier, not the Gemma starters. An ARM64 wheel installing successfully does not prove CPU compatibility. Do not equate model-file size with memory fit, or enable swap to hide a failed memory-fit test.
4. Select the path: App Lab brick, standalone LiteRT-LM, or classical LiteRT. State required downloads/storage first; don't download every model by default.
5. Within the authorized task, follow the selected example's pinned setup commands. Use isolated Python environments. The no-pip-venv method still requires host pip 22.3+; if pip and ensurepip are absent, request a provisioned environment or an explicitly approved, verified bootstrap confined to a virtual environment. Do not make incidental system-package changes. Never use sudo pip.
6. For App Lab, query installed bricks/models and wait for the chosen Gemma weights to install. Import does not install models. Ask before interrupting an active app.
7. Run the documented smoke check; inspect output and exit status. Report environment, command, result, and remaining gaps. Don't mark inference successful merely because packages installed.

Next: [App Lab](../arduino-app-lab/SKILL.md), [LiteRT-LM](../arduino-litert-lm/SKILL.md), or [LiteRT](../arduino-litert/SKILL.md). For API/version uncertainty, use [documentation lookup](../arduino-docs/SKILL.md). Do not reboot, flash, or change networking as an incidental setup step.
