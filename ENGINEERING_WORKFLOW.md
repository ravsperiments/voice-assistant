# Software Engineering Workflow Guide
## Voice Assistant Project - GitHub Task Management

**Status:** Active
**Last Updated:** 2025-10-25
**Audience:** Development Team, Architects, Project Leads

---

## Table of Contents

1. [Overview](#overview)
2. [GitHub Task Management](#github-task-management)
3. [Workflow: Task Lifecycle](#workflow-task-lifecycle)
4. [Command Reference](#command-reference)
5. [Best Practices](#best-practices)
6. [Troubleshooting](#troubleshooting)

---

## Overview

This guide describes how the development team manages work using GitHub Issues integrated with Claude Code automation. Tasks flow through clear states, and the `scripts/github_tasks.py` utility keeps the issue tracker synchronized with development progress.

### Core Principles

- **Single Source of Truth:** GitHub Issues are the authoritative task list
- **Transparent Progress:** All task state changes are logged in GitHub
- **Resumable Work:** Any team member can pick up unfinished work by reviewing GitHub
- **Automated Updates:** Scripts enable fast, consistent task management
- **Design Alignment:** All tasks must align with DESIGN_DOC.md and current phase

### Prerequisites

- GitHub Personal Access Token with `repo` scope (stored in `.env`)
- Python 3.11+
- Git command-line tools
- Access to this repository

---

## GitHub Task Management

### Setup (One-Time)

#### 1. Create GitHub Personal Access Token

1. Go to https://github.com/settings/tokens/new
2. Select scope: `repo` (full control of private repositories)
3. Name it: `voice-assistant-cli` or similar
4. Click "Generate token"
5. Copy the token immediately (won't be shown again)

#### 2. Store Token in .env

```bash
# In /Users/ravi/Documents/Projects/voice-assistant/.env
GITHUB_TOKEN=github_pat_YOUR_TOKEN_HERE
```

**IMPORTANT:** Never commit `.env` to git. It's already in `.gitignore`.

#### 3. Verify Setup

```bash
cd /Users/ravi/Documents/Projects/voice-assistant
export GITHUB_TOKEN=$(grep GITHUB_TOKEN .env | cut -d= -f2)
python scripts/github_tasks.py list --state open --limit 3
```

You should see a list of open issues.

---

## Workflow: Task Lifecycle

### State Flow

```
[Created] → [Assigned] → [In Progress] → [Testing] → [Completed]
                            ↓
                        [Blocked]
                            ↓
                        [Reopened]
```

### 1. Task Creation

**When:**
- New feature/bug discovered
- Architecture review identifies work
- Team prioritizes backlog items

**How:**

Option A: Create via GitHub Web UI (fastest)
```
https://github.com/ravsperiments/voice-assistant/issues/new
```

Option B: Create via CLI Script
```bash
export GITHUB_TOKEN=$(grep GITHUB_TOKEN .env | cut -d= -f2)

python scripts/github_tasks.py create \
  --title "TASK-NNN: Short description" \
  --body "Detailed description of work needed" \
  --labels "epic:core,type:feature,priority:P1" \
  --milestone "MVP v1.0"
```

**Task Title Format:**
```
TASK-NNN: [Type] [Epic] - [Brief Description]

Examples:
✅ TASK-019: Priority 1 - Implement async state machine with structured logging
✅ TASK-001: Create conversation.py module for multi-turn support
❌ TASK-099: Fix stuff  (too vague)
❌ TASK-100: Implement  (incomplete)
```

**Label Format:**
- Epic: `epic:core`, `epic:polish`, `epic:provider-abstractions`
- Type: `type:feature`, `type:bug`, `type:refactor`, `type:docs`, `type:testing`
- Priority: `priority:P0`, `priority:P1`, `priority:P2`
- Component: `component:llm`, `component:stt`, `component:tts`, `component:config`

### 2. Task Assignment & Kickoff

**When Engineer Starts Work:**

1. Assign task to yourself (or ask to be assigned)
2. Update GitHub with initial status comment:

```bash
# Get token
export GITHUB_TOKEN=$(grep GITHUB_TOKEN .env | cut -d= -f2)

# Create a branch (use GitHub issue number in branch name)
git checkout -b task/TASK-NNN-short-description

# Add comment to GitHub issue to signal work starting
# You'll need to do this via the web UI or use gh command if available
```

**What to Document:**
- Which branch you created
- Initial approach/plan
- Any blockers or questions
- Estimated completion date

### 3. Development: In Progress

**During Development:**

```bash
# Work on your branch
git checkout task/TASK-NNN-short-description

# Make commits (these automatically link to issue if commit message mentions #NNN)
git commit -m "Implementation of XYZ feature

- Added new function calculate_latency()
- Updated config parsing for timeout settings
- Added unit tests for edge cases

Addresses #NNN
"
```

**Commit Message Best Practices:**
- First line: Concise summary (<50 chars)
- Blank line
- Bullet points describing changes
- Include issue reference: `Addresses #NNN` or `Fixes #NNN`
- Reference any related issues: `Relates to #MMM`

### 4. Pause/Blocking Work

**If Stuck or Need Help:**

```bash
export GITHUB_TOKEN=$(grep GITHUB_TOKEN .env | cut -d= -f2)

python scripts/github_tasks.py update NNN \
  --add-labels "status:blocked" \
  --body "Comment about why blocked, what's needed"
```

Or add a GitHub comment explaining:
- What's blocking you
- What's needed to unblock
- Who might be able to help

### 5. Code Review & Testing

**Before Marking Complete:**

1. Create Pull Request:
```bash
git push -u origin task/TASK-NNN-short-description

# Then create PR on GitHub with description
gh pr create --title "TASK-NNN: Description" \
  --body "Closes #NNN" \
  --draft  # Start as draft if still testing
```

2. Run tests locally:
```bash
pytest tests/
python -m pytest --cov=components/ tests/
```

3. Get code review from team member

4. Update GitHub with test results:
```bash
# Update issue with test status
python scripts/github_tasks.py update NNN \
  --body "✅ Tests passing
- Unit tests: 24/24 passing
- Integration tests: 5/5 passing
- Code coverage: 89%

Ready for review."
```

### 6. Task Completion

**When Finished & Tested:**

```bash
export GITHUB_TOKEN=$(grep GITHUB_TOKEN .env | cut -d= -f2)

# Update issue to mark as complete
python scripts/github_tasks.py close NNN

# Git workflow
git checkout main
git pull origin main
git merge task/TASK-NNN-short-description
git push origin main
git branch -d task/TASK-NNN-short-description

# Create commit message noting completion
git log --oneline -1
# Should show: "TASK-NNN: ..."
```

**GitHub Issue Should Show:**
- ✅ All checklist items completed
- ✅ Tests passing
- ✅ Code reviewed
- ✅ Merged to main
- Closed with reference to commit/PR

### 7. Reopening Tasks

**If Issue Found After Completion:**

```bash
export GITHUB_TOKEN=$(grep GITHUB_TOKEN .env | cut -d= -f2)

# Reopen the issue
python scripts/github_tasks.py update NNN --state open

# Add comment explaining issue
# (via GitHub web UI or gh command)

# Create follow-up branch for fix
git checkout -b task/TASK-NNN-followup-fix
```

---

## Command Reference

### Authenticate

```bash
# Load token from .env
export GITHUB_TOKEN=$(grep GITHUB_TOKEN .env | cut -d= -f2)

# Verify
echo $GITHUB_TOKEN  # Should show token (keep private!)
```

### List Issues

```bash
# All open issues (table format)
python scripts/github_tasks.py list --state open

# Open issues in JSON (for scripting)
python scripts/github_tasks.py list --state open --format json

# Filter by milestone
python scripts/github_tasks.py list --state open | grep "MVP v1.0"

# Filter by label
python scripts/github_tasks.py list --state open --labels "priority:P1"

# Limit results
python scripts/github_tasks.py list --state open --limit 5

# Closed issues (review completed work)
python scripts/github_tasks.py list --state closed --limit 10
```

### Create Issue

```bash
# Simple creation
python scripts/github_tasks.py create \
  --title "TASK-NNN: My feature" \
  --body "Description of the work"

# With labels and milestone
python scripts/github_tasks.py create \
  --title "TASK-NNN: My feature" \
  --body "Description" \
  --labels "epic:core,type:feature,priority:P1" \
  --milestone "MVP v1.0"

# With body from file
python scripts/github_tasks.py create \
  --title "TASK-NNN: My feature" \
  --body-file task_description.md \
  --labels "epic:core,type:feature" \
  --milestone "MVP v1.0"

# Assign to people
python scripts/github_tasks.py create \
  --title "TASK-NNN: My feature" \
  --body "Description" \
  --assignees "user1,user2"
```

### Update Issue

```bash
# Change title
python scripts/github_tasks.py update 123 \
  --title "TASK-123: New title"

# Change body/description
python scripts/github_tasks.py update 123 \
  --body "Updated description"

# Add labels
python scripts/github_tasks.py update 123 \
  --add-labels "status:in-progress,type:feature"

# Remove labels
python scripts/github_tasks.py update 123 \
  --remove-labels "status:blocked"

# Set labels (replace all)
python scripts/github_tasks.py update 123 \
  --labels "epic:core,type:feature,priority:P1"

# Change milestone
python scripts/github_tasks.py update 123 \
  --milestone "Phase 2.1: Multi-Turn"

# Close issue
python scripts/github_tasks.py update 123 --state closed
```

### Close Issue

```bash
python scripts/github_tasks.py close 123
```

### Practical Workflows

#### Start Work on a Task

```bash
export GITHUB_TOKEN=$(grep GITHUB_TOKEN .env | cut -d= -f2)

# Get task number (e.g., 19)
TASK=19

# Create and switch to working branch
git checkout -b task/TASK-$TASK-short-name

# Update GitHub to show in progress
python scripts/github_tasks.py update $TASK \
  --add-labels "status:in-progress" \
  --remove-labels "status:blocked"

# Add comment (via web UI or gh)
# "Starting work on this task - branch task/TASK-19-short-name"

echo "Ready to work on TASK-$TASK"
```

#### Resume Work on a Task

```bash
export GITHUB_TOKEN=$(grep GITHUB_TOKEN .env | cut -d= -f2)

# List blocked tasks
python scripts/github_tasks.py list --state open --labels "status:blocked"

# Pick one, get details from GitHub, checkout branch
git fetch origin
git checkout task/TASK-NNN-short-name

# Update status to show resuming
python scripts/github_tasks.py update NNN \
  --remove-labels "status:blocked"

echo "Resumed work on TASK-NNN"
```

#### Complete and Close Task

```bash
export GITHUB_TOKEN=$(grep GITHUB_TOKEN .env | cut -d= -f2)

TASK=19

# Make sure all changes committed
git status

# Create final commit
git commit -m "TASK-$TASK: Final commit with all tests passing

- Feature complete
- All tests passing
- Code reviewed and merged

Closes #$TASK"

# Merge to main
git checkout main
git pull
git merge task/TASK-$TASK-short-name
git push

# Close the issue
python scripts/github_tasks.py close $TASK

echo "✅ TASK-$TASK complete and closed"
```

#### Update Progress During Work

```bash
export GITHUB_TOKEN=$(grep GITHUB_TOKEN .env | cut -d= -f2)

# Update issue with progress
python scripts/github_tasks.py update 123 \
  --body "Progress Update:
✅ Implemented state machine
✅ Added structured logging
🔄 Currently working on: health check endpoint
⏱️ Estimated completion: 2 more days"
```

---

## Best Practices

### Task Design

1. **Size:** Aim for 1-3 day tasks (8-24 hours)
   - Too big: Hard to estimate, causes context switching
   - Too small: Overhead of management outweighs value

2. **Scope:** Each task should deliver one clear thing
   - ✅ "Add JSON logging to all components"
   - ❌ "Add logging and refactor main.py and update config"

3. **Acceptance Criteria:** Be specific and testable
   - ✅ "When user speaks during response, system returns to idle state within 500ms"
   - ❌ "Handle concurrent user input"

4. **Labels:** Use consistently for filtering and reporting
   - Always use epic label: `epic:*`
   - Always use type label: `type:*`
   - Always use priority for work ordering

### Development

1. **Branch Naming:**
   ```
   task/TASK-NNN-short-description  (active work)
   bugfix/TASK-NNN-short-description (bug fixes)
   refactor/TASK-NNN-short-description (refactoring)
   ```

2. **Commit Messages:**
   - Reference issue number: `Addresses #NNN` or `Closes #NNN`
   - Explain WHY not just WHAT
   - Keep first line <50 chars
   - Include testing info: "Tests: 15/15 passing"

3. **Testing:**
   - Write tests before/alongside code (TDD preferred)
   - Update tests when refactoring
   - Document any manual testing in issue
   - Run full test suite before marking complete

4. **Code Review:**
   - Get at least one review before closing
   - Address feedback in follow-up commits
   - Mark as "approved" in GitHub

### GitHub Workflow

1. **When Creating Tasks:**
   - Set realistic estimates
   - Check dependencies before assigning
   - Use consistent naming (TASK-NNN format)
   - Add acceptance criteria checklist

2. **When Updating Tasks:**
   - Keep descriptions accurate
   - Update labels to reflect current state
   - Add progress comments if taking longer
   - Request help early if blocked

3. **When Closing Tasks:**
   - Verify all acceptance criteria met
   - Ensure tests passing
   - Confirm code reviewed
   - Reference merged PR/commit

### Resuming Work (For Claude Code)

When using Claude Code to resume work:

1. **Check GitHub for context:**
   ```bash
   export GITHUB_TOKEN=$(grep GITHUB_TOKEN .env | cut -d= -f2)
   python scripts/github_tasks.py list --state open --limit 5
   ```

2. **Pick up incomplete task:**
   - Find task with `status:in-progress` label
   - Read full description and comments
   - Checkout the corresponding branch
   - Check commit history for context

3. **Update GitHub to show resuming:**
   ```bash
   python scripts/github_tasks.py update NNN \
     --body "Resuming work - had paused due to [reason]"
   ```

4. **Continue development from branch**

5. **Close task when complete with final update:**
   ```bash
   python scripts/github_tasks.py close NNN
   ```

---

## Troubleshooting

### "GITHUB_TOKEN environment variable is required"

**Problem:** Token not found in environment

**Solution:**
```bash
# Check .env exists
ls -la .env

# Load token
export GITHUB_TOKEN=$(grep GITHUB_TOKEN .env | cut -d= -f2)

# Verify
echo $GITHUB_TOKEN
```

### "Unable to determine repository"

**Problem:** Script can't find your GitHub repo

**Solution:**
```bash
# Explicitly specify repo
python scripts/github_tasks.py list --repo ravsperiments/voice-assistant --state open
```

Or check git config:
```bash
git config --get remote.origin.url
```

### "401 Unauthorized"

**Problem:** Token is invalid or expired

**Solution:**
1. Generate new token: https://github.com/settings/tokens/new
2. Update `.env` with new token
3. Re-export: `export GITHUB_TOKEN=$(grep GITHUB_TOKEN .env | cut -d= -f2)`

### Script is slow

**Problem:** GitHub API calls are slow

**Solution:**
- Filter to specific state: `--state open` (faster than `all`)
- Use `--limit` to reduce results
- Use `--format json` for piping to other tools

### Can't find completed task in history

**Problem:** Need to see closed issues

**Solution:**
```bash
python scripts/github_tasks.py list --state closed --limit 20
```

### Accidentally closed wrong issue

**Problem:** Closed the wrong task

**Solution:**
```bash
export GITHUB_TOKEN=$(grep GITHUB_TOKEN .env | cut -d= -f2)
python scripts/github_tasks.py update NNN --state open
```

---

## Integration with Claude Code

### Claude Code as Development Coordinator

Claude Code can use this workflow to:

1. **Query current work:**
   ```bash
   export GITHUB_TOKEN=$(grep GITHUB_TOKEN .env | cut -d= -f2)
   python scripts/github_tasks.py list --state open --labels "status:in-progress"
   ```

2. **Create tasks from design decisions:**
   ```bash
   python scripts/github_tasks.py create \
     --title "TASK-NNN: Implementation based on design review" \
     --body "Detailed implementation notes" \
     --labels "epic:core,type:feature"
   ```

3. **Update progress:**
   ```bash
   python scripts/github_tasks.py update NNN \
     --add-labels "status:in-progress"
   ```

4. **Close completed work:**
   ```bash
   python scripts/github_tasks.py close NNN
   ```

5. **Find resumable work:**
   ```bash
   python scripts/github_tasks.py list --state open \
     --labels "status:in-progress,status:blocked"
   ```

### Claude Code Prompt Updates

When Claude Code is asked to work on tasks, it should:

1. **First:** List open issues in current milestone
   ```
   Check what work is already tracked in GitHub
   ```

2. **During:** Update GitHub as progress is made
   ```
   Mark task status in GitHub to show work in progress
   ```

3. **After:** Close issues when complete
   ```
   Update GitHub to mark work complete
   ```

---

## Quick Reference Card

```bash
# Load token (do this in every session)
export GITHUB_TOKEN=$(grep GITHUB_TOKEN .env | cut -d= -f2)

# Check current work
python scripts/github_tasks.py list --state open --limit 10

# Start new task
git checkout -b task/TASK-NNN-name
python scripts/github_tasks.py update NNN --add-labels "status:in-progress"

# Save progress
git commit -m "TASK-NNN: Progress on feature - Addresses #NNN"
python scripts/github_tasks.py update NNN --body "Updated: [progress notes]"

# Get help (blocked)
python scripts/github_tasks.py update NNN --add-labels "status:blocked"

# Resume work
git checkout task/TASK-NNN-name
python scripts/github_tasks.py update NNN --remove-labels "status:blocked"

# Complete task
git push
python scripts/github_tasks.py close NNN

# View completed work
python scripts/github_tasks.py list --state closed --limit 10
```

---

## Related Documentation

- **DESIGN_DOC.md** - Architecture and design decisions
- **IMPLEMENTATION_PLAN.md** - Detailed task breakdown
- **CLAUDE.md** - Project setup and development guide
- **README.md** - User-facing documentation
- **DEPENDENCY_GRAPH.md** - Task dependencies and critical path

---

**Document Status:** Active
**Last Review:** 2025-10-25
**Next Review:** After MVP v1.0 completion

