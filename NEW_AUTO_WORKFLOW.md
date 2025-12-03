# 🚀 New Automated Workflow (Option 2)

## The Problem (Before)

Creating a Latin children's book required **tedious copy-pasting**:

1. Copy prompt from app
2. Paste into ChatGPT/Claude
3. Copy response
4. Paste back into app
5. Repeat 5 times for each stage
6. Hope you didn't make mistakes copying/pasting

**Result:** Frustrating, error-prone, time-consuming 😩

---

## The Solution (Now)

## **One-Click Automation with Review Points** ✨

### New Workflow:

```
English Story → [Click] → Latin Translation → [Review/Edit] →
[Click] → Pages & Vocabulary → [Review/Edit] → [Click] → Images → PDF
```

**Only 3 clicks. 2 review points. Done.**

---

## How to Use

### Step 1: Create Project (Same as before)

1. Open the Streamlit app: `./run_app.sh`
2. Go to **"📝 Create Project"** tab
3. Fill in:
   - Book title
   - Theme
   - Target pages
   - Art style description
4. Click **"Create Project"**

### Step 2: Choose Auto Workflow

When you land on **"Step 2: AI Story"**, you'll see:

```
Choose workflow mode:
⚪ Auto (Recommended) - AI translates automatically
⚪ Manual - Copy/paste prompts to external AI
```

Select **Auto (Recommended)**

### Step 3: English → Latin (Auto Step 1)

**What you do:**
1. Paste or type your English story
2. Click **"🌐 Auto-Translate to Latin"**
3. Wait ~30-60 seconds
4. Review the Latin translation
5. Edit if needed
6. Click **"📖 Create Pages & Vocabulary"**

**What the app does:**
- Calls Gemini API directly
- Uses your known vocabulary database
- Follows classical Latin grammar rules
- Adds proper macrons
- Returns simple, child-friendly Latin

**Tips:**
- Keep English story 100-200 words
- Simple sentences (under 10 words each)
- Concrete, visual actions
- 2-3 characters max

### Step 4: Pagination & Vocabulary (Auto Step 2)

**What you do:**
1. Click **"🤖 Auto-Create Pages"**
2. Wait ~30-60 seconds
3. Review pages:
   - Latin text per page
   - English translation
   - Image prompts
4. Edit any page if needed
5. Click **"💾 Save Changes"**
6. Click **"🎨 Generate Images"**

**What the app does:**
- Divides story into your target page count
- Extracts all unique vocabulary
- Generates dictionary forms automatically
- Creates detailed image prompts for each page
- Identifies which characters appear per page

**Tips:**
- Each page should have 1-2 sentences
- Image prompts describe the **scene**, not character appearance
- Characters are handled separately via reference images

### Step 5: Generate Images (Step 3 - Same as before)

The improved character consistency system (from earlier fix) automatically:
- Uses character references with proper labels
- Tells AI which character is which
- Maintains visual consistency across pages

### Step 6: Build PDF (Step 4 - Same as before)

Click and download!

---

## Auto vs Manual Workflow

| Feature | Auto Workflow | Manual Workflow |
|---------|--------------|-----------------|
| **Speed** | ⚡ Fast (3 clicks) | 🐢 Slow (10+ copy-pastes) |
| **API Calls** | ✅ Automatic | ❌ You do it externally |
| **Review Points** | ✅ 2 (Latin, Pages) | ✅ 5 (Every stage) |
| **Cost** | ~$0.10 Gemini API | Free (use your own AI) |
| **Control** | Medium | High |
| **Best For** | Quick books | Precise control |

---

## Cost Breakdown

### Auto Workflow:
- **Translation:** ~$0.05 (Gemini API)
- **Pagination:** ~$0.05 (Gemini API)
- **Image Generation:** ~$0.35 (Gemini 2.5 Flash Image)
- **Total:** ~$0.45 per book

### Manual Workflow:
- **Your time:** ~30 minutes of copying/pasting
- **External AI:** Free (Claude.ai, ChatGPT free tier)
- **Image Generation:** ~$0.35 (same)
- **Total:** ~$0.35 per book + your time

---

## Technical Details

### New Modules Created:

1. **`scripts/gemini_integration.py`**
   - `translate_to_latin()` - Calls Gemini to translate English → Latin
   - `create_pages_and_vocabulary()` - Calls Gemini to paginate and extract vocab
   - `check_latin_quality()` - (Future) Validates Latin quality

2. **`scripts/auto_workflow.py`**
   - `auto_step_1_translate()` - UI for auto translation step
   - `auto_step_2_paginate()` - UI for auto pagination step
   - `show_auto_workflow()` - Main controller

3. **`app.py` (Modified)**
   - Added workflow mode selector in Step 2
   - Integrated auto workflow alongside manual workflow

### API Integration:

```python
# Example: How auto translation works
from scripts.gemini_integration import translate_to_latin

latin_text = translate_to_latin(
    english_story="A boy finds a cat...",
    project=project,  # Has theme, level, pages
    db=database       # Known vocabulary
)
# Returns: "Puer felem invenit..."
```

---

## FAQ

**Q: Do I need a Gemini API key?**
A: Yes! Set `GEMINI_API_KEY` in your `.env` file.

**Q: Can I still use the manual workflow?**
A: Absolutely! Just select "Manual" mode in Step 2.

**Q: What if the AI makes a mistake in Latin?**
A: You can edit the Latin before proceeding to pagination!

**Q: Can I edit the pages after auto-creation?**
A: Yes! Every page is editable before you generate images.

**Q: What model does it use?**
A: Gemini 2.0 Flash Experimental for text, Gemini 2.5 Flash Image for images.

**Q: Is my data sent to Google?**
A: Yes, your story text is sent to Gemini API for processing. Don't include sensitive information.

**Q: Can I use Claude or GPT instead?**
A: Not yet in auto mode. Use manual workflow for other AI providers.

---

## Troubleshooting

**Error: "GEMINI_API_KEY not found"**
- Create a `.env` file in the project root
- Add: `GEMINI_API_KEY=your_key_here`
- Get a key from: https://ai.google.dev/

**Error: "Translation failed after 2 attempts"**
- Check your API key is valid
- Check you have API quota remaining
- Try a shorter, simpler English story

**Latin translation looks wrong**
- Click back and edit it manually
- The AI is pretty good but not perfect
- You have full editing control before proceeding

**Pages don't match my English story**
- The AI tries to infer pagination from sentence breaks
- Edit the pages directly - every field is editable
- You can manually adjust page breaks

---

## Next Steps

1. **Try it!** Create a test book with auto workflow
2. **Compare** results vs manual workflow
3. **Report bugs** or suggestions

**Enjoy the streamlined workflow!** 🎉
