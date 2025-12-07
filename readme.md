# 💻 Sistem Pakar Rekomendasi Laptop (Laptop Expert System)

![Python](https://img.shields.io/badge/Python-3.8%2B-blue) ![Flask](https://img.shields.io/badge/Framework-Flask-green) ![Pandas](https://img.shields.io/badge/Data-Pandas-orange)

Sistem Pakar berbasis web yang dirancang untuk membantu pengguna menemukan laptop yang paling sesuai berdasarkan **Anggaran (Budget)** dan **Kategori Kebutuhan**. Sistem ini menggabungkan metode *Rule-Based Reasoning* (untuk seleksi awal) dan algoritma *Simple Additive Weighting* (SAW) untuk perankingan rekomendasi.
<img width="2559" height="1209" alt="image" src="https://github.com/user-attachments/assets/f8c56288-aabc-47a5-9fd0-a1395a7aca08" />

<img width="2557" height="1212" alt="image" src="https://github.com/user-attachments/assets/ab768220-771a-4ba4-babf-4df185bd61ea" />



---

## 📋 Daftar Isi
1. [Fitur Utama](#-fitur-utama)
2. [Instalasi dan Penggunaan](#%EF%B8%8F-instalasi-dan-penggunaan)
3. [Struktur Proyek](#-struktur-proyek)
4. [Dokumentasi Sistem Pakar](#-dokumentasi-sistem-pakar)
    - [Akuisisi Pengetahuan (Knowledge Acquisition)](#1-akuisisi-pengetahuan-knowledge-acquisition)
    - [Basis Pengetahuan (Knowledge Base)](#2-basis-pengetahuan-knowledge-base)
    - [Mesin Inferensi (Inference Engine)](#3-mesin-inferensi-inference-engine)
    - [Fasilitas Penjelasan (Explanation Facility)](#4-fasilitas-penjelasan-explanation-facility)

---

## 🚀 Fitur Utama

* **Pencarian Cerdas:** Memfilter laptop berdasarkan budget Rupiah (dikonversi otomatis dari USD).
* **Segmentasi Pengguna:** 4 Kategori peran (Pelajar, Programmer, Desainer, Gamer) dengan aturan spesifikasi yang berbeda.
* **Validasi Realitas:** Mencegah pencarian yang tidak realistis (contoh: mencari laptop gaming berat dengan budget 2 juta).
* **Sistem Ranking (SAW):** Mengurutkan hasil rekomendasi berdasarkan bobot prioritas (CPU vs GPU vs RAM Storage vs Kualitas Layar (Screen) vs Refresh Rate (Hz)).
* **Explainable AI:** Memberikan alasan transparan mengapa laptop tersebut direkomendasikan (misal: "Lolos karena CPU score 15.000 > Min 11.000").
* **Smart Search & Brand Filter:** Fitur pencarian teks bebas dan filter merek (HP, Lenovo, ASUS, dll).
* **Automated Data Pipeline:** Menggunakan script Selenium terintegrasi untuk memperoleh data spesifikasi laptop dan skor benchmark secara otomatis.
* **Advanced Sorting:** Pengurutan berdasarkan *Best Value* (Skor Performa per Rupiah), *Lowest Price*, dan *Highest Score*.
---

## 🛠️ Instalasi dan Penggunaan

### Cara 1: Akses Langsung (Cloud)
Sistem dapat diakses tanpa instalasi melalui link berikut:  
**[https://lres-v2repo.vercel.app/](https://lres-v2repo.vercel.app/)**

### Cara 2: Jalankan Pada Lokal
**Prasyarat**
* Python 3.x
* Pip (Python Package Installer)

**Langkah-langkah** 
1.  **Clone atau Download** repository ini.
    ```bash
    git clone https://github.com/hansits034/lres-v2_repo.git
    cd Laptop-Expert-System
    ```
3.  **Install Library** yang dibutuhkan:
    ```bash
    pip install flask pandas numpy selenium beautifulsoup4 webdriver-manager
    ```
4.  **Pastikan Dataset Tersedia**:
    File `dataset_final_super_lengkap.csv` harus berada di dalam folder root proyek.
5.  **Jalankan Aplikasi**:
    ```bash
    python app.py
    ```
6.  **Akses Web**:
    Buka browser dan kunjungi `http://127.0.0.1:5000/`

---

## 📂 Struktur Proyek

```text
Laptop-Expert-System/
│
├── dataset_final_super_lengkap.csv  # [Knowledge Source] Data spesifikasi laptop
├──masterscrapselenium.py           # [Acquisition] Script Automated Knowledge Extraction
├──expertsystem.py                  # [Logic] Core sistem pakar, Rules, & Algoritma SAW
├── app.py                           # [Controller] Web Server Flask
├── README.md                        # Dokumentasi Proyek
└── templates/
    └── index.html                   # [View] Antarmuka pengguna (Bootstrap 5)
└── static/
    └── style.css                  # [View] Design Visual
```

## 🧠 Dokumentasi Sistem Pakar

Bagian ini menjelaskan arsitektur logika yang diimplementasikan dalam `expertsystem.py`.

### 1. Akuisisi Pengetahuan (*Knowledge Acquisition*)
Pengetahuan sistem ini dibangun dari dua sumber utama:
* **Data Faktual (Dataset):** Menggunakan data CSV yang berisi ribuan laptop dengan atribut: `Harga_USD`, `CPU_Score`, `GPU_Score`, `RAM`, dan `Storage`.
* **Data Heuristik (Pakar):** Aturan-aturan yang ditanamkan (*hard-coded*) berdasarkan pengetahuan umum tentang kebutuhan hardware untuk profesi tertentu.
* **Preprocessing:** Data dibersihkan menggunakan Pandas, menghapus karakter non-numerik, dan mengisi nilai kosong (NULL) dengan 0.
* **Automated Knowledge Extraction:** Menggunakan bot crawler yang dapat dilihat pada `masterscrapselenium.py`. Pada file tersebut telah diterapkan algoritma Human-Like Behavior dalam proses pengumpulan data spesifikasi secara real-time menggunakan distribusi probabilitas Gaussian pada jeda waktu request, sehingga aktivitas bot terlihat natural seperti perilaku browsing manusia biasa. Setelah itu, data yang terkumpul akan disatukan kembali dengan data benchmark eksternal (CPU/GPU Benchmark).

### 2. Basis Pengetahuan (*Knowledge Base*)
Knowledge base direpresentasikan menggunakan struktur data *Dictionary* yang berisi aturan *If-Then* untuk setiap kategori.

**Tabel Aturan (Rules):**

| Kategori Utama | Sub-Kategori (Use Case) | Min CPU | Min GPU | Min RAM | Fokus Bobot Utama (Weights) | Deskripsi Target |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **STUDENT / OFFICE** | **General Tasks** | 9.595 | 1.230 | 8 GB | Storage (40%), RAM (30%), CPU (30%) | Kebutuhan dasar, browsing, office. |
| | **Science / Data** | 16.225 | 3.836 | 16 GB | CPU (50%), RAM (40%) | Komputasi data (Matlab, SPSS). |
| **PROGRAMMER** | **Web & Mobile** | 17.216 | 6.906 | 16 GB | CPU (55%), RAM (35%) | Kompilasi kode, emulator, multitasking. |
| | **AI & ML** | 25.368 | 10.142 | 32 GB | GPU (50%), CPU (35%) | Training model, parallel computing (CUDA). |
| **CREATOR** | **UI / UX Design** | 17.216 | 5.737 | 16 GB | GPU (45%), Screen (30%), CPU (20%) | Akurasi warna layar & rendering grafis ringan. |
| | **Video Editor / 3D** | 25.368 | 10.142 | 32 GB | GPU (45%), CPU (30%) | Rendering berat, scrubbing timeline lancar. |
| **GAMER** | **Casual / Indie** | 10.281 | 1.964 | 8 GB | GPU (60%), CPU (20%) | Game ringan, prioritas budget rendah. |
| | **Esports & Stream** | 16.131 | 10.142 | 16 GB | GPU (50%), Frame/Hz (20%) | Framerate tinggi (144Hz+) & streaming. |
| | **AAA Hardcore** | 30.562 | 17.399 | 32 GB | GPU (60%), CPU (15%) | Visual rata kanan (Ray Tracing, 4K). |


### 3. Mesin Inferensi (*Inference Engine*)
Sistem menggunakan pendekatan Hybrid: **Forward Chaining** untuk alur data, **Constraint Satisfaction Problem (CSP)** untuk eliminasi laptop yang tidak memenuhi syarat (Hard Constraints), dan **Simple Additive Weighting (SAW)** untuk perankingan (Soft Constraints).

**Alur Logika (`sistem.rekomendasi`):**

1.  **Input:**
    Sistem menerima parameter input dari antarmuka:
    * `Budget (IDR)`
    * `Main Category` & `Specific Use Case` (Sub-kategori)
    * `Brand Filter` & `Keyword Search` (Opsional)
2.  **Reality Check (Validasi Awal):**
    Sistem memverifikasi kelayakan budget terhadap kategori yang dipilih untuk mencegah ekspektasi yang tidak realistis sebelum pencarian dilakukan.
    * **Rule Gaming:** Min. **Rp 8.000.000** (Indie/Esport) atau **Rp 15.000.000** (AAA).
    * **Rule Creator:** Min. **Rp 7.000.000**.
    * **Rule Programmer:** Min. **Rp 4.000.000**.
    * *Action:* Jika `Budget < Threshold`, sistem mengembalikan pesan error spesifik dan menghentikan proses.
3.  **Konversi Mata Uang:**
    Budget IDR dikonversi ke USD (Faktor: 16.690) untuk pencocokan dengan dataset.
4.  **Filtering Tahap 1 (Hard Constraints):**
    Seleksi laptop dimana:
    * `Harga Laptop <= Budget User`
    * `CPU Score >= Min CPU`
    * `GPU Score >= Min GPU`
    * `RAM Capacity >= Min RAM`
    * `Screen Score >= Min Screen`
    * `Refresh Rate >= Min Frame` (Khusus Gaming/Creator)
5.  **Ranking Tahap 2 (SAW Algorithm):**
    Laptop yang lolos dihitung skor preferensinya:


    $$V = \left(\frac{CPU}{MaxCPU} \times w_{cpu}\right) + \left(\frac{GPU}{MaxGPU} \times w_{gpu}\right) + \left(\frac{RAM}{MaxRAM} \times w_{ram}\right)$$

### 4. Fasilitas Penjelasan (*Explanation Facility*)
Sistem menyediakan transparansi keputusan melalui fungsi `_generate_explanation`.
* **Cara Kerja:** Membandingkan spesifikasi laptop terpilih dengan aturan yang berlaku.
* **Contoh Output:** `"✅ Est: Rp 12.000.000 | Detail: CPU 12500 (Min 11000), RAM 16GB"`
* **Tujuan:** Memberi pemahaman kepada user bahwa laptop tersebut direkomendasikan karena spesifikasinya melampaui ambang batas minimum yang ditetapkan sistem.

---

## 📝 Catatan Pengembang
* Faktor konversi mata uang diatur pada konstanta `self.KONVERSI_FACTOR = 166.9` (dalam Cents/Satuan khusus dataset) atau disesuaikan dengan kurs `1 USD = ~16.690 IDR`.
* Mapping kolom CSV dilakukan di fungsi `_load_and_clean_data`. Jika menggunakan dataset baru, pastikan nama kolom disesuaikan di bagian ini.
