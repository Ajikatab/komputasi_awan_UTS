from flask import Flask, render_template_string
import boto3
import pymysql

app = Flask(__name__)

# Konfigurasi
BUCKET_NAME = 'ecommerce-product-images-boms '  # Ganti dengan nama bucket kamu
DB_HOST = 'ecommerce-dbs.cjeue8yksxiv.ap-southeast-1.rds.amazonaws.com'  # Endpoint RDS kamu
DB_USER = 'admin'  # Username RDS
DB_PASSWORD = 'Password123!'  # Password RDS
DB_NAME = 'ecommerce_dbs'  # Nama database di RDS

# Inisialisasi boto3 untuk S3
s3 = boto3.client('s3')

# Fungsi untuk mendapatkan URL gambar produk dari S3
def get_image_url_from_s3(bucket_name, file_name):
    url = s3.generate_presigned_url('get_object', Params={'Bucket': bucket_name, 'Key': file_name}, ExpiresIn=3600)
    return url

#  Fungsi untuk mendapatkan koneksi ke RDS MySQL
def get_rds_connection():
    connection = pymysql.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME,
        cursorclass=pymysql.cursors.DictCursor
    )
    return connection

# Fungsi untuk mendapatkan semua produk dari database
def get_products():
    connection = get_rds_connection()
    with connection:
        with connection.cursor() as cursor:
            cursor.execute("SELECT product_id, name, description FROM products")
            products = cursor.fetchall()
            return products

# Endpoint untuk menampilkan daftar produk
@app.route('/')
def index():
    # Ambil data produk dari database
    products_data = get_products()
    
    # Lengkapi data produk dengan URL gambar dari S3 dan harga dari database
    products = []
    for product in products_data:
        product_id = product['product_id']
        product['image_url'] = get_image_url_from_s3(BUCKET_NAME, f'product_{product_id}.jpg')
        product['price'] = get_product_price(product_id)
        products.append(product)

    # HTML untuk tampilan halaman
    html_code = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Product List</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                background-color: #f4f4f9;
                margin: 0;
                padding: 0;
            }
            .container {
                width: 80%;
                margin: 20px auto;
            }
            h1 {
                text-align: center;
                margin-bottom: 40px;
            }
            .product-list {
                display: flex;
                flex-wrap: wrap;
                justify-content: space-around;
                gap: 20px;
            }
            .product-card {
                background: white;
                border-radius: 10px;
                box-shadow: 0px 4px 10px rgba(0,0,0,0.1);
                width: 250px;
                padding: 20px;
                text-align: center;
            }
            .product-card img {
                width: 100%;
                height: 200px;
                object-fit: cover;
                border-radius: 10px;
            }
            .product-card h2 {
                margin: 10px 0;
                font-size: 20px;
            }
            .product-card p {
                margin: 5px 0;
                color: #555;
            }
            .product-card .price {
                font-weight: bold;
                color: #27ae60;
                margin-top: 10px;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Our Products</h1>
            <div class="product-list">
                {% for product in products %}
                    <div class="product-card">
                        <img src="{{ product.image_url }}" alt="Product Image">
                        <h2>{{ product.name }}</h2>
                        <p>{{ product.description }}</p>
                        <p class="price">${{ product.price }}</p>
                    </div>
                {% endfor %}
            </div>
        </div>
    </body>
    </html>
    """
    return render_template_string(html_code, products=products)

# Fungsi untuk mendapatkan harga produk dari database
def get_product_price(product_id):
    connection = get_rds_connection()
    with connection:
        with connection.cursor() as cursor:
            cursor.execute("SELECT price FROM products WHERE product_id = %s", (product_id,))
            result = cursor.fetchone()
            return result['price'] if result else None

if __name__ == '__main__':
    # Jalankan Flask di semua IP dengan port 80
    app.run(host='0.0.0.0', port=80)
