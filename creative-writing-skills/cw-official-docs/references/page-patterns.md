# Wiki Page Patterns and Examples

These are **examples showing the range from simple to complex**, not mandatory templates. Structure your pages to fit what needs documenting - simple pages can be simple, complex pages can be complex.

## Core Principle: Adapt Structure to Content

**Not every page needs 15 sections.** Include what matters, skip what doesn't.

- Minor character? → Name, role, 2 sentences. Done.
- Major character? → More detail where it matters to the story.
- Simple location? → Description and why it matters. That's it.
- Complex magic system? → Elaborate rules and examples.

Trust your judgment on what each page needs.

---

## Character Pages

### Minimal Character (Supporting/Minor)

```markdown
---
title: Innkeeper Greaves
type: character
---

# Innkeeper Greaves

Owner of The Broken Wheel tavern. Gruff but fair, knows everyone's business in the merchant quarter.

Provides shelter to the protagonist in Chapter 3 and tips them off about suspicious strangers in Chapter 8.

**References:**
- Chapter 3, 8
```

### Medium Character (Recurring)

```markdown
---
title: Dr. Sarah Chen
type: character
status: alive
role: supporting
---

# Dr. Sarah Chen

Forensic analyst and former colleague of Marcus Webb.

## Overview
Works in the city's main crime lab. Expertise in trace evidence and ballistics. Maintains professional distance but will bend rules for the right cause.

## Background
PhD in forensic science, 8 years at the crime lab. Former military - met Marcus during joint operations. Left service before the scandal that ended his career.

## Role in Story
Provides forensic analysis that uncovers conspiracy evidence. Initially reluctant to get involved, becomes committed ally after Chapter 9 attack.

## Key Relationships
- **Marcus Webb**: Former colleague, trusts him despite his reputation
- **The protagonist**: Professional relationship evolving into friendship

**References:**
- Chapter 5: Analyzes evidence from the warehouse
- Chapter 9: Nearly killed in attack, commits to helping
- Chapter 15: Testifies despite threats
```

### Complex Character (Major/Protagonist)

```markdown
---
title: Elena Vasquez
type: character
status: alive
role: protagonist
---

# Elena Vasquez

Former investigative journalist turned private investigator after exposing corruption cost her career.

## Physical Description
Late 20s, athletic build from years of martial arts training. Distinctive: always wears her grandmother's silver compass necklace. Dark circles under eyes from chronic insomnia.

## Background
Grew up in industrial district, worked her way through journalism school. Won press freedom award at 24 for exposing city council corruption. Story was buried, she was blacklisted. Turned PI skills to freelance investigation work.

## Personality
Stubborn, driven by need to expose truth. Struggles with trust after betrayal by her editor. Uses sarcasm as defense mechanism. Fiercely protective of her few remaining friends.

## Abilities
- Exceptional research and investigation skills
- Martial arts: black belt in Krav Maga
- Lock picking (learned from questionable sources)
- Photography and surveillance

## Character Arc
Starts believing she can only rely on herself. Through forced cooperation with allies, learns trust again. Final arc: chooses to expose truth even when it costs her personally.

## Goals & Motivations
Primary: Expose the conspiracy that controls the city
Secondary: Clear her professional reputation
Internal: Learn to trust others again

## Key Relationships
- **Marcus Webb**: Information broker, develops mutual respect and trust
- **Dr. Sarah Chen**: Ally who becomes close friend
- **James Torres**: Former editor who betrayed her, conflicted feelings
- **Her grandmother**: Deceased, moral compass (flashbacks)

## Critical Moments
- **Chapter 1**: Discovers the conspiracy while investigating "routine" case
- **Chapter 7**: Attacked in her apartment, realizes how deep this goes
- **Chapter 12**: Confronts James, learns full extent of his betrayal
- **Chapter 18**: Chooses truth over safety, publishes evidence
- **Chapter 24**: Final confrontation with conspiracy leaders

**References:**
- Chapter 1-24 (protagonist throughout)
- See Chapter 12 for full James confrontation
- See Chapter 18 for key character choice
```

**Notice:** All three are valid. Structure fits what needs documenting.

