import sqlite3
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify, Response
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import json
import os 

app = Flask(__name__)

app.secret_key = 'kaan123456' 

DATABASE = 'otel_yonetim.db' 

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row 
    return conn

# Kullanıcı verilerini users.json dosyasına yazan yardımcı fonksiyon
# UYARI: BU FONKSİYON GÜVENLİK RİSKİ TAŞIR! 
# Hashlenmiş şifreleri bile bir dosyaya kaydetmek önerilmez.
# Bu işlem yalnızca kullanıcının özel isteği üzerine demo/test amaçlı yapılmıştır.
# Gerçek (canlı) bir uygulamada ASLA kullanılmamalıdır.
def save_users_to_json_file():
    with app.app_context():
        db = get_db()
        cursor = db.cursor()
        try:
            # Kullanıcıları şifre hashleriyle birlikte çek
            cursor.execute('SELECT id, username, password FROM users')
            users = cursor.fetchall()
            
            users_list = []
            for user in users:
                # Kullanıcı objesini sözlüğe çevirirken 'password' (hashlenmiş) alanını da dahil et
                users_list.append(dict(user)) 

            # users.json dosyasına yaz
            with open('users.json', 'w', encoding='utf-8') as f:
                json.dump(users_list, f, indent=4, ensure_ascii=False)
            print("✔ Kullanıcı verileri (hashlenmiş şifreler dahil) 'users.json' dosyasına kaydedildi/güncellendi. GÜVENLİK RİSKİNE DİKKAT!")
        except Exception as e:
            print(f"Kullanıcı verilerini JSON dosyasına kaydederken hata oluştu: {e}")
        finally:
            db.close()


def init_db():
    with app.app_context():
        db = get_db()
        cursor = db.cursor()

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS misafirler (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ad TEXT NOT NULL,
                soyad TEXT NOT NULL,
                tc_pasaport_no TEXT,
                telefon TEXT,
                email TEXT,
                giris_tarihi_saati DATETIME NOT NULL,
                cikis_tarihi_saati DATETIME,
                oda_no TEXT
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL
            )
        ''')
        
        cursor.execute("SELECT COUNT(*) FROM users")
        if cursor.fetchone()[0] == 0: 
            default_username = "admin"
            default_password = "password" 
            hashed_password = generate_password_hash(default_password)
            cursor.execute('INSERT INTO users (username, password) VALUES (?, ?)', (default_username, hashed_password))
            print(f"Varsayılan yönetici kullanıcısı '{default_username}' başarıyla oluşturuldu.")
        
        db.commit() 
        db.close() 

        # Veritabanı başlatıldıktan sonra kullanıcı verilerini JSON dosyasına kaydet
        save_users_to_json_file()


def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session:
            flash('Bu sayfayı görüntülemek için giriş yapmalısınız.', 'danger')
            return redirect(url_for('giris_formu'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/', methods=['GET'])
def giris_formu():
    if 'logged_in' in session: 
        return redirect(url_for('ana_kayitlar'))
    return render_template('index.html')

@app.route('/giris', methods=['POST'])
def giris():
    kullanici_adi = request.form['kullanici_adi']
    sifre = request.form['sifre']

    db = get_db()
    cursor = db.cursor()
    cursor.execute('SELECT * FROM users WHERE username = ?', (kullanici_adi,))
    user = cursor.fetchone()
    db.close()

    if user and check_password_hash(user['password'], sifre):
        session['logged_in'] = True
        session['username'] = user['username']
        flash('Başarıyla giriş yaptınız!', 'success')
        return redirect(url_for('ana_kayitlar'))
    else:
        flash('Kullanıcı adı veya şifre yanlış.', 'danger')
        return redirect(url_for('giris_formu'))

@app.route('/kayit_ol', methods=['GET', 'POST'])
def kayit_ol():
    if request.method == 'POST':
        kullanici_adi = request.form['kullanici_adi']
        sifre = request.form['sifre']
        hashed_sifre = generate_password_hash(sifre)

        db = get_db()
        cursor = db.cursor()
        try:
            cursor.execute('INSERT INTO users (username, password) VALUES (?, ?)', (kullanici_adi, hashed_sifre))
            db.commit()
            flash('Hesabınız başarıyla oluşturuldu. Giriş yapabilirsiniz.', 'success')
            return redirect(url_for('giris_formu'))
        except sqlite3.IntegrityError:
            flash('Bu kullanıcı adı zaten mevcut.', 'danger')
        finally:
            db.close()
            # Yeni kullanıcı kaydedildikten sonra users.json dosyasını güncelle
            save_users_to_json_file()
    return render_template('register.html')

@app.route('/cikis_yap')
@login_required
def cikis_yap():
    session.pop('logged_in', None)
    session.pop('username', None)
    flash('Başarıyla çıkış yaptınız.', 'info')
    return redirect(url_for('giris_formu'))

@app.route('/ana_kayitlar')
@login_required
def ana_kayitlar():
    return render_template('ana_kayıtlar.html')

@app.route('/ziyaretci_kayit_sayfasi')
@login_required
def ziyaretci_kayit_sayfasi():
    return render_template('ziyaretci_kayit.html', misafir=None) 

@app.route('/kayit', methods=['POST'])
@login_required
def kayit():
    misafir_id = request.form.get('misafir_id')

    ad = request.form['ad']
    soyad = request.form.get('soyad', '')
    tc_pasaport_no = request.form.get('tc_pasaport_no', '')
    telefon = request.form.get('telefon', '')
    email = request.form.get('email', '')
    giris_tarihi_saati = request.form['ziyaret_tarihi'] 
    cikis_tarihi_saati = request.form.get('cikis_tarihi', '')
    oda_no = request.form.get('oda_no', '')

    db = get_db()
    cursor = db.cursor()

    if misafir_id: 
        cursor.execute('''
            UPDATE misafirler SET 
            ad=?, soyad=?, tc_pasaport_no=?, telefon=?, email=?, 
            giris_tarihi_saati=?, cikis_tarihi_saati=?, oda_no=?
            WHERE id=?
        ''', (ad, soyad, tc_pasaport_no, telefon, email, 
              giris_tarihi_saati, cikis_tarihi_saati, oda_no, misafir_id))
        flash('Misafir bilgileri başarıyla güncellendi!', 'success')
    else: 
        cursor.execute('''
            INSERT INTO misafirler (ad, soyad, tc_pasaport_no, telefon, email, giris_tarihi_saati, cikis_tarihi_saati, oda_no)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (ad, soyad, tc_pasaport_no, telefon, email, giris_tarihi_saati, cikis_tarihi_saati, oda_no))
        flash('Yeni misafir başarıyla kaydedildi!', 'success')
    
    db.commit()
    db.close()
    return redirect(url_for('kayitlar_sayfasi'))

