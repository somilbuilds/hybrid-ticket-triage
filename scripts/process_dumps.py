"""
All-in-one script: inventory, validate, move, and report synthetic KB articles.
Run from repo root: python scripts/process_dumps.py
Add --dry-run to preview without moving files.
"""

import os
import sys
import re
import glob
import json
import shutil
import zipfile
import yaml

DRY_RUN = "--dry-run" in sys.argv

REPO_ROOT = os.getcwd()
DATA_DIR = os.path.join(REPO_ROOT, "data", "hackerrank")

ALLOWED_PRODUCT_AREAS = {
    "screen", "integrations", "settings", "library",
    "interviews", "hackerrank_community", "skillup", "general-help"
}

REQUIRED_FM_KEYS = {
    "title", "title_slug", "source_url", "article_slug",
    "last_updated_exact", "last_updated_relative", "breadcrumbs"
}

# ──────────────────────────────────────────────
# 1. Collect existing article IDs
# ──────────────────────────────────────────────
existing_ids = set()
existing_file_count = 0
for root, dirs, files in os.walk(DATA_DIR):
    for f in files:
        if f == "index.md":
            continue
        existing_file_count += 1
        m = re.match(r"^(\d+)-", f)
        if m:
            existing_ids.add(m.group(1))

print(f"[INFO] Existing articles under data/hackerrank/: {existing_file_count}")
print(f"[INFO] Existing numeric article IDs: {len(existing_ids)}")

# ──────────────────────────────────────────────
# 2. Find zip files at repo root
# ──────────────────────────────────────────────
zip_files = sorted(glob.glob(os.path.join(REPO_ROOT, "*.zip")))
print(f"[INFO] ZIP files found at root: {len(zip_files)}")
for z in zip_files:
    print(f"       - {os.path.basename(z)}")

# Also check for loose .md files at root (not known project files)
KNOWN_ROOT_MD = {"README.md", "PROJECT_PLAN.md", "AGENT_HANDOFF.md"}
loose_md = [f for f in glob.glob(os.path.join(REPO_ROOT, "*.md"))
            if os.path.basename(f) not in KNOWN_ROOT_MD]
if loose_md:
    print(f"[INFO] Loose .md files at root: {[os.path.basename(f) for f in loose_md]}")
else:
    print("[INFO] No loose .md files at root.")

# ──────────────────────────────────────────────
# 3. Validate each file inside each zip
# ──────────────────────────────────────────────
valid_files = []     # (zip_path, member_filename, dest_path, product_area, content_bytes)
failed_files = []    # (source_description, reason)
seen_ids_in_batch = set()

for zip_path in zip_files:
    zip_name = os.path.basename(zip_path)
    with zipfile.ZipFile(zip_path, "r") as zf:
        for member in zf.infolist():
            if member.is_dir() or not member.filename.endswith(".md"):
                continue

            tag = f"{zip_name} -> {os.path.basename(member.filename)}"
            raw = zf.read(member.filename)
            try:
                content = raw.decode("utf-8")
            except UnicodeDecodeError:
                failed_files.append((tag, "Not valid UTF-8"))
                continue

            # ── Parse frontmatter ──
            fm_match = re.match(r"^---\s*\n(.*?)\n---\s*\n(.*)$", content, re.DOTALL)
            if not fm_match:
                failed_files.append((tag, "Missing/malformed YAML frontmatter"))
                continue

            fm_text, body = fm_match.group(1), fm_match.group(2)
            try:
                fm = yaml.safe_load(fm_text)
            except Exception as e:
                failed_files.append((tag, f"YAML parse error: {e}"))
                continue

            if not isinstance(fm, dict):
                failed_files.append((tag, "Frontmatter is not a dict"))
                continue

            # ── Check required keys ──
            missing = REQUIRED_FM_KEYS - set(fm.keys())
            if missing:
                failed_files.append((tag, f"Missing keys: {sorted(missing)}"))
                continue

            # ── Extract article_id from filename ──
            basename = os.path.basename(member.filename)
            id_match = re.match(r"^(\d{10})-", basename)
            if not id_match:
                failed_files.append((tag, "Filename doesn't start with 10-digit ID"))
                continue
            article_id = id_match.group(1)

            # ── Check word count ──
            word_count = len(body.split())
            if word_count < 50:
                failed_files.append((tag, f"Word count ({word_count}) is less than 50"))
                continue

            # ── ID must match source_url and article_slug ──
            source_url = str(fm.get("source_url", ""))
            article_slug = str(fm.get("article_slug", ""))

            url_id = None
            url_m = re.search(r"/(\d+)-", source_url)
            if url_m:
                url_id = url_m.group(1)

            slug_id = None
            slug_m = re.match(r"^(\d+)-", article_slug)
            if slug_m:
                slug_id = slug_m.group(1)

            if url_id != article_id:
                failed_files.append((tag, f"Filename ID ({article_id}) != source_url ID ({url_id})"))
                continue
            if slug_id != article_id:
                failed_files.append((tag, f"Filename ID ({article_id}) != article_slug ID ({slug_id})"))
                continue

            # ── Title must match first # heading ──
            h1 = re.search(r"^#\s+(.+)$", body, re.MULTILINE)
            if not h1:
                failed_files.append((tag, "No '# ' heading in body"))
                continue
            if fm["title"].strip() != h1.group(1).strip():
                failed_files.append((tag, f"Title mismatch: FM='{fm['title'].strip()}' H1='{h1.group(1).strip()}'"))
                continue

            # ── No duplicate IDs in existing corpus ──
            if article_id in existing_ids:
                failed_files.append((tag, f"ID {article_id} already in corpus"))
                continue
            if article_id in seen_ids_in_batch:
                failed_files.append((tag, f"ID {article_id} duplicate in batch"))
                continue
            seen_ids_in_batch.add(article_id)

            # ── No stray ## headings ──
            if re.search(r"^##\s", body, re.MULTILINE):
                failed_files.append((tag, "Contains ## heading (repo uses # only)"))
                continue

            # ── Determine destination from zip path structure ──
            parts = member.filename.replace("\\", "/").split("/")
            product_area = subcategory = None

            if "hackerrank" in parts:
                idx = parts.index("hackerrank")
                if len(parts) >= idx + 4:
                    product_area = parts[idx + 1]
                    subcategory = parts[idx + 2]

            if product_area and product_area not in ALLOWED_PRODUCT_AREAS:
                failed_files.append((tag, f"Product area '{product_area}' not in allowed list"))
                continue

            if not product_area:
                # Try to infer from breadcrumbs
                bcs = fm.get("breadcrumbs", [])
                if isinstance(bcs, str):
                    bcs = [b.strip() for b in bcs.split(">")]

                # Map breadcrumb names to product_area slugs
                BC_MAP = {
                    "screening": "screen", "screen": "screen",
                    "integrations": "integrations", "integration": "integrations",
                    "settings": "settings", "account settings": "settings",
                    "library": "library", "question library": "library",
                    "interviews": "interviews", "interview": "interviews",
                    "hackerrank community": "hackerrank_community", "community": "hackerrank_community",
                    "skillup": "skillup", "skill-up": "skillup",
                    "general help": "general-help", "general": "general-help",
                }
                for bc in bcs:
                    key = bc.lower().strip()
                    if key in BC_MAP:
                        product_area = BC_MAP[key]
                        break

                if not product_area:
                    failed_files.append((tag, f"Cannot map breadcrumbs {bcs} to product_area"))
                    continue

                # Use second breadcrumb as subcategory slug
                if len(bcs) >= 2:
                    subcategory = re.sub(r"[^a-z0-9]+", "-", bcs[1].lower().strip()).strip("-")
                else:
                    subcategory = "general"

            dest = os.path.join(DATA_DIR, product_area, subcategory, basename)
            valid_files.append((zip_path, member.filename, dest, product_area, raw))

