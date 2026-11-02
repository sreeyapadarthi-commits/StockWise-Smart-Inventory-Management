
import streamlit as st
import sqlite3
import pandas as pd

# ---------------- PAGE SETTINGS ----------------
st.set_page_config(
    page_title="StockWise",
    page_icon="📦",
    layout="wide"
)

# ---------------- DATABASE ----------------
conn = sqlite3.connect("stockwise.db")

conn.execute("""
CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    category TEXT,
    quantity INTEGER,
    price REAL
)
""")

st.title("📦 StockWise")
st.subheader("Smart Inventory & Stock Management System")
st.write("Manage products, monitor stock, and track inventory.")

# ---------------- ADD PRODUCT ----------------
st.divider()
st.subheader("➕ Add New Product")

with st.form("product_form"):
    name = st.text_input("Product Name")

    category = st.selectbox(
        "Category",
        ["Electronics", "Clothing", "Food", "Stationery", "Other"]
    )

    quantity = st.number_input(
        "Quantity", min_value=0, step=1
    )

    price = st.number_input(
        "Price per Item (₹)", min_value=0.0, step=10.0
    )

    submitted = st.form_submit_button("Save Product")

    if submitted:
        if name.strip():

            existing = conn.execute(
                "SELECT id FROM products WHERE LOWER(name) = LOWER(?)",
                (name.strip(),)
            ).fetchone()

            if existing:
                st.warning("Product already exists!")

            else:
                conn.execute(
                    """INSERT INTO products
                    (name, category, quantity, price)
                    VALUES (?, ?, ?, ?)""",
                    (name.strip(), category, quantity, price)
                )

                conn.commit()
                st.success(f"{name} added successfully!")

        else:
            st.error("Please enter a product name.")

# ---------------- LOAD DATA ----------------
df = pd.read_sql_query(
    "SELECT * FROM products",
    conn
)

# ---------------- DASHBOARD ----------------
st.divider()
st.subheader("📊 Inventory Dashboard")

col1, col2, col3 = st.columns(3)

col1.metric("Total Products", len(df))

low_stock_count = (
    int((df["quantity"] <= 5).sum())
    if not df.empty else 0
)

col2.metric("Low Stock Items", low_stock_count)

inventory_value = (
    (df["quantity"] * df["price"]).sum()
    if not df.empty else 0
)

col3.metric(
    "Inventory Value",
    f"₹{inventory_value:,.2f}"
)

# ---------------- PRODUCT SEARCH ----------------
st.divider()
st.subheader("🔍 Search Product")

search_name = st.text_input("Enter product name")

if search_name:
    search_results = df[
        df["name"].str.contains(
            search_name,
            case=False,
            na=False
        )
    ]

    if not search_results.empty:
        st.dataframe(search_results, use_container_width=True)
    else:
        st.warning("Product not found!")

# ---------------- PRODUCT INVENTORY ----------------
st.divider()
st.subheader("📋 Product Inventory")

if not df.empty:

    st.dataframe(df, use_container_width=True)

    low_stock = df[df["quantity"] <= 5]

    if not low_stock.empty:
        st.warning("⚠️ Some products have low stock!")

        st.dataframe(
            low_stock[["name", "quantity"]],
            use_container_width=True
        )

else:
    st.info("No products yet. Add your first product above.")

# ---------------- UPDATE AND DELETE ----------------
st.divider()
st.subheader("🛠️ Manage Products")

if not df.empty:

    product_names = df["name"].tolist()

    selected_product = st.selectbox(
        "Select Product to Manage",
        product_names
    )

    product = df[df["name"] == selected_product].iloc[0]

    st.write("Current Quantity:", int(product["quantity"]))

    new_quantity = st.number_input(
        "Update Quantity",
        min_value=0,
        step=1,
        value=int(product["quantity"]),
        key="update_quantity"
    )

    col_update, col_delete = st.columns(2)

    with col_update:

        if st.button("Update Stock"):

            conn.execute(
                "UPDATE products SET quantity = ? WHERE id = ?",
                (new_quantity, int(product["id"]))
            )

            conn.commit()

            st.success("Stock updated successfully!")
            st.rerun()

    with col_delete:

        if st.button("Delete Product"):

            conn.execute(
                "DELETE FROM products WHERE id = ?",
                (int(product["id"]),)
            )

            conn.commit()

            st.success("Product deleted!")
            st.rerun()

else:
    st.info("Add products first to manage inventory.")