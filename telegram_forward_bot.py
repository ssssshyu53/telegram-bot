
from pyrogram import Client, filters
import re

api_id = 27522621
api_hash = "678ea1fd4e406db179f0d1ca307e81a7"
bot_token = "7993866113:AAGyU45CV7_qbjXlQY85Obqk-gRNCiec4M0"

# القنوات (قم بتعديلها بوضع معرف القناة مسبوقًا بـ @)
source_channel = "@YastaftwonkMen3"  # قناة المصدر
target_channel = "@fatwaWahidbaly"  # قناة الهدف

app = Client("forwarder_bot", api_id=api_id, api_hash=api_hash, bot_token=bot_token)

@app.on_message(filters.chat(source_channel))
async def process_message(client, message):
    if not message.audio and not message.voice:
        return
    if not message.text:
        return
    if "فضيلة الشيخ: وحيد بالي" not in message.text:
        return

    try:
        number_match = re.search(r"م\s*[:：]?\s*(\d+)", message.text)
        section_match = re.search(r"القسم\s*[:：]?\s*(.+?)\n", message.text)
        question = message.text.split("السؤال")[1].split("يجيب عليه")[0].strip()

        number = number_match.group(1) if number_match else "؟"
        section = section_match.group(1).strip() if section_match else "غير محدد"

        new_text = f"""م : {number}
القسم: {section}

السؤال : 🌸
{question}

يجيب عليه فضيلة الشيخ: وحيد بالي"""

        if message.voice:
            await client.send_voice(chat_id=target_channel, voice=message.voice.file_id, caption=new_text)
        elif message.audio:
            await client.send_audio(chat_id=target_channel, audio=message.audio.file_id, caption=new_text)

    except Exception as e:
        print("خطأ في المعالجة:", e)

app.run()
