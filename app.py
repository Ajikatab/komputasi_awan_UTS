from flask import Flask, render_template
import pymysql

app = Flask(__name__)

# koneksi ke database RDS
connection = pymysql.connect(
    host='ecommerce-dbs.cjeue8yksxiv.ap-southeast-1.rds.amazonaws.com',
    user='admin',
    password='Password123!',
    database='ecommerce_dbs'
)

@app.route('/')
def home():
    cursor = connection.cursor()
    cursor.execute("SELECT name, price, image_url FROM product")
    product = cursor.fetchall()
    return render_template('index.html', product=product)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80)


# # Konfigurasi
# BUCKET_NAME = 'ecommerce-product-images-boms'  # Ganti dengan nama bucket kamu
# DB_HOST = 'ecommerce-dbs.cjeue8yksxiv.ap-southeast-1.rds.amazonaws.com'  # Endpoint RDS kamu
# DB_USER = 'admin'  # Username RDS
# DB_PASSWORD = 'Password123!'  # Password RDS
# DB_NAME = 'ecommerce_dbs'  # Nama database di RDS



