#!/usr/bin/env python

import settings

import json
import os
import ssl

from aiohttp import web, ClientSession
from async_generator import async_generator, yield_

from aiotelegrambot import Bot, Client, Content, Handlers, Message
from aiotelegrambot.rules import Contains

handlers = Handlers()

@handlers.add(content_type=Content.PHOTO)
async def photo(message: Message):
    photos = message.raw.get("message", {}).get("photo", [])
    date = message.raw.get("message", {}).get("date", 0)
    fid = None
    size = 0
    for p in photos:
        if size < p.get("file_size", 0):
            fid = p.get("file_id", None)
            size = p.get("file_size")
    if not fid:
        print("error:", message.raw)
        await message.send_message("Error retrieving photo details, sorry.")
        return
    photofile = await message.request("get", "getFile", data=dict(file_id=fid))
    path = photofile.get("result", {}).get("file_path", "")
    url = 'https://api.telegram.org/file/bot{}/{}'.format(settings.TOKEN, path)
    async with ClientSession() as session:
        async with session.post(settings.GALLERY_PUSH_URL,
               data=dict(date=str(date), url=url)) as resp:
            if resp.status == 200:
                await message.send_message("Photo accepted for processing.")
            else:
                await message.send_message("Photo was rejected, sorry.")

async def webhook_handle(request):
    bot = request.app["bot"]
    data = await request.text()
    await bot.process_update(json.loads(data))
    return web.Response()

@async_generator
async def init_bot(app: web.Application):
    bot = Bot(Client(settings.TOKEN), handlers)
    await bot.initialize(webhook=True)
    await bot.client.set_webhook("https://{}:{}/{}".format(settings.HOST, settings.PORT, settings.TOKEN), certificate=settings.CERTFILE)
    app["bot"] = bot
    await yield_()
    await bot.client.delete_webhook()
    await bot.close()
    await bot.client.close()

app = web.Application()
app.router.add_post("/{}".format(settings.TOKEN), webhook_handle)
app.cleanup_ctx.extend([init_bot])

context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
context.load_cert_chain(settings.CERTFILE, settings.PRIVKEYFILE)

web.run_app(app, host="0.0.0.0", port=settings.PORT, ssl_context=context)

