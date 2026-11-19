#!/usr/bin/env python3
"""Push rika-customer-app scaffold to GitHub via Git Trees + Commits API.
Handles empty repo (no initial commit) by using the Contents API for the first file."""
import base64, json, os, sys, urllib.request, urllib.error

TOKEN = sys.argv[1]
API = "https://api.github.com"
REPO = "Kip-kip/rika-customer-app"
LOCAL = "/home/ubuntu/rika-customer-app"

def req(method, path, payload=None):
    url = API + path
    data = json.dumps(payload).encode() if payload is not None else None
    r = urllib.request.Request(url, data=data, method=method)
    r.add_header("Authorization", "token " + TOKEN)
    r.add_header("Accept", "application/vnd.github+json")
    r.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(r) as resp:
            return resp.status, json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        return e.code, json.loads(body) if body else {}

# Step 1: create the first file via Contents API (handles empty repo)
with open(os.path.join(LOCAL, "README.md"), "rb") as f:
    content = base64.b64encode(f.read()).decode()
code, d = req("PUT", "/repos/" + REPO + "/contents/README.md",
              {"message": "Initial scaffold: rika-customer-app", "content": content})
print("README.md -> HTTP %d" % code)
if code not in (200, 201):
    print("  detail: %r" % d)
    sys.exit(1)

# Step 2: now push remaining files via Trees/Commits (repo is no longer empty)
files = []
for root, _, names in os.walk(LOCAL):
    for n in sorted(names):
        full = os.path.join(root, n)
        rel = os.path.relpath(full, LOCAL)
        if rel.startswith(".git") or rel == "README.md" or rel == "sync.py":
            continue
        files.append((rel, full))
print("remaining files: %d" % len(files))
for rel, full in files:
    with open(full, "rb") as f:
        b64 = base64.b64encode(f.read()).decode()
    code, d = req("PUT", "/repos/" + REPO + "/contents/" + rel,
                  {"message": "scaffold: " + rel, "content": b64})
    print("  %s -> HTTP %d" % (rel, code))

print("done")
