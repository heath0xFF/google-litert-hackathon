# App Lab: build a Gemma greeting app

Create a small app that asks Gemma 4 E2B a question and prints the answer. You'll learn how an App Lab manifest, brick, and Python entry point fit together. The local LLM brick uses **llama.cpp**, not LiteRT-LM; this is an introduction to the board before the standalone LiteRT examples.

**Requirements:** Ventuno Q, App Lab on your computer, internet for installation, and space on the board for a ~3.35 GB model plus containers. No Python installation on your computer, accessory, or cloud API key is needed.

The reference app's inference passed with App Lab 0.9.0 / App CLI 0.12.1 through the CLI. The creation steps below follow Arduino's documentation; the GUI walkthrough has not yet been verified on that image. This Gemma 4 example does not target Uno Q.

## 1. Create your app

Connect App Lab to your Ventuno Q. In **My Apps**, choose **Create new app +**, name it `Gemma Hello World`, and create it.

This app only needs Python. If the new template includes a `sketch/` folder, delete that folder from **this new app** using the File Manager's right-click menu. You do not need to compile or flash an MCU sketch for this exercise.

## 2. Add the model brick

Choose **Add Brick** and add **Large Language Model (LLM)** (`arduino:llm`), not the cloud LLM brick. In its AI model configuration, select and download **Gemma 4 E2B**. Wait for installation to finish before running.

App Lab manages `app.yaml` for you. Compare it with our [reference manifest](app.yaml): the brick's model should be `llamacpp:gemma-4-E2B_q4_0-it`. Adding a brick does not by itself mean its weights are installed.

## 3. Write the Python entry point

Open `python/main.py` in your new app. Use the short [reference program](python/main.py) to replace the generated template, following these three pieces:

1. **Configure the brick:** `LargeLanguageModel(...)` sets the system instruction, temperature, 64-token output limit, and timeout. The model itself is selected in the manifest, not this constructor.
2. **Ask a question:** `hello()` calls `llm.chat(...)`, rejects an empty answer, and prints the reply and a success marker. `raise StopIteration` ends the user loop after one call instead of generating repeatedly.
3. **Start the app:** `App.run(hello)` starts the registered brick and runs the callback. Let App Lab manage this lifecycle rather than calling `hello()` before the brick is ready.

The repository files are a working reference to compare against; you don't need to package or import them.

## 4. Run and read the result

Check that you will not interrupt someone else's running app, then select **Run**. In the **Python** console, expect a greeting followed by **`PASS: local Gemma answered`**. Wording varies; a successful launch alone is not an inference pass.

Select **Stop** afterwards, including after an error. The Python program finishes after one reply, but the model service can remain running until the app is stopped. If no reply appears, inspect the Python logs and confirm that the selected Gemma model finished downloading.

## Understand and change it

- Change the question passed to `llm.chat(...)` to ask for a one-sentence idea for an offline app. Rerun and see how the answer changes without changing the model or brick.
- Change `system_prompt` to request a different style, such as explaining things to a beginner. Keep the same question so you can see the effect of the instruction separately.

When you're comfortable with this workflow, continue to [standalone LiteRT-LM](../standalone-litert-lm/README.md) to manage the model and conversation directly from Python. An App Lab greeting using this brick demonstrates local Gemma, not LiteRT-LM integration.

UI reference: Arduino's [app creation](https://docs.arduino.cc/software/app-lab/apps/manage-apps/#create-a-new-app), [brick configuration](https://docs.arduino.cc/software/app-lab/bricks/use-bricks/), and [file editing](https://docs.arduino.cc/software/app-lab/apps/develop-apps/) instructions. Labels may differ by App Lab version.
