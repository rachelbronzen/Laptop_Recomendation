import os
import re
import time
import glob
import pandas as pd
from bs4 import BeautifulSoup
import random

# --- LIBRARY BARU: SELENIUM (Browser Automation) ---
try:
    from selenium import webdriver
    from selenium.webdriver.chrome.service import Service
    from webdriver_manager.chrome import ChromeDriverManager
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    HAS_SELENIUM = True
except ImportError:
    HAS_SELENIUM = False
    print("⚠️ Library 'selenium' atau 'webdriver-manager' belum terinstall.")
    print("👉 Jalankan: `pip install selenium webdriver-manager`")

# ================= KONFIGURASI =================
# Masukkan Link Pencarian LaptopMedia PERTAMA di sini.
# Script akan memanipulasi URL ini untuk membuka halaman 2, 3, dst secara otomatis.
LAPTOP_START_URLS = [
    "https://laptopmedia.com/specs/?size=n_1000_n&filters%5B0%5D%5Bfield%5D=availability&filters%5B0%5D%5Bvalues%5D%5B0%5D%5Bto%5D=n_2_n&filters%5B0%5D%5Bvalues%5D%5B0%5D%5Bfrom%5D=n_1_n&filters%5B0%5D%5Bvalues%5D%5B0%5D%5Bname%5D=Show%20only%20available%20laptops&filters%5B0%5D%5Btype%5D=any&filters%5B1%5D%5Bfield%5D=brand&filters%5B1%5D%5Bvalues%5D%5B0%5D=HP&filters%5B1%5D%5Btype%5D=any&filters%5B2%5D%5Bfield%5D=price_list&filters%5B2%5D%5Bvalues%5D%5B0%5D%5Bto%5D=n_500_n&filters%5B2%5D%5Bvalues%5D%5B0%5D%5Bfrom%5D=n_1_n&filters%5B2%5D%5Bvalues%5D%5B0%5D%5Bname%5D=Under%20%24500&filters%5B2%5D%5Bvalues%5D%5B1%5D%5Bto%5D=n_800_n&filters%5B2%5D%5Bvalues%5D%5B1%5D%5Bfrom%5D=n_500_n&filters%5B2%5D%5Bvalues%5D%5B1%5D%5Bname%5D=%24500%20-%20%24800&filters%5B2%5D%5Btype%5D=any",
    "https://laptopmedia.com/specs/?size=n_1000_n&filters%5B0%5D%5Bfield%5D=availability&filters%5B0%5D%5Bvalues%5D%5B0%5D%5Bto%5D=n_2_n&filters%5B0%5D%5Bvalues%5D%5B0%5D%5Bfrom%5D=n_1_n&filters%5B0%5D%5Bvalues%5D%5B0%5D%5Bname%5D=Show%20only%20available%20laptops&filters%5B0%5D%5Btype%5D=any&filters%5B1%5D%5Bfield%5D=brand&filters%5B1%5D%5Bvalues%5D%5B0%5D=HP&filters%5B1%5D%5Btype%5D=any&filters%5B2%5D%5Bfield%5D=price_list&filters%5B2%5D%5Bvalues%5D%5B0%5D%5Bto%5D=n_1200_n&filters%5B2%5D%5Bvalues%5D%5B0%5D%5Bfrom%5D=n_800_n&filters%5B2%5D%5Bvalues%5D%5B0%5D%5Bname%5D=%24800%20-%20%241200&filters%5B2%5D%5Bvalues%5D%5B1%5D%5Bto%5D=n_1500_n&filters%5B2%5D%5Bvalues%5D%5B1%5D%5Bfrom%5D=n_1200_n&filters%5B2%5D%5Bvalues%5D%5B1%5D%5Bname%5D=%241200%20-%20%241500&filters%5B2%5D%5Btype%5D=any",
    "https://laptopmedia.com/specs/?size=n_1000_n&filters%5B0%5D%5Bfield%5D=availability&filters%5B0%5D%5Bvalues%5D%5B0%5D%5Bto%5D=n_2_n&filters%5B0%5D%5Bvalues%5D%5B0%5D%5Bfrom%5D=n_1_n&filters%5B0%5D%5Bvalues%5D%5B0%5D%5Bname%5D=Show%20only%20available%20laptops&filters%5B0%5D%5Btype%5D=any&filters%5B1%5D%5Bfield%5D=brand&filters%5B1%5D%5Bvalues%5D%5B0%5D=HP&filters%5B1%5D%5Btype%5D=any&filters%5B2%5D%5Bfield%5D=price_list&filters%5B2%5D%5Bvalues%5D%5B0%5D%5Bfrom%5D=n_1500_n&filters%5B2%5D%5Bvalues%5D%5B0%5D%5Bname%5D=Over%20%241500&filters%5B2%5D%5Btype%5D=any",
    
    "https://laptopmedia.com/specs/?size=n_1000_n&filters%5B0%5D%5Bfield%5D=availability&filters%5B0%5D%5Bvalues%5D%5B0%5D%5Bto%5D=n_2_n&filters%5B0%5D%5Bvalues%5D%5B0%5D%5Bfrom%5D=n_1_n&filters%5B0%5D%5Bvalues%5D%5B0%5D%5Bname%5D=Show%20only%20available%20laptops&filters%5B0%5D%5Btype%5D=any&filters%5B1%5D%5Bfield%5D=brand&filters%5B1%5D%5Bvalues%5D%5B0%5D=Lenovo&filters%5B1%5D%5Btype%5D=any&filters%5B2%5D%5Bfield%5D=price_list&filters%5B2%5D%5Bvalues%5D%5B0%5D%5Bto%5D=n_500_n&filters%5B2%5D%5Bvalues%5D%5B0%5D%5Bfrom%5D=n_1_n&filters%5B2%5D%5Bvalues%5D%5B0%5D%5Bname%5D=Under%20%24500&filters%5B2%5D%5Bvalues%5D%5B1%5D%5Bto%5D=n_800_n&filters%5B2%5D%5Bvalues%5D%5B1%5D%5Bfrom%5D=n_500_n&filters%5B2%5D%5Bvalues%5D%5B1%5D%5Bname%5D=%24500%20-%20%24800&filters%5B2%5D%5Btype%5D=any",
    "https://laptopmedia.com/specs/?size=n_1000_n&filters%5B0%5D%5Bfield%5D=availability&filters%5B0%5D%5Bvalues%5D%5B0%5D%5Bto%5D=n_2_n&filters%5B0%5D%5Bvalues%5D%5B0%5D%5Bfrom%5D=n_1_n&filters%5B0%5D%5Bvalues%5D%5B0%5D%5Bname%5D=Show%20only%20available%20laptops&filters%5B0%5D%5Btype%5D=any&filters%5B1%5D%5Bfield%5D=brand&filters%5B1%5D%5Bvalues%5D%5B0%5D=Lenovo&filters%5B1%5D%5Btype%5D=any&filters%5B2%5D%5Bfield%5D=price_list&filters%5B2%5D%5Bvalues%5D%5B0%5D%5Bto%5D=n_1500_n&filters%5B2%5D%5Bvalues%5D%5B0%5D%5Bfrom%5D=n_1200_n&filters%5B2%5D%5Bvalues%5D%5B0%5D%5Bname%5D=%241200%20-%20%241500&filters%5B2%5D%5Bvalues%5D%5B1%5D%5Bto%5D=n_1200_n&filters%5B2%5D%5Bvalues%5D%5B1%5D%5Bfrom%5D=n_800_n&filters%5B2%5D%5Bvalues%5D%5B1%5D%5Bname%5D=%24800%20-%20%241200&filters%5B2%5D%5Btype%5D=any",
    "https://laptopmedia.com/specs/?size=n_1000_n&filters%5B0%5D%5Bfield%5D=availability&filters%5B0%5D%5Bvalues%5D%5B0%5D%5Bto%5D=n_2_n&filters%5B0%5D%5Bvalues%5D%5B0%5D%5Bfrom%5D=n_1_n&filters%5B0%5D%5Bvalues%5D%5B0%5D%5Bname%5D=Show%20only%20available%20laptops&filters%5B0%5D%5Btype%5D=any&filters%5B1%5D%5Bfield%5D=price_list&filters%5B1%5D%5Bvalues%5D%5B0%5D%5Bfrom%5D=n_1500_n&filters%5B1%5D%5Bvalues%5D%5B0%5D%5Bname%5D=Over%20%241500&filters%5B1%5D%5Btype%5D=any&filters%5B2%5D%5Bfield%5D=brand&filters%5B2%5D%5Bvalues%5D%5B0%5D=Lenovo&filters%5B2%5D%5Btype%5D=any",

    "https://laptopmedia.com/specs/?size=n_1000_n&filters%5B0%5D%5Bfield%5D=availability&filters%5B0%5D%5Bvalues%5D%5B0%5D%5Bto%5D=n_2_n&filters%5B0%5D%5Bvalues%5D%5B0%5D%5Bfrom%5D=n_1_n&filters%5B0%5D%5Bvalues%5D%5B0%5D%5Bname%5D=Show%20only%20available%20laptops&filters%5B0%5D%5Btype%5D=any&filters%5B1%5D%5Bfield%5D=brand&filters%5B1%5D%5Bvalues%5D%5B0%5D=Dell&filters%5B1%5D%5Btype%5D=any",
    "https://laptopmedia.com/specs/?size=n_1000_n&filters%5B0%5D%5Bfield%5D=availability&filters%5B0%5D%5Bvalues%5D%5B0%5D%5Bto%5D=n_2_n&filters%5B0%5D%5Bvalues%5D%5B0%5D%5Bfrom%5D=n_1_n&filters%5B0%5D%5Bvalues%5D%5B0%5D%5Bname%5D=Show%20only%20available%20laptops&filters%5B0%5D%5Btype%5D=any&filters%5B1%5D%5Bfield%5D=brand&filters%5B1%5D%5Bvalues%5D%5B0%5D=ASUS&filters%5B1%5D%5Btype%5D=any",
    "https://laptopmedia.com/specs/?size=n_1000_n&filters%5B0%5D%5Bfield%5D=availability&filters%5B0%5D%5Bvalues%5D%5B0%5D%5Bto%5D=n_2_n&filters%5B0%5D%5Bvalues%5D%5B0%5D%5Bfrom%5D=n_1_n&filters%5B0%5D%5Bvalues%5D%5B0%5D%5Bname%5D=Show%20only%20available%20laptops&filters%5B0%5D%5Btype%5D=any&filters%5B1%5D%5Bfield%5D=brand&filters%5B1%5D%5Bvalues%5D%5B0%5D=Acer&filters%5B1%5D%5Bvalues%5D%5B1%5D=MSI&filters%5B1%5D%5Btype%5D=any",
    "https://laptopmedia.com/specs/?size=n_1000_n&filters%5B0%5D%5Bfield%5D=availability&filters%5B0%5D%5Bvalues%5D%5B0%5D%5Bto%5D=n_2_n&filters%5B0%5D%5Bvalues%5D%5B0%5D%5Bfrom%5D=n_1_n&filters%5B0%5D%5Bvalues%5D%5B0%5D%5Bname%5D=Show%20only%20available%20laptops&filters%5B0%5D%5Btype%5D=any&filters%5B1%5D%5Bfield%5D=brand&filters%5B1%5D%5Bvalues%5D%5B0%5D=LG&filters%5B1%5D%5Bvalues%5D%5B1%5D=Alienware&filters%5B1%5D%5Bvalues%5D%5B2%5D=Samsung&filters%5B1%5D%5Bvalues%5D%5B3%5D=Microsoft&filters%5B1%5D%5Bvalues%5D%5B4%5D=Apple&filters%5B1%5D%5Bvalues%5D%5B5%5D=Panasonic&filters%5B1%5D%5Bvalues%5D%5B6%5D=Gigabyte&filters%5B1%5D%5Bvalues%5D%5B7%5D=AORUS&filters%5B1%5D%5Bvalues%5D%5B8%5D=Razer&filters%5B1%5D%5Bvalues%5D%5B9%5D=Intel&filters%5B1%5D%5Bvalues%5D%5B10%5D=Gainward&filters%5B1%5D%5Bvalues%5D%5B11%5D=Manli&filters%5B1%5D%5Bvalues%5D%5B12%5D=Dynabook&filters%5B1%5D%5Bvalues%5D%5B13%5D=Google&filters%5B1%5D%5Btype%5D=any"
]