---

## Location Pages

### Minimal Location (Background)

```markdown
---
title: The Warehouse District
type: location
---

# The Warehouse District

Abandoned industrial zone on city's east side. Site of several key confrontations due to isolation and lack of security cameras.

**References:**
- Chapter 5: First evidence discovered here
- Chapter 16: Final showdown location
```

### Medium Location (Recurring)

```markdown
---
title: Marcus Webb's Office
type: location
---

# Marcus Webb's Office

Information broker's base of operations in converted apartment above pawn shop.

## Description
Two rooms: outer office (meeting space, covered windows, multiple exits) and inner office (secure room with servers, encrypted files, arsenal). Intentionally run-down appearance conceals high-tech security.

## Security Features
- Reinforced door with biometric lock
- Surveillance covering all approaches
- Panic room with separate exit to alley
- Signal jammers (activated when needed)

## Significance
Neutral ground for information trades. Where most conspiracy evidence is analyzed and stored. Attacked in Chapter 9, forcing Marcus and protagonist to evacuate.

**References:**
- Chapter 3: First meeting location
- Chapter 9: Attack forces evacuation
- Chapter 20: Returned after security upgrades
```

### Complex Location (Major Setting)

```markdown
---
title: Kingsport
type: location
region: Coastal Metropolitan Area
population: ~2 million
---

# Kingsport

Major port city and commercial hub. Setting for the entire story.

## Geography
Natural harbor on the eastern coast. City built on seven hills, with harbor district at sea level, government quarter on highest hill, and industrial zones in lowlands.

## Districts

**Harbor District:** Commercial port, merchant quarter, shipping companies. Broken Wheel tavern located here. Mix of legitimate business and smuggling operations.

**Government Quarter:** City hall, courts, police headquarters on Observatory Hill. Symbolic of power, physically above the people. Conspiracy's visible face operates from here.

**Industrial Zone:** Abandoned warehouses, old factories. Site of key confrontations in Chapters 5 and 16.

**University District:** Academic institutions, crime lab where Dr. Chen works, research facilities.

## History
Founded 200 years ago as trading port. Grew rapidly, became center of regional commerce. Recent decade: increasing corruption, consolidation of power by shadowy consortium.

## Current Status
Appears prosperous on surface. Deeper investigation reveals: police corruption, city officials controlled by conspiracy, independent journalists blacklisted, surveillance exceeding legal bounds.

## Role in Story
City itself functions as character - protagonist fights not just individuals but entrenched system of power. Urban environment enables both conspiracy's control and protagonist's investigative work.

## Key Locations Within
- Marcus Webb's Office (see separate page)
- City Crime Lab (see separate page)  
- The Broken Wheel tavern (see separate page)
- Warehouse District (see separate page)
- City Hall (center of conspiracy operations)

**References:**
- Throughout story (main setting)
- Chapter 12: Full conspiracy scope revealed
- Chapter 22: City-wide consequences of exposure
```

---

## Lore/System Pages

### Minimal Concept

```markdown
---
title: The Monitoring Protocol
type: lore
---

# The Monitoring Protocol

Conspiracy's surveillance system. Combination of official security cameras, illegal wiretaps, and civilian informant network.

Enables conspiracy to track threats and eliminate opposition before they gain traction. Protagonist discovers extent in Chapter 7.

**References:**
- Chapter 7: Discovery
- Chapter 18: System used to track protagonist's movements
```

### Complex System

