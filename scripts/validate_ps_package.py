#!/usr/bin/env python3
"""Validate the Photoshop UXP source manifest or a packaged CCX archive."""

from __future__ import annotations

import argparse
import json
import sys
import zipfile
from pathlib import Path
from typing import Any


REQUIRED_PLUGIN_FILES = {"manifest.json", "index.html", "main.js"}


def fail(message: str) -> None:
    raise ValueError(message)


def validate_manifest(manifest: dict[str, Any], expected_version: str | None = None) -> None:
    if manifest.get("manifestVersion") != 5:
        fail("manifestVersion 必须为 5")

    plugin_id = manifest.get("id")
    if not isinstance(plugin_id, str) or not plugin_id.strip():
        fail("id 必须是非空字符串")

    if expected_version and manifest.get("version") != expected_version:
        fail(
            f"Manifest 版本 {manifest.get('version')!r} 与 VERSION {expected_version!r} 不一致"
        )

    host = manifest.get("host")
    if not isinstance(host, dict):
        fail("可分发 CCX 的 host 必须是对象，不能是数组")
    if host.get("app") != "PS":
        fail("host.app 必须为 PS")
    if not isinstance(host.get("minVersion"), str) or not host["minVersion"]:
        fail("host.minVersion 必须是非空字符串")

    entrypoints = manifest.get("entrypoints")
    if not isinstance(entrypoints, list) or not entrypoints:
        fail("entrypoints 必须是非空数组")


def validate_source(plugin_dir: Path, expected_version: str | None) -> None:
    missing = sorted(name for name in REQUIRED_PLUGIN_FILES if not (plugin_dir / name).is_file())
    if missing:
        fail(f"插件目录缺少文件：{', '.join(missing)}")

    manifest = json.loads((plugin_dir / "manifest.json").read_text(encoding="utf-8"))
    validate_manifest(manifest, expected_version)


def validate_ccx(ccx_path: Path, expected_version: str | None) -> None:
    if not zipfile.is_zipfile(ccx_path):
        fail("CCX 不是有效的 ZIP 容器")

    with zipfile.ZipFile(ccx_path) as archive:
        names = {name.rstrip("/") for name in archive.namelist() if name and not name.endswith("/")}
        missing = sorted(REQUIRED_PLUGIN_FILES - names)
        if missing:
            fail(
                "CCX 根目录缺少文件："
                + ", ".join(missing)
                + "。请勿把整个 PS 文件夹作为外层目录打包。"
            )
        manifest = json.loads(archive.read("manifest.json").decode("utf-8-sig"))
        validate_manifest(manifest, expected_version)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("target", type=Path, help="PS 插件目录或 .ccx 文件")
    parser.add_argument("--version-file", type=Path)
    args = parser.parse_args()

    expected_version = None
    if args.version_file:
        expected_version = args.version_file.read_text(encoding="utf-8").strip()

    try:
        if args.target.is_dir():
            validate_source(args.target, expected_version)
        elif args.target.is_file():
            validate_ccx(args.target, expected_version)
        else:
            fail(f"找不到目标：{args.target}")
    except (OSError, ValueError, json.JSONDecodeError, zipfile.BadZipFile) as exc:
        print(f"校验失败：{exc}", file=sys.stderr)
        return 1

    print(f"校验通过：{args.target}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
