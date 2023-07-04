from pyrogram import Client, filters

@Client.on_message(filters.command("start"))
async def startm(bot, message):
    mes = f"Merhaba {message.from_user.mention},\nBu bot sayesinde Wattpad hikayelerini Epub ve Html formatında indirebilirsin iyi kullanımlar..\n\nBot Kullanımı:\nAdım 1: https://www.wattpad.com/story/221912360-no-26 bu url'den hikayenin kodunu alıyoruz. (221912360)\n\nAdım 2: `/dl 221912360` komutunu bota yolluyoruz.."
    await message.reply_text(mes)
