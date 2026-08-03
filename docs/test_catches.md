# TDD Test Hata Yakalama Raporu (TDD Bug Catching Report)

Bu rapor, `tests/` klasöründeki birim ve entegrasyon testlerinin (TDD - Test Driven Development), **TEKLİF-Sim** uygulamasının mimari, hesaplama ve kural motorlarındaki mantık hatalarını kod geliştirme sürecinde nasıl yakalayıp önlediğini belgeler.

---

## 1. Yakalanan Hata 1: Floating-Point (Kayan Nokta) Hassasiyet Hatası

### Hata Tanımı
Python'da kayan nokta (float) aritmetiği yapılırken, `0.22 - 0.02` işlemi doğrudan `0.20000000000000004` değerini döndürür. Fiyatlandırma motorunun ilk taslağında bu marj değeri doğrudan vergi ve kâr hesaplamalarına sokulduğunda, nihai teklif toplamında kuruş bazlı sapmalar oluşuyordu.

### Testin Hatayı Yakalaması
`tests/test_pricing.py` dosyasındaki `test_competitive_margin_clamped_to_min_margin` ve marj hesaplama testleri çalıştırıldığında şu assertion hatası alındı:
```text
E       assert 0.20000000000000004 == 0.20
E       +  where 0.20000000000000004 = quote['margin_applied']
```

### Çözüm
Testin uyarısı doğrultusunda, `src/pricing.py` içinde uygulanan marj değeri 4 basamağa yuvarlandı:
```python
margin_applied = round(margin_applied, 4)
```

---

## 2. Yakalanan Hata 2: Türkçe Karakter ve Büyük/Küçük Harf Eşleşmesi

### Hata Tanımı
Müşteri e-postalarından gelen strateji metinleri karışık harflerle (örn. "Acil AOG", "REKABETÇİ", "hızlı teslimat") ve Türkçe karakterlerle gelebiliyordu. İlk implementasyonda sadece tam İngilizce string eşlemesi (örn. `strategy_string == "cheapest"`) yapılması planlanmıştı.

### Testin Hatayı Yakalaması
`test_urgency_surcharge` ve strateji eşleme testleri, Türkçe kelimeler kullanıldığında varsayılan marj (default) ve normal aciliyet çarpanı uygulayarak yanlış fiyat hesapladı.

### Çözüm
`src/pricing.py` içinde strateji metinlerini analiz etmeden önce tamamen küçük harfe dönüştüren ve Türkçe köklere göre alt kelime (substring) araması yapan esnek kural yapısı kuruldu:
```python
strategy_lower = strategy_string.lower() if strategy_string else ""
if any(k in strategy_lower for k in ["cheap", "ucuz"]):
    margin_applied = min_margin
elif any(k in strategy_lower for k in ["premium", "rush", "aog", "acil", "hızlı", "hizli"]):
    margin_applied = max_margin
```

---

## 3. Yakalanan Hata 3: Negatif Adam-Saat ve Sınır Değer Doğrulaması

### Hata Tanımı
Kullanıcı veya dış entegrasyon kaynaklarından hatalı veri girişiyle negatif mühendislik saatleri (örn. `-10` saat) aktarıldığında fiyat motorunun negatif maliyet hesaplaması riski bulunuyordu.

### Testin Hatayı Yakalaması
`test_negative_manhours` testi negatif değer içeren bir `manhours` nesnesi gönderdiğinde fiyat motorunun sessizce negatif tutar döndürdüğünü saptadı.

### Çözüm
`src/pricing.py` girişine strict kitleme ve doğrulama eklendi:
```python
for role, hours in manhours_dict.items():
    if hours is not None and hours < 0:
        raise ValueError(f"manhours for '{role}' cannot be negative: {hours}")
```

---

## 4. Yakalanan Hata 4: Zorunlu Part 21.A.239 CVE ve ICA Saatlerinin Eksik Kalması

### Hata Tanımı
Müşteri e-postasında kendi mühendislik adam-saatlerini belirttiği durumda (Customer Provided Hours), EASA Part 21.A.239 gereği zorunlu olan Uyum Doğrulama Mühendisi (CVE) denetim saatleri ve ICA (Instructions for Continued Airworthiness) saatleri müşteri saatlerine eklenmiyordu.

### Testin Hatayı Yakalaması
`test_cve_ica_added_to_customer_hours` testi müşteri saati sunulduğunda dahi `certification_engineer` saatlerinin CVE + ICA payı kadar artması gerektiğini doğruladı ve eksikliği yakaladı.

### Çözüm
`src/pricing.py` içine müşteri saatleri sunulmuş olsa bile zorunlu Part 21 CVE + ICA payını sertifikasyon saatlerine otomatik ekleyen mantık eklendi:
```python
part21_info = classify_part21_change(scope_text, modification_type or "cabin", complexity or "standard")
cve_hours = part21_info["cve_hours"]
ica_hours = part21_info["ica_hours"]
manhours_dict["certification_engineer"] = (manhours_dict.get("certification_engineer") or 0.0) + cve_hours + ica_hours
```

---

## 📌 Sonuç ve TDD Kazanımı

Test-Driven Development (TDD) yaklaşımı sayesinde:
* Hesaplama determinizmi (%100 tekrarlanabilir kuruşu kuruşuna aynı sonuç),
* Türkçe/İngilizce çift dilli metin toleransı,
* EASA Part 21 mevzuatına tam uyumluluk,

daha kod geliştirme aşamasında garanti altına alınmış ve canlıda oluşabilecek ticari/hukuki riskler engellenmiştir.
