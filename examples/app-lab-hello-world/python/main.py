from arduino.app_bricks.llm import LargeLanguageModel
from arduino.app_utils import App

# App Lab selects the local model through app.yaml. These settings control
# the reply, not model selection; keep the greeting short and time-bounded.
llm = LargeLanguageModel(
    system_prompt="Answer briefly, in plain text.",
    temperature=0,
    max_tokens=64,
    timeout=120,
)


def hello():
    response = llm.chat("Say hello to the Google and Qualcomm hackathon in one sentence.")
    # A running model service is not enough: the smoke check needs a reply.
    if not response.strip():
        raise RuntimeError("Gemma returned an empty response")
    print(response, flush=True)
    print("PASS: local Gemma answered", flush=True)
    # App repeats this callback by default. Stop after one greeting; the user
    # must still stop the app in App Lab to release the model service.
    raise StopIteration


# App starts the brick before invoking hello. Calling hello directly would
# bypass that lifecycle and could send a request before the service is ready.
App.run(hello)
