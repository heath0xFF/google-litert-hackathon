---
name: arduino-embedding
description: Build semantic search and retrieval with EmbeddingGemma 2 and the LiteRT-LM EmbeddingEngine on Ventuno Q. Use for text, image, or audio queries, vector scoring, task prefixes, output sizes, and retrieval quality; not text generation.
---

# Semantic search with embeddings

Read [AGENTS.md](../../../AGENTS.md), the [example's setup and notes](../../../examples/standalone-embedding/README.md), its `main.py`, and requirements. For source-only work, skip board operations and downloads; leave inference verification pending.

1. Before a hardware run, confirm board/OS/Python, free disk, and permission to install into an isolated workspace; use [setup](../arduino-setup/SKILL.md) for missing prerequisites. Use Ventuno Q: the pinned native runtime is the Gemma example's, which does not support Uno Q.
2. Models are pinned and checksum-verified: `python3 scripts/download.py embedding` (CPU build, about 485 MB) or `embedding-npu` (Ventuno Q build, about 563 MB). The example uses the 740M multimodal model for text, image, and audio. Smaller text-only and text-plus-vision variants exist upstream but are not pinned here; adding one is a new dependency to discuss first.
3. Preserve the flow: `EmbeddingEngine` with a backend per modality → `compute_embedding_batch` for the library → `compute_embedding` for the query → dot product, with context-manager cleanup. Give the image and audio backends only when those inputs are used, except as the NPU build requires (below).
4. Text takes short task prefixes: `task: search result | query: ...` for a search query and `title: none | text: ...` (or `title: <title> | text: ...`) for library items. Other tasks, such as classification or similarity, use other prefixes listed on the model card. Pictures and audio get none. Omitting prefixes still works but is less precise.
5. Use `EmbeddingOptions(normalize=True)` so a dot product is cosine similarity. Embed the library and the query with the same model build and the same `output_size` (the card lists 128, 256, 512, and 768). Scores from different builds, such as CPU and NPU, are not comparable; only the ranking carries over.
6. Judge retrieval by rank and by the gap to the runner-up. A list always has a winner, and a query with no match still scores something. Never present scores as probabilities or confidence. Test against fixtures with a known winner (the example's `--check`), and use real inputs, never invented ones.
7. Inputs: any image size is scaled by the runtime; audio is short speech. On the Ventuno Q NPU, text and images run on the NPU and audio runs on the CPU, and the NPU build will not start unless audio is given the CPU backend. Follow [NPU guidance](../arduino-npu/SKILL.md) for `--backend npu`, setup, and evidence.
8. Keep scale honest. The example re-embeds a small library on every run. Store vectors for more than a few hundred items, and discuss any vector database or index dependency before adding it. Keep the existing size guards.
9. Embeddings find matches; they do not write answers. To answer a question, hand the top results to Gemma as context using [LiteRT-LM](../arduino-litert-lm/SKILL.md). Application text generation stays Gemma-only.

Use [documentation lookup](../arduino-docs/SKILL.md) for API and model-card questions and [debugging](../arduino-debug/SKILL.md) for startup, scoring, or NPU failures.
