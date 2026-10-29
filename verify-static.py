"""Verify the allowlisted static export before extraction and after Astro build."""
import hashlib
import json
import pathlib
import re
import sys
import tarfile

root = pathlib.Path(__file__).resolve().parent
manifest = json.loads((root / "demo-manifest.json").read_text(encoding="utf-8"))
assert manifest["publicDemo"] is True
assert manifest["repository"] == "murkavpn/oqvel-demo"
assert manifest["base"] == "/oqvel-demo/"
expected = manifest["files"]
allowed = {".html", ".css", ".js", ".woff2", ".ico", ".png", ".jpg", ".svg", ".webp", ".avif", ".txt", ".xml"}

def audit(name, data):
    file = pathlib.PurePosixPath(name)
    assert not file.is_absolute() and ".." not in file.parts and "\\" not in name, "Unsafe path"
    assert file.suffix in allowed or name == ".nojekyll", "Non-static file: " + name
    assert not any(part in {"functions", "api", "node_modules", ".git"} for part in file.parts)
    assert hashlib.sha256(data).hexdigest() == expected[name], "Hash mismatch: " + name
    if file.suffix in {".html", ".css", ".js", ".svg", ".txt", ".xml"}:
        text = data.decode("utf-8")
        patterns = [r"-----BEGIN .*PRIVATE KEY", r"\bgh[pousr]_[A-Za-z0-9]{36,}",
                    r"github_pat_[A-Za-z0-9_]{60,}", r"\b\d{8,12}:[A-Za-z0-9_-]{35}\b",
                    r"/api/", r"(?i)platega|workers\.dev|murkavpn\.pages\.dev", r"(?i)<form\b"]
        assert not any(re.search(pattern, text) for pattern in patterns), "Unsafe content: " + name
        if file.suffix == ".html":
            assert "connect-src 'none'" in text and "form-action 'none'" in text, "Demo CSP missing"

mode = sys.argv[1]
seen = set()
if mode == "--extract":
    archive = root / "demo-static.tar.gz"
    assert hashlib.sha256(archive.read_bytes()).hexdigest() == manifest["archiveSha256"]
    destination = root / "public"
    assert not destination.exists(), "Extraction destination must be empty"
    with tarfile.open(archive, "r:gz") as bundle:
        for member in bundle:
            if member.isdir():
                continue
            assert member.isfile() and member.size < 16 * 1024 * 1024, "Unsafe archive member"
            name = str(pathlib.PurePosixPath(member.name))
            assert name not in seen and name in expected, "Unexpected archive file"
            data = bundle.extractfile(member).read()
            audit(name, data)
            seen.add(name)
            file = destination / name
            file.parent.mkdir(parents=True, exist_ok=True)
            file.write_bytes(data)
else:
    assert mode == "--built"
    for file in (root / "dist").rglob("*"):
        if file.is_file():
            name = file.relative_to(root / "dist").as_posix()
            assert name in expected, "Unexpected build output"
            audit(name, file.read_bytes())
            seen.add(name)
assert seen == set(expected), "Incomplete static export"
print(f"PUBLIC_DEMO audit passed: {len(seen)} files, exact SHA-256 match, no backend/forms/API/credentials.")
