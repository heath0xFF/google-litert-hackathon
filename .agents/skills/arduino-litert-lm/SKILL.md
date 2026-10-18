---
name: arduino-litert-lm
description: Build or extend standalone Gemma applications with LiteRT-LM on Arduino Linux boards. Use for Engine/conversation APIs, litertlm artifacts, bounded generation, and inference measurements; not App Lab bricks or classical tensor pipelines.
---

# Standalone Gemma development

Read [AGENTS.md](../../../AGENTS.md), the [example's setup and compatibility notes](../../../examples/standalone-litert-lm/README.md), its `main.py`, and requirements. For NPU runs or image and audio input, also read the [Gemma NPU example](../../../examples/standalone-litert-lm-npu/README.md) and the [NPU guidance](../arduino-npu/SKILL.md). For source-only work, skip board operations and downloads; leave inference verification pending.

1. Before a hardware run, confirm board/OS/Python, available RAM/disk, and permission to install into an isolated workspace. Refer to [setup](../arduino-setup/SKILL.md) for missing prerequisites.
2. Start with the pinned Gemma 4 E2B `.litertlm` artifact and explicit CPU backend. For authorized board setup, run `python3 scripts/download.py gemma` from the repository root and verify the checksum. GGUF is not interchangeable with `.litertlm`.
3. Preserve the minimal engine → conversation → response flow and context-manager cleanup. Bound context and output, reject empty/oversized prompts, and handle empty responses as failures. Never add a silent cloud or non-Gemma fallback.
4. When hardware testing is authorized, run the documented text smoke check before and after the change. Distinguish model loading, generation, time-to-first-token, and peak process RSS; do not label one metric as another.
5. For sensor input, separate acquisition/validation from prompt construction and label measurements accurately. For images/audio, first verify the exact artifact, runtime API, and supported vision/audio backend. Text success does not validate multimodal inference: the NPU example takes `--image` and `--audio`, so test each input type with the exact model file.
6. Keep this CPU example unchanged. Ventuno Q NPU work has its own example and setup: follow the [NPU guidance](../arduino-npu/SKILL.md). GPU remains unvalidated. For any accelerator, confirm the exact SoC, Linux runtime libraries, artifact, and actual offload evidence; do not reuse SM8750 Android packages or infer NPU operation from discovery logs.
7. Run inference checks when hardware testing is authorized. Record the command, pinned versions, output, timing context, and limitations. Use Ventuno Q for this starter; the pinned native runtime does not support Uno Q. Do not turn setup into an Uno LLM porting project.

Use [documentation lookup](../arduino-docs/SKILL.md) when APIs differ, and [debugging](../arduino-debug/SKILL.md) for loading or generation failures. Embedding vectors for search belong to [embeddings](../arduino-embedding/SKILL.md). Reference examples are foundations for applications, not a requirement to invent new wrappers or services.
