"""One bounded, CPU-only Gemma turn. Run on the board, not your laptop."""
import argparse
from pathlib import Path
import resource
import time

import litert_lm as lm

ROOT = Path(__file__).resolve().parents[2]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", type=Path, default=ROOT / "models/gemma-4-E2B-it.litertlm")
    parser.add_argument("--prompt", default="Say hello to the Google and Qualcomm hackathon in one sentence.")
    args = parser.parse_args()
    if not args.model.is_file():
        parser.error("Model missing. Run: python3 scripts/download.py gemma")
    # This is an early input guard, not a token count. Unusual text can still
    # exceed the engine's context limit even when it fits this character limit.
    if not args.prompt.strip() or len(args.prompt) > 4000:
        parser.error("Use a nonempty prompt of at most 4000 characters; the context is bounded.")

    # Keep the tested CPU path explicit. The context limit bounds the token
    # capacity; the with block releases engine resources even if generation fails.
    started = time.perf_counter()
    with lm.Engine(str(args.model), backend=lm.Backend.CPU(thread_count=4), max_num_tokens=2048) as engine:
        loaded = time.perf_counter()
        # Conversation state belongs to this block. Send follow-up messages
        # here to retain history; a new invocation starts a fresh conversation.
        # Disable thinking and cap the reply for this short greeting example.
        with engine.create_conversation(
            max_output_tokens=128,
            thinking_config=lm.ThinkingConfig(enable_thinking=False, thinking_token_budget=0),
        ) as conversation:
            response = conversation.send_message(args.prompt)
            # The response contains typed content blocks, not a plain string.
            # Read text blocks only; a response without text is not a passing run.
            text = "".join(item["text"] for item in response.get("content", []) if item.get("type") == "text")
            if not text.strip():
                raise RuntimeError("Gemma returned no text; inspect the runtime logs")
            print(text, flush=True)
            # Generation timing includes conversation setup and response handling.
            # On Linux, ru_maxrss is the process high-water mark in KiB, not the
            # model's allocation alone. Divide by 1024 to report MiB.
            print(f"PASS: local Gemma answered; backend=CPU; load={loaded-started:.2f}s; "
                  f"generation={time.perf_counter()-loaded:.2f}s; "
                  f"process_peak_rss={resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024:.0f} MiB")


if __name__ == "__main__":
    main()
