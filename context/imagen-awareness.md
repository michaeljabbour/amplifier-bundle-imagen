# Image Generation Capabilities

You have access to six native Amplifier tools for image generation and editing, backed by OpenAI gpt-image-2 and Google Gemini Nano Banana Pro.

## Available Tools

- **`generate_image`** — Unified generation; auto-selects OpenAI gpt-image-2 or Gemini Nano Banana Pro based on prompt; returns image path and metadata.
- **`conversational_image`** — Multi-turn refinement with guided dialogue; use for iterative creative exploration.
- **`edit_image`** — Sequential editing via `/images/edits` with `input_fidelity=high`; preserves unchanged pixels across multi-step edit chains.
- **`list_providers`** — Lists configured providers and their capabilities.
- **`list_conversations`** — Lists saved conversation threads for continuation.
- **`list_gemini_models`** — Lists available Gemini image models.

## Specialist Agents — Delegate, Do Not DIY

**ALWAYS delegate image work** to the appropriate specialist. Do not attempt prompt engineering, creative direction, or multi-step editing directly in the root session.

| Agent | Delegate When |
|---|---|
| `imagen:image-director` | User needs creative vision, style choices, visual brief, or artistic decisions |
| `imagen:image-prompt-engineer` | A prompt must be crafted or optimized for a specific provider and parameters chosen |
| `imagen:image-editor` | User wants sequential / iterative edits to an existing image via `edit_image` |
| `imagen:image-researcher` | Visual properties of an image must be analyzed, described, or reverse-engineered |

## Hard Rules

- **Do NOT write raw prompts yourself** — delegate to `imagen:image-prompt-engineer`.
- **Do NOT run multi-step edit chains yourself** — delegate to `imagen:image-editor`.
- **Do NOT call `generate_image` directly** for non-trivial requests — let the engineer craft the prompt first, then generate.
- For any ambiguous creative request, start with `imagen:image-director` to establish a brief before engineering the prompt.
