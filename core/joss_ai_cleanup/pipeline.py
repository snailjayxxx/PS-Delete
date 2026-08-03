from __future__ import annotations

import base64
import io
from dataclasses import dataclass

from PIL import Image, ImageChops, ImageFilter

from .schemas import RawEditRequest


MAX_PIXELS = 40_000_000


@dataclass(slots=True)
class PreparedImage:
    image: Image.Image
    mask: Image.Image
    image_png: bytes
    mask_png: bytes
    mask_visual_png: bytes
    width: int
    height: int


def _decode_exact(value: str, expected: int, label: str) -> bytes:
    try:
        raw = base64.b64decode(value, validate=True)
    except Exception as exc:
        raise ValueError(f"Invalid base64 for {label}") from exc
    if len(raw) != expected:
        raise ValueError(f"{label} length mismatch: expected {expected}, got {len(raw)}")
    return raw


def prepare_raw_request(request: RawEditRequest) -> PreparedImage:
    if request.width * request.height > MAX_PIXELS:
        raise ValueError("Selected region is too large; reduce the selection or context size")

    rgb = _decode_exact(
        request.image_rgb_b64,
        request.width * request.height * 3,
        "image_rgb_b64",
    )
    image = Image.frombytes("RGB", (request.width, request.height), rgb)

    if request.mask_l_b64:
        mask_raw = _decode_exact(
            request.mask_l_b64,
            request.width * request.height,
            "mask_l_b64",
        )
        mask = Image.frombytes("L", (request.width, request.height), mask_raw)
    else:
        mask = Image.new("L", image.size, 255)

    image_buffer = io.BytesIO()
    image.save(image_buffer, format="PNG", optimize=False)

    # OpenAI requires an alpha-bearing mask. Transparent pixels are editable.
    alpha = ImageChops.invert(mask)
    mask_rgba = Image.new("RGBA", image.size, (255, 255, 255, 255))
    mask_rgba.putalpha(alpha)
    mask_buffer = io.BytesIO()
    mask_rgba.save(mask_buffer, format="PNG", optimize=False)

    visual_buffer = io.BytesIO()
    mask.save(visual_buffer, format="PNG", optimize=False)

    return PreparedImage(
        image=image,
        mask=mask,
        image_png=image_buffer.getvalue(),
        mask_png=mask_buffer.getvalue(),
        mask_visual_png=visual_buffer.getvalue(),
        width=request.width,
        height=request.height,
    )


def decode_provider_image(data: bytes, size: tuple[int, int]) -> Image.Image:
    try:
        with Image.open(io.BytesIO(data)) as opened:
            result = opened.convert("RGB")
    except Exception as exc:
        raise ValueError("Provider did not return a valid image") from exc

    if result.size != size:
        result = result.resize(size, Image.Resampling.LANCZOS)
    return result


def build_rgba_result(original: Image.Image, edited: Image.Image, mask: Image.Image) -> bytes:
    # Slightly soften only hard mask edges to reduce visible seams; existing feathering is preserved.
    extrema = mask.getextrema()
    working_mask = mask
    if extrema == (0, 255):
        working_mask = mask.filter(ImageFilter.GaussianBlur(radius=0.6))

    # The Photoshop result is a transparent layer. Store edited RGB under the mask;
    # Photoshop performs the final alpha blend over the untouched original layer.
    rgba = edited.convert("RGBA")
    rgba.putalpha(working_mask)
    return rgba.tobytes()
