# Tool Reference

Exhaustive parameter reference for all six `imagegen` MCP tools, return value shapes, and typical use cases. For prompt engineering guidance, see `PROMPT_ENGINEERING_GUIDE.md`. For provider selection, see `PROVIDER_COMPARISON.md`.

---

## generate_image

Unified image generation with automatic provider selection. The primary generation tool.

### Signature

```python
generate_image(
    prompt: str,                              # Required
    provider: "auto" | "openai" | "gemini",  # Default: "auto"
    
    # OpenAI gpt-image-2 parameters
    quality: "auto" | "low" | "medium" | "high",      # Default: "auto"
    size: str,                                          # Default: "auto"
    background: "auto" | "transparent" | "opaque",     # Default: "auto"
    openai_output_format: "png" | "jpeg" | "webp",    # Default: None
    openai_output_compression: int,                    # 0–100; Default: None
    moderation: "auto" | "low",                        # Default: None
    n: int,                                            # 1–10; Default: None
    openai_model: str,                                 # Default: "gpt-image-2"
    
    # Gemini parameters
    size: "1K" | "2K" | "4K",                        # Gemini size (separate from OpenAI size)
    aspect_ratio: str,                                 # Default: None
    reference_images: list[str],                       # Base64-encoded; Default: None
    enable_google_search: bool,                        # Default: False
    gemini_model: str,                                 # Default: None (uses server default)
    
    # Shared parameters
    enhance_prompt: bool,                              # Default: True
    output_path: str,                                  # Optional — save path
    output_format: "markdown" | "json",                # Tool response format; Default: "markdown"
)
```

### Provider-Specific Size Options

**OpenAI sizes:**
| Value | Dimensions | Use Case |
|-------|-----------|----------|
| `"auto"` | Model chooses | General default |
| `"1024x1024"` | 1024×1024 | Square — social, avatar |
| `"1536x1024"` | 1536×1024 | Landscape — website hero |
| `"1024x1536"` | 1024×1536 | Portrait — mobile, story |
| `"1792x1024"` | 1792×1024 | Widescreen — cinematic |
| `"1024x1792"` | 1024×1792 | Tall portrait — app store |
| `"512x512"` | 512×512 | Quick iteration |
| `"256x256"` | 256×256 | Thumbnail / icon test |

**Gemini sizes:**
| Value | Approx. Output | Use Case |
|-------|---------------|----------|
| `"1K"` | ~1024px long edge | Fast iteration |
| `"2K"` | ~2048px long edge | Standard delivery |
| `"4K"` | ~4096px long edge | Print, large display |

### Aspect Ratio (Gemini only)

| Value | Orientation | Common Use |
|-------|------------|------------|
| `"1:1"` | Square | Social media, avatar |
| `"3:2"` | Landscape | Photography standard |
| `"2:3"` | Portrait | Photography standard |
| `"4:3"` | Landscape | Traditional photo/screen |
| `"3:4"` | Portrait | Traditional photo |
| `"16:9"` | Landscape | Widescreen video/web |
| `"9:16"` | Portrait | Mobile story |
| `"4:5"` | Portrait | Instagram portrait |
| `"5:4"` | Landscape | Slight landscape |
| `"21:9"` | Ultra-wide | Cinematic widescreen |

### Return Value

The tool returns either markdown (default) or JSON. JSON shape:

```json
{
  "provider": "openai" | "gemini",
  "model": "gpt-image-2" | "gemini-3-pro-image-preview",
  "output_path": "/path/to/saved/image.png",
  "prompt": "the prompt used",
  "revised_prompt": "model's revised interpretation (OpenAI only)",
  "usage": {
    "output_tokens": 1234,
    "input_tokens": 56
  },
  "metadata": {
    "quality": "high",
    "size": "1536x1024",
    "background": "opaque"
  }
}
```

**Key return fields:**

- **`output_path`**: The saved file path. Use this as `image_path` in subsequent `edit_image` calls.
- **`revised_prompt`** (OpenAI only): The model's own interpretation of the prompt. Useful for debugging — compare to your input prompt to understand what the model understood.
- **`usage.output_tokens`** (OpenAI only): Primary cost driver. High-quality large images consume more output tokens.

### Typical Use Cases

```python
# Quick low-cost exploration — 4 variants
generate_image(prompt="...", quality="low", n=4, provider="openai")

# Final production render — portrait
generate_image(prompt="...", quality="high", size="1024x1536", provider="openai",
               openai_output_format="jpeg", openai_output_compression=92)

# 4K product photo — Gemini
generate_image(prompt="...", provider="gemini", size="4K", aspect_ratio="1:1")

# Portrait with character reference
generate_image(prompt="...", provider="gemini", reference_images=[base64_str1, base64_str2])

# Transparent product asset
generate_image(prompt="...", provider="openai", background="transparent",
               openai_output_format="png", quality="high")

# Real-time weather visualization
generate_image(prompt="current weather in Tokyo skyline", provider="gemini",
               enable_google_search=True, size="2K", aspect_ratio="16:9")
```

