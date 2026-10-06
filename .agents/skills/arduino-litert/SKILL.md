---
name: arduino-litert
description: Build classical vision, audio, or sensor inference with LiteRT Interpreter on Arduino Linux boards. Use for tflite models, preprocessing, tensor buffers, quantization, labels, and backend validation; not Gemma conversations.
---

# Classical inference development

Read [AGENTS.md](../../../AGENTS.md), the [example's setup and compatibility notes](../../../examples/standalone-litert/README.md), its `main.py`, and requirements. For source-only work, skip board operations and downloads; leave inference verification pending.

1. Confirm the intended task. Before hardware execution, confirm board/OS/Python and use [setup](../arduino-setup/SKILL.md) if the environment is not ready. Non-Gemma classical models are allowed.
2. Check board compatibility before downloads. The same Interpreter CPU starter is tested on Ventuno Q and Uno Q 4 GB. Reproduce the MobileNet V2 check with `--check`; a simulated fixture or package import is not hardware inference. Do not introduce API-selection flags, accelerator delegates, or library-removal workarounds into this CPU starter without an explicit requirement.
3. Before replacing a model, inspect its input/output names, shapes, dtypes, quantization scale/zero-point, preprocessing, and label ordering. Treat these as one model-specific contract, not interchangeable settings.
4. The supplied model expects RGB uint8 `[1,224,224,3]`; outputs have 1001 classes including background, scale 1/256, zero-point zero. Those assumptions must not leak into a different model. Do not normalize to float unless the new model requires it.
5. Preserve the Interpreter → allocate tensors → set input → invoke → decode output flow. Add one deterministic fixture that fails if preprocessing or labels break. Use the existing dependencies before introducing another framework.
6. For camera/audio/sensor work, prove acquisition separately and validate real data before inference. Whole-image classification does not provide detection boxes, PPE detection, or safety guarantees. Sensor classifiers require a suitable trained model; thresholds often need only ordinary code.
7. Start with CPU. Verify GPU/NPU support for the exact board/model/build rather than copying Android libraries or assuming Uno Q has Ventuno's NPU. Report end-to-end latency separately from a single invocation.
8. Run repository checks and, when hardware testing is authorized, the inference fixture; record measured board results and gaps. Keep dependencies/models pinned and download weights rather than committing them.

Use [documentation lookup](../arduino-docs/SKILL.md) for unknown tensor/backend APIs and [debugging](../arduino-debug/SKILL.md) for failures.
