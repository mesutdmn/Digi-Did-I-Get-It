
## Multimodal-LLM Destekli Multimedya Soru-Cevap Üretim Sistemi

Bu projede, PDF, DOCX, PPTX, EPUB, ENEX (evernote), TXT, MP3, MP4, MPEG4, PNG, JPG, JPEG, URL'ler, YouTube, Spotify, Wikipedia ve doğrudan metin girişi gibi çeşitli multimedya girdilerinden sorular ve cevaplar üreten tamamen otomatik bir sistem geliştirdik. Kullanıcılar, arayüzde soruları yanıtlayarak detaylı performans geri bildirimi ve gelişim önerileri alabilirler.

🚀 **Canlı Demo**: [Did I Get It](https://digi-btk.streamlit.app/)

* Uygulama, ücretsiz Streamlit bulut sınırlamaları nedeniyle çökebilir. Daha iyi bir deneyim için uygulamayı yerel olarak çalıştırın.

### ⚙️ **Çalışma Akışı**:
1. **Girdi**: Kullanıcılar, multimedya dosyalarını yükler veya URL girer.
2. **İşleme**: Sistem, girdilerden metin ve ses içeriğini çıkarır.
3. **Soru Üretimi**: Büyük Dil Modelleri (LLM'ler), içerikten sorular üretir.
4. **Etkileşimli Quiz**: Kullanıcılar soruları doğrudan arayüzde yanıtlar.
5. **Geri Bildirim ve Öneriler**: Performans raporları ile geri bildirim ve gelişim önerileri sunulur.
6. **Çıktı**: Kullanıcılar, performansları ve gelişim alanlarına dair detaylı bir rapor alır.
7. **Tekrar**: Kullanıcılar yeni içerik yükleyip öğrenme sürecine devam edebilir.
8. **Ekstra**: Quiz çözüldükten sonra sorular ve cevaplar PDF olarak kaydedilebilir.

![Uygulama Akışı](https://github.com/user-attachments/assets/34fcf8c0-fab5-4f58-9c5e-5845febaa43f)

### 📂 **Proje Yapısı**:
```
Digi-Did-I-Get-It/
├── app.py                     # Ana Streamlit uygulama dosyası.
├── question_format.py         # Quiz için soru formatı ve yapısı.
├── all_loaders.py             # Farklı dosya türlerinin yüklenmesini sağlar (PDF, URL, ses, video).
├── parallel_llm.py            # Verimli soru üretimi için paralel LLM çağrılarını yönetir.
├── utils.py                   # Dosyalar arasında paylaşılan yardımcı fonksiyonları içerir.
├── graph.py                   # Soru Üretimi, Rapor Oluşturma ve yardımcı LLM yapısını içerir.
├── requirements.txt           # Projeyi çalıştırmak için gereken bağımlılıkları listeler.
├── requirements_with...txt    # Tekrar edilebilirlik için belirli versiyonlarla bağımlılıkları listeler.
├── packages.txt               # Proje için gerekli OS düzeyinde paketleri listeler.
├── media/                     # Proje medya dosyaları için dizin.
│   └── background.jpg         # Proje için arka plan görseli.
├── styles/                    # Kullanıcı arayüzü için stil ve fontları içerir.
│   ├── style.css              # Streamlit arayüzü için özel CSS.
│   ├── script.js              # Ek etkileşim için bazı Streamlit işlevlerinin üzerine yazar.
│   └── arial-unicode-ms.ttf   # Latin, Yunan, Kiril, Arap, Çince, Korece gibi alfabeler için Arial Unicode MS.
├── README.md                  # İngilizce proje dokümantasyon dosyası.
└── README.tr.md               # Türkçe proje dokümantasyon dosyası.

```
### 🎯 **Kullanım Alanları**:
- **Eğitim**: Öğrenciler, multimedya içeriklerinden oluşturulan sorulara yanıt vererek öğrenimlerini pekiştirebilir.
- **Eğitim ve Gelişim**: Profesyoneller, eğitim materyallerini pekiştirmek ve kavrama yeteneklerini geliştirebilir.
- **Kişisel Gelişim**: Bireyler, multimedya içeriklerinden yeni kavramlar öğrenebilir ve anlama düzeylerini test edebilir.
- **İçerik Üretimi**: İçerik oluşturucular, içeriklerinden interaktif öğrenme deneyimleri için quizler oluşturabilir.
- **Araştırma ve Analiz**: Araştırmacılar, akademik makalelerden ve raporlardan soru üreterek analiz yapabilir.
- **Dil Öğrenimi**: Dil öğrenenler, okuma, dinleme ve anlama becerilerini multimedya içeriklerle geliştirebilir.
- **Eğlence**: Kullanıcılar, quizler ile eğlenceli ve interaktif bir şekilde multimedya içeriklerine erişebilir.
- **Beceri Geliştirme**: Kullanıcılar, çeşitli alanlarda bilgilerini ve becerilerini test edebilir.
- **Bilgi Paylaşımı**: Kullanıcılar, eğitim amacıyla başkalarıyla paylaşmak için multimedya içeriklerinden quizler oluşturabilir.
- **Eğitim Değerlendirmesi**: Eğitmenler, eğitim programlarının etkinliğini multimedya içeriklerinden soru üreterek değerlendirebilir.
- **Etkileşimli Öğrenme**: Kullanıcılar, içerikten üretilen soruları yanıtlayarak multimedya içerikleriyle etkileşimli bir şekilde öğrenebilir.

### 🛠️ **Kullanılan Teknolojiler**
- **LangChain, LangGraph, LangChain-Core, LangChain-Google-GenAI, LangChain-Community, LangChain-Text-Splitters**: Doğal dil işleme ve multimodal girdi verilerini yönetmek için.
- **Pydantic**: Veri yapısını kurmak ve model tutarlılığını sağlamak için.
- **Streamlit**: Kullanıcı arayüzünü oluşturur ve soruları yanıtlama için etkileşimli bir ortam sağlar.
- **PDF & Belge İşleme**: `pypdf`, `python-pptx`, `docx2txt` ve `unstructured[pdf]` gibi kütüphaneler, çeşitli belge formatlarını işler.
- **Video & Ses İşleme**: `moviepy`, `youtube-transcript-api` ve `yt_dlp`, multimedya içeriğini işlemeye yardımcı olur.
- **Raporlama**: `reportlab` ve `markdown2`, kapsamlı PDF raporları oluşturur.

### 🚀 **Kurulum**
1. Depoyu klonlayın:
   ```bash
   git clone https://github.com/mesutdmn/Digi-Did-I-Get-It.git
   ```
2. Proje dizinine gidin:
   ```bash
   cd Digi-Did-I-Get-It
   ```
3. Gerekli bağımlılıkları yükleyin:
   ```bash
   pip install -r requirements.txt
   ```
4. `.env` dosyasına Multimodal Gemini Entegrasyonu ve Spotify erişimi için gerekli API anahtarlarını ekleyin.
    ```bash
   GEMINI_API_KEY=<YOUR_GEMINI_API_KEY>
   SPOTIPY_CLIENT_ID=<YOUR_SPOTIPY_CLIENT_ID>
   SPOTIPY_CLIENT_SECRET=<YOUR_SPOTIPY_CLIENT_SECRET>
    ```
5. Streamlit uygulamasını çalıştırın:
    ```bash
    streamlit run app.py
    ```

### 📌 **Nasıl Kullanılır**
1. **İçerik Yükleyin**: Uygulamayı Streamlit ile başlatın ve multimedya dosyasını yükleyin, metin girin veya bir URL girin.
2. **Soru Dilini Seçin**: Soru üretimi için dili seçin.
3. **Soruları Yanıtlayın**: Sistem, içerikten sorular oluşturacaktır.
4. **Etkileşimli Quiz**: Yanıtlamak istediğiniz soru sayısını seçin ve quize başlayın.
5. **Raporu Görüntüleyin**: Quizi tamamladıktan sonra, performansınızı, zayıf alanlara dair içgörüleri ve gelişim önerilerini içeren detaylı bir rapor alın.

### 🌟 **Takım Üyeleri**
- [Burhan Yıldız](https://www.linkedin.com/in/burhanyildiz/)
- [Hüseyin Baytar](https://www.linkedin.com/in/huseyinbaytar/)
- [Mesut Duman](https://www.linkedin.com/in/mesut-duman/)

### 📺 **Demo Video**
