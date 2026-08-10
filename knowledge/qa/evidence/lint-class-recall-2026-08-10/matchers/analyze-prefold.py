#!/usr/bin/env python3
"""Analyze pre-fold scan data for Q2 (re-finding) and Q4 (candidate TPs)."""

import csv
import sys
from collections import defaultdict

# Read pre-fold data
data = defaultdict(lambda: defaultdict(list))  # slug -> class -> [(idx, count)]

with open('pre-fold-raw.tsv') as f:
    reader = csv.DictReader(f, delimiter='\t')
    for row in reader:
        slug = row['draft_slug']
        cls = row['class']
        idx = int(row['commit_idx'])
        count = int(row['matches_count'])
        data[slug][cls].append((idx, count))

# Sort by commit index
for slug in data:
    for cls in data[slug]:
        data[slug][cls].sort()

print("=" * 80)
print("Q4 — PRE-FOLD STATE MATCHES (candidate true positives)")
print("=" * 80)
print()
print("A 'candidate TP' = class fires at some commit N but NOT at the final commit")
print("(fire disappeared, possibly folded out)")
print()

for cls in ['m', 'q', 'r', 's']:
    print(f"\n--- Class {cls} ---")
    print(f"{'Draft slug':<45} {'First':>5} {'Last':>5} {'Max':>4} {'Cand':>4}")
    total_candidates = 0
    for slug in sorted(data.keys()):
        series = data[slug][cls]
        if not series:
            continue
        first_count = series[0][1]
        last_count = series[-1][1]
        max_count = max(c for _, c in series)
        # Candidate TP: fired at some point but last commit has fewer matches
        # (indicating some were folded out)
        candidate = max_count > last_count
        cand_delta = max_count - last_count if candidate else 0
        total_candidates += cand_delta
        marker = f"+{cand_delta}" if cand_delta > 0 else "0"
        print(f"{slug:<45} {first_count:>5} {last_count:>5} {max_count:>4} {marker:>4}")
    print(f"{'TOTAL candidates':>45} {'':>5} {'':>5} {'':>4} {total_candidates:>4}")

print()
print("=" * 80)
print("Q2 — RE-FINDING RATE (lower bound)")
print("=" * 80)
print()
print("A 're-find' = present at N, absent at N+1, present again at N+2+")
print("Uses count > 0 as 'present', count == 0 as 'absent'")
print()

for cls in ['m', 'q', 'r', 's']:
    print(f"\n--- Class {cls} ---")
    total_refinds = 0
    for slug in sorted(data.keys()):
        series = data[slug][cls]
        if not series:
            continue
        # Build presence vector
        presence = [c > 0 for _, c in series]
        refinds = 0
        for i in range(len(presence) - 2):
            if presence[i] and not presence[i+1]:
                # Absent at i+1; check if present again at i+2+
                for j in range(i+2, len(presence)):
                    if presence[j]:
                        refinds += 1
                        break
        if refinds > 0:
            total_refinds += refinds
            print(f"  {slug}: {refinds} re-find(s)")
            # Show the count series
            counts = [c for _, c in series]
            print(f"    counts: {counts}")
    if total_refinds == 0:
        print(f"  No re-finds detected")
    print(f"  Total re-finds (class {cls}): {total_refinds}")

print()
print("=" * 80)
print("PER-DRAFT SUMMARY — count trajectories")
print("=" * 80)
print()

for slug in sorted(data.keys()):
    print(f"\n--- {slug} ---")
    for cls in ['m', 'q', 'r', 's']:
        series = data[slug][cls]
        if not series:
            continue
        counts = [c for _, c in series]
        if any(c > 0 for c in counts):
            print(f"  {cls}: {counts}")

print()
print("=" * 80)
print("DISAPPEARANCE DETAIL — classes that fired then stopped")
print("=" * 80)
print()

for cls in ['m', 'q', 'r', 's']:
    for slug in sorted(data.keys()):
        series = data[slug][cls]
        if not series:
            continue
        counts = [c for _, c in series]
        shas = [s[:8] for s, _ in series]
        # Find commits where count decreased
        for i in range(1, len(counts)):
            if counts[i] < counts[i-1]:
                delta = counts[i-1] - counts[i]
                print(f"  {cls} | {slug} | commit {i} ({shas[i]}): {counts[i-1]} -> {counts[i]} (lost {delta})")
