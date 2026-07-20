# Fiyatlandırma Spesifikasyonu (Pricing Specification)

Bu doküman, `src/pricing.py` fiyatlandırma motorunun test edilmesinde kullanılacak olan elle hesaplanmış test senaryolarını (test cases) tanımlar. Fiyat motoru geliştirilmeden önce bu spesifikasyon referans alınarak testler yazılacaktır.

---

## 1. Fiyatlandırma Kuralları (Pricing Rules)

### Mühendislik Saat Ücretleri (Labor Rates)
`data/rate_card.csv` dosyasından okunur:
- `cabin_design_engineer`: $95.00
- `structural_engineer`: $110.00
- `avionics_design_engineer`: $105.00
- `certification_engineer`: $80.00
- `project_manager`: $120.00

### Müşteri Sınıfları ve Marjları (Margin Bands)
`data/customer_classes.json` dosyasından okunur:
- **Flagship (Flagship & Internal):** min %5 - max %15 (Varsayılan: %10)
- **Partner (Alliance & Partner):** min %15 - max %30 (Varsayılan: %22)
- **Third Party (Standard Third-Party):** min %30 - max %50 (Varsayılan: %40)

### Strateji Eşleme Kuralları (Strategy Mapping Rules)
Metinsel strateji girdileri şu şekilde eşleştirilir:
- **"cheapest possible" / "cheapest" / "en ucuz":** Kâr marjı alt sınırı (**floor** - `min_margin`).
- **"premium" / "rush" / "AOG" / "acil" / "hızlı":** Kâr marjı üst sınırı (**ceiling** - `max_margin`).
- **"competitive" / "rekabetçi":** Varsayılan marjın 2 puan altı (`default_margin - 0.02`).
- **Diğer / Eşleşmeyen:** Varsayılan marj (**default** - `default_margin`).

### Sabit Ücretler (Fixed Fees)
- **Testing & Certification Fee:** Sabit $1,500.00
- **Material Allowance:** Uçak başına $500.00 (Miktar × $500.00)
- **Contingency (Beklenmedik Durum Payı):** Temel İşçilik Ücretinin %5'i (pre-margin)

---

## 2. Elle Hesaplanmış Test Vakaları (Hand-Calculated Test Cases)

### Vaka 1: Flagship Müşteri - En Ucuz Strateji - 5 Uçak
- **Saatler:** Cabin: 80, Structural: 40, Certification: 20, PM: 10
- **Hesaplama:**
  - Cabin Labor: 80 × $95 = $7,600
  - Structural Labor: 40 × $110 = $4,400
  - Certification Labor: 20 × $80 = $1,600
  - PM Labor: 10 × $120 = $1,200
  - **Temel İşçilik (Base Labor):** $7,600 + $4,400 + $1,600 + $1,200 = $14,800.00
  - **Kâr Marjı:** %5 (Flagship floor) -> $14,800 × 0.05 = $740.00
  - **Contingency:** %5 of Base Labor -> $14,800 × 0.05 = $740.00
  - **Testing Fee:** $1,500.00
  - **Material Allowance:** 5 × $500 = $2,500.00
- **Beklenen Toplam:** $14,800 + $740 + $740 + $1,500 + $2,500 = **$20,280.00**

### Vaka 2: Flagship Müşteri - Rekabetçi Strateji - 5 Uçak
- **Saatler:** Cabin: 80, Structural: 40, Certification: 20, PM: 10 (Aynı)
- **Hesaplama:**
  - Base Labor: $14,800.00
  - **Kâr Marjı:** %8 (Flagship competitive: 10% - 2%) -> $14,800 × 0.08 = $1,184.00
  - **Contingency:** $740.00
  - **Testing Fee:** $1,500.00
  - **Material Allowance:** $2,500.00
- **Beklenen Toplam:** $14,800 + $1,184 + $740 + $1,500 + $2,500 = **$20,724.00**

### Vaka 3: Third Party Müşteri - Acil (Rush) Strateji - 1 Uçak
- **Saatler:** Structural: 60, Certification: 15, PM: 5
- **Hesaplama:**
  - Structural Labor: 60 × $110 = $6,600
  - Certification Labor: 15 × $80 = $1,200
  - PM Labor: 5 × $120 = $600
  - **Temel İşçilik (Base Labor):** $6,600 + $1,200 + $600 = $8,400.00
  - **Kâr Marjı:** %50 (Third Party max_margin/ceiling) -> $8,400 × 0.50 = $4,200.00
  - **Contingency:** $8,400 × 0.05 = $420.00
  - **Testing Fee:** $1,500.00
  - **Material Allowance:** 1 × $500 = $500.00
