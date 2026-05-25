---
name: node-version-management
description: "Install, switch, and migrate between Node.js versions via nvm on macOS"
version: 1.0.0
author: Hermes
tags: [node, nvm, npm, migration, macOS, version-management]
---

# Node.js Version Management (nvm)

Manage Node.js versions using nvm on macOS. nvm is not on the default PATH — must be sourced before use.

## Required Setup

```bash
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"
```

Always source nvm before any nvm command. The shell's `.zshrc` / `.bashrc` may not be loaded in Hermes terminal sessions.

## Common Operations

### List installed versions

```bash
nvm ls
```

### List available LTS versions

```bash
nvm ls-remote --lts
```

**Important:** `nvm ls-remote` returns N/A for installed-but-not-active versions unless you've already sourced nvm.

### Install a new LTS version

```bash
nvm install lts/krypton    # Node 24 LTS
nvm install lts/jod        # Node 22 LTS
```

### Switch between versions

```bash
nvm use lts/krypton        # Use Node 24 LTS
nvm use 22.22.1            # Use exact version
```

### Set default version

```bash
nvm alias default lts/krypton
```

This persists across shell sessions.

## 📦 Migrating Global npm Packages

### Preferred method: reinstall-packages-from

```bash
nvm install <new-version> --reinstall-packages-from=<exact-old-version>
```

**⚠️ PITFALLS**

1. **Use exact version, not alias.** `--reinstall-packages-from=lts/jod` fails with "must point to an installed version". Always use the full semver (e.g. `22.22.1`). Find the exact version with `nvm ls` beforehand.

2. **Broken packages abort the migration silently.** `--reinstall-packages-from` calls `npm install -g` internally. If any global package on the old version has no available version (e.g. a locally-built or abandoned package like `obsi`), the npm install fails, and **the entire migration stalls mid-way** but nvm itself still returns exit code 0. You won't know packages were lost unless you verify.

3. **Always verify after migration.** Run this on the new version:
   ```bash
   npm ls -g --depth=0
   ```
   Then switch to the old version and compare:
   ```bash
   nvm use <old-version>
   npm ls -g --depth=0
   ```

### Fallback: manual migration

If `--reinstall-packages-from` fails (broken package, network error, etc.):

1. Switch to old version, list packages:
   ```bash
   nvm use <old-version>
   npm ls -g --depth=0 2>/dev/null
   ```

2. Note all packages (skip `npm` and `corepack` — they ship with Node):
   ```
   @fission-ai/openspec
   @openai/codex
   eas-cli
   openclaw
   pnpm
   typescript-language-server
   typescript
   vercel
   ```

3. Switch to new version, install them all at once:
   ```bash
   nvm use <new-version>
   npm install -g @fission-ai/openspec @openai/codex eas-cli openclaw pnpm typescript-language-server typescript vercel
   ```

4. Verify again:
   ```bash
   npm ls -g --depth=0 2>/dev/null
   ```

### Post-migration cleanup

After confirming all packages migrated successfully on the new version:

1. Remove broken packages from the old version (they're dead weight):
   ```bash
   nvm use <old-version>
   npm uninstall -g <broken-package-name>
   ```

2. Set the new version as default:
   ```bash
   nvm alias default lts/krypton
   ```
