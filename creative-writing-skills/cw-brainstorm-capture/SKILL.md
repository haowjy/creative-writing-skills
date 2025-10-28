---
name: cw-brainstorm-capture
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
✅ User: "Character A competes with B" → Capture: "A and B compete [user]" + optional: "Tournament? Political? Trial? [AI suggestions]"

### 2. Source Tagging (MANDATORY)

Tag ALL information with its source:
- `[user]` or `[stated]` - User explicitly said this
- `[AI]` or `[suggested]` - AI offered this possibility
- `[TBD]` - Deliberately left undecided
- `[inferred]` - Logical implication user confirmed

Never mix tagged and untagged information.

**AI suggestions encouraged when:**
- User asks for ideas
- User seems stuck
- Offering 2-3 brief possibilities (clearly marked separate)

**AI stays minimal when:**
- User is actively exploring their own ideas
- Just capturing a discussion
- User didn't ask for suggestions

### 3. Preserve Vagueness

Keep it vague if user leaves it vague:
- "might create tension" → Record as uncertain
- "thinking about" → Record as consideration
- "maybe" → Record as possibility

### 4. Multiple Options Coexist

Working notes can contain contradictions. Mark as `[TBD]`, don't resolve.

## Output Approach

**Use whatever structure fits the discussion.** Could be:
- Bullet lists with source tags
- Sections organized by topic
- Timeline format
- Character-focused groupings
- Whatever captures the brainstorm clearly

**Essential elements:**
- Source tags on everything
- Minimal capture (user's words, not elaborations)
- Vagueness preserved
- Options/contradictions noted as `[TBD]`

**Optional sections based on discussion:**
- What's decided vs exploring vs TBD
- AI suggestions (if offered and not decided)
- Contradictions to resolve (if any exist)

## Teaching Example: The Distinction

### User Says:
"I'm thinking character X and character Y compete for leadership. Maybe this creates tension with character Z who was the previous leader."

### ✅ Good Capture:
```markdown
# Leadership Competition Notes

- X and Y compete for leadership [user]
- Z was previous leader [user]
- May create tension with Z [user, uncertain]

[TBD]:
- Form of competition
- How Z responds
- Outcome
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

- X and Y compete for leadership [user]
- Z was previous leader [user]  
- May create tension with Z [user, uncertain]

[TBD]:
- Competition format
- Z's response
- Resolution

[AI suggestions to consider]:
- Competition could be: tournament-style, political maneuvering, or trial-based
- Z could: oppose both, support one, or stay neutral
[User hasn't decided on any of these]
```

## If You're Over-Elaborating

**Stop if you're writing:**
- Numbered scene lists
- Detailed backstories
- Specific dialogue
- Precise timelines
- Multiple paragraphs per point
- Examples user didn't mention

Move AI content to clearly marked suggestions section, keep minimal (2-3 options).

## Success Check

**Good:** User says "Yes, that's what I said"  
**Bad:** User says "I never said all that"

Notes should feel skeletal and incomplete. That's the point - preserves creative freedom.

## Skills are Composable

Feel free to combine with other skills when helpful (e.g., using cw-official-wiki to document finalized worldbuilding, or cw-story-critique to analyze what you're brainstorming).

## File Placement (Claude Code)

1. Check project docs for conventions
2. Look at where similar content lives
3. Place near related content
4. Name: `brainstorm-[topic]-[date].md`
5. Ask if unclear
