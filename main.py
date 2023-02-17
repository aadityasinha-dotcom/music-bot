from swibots import (
        BotApp,
        InlineKeyboardButton,
        filters, 
        group, 
        MemberJoinedEvent, 
        BotContext, 
        Message, 
        RegisterCommand, 
        CommandEvent,
        community,
        InlineMarkup,
        CallbackQueryEvent,
        inline_markup,
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
            RegisterCommand("music", "Search for a music", True),
            RegisterCommand("video", "Search for a video", True)
        ]
)

async def download_song(url: str):
    if url is not None:
        yt = YouTube(url).streams.filter(progressive=True, file_extension='mp4').first().download()
        return yt
    else:
        return -1

async def convert_to_mp3(path: str):
    # Load the MP4 file
    mp4_file = await AudioSegment.from_file(path, format="mp4")
    # Convert the MP4 file to MP3
    mp3_file = mp4_file.export(f"{path}.mp3", format="mp3")
    return f"{path}.mp3"

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
'''

async def get_music(query: str):
    music = VideosSearch(query, limit = 1).result()
    music = music['result'][0]
    return {
            'title': music['title'],
            'url': music['link'],
            # 'thumbnail': music['thumbnail'],
            # 'description': music['description'],
            # 'viewCount': music['viewCount'],
    }


async def show_results_music(search: str, message: Message):
    musics = await get_music(search+" song")
    # musics = {'title': 'Ghungroo'}
    if not musics:
        await message.edit_text(f"I couldn't found any result for {search}!")
        return

    btn = [
       [
            InlineKeyboardButton(
                text=f"{musics.get('title')}",
                callback_data=f"song_search#{musics.get('url')}",
            )
        ],
    ]

    await message.edit_text(f"Here is what i found", inline_markup=InlineMarkup(btn))

async def show_results_video(search: str, message: Message):
    videos = await get_music(search)
    if not videos:
        await message.edit_text(f"I couldn't found any result for {search}!")
        return

    btn = [
            [
                InlineKeyboardButton(
                    text=f"{videos.get('title')}",
                    callback_data=f"video_search#{videos.get('url')}",
                    )
                ],
            ]
        
    await message.edit_text(f"Here is what i found", inline_markup=InlineMarkup(btn))

@app.on_command(["music"])
async def music_search(ctx: BotContext[CommandEvent]):
    message = ctx.event.message
    params = ctx.event.params
    if params is None or len(params) == 0:
        await message.reply_text(f"Please enter a music name!\nType /{ctx.event.command} <music name>")
        return

    mymessage = await message.reply_text(f"Searching for {params}...")
    await show_results_music(params, mymessage)

@app.on_command(["video"])
async def video_search(ctx: BotContext[CommandEvent]):
    message = ctx.event.message
    params = ctx.event.params
    if params is None or len(params) == 0:
        await message.reply_text(f"Please enter a video name!\nType /{ctx.event.command} <video name>")
        return

    mymessage = await message.reply_text(f"Searching for {params}...")
    await show_results_video(params, mymessage)


@app.on_command("echo")
async def echo_handler(ctx: BotContext[CommandEvent]):
    m = await ctx.prepare_response_message(ctx.event.message)
    text = ctx.event.params or "Nothing to echo"
    m.message = f"Your message: {text}"
    await ctx.send_message(m)

@app.on_callback_query(filters.regexp('^song_search'))
async def song_search_callback(ctx: BotContext[CallbackQueryEvent]):
    i, url = ctx.event.callback_data.split("#")
    message: Message = ctx.event.message
    btn = [
            [
                InlineKeyboardButton(
                    text = f"Download",
                    # url = url,
                    callback_data=f"download_music#{url}",
                    )
                ],
            ]
    
    await message.edit_text(f"Downlad this song?", inline_markup=InlineMarkup(btn))

@app.on_callback_query(filters.regexp('^video_search'))
async def video_search_callback(ctx: BotContext[CallbackQueryEvent]):
    i, url = ctx.event.callback_data.split("#")
    message: Message = ctx.event.message
    btn = [
            [
                InlineKeyboardButton(
                    text=f"Download",
                    callback_data=f"download_video#{url}",
                    )
                ],
            ]

    await message.edit_text(f"Download this video?", inline_markup=InlineMarkup(btn))

@app.on_callback_query(filters.regexp('^download_video'))
async def video_download_callback(ctx: BotContext[CallbackQueryEvent]):
    i, url = ctx.event.callback_data.split("#")
    path = await download_song(url)
    index = 0
    for i in range(len(path)-1,-1,-1):
        if path[i]=='/':
            index = i+1
            break
    path = path[index:]
    message: Message = ctx.event.message
    await message.edit_text(f"Downloading")
    if path==-1:
        await message.reply_text(f"Error occurred try again")
        return
    message: Message = ctx.event.message
    btn = [
            [
                InlineKeyboardButton(
                    text = f"Save the file",
                    callback_data=f"save#{path}",
                    )
                ],
            ]
    await message.edit_text(f"Downloaded, do you wanna save this file?", inline_markup=InlineMarkup(btn))

@app.on_callback_query(filters.regexp("^download_music"))
async def song_download_callback(ctx: BotContext[CallbackQueryEvent]):
    i, url = ctx.event.callback_data.split("#")
    path = await download_song(url)
    index = 0
    for i in range(len(path)-1,-1,-1):
        if path[i]=='/':
            index = i+1
            break
    path = path[index:]

    message: Message = ctx.event.message
    await message.edit_text(f"Downloading")
    if path==-1:
        await message.reply_text(f"Error occurred try again")
        return
    btn = [
            [
                InlineKeyboardButton(
                    text=f"Save the file {path}",
                    callback_data=f"save#'{path}",
                    )
                ],
            ]
    await message.edit_text(
            f"Downloaded, do you wanna save this file?", inline_markup=InlineMarkup(btn)
            )


@app.on_callback_query((filters.regexp("^save")))
async def download_message(ctx: BotContext[CallbackQueryEvent]):
    i, path = ctx.event.callback_data.split("#")
    btn = [
            [
                InlineKeyboardButton(
                    text=f"Download file",
                    url=path,
                    )
                ],
            ]
    message: Message = ctx.event.message
    message.media_link = path
    message.status = 7
    message.caption = "File to download"
    message.inline_markup = InlineMarkup(btn)
    await message.send()

app.run()

