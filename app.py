from flask import Flask, render_template, request
from expertsystem import SistemPakarLaptop
import pandas as pd

app = Flask(__name__)

# Inisialisasi Sistem Pakar sekali saja
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
            # Bersihkan input budget
            raw_budget = request.form.get('budget', '').replace('.', '').replace(',', '')
            input_budget = int(raw_budget)
            selected_cat = request.form.get('category')

            # Panggil logika expertsystem.py
            hasil = sistem.rekomendasi(input_budget, selected_cat)

            # Logika Pengecekan Hasil dari expertsystem.py
            if isinstance(hasil, pd.DataFrame):
                # Cek jika expertsystem mengembalikan pesan error dalam DataFrame
                if 'Pesan' in hasil.columns:
                    # Ambil pesan error dari baris pertama
                    error_msg = hasil.iloc[0]['Pesan']
                elif not hasil.empty:
                    # Hasil sukses -> Convert ke dictionary
                    recommendations = hasil.to_dict('records')
                else:
                    error_msg = "Tidak ditemukan hasil yang sesuai."
            else:
                error_msg = "Terjadi kesalahan pada sistem pakar."

        except ValueError:
            error_msg = "Mohon masukkan angka budget yang valid."
        except Exception as e:
            error_msg = f"Terjadi kesalahan internal: {e}"

    return render_template('index.html', 
                           recommendations=recommendations, 
                           error=error_msg,
                           last_budget=input_budget,
                           last_cat=selected_cat)

if __name__ == '__main__':
    app.run(debug=True)
