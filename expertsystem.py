import pandas as pd
import numpy as np

class SistemPakarLaptop:
    def __init__(self, file_path):
        """
        Inisialisasi Sistem Pakar.
        """
        self.file_path = file_path
        self.KONVERSI_FACTOR = 166.9  # Convert Harga Sesuai Kurs Hari ini (0.01 USD = 166.90 IDR)
        self.data = self._load_and_clean_data()
        
        # RULE BASE (KNOWLEDGE BASE)
        self.rules = {
            "ADMIN_PELAJAR": {
                "min_cpu": 3000, "min_gpu": 0, "min_ram": 4,
                "w_cpu": 0.2, "w_gpu": 0.0, "w_ram": 0.3, "w_storage": 0.5,
                "desc": "Kebutuhan mengetik, browsing, dan Office ringan."
            },
            "PROGRAMMER_CODING": {
                "min_cpu": 11000, "min_gpu": 0, "min_ram": 8,
                "w_cpu": 0.5, "w_gpu": 0.0, "w_ram": 0.4, "w_storage": 0.1,
                "desc": "Kompilasi kode berat, multitasking emulator & docker."
            },
            "DESAIN_VIDEO": {
                "min_cpu": 15000, "min_gpu": 8000, "min_ram": 16,
                "w_cpu": 0.4, "w_gpu": 0.6, "w_ram": 0.0, "w_storage": 0.0,
                "desc": "Rendering 3D dan Video Editing yang butuh akselerasi GPU."
            },
            "GAMING_BERAT": {
                "min_cpu": 14000, "min_gpu": 13000, "min_ram": 16,
                "w_cpu": 0.2, "w_gpu": 0.7, "w_ram": 0.1, "w_storage": 0.0,
                "desc": "Gaming AAA rata kanan dengan FPS stabil."
            }
        }

    def _load_and_clean_data(self):
        """
        Memuat data CSV dan menargetkan kolom Harga USD (Price).
        """
        try:
            df = pd.read_csv(self.file_path, encoding='utf-8', low_memory=False)
            
            # Mapping Data
            column_map = {
                'Harga_USD': 'Harga',     
                'CPU_Score': 'CpuScore',
                'GPU_Score': 'GpuScore',
                'RAM_Clean': 'RAM',
                'Storage_Capacity_GB': 'Storage_GB',
                'Nama_Laptop': 'Nama_Produk'
            }
            
            # Rename kolom
            rename_dict = {k: v for k, v in column_map.items() if k in df.columns}
            df = df.rename(columns=rename_dict)

            # HAPUS DUPLIKAT: Agar tidak error dtype
            df = df.loc[:, ~df.columns.duplicated()]

            # Validasi Akhir
            if 'Harga' not in df.columns:
                print("[ERROR FATAL] Kolom 'Harga_USD' atau 'Price' tidak ditemukan di CSV!")
                print(f"Nama kolom yang tersedia: {list(df.columns)}")
                return pd.DataFrame()
            
            # Bersihkan data numerik
            numeric_cols = ['Harga', 'CpuScore', 'GpuScore', 'RAM', 'Storage_GB']
            for col in numeric_cols:
                if col in df.columns:
                    # Amankan jika masih ada duplikat dataframe
                    if isinstance(df[col], pd.DataFrame):
                        df[col] = df[col].iloc[:, 0]

                    if df[col].dtype == 'object':
                         df[col] = df[col].astype(str).str.replace(r'[^\d.]', '', regex=True)
                    
                    df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

            print(f"[INFO] Berhasil memuat {len(df)} data laptop (Format Harga: USD/Cent).")
            return df
            
        except Exception as e:
            print(f"[ERROR] Gagal memuat data: {e}")
            return pd.DataFrame()

    def _reality_check(self, budget_idr, kategori):
        # Validasi budget minimal (Angka dalam Rupiah)
        batas = {
            "GAMING_BERAT": 10000000,
            "DESAIN_VIDEO": 9000000,
            "PROGRAMMER_CODING": 5000000,
            "ADMIN_PELAJAR": 2000000
        }
        limit = batas.get(kategori, 0)
        if budget_idr < limit:
            return False, f"Budget Rp {budget_idr:,} terlalu rendah untuk {kategori}. Minimal Rp {limit:,}."
        return True, "Valid"

    def _generate_explanation(self, row, rule, kategori):
        reasons = []
        # Estimasi Balik ke Rupiah untuk Penjelasan
        est_rupiah = row['Harga'] * self.KONVERSI_FACTOR
        
        if row['CpuScore'] >= rule['min_cpu']:
            reasons.append(f"CPU {int(row['CpuScore'])}")
        if kategori in ["GAMING_BERAT", "DESAIN_VIDEO"] and row['GpuScore'] >= rule['min_gpu']:
             reasons.append(f"GPU {int(row['GpuScore'])}")
        reasons.append(f"RAM {int(row['RAM'])}GB")
        
        return f"✅ Estimasi: Rp {est_rupiah:,.0f}. Spek: {', '.join(reasons)}."

    def rekomendasi(self, user_budget_idr, user_kategori):
        if self.data.empty: return "Database Kosong."
        if user_kategori not in self.rules: return "Kategori Salah."
        if 'Harga' not in self.data.columns: return "Kolom Harga Hilang."

        # Reality Check
        valid, msg = self._reality_check(user_budget_idr, user_kategori)
        if not valid: print(f"⚠️  Info: {msg}")

        # Korvert Budget
        budget_limit_usd = (user_budget_idr / self.KONVERSI_FACTOR) * 1.1 # Toleransi 10%
        
        # Filtering pada data
        candidates = self.data[self.data['Harga'] <= budget_limit_usd].copy()
        
        if candidates.empty:
            return pd.DataFrame(columns=["Pesan"], data=["Budget tidak cukup (setelah konversi)."])

        # Rule Base Filtering (Spek)
        rule = self.rules[user_kategori]
        candidates = candidates[
            (candidates['CpuScore'] >= rule['min_cpu']) &
            (candidates['GpuScore'] >= rule['min_gpu']) &
            (candidates['RAM'] >= rule['min_ram'])
        ]
        
        if candidates.empty:
            return pd.DataFrame(columns=["Pesan"], data=["Tidak ada laptop spek tersebut di range harga ini."])

        # Scoring (SAW)
        max_cpu = candidates['CpuScore'].max() or 1
        max_gpu = candidates['GpuScore'].max() or 1
        max_ram = candidates['RAM'].max() or 1
        
        candidates['Nilai_Rekomendasi'] = (
            ((candidates['CpuScore'] / max_cpu) * rule['w_cpu']) +
            ((candidates['GpuScore'] / max_gpu) * rule['w_gpu']) +
            ((candidates['RAM'] / max_ram) * rule['w_ram'])
        )
        
        # Explain & Format Output
        candidates['Penjelasan_AI'] = candidates.apply(
            lambda row: self._generate_explanation(row, rule, user_kategori), axis=1
        )
        
        # Buat kolom Estimasi Rupiah untuk ditampilkan
        candidates['Estimasi_Rupiah'] = candidates['Harga'] * self.KONVERSI_FACTOR

        # Sorting
        candidates = candidates.sort_values(by='Nilai_Rekomendasi', ascending=False)
        if user_kategori == "ADMIN_PELAJAR":
            candidates = candidates.sort_values(by='Estimasi_Rupiah', ascending=True)

        return candidates[['Nama_Produk', 'Estimasi_Rupiah', 'CpuScore', 'GpuScore', 'RAM', 'Penjelasan_AI']].head(10)


if __name__ == "__main__":
    FILENAME = "dataset_final_super_lengkap.csv" 
    sistem = SistemPakarLaptop(FILENAME)
    
    INPUT_IDR = 2500000
    
    print(f"\n--- REKOMENDASI UNTUK BUDGET RP {INPUT_IDR:,} ---")
    hasil = sistem.rekomendasi(INPUT_IDR, "PROGRAMMER_CODING")
    
    if isinstance(hasil, pd.DataFrame) and not hasil.empty:
        pd.options.display.float_format = 'Rp {:,.0f}'.format
        print(hasil.to_string(index=False))
    else:
        print(hasil)