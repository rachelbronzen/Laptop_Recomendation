import pandas as pd
import numpy as np

class SistemPakarLaptop:
    def __init__(self, file_path):
        """
        Inisialisasi Sistem Pakar.
        """
        self.file_path = file_path
        self.KONVERSI_FACTOR = 166.9 
        self.data = self._load_and_clean_data()
        
        # RULE BASE
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
            column_map = {
                'Harga_USD': 'Harga',     
                'CPU_Score': 'CpuScore',
                'GPU_Score': 'GpuScore',
                'RAM_Clean': 'RAM',
                'Storage': 'Storage_GB',
                'Nama_Laptop': 'Nama_Produk',
                'Screen_Score': 'ScreenScore', 
                'Processor': 'TipeProcessor',     
                'GPU': 'TipeGPU',
                'Display': 'DetailLayar',
                'Detail_URL': 'LinkPenjelasan',
                'Buy_Link': 'LinkPembelian'
            }
            
            rename_dict = {k: v for k, v in column_map.items() if k in df.columns}
            df = df.rename(columns=rename_dict)

            df = df.loc[:, ~df.columns.duplicated()]

            if 'Harga' not in df.columns:
                if 'Price' in df.columns:
                    df = df.rename(columns={'Price': 'Harga'})
                else:
                    print("[ERROR FATAL] Kolom 'Harga_USD' atau 'Price' tidak ditemukan di CSV!")
                    return pd.DataFrame()
            
            numeric_cols = ['Harga', 'CpuScore', 'GpuScore', 'RAM', 'Storage_GB', 'ScreenScore']
            
            for col in numeric_cols:
                if col not in df.columns:
                    df[col] = 0
                    continue

                if isinstance(df[col], pd.DataFrame):
                    df[col] = df[col].iloc[:, 0]

                if df[col].dtype == 'object':
                    df[col] = df[col].astype(str).str.replace(r'[^\d.]', '', regex=True)
                
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

            print(f"[INFO] Berhasil memuat {len(df)} data laptop.")
            return df
            
        except Exception as e:
            print(f"[ERROR] Gagal memuat data: {e}")
            return pd.DataFrame()

    def _reality_check(self, budget_idr, kategori):
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
        """
        Menghasilkan string Explainable AI yang detail.
        """
        reasons = []
        est_rupiah = row['Harga'] * self.KONVERSI_FACTOR
        
        # Penjelasan CPU
        cpu_act = int(row['CpuScore'])
        cpu_min = rule['min_cpu']
        reasons.append(f"CPU {cpu_act} (Min {cpu_min})")
        
        # Penjelasan GPU
        gpu_act = int(row['GpuScore'])
        gpu_min = rule['min_gpu']
        
        if gpu_min > 0:
            reasons.append(f"GPU {gpu_act} (Min {gpu_min})")
        elif gpu_act > 0:
            reasons.append(f"GPU {gpu_act}")

        # Penjelasan Screen Score
        screen_act = int(row.get('ScreenScore', 0))
        reasons.append(f"Screen {screen_act}")

        # 4. RAM
        reasons.append(f"RAM {int(row['RAM'])}GB")
        
        # Gabungkan
        return f"✅ Est: Rp {est_rupiah:,.0f} | Detail: {', '.join(reasons)}"

    def rekomendasi(self, user_budget_idr, user_kategori):
        if self.data.empty: return pd.DataFrame(columns=["Pesan"], data=["Database Kosong / Gagal Load."])
        if user_kategori not in self.rules: return pd.DataFrame(columns=["Pesan"], data=["Kategori Salah."])
        
        valid, msg = self._reality_check(user_budget_idr, user_kategori)
        if not valid: print(f"⚠️  Info: {msg}")

        budget_limit_usd = (user_budget_idr / self.KONVERSI_FACTOR) * 1.1 
        
        candidates = self.data[self.data['Harga'] <= budget_limit_usd].copy()
        
        if candidates.empty:
            return pd.DataFrame(columns=["Pesan"], data=["Budget tidak cukup (setelah konversi)."])

        # Rule Base Filtering
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
        
        candidates['Estimasi_Rupiah'] = candidates['Harga'] * self.KONVERSI_FACTOR

        # Sorting
        candidates = candidates.sort_values(by='Nilai_Rekomendasi', ascending=False)
        if user_kategori == "ADMIN_PELAJAR":
            candidates = candidates.sort_values(by='Estimasi_Rupiah', ascending=True)

        return candidates[['Nama_Produk', 'Estimasi_Rupiah', 'TipeProcessor', 'TipeGPU', 'RAM', 'Storage_GB', 'DetailLayar', 'Penjelasan_AI', 'LinkPenjelasan', 'LinkPembelian']].head(20)


if __name__ == "__main__":
    FILENAME = "dataset_final_super_lengkap.csv" 
    sistem = SistemPakarLaptop(FILENAME)
    
    INPUT_IDR = 6000000 
    
    print(f"\n--- REKOMENDASI UNTUK BUDGET RP {INPUT_IDR:,} ---")
    hasil = sistem.rekomendasi(INPUT_IDR, "PROGRAMMER_CODING")
    
    if isinstance(hasil, pd.DataFrame) and not hasil.empty:
        formatters = {'Estimasi_Rupiah': 'Rp {:,.0f}'.format}
        
        print(hasil.to_string(index=False, formatters=formatters))
    else:
        print(hasil)

