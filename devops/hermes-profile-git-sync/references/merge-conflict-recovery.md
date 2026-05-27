# Merge Conflict Recovery for Profile Configs

When `git pull --rebase=merges -X theirs` leaves `<<<<<<<`/`=======`/`>>>>>>>`
markers in config.yaml, the file becomes invalid YAML. Hermes will fail to load it.

## Detection

```bash
grep -rn "<<<<<<" ~/.hermes/profiles/*/config.yaml
```

## Resolution Script

```python
import re

PROFILES = ['ctf', 'finance', 'ppt', 'researcher']

for profile in PROFILES:
    path = f'/Users/admin/.hermes/profiles/{profile}/config.yaml'
    with open(path) as f:
        raw = f.read()

    # Resolve all conflict blocks, keeping "ours" (stashed/local changes)
    raw = re.sub(
        r'<<<<<<<[ \w]+\n(.*?)\n=======\n(.*?)\n>>>>>>>[ \w]+\n',
        lambda m: m.group(2),
        raw,
        flags=re.DOTALL
    )

    # Clean up stray markers
    raw = raw.replace('<<<<<<< Updated upstream', '')
    raw = raw.replace('=======', '')
    raw = raw.replace('>>>>>>> Stashed changes', '')

    # Remove duplicate blank lines
    raw = re.sub(r'\n{3,}', '\n\n', raw)

    with open(path, 'w') as f:
        f.write(raw)
```

After stripping markers, the YAML may still be malformed (e.g., two
`providers:` blocks merged together, or indentation broken). Fix by
replacing the entire providers section with a clean block:

```python
# Replace from "providers:\n" to "\nfallback_providers:"
YUNWU_PROVIDER = """  yunwu: ... """  # clean provider block
raw = re.sub(
    r'(providers:\n).*?(\nfallback_providers:)',
    r'\1' + YUNWU_PROVIDER + r'\n\2',
    raw,
    flags=re.DOTALL
)
```

## Recovery Checklist

1. `grep` all profiles for conflict markers
2. Run the resolution script above
3. Rebuild any malformed YAML blocks (typically the providers section)
4. `grep` again to confirm all markers gone
5. Commit and push: `cd ~/.hermes/profiles/<name> && git add config.yaml && git commit -m "fix: resolve merge conflicts" && git push origin main`
