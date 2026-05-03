# Image Generation Alternatives for IP-Faithful Children's Books

**Date:** May 2026
**Context:** Evaluating alternatives to `gemini-3.1-flash-image-preview` (Nano Banana 2) for the Toon Link series, where current results show inconsistent Wind Waker locations (Forsaken Fortress doesn't look like the actual fortress) and characters (Helmaroc King looks different on every page) despite passing reference images.

---

## TL;DR — What to Actually Try

1. **Switch from Nano Banana 2 → Nano Banana Pro (`gemini-3-pro-image-preview`) and enable Google Search grounding for images.** This is the biggest single lever and the only mainstream model in 2026 that does **actual internet-based reference lookup**. Cost goes from ~$0.045 → $0.067 per image at batch (1K, 50% discount), but grounding likely solves the Forsaken Fortress problem outright. **However:** Pro tightened IP filtering in Jan 2026 after a Disney C&D — Nintendo characters may now be blocked. Test before committing.
2. **If Pro blocks Nintendo IP, fall back to Nano Banana 2 + manual web grounding** — pre-fetch Wind Waker location screenshots yourself and pass them as reference images, instead of relying on the model's training data.
3. **For maximum IP fidelity with no filter risk, run a local SDXL/Illustrious workflow with a Wind Waker LoRA.** A community Toon Link / Tetra / Wind Waker LoRA already exists on Civitai. Compute cost is essentially free after setup; quality on cel-shaded Zelda art is the best of any option here.
4. **Skip OpenAI gpt-image-1.5.** Has multi-reference (up to 16 images), but content filter is tighter than Gemini's on Nintendo IP, no Google-Search-style grounding, and ~$0.13/image at the resolution we need. Worse on every axis for this use case.
5. **Skip Midjourney.** Best-in-class character consistency via `--oref`, but no official API (third-party scrapers risk account bans) and no way to generate at scale programmatically.

---

## The Core Problem, Restated

We have two distinct failure modes with Nano Banana 2:

- **Location drift:** "Forsaken Fortress" doesn't match the actual Wind Waker fortress. The model has *some* training data on Wind Waker but it's lossy and stylized incorrectly. Reference images we pass help marginally but get treated as style hints, not specifications.
- **Character drift across pages:** Helmaroc King changes appearance every page. Even with character ref images in the prompt, the model treats them loosely.

These are different problems requiring different solutions:
- Location drift is solved by **better source material** — either get the model to look up real reference, or feed it the exact screenshot.
- Character drift is solved by **stronger reference conditioning** — either a model that respects refs more strictly (Flux Kontext, Midjourney `--oref`) or a model fine-tuned on the character (LoRA).

---

## 1. OpenAI gpt-image-1.5 (the 2026 successor to gpt-image-1)

**Status:** DALL-E 3 and gpt-image-1 were both deprecated May 12, 2026. The current model is `gpt-image-1.5` (and `gpt-image-1-mini`).

### Pricing (May 2026)
| Model | Low (1024) | Medium (1024) | High (1024) |
|---|---|---|---|
| `gpt-image-1.5` | $0.009 | $0.034 | $0.133 |
| `gpt-image-1-mini` | $0.005 | — | — |

For our purposes (square, picture-book quality) realistic cost is **$0.034–$0.133 per image** — already 1-3x more than Gemini Flash. Plus you're billed for input image tokens when passing references, which adds up fast with our 5-6 ref images per page strategy.

### Reference Image Support
- **Yes — up to 16 reference images per edit.** Pass via file IDs or URLs.
- Indexed referencing: prompt as `"Image 1: character ref... Image 2: location ref... apply Image 1 character to Image 2 location"`.
- Cookbook explicitly recommends a "character anchor" pattern for multi-page picture book pipelines.

### Web/Internet Lookup
- **No.** gpt-image-1.5 does not have Google Search grounding or any equivalent. It can only use what's in its training data + the references you pass.

### Nintendo IP / Content Filter
- OpenAI's filter is **stricter than Google's** on copyrighted characters. Toon Link prompts will frequently get blocked or returned as a generic "elf boy in green tunic."
- The `moderation` parameter has `auto` (default) and `low` settings; `low` helps with edge cases but does not unlock copyrighted characters.
- Empirically: people working with Nintendo/Disney IP have moved off OpenAI to Gemini precisely because of this.

### Verdict
**Worse for our use case.** More expensive, no internet grounding, tighter IP filter. Only advantage is multi-reference handling, which the OpenAI cookbook suggests is genuinely better than Gemini's — but not enough to overcome the filter problem.

---

## 2. Midjourney V7

**Status:** V7 is current as of mid-2026 (V8 reportedly in late beta). `--cref` (character reference) is **deprecated in V7** — replaced by `--oref` (omni-reference).

### Omni-Reference (`--oref`)
- Unified reference system that handles characters, objects, vehicles, creatures (not just characters like `--cref`).
- Tunable strictness via `--ow` (omni-weight): `0` (loose) → `100` (default) → `1000` (very strict).
- Genuinely the best "put THIS in my image" capability of any current model.
- Pairs with `--sref` (style reference) for separate style anchoring.

### API Access
- **No official API in 2026.** This is the killer.
- Third-party services (ImaginePro, ImagineAPI, UseAPI, ~$10/mo + per-image fees) work by automating Discord/web with Selenium. **Against Midjourney ToS — risk of account ban.**
- Cannot integrate cleanly into our `image_generator.py` pipeline; would require a separate manual or quasi-manual workflow.

### Pricing
- Plans start at $10/mo (Basic, ~200 images), $30/mo Standard (unlimited relax), $60/mo Pro.
- For our volume (15-30 images/book, 1-3 books/month), the $30/mo Standard is plenty.
- Quality on cel-shaded styles is excellent — arguably best in class for stylized art.

### Internet/Reference Lookup
- **No.** Same as OpenAI — only training data + supplied refs.

### Nintendo IP / Content Filter
- More permissive than OpenAI, comparable to or slightly more permissive than Gemini Flash. "Toon Link" prompts work; named Nintendo characters generally render.

### Verdict
**Best raw quality and reference adherence, worst integration story.** If we were willing to do a manual workflow (generate via web UI, drop into `images/` directory), Midjourney would probably produce the best Wind Waker book. But it would break our automation. Worth keeping in mind for a one-off "hero shot" we want perfect (cover image, key page).

---

## 3. Sora 2 / DALL-E 3

**Status: Both effectively dead for our use case.**

- **DALL-E 3:** Deprecated May 12, 2026. Replaced by gpt-image-1.5.
- **Sora 2:** Discontinued by OpenAI on March 24, 2026. App shut down April 26, 2026; API shutting down September 24, 2026. It was a video model anyway — never the right tool for picture books.

Skip both.

---

## 4. Local Models — SDXL, Illustrious XL, Flux

This is where the most interesting options live for our specific problem.

### Why local is appealing for the Toon Link series
- **Zero content filter.** No risk of Nintendo IP blocks ever.
- **Per-image cost is essentially $0** after hardware/setup (modern Mac with M-series GPU runs SDXL fine; 512x512 in ~5-10s).
- **Existing community LoRA for our exact use case.** There's a SDXL/Pony/Illustrious LoRA on Civitai trained on Wind Waker — covers Toon Link, Toon Zelda, and Tetra. (Search Civitai for "Wind Waker Toon Link Tetra PonyXL Character Style LoRA".) Recommended LoRA strength 0.80–1.20.
- **LoRAs solve character drift definitively.** They're literally fine-tuned on the character — drift becomes a non-issue. For one-off characters (Helmaroc King, Big Octo) we'd train our own from 15-30 reference images.

### SDXL vs Flux in 2026
- **SDXL (with Pony Diffusion V6 or Illustrious XL base):** Most mature ecosystem. Best for stylized/cel-shaded art (which is exactly what we need). The Wind Waker LoRA above is built on this stack.
- **Flux 2 / Flux Kontext:** Better prompt adherence, better text rendering, but **weaker on stylized cel-shaded art**. Several 2026 comparisons explicitly note SDXL+LoRA beats Flux for anime/cartoon styles. Flux Kontext is amazing for *editing* an existing image while preserving identity, but for *generating* Toon Link, SDXL+LoRA wins.

### Flux Kontext as a complementary tool
Even if we don't use Flux for primary generation, **Flux Kontext is the strongest "preserve this character/object exactly while changing the scene" model on the market.** Workflow:
1. Generate one canonical Helmaroc King image with SDXL+LoRA (or any model).
2. Use Flux Kontext to put that exact character into each page's scene via natural-language edits.
This solves character drift across pages without any per-character training.

Available via Replicate (~$0.03–0.04/edit) or fal.ai or local (Flux Kontext Dev, open-weights).

### Workflow Cost Comparison
| Approach | Setup cost | Per-image | Per book (20 images) |
|---|---|---|---|
| Nano Banana 2 (current) batch | $0 | $0.022 | ~$0.45 |
| Nano Banana Pro batch (1K) | $0 | $0.067 | ~$1.34 |
| Nano Banana Pro batch + grounding | $0 | ~$0.07 | ~$1.40 |
| gpt-image-1.5 medium | $0 | $0.034 | ~$0.68 |
| Local SDXL + Wind Waker LoRA | ~3-5 hrs setup | $0 | $0 |
| Flux Kontext via Replicate | ~1 hr setup | ~$0.04 | ~$0.80 |
| Midjourney (manual) | $30/mo | included | included |

### Verdict
**For the Toon Link series specifically, local SDXL + the Wind Waker LoRA is probably the right answer.** The community has already done the consistency training for us. Cost is zero, quality on cel-shaded Wind Waker style is the best available, and we control everything.

Downside: requires setting up ComfyUI or AUTOMATIC1111, learning a new workflow, and integrating into `image_generator.py`. ~1 day of work upfront.

For the OoT series and non-Zelda books, Nano Banana Pro with grounding is probably better (no Wind Waker LoRA equivalent, painterly style works fine in Gemini).

---

## 5. The Sleeper: Nano Banana Pro (Gemini 3 Pro Image)

This is buried at the end because it surfaced late in research, but **it's the single most important finding.**

### What it is
- `gemini-3-pro-image-preview` — Google's flagship image model (Nano Banana 2 / `gemini-3.1-flash-image-preview` is the lower-tier "fast" sibling).
- Same API surface as Nano Banana 2; basically a model-name swap in our existing code.

### **Google Search Grounding for Images** ← the killer feature
**This is the "internet reference lookup" capability the user heard about.** Both Nano Banana 2 *and* Nano Banana Pro support grounding via the `google_search` tool — at generation time, the model queries Google's image index for live visual data on the subject.

Use case from Google's own docs: "specific real-world locations or recent events that may not be well-represented in static training data." This is **exactly the Forsaken Fortress problem.**

Code change required is minimal — just add the tool to the request:

```python
from google import genai
from google.genai import types

client = genai.Client()

response = client.models.generate_content(
    model="gemini-3-pro-image-preview",  # or gemini-3.1-flash-image-preview
    contents=[prompt_text, *reference_images],
    config=types.GenerateContentConfig(
        tools=[types.Tool(google_search=types.GoogleSearch())],
        response_modalities=["IMAGE"],
    ),
)
```

The model will search for "Forsaken Fortress Wind Waker", retrieve canonical images, and use them as live reference during generation.

### Pricing
| Resolution | Per image | Batch (50% off) |
|---|---|---|
| 1K (~1MP) | $0.134 | $0.067 |
| 2K (~4MP) | $0.134 | $0.067 |
| 4K (~16MP) | $0.24 | $0.12 |
| Input image | 560 tokens (~$0.002 each) | half |

For a 20-page book at 1K with batch + grounding: roughly **$1.40-$1.80** vs. our current ~$0.45 with Nano Banana 2. Triple the cost, but still well under $2/book.

### IP Filter — the catch
**Google strengthened IP filtering in January 2026** after Disney sent them a C&D in December 2025. Nano Banana Pro has a non-configurable Layer 2 filter that blocks 16 named Disney IPs and detects "famous brand logos and copyrighted characters." Reports indicate Nintendo content is *sometimes* affected, with geographic variation.

**Action item:** Run a small test first — generate 3-5 Toon Link / Wind Waker pages with `gemini-3-pro-image-preview` + grounding, see what the block rate looks like. If it's clean, switch. If Toon Link gets blocked, fall back to Nano Banana 2 (Flash, less aggressive filter) but **still add the grounding tool** — grounding is available on Flash too, and that alone may fix Forsaken Fortress.

### Verdict
**This is the first thing to try.** It's a 5-line code change, costs ~$1.50/book extra, and directly addresses the location-drift problem via real-time web lookup. If the filter doesn't block Nintendo IP, this is probably the answer for everything except per-character drift (which a Flux Kontext or LoRA pass on top would solve).

---

## Recommended Action Plan

In priority order:

### Step 1 (today, 30 min): Try grounding on Nano Banana 2
Add `google_search` tool to existing pipeline calls. Same model, same cost, instant test. If Forsaken Fortress now looks correct, problem half-solved.

### Step 2 (today, 1 hr): Test Nano Banana Pro
Generate 5 representative pages with `gemini-3-pro-image-preview` + grounding. Check (a) whether IP filter blocks Nintendo content and (b) whether character/location consistency improves enough to justify 3x cost.

### Step 3 (if 1+2 are insufficient, ~1 day): Set up local SDXL + Wind Waker LoRA
- Install ComfyUI on the Mac.
- Download Illustrious XL base + the Civitai Wind Waker LoRA.
- Build a simple `comfyui_generator.py` that mirrors the `image_generator.py` interface (takes a project ID, reads prompts, outputs PNGs).
- This is the long-term answer for the Toon Link series.

### Step 4 (only if needed for hero shots): Manual Midjourney pass
For the cover image or one or two pivotal pages where we want maximum quality, generate via Midjourney web UI and drop into `images/`. Don't try to automate this.

### Code change for Step 1 (drop into `scripts/image_generator.py`)
Search for the `client.models.generate_content` call and add `tools=[types.Tool(google_search=types.GoogleSearch())]` to its `config`. Behind a `--grounding` CLI flag so we can A/B test.

---

## Summary Table

| Model | Internet lookup | Ref fidelity | Nintendo IP | API | Price/image (batch) |
|---|---|---|---|---|---|
| **Nano Banana 2 (current)** | Yes (via grounding tool) | Loose | OK | Official | $0.022 |
| **Nano Banana Pro** | **Yes (best)** | Better than Flash | **Risky (Jan 2026 tightening)** | Official | $0.067 |
| gpt-image-1.5 | No | Good (16 ref slots) | Tight filter | Official | $0.017–$0.067 |
| Midjourney V7 (`--oref`) | No | **Best in class** | Mostly OK | None official | ~$0.05 effective |
| Sora 2 | — | — | — | Shutting down | — |
| DALL-E 3 | — | — | — | Deprecated | — |
| Local SDXL + LoRA | No | **Perfect (fine-tuned)** | **No filter** | DIY | $0 |
| Flux Kontext | No | **Best for edit/preserve** | Permissive | Replicate/fal | ~$0.04 |

---

## Sources

- [Nano Banana image generation (Google AI for Developers)](https://ai.google.dev/gemini-api/docs/image-generation)
- [Gemini 3 Developer Guide](https://ai.google.dev/gemini-api/docs/gemini-3)
- [Developers can build with Nano Banana Pro (Gemini 3 Pro Image) — Google Blog](https://blog.google/innovation-and-ai/technology/developers-tools/gemini-3-pro-image-developers/)
- [Grounding with Google Search — Vertex AI docs](https://docs.cloud.google.com/vertex-ai/generative-ai/docs/grounding/grounding-with-google-search)
- [Gemini 3 Pro Image API Pricing 2026](https://blog.laozhang.ai/en/posts/gemini-3-pro-image-api-pricing)
- [Nano Banana Pro IP Restrictions Jan 2026 Policy Update](https://help.apiyi.com/en/nano-banana-pro-policy-update-image-safety-ip-restriction-2026-en.html)
- [Nano Banana Pro Cannot Generate Disney Characters](https://help.apiyi.com/en/nano-banana-pro-disney-ip-blocked-copyright-protection-guide-en.html)
- [OpenAI Image API Pricing 2026 (gpt-image-1.5)](https://www.aifreeapi.com/en/posts/openai-image-generation-api-pricing)
- [GPT Image 1.5 Prompting Guide — OpenAI Cookbook](https://cookbook.openai.com/examples/multimodal/image-gen-1.5-prompting_guide)
- [Image Generation API Guide — OpenAI](https://developers.openai.com/api/docs/guides/image-generation)
- [Midjourney Omni-Reference --oref](https://updates.midjourney.com/omni-reference-oref/)
- [Character Reference (deprecated in V7) — Midjourney docs](https://docs.midjourney.com/hc/en-us/articles/32162917505293-Character-Reference)
- [Does Midjourney Have an API? — ImaginePro](https://www.imaginepro.ai/blog/2025/7/midjourney-api-unofficial-access-alternatives)
- [Sora 2 discontinuation announcement — Wikipedia summary](https://en.wikipedia.org/wiki/Sora_(text-to-video_model))
- [Wind Waker Toon Link / Tetra PonyXL LoRA on Civitai](https://civitai.com/models/369507/wind-waker-toon-link-toon-zelda-tetra-ponyxl-character-style-lora)
- [FLUX.1 Kontext — Black Forest Labs](https://bfl.ai/models/flux-kontext)
- [FLUX 2 vs Stable Diffusion XL Comparison 2026](https://apatero.com/blog/flux-2-vs-stable-diffusion-xl-comparison-2026)
- [Best LoRAs for Consistent Characters 2026 — Thinkpeak AI](https://thinkpeak.ai/best-loras-consistent-characters-2026/)
