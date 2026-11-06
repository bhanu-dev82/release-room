# Build log: Release Room (Flip the Switch)

All times IST. Deadline: Sat 7 Nov 2026, 23:59. Submit by 21:00.

## 2026-11-06, M0 and M2 (demo app)

**Done**
- Local repos created: `release-room` and `release-room-demo-app`. Both are on git `main` with no remote. Nothing is public yet.
- Model roles set in `config/models.yaml` (all from OpenCode; each ID checked against `opencode models`):
  - triage: `nebius/deepseek-ai/DeepSeek-V4.1-Flash-1017`
  - fixer: `nebius/zai-org/GLM-5.3`
  - reviewer: `xai/grok-4.7`
  - Any role can be swapped by changing one line.
- Demo app `keepary-core` built with three seeded bugs and a green baseline.
  - `uv run --with pytest pytest -q` → **7 passed**
  - Baseline tests cover only behaviour the bugs don't touch, so they don't lock in any bug.

**Seeded bugs (reproduced)**

| ID | Review cluster (what users say) | Reproduction | Current | Expected |
|---|---|---|---|---|
| B1 | "App crashes when I scan a receipt without a date" | `parse_receipt("Total: 120", None)` | `AttributeError: 'NoneType' object has no attribute 'strip'` | Receipt with `date=None`, no crash |
| B2 | "Amounts show 100,000 instead of 1,00,000" | `format_inr(100000)` | `100,000` | `1,00,000` (lakh grouping) |
| B3 | "Hindi bills don't read the total" | `parse_receipt("कुल ₹१२०", "2026-11-01").total` | `None` | `120.0` |

**Decisions**
- Model choices follow the owner's picks. Leaderboard data I checked earlier was not used to override them.
- The reviewer uses a different model family from the fixer (xAI vs Z.ai), so it is an independent check.
- The pitch changes from "3 agents, 2 providers" to "3 agents, 3 models, all from OpenCode". Judges score Switch's role, not the provider count.

**Blocked on you**
1. [HUMAN] Install Switch Console. Run: `sudo apt install ~/Downloads/switch-console-amd64.deb`
2. [HUMAN] Create the Discord server `#release-room` and a bot (token goes into Switch Console only). Invite a second person.
3. [HUMAN] Confirm the public GitHub repos are OK. I'll create them only after you say yes.

**Next**
- M1 gates G1 to G5 once Switch Console is installed.
- M3: `tools/` (ingest, cluster, score, cards) with tests.

## 2026-11-06, M3 and M4 (tools, template, permissions)

**Decisions**
- **Solo entry.** The rules allow solo ("at least one AI agent and one person"). The second human is dropped from the demo.
- **Discord for the demo**, because judges recognise it. The README will also point to Switch's bundled Mattermost as the zero-setup way to reproduce, so a judge never has to create a Discord bot.
- **All three agents on OpenCode**, with three different models (see `config/models.yaml`). The reviewer is on a different model family from the fixer.
- **The human gate is OpenCode's own permission prompt, relayed by Switch.**
  - The fixer's `opencode.json` sets `git push *` and `gh pr *` to `ask`.
  - The fixer runs with Switch Auto mode **off**. OpenCode's auto mode approves `ask` rules; only `deny` survives it.
  - Expected result: only push/PR prompts reach the chat. To be confirmed in gate G2.
- **Each agent gets its own folder and config.**
  - OpenCode merges every `opencode.json` from the working directory up through parent folders, so a root config would leak into the agents' clones. I deleted it.
  - Checked with `opencode debug config`: each agent loads only its own file.
  - triage (`agents/triage`): no edits, no commit, push or `gh`.
  - fixer (`workspace/fixer/...`): edits and commits; push and PR ask a person.
  - reviewer (`workspace/reviewer/...`): no edits, commit, push or `gh`. It fetches the fixer's branch through a `fixer` git remote.

**Built**
- `tools/`: ingest (Play Console or sample CSV, UTF-16 aware, masks emails and phone numbers, drops reviewer names), cluster (TF-IDF + agglomerative, deterministic), score, cards (8 lines or fewer), replies (350-character Play limit), triage CLI.
- `data/reviews.synthetic.csv`: 66 synthetic reviews from `tools/make_sample.py` (seed 42): 22 crash (B1), 18 lakh format (B2), 14 Hindi total (B3), 12 noise.
- `make triage` gives exactly 3 cards, each 100% pure against the labels. The 5-star noise is excluded by `--max-stars 3`.
  - CARD-1 crash, severity 58
  - CARD-2 lakh format, 40.5
  - CARD-3 Hindi total, 37.9
