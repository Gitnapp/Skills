# .env Symlink Loop Recovery

## Problem

After a profile sync, all API keys stop working. Error messages show "invalid token" or authentication failures across all providers.

## Root Cause

`.env` was committed to git as a symlink. During sync, the symlink got corrupted into a self-referencing loop:

```
~/.hermes/.env → ~/.hermes/profiles/hermes-default/.env
~/.hermes/profiles/hermes-default/.env → ~/.hermes/profiles/hermes-default/.env  (points to itself!)
```

Both files are only ~49 bytes (just the symlink path). The original .env content (1120+ bytes with 8+ API keys) is lost from the live filesystem.

## Detection

```bash
# Check if .env is a symlink loop (will hang or error)
cat ~/.hermes/.env

# Use lstat to avoid following symlinks
python3 -c "
import os
p = os.path.expanduser('~/.hermes/profiles/hermes-default/.env')
print('is symlink:', os.path.islink(p))
if os.path.islink(p):
    print('target:', os.readlink(p))
"
```

If the target is the same path as the file itself, it's a self-referencing loop.

## Recovery

### Step 1: Delete broken symlinks

```bash
rm -f ~/.hermes/.env ~/.hermes/profiles/hermes-default/.env
```

### Step 2: Find latest snapshot

```bash
ls -t ~/.hermes/profiles/hermes-default/state-snapshots/
```

### Step 3: Restore from snapshot

```bash
SNAP=$(ls -t ~/.hermes/profiles/hermes-default/state-snapshots/ | head -1)
cp ~/.hermes/profiles/hermes-default/state-snapshots/$SNAP/.env ~/.hermes/profiles/hermes-default/.env
chmod 600 ~/.hermes/profiles/hermes-default/.env
```

### Step 4: Recreate main symlink

```bash
ln -s ~/.hermes/profiles/hermes-default/.env ~/.hermes/.env
```

### Step 5: Verify

```bash
# Should be 1000+ bytes, not 49
wc -c ~/.hermes/profiles/hermes-default/.env

# Count API keys
grep -c "API_KEY" ~/.hermes/profiles/hermes-default/.env

# Test a key
KEY=$(grep "YUNWU_API_KEY" ~/.hermes/profiles/hermes-default/.env | cut -d= -f2)
curl -s https://yunwu.ai/v1/models -H "Authorization: Bearer $KEY" | head -c 100
```

## Prevention

1. `.env` MUST be in `.gitignore` for all profile repos
2. Never `git add .env` — it's excluded by .gitignore
3. The sync scripts do `git add -A` which respects .gitignore
4. If .env was previously committed, remove it: `git rm --cached .env && git commit -m "chore: remove .env from git"`
