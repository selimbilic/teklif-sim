# TEKLİF-Sim (Aviation DOA Proposal Simulator)

[![Version](https://img.shields.io/badge/version-2.0.0-blue.svg)](CHANGELOG.md) [![Python](https://img.shields.io/badge/python-3.13-green.svg)](https://www.python.org/) [![EASA Part 21](https://img.shields.io/badge/EASA-Part%2021-red.svg)](https://www.easa.europa.eu/) [![Tests](https://img.shields.io/badge/tests-44%2F44%20passing-brightgreen.svg)](tests/)

**TEKLİF-Sim**, havayolu müşterilerinden gelen uçak modifikasyon taleplerini (kabin, yapısal, aviyonik) analiz eden, EASA Part 21 ve CS-25/CS-23 standartlarına göre regülasyon sınıflandırması yapan, eksik bilgileri belirleyen ve kurallara dayalı %100 deterministik fiyat teklifleri hazırlayan bağımsız bir yapay zeka ve mühendislik simülasyon uygulamasıdır.

*TEKLİF-Sim is a standalone AI and engineering simulation platform for aviation Design Organisation Approvals (DOA). It analyzes aircraft modification emails, classifies EASA Part 21 & CS-25/23 regulatory specifications, detects information gaps, and calculates 100% deterministic proposals.*

---

## 📌 Sürüm ve Versiyon Geçmişi / Version Release History

Projede **Semantic Versioning (SemVer - MAJOR.MINOR.PATCH)** standartları uygulanmakta olup, geçmiş sürümlere Git etiketleri (tags) üzerinden dilediğiniz an erişebilirsiniz.

| Sürüm / Version | Yayın Tarihi | Açıklama / Highlights | Git Tag |
| :--- | :--- | :--- | :--- |
| **`v2.0.0`** (Mevcut) | 2026-07-28 | **EASA Compliance & Aviation Mathematics Overhaul:** DO-178C Annex A 5 kademeli DAL emniyet çarpanları (A=2.4x - E=1.0x), NRE + Wright %80 learning curve filo ölçekleme, CS-23 tüm rollere azaltma, mod tipine özel test & malzeme payı, risk bazlı contingency (%4-%15), EWIS & ICA saatleri, AOG/Rush sürşarjı ve 44/44 birim testleri. | [`v2.0.0`](https://github.com/selimbilic/teklif-sim/releases/tag/v2.0.0) |
| **`v1.3.0`** | 2026-07-27 | **Aviation Precision & Safety DAL Wiring Release:** ARP4761 DAL emniyet çarpanının fiyatlandırmaya bağlanması, esnek DAL metin ayrıştırma, CS-23/CS-25 adam-saat katsayıları, fleet_size <= 0 veri doğrulaması ve 30/30 birim testleri. | [`v1.3.0`](https://github.com/selimbilic/teklif-sim/releases/tag/v1.3.0) |
| **`v1.2.0`** | 2026-07-27 | **Streamlit Action Button Execution Guard:** Buton tıklama bağımlılığı (`analyze_click`), LLM Extraction `@st.cache_data` önbellekleme, AST unused button compliance testi ve Headless Streamlit AppTest paket entegrasyonu. | [`v1.2.0`](https://github.com/selimbilic/teklif-sim/releases/tag/v1.2.0) |
| **`v1.1.0`** | 2026-07-24 | EASA Part 21.A.91 (Minor vs Major STC) sınıflandırması, **CS-25 & CS-23** sabit kanat sertifikasyon motoru, ARP4761 emniyet DAL seviyeleri (DAL A-E), 7 özel proje kategorisi, **Gaps-Locked Fiyat Koruması** ve 10 sentetik test senaryosu. | [`v1.1.0`](https://github.com/selimbilic/teklif-sim/releases/tag/v1.1.0) |
| **`v1.0.0`** | 2026-07-23 | İlk temel sürüm (Baseline Release). Deterministik fiyat motoru (`src/pricing.py`), Gemini 3.1 Flash Lite bilgi çıkarma (`src/extract.py`), DOA adam/saat kestirim motoru, 20/20 test ve Kurumsal Light Streamlit paneli. | [`v1.0.0`](https://github.com/selimbilic/teklif-sim/releases/tag/v1.0.0) |

---

### 🔄 İstediğiniz Versiyona Geçiş Yapma (Git Checkout)

Projeyi dilediğiniz sürüm durumunda çalıştırmak için aşağıdaki Git komutlarını kullanabilirsiniz:

```bash
# Versiyon 2.0.0 (Güncel Sürüm) durumuna dönmek için:
git checkout main

# Versiyon 1.3.0 durumuna dönmek için:
git checkout v1.3.0

# Versiyon 1.2.0 durumuna dönmek için:
git checkout v1.2.0

# Versiyon 1.1.0 durumuna dönmek için:
git checkout v1.1.0

# Versiyon 1.0.0 (İlk Temel Sürüm) durumuna dönmek için:
git checkout v1.0.0
```

Detaylı değişiklik günlüğü için [CHANGELOG.md](CHANGELOG.md) dosyasını inceleyebilirsiniz.

---

## 🏗️ Proje Yapısı / Project Structure

```text
teklif-sim/
├── CHANGELOG.md              # Sürüm ve değişiklik günlüğü (v1.0.0 - v2.0.0)
├── README.md                 # Proje açıklaması, versiyonlar ve çalıştırma yönergeleri
├── requirements.txt          # Gerekli kütüphaneler
├── data/
│   ├── rate_card.csv         # Saatlik mühendislik ücretleri (Sentetik veri)
│   ├── customer_classes.json # Müşteri sınıfları ve kâr marjı aralıkları
│   └── sample_emails/        # Değerlendirme için sentetik e-postalar (6 adet tam kapsama senaryosu)
├── src/
│   ├── __init__.py
│   ├── __version__.py        # Merkezi versiyon tanımı (v2.0.0)
│   ├── llm_test.py           # Gemini API bağlantı test scripti
│   ├── extract.py            # E-posta metninden olguları çıkaran modül (LLM - Gemini 3.1 Flash Lite)
│   ├── gaps.py               # Eksik bilgileri kontrol eden modül (Pure Python)
│   ├── estimation.py         # DOA Adam/Saat, EASA Part 21 ve CS-25/23 Kestirim Motoru
│   ├── draft_email.py        # Eksik bilgileri talep eden e-posta taslağı (LLM + Fallback)
│   ├── pricing.py            # %100 Deterministik fiyat hesaplama motoru (No LLM, Pure Python)
│   ├── summarize.py          # Tek sayfa teklif ve EASA doküman paketi hazırlayan modül
│   └── app.py                # Streamlit Kurumsal Light Arayüzü
├── tests/
│   ├── __init__.py
│   ├── test_pricing.py       # Fiyat motoru testleri (15 test)
│   ├── test_estimation.py    # CS-25/23, Part 21 ve Adam/Saat testleri (20 test)
│   ├── test_compliance.py    # AST izolasyon, 50x determinizm ve clean-room testleri (5 test)
│   └── test_ui.py            # Headless Streamlit UI testleri (4 test)
└── docs/
    ├── pricing_spec.md       # Fiyatlandırma spesifikasyonu
    ├── test_catches.md       # TDD test raporu
    └── report.md             # Mimari ve analiz raporu
```

---

## 🚀 Kurulum ve Çalıştırma / Installation & How to Run

### 1. Sanal Ortamı Hazırlama
```bash
python -m venv .venv
.\.venv\Scripts\activate      # Windows
pip install -r requirements.txt
```

### 2. Ortam Değişkenleri (.env)
Kök dizinde bir `.env` dosyası oluşturup Gemini API anahtarınızı ekleyin:
```env
GEMINI_API_KEY=your_gemini_api_key_here
```

### 3. Test Suitini Çalıştırma (44/44 PASS)
```bash
.\.venv\Scripts\pytest.exe
```

### 4. Web Arayüzünü Ayağa Kaldırma (Streamlit)
```bash
.\.venv\Scripts\streamlit.exe run src/app.py
```
Arayüze tarayıcınızdan **http://localhost:8501** adresi üzerinden erişebilirsiniz.

---

## 🛡️ Mimari Kurallar ve Guardrail'ler
1. **Deterministik Motor İzolasyonu (`src/pricing.py`):** %100 Saf Python. İçerisinde kesinlikle LLM, rastgele sayı (`random`), ağ erişimi veya `datetime.now()` kullanılamaz. AST static analysis testleri ile denetlenmektedir.
2. **Eksik Bilgi Koruması (Pricing Lock):** Müşteri e-postasında kritik eksik bilgi (uçak modeli, filo sayısı vb.) bulunduğunda sistem sahte fiyat üretmez; teklif kilitlenir ve müşteriye gönderilecek e-posta taslağı öne çıkarılır.
3. **Clean-Room Mühendislik:** Gerçek şirket veya havayolu isimleri kesinlikle kullanılmaz; sentetik havayolu isimleri (`Flagship Air`, `Anadolu Jet`, `Global Cargo` vb.) kullanılır.
