import os

from aiotg import Bot, Chat
import imageio
from services import ClassifyModel, get_square

model = ClassifyModel()

bot = Bot(api_token=os.getenv("TG_TOKEN"))


@bot.command("/start")
async def start(chat: Chat, match):
    return chat.reply("Send me photo of ant or bee.")


async def process_image(binary_data, chat_to_reply: Chat):
    # Convert binary data to numpy.ndarray image
    image = imageio.imread(binary_data)

    # Do the magic
    tag = await model.predict.call(image)

    # Simple text response
    await chat_to_reply.reply(f"I think this is {tag} ...")

    # Or image response
    with open(f"{tag}.jpg", "rb") as f:
        await chat_to_reply.send_photo(f, caption=f"The {tag} like this one!")


@bot.handle("photo")
async def handle_photo(chat: Chat, photos):
    # Get image binary data
    meta = await bot.get_file(photos[-1]["file_id"])
    resp = await bot.download_file(meta["file_path"])
    data = await resp.read()

    await process_image(data, chat)


@bot.handle("document")
async def handle_document(chat: Chat, document):
    # Get image binary data
    meta = await bot.get_file(document["file_id"])
    resp = await bot.download_file(meta["file_path"])
    data = await resp.read()

    await process_image(data, chat)


@bot.command(r"/square (.+)")
async def square_command(chat: Chat, match):
    val = match.group(1)
    try:
        val = float(val)
        square = await get_square.call(val)
        resp = f"Square for {val} is {square}"
    except Exception():
        resp = "Invalid number"
    return chat.reply(resp)


bot.run()
