# Shell Environment Inheritance in Hermes

Why some CLI tools' login state isn't available in Hermes terminal sessions, and how to work around it.

## Root Cause

Hermes runs shell commands in **non-interactive, non-login subprocesses**. This means:

- `.zshrc` / `.bashrc` / `.bash_profile` / `.profile` are **NOT** loaded
- Shell plugins (nvm, direnv, rbenv, pyenv, conda init) are **NOT** initialized
- Shell aliases and functions are **NOT** available
- Environment variables set in shell config files are **NOT** present

What IS inherited:
- Environment variables exported in `~/.hermes/.env`
- Environment variables from the parent shell at the time Hermes was started
- Filesystem-based credentials (`~/.config/gh/`, `~/.aws/`, `~/.codex/config.toml`, `~/.npmrc`, `~/.netrc`)

## Diagnosis

When a tool doesn't work, check which auth mechanism it uses:

```bash
which <tool>              # Is it on the default PATH?
<tool> --version          # Is it installed?
<tool> login status       # Check auth status
echo $SOME_VAR            # Check if env var is set
cat ~/.config/<tool>/     # Check file-based credentials
```

## Auth Mechanism Cheat Sheet

| Tool | Auth Storage | Works in Hermes? | Why |
|------|-------------|-----------------|-----|
| `gh` | `~/.config/gh/hosts.yml` | ✅ | File-based |
| `aws` | `~/.aws/credentials` | ✅ | File-based |
| `gcloud` | `~/.config/gcloud/` | ✅ | File-based |
| `npm` | `~/.npmrc` | ✅ | File-based |
| `codex` | `~/.codex/config.toml` + OAuth | ✅ After `codex login` | Config file |
| `nvm` | Shell function in `.zshrc` | ❌ | Must source manually |
| `direnv` | Shell hook | ❌ | Must source `.envrc` manually |
| `rbenv` / `pyenv` | Shell init | ❌ | Must eval init manually |
| `conda activate` | Shell function | ❌ | Use `conda run` instead |
| `source venv/bin/activate` | Shell function | ❌ | Use `./venv/bin/python` directly |

## Workarounds

### nvm — source explicitly

```bash
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"
nvm use lts/krypton
```

### venv — use absolute Python path

```bash
# Instead of:
source .venv/bin/activate && python app.py

# Use:
.venv/bin/python app.py

# Or inline:
source .venv/bin/activate && python app.py
```

### direnv — load the envrc manually

```bash
# Instead of relying on direnv hook:
export $(cat .envrc | xargs)

# Or source the file:
source .envrc
```

### nix — use nix-shell inline

```bash
nix-shell --run "python app.py"
```

### conda — use conda run

```bash
conda run -n myenv python app.py
```

### General pattern for shell-dependent tools

```bash
# Wrap in a single command that sources first:
bash -c 'source ~/.zshrc && your-command-here'
```

But `~/.zshrc` may have interactive-only guards (`[[ $- == *i* ]]`). If so, use a targeted source:

```bash
bash -c 'export NVM_DIR="$HOME/.nvm"; [ -s "$NVM_DIR/nvm.sh" ] && . "$NVM_DIR/nvm.sh"; nvm ls'
```

## PTY Mode

Interactive CLIs (`codex`, `claude-code`, `vim`, `python REPL`) need a pseudo-terminal:

```bash
terminal(command="codex exec 'do something'", pty=true)
```

PTY mode makes the tool think it's running in a real terminal, which helps with:
- ANSI color output
- Interactive prompts
- Progress bars and spinners

But PTY mode still does NOT load shell config files — it's only about terminal device semantics, not login shell initialization.