MAX_PAGES_PER_URL = 10  # Loop sampai halaman 10

# Nama File Output
FILE_FINAL_RAW = 'final_scrap.csv'
FILE_CPU_CSV = 'cpu_bm.csv'
FILE_GPU_CSV = 'gpu_bm.csv'
FILE_FINAL_DATASET = 'dataset_final_super_lengkap.csv'

# URL Benchmark (Tetap download biasa karena jarang diblokir ketat)
URL_CPU_BENCHMARK = "https://www.cpubenchmark.net/cpu_list.php"
URL_GPU_BENCHMARK = "https://www.videocardbenchmark.net/gpu_list.php"

def smart_sleep():
    """
    Tidur dengan durasi acak (Distribusi Normal).
    Mean (Rata-rata) = 40 detik.
    Sigma (Deviasi) = 5 detik.
    Minimal = 30 detik (Hard limit).
    """
    mean_val = 40
    sigma_val = 5
    
    # Generate angka acak
    sleep_time = random.gauss(mean_val, sigma_val)
    
    # Pastikan tidak di bawah 30 detik
    if sleep_time < 30:
        sleep_time = 30 + (30 - sleep_time)
        
    print(f"   ⏳ Menunggu {sleep_time:.2f} detik (Mode Manusia)...")
    time.sleep(sleep_time)

