#!/usr/bin/env python3
import argparse
import hashlib
import json
import re
import subprocess
import sys
import zipfile
from pathlib import Path

FINAL_STATUS = "XIAOJIAO_BUSINESS_MODEL_DRIVEN_PREVIEW_PAGE_UPGRADE_PASS"
MARKER = "ALL_1012D_BUSINESS_MODEL_DRIVEN_PREVIEW_PAGE_UPGRADE_CHECKS_OK"
PACKAGE = "docs/audit_packages/xiaojiao_business_model_driven_preview_page_upgrade_1012D.zip"
MANIFEST = "docs/audit_packages/xiaojiao_business_model_driven_preview_page_upgrade_1012D_manifest.json"

EXPECTED_FILES = [
    "frontend/xiaojiao-preview.html",
    "docs/foundation/xiaojiao_business_model_driven_preview_page_upgrade_1012D.md",
    "docs/foundation/xiaojiao_business_model_driven_preview_page_upgrade_1012D.json",
    "samples/xiaojiao_business_model_driven_preview_page_upgrade_1012D/business_surface_trace_1012D.json",
    "samples/xiaojiao_business_model_driven_preview_page_upgrade_1012D/home_light_entry_trace_1012D.json",
    "samples/xiaojiao_business_model_driven_preview_page_upgrade_1012D/single_lesson_focus_trace_1012D.json",
    "samples/xiaojiao_business_model_driven_preview_page_upgrade_1012D/material_folder_trace_1012D.json",
    "samples/xiaojiao_business_model_driven_preview_page_upgrade_1012D/candidate_review_trace_1012D.json",
    "samples/xiaojiao_business_model_driven_preview_page_upgrade_1012D/legacy_entry_trace_1012D.json",
    "samples/xiaojiao_business_model_driven_preview_page_upgrade_1012D/business_object_state_snapshot_1012D.json",
    "scripts/validate_xiaojiao_business_model_driven_preview_page_upgrade_1012D.py",
    "docs/audit/xiaojiao_business_model_driven_preview_page_upgrade_1012D_result.json",
    "docs/audit/xiaojiao_business_model_driven_preview_page_upgrade_1012D_report.md",
    MANIFEST,
]

REQUIRED_TEXT = [
    "home_light_entry",
    "single_lesson_focus",
    "material_folder",
    "candidate_review_surface",
    "legacy_deep_task_entry",
    "lesson_design visible",
    "lesson_section visible",
    "handout visible",
    "rubric stub visible",
    "resource_reference stub visible",
    "evidence_note visible",
    "teacher_review_gate visible",
    "material_folder_enabled=true",
    "business_progress_enabled=true",
    "review_queue_enabled=true",
    "legacy_agent_as_default=false",
    "old_strong_agent_page_preserved=true",
    "preview_route_only=true",
    "default_route_changed=false",
    "teacher_review_required=true",
    "formal_apply_performed=false",
    "real_database_written=false",
    "memory_written=false",
    "Feishu_written=false",
    "batch_generation_allowed=false",
    "background_generation_allowed=false",
    "new_live_provider_call=false",
    FINAL_STATUS,
    MARKER,
]


def rel(path: Path, root: Path) -> str:
    return path.relative_to(root).as_posix()


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def check_js_syntax(root: Path, html_text: str) -> tuple[bool, str]:
    scripts = "\n".join(re.findall(r"<script[^>]*>([\s\S]*?)</script>", html_text, flags=re.I))
    probe = "new Function(process.env.XIAOJIAO_SCRIPT_TEXT); console.log('JS_SYNTAX_OK');"
    try:
      result = subprocess.run(
          ["node", "-e", probe],
          cwd=root,
          env={**dict(**__import__("os").environ), "XIAOJIAO_SCRIPT_TEXT": scripts},
          text=True,
          capture_output=True,
          timeout=20,
      )
    except FileNotFoundError:
      return False, "node_not_found"
    except subprocess.TimeoutExpired:
      return False, "node_timeout"
    return result.returncode == 0, (result.stdout + result.stderr).strip()


