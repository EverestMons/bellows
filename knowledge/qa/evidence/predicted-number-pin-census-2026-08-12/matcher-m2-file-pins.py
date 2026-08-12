#!/usr/bin/env python3
"""M2 — sha256 file pin matcher.

Extracts MAXIMAL 64-hex tokens that appear on the same line as — or
the line immediately before or after — a `shasum`/`sha256` invocation
naming a path; recomputes against the named file.

A token is a MAXIMAL hex run: a 64-hex run is one M2 token and never
an M1 match inside it.
"""

import os
import re
import subprocess
import hashlib
import sys
from pathlib import Path

HEX_64_RE = re.compile(r'\b([0-9a-fA-F]{64})\b')
SHASUM_RE = re.compile(
    r'(?:shasum\s+-a\s+256|sha256sum|sha256)\s+(.+?)(?:\s*[|;>&]|$)',
    re.IGNORECASE
)
SHASUM_SIMPLE_RE = re.compile(
    r'(?:shasum|sha256)',
    re.IGNORECASE
)

BELLOWS_REPO = os.environ.get(
    'BELLOWS_REPO',
    '/Users/marklehn/Developer/GitHub/bellows'
)
LESSONSFORGE_REPO = os.environ.get(
    'LESSONSFORGE_REPO',
    '/Users/marklehn/Developer/GitHub/lessons-forge'
)


def extract_path_from_shasum_line(line):
    m = SHASUM_RE.search(line)
    if m:
        path_str = m.group(1).strip()
        path_str = path_str.strip("'\"`")
        path_str = path_str.rstrip('`).;,')
        path_str = path_str.split()[0] if path_str else ''
        path_str = path_str.strip("'\"`")
        if path_str and '/' in path_str:
            return path_str
    return None


def compute_sha256(filepath):
    try:
        h = hashlib.sha256()
        with open(filepath, 'rb') as f:
            for chunk in iter(lambda: f.read(8192), b''):
                h.update(chunk)
        return h.hexdigest()
    except (OSError, IOError):
        return None


def file_ever_had_sha256(filepath, target_sha):
    """Check if any committed revision of the file matches the sha256."""
    try:
        repo_dir = None
        test_path = filepath
        while test_path != '/':
            if os.path.isdir(os.path.join(test_path, '.git')):
                repo_dir = test_path
                break
            test_path = os.path.dirname(test_path)
        if not repo_dir:
            return False

        rel_path = os.path.relpath(filepath, repo_dir)
        result = subprocess.run(
            ['git', '-C', repo_dir, 'log', '--all', '--format=%H',
             '--', rel_path],
            capture_output=True, text=True, timeout=10
        )
        if result.returncode != 0:
            return False

        for commit_hash in result.stdout.strip().split('\n'):
            if not commit_hash:
                continue
            blob_result = subprocess.run(
                ['git', '-C', repo_dir, 'show',
                 f'{commit_hash}:{rel_path}'],
                capture_output=True, timeout=10
            )
            if blob_result.returncode == 0:
                actual_sha = hashlib.sha256(blob_result.stdout).hexdigest()
                if actual_sha == target_sha:
                    return True
        return False
    except (subprocess.TimeoutExpired, FileNotFoundError, ValueError):
        return False


def classify_m2_fire(hex_token, named_path):
    if not named_path or not os.path.isabs(named_path):
        candidates = []
        if named_path:
            for base in [BELLOWS_REPO, LESSONSFORGE_REPO,
                        '/Users/marklehn/Developer/GitHub']:
                full = os.path.join(base, named_path)
                if os.path.isfile(full):
                    candidates.append(full)
        if not candidates:
            return 'AMBIGUOUS', named_path

        named_path = candidates[0]

    if not os.path.isfile(named_path):
        if file_ever_had_sha256(named_path, hex_token):
            return 'STALE', named_path
        return 'AMBIGUOUS', named_path

    current_sha = compute_sha256(named_path)
    if current_sha == hex_token:
        return 'RESOLVES-NOW', named_path
    else:
        if file_ever_had_sha256(named_path, hex_token):
            return 'STALE', named_path
        return 'NEVER-TRUE-SURVIVING', named_path


def scan_file(filepath):
    try:
        text = Path(filepath).read_text(encoding='utf-8', errors='replace')
    except (OSError, IOError):
        return []

    lines = text.splitlines()
    results = []
    seen_tokens = set()

    for line_num, line in enumerate(lines):
        for m in HEX_64_RE.finditer(line):
            token = m.group(1).lower()
            if token in seen_tokens:
                continue
            seen_tokens.add(token)

            context_lines = []
            for offset in [-1, 0, 1]:
                idx = line_num + offset
                if 0 <= idx < len(lines):
                    context_lines.append(lines[idx])

            named_path = None
            has_shasum_context = False
            for ctx_line in context_lines:
                if SHASUM_SIMPLE_RE.search(ctx_line):
                    has_shasum_context = True
                    p = extract_path_from_shasum_line(ctx_line)
                    if p:
                        named_path = p
                        break

            if not has_shasum_context:
                continue

            if named_path:
                classification, resolved_path = classify_m2_fire(
                    token, named_path
                )
            else:
                classification = 'AMBIGUOUS'
                resolved_path = None

            results.append({
                'file': filepath,
                'line': line_num + 1,
                'token': token,
                'matcher': 'M2',
                'classification': classification,
                'named_path': named_path,
                'resolved_path': resolved_path,
                'line_text': line.strip()[:120],
            })

    return results


def collect_corpus():
    files = []
    for dirpath in [
        os.path.join(BELLOWS_REPO, 'knowledge', 'decisions'),
        os.path.join(BELLOWS_REPO, 'knowledge', 'decisions', 'Done'),
        os.path.join(LESSONSFORGE_REPO, 'knowledge', 'decisions'),
        os.path.join(LESSONSFORGE_REPO, 'knowledge', 'decisions', 'Done'),
    ]:
        if not os.path.isdir(dirpath):
            continue
        for f in os.listdir(dirpath):
            full = os.path.join(dirpath, f)
            if f.endswith('.md') and os.path.isfile(full):
                files.append(full)
    return sorted(files)


def main():
    corpus = collect_corpus()
    print(f"CORPUS: {len(corpus)} files")
    print(f"BOUNDARY: .md files directly in knowledge/decisions/ and knowledge/decisions/Done/ of bellows and lessons-forge")
    print()

    all_results = []
    for filepath in corpus:
        results = scan_file(filepath)
        all_results.extend(results)

    print(f"=== M2 (64-hex sha256 file pins) ===")
    print(f"Total fires: {len(all_results)}")
    classifications = {}
    for r in all_results:
        c = r['classification']
        classifications[c] = classifications.get(c, 0) + 1
    for c, count in sorted(classifications.items()):
        print(f"  {c}: {count}")
    print()

    for r in all_results:
        path_info = f" -> {r.get('resolved_path', r.get('named_path', '?'))}"
        print(f"  {r['classification']}{path_info} | {os.path.basename(r['file'])}:{r['line']} | {r['token'][:16]}...")


if __name__ == '__main__':
    main()
