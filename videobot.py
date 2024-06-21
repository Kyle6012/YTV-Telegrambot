import logging
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters
import pytube
from pytube import YouTube

logging.basicConfig(level=logging.INFO)

TOKEN = '7124059740:AAG9R9a2l_6xFrlrOGfuSXmwFE6i34E0vQU'

def load_cookies(cookie_file):
    from http.cookiejar import MozillaCookieJar

    cj = MozillaCookieJar()
    cj.load(cookie_file)
    return cj


def get_yt_with_cookies(url, cookie_file):
    yt = YouTube(url)
    cookies = load_cookies(cookie_file)
    yt.request.headers.update({'Cookie': '; '.join([f"{c.name}={c.value}" for c in cookies])})
    return yt

async def start(update, context):
    await context.bot.send_message(chat_id=update.effective_chat.id, text='Hello! I can download YouTube videos for you. Send me a YouTube video URL to get started.')

async def download_video(update, context):
    url = update.message.text
    if not url.startswith('https://youtu.be/'):
        await context.bot.send_message(chat_id=update.effective_chat.id, text='Invalid YouTube URL. Please try again.')
        return

    try:
        yt = get_yt_with_cookies(url, 'cookies.txt')
        streams = yt.streams.filter(progressive=True, file_extension='mp4')

        resolutions = [s.resolution for s in streams]
        resolutions_str = '\n'.join([f'{i+1}. {r}' for i, r in enumerate(resolutions)])

        await context.bot.send_message(chat_id=update.effective_chat.id, text=f'Choose a resolution:\n{resolutions_str}')

        context.user_data['streams'] = streams
        context.user_data['yt'] = yt
        await context.bot.send_message(chat_id=update.effective_chat.id, text='Enter the resolution number:')

    except Exception as e:
        await context.bot.send_message(chat_id=update.effective_chat.id, text=f'An error occurred: {e}')

async def send_video_resolution(update, context):
    try:
        resolution_index = int(update.message.text) - 1
        streams = context.user_data['streams']
        yt = context.user_data['yt']

        if resolution_index < 0 or resolution_index >= len(streams):
            await context.bot.send_message(chat_id=update.effective_chat.id, text='Invalid resolution. Please try again.')
            return

        stream = streams[resolution_index]
        file_path = f'/tmp/{yt.title}.mp4'
        for attempt in range(3):
            try:
                stream.download(file_path)
                break
            except Exception as e:
                if attempt < 2:
                    await asyncio.sleep(2)  # Wait before retrying
                    continue
                else:
                    raise e

        with open(file_path, 'rb') as video_file:
            await context.bot.send_video(chat_id=update.effective_chat.id, video=video_file, caption=f'Downloaded {yt.title} in {streams[resolution_index].resolution}')
    except Exception as e:
        await context.bot.send_message(chat_id=update.effective_chat.id, text=f'An error occurred: {e}')

def main():
    application = ApplicationBuilder().token(TOKEN).build()

    start_handler = CommandHandler('start', start)
    download_handler = MessageHandler(filters.TEXT & ~filters.COMMAND, download_video)
    resolution_handler = MessageHandler(filters.TEXT & ~filters.COMMAND, send_video_resolution)

    application.add_handler(start_handler)
    application.add_handler(download_handler)
    application.add_handler(resolution_handler)

    application.run_polling()

if __name__ == '__main__':
    main()
