# Creative Writing Skills

A comprehensive creative writing assistant for Claude Code and Claude.ai. This plugin provides 17 specialized agents and 12 composable skills for prose writing, brainstorming, critique, story architecture, knowledge management, and more.

> **Now also available as a [Meridian](https://github.com/haowjy/meridian-channel) package** — a more powerful multi-agent version with autonomous draft/critique loops, model routing across providers, and persistent project knowledge. See [For Meridian Users](#for-meridian-users) below.

## What This Plugin Does

This plugin is a comprehensive creative writing assistant that helps you throughout your entire writing process. Whether you're brainstorming ideas, writing prose, or refining your work, it adapts to your needs and learns your personal style.

### Capabilities

- **Brainstorm and capture story ideas** - Explore plot options, worldbuilding, character arcs, and story structure without over-committing to decisions
- **Write prose in your personal style** - Generate scenes, chapters, and dialogue that match your unique voice and writing patterns
- **Create style guides from your writing** - Analyze your existing work to capture your voice, dialogue patterns, formatting preferences, and more
- **Get feedback and critique** - Receive constructive analysis of pacing, character consistency, dialogue quality, and prose
- **Build comprehensive story documentation** - Create character profiles, location wikis, lore pages, and reference materials for your fictional world
- **Maintain consistency across your project** - Automatically reference your established characters, settings, and story rules
- **Run multi-agent draft/critique loops** - Orchestrate writers, critics, and reader simulations in parallel for faster, higher-quality iteration
- **Manage project knowledge** - Maintain a knowledge graph, continuity checks, and canonical wiki across your project

### How to Use (After Installation)

**Claude Code users:** The `story-orchestrator` agent is your primary entry point. It coordinates brainstorming, drafting, critique, and knowledge maintenance across all the specialized agents. Just describe what you want to do.

**Claude.ai web UI users:** Use the `cw-router` skill to guide you to the right skill for your task. Mention **"creative writing"** or **"cw-router"** in your requests.

**Examples:**
- "Help me brainstorm ideas for my magic system" (creative writing)
- "Write the next scene where my protagonist discovers the truth" (use a skill)
- "Critique this chapter for pacing and character consistency" (creative writing)

---

## Agents (17)

Agents are spawned for independent work. The orchestrators coordinate multi-agent workflows.

| Agent | Role |
|---|---|
| **story-orchestrator** | Primary entry point — coordinates all creative writing workflows |
| **draft-orchestrator** | Runs the draft/critique loop with writers, critics, reader-sims |
| **knowledge-orchestrator** | Coordinates wiki updates, graph maintenance, continuity checks |
| **writer** | Writes prose in the project's established style |
| **critic** | Structured critique across four reader reward channels |
| **reader-sim** | Simulates a reader's experience, reports per-channel engagement |
| **character-sim** | Simulates character behavior for dialogue testing and scene exploration |
| **brainstormer** | Wide-open option generation on a scoped question |
| **outliner** | Structural decomposition into beat sheets and arc maps |
| **explorer** | Fast project exploration — finds files, searches content |
| **researcher** | Web research for worldbuilding and fact-checking |
| **continuity-checker** | Checks drafts against established canon |
| **wiki-editor** | Creates and maintains wiki documentation |
| **graph-maintainer** | Updates the project knowledge graph |
| **chronicler** | Records session decisions into persistent notes |
| **session-miner** | Mines past session transcripts for unreported decisions |
| **style-creator** | Analyzes existing prose to create style guides |

## Skills (12)

Skills are composable knowledge modules loaded into agent context.

| Skill | Purpose |
|---|---|
| **brainstorming** | Exploratory idea generation with [TBD] markers |
| **prose-writing** | Voice matching, scene construction, prose craft |
| **prose-critique** | Multi-dimensional feedback (character, voice, structure, prose, continuity) |
| **prose-analysis** | Quantitative prose pattern analysis |
| **wiki-docs** | Encyclopedic documentation with citations |
| **story-architecture** | Arc shape, tension curves, structural analysis |
| **story-context** | Loading relevant story context before tasks |
| **story-decisions** | Decision logging and retrieval |
| **knowledge-graph** | Project knowledge graph maintenance |
| **writing-principles** | Four reward channels, AI failure modes, craft tradition |
| **writing-artifacts** | Artifact types and file conventions |
| **writing-staffing** | Agent roster and coordination patterns |

---

## For Claude.ai Users

### Prerequisites

- A paid Claude plan (Pro, Max, Team, or Enterprise) - Skills are not available on the free tier
- Code execution enabled in Settings → Capabilities (usually enabled by default)

### Installation

1. **Download skills from releases:**
   - Go to the [Releases page](https://github.com/haowjy/creative-writing-skills/releases)
   - Download the `.skill` files you want to use:
     - `cw-router.skill`
     - `prose-writing.skill`
     - `prose-critique.skill`
     - `brainstorming.skill`
     - `wiki-docs.skill`

2. **Upload to Claude.ai:**
   - Go to [Claude.ai](https://claude.ai)
   - Click your profile icon → **Settings**
   - Navigate to **Capabilities** → **Skills**
   - Click **"Upload skill"**
   - Upload each `.skill` file (you can drag and drop or click to browse)

**Tips:**
- Upload only the skills you plan to use
- Start with cw-router, prose-writing, and brainstorming for a core set
- You can add more skills later as needed

### Usage

After uploading skills, simply mention them in your conversations or let Claude automatically use them when appropriate.

**Basic usage examples:**
- "Use brainstorming to help me explore ideas for my antagonist"
- "Use prose-writing to write this scene in my style"
- "Use prose-critique to analyze this chapter"

### Setting Up a Writing Project (Recommended)

For the best experience, create a dedicated Project for your writing:

1. **Create a new Project:**
   - Go to Projects (left sidebar) → Create new project
   - Name it after your writing project (e.g., "My Fantasy Novel")

2. **Configure the Project to use skills:**
   - In Project Settings → Custom instructions, add:
     ```
     This is a creative writing project. You have access to the following skills:
     - cw-router: Guide me to the right skill
     - prose-writing: Write prose in my style
     - brainstorming: Capture brainstorming notes
     - prose-critique: Provide writing feedback
     - wiki-docs: Create story documentation

     Use these skills as appropriate for creative writing tasks.
     ```

     along with any other project-specific instructions (like a bit about what the story is about)

3. **Build your Project knowledge base:**
   - Use the skills in your chat to create documents (style guides, character profiles, worldbuilding pages)
   - Download/copy the documents Claude creates
   - Edit them if needed
   - Re-upload them to your Project knowledge base
   - Repeat this process as your story develops

**Pro tip:** With a configured Project, Claude will automatically use the appropriate skill based on your request, and all responses will be informed by your growing knowledge base. Each document you create and upload makes future responses more accurate and consistent!

**Important note about file formats:**
- Use **plain text formats** (.txt, .md) for your documents - these work best with AI
- If using a text editor, consider: VS Code, Cursor, Notepad, Notepad++, or any plain text editor
- **Avoid Microsoft Word (.docx)** - binary formats are harder for AI to read and format correctly

**Want an even better experience?** Consider using **Claude Code** (see below) with a text editor like VS Code or Cursor. This lets you work directly with files on your computer, making it much easier to organize and maintain your writing project.

---

## For Claude Code Users

### Prerequisites

**What is Node.js?**
Node.js is a JavaScript runtime that lets you run JavaScript programs on your computer (not just in web browsers). It comes with npm (Node Package Manager), which is used to install tools like Claude Code.

**What is Claude Code?**
Claude Code is a command-line interface (CLI) tool that lets you use Claude directly in your terminal and code editor. It's designed for developers and writers who work with files and projects.

---

#### For Windows Users (Recommended: WSL2)

**Why WSL2?**
Claude Code works best in a Unix-like environment with Unix commands. WSL2 (Windows Subsystem for Linux) gives you a full Linux environment on Windows, providing the best experience.

**Install WSL2:**
1. Open PowerShell as Administrator (right-click Start menu → "Windows PowerShell (Admin)")
2. Run: `wsl --install`
3. Restart your computer when prompted
4. After restart, Ubuntu will open and ask you to create a username and password
5. Install Node.js in WSL2:
   ```bash
   curl -fsSL https://deb.nodesource.com/setup_lts.x | sudo -E bash -
   sudo apt-get install -y nodejs
   ```
6. Verify: `node --version` and `npm --version`

For detailed troubleshooting, see [Microsoft's WSL Installation Guide](https://learn.microsoft.com/en-us/windows/wsl/install).

**Install Claude Code:**
Follow the quickstart guide at [Claude Code Quickstart](https://docs.claude.com/en/docs/claude-code/quickstart).

**Using WSL2:**
- Open Ubuntu from your Start menu to access the Linux terminal
- Your Windows files are accessible at `/mnt/c/` (C: drive), `/mnt/d/` (D: drive), etc.
- Navigate to your writing project: `cd /mnt/c/Users/YourUsername/Documents/my-novel`

**Advanced: Native Windows (PowerShell)**
You can also install Node.js and Claude Code directly on Windows, but some Unix-specific features may not work as expected. Download Node.js from [nodejs.org/download](https://nodejs.org/download) and follow the Windows installer.

---

#### For Mac/Linux Users

**Install Node.js:**
1. Visit [nodejs.org/download](https://nodejs.org/download)
2. Download the installer for your operating system
3. Run the installer and follow the setup wizard (this installs both Node.js and npm)
4. Verify installation: `node --version` and `npm --version`

**Install Claude Code:**
Follow the quickstart guide at [Claude Code Quickstart](https://docs.claude.com/en/docs/claude-code/quickstart).

**Using Terminal:**
- **Mac:** Open Terminal from Applications → Utilities or search "Terminal"
- **Linux:** Open Terminal from your applications menu or press Ctrl+Alt+T
- Navigate folders: `cd foldername` to enter, `cd ..` to go back
- See current location: `pwd`
- List files: `ls`

### Installation

#### Option 1: Install from GitHub (Recommended)

1. Add this marketplace to Claude Code:
   ```bash
   claude plugin marketplace add haowjy/creative-writing-skills
   ```

2. Install the plugin:
   ```bash
   claude plugin install creative-writing-skills@creative-writing-skills
   ```

3. Verify installation:
   ```bash
   claude plugin
   ```

You should see `creative-writing-skills` listed with all skills and agents.

#### Option 2: Install from Local Path

1. Clone this repository:
   ```bash
   git clone https://github.com/haowjy/creative-writing-skills.git
   ```

2. Add as a local marketplace:
   ```bash
   claude plugin marketplace add ./creative-writing-skills
   ```

3. Install the plugin:
   ```bash
   claude plugin install creative-writing-skills
   ```

### Usage

Once installed, the `story-orchestrator` agent is your primary entry point. It coordinates brainstorming, drafting, critique, and knowledge maintenance across all specialized agents. Simply describe what you want to do and the orchestrator handles the rest.

**Natural language examples:**
- "Help me brainstorm ideas for my magic system"
- "Write the next scene where my protagonist confronts the antagonist"
- "Create a character profile for my protagonist"
- "Analyze the pacing of this chapter and give me feedback"
- "Create a style guide based on my existing chapters"

**Slash commands (explicit mode switching):**

This plugin includes custom slash commands for explicit skill invocation:
- `/bs` - Brainstorm and explore story ideas
- `/write [style]` - Enter prose writing mode (optionally specify a style)
- `/wiki` - Create canonical wiki/documentation pages
- `/critique` - Get feedback on your writing

These commands are included in the plugin and work automatically after installation.

### Setting Up a Writing Project

For best results, create a dedicated directory for your writing project:

1. **Create a project directory:**
   ```bash
   mkdir my-novel
   cd my-novel
   ```

2. **Generate a style guide:**
   - Place sample chapters in your project directory
   - Ask: "Analyze my writing style and create a style guide"
   - Save the generated style guide (e.g., `style-guide.md`)

3. **Organize your project:**
   ```
   my-novel/
   ├── .claude/
   │   └── CLAUDE.md           # Project instructions
   ├── style-guide.md          # Your writing style
   ├── characters/             # Character profiles
   ├── world-building/         # Lore and setting
   └── chapters/               # Your manuscript
   ```

4. **Work with context:**
   When you work in this directory, Claude automatically uses your style guides, character profiles, and world-building notes to maintain consistency.

---

## Example Workflow

### Complete Writing Workflow

1. **Brainstorm your story:**
   ```
   "Help me brainstorm a magic system for my fantasy world"
   (Uses brainstorming)
   ```

2. **Document finalized ideas:**
   ```
   "Create a documentation page for my magic system"
   (Uses wiki-docs)
   ```

3. **Analyze your writing style:**
   ```
   "Analyze these three chapters and create a style guide"
   (Spawns style-creator agent)
   ```

4. **Write new content:**
   ```
   "Write the opening scene of chapter 5"
   (Uses prose-writing with your style guide)
   ```

5. **Get feedback:**
   ```
   "Critique this chapter for pacing and character consistency"
   (Uses prose-critique)
   ```

---

## Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

## License

Apache License 2.0

See [LICENSE](LICENSE) file for details.
