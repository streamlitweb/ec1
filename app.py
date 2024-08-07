import streamlit as st
import sqlite3
from urllib.parse import quote

# Initialize SQLite database connection
def get_db_connection():
    if 'db_conn' not in st.session_state:
        st.session_state.db_conn = sqlite3.connect('ecommerce.db', check_same_thread=False)
        st.session_state.db_cursor = st.session_state.db_conn.cursor()
        # Create products table if it doesn't exist
        st.session_state.db_cursor.execute('''
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                price REAL NOT NULL
            )
        ''')
        st.session_state.db_conn.commit()
    return st.session_state.db_conn, st.session_state.db_cursor

# Get the database connection and cursor
conn, c = get_db_connection()

# Initialize session state for cart
if 'cart' not in st.session_state:
    st.session_state.cart = []

# Admin password
ADMIN_PASSWORD = "jaishrishyam"

# Function to add product to cart
def add_to_cart(product_id):
    c.execute("SELECT * FROM products WHERE id=?", (product_id,))
    product = c.fetchone()
    if product:
        st.session_state.cart.append({'id': product[0], 'name': product[1], 'price': product[2]})
    st.write("Select cart from side menu to complete the order")

# Function to display products
def display_products():
    st.write("### Products")
    c.execute("SELECT * FROM products")
    products = c.fetchall()
    for product in products:
        st.write(f"**{product[1]}**")
        st.write(f"Price: INR{product[2]}")
        st.button("Add to Cart", key=product[0], on_click=add_to_cart, args=(product[0],))

# Function to display cart
def display_cart():
    st.write("### Cart")
    if st.session_state.cart:
        total = 0
        for item in st.session_state.cart:
            st.write(f"**{item['name']}** - INR{item['price']}")
            total += item['price']
        st.write(f"**Total: INR{total}**")
        contact_number = st.text_input("Enter your contact number:")
        if st.button("Buy Now"):
            st.session_state.contact_number = contact_number
            redirect_to_whatsapp(contact_number, st.session_state.cart)
    else:
        st.write("Your cart is empty.")
# Function to store order in database
def store_order(contact_number, cart, total):
    product_details = ", ".join([f"{item['name']} (${item['price']})" for item in cart])
    c.execute("INSERT INTO orders (contact_number, product_details, total_price) VALUES (?, ?, ?)",
              (contact_number, product_details, total))
    conn.commit()

# Function to redirect to WhatsApp
def redirect_to_whatsapp(contact_number, cart):
    message = "I'm interested in buying:\n"
    for item in cart:
        message += f"{item['name']} - INR{item['price']}\n"
    message += f"Total: INR{sum(item['price'] for item in cart)}"
    encoded_message = quote(message)
    whatsapp_url = f"https://wa.me/+917992328881?text={encoded_message}"
    st.markdown(f"[Click here to complete your purchase on WhatsApp]({whatsapp_url})", unsafe_allow_html=True)

# Admin functions
def add_product(name, price):
    c.execute("INSERT INTO products (name, price) VALUES (?, ?)", (name, price))
    conn.commit()

def update_product(product_id, new_name, new_price):
    c.execute("UPDATE products SET name = ?, price = ? WHERE id = ?", (new_name, new_price, product_id))
    conn.commit()

def delete_product(product_id):
    c.execute("DELETE FROM products WHERE id = ?", (product_id,))
    conn.commit()

# Main app
st.title("My_key_store")

menu = ["Home", "Cart", "Admin"]
choice = st.sidebar.selectbox("Menu", menu)

if choice == "Home":
    display_products()
elif choice == "Cart":
    display_cart()
elif choice == "Admin":
    st.write("### Admin Interface")
    password = st.text_input("Enter password", type="password")
    if password == ADMIN_PASSWORD:
        st.success("Access granted")
        admin_action = st.selectbox("Action", ["Add Product", "Update Product", "Delete Product"])
        
        if admin_action == "Add Product":
            product_name = st.text_input("Product Name")
            product_price = st.number_input("Product Price", min_value=0.0)
            if st.button("Add Product"):
                add_product(product_name, product_price)
                st.success(f"Added {product_name} to the database.")
        
        elif admin_action == "Update Product":
            product_id = st.number_input("Product ID", min_value=1)
            new_product_name = st.text_input("New Product Name")
            new_product_price = st.number_input("New Product Price", min_value=0.0)
            if st.button("Update Product"):
                update_product(product_id, new_product_name, new_product_price)
                st.success(f"Updated product with ID {product_id}.")
        
        elif admin_action == "Delete Product":
            product_id = st.number_input("Product ID", min_value=1)
            if st.button("Delete Product"):
                delete_product(product_id)
                st.success(f"Deleted product with ID {product_id}.")
    else:
        st.error("Access denied")
