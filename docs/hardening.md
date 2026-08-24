# Hardening ideas

The baseline implementation is intentionally small. Production deployments may want
to add some or all of the following safeguards:

- Add `revision` to the config and pin a Hugging Face commit SHA.
- Add `allow_patterns` / `ignore_patterns` to avoid duplicate `.bin`, GGUF, ONNX, or
  other unnecessary artifacts.
- Publish atomically: upload to a staging destination, verify it, then rename/promote.
- Write a manifest containing repository id, commit SHA, file names, sizes, and
  checksums.
- Validate or derive the destination model name from `hf_repo_id`.
- Refuse an existing destination by default and require explicit replacement.
- Add skip-if-identical behavior and resumable uploads.
- Verify shard count, `model.safetensors.index.json`, tokenizer/config files, and total
  bytes before publishing.