---

## edit_image

Edit an existing image via OpenAI's `/images/edits` endpoint. Supports preserve-pixel sequential editing via `input_fidelity=high`.

### Signature

```python
edit_image(
    prompt: str,                                       # Required — edit instruction
    image_path: str,                                   # Required — source image path
    
    mask_path: str,                                    # Optional — PNG mask (transparent = edit region)
    input_fidelity: "high" | "low",                   # Default: "high"
    quality: "auto" | "low" | "medium" | "high",      # Default: None
    size: str,                                         # Same options as generate_image/OpenAI
    background: "auto" | "transparent" | "opaque",    # Default: None
    openai_output_format: "png" | "jpeg" | "webp",    # Default: None
    openai_output_compression: int,                   # 0–100
    n: int,                                            # 1–10; Default: None
    openai_model: str,                                 # Default: "gpt-image-2"
    
    output_path: str,                                  # Optional — save path
    output_format: "markdown" | "json",               # Tool response format
)
```

### input_fidelity Values

| Value | Behavior | When to Use |
|-------|---------|------------|
| `"high"` | Preserves unchanged pixels as closely as possible | **Always for sequential chains** |
| `"low"` | Loosely guided by source; may interpret freely | Style transfers, radical changes |

### Mask Specification

The mask must be a **PNG file with alpha channel**:
- **Transparent pixels** (alpha=0): The region to edit.
- **Opaque pixels** (alpha=255): Protected — model should not change these.

The mask must be the same dimensions as the source image (or the tool will resize). Slightly oversizing the edit region reduces hard edge artifacts at boundaries.

### Return Value

Same shape as `generate_image`, plus:
- `original_image_path`: The source image that was edited.
- `mask_path`: The mask used (if any).

### Typical Use Cases

```python
# Step in an edit chain — change background
edit_image(
    prompt="Replace the grey background with dark marble, keeping the product unchanged",
    image_path="/tmp/step1_output.png",
    input_fidelity="high"
)

# Masked inpainting — remove specific element
edit_image(
    prompt="Remove the power lines, replace with overcast sky matching surroundings",
    image_path="/tmp/landscape.jpg",
    mask_path="/tmp/powerline_mask.png",
    input_fidelity="high",
    quality="high"
)

# Style transfer — low fidelity
edit_image(
    prompt="Render this scene as a Van Gogh oil painting with swirling brushstrokes",
    image_path="/tmp/photo.jpg",
    input_fidelity="low"
)

# Generate variants for A/B testing
edit_image(
    prompt="Change the product color from blue to red",
    image_path="/tmp/product.png",
    n=3,  # Three variants to choose from
    input_fidelity="high"
)
```

---

## conversational_image

Multi-turn image generation with guided dialogue for progressive refinement.

### Signature

```python
conversational_image(
    prompt: str,                                           # Required — new prompt or refinement
    
    # Conversation management
    conversation_id: str,                                  # Optional — continue existing conversation
    dialogue_mode: "quick" | "guided" | "explorer" | "skip",  # Default: "guided"
    skip_dialogue: bool,                                   # Default: False
    
    # Image reference (for continuing from existing image)
    input_image_file_id: str,                             # Optional — OpenAI file ID
    
    # Provider (locked for conversation lifetime)
    provider: "auto" | "openai" | "gemini",              # Default: "auto"
    
    # OpenAI parameters (same as generate_image)
    quality: str,
    size: str,
    background: str,
    openai_output_format: str,
    openai_output_compression: int,
    openai_model: str,
    assistant_model: str,                                  # GPT model for dialogue; Default: "gpt-4o"
    
    # Gemini parameters (same as generate_image)
    aspect_ratio: str,
    reference_images: list[str],
    enable_google_search: bool,
    gemini_model: str,
    
    # Shared
    enhance_prompt: bool,
    output_path: str,
    output_format: "markdown" | "json",
)
```

### Dialogue Modes

| Mode | Questions | When to Use |
|------|-----------|------------|
| `"quick"` | 1–2 questions | User has partial clarity; wants fast path to generation |
| `"guided"` | 3–5 questions | Default — balanced exploration vs speed |
| `"explorer"` | 6+ questions | Complex brief; user wants thorough exploration before committing |
| `"skip"` | No dialogue | Direct generation; treat prompt as final |

### Conversation Lifecycle

1. **Start conversation**: Call without `conversation_id` — a new `conversation_id` is returned.
2. **Continue conversation**: Pass the returned `conversation_id` in subsequent calls.
3. **Refinement turn**: After image is generated, pass new refinement instructions — the model builds on the previous image.
4. **Provider is locked**: Once set in the first call, the provider cannot change for the conversation.

### Return Value

