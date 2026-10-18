"""One bounded Gemma turn on the Hexagon NPU, with optional image or audio input. Run on the board."""
import argparse
from pathlib import Path
import resource
import sys
import time

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
import npu_runtime  # shared NPU plumbing: library paths, runtime swap, NPU evidence check


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", type=Path, default=None,
                        help="NPU .litertlm file (default: the only Gemma models/*qcs8275*.litertlm)")
    parser.add_argument("--prompt", default="Say hello to the Google and Qualcomm hackathon in one sentence.")
    parser.add_argument("--image", type=Path, help="PNG or JPG to describe or read")
    parser.add_argument("--audio", type=Path, help="WAV (16 kHz mono is a safe choice) to transcribe or answer about")
    args = parser.parse_args()
    if args.model is None:
        # The embedding example's NPU model is also named *QCS8275*, so leave embedding files out.
        candidates = sorted(path for path in (ROOT / "models").glob("*.litertlm")
                            if "qcs8275" in path.name.lower() and "embedding" not in path.name.lower())
        if len(candidates) != 1:
            parser.error("Pass --model PATH. Expected exactly one Gemma models/*qcs8275*.litertlm file; "
                         f"found {len(candidates)}. See this example's README for the download.")
        args.model = candidates[0]
    for name in ("model", "image", "audio"):
        path = getattr(args, name)
        if path is not None and not path.is_file():
            parser.error(f"--{name} file not found: {path}")
    # Early input guard, not a token count; the engine's context is still the real limit.
    if not args.prompt.strip() or len(args.prompt) > 4000:
        parser.error("Use a nonempty prompt of at most 4000 characters; the context is bounded.")

    # May restart this program once with the environment the NPU libraries need.
    npu_runtime.ensure_env()
    npu_runtime.redirect_native_logs()  # the NPU libraries are chatty; details go to npu/last-run.log
    import litert_lm as lm
    npu_runtime.use_bundled_litertlm()

    # The only differences from the CPU example: the backend, and where the NPU libraries are.
    # Image and audio encoders are separate parts of the model; give them the NPU only when used.
    npu = lm.Backend.NPU(litert_dispatch_lib_dir=str(npu_runtime.QNN_LIB))
    started = time.perf_counter()
    with lm.Engine(str(args.model), backend=npu,
                   vision_backend=npu if args.image else None,
                   audio_backend=npu if args.audio else None) as engine:
        loaded = time.perf_counter()
        interrupts_before = npu_runtime.cdsp_interrupts()
        with engine.create_conversation(
            max_output_tokens=128,
            thinking_config=lm.ThinkingConfig(enable_thinking=False, thinking_token_budget=0),
        ) as conversation:
            # A message with media is a list of parts; the model reads them together with the text.
            if args.image or args.audio:
                parts = [{"type": "image", "path": str(args.image.resolve())}] if args.image else []
                parts += [{"type": "audio", "path": str(args.audio.resolve())}] if args.audio else []
                message = {"role": "user", "content": parts + [{"type": "text", "text": args.prompt}]}
            else:
                message = args.prompt
            response = conversation.send_message(message)
            text = "".join(item["text"] for item in response.get("content", []) if item.get("type") == "text")
        generated = time.perf_counter()
        used, evidence = npu_runtime.check_npu_used(interrupts_before, npu_runtime.cdsp_interrupts())
    if not text.strip():
        raise RuntimeError("Gemma returned no text; inspect the runtime logs")
    print(text, flush=True)
    print(evidence)
    if not used:
        npu_runtime.fail("FAIL: Gemma answered but no NPU activity was observed")
    print(f"PASS: local Gemma answered; backend=NPU; image={'NPU' if args.image else 'off'}; "
          f"audio={'NPU' if args.audio else 'off'}; load={loaded-started:.2f}s; generation={generated-loaded:.2f}s; "
          f"process_peak_rss={resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024:.0f} MiB")


if __name__ == "__main__":
    main()
