---
name: commit
description: >-
  Use this skill when the user asks to commit changes, make git commits, perform file-wise commits,
  or invokes /commit. Creates clean, file-by-file atomic Git commits authored strictly by
  r.devkota.98@gmail.com with zero AI attribution, strictly keeping all commits local (never pushing
  to the remote repository). Also ensures codebase architecture follows FastAPI app.py conventions
  with /sources, /services, custom exception handling, and custom logging.
---

# Local File-Wise Git Commit Skill (`/commit`)

Turn working tree changes into atomic, file-by-file Git commits authored strictly as `r.devkota.98@gmail.com`, ensuring all commits **remain local** (never pushed to remote repository), and upholding project architecture conventions.

## 1. Non-Negotiable Core Rules

### A. Author & Committer Identity
- Every commit **MUST** be authored and committed with:
  - **Email**: `r.devkota.98@gmail.com`
  - **Name**: `rajandevkota98`
- Enforce explicitly on every commit invocation:
  ```bash
  GIT_AUTHOR_NAME="rajandevkota98" \
  GIT_AUTHOR_EMAIL="r.devkota.98@gmail.com" \
  GIT_COMMITTER_NAME="rajandevkota98" \
  GIT_COMMITTER_EMAIL="r.devkota.98@gmail.com" \
  git commit -m "<message>"
  ```
- Before committing, verify git config:
  ```bash
  git config user.name "rajandevkota98"
  git config user.email "r.devkota.98@gmail.com"
  ```

### B. Strict Local-Only — NEVER Push to Remote
- **NO COMMITS WILL GO TO THE REMOTE REPOSITORY.**
- **NEVER** run `git push`, `git push --all`, or `git push --force`.
- All commits remain strictly within the local Git repository.
- Do not trigger any remote pipelines or workflows.

### C. Zero AI Attribution
- **NEVER** add trailers such as `Co-Authored-By: ...`, `Generated-by: ...`, `Signed-off-by: AI`, or robot/AI emojis (`🤖`, `🧠`, `⚡`).
- **NEVER** mention "Antigravity", "Gemini", "Claude", "ChatGPT", "LLM", or "AI" in commit messages or git logs.
- Commit messages must read as natural, clean, professional human commit messages.

### D. File-by-File / Granular Commit Strategy
- Stage and commit files **one by one** (`git add <file>`), rather than blanket `git add .` or `git add -A`.
- If two files are strictly inseparable (e.g. an implementation file and its accompanying unit test), they may be committed together if logically required.
- Order commits logically:
  1. Configurations, schemas, dependencies (`requirements.txt`, `.gitignore`)
  2. Core foundation (custom exceptions, custom logging, base classes)
  3. Input sources (`sources/`)
  4. Core services (`services/`)
  5. Application entrypoint & routes (`app.py`)
  6. Tests & documentation

---

## 2. Codebase Architecture Alignment

When reviewing diffs or preparing commits in this project, verify code complies with:
- **`app.py`**: Central FastAPI application entrypoint with lifespan events, custom middleware, and route mounting.
- **`/sources`**: Input handling, data ingestion, file/document loaders, and external resource extraction.
- **`/services`**: Business logic, OCR engines, processing pipelines, and data transformation.
- **Custom Exception Handling**: Custom exception hierarchy inheriting from a base exception, handled via FastAPI exception handlers returning uniform error payloads.
- **Custom Logging**: Structured, formatted logging throughout all modules, avoiding unformatted `print()` statements.

---

## 3. Step-by-Step Commit Procedure

### Step 1: Survey & Inspect Working Tree
Run these commands to inspect all modifications and untracked files:
```bash
git status --short
git diff --stat
```

Check for files that should NEVER be committed (e.g., `.env`, credentials, secrets, cache files, virtualenvs). If unignored, add them to `.gitignore` first:
```bash
git add .gitignore
GIT_AUTHOR_NAME="rajandevkota98" \
GIT_AUTHOR_EMAIL="r.devkota.98@gmail.com" \
GIT_COMMITTER_NAME="rajandevkota98" \
GIT_COMMITTER_EMAIL="r.devkota.98@gmail.com" \
git commit -m "chore: update .gitignore"
```

### Step 2: Commit Each File Individually
For each changed or untracked file:

1. **Review file diff**:
   ```bash
   git diff -- <file_path>
   ```

2. **Stage the specific file**:
   ```bash
   git add -- <file_path>
   ```

3. **Format Conventional Commit Message**:
   Format: `<type>(<scope>): <subject>`
   - `type`: `feat`, `fix`, `refactor`, `chore`, `docs`, `test`, `style`, `perf`
   - `subject`: Imperative mood, lower case, no period at end, ≤ 72 characters.
   - Examples:
     - `feat(app): initialize fastapi application with lifespan and routes`
     - `feat(sources): add file and stream data source handlers`
     - `feat(services): implement ocr pipeline service`
     - `feat(core): add custom exceptions and standardized error handlers`
     - `feat(core): add structured logging with colored formatter`
     - `chore(deps): add requirements.txt`

4. **Commit with Identity**:
   ```bash
   GIT_AUTHOR_NAME="rajandevkota98" \
   GIT_AUTHOR_EMAIL="r.devkota.98@gmail.com" \
   GIT_COMMITTER_NAME="rajandevkota98" \
   GIT_COMMITTER_EMAIL="r.devkota.98@gmail.com" \
   git commit -m "<type>(<scope>): <subject>"
   ```

5. **Verify Commit Author**:
   ```bash
   git log -1 --format="commit %h%nAuthor: %an <%ae>%nDate:   %ad%n%n    %s"
   ```
   Confirm author is `rajandevkota98 <r.devkota.98@gmail.com>`.

### Step 3: Final Verification (NO PUSH)
Once all files are committed:
```bash
git status
git log -n 10 --oneline
```
- Verify working tree is clean.
- **DO NOT RUN `git push`**. Reiterate to the user that commits have been safely recorded in the local repository and no commits were sent to the remote repository.