# ──────────────────────────────────────────────
# 4. Report validation results
# ──────────────────────────────────────────────
print(f"\n{'='*60}")
print(f"VALIDATION RESULTS")
print(f"{'='*60}")
print(f"  Valid files ready to move : {len(valid_files)}")
print(f"  Failed files (left at root): {len(failed_files)}")

# Breakdown by product_area
from collections import Counter
area_counts = Counter(v[3] for v in valid_files)
print(f"\n  Breakdown by product_area:")
for area in sorted(area_counts):
    print(f"    {area:25s} : {area_counts[area]}")

if failed_files:
    print(f"\n  FAILED FILES:")
    for tag, reason in failed_files:
        print(f"    ✗ {tag}")
        print(f"      Reason: {reason}")

# ──────────────────────────────────────────────
# 5. Move files (unless --dry-run)
# ──────────────────────────────────────────────
if DRY_RUN:
    print(f"\n[DRY RUN] Would move {len(valid_files)} files. Exiting.")
    sys.exit(0)

print(f"\n{'='*60}")
print(f"MOVING FILES")
print(f"{'='*60}")

moved_count = 0
for zip_path, member_filename, dest, product_area, raw_bytes in valid_files:
    dest_dir = os.path.dirname(dest)
    os.makedirs(dest_dir, exist_ok=True)
    with open(dest, "wb") as f:
        f.write(raw_bytes)
    moved_count += 1
    print(f"  ✓ {os.path.basename(dest)} → {os.path.relpath(dest, REPO_ROOT)}")

print(f"\n  Total moved: {moved_count}")

# ──────────────────────────────────────────────
# 6. Delete zip files
# ──────────────────────────────────────────────
print(f"\n{'='*60}")
print(f"CLEANUP")
print(f"{'='*60}")

for zip_path in zip_files:
    os.remove(zip_path)
    print(f"  ✓ Deleted {os.path.basename(zip_path)}")

# Clean up temp files at root
for tmp in ["all_zips_detailed.txt", "zips_inventory.txt", "failed_report.txt"]:
    fp = os.path.join(REPO_ROOT, tmp)
    if os.path.exists(fp):
        os.remove(fp)
        print(f"  ✓ Deleted temp file {tmp}")

# ──────────────────────────────────────────────
# 7. Final count
# ──────────────────────────────────────────────
new_total = 0
for root, dirs, files in os.walk(DATA_DIR):
    for f in files:
        if f != "index.md":
            new_total += 1

print(f"\n{'='*60}")
print(f"FINAL SUMMARY")
print(f"{'='*60}")
print(f"  New files placed       : {moved_count}")
print(f"  Files that failed      : {len(failed_files)}")
print(f"  New total docs (excl index.md): {new_total}")

# Breakdown
for area in sorted(area_counts):
    print(f"    {area:25s} : +{area_counts[area]}")