```markdown
---
title: The Consortium's Power Structure
type: lore
category: political
---

# The Consortium's Power Structure

Shadow organization controlling Kingsport through layers of legitimate business fronts and corrupted officials.

## Overview
Not a formal organization with membership lists, but network of aligned interests. Business leaders, politicians, police officials, and media owners who maintain power through mutual benefit and information control.

## How It Works

**Top Tier:** Five founding families (never named publicly). Control major industries: shipping, real estate, banking, media, and security.

**Middle Tier:** City officials, police chiefs, judges appointed/elected with consortium backing. Appear legitimate but serve consortium interests.

**Bottom Tier:** Street-level operators - surveillance teams, enforcers, informants. Often don't know full scope of organization.

## Methods
- Blackmail (information gathering on anyone with power)
- Economic pressure (control key industries)
- Media manipulation (suppress unfavorable stories)
- Legal manipulation (control courts and police)
- Violence (only when other methods fail)

## Limitations
- Can't control everything (too obvious)
- Relies on secrecy (exposure is threat)
- Internal conflicts (competing interests)
- Doesn't account for individuals willing to lose everything for truth

## History
Formed 30 years ago when five major businesses realized cooperation more profitable than competition. Gradually expanded influence from economic to political to social control.

## Significance
Primary antagonist of story. Not individual villains but systemic corruption. Protagonist's fight is against structure, not just people.

**References:**
- Chapter 12: Structure revealed through Marcus's intelligence
- Chapter 18: Exposed through protagonist's investigation
- Chapter 24: Partially dismantled but not destroyed
```

---

## Event Pages

### Simple Event

```markdown
---
title: The Warehouse Shootout
type: event
location: Industrial District
chapter: Chapter 16
---

# The Warehouse Shootout

Final confrontation between protagonist's team and conspiracy's enforcement squad.

Protagonist, Marcus, and Dr. Chen cornered in abandoned warehouse. Two-hour standoff ended when police (honest officers, not corrupted ones) responded to neighbors' reports. Conspiracy members arrested, key evidence secured.

Three enforcement members killed, Marcus wounded, protagonist injured but survived.

Turning point: First time conspiracy members faced actual legal consequences.

**References:**
- Chapter 16: Full scene
```

### Complex Event

```markdown
---
title: The Evidence Publication
type: event
date: Story Day 89
chapter: Chapter 18
---

# The Evidence Publication

Protagonist's decision to publish full conspiracy evidence despite personal cost.

## Background
After Chapter 16 arrests, consortium moved to crush story. Threatened protagonist's few remaining media contacts. Made clear: publish and face total destruction of career and life.

## What Happened
Protagonist chose to publish anyway. Used offshore hosting, anonymous sources, encrypted backups. Released: financial records, surveillance logs, testimony from corrupted officials, video evidence.

Published midnight on anonymous platform. Within hours: picked up by national media, international attention, too big to bury.

## Immediate Consequences
- Arrest warrants for 17 consortium members
- Protagonist became public figure (wanted anonymity but became face of story)
- Three city officials resigned
- Federal investigation launched

## Long-term Effects
- Consortium power broken but not destroyed
- City government restructured
- Protagonist vindicated professionally but target for life
- Inspired others to expose corruption elsewhere

## Significance
Story's climax. Protagonist sacrifices personal safety for truth. Demonstrates individual action can challenge systemic corruption, even if victory incomplete.

**References:**
- Chapter 18: Publication decision and initial fallout
- Chapter 22: Wider consequences revealed
```

---

## Item/Object Pages

### Minimal Item

```markdown
---
title: The Encrypted Drive
type: item
---

# The Encrypted Drive

USB drive containing financial records proving conspiracy's control.

Found in Chapter 5, decrypted in Chapter 9, published in Chapter 18. Key evidence that enabled exposure of conspiracy.

**References:**
- Chapters 5, 9, 18
```

### Detailed Item (If It Matters)

```markdown
---
title: Elena's Grandmother's Compass
type: item
category: personal significance
---

# Elena's Grandmother's Compass

Silver compass necklace. Practical navigation tool, but primary significance is emotional.

## Description
Antique silver compass on steel chain. Functional compass (still points north). Engraved on back: "La verdad vale la pena" (Truth is worth the cost).

## History
Belonged to Elena's grandmother, an activist journalist in her youth. Grandmother wore it through dangerous investigations. Given to Elena when she entered journalism school.

## Significance
Symbol of Elena's commitment to truth. She clutches it when making difficult decisions. Mentioned in key character moments:

- Chapter 1: Touches it when deciding to investigate conspiracy
- Chapter 12: Grips it during James confrontation
- Chapter 18: Holds it while clicking "publish" on evidence

Represents generational commitment to truth-telling and accepting consequences.

**References:**
- Chapter 1, 12, 18 (key moments)
- Mentioned throughout as character tic
```