def load_json(path: Path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".", help="repository root")
    args = parser.parse_args()
    root = Path(args.root).resolve()
    checks = []

    def add(name: str, ok: bool, detail=""):
        checks.append({"name": name, "ok": bool(ok), "detail": detail})

    html_path = root / "frontend/xiaojiao-preview.html"
    add("preview_html_exists", html_path.exists(), rel(html_path, root) if html_path.exists() else "missing")
    html = read_text(html_path) if html_path.exists() else ""

    js_ok, js_detail = check_js_syntax(root, html) if html else (False, "no_html")
    add("js_syntax_check", js_ok, js_detail)

    for text in REQUIRED_TEXT:
        add("contains:" + text, text in html, text)

    for rel_path in EXPECTED_FILES:
        add("expected_file:" + rel_path, (root / rel_path).exists(), rel_path)

    for rel_path in EXPECTED_FILES:
        path = root / rel_path
        if path.suffix == ".json" and path.exists():
            try:
                load_json(path)
                add("json_parse:" + rel_path, True, rel_path)
            except Exception as exc:
                add("json_parse:" + rel_path, False, str(exc))

    forbidden_live = [
        "fetch('/api/provider",
        "fetch(\"/api/provider",
        "openai.chat.completions.create",
        "client.responses.create",
        "provider_called: true",
        "model_called: true"
    ]
    add("no_new_live_provider_call", not any(s in html for s in forbidden_live), "provider calls blocked")

    package_files = [root / p for p in EXPECTED_FILES if (root / p).exists()]
    secret_pattern = re.compile(r"(sk-[A-Za-z0-9_-]{20,}|api[_-]?key\s*[:=]\s*['\"][^'\"]+|secret\s*[:=]\s*['\"][^'\"]+|token\s*[:=]\s*['\"][^'\"]+)", re.I)
    secret_hits = []
    absolute_hits = []
    absolute_patterns = [
        re.compile(r"[A-Za-z]:" + r"\\\\"),
        re.compile("/" + "Users" + r"/[^\s'\"]+"),
        re.compile("/" + "mnt" + r"/[^\s'\"]+"),
    ]
    for path in package_files:
        text = read_text(path)
        if secret_pattern.search(text):
            secret_hits.append(rel(path, root))
        if any(pattern.search(text) for pattern in absolute_patterns):
            absolute_hits.append(rel(path, root))
    add("no_api_key_leakage", not secret_hits, ",".join(secret_hits))
    add("no_token_secret_key_files", not any(re.search(r"(token|secret|key)", p.name, re.I) for p in package_files), "package filenames")
    add("no_absolute_paths", not absolute_hits, ",".join(absolute_hits))

    manifest_path = root / MANIFEST
    zip_path = root / PACKAGE
    if manifest_path.exists():
        manifest = load_json(manifest_path)
        manifest_entries = sorted(manifest.get("entries", []))
        add("manifest_final_status", manifest.get("final_status") == FINAL_STATUS, manifest.get("final_status"))
        add("manifest_marker", manifest.get("marker") == MARKER, manifest.get("marker"))
    else:
        manifest = {}
        manifest_entries = []
        add("manifest_exists", False, MANIFEST)

    if zip_path.exists():
        with zipfile.ZipFile(zip_path, "r") as zf:
            zip_entries = sorted(zf.namelist())
        zip_hash = hashlib.sha256(zip_path.read_bytes()).hexdigest()
        add("zip_exists", True, PACKAGE)
        add("no_backslash_zip_entries", not any("\\" in e for e in zip_entries), str(zip_entries))
        add("zip_sha256_matches_manifest", manifest.get("zip_sha256") == zip_hash, zip_hash)
    else:
        zip_entries = []
        add("zip_exists", False, PACKAGE)

    manifest_minus_zip = sorted(set(manifest_entries) - set(zip_entries))
    zip_minus_manifest = sorted(set(zip_entries) - set(manifest_entries))
    add("manifest_minus_zip=[]", manifest_path.exists() and zip_path.exists() and not manifest_minus_zip, json.dumps(manifest_minus_zip, ensure_ascii=False))
    add("zip_minus_manifest=[]", manifest_path.exists() and zip_path.exists() and not zip_minus_manifest, json.dumps(zip_minus_manifest, ensure_ascii=False))

    ok = all(c["ok"] for c in checks)
    result = {
        "stage": "1012D_BUSINESS_MODEL_DRIVEN_PREVIEW_PAGE_UPGRADE",
        "ok": ok,
        "final_status": FINAL_STATUS if ok else "XIAOJIAO_BUSINESS_MODEL_DRIVEN_PREVIEW_PAGE_UPGRADE_FAIL",
        "marker": MARKER if ok else "CHECKS_NOT_OK",
        "checks": checks
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
