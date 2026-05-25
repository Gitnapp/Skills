# nvm Node LTS Migration

How to switch to a new Node LTS and migrate all global npm packages.

## Scenario

Current: Node v22 LTS (Jod)
Target: Node v24 LTS (Krypton)

## Steps

1. **Check current state**

```bash
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"
nvm ls
```

2. **List current global packages** (for reference if migration fails)

```bash
nvm use <current_version>
npm ls -g --depth=0
```

3. **Install new LTS with package reinstall**

```bash
nvm install lts/krypton --reinstall-packages-from=<exact_current_version>
```

⚠️ `--reinstall-packages-from` requires the exact version number (e.g. `22.22.1`), not an alias like `lts/jod`.

4. **Handle failed packages** from the reinstall step

If a package fails (e.g. broken package like `obsi` with `ENOVERSIONS`), npm may abort early and skip most packages. Fix by:

```bash
# Switch back to old version, list globals
nvm use <old_version>
npm ls -g --depth=0 2>/dev/null

# Switch to new version, reinstall manually (skip the broken package)
nvm use lts/krypton
npm install -g <pkg1> <pkg2> <...>
```

5. **Set as default**

```bash
nvm alias default lts/krypton
```

6. **Clean up old version's broken packages**

```bash
nvm use <old_version>
npm uninstall -g <broken_package_name>
nvm use lts/krypton
```

## Pitfalls

- **`nvm` not found in subprocesses** — always source `$NVM_DIR/nvm.sh` first. nvm is a shell function, not a PATH binary.
- **`--reinstall-packages-from` needs exact version** — aliases like `lts/jod` aren't accepted.
- **A single failing package aborts the whole reinstall** — plan to manually reinstall if any package errors out.
- **Packages often upgrade** to newer versions automatically during reinstall — verify expected behavior.
