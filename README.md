# Release Room

A one-person release desk for an app studio, run in one Discord room by Switch.

Status: in progress for the Flip the Switch hackathon (deadline Sat 7 Nov 2026, 23:59 IST).

## 1. The problem
(to write: a real user, 3 to 5 sentences)

## 2. How it works
(to write: diagram of the room, agents, and the human gate)

## 3. How Switch is used
(to write, Switch section first)

| Switch feature | Where we use it | Without Switch |
|---|---|---|
| Agents as named teammates | triage, fixer, reviewer | Three separate tools, no shared room |
| Room Instructions | the release policy | The policy drifts across prompts |
| Room history | fixer reads the cards | Humans re-explain every bug |
| @mention handoffs | triage → fixer → reviewer | Humans copy-paste between tools |
| Permission prompts | the push and PR gate | The agent pushes unchecked |

## 4. Models
See `config/models.yaml`. Three roles, three model IDs, all from OpenCode.

## 5. Quickstart
(to write and test on a clean clone)

## 6. Tests
(to write: `make test`)

## 7. Limitations and next steps
(to write)

## License
MIT. See `LICENSE`.
