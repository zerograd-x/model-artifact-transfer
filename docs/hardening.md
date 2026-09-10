# Hardening ideas

The baseline implementation deliberately keeps the transfer contract small.
Production deployments may want to add:

- Resolve and record the immutable source revision rather than relying only on a
  symbolic branch or tag.
- Add `allow_patterns` / `ignore_patterns` for source materialization to avoid
  transferring unnecessary artifact variants.
- Generate a manifest containing source identity, file paths, sizes, and
  checksums before publish.
- Verify expected model/config/tokenizer files and sharded-weight indexes before
  accepting an artifact.
- Upload to a unique staging prefix, verify every object, then publish a small
  manifest or pointer that marks the artifact complete.
- Add skip-if-identical behavior based on the manifest rather than destination
  existence alone.
- Add resumable multipart or per-file retry semantics for large artifacts.
- Record total bytes and object count before and after publish.
- Define an explicit cleanup procedure for abandoned partial prefixes.
