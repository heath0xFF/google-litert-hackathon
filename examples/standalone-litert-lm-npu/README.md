# Standalone LiteRT-LM on the NPU: Gemma with text, image, and audio

Run a local Gemma 4 E2B conversation on the Ventuno Q's **Qualcomm Hexagon NPU** from Python, and optionally give it an image or an audio clip. It is the [CPU example](../standalone-litert-lm/README.md) with a different backend.

**Requirements:** Ventuno Q (Qualcomm QCS8275) with Ubuntu 24.04 ARM64, Python 3.12, host pip 22.3+, SSH access, and internet for setup. Allow about 3.5 GB: the NPU model (about 3 GB) plus about 170 MB of libraries. Tested with `litert-lm-api==0.18.0`. **Ventuno Q only:** the model and libraries target this chip.

**Two doorways to the same NPU:** Gemma runs a model compiled ahead of time for this chip through LiteRT's Qualcomm *dispatch* library, while the [MobileNet example](../standalone-litert/README.md#4-optional-run-on-the-npu-ventuno-q) uses Qualcomm's *delegate*, which compiles an ordinary `.tflite` model for the NPU when it loads.

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
python3 -m venv --without-pip .venv-lm   # skip if you already made it for the CPU example
python3 -m pip --python .venv-lm/bin/python install -r examples/standalone-litert-lm-npu/requirements.txt
python3 scripts/setup_npu.py
```

`setup_npu.py` downloads about 170 MB into `npu/`. It checks pinned SHA-256 hashes for Qualcomm's NPU libraries (fetched from Qualcomm, not stored in this repository) and the LiteRT-LM runtime built for the NPU. It also copies `libatomic` from the board or gets it through `apt-get download` if missing; that library has no repository-pinned hash. It needs no `sudo` and is safe to run again. Use `--force` to replace cached files, including `libatomic`.

**Get the model.** The NPU build of Gemma 4 E2B for QCS8275 is a different file from the CPU example's `gemma-4-E2B-it.litertlm`: the CPU file contains no NPU graphs, and the NPU file does not run on the CPU. Put it in `models/`.

> **TODO before the hackathon:** replace this paragraph with the published model link and pinned download command.

## 3. Run on the board

```bash
timeout 120 .venv-lm/bin/python examples/standalone-litert-lm-npu/main.py
```

Expect a greeting, a line starting **`NPU evidence:`**, and **`PASS: local Gemma answered; backend=NPU; ...`** with exit status 0. Wording varies. A run that answers but shows no NPU activity fails instead of passing.

Now give it something to look at or listen to:

```bash
python3 scripts/download.py vision    # fetches the parrot photo used below
.venv-lm/bin/python examples/standalone-litert-lm-npu/main.py \
  --image models/parrot.jpg --prompt "What animal is this? Answer in one sentence."

.venv-lm/bin/python examples/standalone-litert-lm-npu/main.py \
  --audio hello.wav --prompt "Transcribe the audio exactly. Output only the words spoken."
```

No audio file ships with the repository. Use any short WAV; 16 kHz mono is the safest. On a Mac you can make one and copy it over:

```bash
say -o hello.aiff "The access code is blue seven four nine." && afconvert -f WAVE -d LEI16@16000 -c 1 hello.aiff hello.wav
scp hello.wav "$BOARD":litert-hackathon/
```

The NPU libraries print hundreds of lines, mostly harmless shutdown messages. They go to `npu/last-run.log`, and the end of that log is shown if a run fails.

## Understand the code

Open [main.py](main.py) next to the CPU example's. The LiteRT-LM flow is the same engine → conversation → message. Three things change:

1. **Backend:** `lm.Backend.NPU(litert_dispatch_lib_dir=...)` replaces `lm.Backend.CPU(...)`. The directory holds LiteRT's Qualcomm dispatch library and the Qualcomm NPU libraries it loads.
2. **Image and audio parts:** the image and audio encoders are separate parts of the model, so `vision_backend` and `audio_backend` are given the NPU only when you pass `--image` or `--audio`.
3. **Message with media:** a message with an image or audio is a list of parts (`image`, `audio`, `text`) that the model reads together.

The rest is plumbing in [scripts/npu_runtime.py](../../scripts/npu_runtime.py), which you can skip: it points the program at the libraries (restarting it once to set `LD_LIBRARY_PATH`), switches `litert-lm-api` to the NPU-enabled runtime library, and checks for traces of NPU use. That runtime swap is why `requirements.txt` pins an exact version. Without it the same model ran about three times slower in our tests, because the NPU stayed in its default power mode.

**What the evidence line means.** A model that loads is not proof it ran on the NPU. The line reports that Qualcomm's NPU library is loaded, that the channel to the NPU is open, and how many interrupts the NPU's processor sent during generation. The run passes only if there was NPU activity.

## Understand and change it

Compare against the CPU example with the same prompt:

```bash
.venv-lm/bin/python examples/standalone-litert-lm/main.py --prompt "Say hello to the hackathon in one sentence."
.venv-lm/bin/python examples/standalone-litert-lm-npu/main.py --prompt "Say hello to the hackathon in one sentence."
```

On our test board, that greeting generated in about 0.8 s on the NPU and about 5 s on the CPU (single runs; yours will vary). The CPU example needs its own model; use the model from its README.

Then try a longer prompt, an image of your own, or a voice clip. Keep the 128-token output limit while experimenting: the model's context length is fixed when it is compiled and cannot be raised at run time. Text, image, and audio inputs here were tested with short, clean examples on one board; treat the outputs as prototypes, not guarantees, and expect the occasional misheard word.

## If something fails

| Message | Meaning |
|---|---|
| `NPU libraries not found` | Run `python3 scripts/setup_npu.py`. |
| `Cannot open /dev/fastrpc-cdsp` | Your account needs the `fastrpc` group. Ask an organizer. |
| `Checksum mismatch` | A download was cut short. Run `setup_npu.py` again. |
| Could not download `libatomic1` | Ask an organizer, or run `sudo apt install libatomic1` if you have sudo. |
| `FAIL: ... no NPU activity was observed` | The model answered without using the NPU, most often because it is the CPU model. Use the NPU model. |
| `Failed to create LiteRT-LM engine` | The model file is damaged, incomplete, or not a `.litertlm` file. Download it again. |
