# Bitwarden CLI for .env Management

Use Bitwarden CLI (`bw`) to store and retrieve .env files as base64-encoded secure notes.

## Setup

```bash
brew install bitwarden-cli
bw login
export BW_SESSION="$(bw unlock --raw)"
bw sync
```

## Store .env as Secure Note

```bash
# Encode .env to base64
ENV_B64=$(base64 -i ~/.hermes/profiles/<profile>/.env)

# Create secure note in Bitwarden
bw create item <<EOF
{
  "organizationId": null,
  "folderId": null,
  "type": 2,
  "name": "hermes-profile-<profile>-env",
  "notes": "$ENV_B64",
  "secureNote": {
    "type": 0
  }
}
EOF
```

## Retrieve .env from Bitwarden

```bash
export BW_SESSION="$(bw unlock --raw)"

# Get base64 content
ENV_B64=$(bw get notes "hermes-profile-<profile>-env" --session "$BW_SESSION")

# Decode and write
echo "$ENV_B64" | base64 -d > ~/.hermes/profiles/<profile>/.env
chmod 600 ~/.hermes/profiles/<profile>/.env
```

## Update .env in Bitwarden

```bash
export BW_SESSION="$(bw unlock --raw)"

# Get item ID
ITEM_ID=$(bw list items --search "hermes-profile-<profile>-env" --session "$BW_SESSION" | jq -r '.[0].id')

# Encode new .env
ENV_B64=$(base64 -i ~/.hermes/profiles/<profile>/.env)

# Update
bw edit item "$ITEM_ID" <<EOF
{
  "notes": "$ENV_B64"
}
EOF

bw sync
```

## Naming Convention

- Item name: `hermes-profile-<profile>-env`
- Examples: `hermes-profile-ctf-env`, `hermes-profile-finance-env`

## Safety Notes

- Treat `BW_SESSION` as a secret — never echo it
- Set `.env` permissions to `600` after decoding
- Sync Bitwarden after updates: `bw sync`
- Consider enabling Hermes secret redaction if fetching secrets into tool output
