---
name: cw-brainstorming
description: Creative writing skill for capturing story brainstorming. Use when the user is exploring narrative ideas, discussing characters, planning episodes, or thinking through story possibilities. Creates minimal working notes that preserve creative freedom by recording only what was stated and marking sources.
---

# Brainstorming Capture

Capture story brainstorming in working note format that preserves creative freedom.

## Core Principle

Record brainstorming WITHOUT:
- Over-elaborating on what was stated
- Mixing user statements with AI suggestions unmarked
- Inventing excessive details
- Constraining future creativity

**AI suggestions are valuable but must be clearly marked and kept minimal.**

## Types of Brainstorming

This skill handles all brainstorming types:
- Story/plot directions (general narrative exploration)
- Chapter structure and beats (planning individual chapters)
- Worldbuilding and lore (magic systems, cultures, history, geography)
- Character development (motivations, arcs, relationships)
- Timeline and continuity (chronology, contradictions)

All share core principles (minimal capture, source tagging, preserve vagueness).
See references/ for specialized guidance:
- `chapter-planning.md` - Capturing beat and scene exploration
- `worldbuilding.md` - Exploring fictional world elements (use web search for research)
- `character-development.md` - Exploring motivations, arcs, relationships
- `continuity-timeline.md` - Timeline tracking and contradiction handling

## Critical Rules

### 1. Minimal Capture Only

Record ONLY what the user explicitly states. Do NOT add elaborations, examples they didn't give, or details to fill gaps.

**The problem is mixing, not suggesting:**

❌ User: "Character A competes with B" → Capture: "A and B compete for leadership through a tournament with three rounds..."
✅ User: "Character A competes with B" → Capture: "A and B compete" + optional: "<AI>Tournament? Political? Trial?</AI>"

### 2. Source Tagging (Simple 3-Tag System)

**Default: Untagged = user said it.** Most ideas come from the user, so treat them as the default.

**ONLY use tags for special context:**

1. **`<AI>...</AI>`** - AI suggestions/possibilities (MUST be clearly wrapped)
   - Use when offering ideas user didn't state
   - Keep to 2-3 brief options
   - Example: `<AI>Competition could be: tournament-style, political maneuvering, or trial-based</AI>`

2. **`<hidden>...</hidden>`** - Author-only information meant to be revealed later
   - Secret character motivations
   - Planned twists/revelations
   - Behind-the-scenes reasons unknown to characters/readers yet
   - Example: `<hidden>Z secretly wants them both to fail so he can reclaim leadership</hidden>`

**When to offer AI suggestions:**
- User asks for ideas
- User seems stuck
- Offering brief possibilities to spark creativity

**When to stay minimal:**
- User is actively exploring their own ideas
- Just capturing an ongoing discussion
- User didn't ask for suggestions

### 3. Preserve Vagueness

Keep it vague if user leaves it vague:
- "might create tension" → Record as uncertain
- "thinking about" → Record as consideration
- "maybe" → Record as possibility

### 4. Multiple Options Coexist

Working notes can contain contradictions and multiple possibilities. Don't resolve them - just list the options being considered.

## Output Approach

**Use whatever structure fits the discussion.** Could be:
- Bullet lists
- Sections organized by topic
- Timeline format
- Character-focused groupings
- Whatever captures the brainstorm clearly

**Essential elements:**
- Minimal capture (user's words, not elaborations)
- Vagueness preserved
- AI suggestions wrapped in `<AI>` tags
- Author-only info wrapped in `<hidden>` tags when relevant

**Optional sections based on discussion:**
- Open questions to explore
- Multiple options being considered
- AI suggestions (if offered)
- Contradictions to resolve later

## Teaching Example: The Distinction

### User Says:
"I'm thinking character X and character Y compete for leadership. Maybe this creates tension with character Z who was the previous leader."

### ✅ Good Capture:
```markdown
# Leadership Competition Notes

- X and Y compete for leadership
- Z was previous leader
- May create tension with Z (uncertain)

Open questions:
- Form of competition?
- How does Z respond?
- Outcome?
```

### ❌ Bad Capture:
```markdown
# Leadership Competition Arc

X and Y compete for leadership after Z steps down. Z feels threatened by the challenge to his authority.

The competition unfolds in three stages:
1. Announcement and initial positioning
2. First challenge where X demonstrates strength
3. Second challenge where Y shows wisdom
...
[20 more invented beats]
```

**Why bad?** Added massive elaboration the user never stated.

### ✅ Good with AI Suggestions:
```markdown
# Leadership Competition Notes

- X and Y compete for leadership
- Z was previous leader
- May create tension with Z (uncertain)

Open questions:
- Competition format: <AI>tournament-style? political maneuvering? trial-based?</AI>
- Z's response: <AI>oppose both? support one? stay neutral?</AI>
- Resolution?
```

### ✅ Good with Hidden Author Notes:
```markdown
# Leadership Competition Notes

- X and Y compete for leadership
- Z was previous leader
- May create tension with Z (uncertain)
- <hidden>Z is secretly manipulating both X and Y to destroy each other, planning to reclaim power after they're both discredited</hidden>

Open questions:
- Competition format?
- Outcome?
```

**Why use `<hidden>`?** The manipulation twist is planned for later reveal. Readers/characters don't know yet, but the author needs to track it while brainstorming.

## If You're Over-Elaborating

**Stop if you're writing:**
- Numbered scene lists
- Detailed backstories
- Specific dialogue
- Precise timelines
- Multiple paragraphs per point
- Examples user didn't mention

Wrap AI suggestions in `<AI>` tags, keep minimal (2-3 options).

## Success Check

**Good:** User says "Yes, that's what I said"
**Bad:** User says "I never said all that"

Notes should feel skeletal and incomplete. That's the point - preserves creative freedom.

## After Capturing: Discuss and Explore

**DON'T just write notes and stop.** After capturing, engage with the user to help develop ideas:

**Useful follow-ups:**
- **Clarifying questions:** "You mentioned tension with Z - are you thinking internal conflict or external confrontation?"
- **Potential directions:** "This setup could go a few ways: political intrigue, personal drama, or action-focused. What feels right?"
- **Exploring implications:** "If Z opposes them both, how does that change the power dynamics?"
- **Connecting threads:** "This competition ties into the earlier succession crisis you mentioned - want to explore that link?"

**Keep it conversational:**
- Offer 2-3 possibilities, not exhaustive lists
- Ask about what excites the user
- Help clarify vague ideas without over-defining them
- Point out interesting implications or contradictions

**The goal:** Help the user think through their ideas, not take over the creative process.

## Skills are Composable

Feel free to combine with other skills when helpful (e.g., using cw-official-docs to document finalized worldbuilding, or cw-story-critique to analyze what you're brainstorming).

## File Placement (Claude Code)

1. Check project docs for conventions
2. Look at where similar content lives
3. Place near related content
4. Name: `brainstorm-[topic].md`
5. Ask if unclear
