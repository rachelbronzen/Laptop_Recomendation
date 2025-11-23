from flask import Flask, render_template, request
from expertsystem import SistemPakarLaptop
import pandas as pd

app = Flask(__name__)

# Inisialisasi Sistem Pakar sekali saja saat aplikasi mulai
# Pastikan nama file CSV sesuai dengan yang ada di folder Anda
FILENAME = "dataset_final_super_lengkap.csv"
try:
    sistem = SistemPakarLaptop(FILENAME)
    print("Sistem Pakar Berhasil Dimuat!")
except Exception as e:
    print(f"Error memuat sistem: {e}")

@app.route('/', methods=['GET', 'POST'])
def index():
    recommendations = None
    error_msg = None
    input_budget = ""
    selected_cat = ""

    if request.method == 'POST':
        try:
            # Ambil data dari form HTML
            # Hapus titik atau koma jika user input "15.000.000"
            raw_budget = request.form.get('budget', '').replace('.', '').replace(',', '')
            input_budget = int(raw_budget)
            selected_cat = request.form.get('category')

            # Panggil fungsi rekomendasi dari expertsystem.py
            hasil = sistem.rekomendasi(input_budget, selected_cat)

            # Cek apakah hasil berupa DataFrame valid
            if isinstance(hasil, pd.DataFrame) and not hasil.empty:
                # Convert DataFrame ke Dictionary agar bisa dibaca HTML
                recommendations = hasil.to_dict('records')
            elif isinstance(hasil, pd.DataFrame) and hasil.empty:
                error_msg = "Tidak ditemukan laptop dengan kriteria tersebut."
            else:
                # Jika return string error dari sistem pakar
                error_msg = hasil

        except ValueError:
            error_msg = "Mohon masukkan angka budget yang valid."

    return render_template('index.html', 
                           recommendations=recommendations, 
                           error=error_msg,
                           last_budget=input_budget,
                           last_cat=selected_cat)

if __name__ == '__main__':
    app.run(debug=True)