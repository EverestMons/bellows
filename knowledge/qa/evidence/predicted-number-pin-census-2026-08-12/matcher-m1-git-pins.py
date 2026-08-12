#!/usr/bin/env python3
"""M1 — git-object pin matcher.

Extracts MAXIMAL 40-hex runs from plan text and attempts resolution
via `git cat-file -e` against the scanned plan's own Project repo,
the root repo, and the other corpus repo.

A token is a MAXIMAL hex run: a 40-hex run inside a longer hex run
is NOT an M1 match. Runs of other lengths >= 12 are counted and
reported but matched by neither M1 nor M2.
"""

import os
import re
import subprocess
import sys
from pathlib import Path

HEX_RUN_RE = re.compile(r'\b([0-9a-fA-F]{12,})\b')

BELLOWS_REPO = os.environ.get(
    'BELLOWS_REPO',
    '/Users/marklehn/Developer/GitHub/bellows'
)
ROOT_REPO = os.environ.get(
    'ROOT_REPO',
    '/Users/marklehn/Developer/GitHub'
)
LESSONSFORGE_REPO = os.environ.get(
    'LESSONSFORGE_REPO',
    '/Users/marklehn/Developer/GitHub/lessons-forge'
)

PROJECT_HEADER_RE = re.compile(r'^\*\*Project:\*\*\s*(.+)', re.MULTILINE)


def detect_project(text):
    m = PROJECT_HEADER_RE.search(text)
    if m:
        val = m.group(1).strip().lower()
        if 'lessons' in val or 'forge' in val:
            return 'lessons-forge'
        if 'bellows' in val:
            return 'bellows'
    return 'unknown'


def repo_for_project(project):
    if project == 'bellows':
        return BELLOWS_REPO
    if project == 'lessons-forge':
        return LESSONSFORGE_REPO
    return None


def other_corpus_repo(project):
    if project == 'bellows':
        return LESSONSFORGE_REPO
    if project == 'lessons-forge':
        return BELLOWS_REPO
    return None


def git_object_exists(repo_path, hex_token):
    try:
        result = subprocess.run(
            ['git', '-C', repo_path, 'cat-file', '-e', hex_token],
            capture_output=True, timeout=5
        )
        return result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False


def git_object_exists_in_history(repo_path, hex_token):
    """Check if object exists anywhere in the repo (including reflog/history)."""
    return git_object_exists(repo_path, hex_token)


def classify_fire(hex_token, project, plan_file):
    project_repo = repo_for_project(project)
    other_repo = other_corpus_repo(project)
    repos_to_check = []
    if project_repo:
        repos_to_check.append(('PROJECT', project_repo))
    repos_to_check.append(('ROOT', ROOT_REPO))
    if other_repo:
        repos_to_check.append(('OTHER', other_repo))

    resolved_in = []
    for label, repo in repos_to_check:
        if git_object_exists(repo, hex_token):
            resolved_in.append(label)

    if not resolved_in:
        return 'NEVER-TRUE-SURVIVING', None
    if 'PROJECT' in resolved_in:
        return 'RESOLVES-NOW', 'PROJECT'
    if resolved_in:
        return 'CROSS-REPO', resolved_in[0]
    return 'AMBIGUOUS', None


def scan_file(filepath):
    try:
        text = Path(filepath).read_text(encoding='utf-8', errors='replace')
    except (OSError, IOError):
        return []

    project = detect_project(text)
    results = []
    seen_tokens = set()

    for line_num, line in enumerate(text.splitlines(), 1):
        for m in HEX_RUN_RE.finditer(line):
            token = m.group(1).lower()
            if token in seen_tokens:
                continue
            seen_tokens.add(token)
            length = len(token)

            if length == 40:
                classification, resolved_repo = classify_fire(
                    token, project, filepath
                )
                results.append({
                    'file': filepath,
                    'line': line_num,
                    'token': token,
                    'length': length,
                    'matcher': 'M1',
                    'project': project,
                    'classification': classification,
                    'resolved_repo': resolved_repo,
                    'line_text': line.strip()[:120],
                })
            elif length == 64:
                results.append({
                    'file': filepath,
                    'line': line_num,
                    'token': token,
                    'length': length,
                    'matcher': 'M2-candidate',
                    'project': project,
                    'classification': 'DEFERRED-TO-M2',
                    'resolved_repo': None,
                    'line_text': line.strip()[:120],
                })
            else:
                results.append({
                    'file': filepath,
                    'line': line_num,
                    'token': token,
                    'length': length,
                    'matcher': 'PREFIX-POPULATION',
                    'project': project,
                    'classification': 'NOT-MATCHED',
                    'resolved_repo': None,
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
    print(f"REPOS: bellows={BELLOWS_REPO}, root={ROOT_REPO}, lessons-forge={LESSONSFORGE_REPO}")
    print()

    all_results = []
    for filepath in corpus:
        results = scan_file(filepath)
        all_results.extend(results)

    m1_fires = [r for r in all_results if r['matcher'] == 'M1']
    m2_candidates = [r for r in all_results if r['matcher'] == 'M2-candidate']
    prefix_pop = [r for r in all_results if r['matcher'] == 'PREFIX-POPULATION']

    print(f"=== M1 (40-hex git-object pins) ===")
    print(f"Total fires: {len(m1_fires)}")
    classifications = {}
    for r in m1_fires:
        c = r['classification']
        classifications[c] = classifications.get(c, 0) + 1
    for c, count in sorted(classifications.items()):
        print(f"  {c}: {count}")
    print()

    for r in m1_fires:
        repo_info = f" [{r['resolved_repo']}]" if r['resolved_repo'] else ""
        print(f"  {r['classification']}{repo_info} | {os.path.basename(r['file'])}:{r['line']} | {r['token'][:16]}...")
    print()

    print(f"=== 64-hex tokens (M2 candidates) ===")
    print(f"Total: {len(m2_candidates)}")
    print()

    print(f"=== Prefix population (12–39 or 41–63 hex) ===")
    length_dist = {}
    for r in prefix_pop:
        length_dist[r['length']] = length_dist.get(r['length'], 0) + 1
    print(f"Total: {len(prefix_pop)}")
    for length in sorted(length_dist):
        print(f"  {length}-hex: {length_dist[length]}")


if __name__ == '__main__':
    main()
