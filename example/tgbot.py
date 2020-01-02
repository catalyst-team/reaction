import os

import imageio
from aiotg import Bot, Chat

from services import ClassifyModel, get_square

model = ClassifyModel()

bot = Bot(api_token=os.getenv("TG_TOKEN"))


@bot.command("/start")
async def start(chat: Chat, match):
    return chat.reply("Send me photo of ant or bee.")


@bot.handle("photo")
async def handle_photo(chat: Chat, photos):
    # Get image binary data
    meta = await bot.get_file(photos[-1]["file_id"])
    resp = await bot.download_file(meta["file_path"])
    data = await resp.read()

    # Convert binary data to numpy.ndarray image
    image = imageio.imread(data)

    # Do the magic
    tag = await model.predict.call(image)

    # Simple text response
    await chat.reply(f"I think this is {tag} ...")

    # Or image response
    with open(f"{tag}.jpg", "rb") as f:
        await chat.send_photo(f, caption=f"... the {tag} like this one!")


@bot.command(r"/square (.+)")
async def square_command(chat: Chat, match):
    val = match.group(1)
    try:
        val = float(val)
        square = await get_square.call(val)
        resp = f"Square for {val} is {square}"
    except:
        resp = "Invalid number"
    return chat.reply(resp)


bot.run()
