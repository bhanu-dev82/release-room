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
