from flask import Flask, render_template, redirect, url_for, request, session
import csv 

app = Flask(__name__)
app.secret_key = 'ilham_yovy'

# Fungsi membaca data csv
def read_data(file_path):
    data = []
    with open(file_path, "r") as csv_file:
        reader = csv.DictReader(csv_file)
        for row in reader:
            row['harga'] = float(row['harga'].replace('.', '').replace(',', ''))
            data.append(row)
    return data

# Fungsi memformat harga dengan pemisah ribuan (.)
def format_harga(value):
    return "{:,.0f}".format(value)

# Menambahkan filter ke Jinja2
app.jinja_env.filters['format_harga'] = format_harga

# Rute untuk menampilkan data berdasarkan kategori
@app.route('/kategori/<kategori>')
def show_by_category(kategori):
    # Mendapatkan parameter dari query string
    sort_option = request.args.get('sort', default='none', type=str)
    search_query = request.args.get('search', default='', type=str)
    
    # Membaca data dari file CSV
    data_path = 'data_toko.csv'
    data = read_data(data_path)
    
    # Menggunakan list comprehension untuk melakukan filtering berdasarkan kategori
    filtered_data = [item for item in data if item['kategori'].lower() == kategori.lower()]
    
    # Menentukan cara pengurutan
    if sort_option == 'asc':
        filtered_data = sorted(filtered_data, key=lambda x: float(x['harga']))
    elif sort_option == 'desc':
        filtered_data = sorted(filtered_data, key=lambda x: float(x['harga']), reverse=True)
    
    # Filtering berdasarkan pencarian menggunakan linear search
    if search_query:
        search_results = [item for item in filtered_data if search_query.lower() in item['nama_barang'].lower()]
        filtered_data = search_results

    # Render template dengan data yang telah difilter
    return render_template('kategori.html', data=filtered_data, kategori=kategori, search_query=search_query)

# Menambahkan rute untuk mengurutkan data berdasarkan harga terendah
@app.route('/sort/asc')
def sort_asc():
    data_path = 'data_toko.csv'
    data = read_data(data_path)
    sorted_data = sorted(data, key=lambda x: float(x['harga']))
    return render_template('product.html', data=sorted_data)

# Menambahkan rute untuk mengurutkan data berdasarkan harga tertinggi
@app.route('/sort/desc')
def sort_desc():
    data_path = 'data_toko.csv'
    data = read_data(data_path)
    sorted_data = sorted(data, key=lambda x: float(x['harga']), reverse=True)
    return render_template('product.html', data=sorted_data)

# Rute beranda
@app.route("/")
def home():
    keranjang = session.get('keranjang', [])
    data_path = 'data_toko.csv'
    data = read_data(data_path)
    
    return render_template('home.html', keranjang=keranjang, data=data)

# Rute untuk menampilkan semua barang
@app.route('/daftar_barang')
def daftar_barang():
    search_query = request.args.get('search', default='', type=str)
    data_path = 'data_toko.csv'
    data = read_data(data_path)

    # Lakukan pencarian menggunakan linear search
    search_results = [item for item in data if search_query.lower() in item['nama_barang'].lower()]

    # Render template dengan data yang telah difilter
    return render_template('product.html', data=search_results, search_query=search_query, keranjang=session.get('keranjang', []))


# Rute untuk menambahkan barang ke keranjang
@app.route('/tambah_ke_keranjang', methods=['POST'])
def tambah_ke_keranjang():
    if request.method == 'POST':
        try:
            nama_barang = request.form['nama_barang']
            harga = float(request.form['harga'])

            if 'keranjang' not in session:
                session['keranjang'] = []

            session['keranjang'].append({
                'nama_barang': nama_barang,
                'harga': harga
            })

            return redirect(url_for('daftar_barang'))
        except KeyError:
            return "Invalid request. Missing 'nama_barang' or 'harga' in the form data."
    return render_template('keranjang.html')

# Rute untuk menampilkan keranjang
@app.route('/keranjang')
def keranjang():
    keranjang = session.get('keranjang', [])
    return render_template('keranjang.html', keranjang=keranjang)


# Rute untuk halaman fashion
@app.route('/fashion')
def fashion():
    return render_template('fashion.html')

if __name__ == '__main__':
    app.run(debug=True)
