# Image Production Policy

Apply this policy before generation/editing and again before delivery. It is a
workflow gate, not legal advice.

## Rights, Consent, and Authenticity

- Ask the user to confirm they have permission to upload and transform
  reference images when ownership or authorization is not clear.
- Obtain explicit confirmation before identity-sensitive work involving a
  private person, biometric likeness, a child, medical context, or intimate
  context. Do not infer consent from possession of a file.
- Preserve trademarked and branded assets only when the requested use is
  authorized. Never describe generated marks as official or exact without
  verification against supplied source artwork.
- Do not remove watermarks, signatures, provenance marks, or safety labels.
  A rights-holder may request restoration of their own damaged source, but the
  delivered record must retain the source and transformation history.
- Clearly label synthetic or materially edited imagery where omission could
  mislead viewers. Never fabricate provenance or claim a C2PA credential,
  invisible watermark, or authenticity guarantee that was not actually created.

## Privacy and Data Minimization

- Reference images are sent to the selected external provider. Say so before
  uploading sensitive material and use only the minimum necessary inputs.
- Do not include secrets, private identifiers, precise location data, or
  unrelated people in prompts or references. Crop/redact locally where possible.
- Do not promise metadata removal. For sensitive delivery, inspect the actual
  output and strip EXIF/location metadata with an appropriate local tool, then
  verify the cleaned file.
- Keep provider responses, prompts, and source assets out of public paths unless
  the user asked for publication.

## Safety and Provider Errors

- Keep provider moderation enabled. A less restrictive documented setting is
  not permission to evade policy.
- For `moderation_blocked` or another image-generation user error, do not retry
  the same request automatically and do not disguise, split, or euphemize the
  request to bypass safeguards.
- Give the user a generic safety message. In developer diagnostics, retain the
  request ID, stable error code, provider, moderation stage, and coarse public
  categories when available; do not expose internal classifiers or scores.
- Retry only transient failures such as rate limits or server errors, using
  bounded backoff. A blocked/user-error retry requires a substantive,
  policy-compliant change to the user request or inputs.

## Accessibility and Delivery

- Supply concise alt text that describes the image's purpose and meaningful
  visual content. For informative images, also provide any literal on-image text
  as a plain-text transcript.
- Check legibility, contrast, color dependence, cropping, and safe areas at the
  intended display size. Treat model-rendered text as draft copy until verified.
- Record at minimum: artifact ID/path, timestamp, provider/model, prompt or
  prompt hash according to privacy needs, parameters, source hashes, parent
  artifact, edit history, rights/consent assertion, QA result, approver, and alt
  text. Use `imagen:schemas/artifact-manifest.schema.json` when writing a machine-readable record.
- When Gemini Google Search grounding is enabled, preserve and display the
  provider-returned Search Suggestions and source citations with the grounded
  result. If the active client cannot present that material, do not enable
  grounding.

Authoritative OpenAI behavior references:

- https://developers.openai.com/api/docs/guides/image-generation#customize-image-output
- https://developers.openai.com/api/docs/guides/image-generation#edit-images
- https://developers.openai.com/api/docs/guides/image-generation#handling-blocked-requests-and-other-errors
