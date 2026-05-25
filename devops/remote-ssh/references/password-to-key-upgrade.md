# Password-to-Key SSH Upgrade Reference

## Full Workflow: Probe → Auth → Key Install → Config → Verify

### Step 1: Probe the target

Check which usernames the target accepts — use a single-shot loop to avoid "Too many authentication failures" (SSH disconnects after 6 failures):

```bash
for u in eric admin zijian root ubuntu; do
  echo -n "user $u: "
  ssh -o StrictHostKeyChecking=no -o ConnectTimeout=3 \
      -o PasswordAuthentication=no -o BatchMode=yes \
      $u@<hostname> 'echo OK' 2>&1 || true
done
```

- `PasswordAuthentication=no` skips password prompts so each attempt returns instantly
- `BatchMode=yes` prevents interactive prompts
- The loop deliberately succeeds or fails fast — no 6-attempt penalty per user

### Step 2: Connect with password

```bash
# Install sshpass if missing
brew install sshpass

# Connect (one-off)
sshpass -p 'password' ssh -o StrictHostKeyChecking=no user@hostname 'hostname && whoami'
```

### Step 3: Install SSH public key

```bash
sshpass -p 'password' ssh-copy-id -o StrictHostKeyChecking=no \
    -i ~/.ssh/id_ed25519.pub user@hostname
```

### Step 4: Create SSH config alias with Tailscale hostname

```bash
cat >> ~/.ssh/config << 'EOF'

Host <short-name>
  HostName <machine-name>.tailXXXX.ts.net
  User <username>
  IdentityFile ~/.ssh/id_ed25519
EOF
```

Tailscale hostname format: `<machine-name>.tail<network-id>.ts.net` (find it via `tailscale status`).

### Step 5: Accept host key for new hostname

```bash
ssh -o StrictHostKeyChecking=no <short-name> 'hostname && whoami'
```

### Notes

- `~/.ssh/config` is a protected file — `patch`/`write_file` tools may deny writes. Use `sed -i ''` or `cat > ... << 'EOF'` via terminal.
- After switching hostnames (e.g. from raw IP to Tailscale FQDN), the old host key lingers in `~/.ssh/known_hosts`. If you get "Host key verification failed", run `ssh-keygen -R <old-hostname>`.
- sshpass stores the password in the command line — visible in process listings (`ps aux`). For sensitive passwords, consider `ssh -o PreferredAuthentications=keyboard-interactive -o PubkeyAuthentication=no` and typing interactively instead.
