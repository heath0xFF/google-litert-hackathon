---
name: arduino-debug
description: Diagnose Arduino App Lab, LiteRT-LM, LiteRT, embedding, or NPU failures using logs and reproducible checks. Use for failed setup, missing models, wrong predictions or poor retrieval, memory pressure, camera/sensor issues, or suspected backend problems. Do not rebuild a working app by default.
---

# Evidence-first debugging

Read [AGENTS.md](../../../AGENTS.md) and the affected example's README and source end to end; setup gotchas are documented beside its commands. Ask for the failing command and relevant redacted error if absent.

1. Establish which machine produced the error, board identity, OS/runtime/model versions, recent changes, and current workloads. Gather the smallest relevant logs; don't dump environments, auth files, or unrelated user data.
2. If execution is authorized, reproduce using the existing smoke check, with the user's permission for any app interruption. Otherwise analyze supplied logs/source and label the diagnosis unconfirmed. Separate connection/provisioning, model loading, input preparation, inference, and output interpretation failures.
3. Follow the evidence:
   - No pip/ensurepip: request appropriate provisioning; never sudo pip or silently alter system Python.
   - Missing weights: distinguish catalog, installed model, and app import; use the documented download path.
   - Hash mismatch: preserve any existing suspect file, verify the pinned source, and retry only as appropriate. The download helper intentionally removes incomplete/bad temporary downloads. Never change a checksum merely to accept the failing file.
   - Wrong class: verify dtype/shape, quantization, preprocessing, background offset, and matching labels before changing the model.
   - Killed/slow process: inspect RAM, swap, disk, and competing workloads. Do not silently enable swap, cloud offload, or a larger model.
   - Accelerator warning: identify the selected backend and actual exit/result before diagnosing failed CPU inference. A `NPU accelerator could not be loaded` warning is printed on healthy CPU runs.
   - NPU setup: `NPU libraries not found` means run `python3 scripts/setup_npu.py`. `Cannot open /dev/fastrpc-cdsp` means the account lacks the `fastrpc` group: ask the user or an organizer, and do not change permissions yourself. A checksum mismatch means run the script again; never edit a pin to accept the file.
   - `FAIL: ... no NPU activity was observed`: the work finished on the CPU. Check that the model file is the QCS8275 build for the NPU backend before suspecting the libraries, and do not weaken or remove the check.
   - NPU engine will not start: compare the QAIRT version inside the model file with the downloaded libraries (see [NPU guidance](../arduino-npu/SKILL.md)). For audio on the NPU, confirm the pinned `litert-lm-api` (0.17.1 failed with `Some ops are not accelerated`; 0.18.0 works for Gemma), and for EmbeddingGemma that audio is given the CPU backend.
   - Native log flood: NPU runs write the libraries' output to `npu/last-run.log`; read its tail. Memory-handle errors at shutdown were harmless in our runs when the result and exit status were good; investigate them only if the result is wrong.
   - Poor retrieval: check the task prefixes, normalization, that the query and library share one model build and `output_size`, and the gap between first and second place, before changing models.
   - Missing peripheral: distinguish device nodes from actual hardware. No fabricated readings or inferred camera access.
4. State a root-cause hypothesis and the smallest diagnostic that distinguishes it from alternatives. Read every caller of code you intend to change; fix shared causes rather than patching one symptom.
5. Make one justified change within the authorized scope, rerun available checks, and record before/after evidence. If hardware is unavailable, leave the original failing board check and inference baseline pending. Stop if evidence contradicts the hypothesis.

Do not upgrade firmware, change network settings, disable security checks, stop unrelated workloads, or erase caches/models as a blanket repair. Ask first when a disruptive action is genuinely needed. Use [arduino-docs](../arduino-docs/SKILL.md) for version-specific APIs. Report unresolved issues honestly instead of converting an attempted fix into a PASS.
