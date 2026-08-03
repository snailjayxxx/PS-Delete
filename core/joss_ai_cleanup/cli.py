from __future__ import annotations

import argparse
import asyncio
import base64
import os
import sys
from pathlib import Path

from PIL import Image

from .app import app
from .config import ConfigStore
from .pipeline import build_rgba_result, decode_provider_image, prepare_raw_request
from .prompts import build_prompt
from .providers.registry import create_provider
from .schemas import RawEditRequest


def _configure(args: argparse.Namespace) -> int:
    store = ConfigStore()
    if args.api_key:
        store.set_api_key(args.provider, args.api_key)
    values = {
        "base_url": args.base_url,
        "model": args.model,
        "workspace_id": args.workspace_id,
        "endpoint_id": args.endpoint_id,
        "region": args.region,
    }
    store.update_settings(args.provider, values)
    print(f"Configured provider: {args.provider}")
    return 0


async def _edit_file_async(args: argparse.Namespace) -> int:
    input_path = Path(args.input).expanduser().resolve()
    output_path = Path(args.output).expanduser().resolve()
    if not input_path.exists():
        raise FileNotFoundError(input_path)

    with Image.open(input_path) as opened:
        icc_profile = opened.info.get("icc_profile")
        exif = opened.info.get("exif")
        image = opened.convert("RGB")
    width, height = image.size
    if width * height > 40_000_000:
        image.thumbnail((7000, 7000), Image.Resampling.LANCZOS)
        width, height = image.size

    if args.mask:
        with Image.open(Path(args.mask).expanduser().resolve()) as mask_opened:
            mask = mask_opened.convert("L").resize((width, height), Image.Resampling.LANCZOS)
    else:
        mask = Image.new("L", (width, height), 255)

    request = RawEditRequest(
        provider=args.provider,
        model=args.model,
        operation=args.operation,
        prompt=args.prompt or "",
        width=width,
        height=height,
        image_rgb_b64=base64.b64encode(image.tobytes()).decode("ascii"),
        mask_l_b64=base64.b64encode(mask.tobytes()).decode("ascii"),
        quality=args.quality,
        rights_confirmed=args.rights_confirmed,
    )
    prepared = prepare_raw_request(request)
    store = ConfigStore()
    provider = create_provider(args.provider, store.get_api_key(args.provider), store.get_settings(args.provider))
    result = await provider.edit(
        prepared,
        build_prompt(request.operation, request.prompt, True),
        request.model,
        request.quality,
        {},
    )
    edited = decode_provider_image(result.image_bytes, prepared.image.size)
    rgba_bytes = build_rgba_result(prepared.image, edited, prepared.mask)
    rgba = Image.frombytes("RGBA", prepared.image.size, rgba_bytes)

    # File output should be visually complete, unlike the transparent Photoshop layer result.
    final = Image.alpha_composite(prepared.image.convert("RGBA"), rgba).convert("RGB")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    suffix = output_path.suffix.lower()
    save_meta = {}
    if icc_profile:
        save_meta["icc_profile"] = icc_profile
    if exif:
        save_meta["exif"] = exif
    if suffix in {".tif", ".tiff"}:
        final.save(output_path, format="TIFF", compression="tiff_lzw", **save_meta)
    elif suffix == ".png":
        final.save(output_path, format="PNG", **save_meta)
    else:
        final.save(output_path, format="JPEG", quality=100, subsampling=0, **save_meta)
    print(output_path)
    return 0


def _edit_file(args: argparse.Namespace) -> int:
    if args.operation == "authorized_overlay" and not args.rights_confirmed:
        print("--rights-confirmed is required for authorized_overlay", file=sys.stderr)
        return 2
    return asyncio.run(_edit_file_async(args))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="joss-ai-cleanup-core")
    parser.add_argument("--version", action="version", version="0.1.0")
    sub = parser.add_subparsers(dest="command", required=True)

    serve = sub.add_parser("serve", help="Run the localhost API server")
    serve.add_argument("--host", default="127.0.0.1")
    serve.add_argument("--port", type=int, default=18780)

    configure = sub.add_parser("configure", help="Store provider credentials and settings")
    configure.add_argument("--provider", required=True)
    configure.add_argument("--api-key")
    configure.add_argument("--base-url")
    configure.add_argument("--model")
    configure.add_argument("--workspace-id")
    configure.add_argument("--endpoint-id")
    configure.add_argument("--region")

    edit = sub.add_parser("edit-file", help="Process one image file")
    edit.add_argument("--input", required=True)
    edit.add_argument("--output", required=True)
    edit.add_argument("--mask")
    edit.add_argument("--provider", required=True)
    edit.add_argument("--model")
    edit.add_argument(
        "--operation",
        default="remove_object",
        choices=["remove_object", "film_dust", "film_scratch", "denoise", "authorized_overlay", "custom"],
    )
    edit.add_argument("--prompt", default="")
    edit.add_argument("--quality", choices=["low", "medium", "high"], default="medium")
    edit.add_argument("--rights-confirmed", action="store_true")
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    try:
        if args.command == "serve":
            import uvicorn

            uvicorn.run(app, host=args.host, port=args.port, log_level="info")
            return
        if args.command == "configure":
            raise SystemExit(_configure(args))
        if args.command == "edit-file":
            raise SystemExit(_edit_file(args))
    except KeyboardInterrupt:
        raise SystemExit(130)
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        raise SystemExit(1)
