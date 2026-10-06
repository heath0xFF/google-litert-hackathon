# Standalone LiteRT-LM: Gemma hello world

Generate a local Gemma 4 E2B response from Python using **LiteRT-LM on CPU**. No App Lab or accessories required.

**Requirements:** Ventuno Q with Ubuntu 24.04 ARM64, Python 3.12, host pip 22.3+, and SSH access. Allow space for the ~2.59 GB model plus Python packages and internet for installation. Tested with `litert-lm-api==0.17.1`.

**Not for Uno Q:** this pinned native runtime requires ARM LSE instructions absent on Uno Q. It fails before generation; this is not a measured memory limit.

## 1. Copy and connect with your computer

From the repository root, replace `BOARD_HOST` and the account if needed. Use a different destination if `~/litert-hackathon` already contains work you do not want to overwrite.

```bash
export BOARD=arduino@BOARD_HOST
ssh "$BOARD" 'mkdir -p ~/litert-hackathon'
scp -r examples scripts "$BOARD":litert-hackathon/
ssh "$BOARD"
```

## 2. Install on the board

```bash
cd ~/litert-hackathon
python3 -m venv --without-pip .venv-lm
python3 -m pip --python .venv-lm/bin/python install -r examples/standalone-litert-lm/requirements.txt
python3 scripts/download.py gemma
```

Host pip installs into the isolated environment, not system Python. This works without `ensurepip`, which is missing on the tested board image. If host pip is absent or older than 22.3, ask an organizer to provision the Python tooling; do not use `sudo pip`.

The downloader verifies the pinned model with SHA-256. A mismatch is a failed download: move any suspect cached file aside and retry, rather than changing its expected hash. App Lab's GGUF model is not a substitute for this `.litertlm` file.

## 3. Run on the board

```bash
timeout 120 .venv-lm/bin/python examples/standalone-litert-lm/main.py
```

Expect a greeting followed by **`PASS: local Gemma answered; backend=CPU; ...`** and exit status 0. Wording varies. Missing models, empty responses, exceptions, and timeouts are failures. If the process is killed, inspect available RAM and competing workloads rather than silently switching to cloud inference.

## Understand the code

Open [main.py](main.py) and follow the three runtime calls:

1. **Load:** `lm.Engine(...)` opens the `.litertlm` model and selects four CPU threads and a 2,048-token context. Unlike the App Lab brick, your program owns the engine's lifetime.
2. **Create a conversation:** `engine.create_conversation(...)` creates the conversation state and sets the 128-token output limit with thinking disabled. Reusing this conversation allows follow-up messages; a new conversation starts without that history.
3. **Send and read:** `conversation.send_message(args.prompt)` performs generation. The script extracts the text from the response and rejects an empty result. The `with` blocks release the conversation and engine on exit.

The reported load time, generation time, and peak process memory measure different parts of that flow. Each invocation currently creates a fresh conversation; running the command again does not continue the previous chat.

## Understand and change it

First, try a different task without changing the code:

```bash
.venv-lm/bin/python examples/standalone-litert-lm/main.py \
  --prompt 'Suggest three useful offline applications for a small Linux computer.'
```

Then edit the script to send a second message, such as “Which of those ideas needs the least hardware?”, **inside the same conversation's `with` block**. Extract and print its reply as you did for the first message. Compare that with asking the follow-up in a fresh invocation: which context is missing?

Keep the context/output limits while experimenting. The prompt character limit is only an early guard; unusual text may still exceed the token context. Camera input and GPU/NPU acceleration need separate validation; no cloud fallback is configured.

Next, try [standalone LiteRT](../standalone-litert/README.md) for a task that needs class scores instead of generated text.