# ================= LANGKAH 0: BERSIH-BERSIH =================
def step_0_cleanup():
    print("\n[LANGKAH 0] Membersihkan file lama...")
    patterns = [
        "halaman*.html", 
        "cpu_list.php", 
        "gpu_list.html", 
        FILE_FINAL_RAW, 
        FILE_CPU_CSV, 
        FILE_GPU_CSV, 
        FILE_FINAL_DATASET
    ]
    
    deleted_count = 0
    for pattern in patterns:
        for f in glob.glob(pattern):
            try:
                os.remove(f)
                deleted_count += 1
            except Exception as e:
                print(f"⚠️ Gagal menghapus {f}: {e}")
    print(f"✅ Berhasil menghapus {deleted_count} file lama.")

# ================= LANGKAH 1: BROWSER AUTOMATION (DIRECT LINK PATTERN) =================
def step_1_fetch_laptops_selenium():
    if not HAS_SELENIUM:
        return

    print("\n[LANGKAH 1] Memulai Browser Otomatis (Selenium)...")
    print("   🌐 Membuka Google Chrome...")

    # Setup Chrome Driver
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    options.add_argument("--disable-blink-features=AutomationControlled") # Anti-detect bot
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    
    page_counter = 1

    try:
        for base_url in LAPTOP_START_URLS:
            print(f"   🔗 Memproses Filter Utama...")

            # LOOP HALAMAN 1 SAMPAI 10
            for i in range(1, MAX_PAGES_PER_URL + 1):
                
                # --- LOGIKA PEMBUATAN URL ---
                if i == 1:
                    # Halaman 1 pakai link asli
                    target_url = base_url
                else:
                    # Halaman 2+ menyisipkan parameter 'current=n_X_n' setelah tanda tanya (?)
                    # Pola: .../specs/?size=...  MENJADI .../specs/?current=n_2_n&size=...
                    if "?" in base_url:
                        target_url = base_url.replace("?", f"?current=n_{i}_n&")
                    else:
                        target_url = base_url + f"?current=n_{i}_n"

                print(f"\n   🌍 Mengakses Halaman {i}...")
                print(f"   (Link: {target_url[:60]}...)")
                
                driver.get(target_url)
                
                #print("   ⏳ Menunggu 30 detik agar data termuat sempurna...")
                smart_sleep() 

                filename = f"halaman{page_counter}.html"
                print(f"   💾 Menyimpan {filename}...")
                
                with open(filename, "w", encoding="utf-8") as f:
                    f.write(driver.page_source)
                
                page_counter += 1
                
    except Exception as e:
        print(f"   ❌ Terjadi error fatal pada browser: {e}")
    finally:
        print("   ✅ Menutup Browser.")
        driver.quit()

