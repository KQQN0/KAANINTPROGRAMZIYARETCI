# db2json.py (DÜZELTİLMİŞ HALİ)
import sqlite3
import json
from app import app, get_db # app ve get_db fonksiyonunu app.py'den import edin

def export_data_to_json():
    with app.app_context(): # Flask uygulama bağlamı içinde çalıştır
        db = get_db()
        cursor = db.cursor()

        # Kullanıcıları çek
        cursor.execute("SELECT id, username FROM users") # Şifreyi dahil etmeyin!
        users = cursor.fetchall()
        users_data = []
        for user in users:
            users_data.append(dict(user)) # sqlite3.Row objesini dict'e çevirir

        # Misafirleri çek
        cursor.execute("SELECT * FROM misafirler")
        visitors = cursor.fetchall()
        visitors_data = []
        for visitor in visitors:
            visitors_data.append(dict(visitor))

        db.close()

        # JSON dosyalarına yaz
        with open('users.json', 'w', encoding='utf-8') as f:
            json.dump(users_data, f, ensure_ascii=False, indent=4)

        with open('misafirler.json', 'w', encoding='utf-8') as f: # Dosya adını misafirler.json olarak değiştirdim
            json.dump(visitors_data, f, ensure_ascii=False, indent=4)

        print("✔ Kullanıcılar 'users.json' ve misafirler 'misafirler.json' dosyalarına başarıyla aktarıldı.")

if __name__ == '__main__':
    export_data_to_json()