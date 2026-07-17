# Teklif Simülatörü (Quote Simulator)

Bu proje, havayolu müşterilerinden gelen uçak modifikasyon taleplerini (kabini, yapısal, aviyonik) analiz eden, eksik bilgileri belirleyen ve kurallara dayalı deterministik fiyat teklifleri hazırlayan bağımsız bir yapay zeka uygulamasıdır.

This project is a standalone AI-powered simulator that analyzes aircraft modification requests (cabin, structural, avionics) from airlines, detects information gaps, and generates deterministic pricing proposals.

---

## Proje Yapısı / Project Structure

```
teklif-sim/
├── README.md                 # Proje açıklaması ve çalıştırma yönergeleri
├── requirements.txt         # Gerekli kütüphaneler
├── data/
│   ├── rate_card.csv         # Saatlik mühendislik ücretleri (Sentetik veri)
│   ├── customer_classes.json # Müşteri sınıfları ve kâr marjı aralıkları
│   └── sample_emails/        # Değerlendirme için sentetik e-postalar (10 adet)
├── src/
│   ├── __init__.py
│   ├── llm_test.py           # Gemini API bağlantı test scripti
│   ├── extract.py            # E-posta metninden olguları çıkaran modül (LLM)
│   ├── gaps.py               # Eksik bilgileri kontrol eden modül (Pure Python)
│   ├── draft_email.py        # Eksik bilgileri talep eden e-posta taslağı (LLM + Fallback)
│   ├── pricing.py            # Deterministik fiyat hesaplama motoru (No LLM)
│   ├── summarize.py          # Tek sayfa teklif özeti hazırlayan modül
│   └── app.py                # Streamlit arayüzü
├── tests/
│   ├── __init__.py
│   ├── test_pricing.py       # Fiyat motoru testleri (Spec-First)
│   └── test_compliance.py    # Clean-room ve uyumluluk testleri
└── docs/
    ├── pricing_spec.md       # Fiyatlandırma spesifikasyonu (Manuel hesaplamalar)
    ├── test_catches.md       # TDD testleri tarafından yakalanan bug raporu
    └── report.md             # Genel mimari, 10 e-posta analizi ve rapor
```

---

## Kurulum / Installation

Sanal ortamı oluşturun ve bağımlılıkları yükleyin:
Create the virtual environment and install dependencies:

```bash
python -m venv .venv
.venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

---

## Ortam Değişkenleri / Environment Variables

Kök dizinde bir `.env` dosyası oluşturup Gemini API anahtarınızı ekleyin:
Create a `.env` file in the root directory and add your Gemini API key:

```env
GEMINI_API_KEY=your_gemini_api_key_here
```
