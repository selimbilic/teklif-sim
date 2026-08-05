# TEKLİF-Sim (Aviation DOA Proposal Simulator)

[![Version](https://img.shields.io/badge/version-3.0.0-blue.svg)](CHANGELOG.md) [![Python](https://img.shields.io/badge/python-3.13-green.svg)](https://www.python.org/) [![EASA Part 21](https://img.shields.io/badge/EASA-Part%2021-red.svg)](https://www.easa.europa.eu/) [![Tests](https://img.shields.io/badge/tests-68%2F68%20passing-brightgreen.svg)](tests/)

**TEKLİF-Sim**, havayolu müşterilerinden gelen uçak modifikasyon taleplerini (kabin, yapısal, aviyonik) analiz eden, EASA Part 21 ve CS-25/CS-23 standartlarına göre regülasyon sınıflandırması yapan, eksik bilgileri belirleyen ve kurallara dayalı %100 deterministik fiyat teklifleri hazırlayan bağımsız bir yapay zeka ve mühendislik simülasyon uygulamasıdır.

*TEKLİF-Sim is a standalone AI and engineering simulation platform for aviation Design Organisation Approvals (DOA). It analyzes aircraft modification emails, classifies EASA Part 21 & CS-25/23 regulatory specifications, detects information gaps, and calculates 100% deterministic proposals.*

> [!WARNING]
> **🔒 Veri Gizliliği ve Güvenlik Uyarısı / Privacy & Data Security Disclaimer:**
> Bu uygulama, gelen e-postaları ve yüklenen dokümanları analiz etmek için **Google Gemini Pro API** servisini kullanmaktadır. KVKK, GDPR ve kurumsal gizlilik politikaları gereği, istemci tarafında **Microsoft Presidio** ile PII ve hassas veriler yerel CPU üzerinde anonimleştirilmektedir. Yine de son ortamda yalnızca sentetik veya yetkilendirilmiş veriler kullanılması önerilir.

---

## 📌 Sürüm ve Versiyon Geçmişi / Version Release History

Projede **Semantic Versioning (SemVer - MAJOR.MINOR.PATCH)** standartları uygulanmakta olup, geçmiş sürümlere Git etiketleri (tags) üzerinden dilediğiniz an erişebilirsiniz.

| Sürüm / Version | Yayın Tarihi | Açıklama / Highlights | Git Tag |
| :--- | :--- | :--- | :--- |
| **`v3.0.0`** (Mevcut) | 2026-08-05 | **Gemini Pro Enterprise Hybrid Release (Free Tech Stack & REST API):** Çok biçimli doküman yükleme (PDF, XLSX, DOCX, TXT), Microsoft Presidio yerel PII anonimleştirme, Gemini Pro multimodel analiz, canlı ECB/TCMB ücretsiz kur çevirici (`USD`, `EUR`, `GBP`, `TRY`), SQLAlchemy ORM veritabanı kalıcılığı & CRM geçmiş teklif arama, FastAPI REST servis katmanı, Monte-Carlo risk simülasyonu (P10/P50/P90), ReportLab PDF ve python-docx Word kurumsal teklif çıktısı ve %100 yeşil 68/68 birim testleri. | [`v3.0.0`](https://github.com/selimbilic/teklif-sim/releases/tag/v3.0.0) |
| **`v2.1.0`** | 2026-08-03 | **Enterprise Security, Config & Aviation Engine Release:** Harici YAML konfigürasyon (`config/settings.yaml`), GitHub Actions CI/CD pipeline, `requirements-lock.txt`, merkezi `logger.py`, prompt injection süzgeci & semantik değer sınır doğrulaması, sliding window `rate_limiter.py`, EWIS parametrik uçak karmaşıklık modeli ve 52/52 birim testleri. | [`v2.1.0`](https://github.com/selimbilic/teklif-sim/releases/tag/v2.1.0) |
| **`v2.0.1`** | 2026-07-28 | **Security & Pricing Engine Hardening:** `app.py` üzerinde HTML Injection / XSS koruması (`html.escape`), kamuya açık LLM veri gizliliği uyarısı, `pricing.py` içinde bilinmeyen rol doğrulama hatası (`ValueError`), `competitive` marjının taban marja clamp edilmesi ve 46/46 birim testleri. | [`v2.0.1`](https://github.com/selimbilic/teklif-sim/releases/tag/v2.0.1) |
| **`v2.0.0`** | 2026-07-28 | **EASA Compliance & Aviation Mathematics Overhaul:** DO-178C Annex A 5 kademeli DAL emniyet çarpanları (A=2.4x - E=1.0x), NRE + Wright %80 learning curve filo ölçekleme, CS-23 tüm rollere azaltma, mod tipine özel test & malzeme payı, risk bazlı contingency (%4-%15), EWIS & ICA saatleri, AOG/Rush sürşarjı ve 44/44 birim testleri. | [`v2.0.0`](https://github.com/selimbilic/teklif-sim/releases/tag/v2.0.0) |
| **`v1.3.0`** | 2026-07-27 | **Aviation Precision & Safety DAL Wiring Release:** ARP4761 DAL emniyet çarpanının fiyatlandırmaya bağlanması, esnek DAL metin ayrıştırma, CS-23/CS-25 adam-saat katsayıları, fleet_size <= 0 veri doğrulaması ve 30/30 birim testleri. | [`v1.3.0`](https://github.com/selimbilic/teklif-sim/releases/tag/v1.3.0) |
| **`v1.2.0`** | 2026-07-27 | **Streamlit Action Button Execution Guard:** Buton tıklama bağımlılığı (`analyze_click`), LLM Extraction `@st.cache_data` önbellekleme, AST unused button compliance testi ve Headless Streamlit AppTest paket entegrasyonu. | [`v1.2.0`](https://github.com/selimbilic/teklif-sim/releases/tag/v1.2.0) |
| **`v1.1.0`** | 2026-07-24 | EASA Part 21.A.91 (Minor vs Major STC) sınıflandırması, **CS-25 & CS-23** sabit kanat sertifikasyon motoru, ARP4761 emniyet DAL seviyeleri (DAL A-E), 7 özel proje kategorisi, **Gaps-Locked Fiyat Koruması** ve 10 sentetik test senaryosu. | [`v1.1.0`](https://github.com/selimbilic/teklif-sim/releases/tag/v1.1.0) |
| **`v1.0.0`** | 2026-07-23 | İlk temel sürüm (Baseline Release). Deterministik fiyat motoru (`src/pricing.py`), Gemini bilgi çıkarma (`src/extract.py`), DOA adam/saat kestirim motoru, 20/20 test ve Kurumsal Light Streamlit paneli. | [`v1.0.0`](https://github.com/selimbilic/teklif-sim/releases/tag/v1.0.0) |

---

### 🔄 İstediğiniz Versiyona Geçiş Yapma (Git Checkout)

Projeyi dilediğiniz sürüm durumunda çalıştırmak için aşağıdaki Git komutlarını kullanabilirsiniz:

```bash
# Versiyon 3.0.0 (Güncel Sürüm) durumuna dönmek için:
git checkout main

# Versiyon 2.1.0 durumuna dönmek için:
git checkout v2.1.0

# Versiyon 2.0.1 durumuna dönmek için:
git checkout v2.0.1

# Versiyon 2.0.0 durumuna dönmek için:
git checkout v2.0.0
```

Detaylı değişiklik günlüğü için [CHANGELOG.md](CHANGELOG.md) dosyasını inceleyebilirsiniz.

---

## 🏗️ Proje Yapısı / Project Structure

```text
teklif-sim/
├── .github/
│   └── workflows/
│       └── ci.yml            # GitHub Actions CI/CD otomasyonu (Pytest multi-version)
├── config/
│   └── settings.yaml         # Harici konfigürasyon parametreleri
├── CHANGELOG.md              # Sürüm ve değişiklik günlüğü (v1.0.0 - v3.0.0)
├── README.md                 # Proje açıklaması, versiyonlar ve çalıştırma yönergeleri
├── requirements.txt          # Gerekli kütüphaneler (FastAPI, Presidio, ReportLab, docx)
├── data/
│   ├── rate_card.csv         # Saatlik mühendislik ücretleri (Sentetik veri)
│   ├── customer_classes.json # Müşteri sınıfları ve kâr marjı aralıkları
│   └── teklif_sim.db         # SQLite ilişkisel veritabanı kalıcılığı (v3.0.0)
├── src/
│   ├── __init__.py
│   ├── __version__.py        # Merkezi versiyon tanımı (v3.0.0)
│   ├── config.py             # Harici YAML konfigürasyon yükleyici
│   ├── logger.py             # Merkezi yapılandırılmış loglama modülü
│   ├── parser.py             # PDF/XLSX/DOCX/TXT çok biçimli doküman ayrıştırıcı (v3.0.0)
│   ├── privacy.py            # Microsoft Presidio yerel PII maskeleme modülü (v3.0.0)
│   ├── extract.py            # Gemini Pro multimodel bilgi çıkarma ve model fallback (v3.0.0)
│   ├── forex.py              # Ücretsiz ECB/TCMB açık XML canlı döviz kuru motoru (v3.0.0)
│   ├── database.py           # SQLAlchemy ORM veritabanı kayıt ve CRM geçmişi (v3.0.0)
│   ├── api.py                # FastAPI REST API servis katmanı & OpenAPI docs (v3.0.0)
│   ├── simulation.py         # Monte-Carlo P10/P50/P90 risk mühendisliği simülasyonu (v3.0.0)
│   ├── export.py             # EASA Part 21 formatlı ReportLab PDF & Word doküman çıktısı (v3.0.0)
│   ├── gaps.py               # Eksik bilgileri kontrol eden modül
│   ├── estimation.py         # DOA Adam/Saat, EASA Part 21 ve CS-25/23 Kestirim Motoru
│   ├── draft_email.py        # Eksik bilgileri talep eden e-posta taslağı
│   ├── pricing.py            # %100 Deterministik fiyat hesaplama motoru (No LLM, Pure Python)
│   ├── summarize.py          # Tek sayfa teklif özet hazırlama modülü
│   └── app.py                # Streamlit Kurumsal Web Portalı (v3.0.0)
├── tests/
│   ├── test_pricing.py       # Fiyat motoru testleri
│   ├── test_estimation.py    # CS-25/23, Part 21 ve Adam/Saat testleri
│   ├── test_compliance.py    # AST izolasyon, determinizm ve clean-room testleri
│   ├── test_ui.py            # Headless Streamlit UI testleri
│   ├── test_v210_features.py # v2.1.0 güvenlik ve EWIS testleri
│   ├── test_v300_phase1.py   # v3.0.0 Parser, PII ve Gemini Pro testleri
│   ├── test_v300_phase2.py   # v3.0.0 ECB Forex ve DB CRUD testleri
│   ├── test_v300_phase3.py   # v3.0.0 FastAPI REST API entegrasyon testleri
│   └── test_v300_phase4_5.py # v3.0.0 Monte-Carlo ve PDF/DOCX export testleri
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
GEMINI_MODEL=gemini-1.5-flash
```

### 3. Test Suitini Çalıştırma (68/68 PASS)
```bash
.\.venv\Scripts\pytest
```

### 4. Web Arayüzünü Ayağa Kaldırma (Streamlit)
```bash
.\.venv\Scripts\streamlit.exe run src/app.py
```
Arayüze tarayıcınızdan **http://localhost:8501** adresi üzerinden erişebilirsiniz.

### 5. FastAPI REST API Servisini Ayağa Kaldırma
```bash
.\.venv\Scripts\uvicorn.exe src.api:app --reload --port 8000
```
Swagger UI dokümantasyonuna **http://localhost:8000/docs** adresi üzerinden erişebilirsiniz.

---

## 🛡️ Mimari Kurallar ve Guardrail'ler
1. **Deterministik Motor İzolasyonu (`src/pricing.py`):** %100 Saf Python. İçerisinde kesinlikle LLM, rastgele sayı (`random`), ağ erişimi veya `datetime.now()` kullanılamaz. AST static analysis testleri ile denetlenmektedir.
2. **Eksik Bilgi Koruması (Pricing Lock):** Müşteri e-postasında kritik eksik bilgi (uçak modeli, filo sayısı vb.) bulunduğunda sistem sahte fiyat üretmez; teklif kilitlenir ve müşteriye gönderilecek e-posta taslağı öne çıkarılır.
3. **Clean-Room Mühendislik:** Gerçek şirket veya havayolu isimleri kesinlikle kullanılmaz; sentetik havayolu isimleri (`Flagship Air`, `Anadolu Jet`, `Global Cargo` vb.) kullanılır.
4. **Havacılık Sertifikasyon Kapsamı:** Kapsam **sadece sabit kanatlı uçaklarla (CS-25 / CS-23)** kısıtlıdır. Döner kanatlı hava araçları (CS-27 / CS-29 Helikopter) kapsam dışıdır.

---

## 📐 Mimari Karar Kaydı (Architecture Decision Record - ADR)

* **ADR-01 - ADR-12:** (Önceki versiyon kararları: Deterministik motor ayrımı, Wright %80 öğrenme eğrisi, Streamlit hot-reload, Pricing Lock guardrail, DO-178C 5 kademeli DAL emniyet çarpanları, Harici YAML konfigürasyon, API Rate Limiting).
* **ADR-13: %100 Ücretsiz Teknolojik Mimari Seçimi:** Ağ ve bulut bağımlılığı olan ücretli servisler yerine 0 TL maliyetli açık kaynaklı kütüphaneler tercih edilmiştir: GCP DLP yerine **Microsoft Presidio**, ticari döviz API'leri yerine **Avrupa Merkez Bankası (ECB) public XML**, ücretli cloud DB yerine **SQLite / PostgreSQL SQLAlchemy ORM**.
* **ADR-14: Yerel PII Anonimleştirme ve Gemini Pro Hibrit Katmanı (`src/privacy.py`):** Müşteri verileri Gemini Pro API'ye gönderilmeden önce istemci tarafında yerel CPU üzerinde sansürlenmekte, böylece KVKK/GDPR ihlali engellenmektedir.
* **ADR-15: FastAPI Kurumsal Entegrasyon Katmanı (`src/api.py`):** ERP/SAP sistemleriyle doğrudan etkileşim kurulabilmesi amacıyla REST API mimarisine geçilmiştir.
* **ADR-16: Monte-Carlo Risk Mühendisliği Simülasyonu (`src/simulation.py`):** Proje belirsizliklerini P10 (İyimser), P50 (Beklenen) ve P90 (Risk Payı) istatistiksel güven aralıklarıyla hesaplamak için 1,000 çalıştırmalı Triangular Monte-Carlo simülatörü eklenmiştir.
* **ADR-17: EASA Part 21 Doküman İhracat Motoru (`src/export.py`):** Üretilen tekliflerin kurumsal ve resmi standartlarda indirilebilmesi için ReportLab PDF ve python-docx Word ihracat altyapısı kurulmuştur.