@app.route('/kayitlar_sayfasi')
@login_required
def kayitlar_sayfasi():
    db = get_db()
    cursor = db.cursor()
    cursor.execute('SELECT * FROM misafirler ORDER BY giris_tarihi_saati DESC')
    ziyaretciler = cursor.fetchall()
    db.close()
    return render_template('kayitlar.html', ziyaretciler=ziyaretciler)

@app.route('/duzenle_ziyaretci/<int:misafir_id>', methods=['GET'])
@login_required
def duzenle_ziyaretci(misafir_id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute('SELECT * FROM misafirler WHERE id = ?', (misafir_id,))
    misafir = cursor.fetchone()
    db.close()

    if misafir:
        return render_template('ziyaretci_kayit.html', misafir=misafir)
    else:
        flash('Misafir bulunamadı.', 'danger')
        return redirect(url_for('kayitlar_sayfasi'))

@app.route('/sil_ziyaretci/<int:misafir_id>', methods=['POST']) 
@login_required
def sil_ziyaretci(misafir_id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute('DELETE FROM misafirler WHERE id = ?', (misafir_id,))
    db.commit()
    db.close()
    flash('Misafir kaydı başarıyla silindi.', 'success')
    return redirect(url_for('kayitlar_sayfasi'))

@app.route('/ziyaretci_filtreleme_sayfasi')
@login_required
def ziyaretci_filtreleme_sayfasi():
    return render_template('ziyaretci_filtreleme.html', ziyaretciler=[])

@app.route('/filtreleme', methods=['POST'])
@login_required
def filtreleme():
    ad = request.form.get('ad', '').strip()
    soyad = request.form.get('soyad', '').strip()
    giris_tarihi = request.form.get('giris_tarihi', '').strip()
    cikis_tarihi = request.form.get('cikis_tarihi', '').strip()

    db = get_db()
    cursor = db.cursor()

    query = "SELECT * FROM misafirler WHERE 1=1"
    params = []

    if ad:
        query += " AND ad LIKE ?"
        params.append('%' + ad + '%')
    if soyad:
        query += " AND soyad LIKE ?"
        params.append('%' + soyad + '%')
    if giris_tarihi:
        query += " AND giris_tarihi_saati LIKE ?" 
        params.append(giris_tarihi + '%')
    if cikis_tarihi:
        query += " AND cikis_tarihi_saati LIKE ?"
        params.append(cikis_tarihi + '%') 

    query += " ORDER BY giris_tarihi_saati DESC"

    cursor.execute(query, params)
    ziyaretciler = cursor.fetchall()
    db.close()
    return render_template('ziyaretci_filtreleme.html', ziyaretciler=ziyaretciler)


@app.route('/ziyaretci_yogunluk_sayfasi')
@login_required
def ziyaretci_yogunluk_sayfasi():
    db = get_db()
    cursor = db.cursor()
    
    # Günlük yoğunluk (sadece giriş tarihi baz alınarak)
    cursor.execute("SELECT DATE(giris_tarihi_saati) as tarih, COUNT(*) as sayi FROM misafirler GROUP BY tarih ORDER BY tarih DESC")
    # Row objelerini sözlüklere dönüştür
    gunluk_yogunluk = [dict(row) for row in cursor.fetchall()]

    # Haftalık yoğunluk (giriş tarihi baz alınarak)
    cursor.execute("SELECT STRFTIME('%Y-%W', giris_tarihi_saati) as hafta, COUNT(*) as sayi FROM misafirler GROUP BY hafta ORDER BY hafta DESC")
    # Row objelerini sözlüklere dönüştür
    haftalik_yogunluk = [dict(row) for row in cursor.fetchall()]

    # Aylık yoğunluk (giriş tarihi baz alınarak)
    cursor.execute("SELECT STRFTIME('%Y-%m', giris_tarihi_saati) as ay, COUNT(*) as sayi FROM misafirler GROUP BY ay ORDER BY ay DESC")
    # Row objelerini sözlüklere dönüştür
    aylik_yogunluk = [dict(row) for row in cursor.fetchall()]
    
    db.close()
    return render_template('ziyaretci_yogunluk.html', 
                           gunluk_yogunluk=gunluk_yogunluk,
                           haftalik_yogunluk=haftalik_yogunluk,
                           aylik_yogunluk=aylik_yogunluk)

@app.route('/export_json')
@login_required
def export_json():
    db = get_db()
    cursor = db.cursor()
    cursor.execute('SELECT * FROM misafirler')
    misafirler = cursor.fetchall()
    db.close()

    misafirler_list = []
    for misafir in misafirler:
        misafirler_list.append(dict(misafir))

    json_data = json.dumps(misafirler_list, indent=4, ensure_ascii=False)
    response = Response(json_data, mimetype='application/json')
    response.headers.set('Content-Disposition', 'attachment', filename='misafir_kayitlari.json')
    return response

# Web üzerinden kullanıcı JSON indirme rotası (admin.json)
# Bu rota artık users.json dosyası otomatik oluştuğu için fazlalık olabilir,
# ancak hala web'den indirme işlevi olarak tutuldu.
@app.route('/export_users_json')
@login_required
def export_users_json():
    db = get_db()
    cursor = db.cursor()
    # Şifre hash'lerini de dahil ederek kullanıcıları çek
    # GÜVENLİK RİSKİ: Bu, şifre hash'lerini web üzerinden indirmeye izin verir.
    cursor.execute('SELECT id, username, password FROM users')
    users = cursor.fetchall()
    db.close()

    users_list = []
    for user in users:
        users_list.append(dict(user)) 

    json_data = json.dumps(users_list, indent=4, ensure_ascii=False)
    response = Response(json_data, mimetype='application/json')
    response.headers.set('Content-Disposition', 'attachment', filename='admin.json') 
    return response

if __name__ == '__main__':
    init_db() 
    app.run(host="0.0.0.0" , port=int(os.environ.get("PORT", 5000)), debug=True)

