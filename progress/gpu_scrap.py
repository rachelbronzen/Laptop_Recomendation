import re
import pandas as pd
import os

# Konfigurasi Nama File
FILE_INPUT = 'gpu_bm.html'
FILE_OUTPUT = 'gpu_benchmark_score.csv'

def scrape_gpu_benchmark_robust(filename):
    print(f"Membaca file: {filename}...")
    
    try:
        with open(filename, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
    except FileNotFoundError:
        print(f"Error: File {filename} tidak ditemukan.")
        return

    # 1. Cari posisi ID tabel 'cputable' sebagai jangkar (anchor)
    start_marker = 'id="cputable"'
    start_idx = content.find(start_marker)

    if start_idx == -1:
        print("Error: Tabel dengan ID 'cputable' tidak ditemukan dalam file HTML.")
        return

    # 2. Cari tag pembuka <tbody> SETELAH posisi 'cputable'
    tbody_start = content.find('<tbody', start_idx)
    
    if tbody_start == -1:
        print("Error: Tag <tbody> tidak ditemukan setelah header tabel.")
        return

    # 3. Cari tag penutup </tbody>
    tbody_end = content.find('</tbody>', tbody_start)
    
    if tbody_end == -1:
        print("Error: Tag penutup </tbody> tidak ditemukan.")
        return

    # Ambil konten mentah di dalam tbody
    # (+8 untuk menyertakan panjang tag </tbody> agar aman, meski tidak wajib)
    tbody_content = content[tbody_start:tbody_end+8]

    # 4. Pecah menjadi baris-baris (rows) berdasarkan tag <tr>
    # Menggunakan split lebih aman daripada regex untuk blok HTML besar
    rows_raw = tbody_content.split('<tr')
    
    data = []
    # Regex sederhana untuk membersihkan tag HTML (misal: <a>, <span>)
    tag_cleaner = re.compile(r'<.*?>')

    print(f"Memproses {len(rows_raw)} baris data...")

    for row_html in rows_raw:
        # Lewati pecahan yang tidak memiliki sel data
        if '<td' not in row_html:
            continue

        # Ambil semua kolom <td>...</td>
        cols = re.findall(r'<td[^>]*>(.*?)</td>', row_html, re.DOTALL | re.IGNORECASE)

        # Pastikan baris memiliki 5 kolom standar PassMark
        # 0: Name, 1: Score, 2: Rank, 3: Value, 4: Price
        if len(cols) >= 5:
            # Fungsi bantu pembersih
            def clean_cell(raw_html):
                # Hapus tag HTML
                text = re.sub(tag_cleaner, '', raw_html).strip()
                # Ganti entitas HTML umum
                text = text.replace('&nbsp;', ' ').replace('&amp;', '&')
                return text

            name = clean_cell(cols[0])
            mark = clean_cell(cols[1])
            rank = clean_cell(cols[2])
            value = clean_cell(cols[3])
            price = clean_cell(cols[4])

            # Bersihkan field harga dari simbol non-angka untuk analisis (opsional)
            # Jika ingin format asli ($99.99*), biarkan `price` apa adanya.
            # price = price.replace('*', '').replace(',', '').replace('$', '')

            data.append([name, mark, rank, value, price])

    # 5. Simpan ke CSV
    if data:
        headers = [
            'Videocard Name', 
            'Passmark G3D Mark', 
            'Rank', 
            'Videocard Value', 
            'Price (USD)'
        ]
        df = pd.DataFrame(data, columns=headers)
        df.to_csv(FILE_OUTPUT, index=False)
        
        print("-" * 40)
        print(f"✅ SUKSES! Data berhasil diekstrak.")
        print(f"Jumlah Baris: {len(df)}")
        print(f"Disimpan ke : {os.path.abspath(FILE_OUTPUT)}")
        print("-" * 40)
        print("5 Data Teratas:")
        print(df.head().to_markdown(index=False))
    else:
        print("⚠️ Peringatan: Tidak ada data valid yang ditemukan dalam tabel.")

if __name__ == "__main__":
    scrape_gpu_benchmark_robust(FILE_INPUT)