- `switch/release-room.template.yaml`: 3 agents and 1 room, with room instructions and a kickoff. Field names follow docs/TEMPLATES.md.
- `make demo-data` / `make reset` / `make check` (tests plus a tracked-secrets scan).
- Tests: **28 passed**.

**Tuning record (clustering)**
- At distance threshold 0.85 the lakh cluster split in two. At 0.9 to 0.97 the three clusters were stable, so I chose 0.9.
- One 5-star review ("Best receipt app I have used") joined the crash cluster. Fixed by triaging complaints only (3 stars or fewer).
- Added review filler words ("app", "please", "don"…) to the stop words.

**Blocked on you**
1. [HUMAN] Discord bot setup and server connection in Switch Console.
2. [HUMAN] OK to make the two repos public on GitHub. The fixer's PR step and `make demo-data`'s default URL need `bhanu-dev82/release-room-demo-app` to exist.

**Next**
- Gates G1 to G5 in Switch.
- A B1 dry run of each model in OpenCode.
- README, video, submission.

## 2026-11-06, ~16:20: Switch up, model checks

**Switch**
- Fixed "Secure secret storage is unavailable". KDE picked KWallet, which is disabled on this machine.
  - The fix: launch with `--password-store=gnome-libsecret` (GNOME Keyring is running and unlocked), per Switch's Linux troubleshooting docs.
  - It's set in a user copy of the launcher, `~/.local/share/applications/switch-console.desktop`.
