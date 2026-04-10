# Page Patterns

Examples showing the range from simple to complex. Not templates — structure your pages to fit what needs documenting.

## Core Principle

Not every page needs 15 sections. Include what matters, skip what doesn't.

- Minor character → name, role, 2 sentences. Done.
- Major character → detail where it matters to the story.
- Simple location → description and why it matters.
- Complex magic system → elaborate rules and examples.

---

## Character Pages

### Minimal (Supporting/Minor)

```markdown
# Innkeeper Greaves

Owner of [[The Broken Wheel]] tavern. Gruff but fair, knows everyone's business in the merchant quarter.

Provides shelter to the protagonist in Chapter 3 and tips about suspicious strangers in Chapter 8.

**References:** Chapter 3, 8
```

### Medium (Recurring)

```markdown
# Dr. Sarah Chen

Forensic analyst and former colleague of [[Marcus Webb]].

## Background
PhD in forensic science, 8 years at the crime lab. Former military — met Marcus during joint operations.

## Role in Story
Provides forensic analysis uncovering conspiracy evidence. Initially reluctant, becomes committed ally after the Chapter 9 attack.

## Relationships
- **[[Marcus Webb]]**: Former colleague, trusts him despite his reputation
- **[[Elena Vasquez]]**: Professional relationship evolving into friendship

```mermaid
graph LR
    SC[Sarah Chen] -->|trusts| MW[Marcus Webb]
    SC -->|allies with| EV[Elena Vasquez]
    MW -->|information broker for| EV
```

**References:**
- Chapter 5: Analyzes warehouse evidence
- Chapter 9: Nearly killed in attack
- Chapter 15: Testifies despite threats
```

### Complex (Protagonist)

Full sections on background, personality, abilities, character arc, relationships (with diagram), and critical moments. Every claim cited. See the content that's appropriate — don't pad sections just because the template has them.

---

## Location Pages

### Minimal

```markdown
# The Warehouse District

Abandoned industrial zone on the city's east side. Site of key confrontations.

**References:** Chapter 5, 16
```

### Medium

```markdown
# Marcus Webb's Office

Information broker's base in a converted apartment above a pawn shop.

## Description
Two rooms: outer office (meeting space, covered windows, multiple exits) and inner office (secure room with servers and encrypted files). Intentionally run-down appearance conceals high-tech security.

## Significance
Neutral ground for information trades. Where most conspiracy evidence is analyzed. Attacked in Chapter 9.

**References:**
- Chapter 3: First meeting
- Chapter 9: Attack and evacuation
- Chapter 20: Returned after security upgrades
```

---

## Lore/System Pages

### Minimal

```markdown
# The Monitoring Protocol

The [[Consortium]]'s surveillance system — official cameras, illegal wiretaps, and civilian informant network. Enables tracking and elimination of opposition before they gain traction.

**References:** Chapter 7 (discovery), Chapter 18 (used against protagonist)
```

### Complex

Full structure covering overview, how the system works, limitations, history, and story significance. Relationship diagrams for organizational structures. Cite every factual claim.

---

## Event Pages

```markdown
# The Warehouse Shootout

Final confrontation between the protagonist's team and the [[Consortium]]'s enforcement squad in the [[Warehouse District]].

[[Elena Vasquez]], [[Marcus Webb]], and [[Dr. Sarah Chen]] were cornered. Two-hour standoff ended when honest officers from the [[Kingsport PD]] responded. Key evidence secured; Marcus wounded.

Turning point: first time Consortium members faced legal consequences.

**References:** Chapter 16
```

---

## Timeline Pages

Keep timelines focused on significant events. Don't list every minor occurrence.

```markdown
# Investigation Timeline

| Day | Event | Chapter |
|-----|-------|---------|
| 1   | [[Elena Vasquez]] accepts missing person case | 1 |
| 12  | Discovers connection to [[Consortium]] | 4 |
| 34  | Attacked in apartment | 7 |
| 56  | [[Marcus Webb]]'s office attacked | 9 |
| 78  | Evidence decrypted | 13 |
| 89  | Evidence published | 18 |
```

---

## Usage Notes

- Simple pages for simple topics — don't inflate
- Complex pages only when complexity serves the documentation
- Every entity mentioned gets a link on first appearance per section
- Relationship diagrams when relationships are complex enough to warrant visual representation
- Trust your judgment on what each page needs
