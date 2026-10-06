"""Classify an image with the pinned uint8 MobileNet V2 and LiteRT Interpreter on CPU."""
import argparse
from pathlib import Path
import time

import numpy as np
from PIL import Image, ImageOps
from ai_edge_litert.interpreter import Interpreter

ROOT = Path(__file__).resolve().parents[2]
ASSETS = ROOT / "models"


def pixels(path):
    # Phone photos may store rotation in EXIF rather than in the pixels.
    # Apply it before resizing so inference sees the same orientation as a viewer.
    with Image.open(path) as image:
        image = ImageOps.exif_transpose(image).convert("RGB").resize((224, 224), Image.Resampling.BILINEAR)
        # This pinned model expects uint8 RGB, not normalized float inputs.
        # Add the batch dimension to produce [1, 224, 224, 3].
        return np.asarray(image, dtype=np.uint8)[None].copy()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--image", type=Path, default=ASSETS / "parrot.jpg")
    parser.add_argument("--check", action="store_true", help="Check the bundled parrot fixture")
    args = parser.parse_args()
    if args.check and args.image != ASSETS / "parrot.jpg":
        parser.error("--check uses only the bundled parrot image")
    paths = [args.image, ASSETS / "mobilenet_v2_1.0_224_quant.tflite", ASSETS / "imagenet_labels.txt"]
    if not all(path.is_file() for path in paths):
        parser.error("Input/model/labels missing. Run: python3 scripts/download.py vision")
    # Label indices must match the model output, including background at zero.
    # Dropping that first entry would shift every prediction to the wrong label.
    labels = paths[2].read_text().splitlines()
    if len(labels) != 1001:
        raise ValueError("Expected the pinned 1001-label file, including background at index 0")
    model = Interpreter(model_path=str(paths[1]), num_threads=4)
    # Loading the model does not allocate its tensor buffers. Allocate before
    # setting input; obtain tensor indices from metadata rather than guessing.
    model.allocate_tensors()
    input_tensor, output_tensor = model.get_input_details()[0], model.get_output_details()[0]
    input_data = pixels(args.image)
    model.set_tensor(input_tensor["index"], input_data)
    # Measure only invocation, excluding model loading and image preparation.
    # This is a single-image measurement, not camera throughput.
    started = time.perf_counter()
    model.invoke()
    elapsed = time.perf_counter() - started
    # Dequantization is (value - zero_point) * scale. For this pinned model,
    # zero_point=0 and scale=1/256, so division suffices. Recheck both values
    # when replacing the model; these scores are not calibrated certainty.
    scores = model.get_tensor(output_tensor["index"])[0].astype(np.float32) / 256
    ranking = np.argsort(-scores, kind="stable")[:5]
    for index in ranking:
        print(f"{scores[index]:.4f}  {labels[index]}")
    print(f"backend=CPU; inference={elapsed*1000:.1f} ms (one invocation, not camera FPS)")
    # Check the model contract and a known prediction, not just that invoke
    # returned. Run without Python's -O flag, which removes these assertions.
    if args.check:
        assert input_data.shape == (1, 224, 224, 3)
        assert input_data.dtype == input_tensor["dtype"] == np.uint8
        assert tuple(output_tensor["shape"]) == (1, 1001)
        assert output_tensor["dtype"] == np.uint8
        assert output_tensor["quantization"] == (1 / 256, 0)
        assert labels[ranking[0]] == "macaw" and scores[ranking[0]] > 0.5
        print("PASS: parrot fixture classified as macaw")


if __name__ == "__main__":
    main()