---

## Organization Pages

### Simple Organization

```markdown
---
title: The Honest Officers Coalition
type: faction
---

# The Honest Officers Coalition

Informal group of police officers not corrupted by consortium. Operate carefully within department.

Coordinate with protagonist secretly. Respond to Warehouse Shootout in Chapter 16, enabling arrests. Help protect evidence afterward.

Led informally by Captain Rodriguez (see separate page).

**References:**
- Chapter 14: First contact
- Chapter 16: Warehouse response
```

### Complex Organization

```markdown
---
title: Kingsport Police Department
type: faction
founded: 1823
status: Partially corrupted
---

# Kingsport Police Department

City's official law enforcement. 2,000 officers. Partially compromised by consortium influence.

## Structure
- Commissioner: Appointed by mayor (consortium-controlled)
- Deputy Commissioners (3): Mix of corrupted and honest
- 12 Precincts: Varying levels of corruption
- Special units: Homicide, Vice, Internal Affairs (IA mostly neutered)

## Corruption Levels
**Fully compromised:** Upper leadership, Vice unit (protect consortium operations)
**Partially compromised:** Most precincts (some corrupted officers, some honest)
**Mostly clean:** Some homicide detectives, handful of honest veterans

## Methods of Control
- Promotions based on loyalty, not merit
- Honest officers assigned to low-priority work
- Evidence mysteriously disappears in key cases
- Officers who investigate wrong targets transferred or forced out

## Honest Officers
Roughly 30% of department not corrupted. Operate carefully, document everything, coordinate secretly. Form informal network called Honest Officers Coalition.

## Role in Story
Initially obstacle (corrupted officers hinder investigation). Later: internal allies emerge, enabling final confrontations. Demonstrated: institutions not inherently corrupt, but can be captured and must be reclaimed.

**References:**
- Throughout story
- Chapter 14: Honest officers make contact
- Chapter 16: Mixed response to Warehouse Shootout
- Chapter 22: Post-exposure reforms begun
```

---

## Timeline Pages

Keep timelines focused. Don't list every minor event.

### Simple Timeline

```markdown
---
title: Investigation Timeline
type: timeline
---

# Investigation Timeline

**Day 1:** Elena accepts missing person case (Chapter 1)
**Day 12:** Discovers connection to consortium (Chapter 4)
**Day 34:** Attacked in apartment (Chapter 7)
**Day 56:** Marcus's office attacked (Chapter 9)
**Day 78:** Evidence decrypted (Chapter 13)
**Day 89:** Evidence published (Chapter 18)
**Day 95:** Federal investigation begins (Chapter 22)

**References:** See individual chapters for full events
```

### Detailed Timeline (When Chronology Complex)

Could include parallel storylines, flashbacks, multiple POVs. Structure to show what needs showing.

---

## Magic/Power System Template

### Simple System

```markdown
---
title: Telepathic Link
type: magic-system
---

# Telepathic Link

Mental communication between bonded individuals. Rare ability, appears spontaneously.

## How It Works
Thoughts transmit directly between bonded pair. No distance limit. Can be blocked by conscious effort (privacy maintained).

## Requirements
Spontaneous bond, usually forms during intense shared experience. Can't be forced or trained.

## Limitations
Only between two people. Can't be extended to others. Emotionally exhausting if overused.

## In Story
Protagonist and Marcus develop link in Chapter 9 attack. Enables coordination during final confrontation.

**References:**
- Chapter 9: Bond forms
- Chapter 16: Used tactically
```

### Complex System (When Rules Matter)

Use detailed structure if magic system is central to story and needs elaborate rules. Otherwise, keep simple.

---

## Usage Notes

**Remember:**
1. These are examples, not mandatory templates
2. Simple pages for simple topics
3. Complex pages only when complexity serves the documentation
4. Skip sections that don't apply
5. Add sections your specific page needs
6. Trust your judgment

**Common page types not shown here?** Create structure that makes sense for your content. These examples show patterns, not limits.

**Questions about structure?** Ask yourself: "Does this section add useful information?" If no, skip it.
