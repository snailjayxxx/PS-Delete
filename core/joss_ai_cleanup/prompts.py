from __future__ import annotations

from .schemas import Operation


BASE_RULES = (
    "Preserve the original composition, perspective, lighting, color, faces, text, "
    "film grain and all areas not explicitly marked for editing. Do not crop, rotate, "
    "reframe, add new subjects, or change the camera viewpoint. Return one edited image only."
)

PROMPTS: dict[Operation, str] = {
    "remove_object": (
        "Remove the unwanted object or person inside the marked area and reconstruct a natural, "
        "photorealistic background using the surrounding visual context."
    ),
    "film_dust": (
        "Remove only film-scan dust, hair and small debris inside the marked area. Preserve genuine "
        "film grain, eyelashes, hair strands, stars, wires and fine photographic texture."
    ),
    "film_scratch": (
        "Repair only film scratches and scan damage inside the marked area. Reconstruct detail from "
        "nearby context while preserving the original photographic character and grain."
    ),
    "denoise": (
        "Reduce objectionable luminance and chroma noise while preserving edges, facial identity, "
        "skin texture and natural film grain. Avoid plastic smoothing or invented detail."
    ),
    "authorized_overlay": (
        "Remove the selected text, date stamp, logo or overlay from this image that the user owns or "
        "is authorized to edit, and reconstruct the hidden background naturally."
    ),
    "custom": "Apply only the user's requested edit inside the marked area.",
}


def build_prompt(operation: Operation, user_prompt: str, has_mask: bool) -> str:
    mask_rule = (
        "A second image is supplied as a mask: white or opaque pixels indicate the only area that may "
        "be changed; black or transparent pixels must remain unchanged."
        if has_mask
        else "No explicit mask is supplied; make the smallest possible change needed for the request."
    )
    custom = f" User instruction: {user_prompt}" if user_prompt else ""
    return f"{PROMPTS[operation]} {mask_rule} {BASE_RULES}{custom}"
