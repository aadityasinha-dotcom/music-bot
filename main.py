from swibots import (
        BotApp, 
        group, 
        MemberJoinedEvent, 
        BotContext, 
        Message, 
        RegisterCommand, 
        CommandEvent,
        community
)
import logging
import re
from youtubesearchpython import VideosSearch
from pytube import YouTube
from pydub import AudioSegment


logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = BotApp(
        "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6MzM0LCJpc19ib3QiOnRydWUsImFjdGl2ZSI6dHJ1ZSwiaWF0IjoxNjc2MjY5ODI4LCJleHAiOjIzMDc0MjE4Mjh9.Z7lqKzrD7Pe_Q8bTDyYRKDRxXniU6u_AjytyxGXhNmI",
             "your bot description").register_command(
        [
            RegisterCommand("echo", "Echoes the message", True),
            RegisterCommand(["search", "file", "files"],
                        "Search for indexed media", True),
            RegisterCommand(["music"],
                        "Search for a music", True),
        ]
)

async def convert_to_mp3(path: str):
    # Load the MP4 file
    mp4_file = AudioSegment.from_file(path, format="mp4")
    # Convert the MP4 file to MP3
    mp3_file = mp4_file.export(f"{path}.mp3", format="mp3")

'''
async def save_file(media: SwiMedia):
    """Save file in database"""

    # TODO: Find better way to get same file_id for same media to avoid duplicates
    # file_id, file_ref = unpack_new_file_id(media.file_id)
    file_name = re.sub(r"(_|\-|\.|\+)", " ", str(media.file_name))
    try:
        file = Media(
            file_id=media.id,
            source_id=media.source_id,
            file_name=media.file_name,
            file_size=media.file_size,
            file_type=media.media_type,
            mime_type=media.mime_type,
            caption=media.caption,
            description=media.description,
            file_url=media.url,
        )
    except ValidationError as e:
        logger.exception('Error occurred while saving file in database')
        return False, 2
    else:
        try:
            await file.commit()
        except DuplicateKeyError:
            logger.warning(
                f'{getattr(media, "file_name", "NO_FILE")} is already saved in database'
            )

            return False, 0
        else:
            logger.info(
                f'{getattr(media, "file_name", "NO_FILE")} is saved to database')
            return True, 1

async def get_music(query: str):
    music = VideoSearch(str, limit = 1).result()
    music = music['result'][0]
    return {
            'title': music['title'],
            'url': music['link'],
            'thumbnail': music['thumbnail'],
            'description': music['description'],
            'viewCount': music['viewCount'],
    }
'''


async def show_results(search: str, message: Message):
    musics = await get_music(search)
    if not musics:
        await message.edit_text(f"I couldn't found any result for {search}!")
        return

    btn = [
        [
            InlineKeyboardButton(
                text=f"{music.get('title')} - {music.get('year')}",
                callback_data=f"{music.get('title')}#{search}",
            )
        ]
        for music in musics
    ]
    await message.edit_text(f"Here is what i found", inline_markup=InlineMarkup(btn))

@app.on_command(["music"])
async def imdb_search(ctx: BotContext[CommandEvent]):
    message = ctx.event.message
    params = ctx.event.params
    if params is None or len(params) == 0:
        await message.reply_text(f"Please enter a music name!\nType /{ctx.event.command} <movie name>")
        return

    mymessage = await message.reply_text(f"Searching for {params}...")
    await show_results(params, mymessage)


@app.on_command("echo")
async def echo_handler(ctx: BotContext[CommandEvent]):
    m = await ctx.prepare_response_message(ctx.event.message)
    text = ctx.event.params or "Nothing to echo"
    m.message = f"Your message: {text}"
    await ctx.send_message(m)

app.run()
