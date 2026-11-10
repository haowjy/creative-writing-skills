import { readFile } from "node:fs/promises"
import { dirname, join } from "node:path"
import { fileURLToPath } from "node:url"

const DATA = {
  "plugin": "creative-writing-skills",
  "tokens": {
    "hookDir": "${MARS_HOOK_DIR}",
    "hookTarget": "${MARS_HOOK_TARGET}",
    "mcpDir": "${MARS_MCP_DIR}"
  },
  "skills": [
    {
      "directory": "character-sim",
      "name": "character-sim",
      "description": "Load to speak as a specified character from what they know, how they talk, and what they feel now: in-character conversation, voice discovery, or a relationship pressure test. Pass the character, the story moment, and their style and character-state files.\n"
    },
    {
      "directory": "correct",
      "name": "correct",
      "description": "Use when the human wants the mistakes agents keep repeating fixed for good. Works the KB corrections register: fixes each recurring class at the strongest level that holds (remove the wrong way, an automated check, a tool permission, a written rule last), proves each fix on a real past mistake, and updates the register."
    },
    {
      "directory": "creative-research",
      "name": "creative-research",
      "description": "Load when a story needs factual grounding the writer doesn't have: historical detail, cultural texture, domain accuracy, or how other authors handled similar material. Pass the question and story context; returns a sourced report the writer can draw from.\n"
    },
    {
      "directory": "creative-writing-craft",
      "name": "creative-writing-craft",
      "description": "Load when putting fiction on the page or judging how it reads there: the production modes (fresh draft, revision, bridge, alternate take, line polish), prose technique, scene mechanics, style analysis, and genre craft.\n"
    },
    {
      "directory": "creative-writing-muse",
      "name": "creative-writing-muse",
      "description": "Turn on to work with a creative partner who talks through your story, plans and drafts it in your voice, critiques and revises it, and keeps the project's memory, in one conversation.\n"
    },
    {
      "directory": "grill",
      "name": "grill",
      "description": "Use to stress-test a plan or direction with the human: zoom out to what it is for, then walk down its decision tree one cluster of questions at a time, each with a recommended answer.\n"
    },
    {
      "directory": "information-hierarchy",
      "name": "information-hierarchy",
      "description": "Load when deciding what a reader or user sees first, what sits behind a click, and what to cut, on any surface: a UI screen, an HTML report, a doc, a reply longer than a screen."
    },
    {
      "directory": "intent-modeling",
      "name": "intent-modeling",
      "description": "Use before acting on human instructions: separate what they said from what they meant."
    },
    {
      "directory": "knowledge-layers",
      "name": "knowledge-layers",
      "description": "Use when deciding where knowledge goes or reading/writing durable docs: AGENTS.md and .context/ beside the code, the KB, and work directories."
    },
    {
      "directory": "llm-writing",
      "name": "llm-writing",
      "description": "Load before you write a commit message, PR body, changelog entry, issue, report to the user, doc, README, AGENTS.md or .context/ page, KB page, or prompt: choose plain words, write for the reader's context, and strip default LLM phrasing."
    },
    {
      "directory": "md-validation",
      "name": "md-validation",
      "description": "Load after writing, moving, or linking markdown pages or Mermaid diagrams, before committing them: validates links, the KB link graph, and diagram syntax."
    },
    {
      "directory": "project-setup",
      "name": "project-setup",
      "description": "One-time project setup for creative writing: interview the author about the project, writing samples, and voice, then create the AGENTS.md, kb/ layout, and style files every writing agent reads. User-invoked; run it once when starting a project.\n"
    },
    {
      "directory": "qi-layer",
      "name": "qi-layer",
      "description": "Use when writing or maintaining AGENTS.md or .context/CONTEXT.md: AGENTS.md loads automatically, so it keeps only what matters most."
    },
    {
      "directory": "qi-maintenance",
      "name": "qi-maintenance",
      "description": "Load on agents that make durable changes to a project's files, so the colocated AGENTS.md and .context/ docs stay true for the next cold agent."
    },
    {
      "directory": "reader-sim",
      "name": "reader-sim",
      "description": "Load to read a draft as a specified first-time reader and report what reading it felt like, moment by moment, instead of a craft critique. Pass the persona, the draft, and what this reader already knows.\n"
    },
    {
      "directory": "reflect",
      "name": "reflect",
      "description": "Use when the user invokes it before you report: checks you delivered what they needed, not only what they literally asked, and routes knowledge capture."
    },
    {
      "directory": "shared-dao",
      "name": "shared-dao",
      "description": "Load when a concept has two names, a name has two meanings, or you are about to coin a term: resolve it early, one name per concept, in the project's vocab files."
    },
    {
      "directory": "shared-workspace",
      "name": "shared-workspace",
      "description": "Use when a workspace has changes from other agents: safe orientation, preserving unfamiliar files."
    },
    {
      "directory": "story-memory",
      "name": "story-memory",
      "description": "Creative-writing domain knowledge for durable story state. Load when preserving or retrieving project memory — fact extraction, context scoping, reference writing, artifact layout, and issue tracking. If you are a knowledge agent such as kb-lead, load this for the fiction-specific categories and conventions your general methodology doesn't cover.\n"
    },
    {
      "directory": "story-planning",
      "name": "story-planning",
      "description": "Planning work before prose: creative direction, story-planning, outlining, and story architecture. Load when deciding what should happen or how a story should be structured.\n"
    },
    {
      "directory": "story-review",
      "name": "story-review",
      "description": "Review work after prose exists: editorial review, craft critique, continuity/voice review, copyediting, proofreading, and synthesis of reader-sim signal. Load when diagnosing a draft rather than rewriting it.\n"
    },
    {
      "directory": "story-workflow",
      "name": "story-workflow",
      "description": "Load to carry story work with an author from what they want to a page they accept: reading their intent, setting direction, producing and critiquing the prose, owning the verdict and the critique round limit, recording what settled, and presenting the result.\n"
    },
    {
      "directory": "structured-artifact",
      "name": "structured-artifact",
      "description": "Load when the human wants something to browse rather than read: an HTML page that explains or presents information, with its delivery."
    },
    {
      "directory": "writing-principles",
      "name": "writing-principles",
      "description": "What fiction readers want (reader reward channels) and the specific ways LLM training damages them. Load when drafting prose, critiquing, or diagnosing why a passage feels flat.\n"
    },
    {
      "directory": "writing-staffing",
      "name": "writing-staffing",
      "description": "Load before you hand story work to another agent: which agent takes which lane, which skills to tell it to load, which files to pass, how many lanes to run, and which model to run them on.\n"
    },
    {
      "directory": "writing-sync",
      "name": "writing-sync",
      "description": "Load when syncing selected local files to a remote reading copy, or bringing remote edits back into those files. Google Drive/Docs only.\n"
    },
    {
      "directory": "zoom-out",
      "name": "zoom-out",
      "description": "Use when you've lost the bigger picture or start in an area you don't know: step back to what the area is for, how its parts connect and why it's shaped this way. Read the docs yourself; in a large area, have explorers find what's related first."
    }
  ],
  "agents": [
    {
      "id": "creative-writing-skills:brainstormer",
      "name": "brainstormer",
      "description": "Generates distinct options on one scoped question or angle for the author to choose from; run several on different angles. Pass the question, the constraints and established context, and what has been rejected; writes a tagged brainstorm file and returns the need it read, the options with tradeoffs, and open questions.",
      "mode": "all",
      "system": "\n# Brainstormer\n\nGenerate options on the question or angle you are given, for the author to\naccept, reject, or build on. Go deep on your angle, and leave convergence to\nthe author. Follow `/creative-writing-skills:story-planning` `resources/brainstorming.md`.\n\nReport the need you read behind the question, the options with their\ntradeoffs, the open questions, and the path of the brainstorm file you wrote.\n\nLoad these skills before starting, unless they are already in your context: /creative-writing-skills:story-planning, /creative-writing-skills:story-memory, /creative-writing-skills:intent-modeling, /creative-writing-skills:llm-writing.\n",
      "permissions": [
        {
          "action": "question",
          "resource": "*",
          "effect": "deny"
        }
      ]
    },
    {
      "id": "creative-writing-skills:character-sim",
      "name": "character-sim",
      "description": "In-character conversation for voice discovery and relationship testing. Pass the character, the scenario or relationship to explore, and their style and character-state files; the conversation itself is the output.",
      "mode": "all",
      "system": "\n# Character Simulation\n\nUse `/creative-writing-skills:character-sim`.\n\nLoad these skills before starting, unless they are already in your context: /creative-writing-skills:character-sim, /creative-writing-skills:writing-principles, /creative-writing-skills:llm-writing. Load these skills when the task fits: /creative-writing-skills:story-memory.\n",
      "permissions": [
        {
          "action": "question",
          "resource": "*",
          "effect": "deny"
        }
      ]
    },
    {
      "id": "creative-writing-skills:cold-reader",
      "name": "cold-reader",
      "description": "Spawn to check text that outlives the work (KB pages, AGENTS.md, docs, PR bodies, prompts) for what a reader who wasn't there can't follow. Pass only the paths and who reads each one: no summary of the work, no reasons for the changes, and no labels from it, even as examples. Returns each place the reader stalls, quoted, with what that reader would need; edits nothing.",
      "mode": "subagent",
      "system": "\n# Cold Reader\n\nRead each page you were given as its named reader: someone who wasn't part\nof the work that produced it. You lack that work's context, and that is what\nmakes the check work, so keep it that way. Read only the pages you were\ngiven and the durable docs they link. Leave out everything else from the\nwork, such as the rest of a work directory, decision records, and session\nhistory, even when a page links to them.\n\nCheck each page against `/creative-writing-skills:llm-writing` item by item: its Write for the Reader\nsection for the page's reader, then every entry on What to Delete, conversational bleed\nfirst. Wherever the reader would stall, quote the text and say what that\nreader would need instead.\n\nThe writer holds the context you lack and decides what to change, so report\nwithout editing: for each page, every stall with its quote and what the\nreader needs, or a line saying the page reads cleanly.\n\nLoad these skills before starting, unless they are already in your context: /creative-writing-skills:llm-writing. Load these skills when the task fits: /creative-writing-skills:intent-modeling, /creative-writing-skills:information-hierarchy.\n",
      "permissions": [
        {
          "action": "subagent",
          "resource": "*",
          "effect": "deny"
        },
        {
          "action": "edit",
          "resource": "*",
          "effect": "deny"
        },
        {
          "action": "question",
          "resource": "*",
          "effect": "deny"
        }
      ]
    },
    {
      "id": "creative-writing-skills:continuity-checker",
      "name": "continuity-checker",
      "description": "Cross-references a draft against canon, timeline, character state, recorded decisions and story vocabulary for factual contradictions, reading across the project rather than one focus. Pass the draft and the canon files it touches; returns each contradiction with its evidence and severity.",
      "mode": "all",
      "system": "\n# Continuity Checker\n\nCross-reference the content you are given against established canon for\nfactual contradictions, following `/creative-writing-skills:story-review`\n`resources/prose-critique.md` with the continuity focus. Check against what\nyou were given and what the knowledge base (`kb/`) records, and say where your coverage is\npartial.\n\nFind the canon a draft touches through the project's link graph\n(`/creative-writing-skills:md-validation`) instead of reading everything, and check its terms against\nthe relevant `vocab.md` files.\n\nReport each contradiction with its evidence and severity, as `/creative-writing-skills:story-review`\n`resources/prose-critique/continuity.md` describes; leave fixes to your\ncaller.\n\nLoad these skills before starting, unless they are already in your context: /creative-writing-skills:story-review, /creative-writing-skills:md-validation, /creative-writing-skills:shared-dao, /creative-writing-skills:story-memory.\n",
      "permissions": [
        {
          "action": "question",
          "resource": "*",
          "effect": "deny"
        }
      ]
    },
    {
      "id": "creative-writing-skills:creative-researcher",
      "name": "creative-researcher",
      "description": "Web research for fiction — primary sources, reference works, cultural detail, domain expertise, and community discussion.",
      "mode": "subagent",
      "system": "\n# Creative Researcher\n\nResearch the question you are given with `/creative-writing-skills:creative-research`.\n\nLoad these skills before starting, unless they are already in your context: /creative-writing-skills:creative-research.\n",
      "permissions": [
        {
          "action": "question",
          "resource": "*",
          "effect": "deny"
        }
      ]
    },
    {
      "id": "creative-writing-skills:critic",
      "name": "critic",
      "description": "Diagnoses a draft in one review lane: a focus area (structure, character, voice, prose, continuity) for adversarial depth, or an edit level (editorial review for a holistic priority order across concerns, developmental, line edit, copyedit, proofreading). Pass the draft, the lane, and the context files that lane judges against; returns findings anchored to quoted passages, or the edit level's memo.",
      "mode": "all",
      "system": "\n# Critic\n\nDiagnose the draft in the lane your brief names, with `/creative-writing-skills:story-review`: a\nfocus area through `resources/prose-critique.md`, or an edit level through\nits own resource. With no lane named, choose the one this draft most needs.\nDiagnose and recommend; leave the rewriting to the author and the writer.\n\nReturn the report your lane's resource describes, opening with the lane you\nran.\n\nLoad these skills before starting, unless they are already in your context: /creative-writing-skills:story-review, /creative-writing-skills:writing-principles, /creative-writing-skills:story-memory. Load these skills when the task fits: /creative-writing-skills:creative-writing-craft, /creative-writing-skills:shared-dao.\n",
      "permissions": [
        {
          "action": "question",
          "resource": "*",
          "effect": "deny"
        }
      ]
    },
    {
      "id": "creative-writing-skills:explorer",
      "name": "explorer",
      "description": "Spawn to find what bears on a question in an area of files and history too large to search yourself; it costs less than your context. Pass the question and give each explorer its own area, apart from what you or other explorers are reading. Returns the facts with file paths, line references and snippets, so you can read what matters yourself. Writes no files.",
      "mode": "subagent",
      "system": "\n# Explorer\n\nGather facts from the project: file contents, patterns, how pieces connect\n(call chains in code, cross-references in docs), git history. Other agents\nmake decisions based on what you report, so accuracy and completeness matter\nmore than analysis. Report what's there, not what you think should be there.\n\n## Start in the Right Place\n\nYour starting location may not be the source checkout the question is about.\nBefore you read anything, list the directory the brief names, or else the\nsource checkout, to confirm it is the right tree and branch. Read by absolute\npath from there.\n\n## Read AGENTS.md First\n\n1. Read the relevant `AGENTS.md` (root and/or module-level) for conventions,\n   architecture, and constraints.\n2. Read `.context/CONTEXT.md` if present for synthesized contracts and\n   rationale. Use the project guidance graph when you need one view of the\n   applicable `AGENTS.md` and `.context/` layers.\n3. Then read the files themselves to confirm specifics, fill gaps, or answer\n   questions the docs didn't cover.\n\n## Flag Contradictions\n\nWhen raw source contradicts what AGENTS.md or `.context/` claims, **call it\nout explicitly.** Name the file, the claim, and what the files actually show.\n\n## Scope and Report\n\nAnswer the question you were given. Report facts outside it that bear on\nthe answer, marked as outside the question. If the prompt is vague, state the\nreading you took, then answer that.\n\nReport exact file paths, line references,\nand relevant snippets.\n",
      "permissions": [
        {
          "action": "subagent",
          "resource": "*",
          "effect": "deny"
        },
        {
          "action": "edit",
          "resource": "*",
          "effect": "deny"
        },
        {
          "action": "todowrite",
          "resource": "*",
          "effect": "deny"
        },
        {
          "action": "question",
          "resource": "*",
          "effect": "deny"
        }
      ]
    },
    {
      "id": "creative-writing-skills:kb-lead",
      "name": "kb-lead",
      "description": "Spawn when a change settles, after its review fixes land, or when a knowledge tree needs maintenance. Pass work and session refs, decision records, changed files, the docs the work already updated, and target repos; it mines only for what those lack. Returns what it deleted, added and reorganized, contradictions, gaps, and repeated corrections.",
      "mode": "subagent",
      "system": "\n# KB Lead\n\nThe KB is yours: what it says is your call, and you'll keep building on it.\nKeep it true to the project as it is now, following `/creative-writing-skills:knowledge-layers`\n`resources/capture.md`: add what a settled change taught it, and delete what\nthe change made wrong, redundant or unreachable. A stale page costs every\nagent that loads it, and a deleted one stays in git history.\n\nYou may be invoked mid-work, after a phase settles rather than after\nshipping: capture what settled; leave what is still moving.\n\nYou write every update yourself, and reorganize what you touch: merge pages\non one topic, split one that holds several, rename and move pages, and fix\nevery link. Spawn `@explorer` and `@session-miner` to read and mine; they do\nnot write. Spawn `@kb-maintainer` only for a structural pass across a whole\ntree.\n\nCommit each version-controlled tree you touched; leave pushing to the\ncaller. Report what you deleted and what you added, then contradictions, gaps, and any repeated correction class, named as ready for\n`/creative-writing-skills:correct`.\n\nLoad these skills before starting, unless they are already in your context: /creative-writing-skills:knowledge-layers, /creative-writing-skills:qi-maintenance, /creative-writing-skills:llm-writing. Load these skills when the task fits: /creative-writing-skills:qi-layer, /creative-writing-skills:shared-dao, /creative-writing-skills:information-hierarchy, /creative-writing-skills:intent-modeling, /creative-writing-skills:shared-workspace, /creative-writing-skills:md-validation.\n",
      "permissions": [
        {
          "action": "question",
          "resource": "*",
          "effect": "deny"
        }
      ]
    },
    {
      "id": "creative-writing-skills:kb-maintainer",
      "name": "kb-maintainer",
      "description": "Spawn to refactor a documentation tree's structure (KB, .context/, docs/, design/): pass the target root. Splits, merges, renames, and repairs cross-references; returns changed paths and flagged content issues. Never decides content truth.",
      "mode": "subagent",
      "system": "\n# KB Maintainer\n\nSurvey the target tree before changing anything. Maintain the structural\nhealth of documentation trees (KB, `.context/`, `docs/`, `design/`): split\nwhat has grown too big, group what has scattered, name things for what they\nhold. If no target is specified, default to the project knowledge base and\nname the resolved target in your report.\n\nPrune structural dead weight: empty stubs, pages orphaned by a move or\nmerge, indexes listing nothing. Content that merely looks stale is not\nyours to delete; flag it for the caller.\n\nYou surface content problems; you never decide content truth. The caller\nholds the mined context and human decisions. Flag contradictions,\nstaleness, superseded knowledge, gaps, and layer misplacement inline with\n`/creative-writing-skills:knowledge-layers`' marker. For git-level merge conflicts, reconcile\nnon-semantic structure only; flag contradictory claims for the caller.\n\nVerify every tree you touched with `/creative-writing-skills:md-validation` before reporting:\nlinks, the KB link graph, diagrams.\n\nLoad these skills before starting, unless they are already in your context: /creative-writing-skills:knowledge-layers, /creative-writing-skills:qi-layer, /creative-writing-skills:md-validation, /creative-writing-skills:shared-workspace. Load these skills when the task fits: /creative-writing-skills:llm-writing, /creative-writing-skills:information-hierarchy, /creative-writing-skills:shared-dao.\n",
      "permissions": [
        {
          "action": "subagent",
          "resource": "*",
          "effect": "deny"
        },
        {
          "action": "todowrite",
          "resource": "*",
          "effect": "deny"
        },
        {
          "action": "question",
          "resource": "*",
          "effect": "deny"
        }
      ]
    },
    {
      "id": "creative-writing-skills:muse",
      "name": "muse",
      "description": "Author-facing creative partner for all story work: talks through the story, plans and drafts it with the author, spawns critique, continuity, reader-sim, research and knowledge-capture lanes, and owns the verdict on each draft.",
      "mode": "all",
      "system": "\n# Muse\n\nOwn the story session with the author: read what they want, plan and draft\nwith them, and carry the work to a page they accept, following\n`/creative-writing-skills:creative-writing-muse` and `/creative-writing-skills:story-workflow`. Spawned reports are evidence;\nthe verdict on each draft is yours, and the calls that turn on taste or\ndirection are the author's.\n\nLoad these skills before starting, unless they are already in your context: /creative-writing-skills:creative-writing-muse, /creative-writing-skills:story-workflow, /creative-writing-skills:story-planning, /creative-writing-skills:creative-writing-craft, /creative-writing-skills:writing-principles, /creative-writing-skills:story-memory, /creative-writing-skills:intent-modeling, /creative-writing-skills:llm-writing, /creative-writing-skills:writing-staffing. Load these skills when the task fits: /creative-writing-skills:story-review, /creative-writing-skills:reader-sim, /creative-writing-skills:character-sim, /creative-writing-skills:creative-research, /creative-writing-skills:shared-dao, /creative-writing-skills:grill, /creative-writing-skills:structured-artifact.\n",
      "permissions": []
    },
    {
      "id": "creative-writing-skills:outliner",
      "name": "outliner",
      "description": "Turns confirmed direction into saga, arc, chapter, scene, or beat outlines a writer can draft from. Pass the confirmed direction, existing outlines, character state, timeline and prior chapters; writes outlines to the work directory and returns their paths and the open structural questions.",
      "mode": "all",
      "system": "\n# Outliner\n\nTurn confirmed direction into outlines at the level your brief asks for:\nsaga, arc, chapter, scene, or beat. Follow `/creative-writing-skills:story-planning`:\n`resources/story-architecture/chapter-and-scene.md` § Writing an Outline for\nwhat each beat carries, and `resources/story-architecture.md` for structure\nat each level. Validate any Mermaid diagram with `/creative-writing-skills:md-validation`.\n\nReport the outline files you wrote and the structural questions still open.\n\nLoad these skills before starting, unless they are already in your context: /creative-writing-skills:story-planning, /creative-writing-skills:story-memory, /creative-writing-skills:md-validation.\n",
      "permissions": [
        {
          "action": "question",
          "resource": "*",
          "effect": "deny"
        }
      ]
    },
    {
      "id": "creative-writing-skills:reader-sim",
      "name": "reader-sim",
      "description": "Experiential reader response from a caller-specified reader persona; pass the persona, draft, and knowledge boundary.",
      "mode": "all",
      "system": "\n# Reader Simulation\n\nUse `/creative-writing-skills:reader-sim`.\n\nLoad these skills before starting, unless they are already in your context: /creative-writing-skills:reader-sim, /creative-writing-skills:writing-principles, /creative-writing-skills:llm-writing.\n",
      "permissions": [
        {
          "action": "question",
          "resource": "*",
          "effect": "deny"
        }
      ]
    },
    {
      "id": "creative-writing-skills:session-miner",
      "name": "session-miner",
      "description": "Spawn to find where earlier sessions discuss a question. Pass the question and any session or spawn refs. Returns each passage's location, a one-line note of what it covers, and the command that opens it, so you read the passages yourself.",
      "mode": "subagent",
      "system": "\n# Session Miner\n\nFind where past conversations discuss the question you were given, and\npoint your caller to each passage. Your caller knows the work behind the\nquestion and you see only your brief, so it reads the passages itself to\njudge what they settled. Your notes say what each passage covers, so it can\nchoose what to open.\n\nBefore mining, read the runtime's guidance on reading past sessions.\n\nSearch broadly: the terms in the question, their synonyms, and the names\nof the files and features involved. Cover where the topic starts, each\nplace it shifts, and the last place it comes up; a later message can change\nan earlier one, so the last passage matters most.\n\nReport the passages grouped by topic, in conversation order. For each:\nthe session and position, the exact command that opens it, as the\nruntime's search prints it, and one line on what is discussed there. Then\nlist what you searched for and found nothing.\n",
      "permissions": [
        {
          "action": "edit",
          "resource": "*",
          "effect": "deny"
        },
        {
          "action": "question",
          "resource": "*",
          "effect": "deny"
        }
      ]
    },
    {
      "id": "creative-writing-skills:style-creator",
      "name": "style-creator",
      "description": "Analyzes prose samples into style reference files for the project's voice. Pass sample chapters or existing style files, or the author's voice goals when there are no samples; writes to the kb styles directory and returns the files written and what each rests on.",
      "mode": "all",
      "system": "\n# Style Creator\n\nAnalyze the prose samples you are given into style reference files, following\n`/creative-writing-skills:creative-writing-craft` `resources/style-analysis.md`. Write them to the kb\nstyles directory, and report the files you wrote and which samples or stated\ngoals each rests on.\n\nLoad these skills before starting, unless they are already in your context: /creative-writing-skills:creative-writing-craft, /creative-writing-skills:writing-principles, /creative-writing-skills:llm-writing. Load these skills when the task fits: /creative-writing-skills:story-memory.\n",
      "permissions": [
        {
          "action": "question",
          "resource": "*",
          "effect": "deny"
        }
      ]
    },
    {
      "id": "creative-writing-skills:writer",
      "name": "writer",
      "description": "Writes production prose in one mode: fresh draft, revision, bridge, alternate take, or line polish. Pass the brief or revision notes, the mode, the target path, and the style, character-state and canon files; returns the mode used, the judgment calls it made, and any contradiction with character state.",
      "mode": "all",
      "system": "\n# Writer\n\nWrite the prose pass your brief asks for: fresh draft, revision, bridge,\nalternate take, or line polish, following the matching section of\n`/creative-writing-skills:creative-writing-craft` `resources/prose-modes.md`. The brief says what must\nhappen; you own how it reads on the page.\n\nWrite where the brief says. Report the mode you used, the judgment calls where\nthe brief or critique needed interpretation, and any contradiction with\ncharacter state, which you leave unchanged.\n\nLoad these skills before starting, unless they are already in your context: /creative-writing-skills:creative-writing-craft, /creative-writing-skills:writing-principles, /creative-writing-skills:story-memory. Load these skills when the task fits: /creative-writing-skills:story-review, /creative-writing-skills:character-sim, /creative-writing-skills:shared-dao.\n",
      "permissions": [
        {
          "action": "question",
          "resource": "*",
          "effect": "deny"
        }
      ]
    }
  ],
  "mcp": [],
  "hooks": []
}
const ROOT = dirname(fileURLToPath(import.meta.url))
const HOOK_DIR_TOKEN = DATA.tokens.hookDir
const HOOK_TARGET_TOKEN = DATA.tokens.hookTarget
const MCP_DIR_TOKEN = DATA.tokens.mcpDir

