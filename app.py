from flask import Flask, render_template
import pymysql

app = Flask(__name__)

# Konfigurasi koneksi ke database RDS
DB_CONFIG = {
    'host': 'ecommerce-dbs.cjeue8yksxiv.ap-southeast-1.rds.amazonaws.com',
    'user': 'admin',
    'password': 'Password123!',
    'database': 'ecommerce_dbs'
}

# Fungsi untuk mendapatkan koneksi ke database
def get_db_connection():
    return pymysql.connect(**DB_CONFIG)

@app.route('/')
def home():
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT product_id, name, description, price, image_url FROM products")
            products = cursor.fetchall()
    finally:
        connection.close()

    return render_template('index.html', products=products)

if __name__ == "__main__":
    # Jalankan Flask di semua IP dengan port 80
    app.run(host='0.0.0.0', port=80)
