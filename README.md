# Creative Writing Skills

A comprehensive creative writing assistant for Claude Code and Claude.ai. This plugin provides six specialized skills to help you write prose in your personal style, capture brainstorming notes, create story documentation, analyze your writing, and more.

## What This Plugin Does

This plugin is a comprehensive creative writing assistant that helps you throughout your entire writing process. Whether you're brainstorming ideas, writing prose, or refining your work, it adapts to your needs and learns your personal style.

### Capabilities

- **Brainstorm and capture story ideas** - Explore plot options, worldbuilding, character arcs, and story structure without over-committing to decisions
- **Write prose in your personal style** - Generate scenes, chapters, and dialogue that match your unique voice and writing patterns
- **Create style guides from your writing** - Analyze your existing work to capture your voice, dialogue patterns, formatting preferences, and more
- **Get feedback and critique** - Receive constructive analysis of pacing, character consistency, dialogue quality, and prose
- **Build comprehensive story documentation** - Create character profiles, location wikis, lore pages, and reference materials for your fictional world
- **Maintain consistency across your project** - Automatically reference your established characters, settings, and story rules

### How to Use (After Installation)

Once you've installed the skills (see installation sections below for Claude.ai or Claude Code), mention **"creative writing"** in your requests, and the appropriate skills should activate based on your needs. If it doesn't work, you can try to mention **"cw-router"** directly, and if that doesn't work, make sure to mention to **"use a skill"**.

**Examples:**
- "Help me brainstorm ideas for my magic system" (creative writing)
- "Write the next scene where my protagonist discovers the truth" (use a skill)
- "Create a style guide based on these three chapters" (cw-router)
- "Critique this chapter for pacing and character consistency" (creative writing)

---

## For Claude.ai Users

### Prerequisites

- A paid Claude plan (Pro, Max, Team, or Enterprise) - Skills are not available on the free tier
- Code execution enabled in Settings → Capabilities (usually enabled by default)

### Installation

1. **Download skills from releases:**
   - Go to the [Releases page](https://github.com/haowjy/creative-writing-skills/releases)
   - Download the skill ZIP files you want to use:
     - `cw-router.zip`
     - `cw-prose-writing.zip`
     - `cw-story-critique.zip`
     - `cw-style-skill-creator.zip`
     - `cw-brainstorm-capture.zip`
     - `cw-official-wiki.zip`

2. **Upload to Claude.ai:**
   - Go to [Claude.ai](https://claude.ai)
   - Click your profile icon → **Settings**
   - Navigate to **Capabilities** → **Skills**
   - Click **"Upload skill"**
   - Upload each ZIP file (you can drag and drop or click to browse)

**Tips:**
- Upload only the skills you plan to use
- Start with cw-router, cw-prose-writing, and cw-brainstorm-capture for a core set
- You can add more skills later as needed

### Usage

After uploading skills, simply mention them in your conversations or let Claude automatically use them when appropriate.

**Basic usage examples:**
- "Use cw-brainstorm-capture to help me explore ideas for my antagonist"
- "Use cw-prose-writing to write this scene in my style"
- "Use cw-story-critique to analyze this chapter"

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
     - cw-prose-writing: Write prose in my style
     - cw-brainstorm-capture: Capture brainstorming notes
     - cw-story-critique: Provide writing feedback
     - cw-style-skill-creator: Create style guides
     - cw-official-wiki: Create story documentation

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

You should see `creative-writing-skills` listed with all six skills.

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

Once installed, simply ask Claude for help with creative writing tasks. The router skill will help guide you to the right tool, or Claude will automatically select the appropriate skill based on your request.

**Examples:**
- "Help me brainstorm ideas for my magic system"
- "Write the next scene where my protagonist confronts the antagonist"
- "Create a character profile for my protagonist"
- "Analyze the pacing of this chapter and give me feedback"
- "Create a style guide based on my existing chapters"

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
   (Uses cw-brainstorm-capture)
   ```

2. **Document finalized ideas:**
   ```
   "Create a wiki page for my magic system"
   (Uses cw-official-wiki)
   ```

3. **Analyze your writing style:**
   ```
   "Analyze these three chapters and create a style guide"
   (Uses cw-style-skill-creator)
   ```

4. **Write new content:**
   ```
   "Write the opening scene of chapter 5"
   (Uses cw-prose-writing with your style guide)
   ```

5. **Get feedback:**
   ```
   "Critique this chapter for pacing and character consistency"
   (Uses cw-story-critique)
   ```

---

## Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

## License

Apache License 2.0

See [LICENSE](LICENSE) file for details.