In dialogue mode (before generation), returns questions to ask the user. After generation:

```json
{
  "conversation_id": "conv_abc123",
  "provider": "openai",
  "output_path": "/path/to/image.png",
  "dialogue_history": ["..."],
  "generation_count": 1
}
```

### Typical Use Cases

```python
# Start creative exploration with guided dialogue
conv = conversational_image(
    prompt="I want a hero image for a wellness brand",
    dialogue_mode="guided",
    provider="gemini"
)
# conversation_id returned for continuation

# Continue with answer to dialogue questions
result = conversational_image(
    prompt="Outdoor, morning light, diverse women doing yoga, soft and uplifting",
    conversation_id=conv.conversation_id,
    provider="gemini"
)

# Refine the generated image
refined = conversational_image(
    prompt="Make the colors warmer and add more lens flare in the background",
    conversation_id=conv.conversation_id,
    provider="gemini"
)
```

---

## list_providers

Lists configured providers and their status.

### Signature

```python
list_providers()
```

### Return Value

```json
{
  "providers": [
    {
      "name": "openai",
      "model": "gpt-image-2",
      "configured": true,
      "api_key_present": true,
      "capabilities": ["generate", "edit", "transparent_background", "sequential_editing"]
    },
    {
      "name": "gemini",
      "model": "gemini-3-pro-image-preview",
      "configured": true,
      "api_key_present": true,
      "capabilities": ["generate", "4K", "reference_images", "google_search"]
    }
  ]
}
```

### Typical Use Case

Call at session start or when debugging to confirm which providers are available before routing generation requests.

---

## list_conversations

Lists saved image generation conversation threads.

### Signature

```python
list_conversations(
    limit: int,          # Max conversations to return; Default: 10; Max: 100
    provider: str,       # Filter by provider; Default: None (all providers)
    output_format: "markdown" | "json",  # Default: "markdown"
)
```

### Return Value

```json
{
  "conversations": [
    {
      "conversation_id": "conv_abc123",
      "provider": "gemini",
      "created_at": "2026-04-21T10:30:00Z",
      "generation_count": 3,
      "last_prompt": "Make the colors warmer",
      "last_output_path": "/path/to/latest.png"
    }
  ],
  "total": 12
}
```

### Typical Use Case

Resume a previous generation session to continue refining an image that was started in a prior session.

```python
# Find the conversation to resume
convs = list_conversations(provider="gemini", limit=5)

# Continue with the conversation_id
refined = conversational_image(
    prompt="Increase the contrast and add film grain",
    conversation_id="conv_abc123",
    provider="gemini"
)
```

---

## list_gemini_models

Lists available Gemini models that support image generation.

### Signature

```python
list_gemini_models()
```

### Return Value

```json
{
  "models": [
    {
      "name": "gemini-3-pro-image-preview",
      "display_name": "Gemini Nano Banana Pro",
      "supported_sizes": ["1K", "2K", "4K"],
      "supported_aspect_ratios": ["1:1", "3:2", "2:3", "4:3", "3:4", "16:9", "9:16", "4:5", "5:4", "21:9"],
      "reference_images_supported": true,
      "google_search_supported": true
    },
    {
      "name": "gemini-2.5-flash-preview-image-generation",
      "display_name": "Gemini 2.5 Flash",
      "supported_sizes": ["1K", "2K"],
      "reference_images_supported": false,
      "google_search_supported": false
    }
  ]
}
```

### Typical Use Case

Call when configuring a Gemini generation request to confirm which models are available and their capabilities. Use `gemini_model="gemini-3-pro-image-preview"` for highest quality; use `gemini-2.5-flash-preview-image-generation` for faster iteration.

---

## Cross-Tool Workflow Patterns

### Full Generation Pipeline

```python
# 1. Quick exploration
variants = generate_image(prompt="...", quality="low", n=4, provider="openai")

# 2. Select best variant, produce final quality render
final = generate_image(prompt="[refined prompt]", quality="high", size="1536x1024",
                       openai_output_format="jpeg", openai_output_compression=92)

# 3. Sequential edit chain
step1 = edit_image(prompt="Change background to...", image_path=final.output_path)
step2 = edit_image(prompt="Add lens flare", image_path=step1.output_path)
```

### Reference-Based Gemini Generation

```python
import base64

def encode(path): return base64.b64encode(open(path, "rb").read()).decode()

refs = [encode("ref1.jpg"), encode("ref2.jpg"), encode("ref3.jpg")]

result = generate_image(
    prompt="The character from the reference images in a forest setting at golden hour",
    provider="gemini",
    reference_images=refs,
    size="2K",
    aspect_ratio="3:2"
)
```

### Live Data Visualization

```python
result = generate_image(
    prompt="The current weather conditions in Tokyo as seen from Shibuya crossing",
    provider="gemini",
    enable_google_search=True,
    size="2K",
    aspect_ratio="16:9"
)
```