- **Beklenen Toplam:** $8,400 + $4,200 + $420 + $1,500 + $500 = **$15,020.00**

### Vaka 4: Partner Müşteri - Belirsiz Strateji (Varsayılan Marj) - 8 Uçak
- **Saatler:** Structural: 150, Avionics: 100, Certification: 40, PM: 20
- **Hesaplama:**
  - Structural: 150 × $110 = $16,500
  - Avionics: 100 × $105 = $10,500
  - Certification: 40 × $80 = $3,200
  - PM: 20 × $120 = $2,400
  - **Base Labor:** $16,500 + $10,500 + $3,200 + $2,400 = $32,600.00
  - **Kâr Marjı:** %22 (Partner default_margin) -> $32,600 × 0.22 = $7,172.00
  - **Contingency:** $32,600 × 0.05 = $1,630.00
  - **Testing Fee:** $1,500.00
  - **Material Allowance:** 8 × $500 = $4,000.00
- **Beklenen Toplam:** $32,600 + $7,172 + $1,630 + $1,500 + $4,000 = **$46,902.00**

### Vaka 5: Third Party Müşteri - En Ucuz Strateji - 12 Uçak
- **Saatler:** Cabin: 120, Certification: 30, PM: 10
- **Hesaplama:**
  - Cabin: 120 × $95 = $11,400
  - Certification: 30 × $80 = $2,400
  - PM: 10 × $120 = $1,200
  - **Base Labor:** $11,400 + $2,400 + $1,200 = $15,000.00
  - **Kâr Marjı:** %30 (Third Party floor) -> $15,000 × 0.30 = $4,500.00
  - **Contingency:** $15,000 × 0.05 = $750.00
  - **Testing Fee:** $1,500.00
  - **Material Allowance:** 12 × $500 = $6,000.00
- **Beklenen Toplam:** $15,000 + $4,500 + $750 + $1,500 + $6,000 = **$27,750.00**

### Vaka 6: Partner Müşteri - Rekabetçi Strateji - 2 Uçak
- **Saatler:** Cabin: 50, Avionics: 50, Certification: 15, PM: 5
- **Hesaplama:**
  - Cabin: 50 × $95 = $4,750
  - Avionics: 50 × $105 = $5,250
  - Certification: 15 × $80 = $1,200
  - PM: 5 × $120 = $600
  - **Base Labor:** $4,750 + $5,250 + $1,200 + $600 = $11,800.00
  - **Kâr Marjı:** %20 (Partner competitive: 22% - 2%) -> $11,800 × 0.20 = $2,360.00
  - **Contingency:** $11,800 × 0.05 = $590.00
  - **Testing Fee:** $1,500.00
  - **Material Allowance:** 2 × $500 = $1,000.00
- **Beklenen Toplam:** $11,800 + $2,360 + $590 + $1,500 + $1,000 = **$17,250.00**

### Vaka 7: Third Party Müşteri - Varsayılan Strateji - 1 Uçak
- **Saatler:** Avionics: 100, Certification: 25, PM: 10
- **Hesaplama:**
  - Base Labor: (100 × $105) + (25 × $80) + (10 × $120) = $10,500 + $2,000 + $1,200 = $13,700.00
  - **Kâr Marjı:** %40 (Third Party default) -> $13,700 × 0.40 = $5,480.00
  - **Contingency:** $13,700 × 0.05 = $685.00
  - **Testing Fee:** $1,500.00
  - **Material Allowance:** 1 × $500 = $500.00
- **Beklenen Toplam:** $13,700 + $5,480 + $685 + $1,500 + $500 = **$21,865.00**

### Vaka 8: Flagship Müşteri - Acil (Rush) Strateji - 3 Uçak
- **Saatler:** Cabin: 150, Structural: 100, Avionics: 50, Certification: 30, PM: 20
- **Hesaplama:**
  - Cabin: 150 × $95 = $14,250
  - Structural: 100 × $110 = $11,000
  - Avionics: 50 × $105 = $5,250
  - Certification: 30 × $80 = $2,400
  - PM: 20 × $120 = $2,400
  - **Base Labor:** $14,250 + $11,000 + $5,250 + $2,400 + $2,400 = $35,300.00
  - **Kâr Marjı:** %15 (Flagship ceiling) -> $35,300 × 0.15 = $5,295.00
  - **Contingency:** $35,300 × 0.05 = $1,765.00
  - **Testing Fee:** $1,500.00
  - **Material Allowance:** 3 × $500 = $1,500.00
- **Beklenen Toplam:** $35,300 + $5,295 + $1,765 + $1,500 + $1,500 = **$45,360.00**
