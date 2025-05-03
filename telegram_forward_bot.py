from pyrogram import Client, filters
import re
import os
from aiohttp import web
import asyncio

# معلومات الواجهة البرمجية
api_id = 27522621
api_hash = "678ea1fd4e406db179f0d1ca307e81a7"
bot_token = "7993866113:AAGyU45CV7_qbjXlQY85Obqk-gRNCiec4M0"

# القنوات (قم بتعديلها بوضع معرف القناة مسبوقًا بـ @)
source_channel = "@salamyg"  # قناة المصدر
target_channel = "@fatwaWahidbaly"  # قناة الهدف

# إنشاء تطبيق الويب لعمل HTTP server
app_web = web.Application()

# إنشاء عميل بيروغرام
app = Client("forwarder_bot", api_id=api_id, api_hash=api_hash, bot_token=bot_token)

# دالة للتحقق من صحة الخادم
async def health_check(request):
    return web.Response(text="البوت يعمل بنجاح!")

# إضافة مسار للتحقق من الصحة
app_web.router.add_get("/", health_check)

# معالجة الرسائل من القناة المصدر
@app.on_message(filters.chat(source_channel))
async def process_message(client, message):
    print(f"تم استلام رسالة من: {source_channel}")
    
    # تحقق من وجود ملف صوتي أو رسالة صوتية
    if not (message.audio or message.voice):
        return
    
    # تحقق من وجود نص
    if not message.caption and not message.text:
        return
    
    # استخدم النص أو التعليق حسب ما هو متاح
    text_content = message.text if message.text else message.caption
    
    # تحقق من أن الرسالة تتعلق بالشيخ وحيد بالي
    if "فضيلة الشيخ: وحيد بالي" not in text_content and "الشيخ : وحيد بالي" not in text_content:
        return
    
    try:
        # استخراج رقم الرسالة والقسم والسؤال باستخدام التعبيرات المنتظمة
        number_match = re.search(r"م\s*[:：]?\s*(\d+)", text_content)
        section_match = re.search(r"القسم\s*[:：]?\s*(.+?)(?:\n|$)", text_content)
        
        # محاولة استخراج السؤال بطرق مختلفة للتأكد من الدقة
        question = ""
        if "السؤال" in text_content:
            question_parts = text_content.split("السؤال")
            if len(question_parts) > 1:
                if "يجيب عليه" in question_parts[1]:
                    question = question_parts[1].split("يجيب عليه")[0].strip()
                else:
                    question = question_parts[1].strip()
        
        # استخدام القيم الافتراضية إذا لم يتم العثور على المعلومات
        number = number_match.group(1) if number_match else "؟"
        section = section_match.group(1).strip() if section_match else "غير محدد"
        
        # تنسيق النص الجديد
        new_text = f"""م : {number}
القسم: {section}

السؤال : 🌸

{question}

يجيب عليه فضيلة الشيخ: وحيد بالي"""

        print(f"جاري إعادة توجيه الرسالة إلى: {target_channel}")
        
        # إرسال الرسالة المنسقة مع الملف الصوتي
        if message.voice:
            await client.send_voice(chat_id=target_channel, voice=message.voice.file_id, caption=new_text)
        elif message.audio:
            await client.send_audio(chat_id=target_channel, audio=message.audio.file_id, caption=new_text)
            
        print("تم إرسال الرسالة بنجاح")
        
    except Exception as e:
        print(f"خطأ في المعالجة: {e}")

# دالة لتشغيل خادم الويب
async def run_web_server():
    # الحصول على رقم المنفذ من متغيرات البيئة أو استخدام القيمة الافتراضية
    port = int(os.environ.get("PORT", 10000))
    
    # إعداد الخادم
    runner = web.AppRunner(app_web)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', port)
    
    print(f"بدء تشغيل خادم الويب على المنفذ {port}")
    await site.start()
    
    # الانتظار إلى أجل غير مسمى
    while True:
        await asyncio.sleep(3600)  # انتظار لمدة ساعة ثم التحقق مرة أخرى

# الدالة الرئيسية لتشغيل البوت وخادم الويب معًا
async def main():
    # تشغيل خادم الويب في مهمة منفصلة
    asyncio.create_task(run_web_server())
    
    # تشغيل بوت التيليجرام
    print("بدء تشغيل بوت التيليجرام...")
    await app.start()
    
    # انتظار إلى أجل غير مسمى
    await asyncio.sleep(999999)

# بدء تنفيذ البرنامج
if __name__ == "__main__":
    # تشغيل الدالة الرئيسية مع دعم الإلغاء
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(main())
    except KeyboardInterrupt:
        print("تم إيقاف البوت")
