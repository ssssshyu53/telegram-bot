import os
from pyrogram import Client, filters
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading

# استخدام المنفذ 10000 كما هو مطلوب من Render
PORT = int(os.environ.get('PORT', 10000))

# معلومات الواجهة البرمجية
api_id = os.environ.get('API_ID', '27522621')
api_hash = os.environ.get('API_HASH', '678ea1fd4e406db179f0d1ca307e81a7')
bot_token = os.environ.get('BOT_TOKEN', '7993866113:AAGyU45CV7_qbjXlQY85Obqk-gRNCiec4M0')

# القنوات
source_channel = "@salamyg"
target_channel = "@fatwaWahidbaly"

class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write(b'Telegram Bot is running')
    
    def do_HEAD(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()

def run_server():
    server_address = ('0.0.0.0', PORT)
    httpd = HTTPServer(server_address, SimpleHTTPRequestHandler)
    print(f'Starting HTTP server on port {PORT}...')
    httpd.serve_forever()

# إنشاء عميل بيروغرام
app = Client("forwarder_bot", api_id=api_id, api_hash=api_hash, bot_token=bot_token)

@app.on_message(filters.chat(source_channel))
async def process_message(client, message):
    print(f"تم استلام رسالة من: {source_channel}")
    
    if not (message.audio or message.voice):
        return
    
    if not message.caption and not message.text:
        return
    
    text_content = message.text if message.text else message.caption
    
    if "فضيلة الشيخ: وحيد بالي" not in text_content and "الشيخ : وحيد بالي" not in text_content:
        return
    
    try:
        import re
        number_match = re.search(r"م\s*[:：]?\s*(\d+)", text_content)
        section_match = re.search(r"القسم\s*[:：]?\s*(.+?)(?:\n|$)", text_content)
        
        question = ""
        if "السؤال" in text_content:
            question_parts = text_content.split("السؤال")
            if len(question_parts) > 1:
                if "يجيب عليه" in question_parts[1]:
                    question = question_parts[1].split("يجيب عليه")[0].strip()
                else:
                    question = question_parts[1].strip()
        
        number = number_match.group(1) if number_match else "؟"
        section = section_match.group(1).strip() if section_match else "غير محدد"
        
        new_text = f"""م : {number}
القسم: {section}

السؤال : 🌸
{question}

يجيب عليه فضيلة الشيخ: وحيد بالي"""
        
        print(f"جاري إعادة توجيه الرسالة إلى: {target_channel}")
        
        if message.voice:
            await client.send_voice(chat_id=target_channel, voice=message.voice.file_id, caption=new_text)
        elif message.audio:
            await client.send_audio(chat_id=target_channel, audio=message.audio.file_id, caption=new_text)
            
        print("تم إرسال الرسالة بنجاح")
        
    except Exception as e:
        print(f"خطأ في المعالجة: {e}")

if __name__ == "__main__":
    # بدء خادم HTTP في thread منفصل
    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()
    
    print("جاري بدء تشغيل البوت...")
    # تشغيل البوت
    app.run()
