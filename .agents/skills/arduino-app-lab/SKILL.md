---
name: arduino-app-lab
description: Build, extend, import, or run Arduino App Lab applications on Ventuno Q using installed bricks and optional MCU sketches. Use for app manifests, local Gemma configuration, and Python-to-MCU integration; not standalone LiteRT code.
---

# Build with App Lab

Read [AGENTS.md](../../../AGENTS.md) and the [working example](../../../examples/app-lab-hello-world/README.md), including its `app.yaml` and `python/main.py`. For source-only work, use the recorded baseline and leave board verification pending; do not initiate setup or downloads.

1. For hardware operations, establish board identity, App CLI version, and current workloads. Use [setup](../arduino-setup/SKILL.md) if access or prerequisites are missing.
2. With authorized board access, query `arduino-app-cli brick list`, `brick details`, `model list`, and command `--help`. Read the closest bundled example and installed API docs before changing API usage. Use `app list` and `config get` to locate apps/examples rather than guessing versioned paths.
3. Keep the existing project shape: `app.yaml`, `python/main.py`, optional `sketch/` and assets. Every brick import needs a matching manifest entry. Add an MCU sketch only when physical I/O requires it; no sketch is needed for the greeting.
4. Select Gemma explicitly. The tested local LLM brick uses llama.cpp/GGUF, not LiteRT-LM. Catalog availability does not prove the weights are downloaded or the model fits another board.
5. Verify installed Python signatures rather than copying latest-web APIs blindly. Bound model output/timeouts, surface failures, and let App manage the lifecycle. Read any existing sketch before changing it; coordinate flashing with the user.
6. For accessories, establish real camera/sensor input separately before fusing it with generation. Modulinos use Qwiic/I²C; use a verified MCU/Router Bridge example where appropriate. Do not fake measurements or make safety claims.
7. For this starter, guide the user through creating a Python-only app, adding the LLM brick, and using the reference program. Explain the manifest → brick → Python callback flow; no repository packaging step is needed. GUI instructions are documented but not yet hardware-walkthrough verified.
8. With permission to start the app, run it, inspect Python logs for the expected result, and stop it after a one-shot test to release its model service. If using import for another task, use the importer's actual destination; repeated imports may add a suffix.

Report the exact model, brick/runtime versions, observed output, and anything untested. Use [arduino-debug](../arduino-debug/SKILL.md) for failures and [arduino-docs](../arduino-docs/SKILL.md) for API discovery. A successful start command is not an inference pass.
