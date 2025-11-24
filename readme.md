# 💻 Sistem Pakar Rekomendasi Laptop (Laptop Expert System)

![Python](https://img.shields.io/badge/Python-3.8%2B-blue) ![Flask](https://img.shields.io/badge/Framework-Flask-green) ![Pandas](https://img.shields.io/badge/Data-Pandas-orange) ![License](https://img.shields.io/badge/License-MIT-lightgrey)

Sistem Pakar berbasis web yang dirancang untuk membantu pengguna menemukan laptop yang paling sesuai berdasarkan **Anggaran (Budget)** dan **Kategori Kebutuhan**. Sistem ini menggabungkan metode *Rule-Based Reasoning* (untuk seleksi awal) dan algoritma *Simple Additive Weighting* (SAW) untuk perankingan rekomendasi.

---

## 📋 Daftar Isi
1. [Fitur Utama](#-fitur-utama)
2. [Instalasi dan Penggunaan](%EF%B8%8F-instalasi-dan-penggunaan)
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
* **Sistem Ranking (SAW):** Mengurutkan hasil rekomendasi berdasarkan bobot prioritas (CPU vs GPU vs RAM).
* **Explainable AI:** Memberikan alasan transparan mengapa laptop tersebut direkomendasikan (misal: "Lolos karena CPU score 15.000 > Min 11.000").

---

## 🛠️ Instalasi dan Penggunaan

### Prasyarat
* Python 3.x
* Pip (Python Package Installer)

### Langkah-langkah
1.  **Clone atau Download** repository ini.
2.  **Install Library** yang dibutuhkan:
    ```bash
    pip install flask pandas numpy
    ```
3.  **Pastikan Dataset Tersedia**:
    File `dataset_final_super_lengkap.csv` harus berada di dalam folder root proyek.
4.  **Jalankan Aplikasi**:
    ```bash
    python app.py
    ```
5.  **Akses Web**:
    Buka browser dan kunjungi `http://127.0.0.1:5000/`

---

## 📂 Struktur Proyek

```text
Laptop-Expert-System/
│
├── dataset_final_super_lengkap.csv  # [Knowledge Source] Data spesifikasi laptop
├── expertsystem.py                  # [Logic] Core sistem pakar, Rules, & Algoritma SAW
├── app.py                           # [Controller] Web Server Flask
├── README.md                        # Dokumentasi Proyek
└── templates/
    └── index.html                   # [View] Antarmuka pengguna (Bootstrap 5)
```

## 🧠 Dokumentasi Sistem Pakar

Bagian ini menjelaskan arsitektur logika yang diimplementasikan dalam `expertsystem.py`.

### 1. Akuisisi Pengetahuan (*Knowledge Acquisition*)
Pengetahuan sistem ini dibangun dari dua sumber utama:
* **Data Faktual (Dataset):** Menggunakan data CSV yang berisi ribuan laptop dengan atribut: `Harga_USD`, `CPU_Score`, `GPU_Score`, `RAM`, dan `Storage`.
* **Data Heuristik (Pakar):** Aturan-aturan yang ditanamkan (*hard-coded*) berdasarkan pengetahuan umum tentang kebutuhan hardware untuk profesi tertentu.
* **Preprocessing:** Data dibersihkan menggunakan Pandas, menghapus karakter non-numerik, dan mengisi nilai kosong (NULL) dengan 0.

### 2. Basis Pengetahuan (*Knowledge Base*)
Knowledge base direpresentasikan menggunakan struktur data *Dictionary* yang berisi aturan *If-Then* untuk setiap kategori.

**Tabel Aturan (Rules):**

| Kategori Pengguna | Min CPU | Min GPU | Min RAM | Bobot CPU | Bobot GPU | Bobot RAM | Prioritas |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **ADMIN / PELAJAR** | 3.000 | 0 | 4 GB | 20% | 0% | 30% | Storage & Harga Murah |
| **PROGRAMMER** | 11.000 | 0 | 8 GB | 50% | 0% | 40% | CPU Multicore & RAM |
| **DESAIN / VIDEO** | 15.000 | 8.000 | 16 GB | 40% | 60% | 0% | GPU & CPU Seimbang |
| **GAMING BERAT** | 14.000 | 13.000 | 16 GB | 20% | 70% | 10% | GPU High-End |

### 3. Mesin Inferensi (*Inference Engine*)
Sistem menggunakan pendekatan **Forward Chaining** dengan kombinasi *Constraint Satisfaction* dan *Weighted Scoring*.

**Alur Logika (`sistem.rekomendasi`):**

1.  **Input:** User memasukkan `Budget (IDR)` dan `Kategori`.
2.  **Reality Check (Validasi Awal):**
    Sistem memeriksa batas minimal budget untuk kategori tertentu.
    * *Rule:* Jika `Kategori == GAMING` dan `Budget < 10 Juta`, maka tolak permintaan.
3.  **Konversi Mata Uang:**
    Budget IDR dikonversi ke USD (Faktor: 16.690) untuk pencocokan dengan dataset.
4.  **Filtering Tahap 1 (Hard Constraints):**
    Seleksi laptop dimana:
    * `Harga Laptop <= Budget User`
    * `CPU Laptop >= Min CPU Kategori`
    * `GPU Laptop >= Min GPU Kategori`
    * `RAM Laptop >= Min RAM Kategori`
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
