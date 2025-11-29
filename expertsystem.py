import pandas as pd
import numpy as np
import re
import math

class SistemPakarLaptop:
    def __init__(self, file_path):
        self.file_path = file_path
        self.KONVERSI_FACTOR = 166.9
        
        # Daftar Brand yang diminta
        self.TARGET_BRANDS = [
            "HP", "Lenovo", "Dell", "ASUS", "Acer", "MSI", "LG", "Alienware", 
            "Samsung", "Microsoft", "Apple", "Panasonic", "Gigabyte", "AORUS", 
            "Razer", "Intel", "Gainward", "Dynabook", "Google", "Zotac"
        ]
        
        self.data = self._load_and_clean_data()
        
        # Rule Base
        self.rules = {
            "SHOW_ALL": {
                "all": { "min_cpu": 0, "min_gpu": 0, "min_ram": 0, "min_screen": 0, "min_frame": 0, "w_cpu": 0.2, "w_gpu": 0.2, "w_ram": 0.2, "w_storage": 0.2, "w_screen": 0.2, "w_frame": 0.0, "desc": "Menampilkan semua laptop tanpa filter spesifikasi minimum." }
            },
            "ADMIN_PELAJAR": {
                "umum": { "min_cpu": 9595, "min_gpu": 1230, "min_ram": 8, "min_screen": 0, "min_frame": 0, "w_cpu": 0.3, "w_gpu": 0.0, "w_ram": 0.3, "w_storage": 0.4, "w_screen": 0.0, "w_frame": 0.0, "desc": "Office, browsing." },
                "spesifik": { "min_cpu": 16225, "min_gpu": 3836, "min_ram": 16, "min_screen": 0, "min_frame": 0, "w_cpu": 0.5, "w_gpu": 0.0, "w_ram": 0.4, "w_storage": 0.1, "w_screen": 0.0, "w_frame": 0.0, "desc": "Matlab, data." }
            },
            "PROGRAMMER_CODING": {
                "web_mobile": { "min_cpu": 17216, "min_gpu": 6906, "min_ram": 16, "min_screen": 0, "min_frame": 0, "w_cpu": 0.55, "w_gpu": 0.05, "w_ram": 0.35, "w_storage": 0.05, "w_screen": 0.0, "w_frame": 0.0, "desc": "Web/Mobile Dev." },
                "machine_learning": { "min_cpu": 25368, "min_gpu": 10142, "min_ram": 32, "min_screen": 0, "min_frame": 0, "w_cpu": 0.35, "w_gpu": 0.5, "w_ram": 0.15, "w_storage": 0.0, "w_screen": 0.0, "w_frame": 0.0, "desc": "AI/ML." }
            },
            "DESAIN_VIDEO": {
                "ui_ux": { "min_cpu": 17216, "min_gpu": 5737, "min_ram": 16, "min_screen": 80, "min_frame": 0, "w_cpu": 0.2, "w_gpu": 0.45, "w_ram": 0.05, "w_storage": 0.0, "w_screen": 0.3, "w_frame": 0.0, "desc": "UI/UX." },
                "video_editing": { "min_cpu": 25368, "min_gpu": 10142, "min_ram": 32, "min_screen": 80, "min_frame": 0, "w_cpu": 0.3, "w_gpu": 0.45, "w_ram": 0.1, "w_storage": 0.0, "w_screen": 0.15, "w_frame": 0.0, "desc": "Video Editing." }
            },
            "GAMING_BERAT": {
                "indie": { "min_cpu": 10281, "min_gpu": 1964, "min_ram": 8, "min_screen": 0, "min_frame": 60, "w_cpu": 0.2, "w_gpu": 0.6, "w_ram": 0.1, "w_storage": 0.0, "w_screen": 0.0, "w_frame": 0.1, "desc": "Indie Games." },
                "esport_stream": { "min_cpu": 16131, "min_gpu": 10142, "min_ram": 16, "min_screen": 0, "min_frame": 144, "w_cpu": 0.2, "w_gpu": 0.5, "w_ram": 0.1, "w_storage": 0.0, "w_screen": 0.0, "w_frame": 0.2, "desc": "Esports." },
                "aaa_high": { "min_cpu": 30562, "min_gpu": 17399, "min_ram": 32, "min_screen": 120, "min_frame": 165, "w_cpu": 0.15, "w_gpu": 0.6, "w_ram": 0.1, "w_storage": 0.0, "w_screen": 0.1, "w_frame": 0.05, "desc": "AAA Games." }
            }
        }

    def _load_and_clean_data(self):
        try:
            df = pd.read_csv(self.file_path, encoding='utf-8', low_memory=False)
            column_map = {'Harga_USD': 'Harga', 'CPU_Score': 'CpuScore', 'GPU_Score': 'GpuScore', 'RAM_Clean': 'RAM', 'Storage': 'Storage_GB', 'Nama_Laptop': 'Nama_Produk', 'Screen_Score': 'ScreenScore', 'Processor': 'TipeProcessor', 'GPU': 'TipeGPU', 'Display': 'DetailLayar', 'Detail_URL': 'LinkPenjelasan', 'Buy_Link': 'LinkPembelian'}
            df = df.rename(columns={k: v for k, v in column_map.items() if k in df.columns})
            df = df.loc[:, ~df.columns.duplicated()]
            
            if 'Harga' not in df.columns:
                if 'Price' in df.columns: df = df.rename(columns={'Price': 'Harga'})
                else: return pd.DataFrame()
            
            numeric_cols = ['Harga', 'CpuScore', 'GpuScore', 'RAM', 'Storage_GB', 'ScreenScore']
            for col in numeric_cols:
                if col not in df.columns: df[col] = 0
                if isinstance(df[col], pd.DataFrame): df[col] = df[col].iloc[:, 0]
                if df[col].dtype == 'object': df[col] = df[col].astype(str).str.replace(r'[^\d.]', '', regex=True)
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

            # Ekstraksi Refresh Rate
            def extract_hz(text):
                if not isinstance(text, str): return 60 
                match = re.search(r'(\d+)\s*Hz', text, re.IGNORECASE)
                return int(match.group(1)) if match else 60
            
            if 'DetailLayar' in df.columns: df['RefreshRate'] = df['DetailLayar'].apply(extract_hz)
            else: df['RefreshRate'] = 60

            # --- FITUR BARU: Identifikasi Brand ---
            def identify_brand(product_name):
                if not isinstance(product_name, str): return "Other"
                name_upper = product_name.upper()
                for brand in self.TARGET_BRANDS:
                    if brand.upper() in name_upper:
                        return brand
                return "Other"

            df['Brand'] = df['Nama_Produk'].apply(identify_brand)
            
            return df
        except Exception as e: 
            print(f"Error Loading: {e}")
            return pd.DataFrame()

    def _reality_check(self, budget_idr, kategori, sub_kategori):
        if kategori == "SHOW_ALL": return True, "Valid" # Show all bypass
        
        batas_min = 2000000
        if kategori == "GAMING_BERAT":
            batas_min = 15000000 if sub_kategori == "aaa_high" else 8000000
        elif kategori == "DESAIN_VIDEO": batas_min = 7000000
        elif kategori == "PROGRAMMER_CODING": batas_min = 4000000
        return (False, f"Budget terlalu rendah (Min Rp {batas_min:,})") if budget_idr < batas_min else (True, "Valid")

    def _generate_explanation(self, row, rule, kategori):
        reasons = []
        est_rupiah = row['Harga'] * self.KONVERSI_FACTOR
        
        # Penjelasan Generic untuk Show All
        if kategori == "SHOW_ALL":
            return f"Est: Rp {est_rupiah:,.0f} | CPU {int(row['CpuScore'])}, GPU {int(row['GpuScore'])}, RAM {int(row['RAM'])}GB"

        cpu_act = int(row['CpuScore'])
        reasons.append(f"CPU {cpu_act} (min:{rule['min_cpu']})")
        
        if rule['w_gpu'] > 0 or row['GpuScore'] > 2000:
            gpu_act = int(row['GpuScore'])
            if rule['min_gpu'] > 0: reasons.append(f"GPU {gpu_act} (min:{rule['min_gpu']})")
            else: reasons.append(f"GPU {gpu_act}")

        reasons.append(f"RAM {int(row['RAM'])}GB")
        
        if rule['w_screen'] > 0: reasons.append(f"Scrn {int(row['ScreenScore'])}")
        if rule['w_frame'] > 0 and row['RefreshRate'] > 60: reasons.append(f"{int(row['RefreshRate'])}Hz")

        final_score = row.get('Nilai_Rekomendasi', 0)
        details = ", ".join(reasons)
        return f"Est: Rp {est_rupiah:,.0f} | {details}, Overall Score: {final_score:.3f}"

    def rekomendasi(self, user_budget_idr, user_kategori, user_sub_kategori, 
                    search_query=None, brand_filter=None, sort_option="score", page=1, per_page=20):
        
        empty_result = {"data": [], "total_pages": 0, "current_page": 1, "total_items": 0}

        if self.data.empty or user_kategori not in self.rules:
            return empty_result

        # Handle Sub Kategori untuk SHOW_ALL
        if user_kategori == "SHOW_ALL":
            user_sub_kategori = "all"
        
        if user_sub_kategori not in self.rules[user_kategori]:
            return empty_result

        rule = self.rules[user_kategori][user_sub_kategori]
        
        # 1. Validasi Budget
        budget_limit_usd = (user_budget_idr / self.KONVERSI_FACTOR) * 1.1 
        candidates = self.data[self.data['Harga'] <= budget_limit_usd].copy()
        
        # 2. Filter Search Name (Jika ada)
        if search_query:
            candidates = candidates[candidates['Nama_Produk'].str.contains(search_query, case=False, na=False)]

        # 3. Filter Brand (Jika ada)
        if brand_filter and brand_filter != "ALL":
            candidates = candidates[candidates['Brand'] == brand_filter]

        if candidates.empty: return empty_result

        # 4. Filtering Spek (Hanya jika bukan SHOW_ALL)
        if user_kategori != "SHOW_ALL":
            candidates = candidates[
                (candidates['CpuScore'] >= rule['min_cpu']) &
                (candidates['GpuScore'] >= rule['min_gpu']) &
                (candidates['RAM'] >= rule['min_ram']) &
                (candidates['ScreenScore'] >= rule['min_screen']) &
                (candidates['RefreshRate'] >= rule['min_frame'])
            ]
        
        if candidates.empty: return empty_result

        # 5. Scoring
        max_cpu = candidates['CpuScore'].max() or 1
        max_gpu = candidates['GpuScore'].max() or 1
        max_ram = candidates['RAM'].max() or 1
        max_storage = candidates['Storage_GB'].max() or 1
        max_screen = candidates['ScreenScore'].max() or 1
        max_frame = candidates['RefreshRate'].max() or 1
        
        candidates['Nilai_Rekomendasi'] = (
            ((candidates['CpuScore'] / max_cpu) * rule['w_cpu']) +
            ((candidates['GpuScore'] / max_gpu) * rule['w_gpu']) +
            ((candidates['RAM'] / max_ram) * rule['w_ram']) +
            ((candidates['Storage_GB'] / max_storage) * rule['w_storage']) +
            ((candidates['ScreenScore'] / max_screen) * rule['w_screen']) +
            ((candidates['RefreshRate'] / max_frame) * rule['w_frame'])
        )
        
        candidates['Estimasi_Rupiah'] = candidates['Harga'] * self.KONVERSI_FACTOR

        # --- SORTING ---
        if sort_option == "lowest_price":
            candidates = candidates.sort_values(by='Estimasi_Rupiah', ascending=True)
        elif sort_option == "highest_price":
            candidates = candidates.sort_values(by='Estimasi_Rupiah', ascending=False)
        elif sort_option == "best_value":
            candidates['Value_Factor'] = candidates['Nilai_Rekomendasi'] / candidates['Estimasi_Rupiah']
            candidates = candidates.sort_values(by='Value_Factor', ascending=False)
        else:
            candidates = candidates.sort_values(by='Nilai_Rekomendasi', ascending=False)

        # Generate Penjelasan
        candidates['Penjelasan_AI'] = candidates.apply(
            lambda row: self._generate_explanation(row, rule, user_kategori), axis=1
        )

        cols_output = ['Nama_Produk', 'Estimasi_Rupiah', 'TipeProcessor', 'TipeGPU', 'RAM', 'Storage_GB', 'DetailLayar', 'RefreshRate', 'Penjelasan_AI', 'LinkPenjelasan', 'LinkPembelian']
        final_df = candidates[cols_output]

        # --- PAGINATION ---
        total_items = len(final_df)
        total_pages = math.ceil(total_items / per_page)
        
        if page < 1: page = 1
        if page > total_pages: page = total_pages if total_pages > 0 else 1
        
        start_idx = (page - 1) * per_page
        end_idx = start_idx + per_page
        
        page_data = final_df.iloc[start_idx:end_idx]

        return {
            "data": page_data.to_dict('records'),
            "total_pages": total_pages,
            "current_page": page,
            "total_items": total_items
        }

    def get_brands(self):
        return self.TARGET_BRANDS