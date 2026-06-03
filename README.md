# AnonimTR Bot 🤖

> **"Kimliğin Değil, Sohbetin Önemli."**

Gelişmiş anonim Telegram sohbet botu. Kullanıcılar kimliklerini paylaşmadan yeni insanlarla tanışabilir.

## 🚀 Özellikler

- 🔒 **Tam Anonimlik** — Kullanıcı adı, telefon ve kimlik paylaşılmaz
- 🌐 **6 Dil** — Türkçe, İngilizce, Almanca, Fransızca, Arapça, Rusça
- 🤝 **Akıllı Eşleştirme** — Dil, premium öncelik bazlı
- 📱 **Tüm Medya** — Metin, fotoğraf, video, ses, GIF, sticker, dosya
- 🛡️ **Güvenlik** — Spam, flood, reklam ve küfür koruması
- 👑 **Premium Sistemi** — Öncelikli eşleşme, VIP rozet
- ⭐ **Seviye/XP** — 10 seviye, rozet sistemi
- 🔗 **Referans** — Davet linki, XP ödülü
- 📊 **İstatistik** — Kişisel ve genel istatistikler
- 👮 **Admin Paneli** — Ban, duyuru, kullanıcı yönetimi
- 📢 **Kanal Kontrolü** — Zorunlu kanal üyeliği

## 📋 Kurulum

### Gereksinimler

- Python 3.10+
- MongoDB Atlas veya yerel MongoDB
- Telegram Bot Token (@BotFather)

### Adımlar

```bash
# Bağımlılıkları yükle
pip install -r requirements.txt

# Ortam değişkenlerini ayarla
export TELEGRAM_BOT_TOKEN="your_token"
export MONGODB_URI="your_mongodb_uri"
export GEMINI_API_KEY="your_gemini_key"
export ADMIN_IDS="123456789,987654321"

# Botu çalıştır
python bot.py
```

### Docker ile Çalıştırma

```bash
docker build -t anonimtr-bot .
docker run -d \
  -e TELEGRAM_BOT_TOKEN=your_token \
  -e MONGODB_URI=your_mongodb_uri \
  -e ADMIN_IDS=your_admin_id \
  --name anonimtr-bot \
  anonimtr-bot
```

## 🎮 Kullanıcı Komutları

| Komut | Açıklama |
|-------|----------|
| `/start` | Botu başlatır |
| `/profil` | Profil bilgilerini gösterir |
| `/sohbetbul` | Yeni sohbet arar |
| `/yenile` | Yeni eşleşme bulur |
| `/bitir` | Aktif sohbeti sonlandırır |
| `/engelle` | Karşı tarafı engeller |
| `/sikayet` | Karşı tarafı şikayet eder |
| `/premium` | Premium bilgisi |
| `/referans` | Davet bağlantısı |
| `/ayarlar` | Ayarlar |
| `/dil` | Dil değiştir |
| `/istatistik` | İstatistikler |
| `/yardim` | Yardım menüsü |

## 👑 Admin Komutları

| Komut | Açıklama |
|-------|----------|
| `/admin` | Admin paneli |
| `/ban <id> [sebep]` | Kullanıcı yasakla |
| `/unban <id>` | Yasak kaldır |
| `/kullanici <id>` | Kullanıcı bilgileri |
| `/duyuru <mesaj>` | Tüm kullanıcılara duyuru |
| `/premiumver <id>` | Premium ver |
| `/premiumal <id>` | Premium kaldır |
| `/karaliste <id>` | Kara listeye al |
| `/karalistedenkaldir <id>` | Kara listeden çıkar |
| `/istatistik` | Genel istatistikler |

## ⚙️ Ortam Değişkenleri

| Değişken | Zorunlu | Açıklama |
|----------|---------|----------|
| `TELEGRAM_BOT_TOKEN` | ✅ | BotFather'dan alınan token |
| `MONGODB_URI` | ✅ | MongoDB bağlantı adresi |
| `GEMINI_API_KEY` | ❌ | Google Gemini API anahtarı |
| `ADMIN_IDS` | ❌ | Admin Telegram ID'leri (virgülle ayrılmış) |

## 🗄️ Veritabanı Yapısı

MongoDB koleksiyonları:
- `users` — Kullanıcı profilleri
- `chats` — Sohbet geçmişi
- `queue` — Eşleşme bekleme kuyruğu
- `reports` — Şikayetler
- `blacklist` — Kara liste
- `stats` — Günlük istatistikler

## 📁 Proje Yapısı

```
telegram-bot/
├── bot.py              # Ana giriş noktası
├── config.py           # Konfigürasyon
├── database.py         # MongoDB işlemleri
├── requirements.txt    # Python bağımlılıkları
├── handlers/           # Komut işleyicileri
│   ├── start.py        # /start, kanal kontrolü, dil
│   ├── chat.py         # Anonim sohbet sistemi
│   ├── profile.py      # Profil
│   ├── stats.py        # İstatistikler
│   ├── settings.py     # Ayarlar
│   ├── premium.py      # Premium sistemi
│   ├── referral.py     # Referans sistemi
│   └── admin.py        # Admin paneli
├── middlewares/        # Middleware'ler
│   ├── channel_check.py    # Kanal üyelik kontrolü
│   └── flood_control.py    # Flood koruması
├── utils/              # Yardımcı araçlar
│   ├── keyboards.py    # Klavyeler
│   └── filters.py      # İçerik filtreleri
└── locales/            # Dil dosyaları
    ├── tr.py  en.py  de.py
    ├── fr.py  ar.py  ru.py
    └── __init__.py
```

## 📄 Lisans

MIT License — AnonimTR Bot
