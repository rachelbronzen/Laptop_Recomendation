from flask import Flask, render_template, request
from expertsystem import SistemPakarLaptop

app = Flask(__name__)

# Inisialisasi Sistem Pakar
FILENAME = "dataset_final_super_lengkap.csv"
try:
    sistem = SistemPakarLaptop(FILENAME)
    print("Sistem Pakar Berhasil Dimuat!")
except Exception as e:
    print(f"Error memuat sistem: {e}")

@app.route('/', methods=['GET', 'POST'])
def index():
    # Variables for template
    result_data = []
    error_msg = None
    input_budget = ""
    selected_cat = ""
    selected_sub = ""
    search_query = ""
    selected_brand = "ALL"
    
    # Pagination & Sorting Defaults
    current_page = 1
    total_pages = 1
    sort_option = "score" 

    if request.method == 'POST':
        try:
            # 1. Ambil Parameter Dasar
            raw_budget = request.form.get('budget', '').replace('.', '').replace(',', '')
            input_budget = int(raw_budget) if raw_budget else 0
            selected_cat = request.form.get('category')
            selected_sub = request.form.get('sub_category')
            
            # 2. Ambil Parameter Baru (Search & Brand)
            search_query = request.form.get('search_query', '')
            selected_brand = request.form.get('brand_filter', 'ALL')

            # 3. Ambil Parameter Pagination & Sorting
            try: current_page = int(request.form.get('page', 1))
            except: current_page = 1
            
            sort_option = request.form.get('sort_option', 'score')

            # 4. Validasi Dasar (Kecuali jika SHOW_ALL, sub_category dihandle sistem)
            if not selected_cat:
                raise ValueError("Mohon pilih kategori utama.")
            if selected_cat != "SHOW_ALL" and not selected_sub:
                raise ValueError("Mohon pilih sub-kategori.")

            # 5. Panggil Engine dengan Parameter Baru
            hasil = sistem.rekomendasi(
                input_budget, 
                selected_cat, 
                selected_sub, 
                search_query=search_query,     # NEW
                brand_filter=selected_brand,   # NEW
                sort_option=sort_option, 
                page=current_page,
                per_page=24
            )

            if hasil['total_items'] > 0:
                result_data = hasil['data']
                total_pages = hasil['total_pages']
                current_page = hasil['current_page']
            else:
                error_msg = "Tidak ditemukan laptop yang sesuai kriteria/filter ini."

        except ValueError as ve:
            error_msg = str(ve) if str(ve) else "Mohon masukkan data yang valid."
        except Exception as e:
            error_msg = f"Internal Error: {e}"

    # Kirim daftar brand ke template untuk dropdown
    brands_list = sistem.get_brands()
    brands_list.sort()

    return render_template('index.html', 
                           recommendations=result_data, 
                           error=error_msg,
                           last_budget=input_budget,
                           last_cat=selected_cat,
                           last_sub=selected_sub,
                           last_search=search_query,    # NEW
                           last_brand=selected_brand,   # NEW
                           current_page=current_page,
                           total_pages=total_pages,
                           current_sort=sort_option,
                           brands=brands_list)          # NEW

if __name__ == '__main__':
    app.run(debug=True)