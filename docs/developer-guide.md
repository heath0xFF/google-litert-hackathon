# Beyond the first example

Optional background for adapting the starters. For setup and your first result, use the [README journey](../README.md#follow-the-examples).

## Two development paths, one introduction

Use **LiteRT-LM** when the application needs generated language, and **LiteRT** when a trained model should return predictions such as class scores. The App Lab greeting is an introduction to the board's app/brick workflow, not a LiteRT implementation. Starting from and modifying a working sample is enough; rebuilding its plumbing is not the exercise.

| Path | Application interface | Model format |
|---|---|---|
| [App Lab](../examples/app-lab-hello-world/README.md) | Python bricks, optionally connected to an MCU sketch | Gemma GGUF through llama.cpp |
| [LiteRT-LM](../examples/standalone-litert-lm/README.md) | Python engine and conversation | Gemma `.litertlm` |
| [LiteRT](../examples/standalone-litert/README.md) | Interpreter input/output tensors | MobileNet `.tflite` |

LiteRT runs general-purpose tensor models. LiteRT-LM adds language-model features such as tokenization, KV-cache management, and generation. App Lab's LLM brick uses llama.cpp instead: using Gemma does not automatically mean using LiteRT-LM. GGUF and `.litertlm` artifacts are not interchangeable.

App Lab manages its app containers and model services. The standalone examples use ordinary Python environments on the board; they do not depend on App Lab. Both boards also have a separate MCU, but none of these examples needs an MCU sketch.

## Change one thing at a time

- **Text generation:** change the prompt first. Keep the bounded context/output and Gemma selection. E2B is the starting model; measure memory before trying a larger one. Application generation is Gemma-only; classical ML models may be non-Gemma.
- **Image classification:** try your own image before replacing MobileNet. When replacing a model, update preprocessing, quantization, and labels together; the example README gives the current tensor contract.
- **Camera input:** first capture a real frame to a file and classify it. Gemma image input needs separate verification of the exact artifact and runtime's vision API; text generation does not prove image support.
- **Sensor input:** prove acquisition separately, then pass clearly labeled measurements to your application. Modulinos use Qwiic/I²C, not USB. Follow a board-supported Modulino/Router Bridge example and verify cables/power before wiring.

Possible projects: a motion-triggered photo classifier, a local text assistant, or a field note combining measured temperature/humidity with a short Gemma response. Start with ordinary calibrated thresholds for triggers; a learned sensor classifier needs training data and a suitable model. Do not invent missing readings or treat prototype outputs as safety guarantees.

## Compatibility and measurement

The three starters were tested on Ventuno Q with Ubuntu 24.04 ARM64/Python 3.12. The classical Interpreter example also passed on Uno Q 4 GB with Debian ARM64/Python 3.13; the Gemma starters target Ventuno only. Exact runtime pins are in each example.

Our standalone examples teach the APIs on CPU, not Qualcomm NPU deployment. GPU/NPU support depends on the SoC, OS, model, runtime, and drivers; a detected device or runner name is not proof of offload. Android/SM8750 model artifacts and QNN libraries are not interchangeable with this Linux setup. Validate backend changes as separate experiments; keep the working Interpreter CPU example intact.

Report model load time, inference/generation time, and memory separately. Single-image invocation time is not camera FPS; file size is not peak RAM. Accessories, standalone acceleration, factory-image provisioning, and disconnected startup remain unvalidated extensions. Initial model/package/container downloads need internet; App Lab testing included some cached container images.

Standalone assets are revision-pinned and checksum-verified by the download helper. App Lab manages its own model catalog. Review [upstream terms](third-party.md) before redistributing assets.

## Upstream documentation

- [Ventuno Q](https://www.arduino.cc/product-ventuno-q) / [Uno Q](https://docs.arduino.cc/hardware/uno-q/)
- [App Lab bricks](https://docs.arduino.cc/software/app-lab/tutorials/bricks/) / [examples](https://github.com/arduino/app-bricks-examples) / [brick source](https://github.com/arduino/app-bricks-py)
- [LiteRT-LM Python](https://ai.google.dev/edge/litert-lm/python) / [Gemma 4](https://ai.google.dev/edge/litert-lm/models/gemma-4)
- [Interpreter API](https://ai.google.dev/edge/litert/api_docs/python/tf/lite/Interpreter): method reference; our import is from `ai_edge_litert`, not TensorFlow
- [Modulino library](https://github.com/arduino-libraries/Arduino_Modulino) / [Router Bridge](https://github.com/arduino-libraries/Arduino_RouterBridge)
