from PIL import Image
from io import BytesIO


ALLOWED_TYPES = {
    "image/jpeg",
    "image/png",
    "image/webp"
}


def compress_image(
    file_content: bytes,
    max_width: int = 1600,
    max_height: int = 1600,
    quality: int = 80
) -> tuple[bytes, str]:

    image = Image.open(
        BytesIO(file_content)
    )

    # Pastikan image menggunakan RGB/RGBA
    if image.mode in ("RGBA", "LA"):
        background = Image.new(
            "RGB",
            image.size,
            "white"
        )

        background.paste(
            image,
            mask=image.getchannel("A")
        )

        image = background

    else:
        image = image.convert("RGB")

    # Resize jika terlalu besar
    image.thumbnail(
        (max_width, max_height),
        Image.Resampling.LANCZOS
    )

    # Simpan sebagai WebP
    output = BytesIO()

    image.save(
        output,
        format="WEBP",
        quality=quality,
        method=6
    )

    output.seek(0)

    return output.getvalue(), "image/webp"