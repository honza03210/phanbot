from PIL import Image, ImageDraw, ImageFont
from requests import get


def render_as_pic(table, rows) -> Image:
    """
    copy-paste, but it works
    """

    # Create a new image with a white background
    img_width, img_height = 730, 45 + 22 * rows
    background_color = (0, 0, 0)  # Black
    table_color = (255, 255, 255)  # White
    font_path = "/usr/share/fonts/truetype/liberation2/LiberationMono-Bold.ttf"

    font_size = 16
    line_spacing = 4
    font = ImageFont.truetype(font_path, font_size)
    line_height = font.getsize("hg")[1] + line_spacing
    rows = table.split("\n")

    image = Image.new("RGB", (img_width, img_height), background_color)
    draw = ImageDraw.Draw(image)
    
    # Render the table onto the image
    y = 5
    for row in rows:
        draw.text((5, y), row, font=font, fill=table_color)
        y += line_height
    return image


async def send_cat(channel, cat_key, gib_message = True):
    url = "https://api.thecatapi.com/v1/images/search"
    headers = {"x-api-key": cat_key}
    response = get(url, headers=headers)

    if response.status_code != 200:
        return
    
    cat_url = response.json()[0]["url"]

    if gib_message:
        await channel.send("Tady mas kocicku <3\n" + cat_url)

