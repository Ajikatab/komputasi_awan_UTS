from flask import Flask, render_template_string, request, redirect, url_for
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
    # Menghubungkan ke database dan mengambil data produk
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT product_id, name, description, price, image_url FROM products")
            products = cursor.fetchall()
    finally:
        connection.close()

    # HTML template sebagai string
    html_template = """
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
                color: #333;
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
                overflow: hidden;  /* For neat clipping */
                transition: transform 0.3s ease, box-shadow 0.3s ease;
            }
            .product-card:hover {
                transform: translateY(-10px);
                box-shadow: 0px 6px 15px rgba(0,0,0,0.2);
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
                color: #333;
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
            .product-card .description {
                font-size: 14px;
                color: #777;
                margin-top: 5px;
                min-height: 40px;  /* Ensure enough space for description */
            }
            .add-to-cart-btn {
                background-color: #ff6347;
                color: white;
                border: none;
                padding: 10px;
                border-radius: 5px;
                margin-top: 15px;
                cursor: pointer;
                transition: background-color 0.3s ease;
            }
            .add-to-cart-btn:hover {
                background-color: #e55347;
            }
            .delete-btn {
                background-color: #e74c3c;
                color: white;
                border: none;
                padding: 8px;
                border-radius: 5px;
                margin-top: 10px;
                cursor: pointer;
                transition: background-color 0.3s ease;
            }
            .delete-btn:hover {
                background-color: #c0392b;
            }
            .add-product-form {
                margin: 20px auto;
                text-align: center;
                width: 70%;
            }
            .add-product-form input, .add-product-form textarea {
                width: 100%;
                padding: 10px;
                margin-bottom: 10px;
                border-radius: 5px;
                border: 1px solid #ddd;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Our Products</h1>
            <div class="product-list">
                {% for product in products %}
                    <div class="product-card">
                        <img src="{{ product[4] }}" alt="Image of {{ product[1] }}">
                        <h2>{{ product[1] }}</h2>
                        <p class="description">
                            {% if product[2] %}
                                {{ product[2] }}
                            {% else %}
                                No description available
                            {% endif %}
                        </p>
                        <p class="price">${{ product[3] }}</p>
                        <button class="add-to-cart-btn">Add to Cart</button>
                        <form method="POST" action="{{ url_for('delete_product', product_id=product[0]) }}">
                            <button type="submit" class="delete-btn">Delete</button>
                        </form>
                    </div>
                {% endfor %}
            </div>
            <h2>Add New Product</h2>
            <form class="add-product-form" method="POST" action="{{ url_for('add_product') }}">
                <input type="text" name="name" placeholder="Product Name" required>
                <textarea name="description" placeholder="Product Description" required></textarea>
                <input type="number" name="price" placeholder="Price" required>
                <input type="text" name="image_url" placeholder="Image URL" required>
                <button type="submit">Add Product</button>
            </form>
        </div>
    </body>
    </html>
    """
    
    return render_template_string(html_template, products=products)


@app.route('/delete_product/<int:product_id>', methods=['POST'])
def delete_product(product_id):
    # Menghapus produk dari database
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM products WHERE product_id = %s", (product_id,))
            connection.commit()
    finally:
        connection.close()

    # Redirect ke halaman utama setelah penghapusan
    return redirect(url_for('home'))


@app.route('/add_product', methods=['POST'])
def add_product():
    # Menambahkan produk baru ke database
    name = request.form['name']
    description = request.form['description']
    price = request.form['price']
    image_url = request.form['image_url']
    
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                "INSERT INTO products (name, description, price, image_url) VALUES (%s, %s, %s, %s)",
                (name, description, price, image_url)
            )
            connection.commit()
    finally:
        connection.close()

    # Redirect ke halaman utama setelah penambahan produk
    return redirect(url_for('home'))


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80)
