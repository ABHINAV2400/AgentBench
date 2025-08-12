from flask import Flask, request, jsonify, render_template_string
import threading
import time
import json

app = Flask(__name__)

# Mock e-commerce site data
products = [
    {"id": 1, "name": "Laptop", "price": 999.99, "category": "Electronics", "in_stock": True},
    {"id": 2, "name": "Mouse", "price": 29.99, "category": "Electronics", "in_stock": True},
    {"id": 3, "name": "Keyboard", "price": 79.99, "category": "Electronics", "in_stock": False},
    {"id": 4, "name": "Monitor", "price": 299.99, "category": "Electronics", "in_stock": True}
]

shopping_cart = []

@app.route('/')
def home():
    return render_template_string('''
    <html>
    <head><title>MockStore</title></head>
    <body>
        <h1>Welcome to MockStore</h1>
        <nav>
            <a href="/products">Products</a> |
            <a href="/cart">Cart</a> |
            <a href="/search">Search</a>
        </nav>
        <p>Welcome to our online store!</p>
    </body>
    </html>
    ''')

@app.route('/products')
def products_page():
    products_html = ""
    for p in products:
        stock_status = "In Stock" if p["in_stock"] else "Out of Stock"
        products_html += f'''
        <div class="product" data-id="{p["id"]}">
            <h3>{p["name"]}</h3>
            <p>Price: ${p["price"]}</p>
            <p>Category: {p["category"]}</p>
            <p>Status: {stock_status}</p>
            <button onclick="addToCart({p["id"]})" {"disabled" if not p["in_stock"] else ""}>
                Add to Cart
            </button>
        </div>
        '''
    
    return render_template_string(f'''
    <html>
    <head><title>Products - MockStore</title></head>
    <body>
        <h1>Products</h1>
        <nav><a href="/">Home</a> | <a href="/cart">Cart</a></nav>
        {products_html}
        <script>
        function addToCart(productId) {{
            fetch('/api/cart/add', {{
                method: 'POST',
                headers: {{'Content-Type': 'application/json'}},
                body: JSON.stringify({{product_id: productId}})
            }});
        }}
        </script>
    </body>
    </html>
    ''')

@app.route('/cart')
def cart_page():
    cart_html = ""
    total = 0
    for item in shopping_cart:
        product = next(p for p in products if p["id"] == item["product_id"])
        total += product["price"] * item["quantity"]
        cart_html += f'''
        <div class="cart-item">
            <h4>{product["name"]}</h4>
            <p>Price: ${product["price"]}</p>
            <p>Quantity: {item["quantity"]}</p>
        </div>
        '''
    
    return render_template_string(f'''
    <html>
    <head><title>Cart - MockStore</title></head>
    <body>
        <h1>Shopping Cart</h1>
        <nav><a href="/">Home</a> | <a href="/products">Products</a></nav>
        {cart_html}
        <p><strong>Total: ${total:.2f}</strong></p>
        <button onclick="checkout()">Checkout</button>
        <script>
        function checkout() {{
            fetch('/api/checkout', {{method: 'POST'}})
            .then(response => response.json())
            .then(data => alert(data.message));
        }}
        </script>
    </body>
    </html>
    ''')

@app.route('/search')
def search_page():
    query = request.args.get('q', '')
    results = []
    if query:
        results = [p for p in products if query.lower() in p["name"].lower()]
    
    results_html = ""
    for p in results:
        results_html += f'''
        <div class="search-result">
            <h4>{p["name"]}</h4>
            <p>Price: ${p["price"]}</p>
        </div>
        '''
    
    return render_template_string(f'''
    <html>
    <head><title>Search - MockStore</title></head>
    <body>
        <h1>Search Products</h1>
        <nav><a href="/">Home</a> | <a href="/products">Products</a></nav>
        <form method="GET">
            <input type="text" name="q" value="{query}" placeholder="Search products...">
            <button type="submit">Search</button>
        </form>
        {results_html}
    </body>
    </html>
    ''')

# API endpoints
@app.route('/api/cart/add', methods=['POST'])
def add_to_cart():
    data = request.get_json()
    product_id = data.get('product_id')
    
    # Check if product exists and is in stock
    product = next((p for p in products if p["id"] == product_id), None)
    if not product or not product["in_stock"]:
        return jsonify({"error": "Product not available"}), 400
    
    # Add to cart
    existing_item = next((item for item in shopping_cart if item["product_id"] == product_id), None)
    if existing_item:
        existing_item["quantity"] += 1
    else:
        shopping_cart.append({"product_id": product_id, "quantity": 1})
    
    return jsonify({"message": "Added to cart"})

@app.route('/api/checkout', methods=['POST'])
def checkout():
    if not shopping_cart:
        return jsonify({"error": "Cart is empty"}), 400
    
    total = sum(next(p for p in products if p["id"] == item["product_id"])["price"] * item["quantity"] for item in shopping_cart)
    shopping_cart.clear()
    return jsonify({"message": f"Order placed successfully! Total: ${total:.2f}"})

@app.route('/health')
def health():
    return jsonify({"status": "healthy", "service": "web_navigation_mock_server"})

def start_server():
    app.run(host='127.0.0.1', port=8002, debug=False, use_reloader=False)

if __name__ == "__main__":
    start_server()