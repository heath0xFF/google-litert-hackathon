# Third-party assets

Runtime packages and downloaded models retain their upstream licenses and notices. The links below identify their sources; they do not replace the license texts or grant permission to redistribute unrelated SDKs.

| Component / asset | Source and terms to review |
|---|---|
| LiteRT | [google-ai-edge/LiteRT](https://github.com/google-ai-edge/LiteRT), Apache-2.0; inspect dependencies/notices of the shipped package |
| LiteRT-LM | [google-ai-edge/LiteRT-LM](https://github.com/google-ai-edge/LiteRT-LM), Apache-2.0; inspect package notices |
| Gemma 4 E2B LiteRT-LM artifact | [Model card](https://huggingface.co/litert-community/gemma-4-E2B-it-litert-lm), labeled Apache-2.0 |
| Gemma 4 E2B Q4 GGUF | [Google model card](https://huggingface.co/google/gemma-4-E2B-it-qat-q4_0-gguf), labeled Apache-2.0 |
| MobileNet V2, labels, parrot test JPEG | [google-coral/test_data](https://github.com/google-coral/test_data/tree/104342d2d3480b3e66203073dac24f4e2dbb4c41), repository contains an [Apache-2.0 license](https://github.com/google-coral/test_data/blob/104342d2d3480b3e66203073dac24f4e2dbb4c41/LICENSE); review any asset-specific attribution before repackaging |
| Arduino App Bricks | [arduino/app-bricks-py](https://github.com/arduino/app-bricks-py), MPL-2.0 with separately licensed runtime/container dependencies |

Models and reference images are retrieved from their upstream hosts into ignored directories, not redistributed in this repository. The Coral model is the ordinary `.tflite` file, **not** its Edge TPU-compiled counterpart. No Coral hardware is needed.

Do not commit proprietary Qualcomm libraries, SDK archives, credentials, cached containers, or work-network inventory. A public model download does not grant permission to redistribute unrelated accelerator SDKs.