- Local Switch server running (server 0.31.0, Console 0.40.1). Discord connected as @bhanu82. One room so far (#general), with 0 agents.

**Model checks** (`opencode run`, prompt "Reply with exactly: OK")

| Role | Model | Result |
|---|---|---|
| triage | nebius/deepseek-ai/DeepSeek-V4.1-Flash-1017 | OK (3 s) |
| fixer | nebius/zai-org/GLM-5.3 | OK (2 s) |
| reviewer | xai/grok-4.7 | **Fail**: `invalid_grant: Invalid or unknown refresh token`. OpenCode's stored xAI login has expired, so it needs a fresh `opencode auth login`. |

**Fixer dry run on B1** (GLM-5.3, throwaway clone in /tmp, no Switch)
- 23 s. It wrote a failing test from the complaint, saw it fail with `AttributeError`, fixed `parse_receipt`, and committed on `rr/card-1`.
- 2 files, +8/−2. An independent test run: **8 passed**.
- The 6-line summary (Cause/Fix/Test/Files/Risk/Diff) matched the format in the instructions.

## 2026-11-06, ~17:30: repos public, OpenCode version problem

**Published.** Both repos are public with MIT licences (GitHub detects them), topics and a README written for judges.
- https://github.com/bhanu-dev82/release-room
- https://github.com/bhanu-dev82/release-room-demo-app (tag `seeded` = the commit with the three bugs)

`make reset` now clones from GitHub. A dry-run `git push` of a branch from the fixer's clone succeeds, and `gh` has admin access to the repo.

**CI removed.** GitHub Actions won't start jobs on this account: "account is locked due to a billing issue". I deleted the workflow files and badges rather than show judges a red badge. Tests run with `make test` / `make check`.

**"Sign-in could not be checked" for OpenCode in Switch** is a known Switch bug: [switch#1421](https://github.com/sandbox-quantum/switch/issues/1421), P1, open. Switch 0.40 supports OpenCode 1.x only.
- OpenCode 2.x prints `server listening`; Switch waits for `opencode server listening`.
- 2.x also returns HTML from `/global/health` and `/provider`.
- I reproduced both against the installed 2.2.3.

**Fix without touching the daily OpenCode 2.2.3:**
- Installed `opencode-ai@1.19.5` into `~/.local/opencode-switch/`.
- Wrapper `~/.local/bin/opencode-switch` sets its own `XDG_DATA_HOME` (`~/.local/share/opencode-switch`), so 1.x never opens 2.x's database.
- 1.x has its own empty `auth.json`. 2.x keeps its logins in its database, and 1.x's file format differs, so I didn't share files.
- Both 1.x and the models.dev catalogue know `nebius` (`NEBIUS_API_KEY`) and `xai` (`XAI_API_KEY`), and all three chosen model IDs are listed.
- [HUMAN] Log in for 1.x: `opencode-switch auth login` → Nebius, then xAI. Then in Switch: Agent providers → OpenCode → Change source → Path Override → `/home/bhd/.local/bin/opencode-switch` → Recheck.
- The OpenCode Console key saved in the old `auth.json` has expired ("Create a new API key in OpenCode Console"). Unused by our three models.

## 2026-11-06, ~18:00: template import blocked, controller PATH

**Symptom.** In Switch's template form, "Create all" is disabled: "None of your machines on this server can run triage, fixer, or reviewer yet: opencode isn't installed or ready (login could not be checked)." The form shows Machine: "Not set by the template".

**Cause (from Switch's source, `console/packages/agent-controller/src/doctor.ts` and `status.ts`).**
- The machine's own controller decides provider readiness, not Console's Path Override.
- It finds the CLI with `PathProviderLocator`, which takes the first `opencode` on PATH. The login-shell PATH gives `~/.opencode/bin` (OpenCode 2.2.3), so the 1.x Path Override never applies.
- The 2.x check fails, so the controller reports "login could not be checked" (switch#1421).

**Verified.** The 1.x wrapper passes the same steps the controller runs. `opencode serve` prints `opencode server listening on …` (the prefix Switch waits for). `/global/health` returns `{"healthy":true,"version":"1.19.5"}`. `/provider` lists `openrouter` and `opencode`.

**Fix (Switch only).**
- `~/.local/opencode-switch/bin/opencode` is the 1.x wrapper under the name `opencode`.
- `~/.local/bin/switch-console-launch` puts that folder first on PATH, then starts Switch Console with `--password-store=gnome-libsecret`.
- The app menu entry now runs the launcher. Your terminal still finds 2.2.3.

**Still needed.**
- 1.x has no Nebius or xAI login yet. The template's three models need `opencode-switch auth login` for Nebius Token Factory and for xAI. The 1.x model list only shows models from connected providers.
- Switch Console must be fully quit and started from the app menu, so the new PATH applies.

## 2026-11-07 (early), restored the three-model OpenCode setup

**Decision.** Multi-model stays. Each agent uses a different model family: DeepSeek V4.1 Flash-1017 (triage), GLM-5.3 (fixer), Grok 4.7 (reviewer). Antigravity is dropped as the main provider because Switch can't pick its model.

**Set up.**
- OpenCode 1.19.5 is installed in `~/.local/opencode-switch` (npm prefix, not global). The version is the one Switch's own bug report confirms works.
- `~/.local/bin/opencode-switch` is the 1.x command. It sets its own data folder, `~/.local/share/opencode-switch`, so logins and sessions stay separate from 2.2.3.
- `~/.local/bin/switch-console-launch` puts the 1.x shim first on PATH for Switch Console only. Start Switch from the app menu.
- Your terminal's `opencode` is still 2.2.3.
- Checked: `opencode serve` prints `opencode server listening on …`, `/global/health` is healthy at 1.19.5, and `/provider` lists `openrouter`.

**Template and config.** The files match commit 6734069: the three agents use `provider: opencode`, with the three model IDs and the `opencode.json` permission files.

**Still needed (human).**
1. `opencode-switch auth login`, then Nebius Token Factory and paste the key.
2. `opencode-switch auth login`, then xAI. The 1.x login may ask for an API key from console.x.ai rather than your subscription login.
3. Quit Switch Console and reopen it from the app menu. Then Settings → Agent providers → OpenCode → Recheck should read Signed in.

## 2026-11-06, ~21:45: "Sign-in could not be checked" came back

**Symptom.** Settings → Agent providers → OpenCode shows v1.19.5 (Path Override) but "Sign-in could not be checked… as its agents controller reported it to Switch".

**Cause.** The controller (a separate process) finds `opencode` on its own PATH, and the Path Override only affects Console's own check. Console builds the controller's PATH from your login shell, and `~/.bashrc` line 159 (added by OpenCode 2.x's installer) puts `~/.opencode/bin` first. `/proc/<controller>/environ` showed `~/.opencode/bin` third and the 1.x shim eighth. It picked 2.2.3, which fails the check (switch#1421).

**Fix.**
- `~/.bashrc` line 159 now reads `[ -z "$SWITCH_OPENCODE_V1" ] && export PATH=/home/bhd/.opencode/bin:$PATH`. Backup: `~/.bashrc.bak-before-switch-opencode`.
- `~/.local/bin/switch-console-launch` exports `SWITCH_OPENCODE_V1=1`, so only shells started under Switch Console skip that line.
- Test: a login shell with the launcher's environment gives `opencode` → 1.19.5. A normal terminal still gives 2.2.3.

**Model check through OpenCode 1.19.5** (logins now in the Switch data folder: Nebius api key, xAI oauth).
- nebius/deepseek-ai/DeepSeek-V4.1-Flash-1017: OK (10 s)
- nebius/zai-org/GLM-5.3: OK (9 s)
- xai/grok-4.7: OK (9 s)

**Next.** Restart Switch Console fully from the app menu (the controller only reads PATH at start), then Recheck.
