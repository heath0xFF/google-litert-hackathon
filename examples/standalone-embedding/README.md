# Standalone EmbeddingGemma 2: search by meaning, with text, pictures, and sound

Turn a sentence, a photo, or a spoken clip into a list of 768 numbers that captures its meaning, then use those numbers to find the closest sentences in a small library. This is semantic search, and it is the retrieval half of retrieval-augmented generation. There is no text generation here, so it is fast and small. **EmbeddingGemma 2** puts text, images, and audio into one shared space, which is why a photo of a parrot can find a sentence about macaws.

**Requirements:** Ventuno Q with Ubuntu 24.04 ARM64, Python 3.12, host pip 22.3+, SSH access, and internet for installation. The model is about 485 MB (the optional NPU build, about 563 MB). Tested with `litert-lm-api==0.18.0` on Ventuno Q only. It uses the same native runtime as the [Gemma example](../standalone-litert-lm/README.md), which that README lists as unsupported on Uno Q.

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
python3 -m venv --without-pip .venv-lm   # skip if you already made it for a Gemma example
python3 -m pip --python .venv-lm/bin/python install -r examples/standalone-embedding/requirements.txt
python3 scripts/download.py embedding    # the model, about 485 MB
python3 scripts/download.py vision       # includes the parrot photo used below
```

Downloads are pinned and SHA-256 verified. For a checksum mismatch, move any suspect cached file aside and retry; do not change the expected hash.

## 3. Run on the board

```bash
timeout 120 .venv-lm/bin/python examples/standalone-embedding/main.py --check
```

Expect a ranked list in which the **Wi-Fi sentence is first** for the question "How do I get my board online?", a second query in which the **macaw sentence is first** for the parrot photo, and **`PASS: Wi-Fi sentence found ...`** with exit status 0.

Now search the library yourself with text, a picture, or your voice:

```bash
.venv-lm/bin/python examples/standalone-embedding/main.py --query "What gives the aurora its colors?"
.venv-lm/bin/python examples/standalone-embedding/main.py --image models/parrot.jpg
.venv-lm/bin/python examples/standalone-embedding/main.py --audio question.wav
```

No audio file ships with the repository. Use any short WAV; 16 kHz mono is the safest. On a Mac you can make one and copy it over:

```bash
say -o question.aiff "How do I connect my board to the Wi-Fi network?" && afconvert -f WAVE -d LEI16@16000 -c 1 question.aiff question.wav
scp question.wav "$BOARD":litert-hackathon/
```

## 4. Optional: run on the NPU

The Ventuno Q has a Qualcomm Hexagon NPU. Get the NPU build of the model and the NPU libraries (about 170 MB, no `sudo`, shared with the other NPU examples), then add one flag:

```bash
python3 scripts/download.py embedding-npu
python3 scripts/setup_npu.py
timeout 120 .venv-lm/bin/python examples/standalone-embedding/main.py --backend npu --check
```

The ranking and the `PASS` line are the same, plus a line starting **`NPU evidence:`**; the run fails if no NPU activity is seen. On our test board, embedding a text query took about 12 ms on the NPU and about 0.5 s on the CPU, and a photo took about 0.4 s against about 3.4 s (single runs on one board; yours will vary). Like the Gemma NPU model, this build is compiled ahead of time for the chip and runs through LiteRT's Qualcomm dispatch library.

**Audio runs on the CPU.** The model card lists audio as unsupported on this NPU. The NPU build will not even start unless audio is given a backend, so `main.py` always gives audio the CPU. Spoken queries work; they just are not accelerated. **Scores differ between builds:** the Wi-Fi match scored about 0.82 on the CPU build and about 0.58 on the NPU build. Compare scores only within one model build; the ranking is what carries over.

## Understand the code

Open [main.py](main.py) and follow the data:

1. **Load:** `lm.EmbeddingEngine(...)` takes a backend for each part of the model: text, vision, and audio. The image part is given a backend only when you search with a picture. Audio is given one only when you search with sound on the CPU build, and always on the NPU build (see section 4).
2. **Embed:** `compute_embedding_batch(...)` embeds the whole library and `compute_embedding(...)` embeds the query. Each returns 768 numbers. `EmbeddingOptions(normalize=True)` scales every vector to length 1, so a plain dot product is the cosine similarity.
3. **One space for all inputs:** a query can be a string, `lm.Content.ImageFile(path)`, or `lm.Content.AudioFile(path)`. The library is always sentences, but the query can be any of the three, because they all land in the same space.
4. **Task prefixes:** for text, the model expects short prefixes: `task: search result | query: ...` on queries and `title: none | text: ...` on library sentences. Pictures and audio get none. Leaving the prefixes out still works but is less precise.
5. **Rank:** sort by score. A scored list always has a first place, so look at the gap, not only the winner. The spoken clip "The access code is blue seven four nine" has no matching sentence, and its best score was about 0.64 against about 0.86 for a real match.

## Understand and change it

Search your own notes: put one sentence per line in a file and pass `--docs notes.txt` with a question about them. The library is embedded each run; a real application would store the vectors instead.

Try smaller vectors: add `output_size=256` (or `128`) to `EmbeddingOptions` for both the library and the query. They must match. Vectors take a third or a sixth of the space, and the ranking held in our test, but the gap between a match and a non-match shrank (for our Wi-Fi example, about 0.19 at 768 numbers and about 0.10 at 128).

To build on this, retrieve the top few sentences and give them to Gemma as context, using the [Gemma example](../standalone-litert-lm/README.md); that chaining is not implemented here.

Limits: the library is eight sentences, scores are not calibrated confidence, and we tested short, clean English text, one photo, and short synthetic speech on one board.

## If something fails

| Message | Meaning |
|---|---|
| `File not found: ...` | Run the `download.py` command shown in the message. |
| `That is the Ventuno Q NPU build ... Add --backend npu.` | You gave the NPU model to the CPU run. Add the flag, or use the CPU model. |
| `NPU libraries not found` | Run `python3 scripts/setup_npu.py`. |
| `FAIL: ... no NPU activity was observed` | The embeddings ran without the NPU, most often because the CPU model was used with `--backend npu`. Use the model from `download.py embedding-npu`. |
