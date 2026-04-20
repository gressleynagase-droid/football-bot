import requests
import pandas as pd
from datetime import datetime

# --- إعدادات الاتصال ---
TELEGRAM_TOKEN = "8528166554:AAERAZHlLG1SCXeggeiq5R7X7-m31APNc_Y"
CHAT_ID = "177315120"
FOOTBALL_API_KEY = "ee2290f695a149ce8177e0446c4f00d3"

def send_to_telegram(file_name, count):
    """إرسال ملف الإكسيل إلى تيليجرام"""
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendDocument"
    today = datetime.now().strftime('%Y-%m-%d')
    caption = f"⚽️ جدول مباريات اليوم ({today})\n✅ تم استخراج {count} مباراة بنجاح."
    
    try:
        with open(file_name, 'rb') as file:
            payload = {'chat_id': CHAT_ID, 'caption': caption}
            files = {'document': file}
            response = requests.post(url, data=payload, files=files)
            if response.status_code == 200:
                print("✅ تم إرسال الملف إلى تيليجرام بنجاح!")
            else:
                print(f"❌ فشل الإرسال: {response.text}")
    except Exception as e:
        print(f"حدث خطأ أثناء الإرسال: {e}")

def get_matches_to_excel():
    """جلب البيانات وتصديرها"""
    url = "https://api.football-data.org/v4/matches"
    headers = { 'X-Auth-Token': FOOTBALL_API_KEY }

    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            matches = data.get('matches', [])

            if not matches:
                print("⚠️ لا توجد مباريات اليوم لتصديرها.")
                return

            matches_list = []
            for match in matches:
                # تحويل الوقت لتوقيت الرياض (UTC+3)
                raw_date = match['utcDate']
                time_ksa = pd.to_datetime(raw_date).tz_convert('Asia/Riyadh').strftime('%I:%M %p')
                
                matches_list.append({
                    'الدوري': match['competition']['name'],
                    'الموعد (توقيت مكة)': time_ksa,
                    'فريق الأرض': match['homeTeam']['name'],
                    'فريق الضيف': match['awayTeam']['name'],
                    'النتيجة': f"{match['score']['fullTime']['home']} - {match['score']['fullTime']['away']}" 
                               if match['score']['fullTime']['home'] is not None else "لم تبدأ بعد"
                })

            # تحويل البيانات إلى إكسيل
            df = pd.DataFrame(matches_list)
            file_name = f"matches_{datetime.now().strftime('%Y%m%d')}.xlsx"
            df.to_excel(file_name, index=False)
            
            print(f"✅ تم إنشاء الملف: {file_name}")
            
            # إرسال الملف إلى تيليجرام
            send_to_telegram(file_name, len(matches_list))
            
        else:
            print(f"❌ خطأ في الـ API: {response.status_code}")
    except Exception as e:
        print(f"حدث خطأ في استخراج البيانات: {e}")

if __name__ == "__main__":
    get_matches_to_excel()
