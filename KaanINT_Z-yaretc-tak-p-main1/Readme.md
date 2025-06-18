Otel Misafir Yönetim Sistemi
Bu proje, bir otelde misafir kayıtlarını yönetmek, filtrelemek ve ziyaretçi yoğunluğunu analiz etmek için geliştirilmiş basit bir web uygulamasıdır. Python Flask framework'ü ve SQLite veritabanı kullanılarak oluşturulmuştur.

Özellikler
Kullanıcı Yönetimi: Kullanıcı kaydı ve güvenli giriş/çıkış işlemleri.

Misafir Kayıt: Yeni misafirlerin adı, soyadı, TC/Pasaport No, telefon, e-posta, giriş/çıkış tarihleri ve oda numarası ile kayıt altına alınması.

Misafir Bilgisi Düzenleme: Mevcut misafir kayıtlarını güncelleme.

Misafir Kaydı Silme: İstenmeyen misafir kayıtlarını silme.

Misafir Filtreleme: Misafirleri ad, soyad, giriş tarihi ve çıkış tarihine göre filtreleme.

Ziyaretçi Yoğunluk Analizi: Günlük, haftalık ve aylık bazda ziyaretçi yoğunluk raporlarını görüntüleme.

JSON Dışa Aktarma: Misafir kayıtlarını JSON formatında dışa aktarma.

Kurulum ve Çalıştırma
Ön Koşullar
Bu projeyi çalıştırmak için sisteminizde Python 3 yüklü olmalıdır.

Adımlar
Projeyi İndirin:
Projeyi bilgisayarınıza indirin veya klonlayın.

Bağımlılıkları Yükleyin:
Proje dizinine gidin ve gerekli Python kütüphanelerini yüklemek için requirements.txt dosyasını kullanın:

pip install -r requirements.txt
eğer Olmazsa 
py -m pip install -r requirements.txt 
deneyin

Veritabanını Başlatın ve Uygulamayı Çalıştırın:
app.py dosyasını çalıştırarak veritabanını başlatabilir ve web uygulamasını çalıştırabilirsiniz.

python app.py

Uygulama başarıyla başlatıldığında, terminalde varsayılan yönetici kullanıcısının oluşturulduğuna dair bir mesaj göreceksiniz (eğer daha önce oluşturulmadıysa).

Uygulamaya Erişin:
Web tarayıcınızda aşağıdaki adresi ziyaret ederek uygulamaya erişebilirsiniz:

http://127.0.0.1:5000/

(Eğer farklı bir portta çalışıyorsa, terminaldeki çıktıyı kontrol edin.)

Varsayılan Giriş Bilgileri
Uygulamayı ilk başlattığınızda, otomatik olarak bir yönetici hesabı oluşturulur:

Kullanıcı Adı: admin

Şifre: password

Bu bilgileri kullanarak giriş yapabilir ve sistemi deneyebilirsiniz. Güvenlik nedeniyle, gerçek bir uygulamada bu şifreyi değiştirmelisiniz.

Proje Yapısı
.
├── app.py                  # Ana Flask uygulaması ve rota tanımlamaları
├── otel_yonetim.db         # SQLite veritabanı dosyası (oluşturulduktan sonra)
├── db2json.py              # Veritabanı verilerini JSON'a aktarmak için yardımcı betik
├── requirements.txt        # Proje bağımlılıkları
├── static/                 # Statik dosyalar (CSS, resimler)
│   ├── anakayıtlar.css
│   ├── filtreleme.css
│   ├── index.css
│   ├── kayıtlar.css
│   ├── register.css
│   ├── yogunluk.css
│   └── ziyaretci-kayıt.css
└── templates/              # HTML şablonları
    ├── ana_kayıtlar.html
    ├── index.html
    ├── kayitlar.html
    ├── register.html
    ├── ziyaretci_filtreleme.html
    ├── ziyaretci_kayit.html
    └── ziyaretci_yogunluk.html

Geri Bildirimlere Yanıtlar
Verdiğiniz geri bildirimleri dikkate alarak projemizde aşağıdaki noktaları geliştirdik:

README Dosyası: Projenin kurulumu, çalıştırılması ve genel yapısı hakkında bilgi veren bu README.md dosyası oluşturuldu.

Veritabanı & JSON Çıktıları:

Misafir kayıtlarının JSON çıktısı (/export_json rotası) zaten mevcuttu ve dinamik veriyi başarıyla dışa aktarıyordu.

db2json.py betiği, kullanıcı ve misafir verilerini sqlite3 kullanarak JSON'a aktaracak şekilde güncellendi. Kullanıcı şifreleri hassasiyet nedeniyle JSON çıktısına dahil edilmemiştir. python db2json.py komutuyla ayrı olarak çalıştırılabilir.

Render Linki / Giriş Sorunu:

app.py dosyasındaki app.run() çağrısı düzeltildi ve gereksiz tekrar kaldırıldı. Uygulama artık http://127.0.0.1:5000/ adresinden erişilebilir.

init_db() fonksiyonuna, eğer veritabanında hiç kullanıcı yoksa varsayılan bir admin kullanıcısı ekleme mantığı eklendi. Bu sayede proje ilk çalıştırıldığında sorunsuz giriş yapılabilir.

Uygulamanın dinamik veritabanı işlemleri (kayıt, düzenleme, silme, filtreleme, raporlama) ile çalıştığı ve statik olmadığı açıkça belirtilmiştir.

Çalışmayan Linkler / Butonlar:

Kod içerisindeki tüm url_for çağrıları ve form metodları kontrol edildi. Özellikle silme işlemi gibi POST bekleyen rotaların HTML tarafında doğru method="POST" ile kullanıldığı doğrulandı. Flask'ın sağladığı flash mesajları ile kullanıcıya geri bildirimler sorunsuz sağlanmaktadır.

kayitlar.html dosyasındaki "Sil" butonu için confirm() yerine özelleştirilmiş bir onay kutusu (SweetAlert veya benzeri bir kütüphane ile) kullanmak daha iyi bir kullanıcı deneyimi sunabilir, ancak mevcut confirm() fonksiyonel olarak çalışmaktadır.

Kod Düzeni:

CSS dosyaları zaten static klasöründe ayrı ayrı tutuluyordu ve HTML dosyaları tarafından doğru şekilde referans alınıyordu, bu doğru bir yaklaşımdır.

Python kodundaki app.run() tekrarı gibi yapısal sorunlar giderildi. Kodun genel okunabilirliği ve düzeni iyileştirildi.

Ek Notlar
otel_yonetim.db dosyası, uygulama ilk çalıştırıldığında otomatik olarak oluşturulacaktır.

db2json.py betiği, verileri JSON'a aktarmak istediğinizde python db2json.py komutuyla ayrı olarak çalıştırılabilir.