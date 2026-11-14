# How to build a new lab

## 1. Copy the template

```bash
cp -r templates/new-lab/ <lab-name>/
cd <lab-name>/
```

Use the CVE ID or a short slug as the directory name: `cve-2026-123158`, `ssrf-dns-rebind`, `xxe-oob`.

## 2. Edit in this order

| File | What to change |
|------|----------------|
| `README.md` | title, one-line description, accounts table, build time estimate |
| `lab/Dockerfile` | base image, packages, what to build or install |
| `lab/setup.sh` | user accounts, flag placement, any build assertions |
| `lab/sshd_config` | only if the lab does not use SSH at all |
| `docker-compose.yml` | port mapping, capabilities, any extra services |
| `test.sh` | accounts to test, what to assert, cleanup |
| `docs/01-introduction.md` | what the bug is and why it matters |
| `docs/02-background.md` | concepts the student needs before starting |
| `docs/03-finding-the-bug.md` | verification steps inside the container |
| `docs/04-exploitation.md` | building and running the exploit |
| `docs/05-defense.md` | how to detect and fix it |
| `solutions/walkthrough.md` | full solution with every command and output |

## 3. Test locally before pushing

```bash
cd <lab-name>/
docker compose up --build -d
bash test.sh
docker compose down
```

All three assertions must pass:
- bypass lands on account 1
- bypass lands on account 2 (or whatever the lab has)
- short / normal input is correctly rejected

## 4. Add the lab to the top-level README

```bash
cd ../
# add a row to the table in README.md
```

## 5. Commit

```bash
git add <lab-name>/ README.md
git commit -m "Add <lab-name> lab"
git push origin master
```

CI discovers the new `test.sh` automatically and runs it on every push.

## Writing the docs

Read `~/Documents/THM/tracks/voice.md` before writing any prose. The short version:

- Say why before how. One sentence explaining what a command does, then the command, then the exact output.
- No "let's explore", no "it's worth noting", no em dashes.
- Show output exactly as it appears. Never truncate with `...`.
- Short paragraphs. Active voice. "You", not "the user".
