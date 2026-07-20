# TDD Test Hata Yakalama Raporu (TDD Bug Catching Report)

Bu rapor, `tests/test_pricing.py` dosyasındaki birim testlerin (unit tests), fiyatlandırma motorunun ilk implementasyonundaki mantık ve hesaplama hatalarını nasıl yakaladığını belgeler.

---

## Yakalanan Hata 1: Floating-Point (Kayan Nokta) Hassasiyet Hatası

### Hata Tanımı
Python'da kayan nokta (float) aritmetiği yapılırken, `0.22 - 0.02` işlemi doğrudan `0.20000000000000004` değerini döndürür. Fiyatlandırma motorunun ilk taslağında bu marj değeri doğrudan vergi ve kâr hesaplamalarına sokulduğunda, nihai teklif toplamında kuruş bazlı sapmalar oluşuyordu.

### Testin Hatayı Yakalaması
`test_pricing.py` dosyasındaki `test_case_6_partner_competitive` testi çalıştırıldığında şu assertion hatası alındı:
```text
E       assert 0.20000000000000004 == 0.20
E       +  where 0.20000000000000004 = quote['margin_applied']
```

### Çözüm
Testin uyarısı doğrultusunda, `src/pricing.py` içinde uygulanan marj değeri yuvarlama işlemine tabi tutuldu:
```python
margin_applied = round(margin_applied, 4)
```
Bu sayede test başarıyla yeşile döndü.

---

## Yakalanan Hata 2: Türkçe Karakter ve Büyük/Küçük Harf Eşleşmesi

### Hata Tanımı
Müşteri e-postalarından gelen strateji metinleri karışık harflerle (örn. "Acil", "REKABETÇİ") ve Türkçe karakterlerle gelebiliyordu. İlk implementasyonda sadece tam İngilizce string eşlemesi (örn. `strategy_string == "cheapest"`) yapılması planlanmıştı.

### Testin Hatayı Yakalaması
`test_case_6_partner_competitive` ("rekabetçi fiyat verilsin" girdisiyle) ve `test_case_8_flagship_rush` ("acil AOG..." girdisiyle) testleri, eşleşme sağlanamadığı için varsayılan marj (default_margin) uyguladı ve yanlış fiyat hesaplayarak başarısız oldu.

### Çözüm
Testlerin uyarısı doğrultusunda, `src/pricing.py` içinde strateji metinlerini analiz etmeden önce tamamen küçük harfe dönüştüren ve Türkçe köklere göre alt kelime (substring) araması yapan yapı kuruldu:
```python
strategy_lower = strategy_string.lower() if strategy_string else ""
if any(k in strategy_lower for k in ["cheap", "ucuz"]):
    margin_applied = min_margin
elif any(k in strategy_lower for k in ["premium", "rush", "aog", "acil", "hızlı", "hizli"]):
    ...
```
Testler sayesinde bu strateji eşleme motorunun esnekliği ve doğruluğu kod yazım aşamasında garanti altına alındı.
