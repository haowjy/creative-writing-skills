import { readFile } from "node:fs/promises"
import { dirname, join } from "node:path"
import { fileURLToPath } from "node:url"

const DATA = {
  "plugin": "creative-writing-skills",
  "tokens": {
    "hookDir": "${MARS_HOOK_DIR}",
    "mcpDir": "${MARS_MCP_DIR}"
  },
  "skills": [
    {
      "directory": "character-sim",
      "name": "character-sim",
      "description": "Speak as a specified character from their current knowledge, voice, and emotional state. Use for skill-only workflows that need in-character conversation, voice discovery, or relationship pressure tests.\n"
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
      "description": "Craft references for writing fiction well: prose, scenes, style, voice, and genre/page-level technique. Load when a writer, critic, or muse needs how-to-write guidance rather than a production mode.\n"
    },
    {
      "directory": "creative-writing-modes",
      "name": "creative-writing-modes",
      "description": "Creative-writing addendum to /llm-writing. Load when putting prose on the page: draft, revise, bridge, vary, or polish.\n"
    },
    {
      "directory": "creative-writing-muse",
      "name": "creative-writing-muse",
      "description": "Load when no subagents are available and one agent must plan, draft, critique, research, and capture memory by switching stances.\n"
    },
    {
      "directory": "grill",
      "name": "grill",
      "description": "Use in conversation to stress-test a plan or direction. Interviews the human in rounds, asking every question that is ready with a recommended answer, until no decision is left open.\n"
    },
    {
      "directory": "grill-with-docs",
      "name": "grill-with-docs",
      "description": "Use when grilling should be grounded primarily in project artifacts. Loads `/grill`, checks project vocabulary and prior decisions first, and spawns bounded explorers when the answer should come from docs.\n"
    },
    {
      "directory": "information-hierarchy",
      "name": "information-hierarchy",
      "description": "Load for large human-facing outputs: reports, docs, multi-section\nexplanations, artifacts. Choose the right form for each beat (prose, diagram,\ntable, mockup) and put the answer first, depth behind it. If the medium allows, use progressive disclosure.\n"
    },
    {
      "directory": "intent-modeling",
      "name": "intent-modeling",
      "description": "Use before acting on human instructions: separate what they said from what they meant."
    },
    {
      "directory": "knowledge-layers",
      "name": "knowledge-layers",
      "description": "Use when deciding where knowledge goes or reading/writing durable docs: AGENTS.md, .context/, KB, docs/, and work directories."
    },
    {
      "directory": "llm-writing",
      "name": "llm-writing",
      "description": "Load before writing or revising human-facing text. Choose words deliberately, ground the piece in the reader's context, and remove default LLM phrasing before the final draft."
    },
    {
      "directory": "md-validation",
      "name": "md-validation",
      "description": "Use when validating markdown links or Mermaid diagrams."
    },
    {
      "directory": "project-setup",
      "name": "project-setup",
      "description": "One-time project setup for creative writing: interview the author about the project, writing samples, and voice, then create the AGENTS.md, kb/ layout, and style files every writing agent reads. User-invoked; run it once when starting a project.\n"
    },
    {
      "directory": "qi-layer",
      "name": "qi-layer",
      "description": "Use when writing or maintaining AGENTS.md, .context/CONTEXT.md, or a Claude-specific CLAUDE.md: keep intent docs minimal and load-bearing."
    },
    {
      "directory": "qi-maintenance",
      "name": "qi-maintenance",
      "description": "Load on agents that make durable changes to a project's files, so the colocated AGENTS.md and .context/ docs stay true for the next cold agent."
    },
    {
      "directory": "reader-sim",
      "name": "reader-sim",
      "description": "Read as a specified first-time reader persona and report the felt experience. Use for skill-only workflows when a draft needs persona-bound reader-response signal instead of analytical critique.\n"
    },
    {
      "directory": "reflect",
      "name": "reflect",
      "description": "Use when the user invokes it before you report: checks you delivered what they needed, not only what they literally asked, and routes knowledge capture."
    },
    {
      "directory": "shared-dao",
      "name": "shared-dao",
      "description": "Use when establishing shared vocabulary: resolve terminology early, one name per concept, vocab files as record."
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
      "directory": "structured-artifact",
      "name": "structured-artifact",
      "description": "Load when creating structured HTML artifacts to explain and present information.\n"
    },
    {
      "directory": "writing-principles",
      "name": "writing-principles",
      "description": "What fiction readers want (reader reward channels) and the specific ways LLM training damages them. Load when drafting prose, critiquing, or diagnosing why a passage feels flat.\n"
    },
    {
      "directory": "writing-staffing",
      "name": "writing-staffing",
      "description": "Dispatch reference for composing writing teams. Teaches which extra skills to attach, which files to pass, which resources to reference, and when to fan out versus run parallel lanes. Load when staffing a workflow.\n"
    },
    {
      "directory": "writing-sync",
      "name": "writing-sync",
      "description": "Load when syncing selected local files to a remote reading copy, or bringing remote edits back into those files. Google Drive/Docs only.\n"
    },
    {
      "directory": "zoom-out",
      "name": "zoom-out",
      "description": "Use when orienting in an unfamiliar area: fans out parallel explorers across structure, knowledge, and history, then synthesizes one orientation map."
    }
  ],
  "mcp": [],
  "hooks": []
}
const ROOT = dirname(fileURLToPath(import.meta.url))
const HOOK_DIR_TOKEN = DATA.tokens.hookDir
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

function runtimeServer(name, server) {
  const resolved = substituteMcpDir(server, join(ROOT, "mcp", name))
  if (!resolved.environment) return resolved

  const environment = {}
  for (const [key, value] of Object.entries(resolved.environment)) {
    const match = /^\{env:(.+)\}$/.exec(value)
    if (!match) {
      environment[key] = value
      continue
    }
    const resolvedValue = process.env[match[1]]
    if (resolvedValue !== undefined) environment[key] = resolvedValue
  }
  return { ...resolved, environment }
}

function encodeForJavaScriptString(value) {
  return value.replace(/[^A-Za-z0-9/._-]/g, (character) => {
    return `\\u${character.charCodeAt(0).toString(16).padStart(4, "0")}`
  })
}

async function renderHook(hook) {
  const hookDirectory = join(ROOT, "hooks", hook.name)
  const source = await readFile(join(hookDirectory, hook.fragment), "utf8")
  return source.replaceAll(HOOK_DIR_TOKEN, encodeForJavaScriptString(hookDirectory))
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
          throw new Error(`OpenCode hook ${hook.name} must export default { id, setup }`)
        }
        const cleanup = await definition.setup(ctx)
        if (typeof cleanup === "function") cleanups.push(cleanup)
      } catch (error) {
        console.error(`[${DATA.plugin}] failed to load hook ${hook.name}`, error)
      }
    }

    if (cleanups.length) {
      return async () => {
        for (const cleanup of cleanups.reverse()) await cleanup()
      }
    }
  },
}
