import base64

from PIL import Image

from joss_ai_cleanup.pipeline import build_rgba_result, prepare_raw_request
from joss_ai_cleanup.schemas import RawEditRequest


def test_prepare_and_alpha_result():
    image = Image.new("RGB", (4, 3), (10, 20, 30))
    mask = Image.new("L", (4, 3), 0)
    mask.putpixel((2, 1), 255)
    request = RawEditRequest(
        provider="openai",
        width=4,
        height=3,
        image_rgb_b64=base64.b64encode(image.tobytes()).decode(),
        mask_l_b64=base64.b64encode(mask.tobytes()).decode(),
    )
    prepared = prepare_raw_request(request)
    edited = Image.new("RGB", (4, 3), (200, 100, 50))
    rgba = Image.frombytes("RGBA", (4, 3), build_rgba_result(prepared.image, edited, prepared.mask))
    assert rgba.getpixel((0, 0))[3] == 0
    assert rgba.getpixel((2, 1))[3] > 0
