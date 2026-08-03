# Fiyatlandırma Spesifikasyonu (Pricing Specification v2.0.0)

Bu doküman, `src/pricing.py` v2.0.0 fiyatlandırma motorunun iş kurallarını, modifikasyon türüne duyarlı maliyet tablolarını, risk bazlı contingency oranlarını, aciliyet sürşarjlarını ve test senaryolarını tanımlar.

---

## 1. Fiyatlandırma Kuralları (Pricing Rules v2.0.0)

### 1.1 Mühendislik Saat Ücretleri (Rate Card)
`data/rate_card.csv` dosyasından dinamik olarak okunur:
- `cabin_design_engineer`: $95.00/saat
- `structural_engineer`: $110.00/saat
- `avionics_design_engineer`: $105.00/saat
- `certification_engineer`: $80.00/saat
- `project_manager`: $120.00/saat

### 1.2 Müşteri Sınıfları ve Marj Bantları (Margin Bands)
`data/customer_classes.json` dosyasından dinamik olarak okunur:
- **Flagship (Bayrak Taşıyıcı & İç Hesap):** min %5 - default %10 - max %15
- **Partner (İttifak & Ortak Hesap):** min %15 - default %22 - max %30
- **Third Party (Üçüncü Taraf Standard):** min %30 - default %40 - max %50

### 1.3 Strateji Eşleme Kuralları (Strategy Mapping)
- **"cheapest possible" / "cheapest" / "en ucuz":** Kâr marjı alt sınırı (`min_margin`).
- **"premium" / "rush" / "AOG" / "acil" / "hızlı":** Kâr marjı üst sınırı (`max_margin`).
- **"competitive" / "rekabetçi":** `max(min_margin, default_margin - 0.02)`.
- **Diğer / Eşleşmeyen:** Varsayılan marj (`default_margin`).

---

## 2. Dinamik Maliyet ve Risk Bileşenleri (v2.0.0 Enhancements)

### 2.1 Aciliyet Sürşarjı (AOG / Rush Urgency Surcharge)
Sadece Temel İşçilik Maliyetine (`base_labor_cost`) uygulanır:
- **Normal:** 1.00x (Sürşarj yok)
- **Rush / Acil / Hızlı:** 1.25x (%25 sürşarj)
- **AOG (Aircraft On Ground):** 1.50x (%50 sürşarj)

### 2.2 Modifikasyon Türüne ve Karmaşıklığa Duyarlı Test Ücreti (Testing Fee Table)
Sertifikasyon standartları (CS-25.1309, DO-160G EMI/EMC, statik testler) uyarınca belirlenen sabit test ücretleridir ($ USD):

| Modifikasyon Türü | Minor | Standard | Major |
|---|---|---|---|
| `cabin` / `cabin_lopa` | $800 / $1,000 | $2,500 / $3,000 | $6,000 / $7,000 |
| `structural` / `repair` | $2,000 / $1,500 | $7,000 / $5,000 | $18,000 / $14,000 |
| `avionics` | $2,500 | $8,500 | $20,000 |
| `cargo` (P2F STC) | $5,000 | $18,000 | $40,000 |
| `ifc` (Satellite Wi-Fi) | $3,500 | $12,000 | $25,000 |
| `ife` / `isps` | $2,000 / $1,500 | $7,000 / $5,000 | $16,000 / $12,000 |
| `elams` / `gain` | $1,000 / $1,200 | $3,500 / $4,000 | $8,000 / $10,000 |

### 2.3 Uçak Başına Malzeme Ödeneği (Material Allowance per Aircraft)
Uçak başına modifikasyon ve kit maliyetleridir ($ USD):

| Modifikasyon Türü | Minor | Standard | Major |
|---|---|---|---|
| `cabin` | $250 | $1,500 | $5,000 |
| `structural` | $800 | $4,000 | $15,000 |
| `avionics` | $1,000 | $5,000 | $12,000 |
| `cargo` | $5,000 | $25,000 | $80,000 |
| `ifc` | $3,000 | $15,000 | $30,000 |

### 2.4 Risk Bazlı Beklenmedik Durum Payı (Risk-Based Contingency)
AACE Uluslararası Havacılık Standartları uyarınca proje karmaşıklığı ve STC gereksinimine göre düzeltilmiş temel işçilik üzerinden hesaplanır:

| Karmaşıklık | STC Gerekmiyor (Minor/Major Change) | STC Gerekiyor (Major STC) |
|---|---|---|
| **Minor** | %4 | %6 |
| **Standard** | %7 | %10 |
| **Major** | %10 | %15 |

### 2.5 Büyük Filo İndirimi (Volume Discount)
Filo büyüklüğüne göre ara toplama (subtotal) uygulanan indirim oranı:
- **Filo < 20:** %0
- **20 $\le$ Filo < 50:** %5 indirim
- **Filo $\ge$ 50:** %10 indirim

---

## 3. Örnek Hesaplama Vakası (Sample Test Case v2.0.0)

### Vaka 1: Flagship Müşteri - En Ucuz Strateji - 5 Uçak - Cabin Standard
- **Girdi:** Cabin: 80h, Structural: 40h, Cert: 20h, PM: 10h ($n = 5$ uçak)
- **Hesaplama:**
  - Base Labor: $(80 \times \$95) + (40 \times \$110) + (20 \times \$80) + (10 \times \$120) = \$14,800.00$
  - **Urgency Multiplier:** Normal (1.0x) $\implies \$14,800.00$
  - **Kâr Marjı:** %5 (Flagship floor) $\implies \$14,800 \times 0.05 = \$740.00$
  - **Testing Fee (Cabin Standard):** $\$2,500.00$
  - **Material Allowance (Cabin Standard, 5 Uçak):** $5 \times \$1,500 = \$7,500.00$
  - **Contingency (Standard, STC yok):** %7 $\implies \$14,800 \times 0.07 = \$1,036.00$
  - **Subtotal:** $\$14,800 + \$740 + \$2,500 + \$7,500 + \$1,036 = \mathbf{\$26,576.00}$
  - **Volume Discount:** %0 ($5 < 20$)
  - **Toplam Fiyat:** $\mathbf{\$26,576.00}$
