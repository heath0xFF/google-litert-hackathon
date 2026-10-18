"""Semantic search with EmbeddingGemma 2: rank a few sentences by meaning, using a text, image, or audio query.

Run on the board. Add --backend npu to run on the Ventuno Q's NPU (run scripts/setup_npu.py once first).
"""
import argparse
from pathlib import Path
import resource
import sys
import time

ROOT = Path(__file__).resolve().parents[2]
CPU_MODEL = ROOT / "models" / "embeddinggemma-2-740m.litertlm"
NPU_MODEL = ROOT / "models" / "embeddinggemma-2-740m_Qualcomm_QCS8275.litertlm"

# A tiny library to search. Replace it with your own sentences using --docs FILE (one per line).
DOCS = [
    "The macaw is a large, colorful parrot native to the Americas.",
    "To connect the board to Wi-Fi, open the network settings and choose your access point.",
    "Sourdough bread needs a long fermentation with wild yeast.",
    "A soil moisture sensor reports how wet the ground around a plant is.",
    "The northern lights are caused by charged particles from the sun.",
    "A neural processing unit runs machine learning models faster and with less power than a CPU.",
    "Marathon runners should hydrate and pace themselves in the first miles.",
    "Modulino sensor modules plug into the board with Qwiic cables.",
]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    query = parser.add_mutually_exclusive_group()
    query.add_argument("--query", default="How do I get my board online?", help="text to search for")
    query.add_argument("--image", type=Path, help="search with a picture instead of text")
    query.add_argument("--audio", type=Path, help="search with a spoken clip instead of text (WAV, 16 kHz mono is safest)")
    parser.add_argument("--docs", type=Path, help="text file with one sentence per line (default: a built-in library)")
    parser.add_argument("--backend", choices=["cpu", "npu"], default="cpu",
                        help="cpu (default), or npu: the Hexagon NPU; run scripts/setup_npu.py once first")
    parser.add_argument("--model", type=Path, help="override the model file")
    parser.add_argument("--top", type=int, default=3, help="how many results to show")
    parser.add_argument("--check", action="store_true", help="run the fixed text and image checks")
    args = parser.parse_args()
    npu = args.backend == "npu"
    model = args.model or (NPU_MODEL if npu else CPU_MODEL)
    parrot = ROOT / "models" / "parrot.jpg"
    for path in (model, args.docs, args.image, args.audio):
        if path is not None and not path.is_file():
            parser.error(f"File not found: {path}. Models: python3 scripts/download.py "
                         f"{'embedding-npu' if npu else 'embedding'}; the test photo: python3 scripts/download.py vision")
    if not npu and "qcs8275" in model.name.lower():
        parser.error("That is the Ventuno Q NPU build of the model, which only runs on the NPU. Add --backend npu.")
    if args.check and (args.docs or args.image or args.audio or not parrot.is_file()):
        parser.error("--check uses the built-in library and models/parrot.jpg only (python3 scripts/download.py vision)")
    docs = DOCS if args.docs is None else [line.strip() for line in args.docs.read_text().splitlines() if line.strip()]
    if not docs or len(docs) > 1000 or not args.query.strip() or len(args.query) > 2000:
        parser.error("Use 1 to 1000 sentences and a nonempty query of at most 2000 characters.")

    if npu:
        # Shared NPU plumbing lives in scripts/npu_runtime.py: library paths, an NPU-use check, quiet logs.
        sys.path.insert(0, str(ROOT / "scripts"))
        import npu_runtime
        npu_runtime.ensure_env()  # may restart this program once with the environment the NPU libraries need
        npu_runtime.redirect_native_logs()
    import litert_lm as lm
    if not npu:
        lm.set_min_log_severity(lm.LogSeverity.ERROR)  # keep the terminal to the results

    # Choose a backend for each part of the model: text, image, and audio. On the Ventuno Q's NPU the model
    # runs text and images. The model card lists audio as unsupported on this NPU, and this model build will
    # not start unless audio is given a backend, so audio always gets the CPU.
    use_image = bool(args.image) or args.check
    if npu:
        accelerator = lm.Backend.NPU(litert_dispatch_lib_dir=str(npu_runtime.QNN_LIB))
        backends = dict(backend=accelerator, vision_backend=accelerator if use_image else None,
                        audio_backend=lm.Backend.CPU())
    else:
        backends = dict(backend=lm.Backend.CPU(), vision_backend=lm.Backend.CPU() if use_image else None,
                        audio_backend=lm.Backend.CPU() if args.audio else None)

    # normalize=True makes every vector length 1, so a plain dot product below is cosine similarity.
    options = lm.EmbeddingOptions(normalize=True)

    def search(engine, query):
        """Embed the library and the query, and return (ranked results, seconds for the query)."""
        # EmbeddingGemma 2 expects short task prefixes on text: one for search queries, one for documents.
        # Pictures and audio are passed as they are, with no prefix.
        library = [d.embedding for d in engine.compute_embedding_batch([f"title: none | text: {doc}" for doc in docs], options)]
        if isinstance(query, str):
            query = f"task: search result | query: {query}"
        started = time.perf_counter()
        vector = engine.compute_embedding(query, options).embedding
        elapsed = time.perf_counter() - started
        scores = [sum(q * d for q, d in zip(vector, doc)) for doc in library]
        return sorted(zip(scores, docs), reverse=True), elapsed, len(vector)

    started = time.perf_counter()
    with lm.EmbeddingEngine(str(model), **backends) as engine:
        loaded = time.perf_counter()
        interrupts_before = npu_runtime.cdsp_interrupts() if npu else None
        if args.image:
            label, query = f"image {args.image.name}", lm.Content.ImageFile(str(args.image.resolve()))
        elif args.audio:
            label, query = f"audio {args.audio.name}", lm.Content.AudioFile(str(args.audio.resolve()))
        else:
            label, query = f'"{args.query}"', args.query
        ranked, query_seconds, size = search(engine, query)
        print(f"Query: {label}   ({size}-number vectors)")
        for rank, (score, doc) in enumerate(ranked[:args.top], 1):
            print(f"{rank}. {score:.3f}  {doc}")
        if args.check:
            # A fixed contract: the Wi-Fi sentence answers the Wi-Fi question, and the parrot photo
            # is closest to the macaw sentence. The picture is compared with sentences, not with a label.
            assert "Wi-Fi" in ranked[0][1], ranked[0]
            picture_ranked, picture_seconds, _ = search(engine, lm.Content.ImageFile(str(parrot)))
            print(f"Query: image parrot.jpg\n1. {picture_ranked[0][0]:.3f}  {picture_ranked[0][1]}")
            assert "macaw" in picture_ranked[0][1], picture_ranked[0]
        used, evidence = npu_runtime.check_npu_used(interrupts_before, npu_runtime.cdsp_interrupts()) if npu else (True, "")
    print(f"backend={args.backend.upper()}; load={loaded-started:.2f}s; one query embedded in {query_seconds*1000:.1f} ms; "
          f"process_peak_rss={resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024:.0f} MiB")
    if npu:
        print(evidence)
        if not used:
            npu_runtime.fail("FAIL: embeddings were computed but no NPU activity was observed")
    if args.check:
        print("PASS: Wi-Fi sentence found for a Wi-Fi question; parrot photo matched the macaw sentence"
              + (" on the NPU" if npu else ""))


if __name__ == "__main__":
    main()
