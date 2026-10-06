---
name: arduino-debug
description: Diagnose Arduino App Lab, LiteRT-LM, or LiteRT failures using logs and reproducible checks. Use for failed setup, missing models, wrong predictions, memory pressure, camera/sensor issues, or suspected backend problems. Do not rebuild a working app by default.
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
   - Accelerator warning: identify the selected backend and actual exit/result before diagnosing failed CPU inference.
   - Missing peripheral: distinguish device nodes from actual hardware. No fabricated readings or inferred camera access.
4. State a root-cause hypothesis and the smallest diagnostic that distinguishes it from alternatives. Read every caller of code you intend to change; fix shared causes rather than patching one symptom.
5. Make one justified change within the authorized scope, rerun available checks, and record before/after evidence. If hardware is unavailable, leave the original failing board check and inference baseline pending. Stop if evidence contradicts the hypothesis.

Do not upgrade firmware, change network settings, disable security checks, stop unrelated workloads, or erase caches/models as a blanket repair. Ask first when a disruptive action is genuinely needed. Use [arduino-docs](../arduino-docs/SKILL.md) for version-specific APIs. Report unresolved issues honestly instead of converting an attempted fix into a PASS.