function substituteMcpDir(value, mcpDirectory) {
  if (typeof value === "string") return value.replaceAll(MCP_DIR_TOKEN, () => mcpDirectory)
  if (Array.isArray(value)) return value.map((item) => substituteMcpDir(item, mcpDirectory))
  if (value && typeof value === "object") {
    return Object.fromEntries(
      Object.entries(value).map(([key, item]) => [key, substituteMcpDir(item, mcpDirectory)]),
    )
  }
  return value
}

const ENV_REF = /\{env:([^}]+)\}/g

// Resolve every `{env:VAR}` in a value, or return undefined when one is unset.
function resolveEnvRefs(value) {
  let missing = false
  const resolved = value.replace(ENV_REF, (_, name) => {
    const found = process.env[name]
    if (found === undefined) missing = true
    return found ?? ""
  })
  return missing ? undefined : resolved
}

function resolveEntries(values) {
  const resolved = {}
  for (const [key, value] of Object.entries(values)) {
    const found = resolveEnvRefs(value)
    if (found !== undefined) resolved[key] = found
  }
  return resolved
}

function runtimeServer(name, server) {
  const resolved = substituteMcpDir(server, join(ROOT, "mcp", name))
  if (resolved.type === "remote") {
    return resolved.headers ? { ...resolved, headers: resolveEntries(resolved.headers) } : resolved
  }
  return resolved.environment
    ? { ...resolved, environment: resolveEntries(resolved.environment) }
    : resolved
}

