# Standalone LiteRT: image classification

Classify an image with **MobileNet V2 and LiteRT Interpreter on CPU**. No App Lab, TensorFlow, camera, or sensor required. Model, labels, and reference image total approximately 4.3 MB, plus Python packages.

**Tested:** Ventuno Q (Ubuntu 24.04 ARM64, Python 3.12) and Uno Q 4 GB (Debian 13 ARM64, Python 3.13), using `ai-edge-litert==2.2.0`. You need SSH access and internet for installation. The tested Uno image needs an organizer-prepared Python environment as described below.

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
```

**With host pip 22.3+ (Ventuno Q):** create an isolated environment and install into it. This does not need `ensurepip` or change system Python.

```bash
python3 -m venv --without-pip .venv-litert
python3 -m pip --python .venv-litert/bin/python install -r examples/standalone-litert/requirements.txt
```

**Without host pip (including the tested Uno Q image):** ask an organizer to prepare `.venv-litert` with pip, then use this instead of the two commands above:

```bash
.venv-litert/bin/python -m pip install -r examples/standalone-litert/requirements.txt
```

On either board, download the model and test image:

```bash
python3 scripts/download.py vision
```

Downloads are pinned and SHA-256 verified. For a checksum mismatch, move any suspect cached file aside and retry; do not change the expected hash. Do not use `sudo pip` or modify package libraries to work around setup failures.

## 3. Run on the board

```bash
timeout 60 .venv-litert/bin/python examples/standalone-litert/main.py --check
```

Expect **`macaw`** first with a score near `0.9961`, **`PASS: parrot fixture classified as macaw`**, and exit status 0. Do not use Python's `-O` flag: it disables the assertions in this check.

## Understand the code

Open [main.py](main.py) and follow the input through the model:

1. **Prepare pixels:** `pixels()` corrects EXIF orientation, converts to RGB, and resizes the image. It returns **uint8 `[1,224,224,3]`**: one image, height, width, and three color channels. This model does not expect normalized floats.
2. **Run the model:** `Interpreter(...)` loads the `.tflite` file with four CPU threads. `allocate_tensors()` prepares its buffers, `set_tensor()` supplies the image, and `invoke()` performs inference. This is the Interpreter API used by our tested CPU path.
3. **Read predictions:** `get_tensor()` returns 1,001 quantized class scores. The script divides by 256 (scale `1/256`, zero point zero), ranks them, and looks up matching labels. Label zero is background; dropping it would shift every other label.

Model inputs, output quantization, and label order are one contract. If you replace the model, check all three rather than just changing the filename. The original `--check` fixture helps catch mistakes.

## Understand and change it

Try a photo that is already on the board:

```bash
.venv-litert/bin/python examples/standalone-litert/main.py --image /path/to/photo.jpg
```

Next, compare a wide shot and a close crop of the same object. Keep the supplied parrot fixture unchanged. How do the top five labels change when the background occupies less of the image? The pretrained model can only predict its existing classes; a new photo does not teach it a new label.

This is whole-image classification, not object detection or a safety check. Scores are not calibrated certainty. Timing covers one invocation, not loading, preprocessing, or camera FPS. To add a camera, start by capturing a real frame to a file; streaming and acceleration are not implemented here.

Build on this path when your application needs a class or score. Use [LiteRT-LM](../standalone-litert-lm/README.md) when it needs generated language, or combine the two only when a prediction genuinely needs an explanation.