# ================= LANGKAH 2: PARSING HTML LAPTOP =================
def parse_single_laptop_page(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    data_laptop = []
    
    # Mencari list item laptop
    laptop_listings = soup.find_all('li', class_=re.compile(r'flex items-center gap-2 list-none border-b py-1 mb-2'))
    
    for listing in laptop_listings:
        main_link = listing.find('a', class_=re.compile(r"grid-cols-laptopLayoutSmall"))
        if not main_link: continue
        
        # Nama
        name_el = main_link.find('h2')
        name = name_el.get_text(strip=True) if name_el else 'N/A'
        
        # Specs
        specs = {}
        specs_container = main_link.find('dl')
        if specs_container:
            dt_elements = specs_container.find_all('dt')
            dd_elements = specs_container.find_all('dd')
            for dt, dd in zip(dt_elements, dd_elements):
                key = dt.get_text(strip=True).replace(':', '') 
                value = dd.get_text(strip=True)
                specs[key] = value

        # Harga
        price_el = listing.find('div', class_='priceBtn')
        price_raw = 'N/A'
        if price_el:
            span_price = price_el.find('span', class_='text-lm-darkBlue')
            if span_price:
                price_raw = span_price.get_text(strip=True)
        
        price_cleaned = re.sub(r'[$,€]', '', price_raw).replace(' ', '').replace('sup', '')

        # Links
        detail_url = main_link['href'] if 'href' in main_link.attrs else 'N/A'
        buy_link_el = listing.find('a', target='_blank', href=re.compile(r'amazon\.com'))
        buy_link = buy_link_el['href'] if buy_link_el else 'N/A'
        
        data_laptop.append({
            'Nama_Laptop': name,
            'Processor': specs.get('Processor', 'N/A'),
            'RAM': specs.get('Internal memory', 'N/A'),
            'GPU': specs.get('Video card', 'N/A'),
            'Display': specs.get('Display', 'N/A'),
            'Storage': specs.get('Solid-state drive', '') + ' ' + specs.get('Hard drive', ''),
            'Harga_USD': price_cleaned,
            'Detail_URL': detail_url,
            'Buy_Link': buy_link,
        })
    return data_laptop

def step_2_process_laptops():
    print("\n[LANGKAH 2] Memproses file halaman*.html...")
    all_data = []
    
    files = sorted(glob.glob("halaman*.html"), key=os.path.getmtime) # Urutkan berdasarkan waktu
    
    if not files:
        print("❌ Tidak ditemukan file halaman*.html! Pastikan Langkah 1 sukses.")
        return

    for file_name in files:
        try:
            with open(file_name, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Cek validitas konten
            if "laptopLayoutSmall" not in content and "priceBtn" not in content:
                print(f"   ⚠️ {file_name} sepertinya halaman kosong/error. Skip.")
                continue

            data = parse_single_laptop_page(content)
            all_data.extend(data)
            print(f"   ✅ {file_name}: {len(data)} item.")
        except Exception as e:
            print(f"   ❌ Error membaca {file_name}: {e}")

    if all_data:
        df = pd.DataFrame(all_data)
        df['Storage'] = df['Storage'].astype(str).str.strip().replace(r'\s+', ' ', regex=True)
        df.to_csv(FILE_FINAL_RAW, index=False)
        print(f"   🎉 Data mentah disimpan ke: {os.path.abspath(FILE_FINAL_RAW)}")
        print(f"   (Jumlah Baris: {len(df)})")
    else:
        print("   ⚠️ Tidak ada data laptop yang terekstrak.")

# ================= LANGKAH 3-6: BENCHMARK (Requests biasa cukup) =================
# Menggunakan requests biasa karena situs benchmark jarang memblokir
import requests 

def download_benchmark(url, filename):
    if os.path.exists(filename): 
        return True
    print(f"   Downloading {filename}...")
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        r = requests.get(url, headers=headers)
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(r.text)
        return True
    except:
        return False

def step_3_to_6_benchmarks():
    print("\n[LANGKAH 3-6] Mengurus Benchmark CPU & GPU...")
    
    # CPU
    download_benchmark(URL_CPU_BENCHMARK, "cpu_list.php")
    try:
        with open("cpu_list.php", 'r', encoding='utf-8', errors='ignore') as f:
            soup = BeautifulSoup(f.read(), 'html.parser')
        table = soup.find('table', id='cputable') or soup.find('table')
        if table:
            rows = table.find_all('tr')[1:]
            cpu_data = []
            for row in rows:
                cols = row.find_all('td')
                if len(cols) >= 2:
                    cpu_data.append({
                        'CPU Name': cols[0].get_text(strip=True),
                        'CPU Mark': re.sub(r'[^\d]', '', cols[1].get_text(strip=True))
                    })
            pd.DataFrame(cpu_data).to_csv(FILE_CPU_CSV, index=False)
            print(f"   ✅ CPU Benchmark: {len(cpu_data)} items.")
    except Exception as e:
        print(f"   ❌ Error CPU: {e}")

    # GPU
    download_benchmark(URL_GPU_BENCHMARK, "gpu_list.html")
    try:
        with open("gpu_list.html", 'r', encoding='utf-8', errors='ignore') as f:
            soup = BeautifulSoup(f.read(), 'html.parser')
        table = soup.find('table', id='cputable') or soup.find('table', id='gputable') or soup.find('table')
        if table:
            rows = table.find_all('tr')[1:]
            gpu_data = []
            for row in rows:
                cols = row.find_all('td')
                if len(cols) >= 2:
                    gpu_data.append({
                        'Videocard Name': cols[0].get_text(strip=True),
                        'Passmark G3D Mark': re.sub(r'[^\d]', '', cols[1].get_text(strip=True))
                    })
            pd.DataFrame(gpu_data).to_csv(FILE_GPU_CSV, index=False)
            print(f"   ✅ GPU Benchmark: {len(gpu_data)} items.")
    except Exception as e:
        print(f"   ❌ Error GPU: {e}")

# ================= LANGKAH 7: PREPROCESSING FINAL =================
def step_7_preprocessing():
    print("\n[LANGKAH 7] Preprocessing & Scoring (Final)...")
    
    if not os.path.exists(FILE_FINAL_RAW): return
    
    try:
        df = pd.read_csv(FILE_FINAL_RAW, on_bad_lines='skip', engine='python')
    except: return

    # Load Referensi
    cpu_dict = {}
    if os.path.exists(FILE_CPU_CSV):
        df_cpu = pd.read_csv(FILE_CPU_CSV)
        df_cpu['CPU Name'] = df_cpu['CPU Name'].astype(str).str.replace(r'\s*@.*', '', regex=True).str.lower().str.strip()
        df_cpu['CPU Mark'] = pd.to_numeric(df_cpu['CPU Mark'], errors='coerce').fillna(0).astype(int)
        cpu_dict = dict(zip(df_cpu['CPU Name'], df_cpu['CPU Mark']))

    gpu_dict = {}
    if os.path.exists(FILE_GPU_CSV):
        df_gpu = pd.read_csv(FILE_GPU_CSV)
        df_gpu['Videocard Name'] = df_gpu['Videocard Name'].astype(str).str.lower().str.strip()
        df_gpu['Passmark G3D Mark'] = pd.to_numeric(df_gpu['Passmark G3D Mark'], errors='coerce').fillna(0).astype(int)
        gpu_dict = dict(zip(df_gpu['Videocard Name'], df_gpu['Passmark G3D Mark']))

    def get_cpu_score(name):
        name = str(name).lower()
        best = 0
        longest = 0
        for k, v in cpu_dict.items():
            if k in name and len(k) > longest:
                longest = len(k)
                best = v
        if best > 0: return best
        # Manual Fallback
        if 'm4' in name: return 22000
        if 'm3' in name: return 19000
        if 'i7' in name: return 15000
        if 'i5' in name: return 10000
        if 'ryzen 7' in name: return 16000
        return 3000 

    def get_gpu_score(name):
        name = str(name).lower()
        best = 0
        longest = 0
        for k, v in gpu_dict.items():
            if k in name and len(k) > longest:
                longest = len(k)
                best = v
        if best > 0: return best
        if 'rtx 40' in name: return 20000
        if 'rtx 30' in name: return 15000
        if 'gtx' in name: return 6000
        return 1500

    def clean_price(val):
        try:
            val = str(val).replace('$','').replace(',','').replace('USD','').strip()
            v = float(val)
            if v > 500000: return int(v)
            return int(v * 16000)
        except: return 0
    
    df['Price_IDR'] = df['Harga_USD'].apply(clean_price)
    df['CPU_Score'] = df['Processor'].apply(get_cpu_score)
    df['GPU_Score'] = df['GPU'].apply(get_gpu_score)
    
    df.to_csv(FILE_FINAL_DATASET, index=False)
    print(f"\n🎉 SUKSES! Dataset Lengkap disimpan di: {os.path.abspath(FILE_FINAL_DATASET)}")
    print(df[['Nama_Laptop', 'CPU_Score', 'GPU_Score', 'Price_IDR']].head())

# ================= MAIN LOOP =================
if __name__ == "__main__":
    print("🚀 Memulai Scraper All-in-One (Mode Browser Otomatis)...")
    start_time = time.time()
    
    step_0_cleanup()
    step_1_fetch_laptops_selenium()
    step_2_process_laptops()
    step_3_to_6_benchmarks()
    step_7_preprocessing()
    
    end_time = time.time()
    print(f"\n⏱️ Selesai dalam {end_time - start_time:.2f} detik.")