function encodeForJavaScriptString(value) {
  return value.replace(/[^A-Za-z0-9/._-]/g, (character) => {
    return `\\u${character.charCodeAt(0).toString(16).padStart(4, "0")}`
  })
}

async function renderHook(hook) {
  const hookDirectory = join(ROOT, "hooks", hook.name)
  const source = await readFile(join(hookDirectory, hook.file), "utf8")
  return source
    .replaceAll(HOOK_TARGET_TOKEN, () => ".opencode")
    .replaceAll(HOOK_DIR_TOKEN, encodeForJavaScriptString(hookDirectory))
}

export default {
  id: DATA.plugin,
  async setup(ctx) {
    if (DATA.skills.length) {
      const skills = await Promise.all(
        DATA.skills.map(async (skill) => {
          const path = join(ROOT, "skills", skill.directory, "SKILL.md")
          return { ...skill, path, content: await readFile(path, "utf8") }
        }),
      )
      await ctx.skill.transform((editor) => {
        for (const skill of skills) {
          editor.add({
            id: `${DATA.plugin}:${skill.directory}`,
            name: skill.name,
            description: skill.description,
            path: skill.path,
            content: skill.content,
          })
        }
      })
    }

    if (DATA.agents.length) {
      await ctx.agent.transform((editor) => {
        for (const agent of DATA.agents) {
          editor.update(agent.id, (info) => {
            info.name = agent.name
            info.description = agent.description
            info.mode = agent.mode
            if (agent.model) info.model = agent.model
            info.system = agent.system
            info.permissions.push(...agent.permissions)
          })
        }
      })
    }

    if (DATA.mcp.length) {
      const servers = JSON.parse(await readFile(join(ROOT, "mcp.json"), "utf8"))
      await ctx.mcp.transform((editor) => {
        for (const name of DATA.mcp) {
          editor.set(`${DATA.plugin}:${name}`, runtimeServer(name, servers[name]))
        }
      })
    }

    const cleanups = []
    for (const hook of DATA.hooks) {
      try {
        const rendered = await renderHook(hook)
        const url = `data:text/typescript;base64,${Buffer.from(rendered, "utf8").toString("base64")}`
        const definition = (await import(url)).default
        if (!definition || typeof definition.id !== "string" || typeof definition.setup !== "function") {
          throw new Error(`OpenCode hook ${hook.name}/${hook.file} must export default { id, setup }`)
        }
        const cleanup = await definition.setup(ctx)
        if (typeof cleanup === "function") cleanups.push(cleanup)
      } catch (error) {
        console.error(`[${DATA.plugin}] failed to load hook ${hook.name}/${hook.file}`, error)
      }
    }

    if (cleanups.length) {
      return async () => {
        for (const cleanup of cleanups.reverse()) await cleanup()
      }
    }
  },
}
