# Google × Qualcomm Arduino LiteRT Hackathon

This repository is a reference and starter kit for hackathon participants. Use the examples as a starting point for your own project.

Build local AI applications on **Arduino Ventuno Q**. Learn the board by creating a small App Lab app, then explore two development paths: **LiteRT-LM for generated text** and **LiteRT for task-specific predictions**. Run working code, understand the important calls, and start shaping your own application.

## Get ready

Clone this repository. Have your board running its supported Linux image and connected to the network; ask an organizer for its address/account or help provisioning it.

You'll use App Lab on your computer for the first example, and a terminal with SSH/SCP on macOS, Linux, or WSL for the standalone examples. Each example README walks you through setup, a first result, and a small change to make yourself.

No webcam or sensor is needed. Installation requires internet; inference runs locally on the board. Allow at least 10 GB free for the first three examples, about 5 GB more for the embedding and NPU examples, plus room for uncached App Lab containers.

## Follow the examples

These are independent examples, not prerequisites for one another. Follow the progression below, or jump to the approach you need. **Using Uno Q 4 GB? Go straight to step 3.** The Gemma examples target Ventuno Q.

### 1. Start with App Lab: learn the board's app workflow

Follow [App Lab hello world](examples/app-lab-hello-world/README.md) to create an app, add the local LLM brick, select Gemma 4 E2B, and write a short Python greeting program. The finished files are there to compare against; no ZIP import is required.

Learn how `app.yaml` selects the brick/model and how `python/main.py` calls it. Change the question and system instruction to see their effects. App Lab handles the runtime for you through **llama.cpp**: this is the introduction, not a third LiteRT development path.

### 2. Take control of Gemma with standalone LiteRT-LM

Next, open [standalone LiteRT-LM](examples/standalone-litert-lm/README.md). Generate a similar greeting, this time from a Python script that loads the model and manages the conversation directly, without App Lab.

Choose this approach when you want generation inside your own Python application and control over prompts, conversation lifecycle, and output limits. Follow the **engine → conversation → message** flow in the script, try `--prompt`, and then experiment with a follow-up in the same conversation. The example runs on **CPU** and reports load time, generation time, and memory use.

### 3. Try LiteRT when you don't need a language model

Now open [standalone LiteRT](examples/standalone-litert/README.md). Run the MobileNet image classifier on the supplied parrot image, then try a photo of your own.

Not every AI task needs generated text. For image classification, a small task-specific model gives you labels directly, with a much smaller download. This example shows the core LiteRT flow: prepare pixels, invoke the **CPU Interpreter**, and read the output. Compare a wide shot and a close crop of the same object to see why input preparation matters. Use this path when your application needs predictions rather than generated text.

### 4. Search by meaning with EmbeddingGemma 2

Open [standalone embedding](examples/standalone-embedding/README.md). An embedding model turns a sentence, a photo, or a spoken clip into a list of numbers, so you can find the closest match in a small library: semantic search, and the retrieval half of retrieval-augmented generation. There is no text generation, so the model is small (about 485 MB) and fast. It uses the same LiteRT-LM Python package as the Gemma example and runs on the CPU. Try a text question, then search the same library with a photo.

### 5. Move to the NPU (Ventuno Q only)

Once the CPU examples work, run them on the board's **Qualcomm Hexagon NPU**. `python3 scripts/setup_npu.py` downloads and verifies the NPU libraries once (about 170 MB, no `sudo`). Then add `--backend npu` to the [MobileNet example](examples/standalone-litert/README.md#4-optional-run-on-the-npu-ventuno-q) and the [embedding example](examples/standalone-embedding/README.md#4-optional-run-on-the-npu), and try [Gemma on the NPU](examples/standalone-litert-lm-npu/README.md) with text, an image, or an audio clip. Gemma and the embedding example each need their own NPU model file, linked from their READMEs.

The examples reach the NPU in two ways: Gemma and EmbeddingGemma run models compiled ahead of time for this chip through LiteRT's Qualcomm *dispatch* library, while MobileNet uses Qualcomm's *delegate*, which compiles an ordinary `.tflite` model for the NPU when it loads. Each run prints evidence of NPU activity and fails if it sees none, so a pass is not just a model that loaded.

### 6. Build on the path that fits your idea

Use **LiteRT-LM** for an offline text assistant or summaries of real measurements; use **LiteRT** for an image-sorting tool or another trained prediction task. Combine them only if your idea needs both. Keep the original example as a known-good reference while you build.

The [developer guide](docs/developer-guide.md) has background and extension ideas when you need them. Camera/sensor integration, GPU acceleration, and fully disconnected startup remain unvalidated extensions; the NPU examples are tested on Ventuno Q only. They are not prerequisites for getting started.

## Repository structure

```text
examples/
  app-lab-hello-world/    Guided app creation and finished reference files
  standalone-litert-lm/  Gemma script, requirements, and instructions
  standalone-litert/     Image classifier, requirements, and instructions (CPU, or NPU with a flag)
  standalone-embedding/  EmbeddingGemma 2 semantic search with text, image, and audio (CPU, or NPU with a flag)
  standalone-litert-lm-npu/  Gemma on the NPU with text, image, and audio
.agents/skills/          Eight optional coding-assistant skills
.claude/skills/          Links to those same skills for Claude Code
AGENTS.md                Example/skill map and shared agent instructions
CLAUDE.md, GEMINI.md     Point assistants to AGENTS.md
scripts/                 Verified model downloads and NPU setup
docs/                    Optional technical reference and third-party terms
```

## Using a coding assistant

Open your assistant in this checkout and paste:

```text
Read AGENTS.md and use the arduino-setup skill to guide me through the
README's examples, starting with App Lab unless my board or goal calls
for a different path. Ask about my computer, board, and access method
if needed. Explain the setup and ask before making changes or downloading
models. Run the selected example's smoke check and show me the result.
```

The skills are optional; the examples work without an assistant. [AGENTS.md](AGENTS.md) maps the examples and skills and explains discovery for different tools.

## Getting help

Ask an event mentor for board setup or access help. If an example fails, share the example name, board/OS/Python versions, command, and error output. Remove credentials, private addresses, and confidential data before sharing logs publicly.

## License

The repository's original code and documentation are licensed under [Apache-2.0](LICENSE). Models and runtimes retain their own licenses; see [third-party assets](docs/third-party.md).
