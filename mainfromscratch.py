#encoding=utf-8
import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
from collections import defaultdict

from ydisk import save_photos
from regions_codes import REGION_CODES

ID_CHAT_SVALKA = '***'
ID_RUSSIA_FROM_TIMETABLES = '***'
ID_CHAT_LOG = '***'
TG_TOKEN = '***'

media_groups = defaultdict(list)
previous_media_group_id = 0

def is_valid_message(text):
    res = text.split(' ')
    if '#расписания' not in res:
        return False
    if len(res) < 3:
        return False
    region_list = [string for string in res if string in REGION_CODES]
    if region_list:
        code_index = res.index(region_list[0])
    rasp_index = res.index('#расписания')
    return res[code_index], ' '.join(res[code_index + 1:rasp_index])

async def process_message(message, context):
    photos = []
    message_date = message.date
    txt = message.caption
    if not txt:
        txt = message.text
    if message.photo:
        photos.append(message.photo[-1])
    print(txt, photos)

    if txt and is_valid_message(txt):
        number_of_region, name_of_region = is_valid_message(txt)
        print(number_of_region)
        if message.reply_to_message:
            # Handle reply to photo
            if message.reply_to_message.photo:
                photos.append(message.reply_to_message.photo[-1])
            # Handle reply to album
            if message.reply_to_message.media_group_id:
                media_group = media_groups[message.reply_to_message.media_group_id]
                photos = [msg.photo[-1] for msg in media_group if msg.photo]
        if photos:
            await save_photos(photos, number_of_region, name_of_region, message_date)
            await context.bot.send_message(ID_CHAT_LOG, f'saved {len(photos)} photo(s) to {number_of_region} {name_of_region}')
        if number_of_region in CHATICS:
            # Resending reply to album
            if message.reply_to_message.media_group_id:
                for media in media_group:
                    pass

async def process_media_group(media_group, context):
    photos = [message.photo[-1] for message in media_group if message.photo]
    message = media_group[0]
    message_date = message.date
    txt = message.caption
    print(txt, photos)

    if txt and is_valid_message(txt):
        number_of_region, name_of_region = is_valid_message(txt)
        await save_photos(photos, number_of_region, name_of_region, message_date)
        await context.bot.send_message(ID_CHAT_LOG, f'saved {len(photos)} photo(s) to {number_of_region} {name_of_region}')
        if number_of_region in CHATICS:
            for media in media_group:
                pass

async def handle_message(update, context):
    message = update.message
    global previous_media_group_id

    if not message or str(message.chat_id) != ID_RUSSIA_FROM_TIMETABLES: 
        return

    if message.media_group_id:
        if message.media_group_id in media_groups:
            media_groups[message.media_group_id].append(message)
            print(message.media_group_id, previous_media_group_id)
        else:
            if media_groups:
                await process_media_group(media_groups[previous_media_group_id], context)
            media_groups[message.media_group_id].append(message)
            previous_media_group_id = message.media_group_id
            print(f'New media group: {previous_media_group_id}')
    else:
        await process_message(message, context)

def main():
    application = ApplicationBuilder().token(TG_TOKEN).build()
    application.add_handler(MessageHandler(filters.TEXT | filters.PHOTO, handle_message))
    application.run_polling()

if __name__ == "__main__":
    main()
