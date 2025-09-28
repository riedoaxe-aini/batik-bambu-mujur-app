import streamlit as st
import pandas as pd
import os
from PIL import Image
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from pathlib import Path
from datetime import datetime, timedelta
import uuid
import hashlib
import base64
import plotly.express as px
import plotly.graph_objects as go
from streamlit_extras.metric_cards import style_metric_cards
from streamlit_extras.stylable_container import stylable_container
from streamlit_extras.dataframe_explorer import dataframe_explorer
import random
import time
import folium
from streamlit_folium import folium_static
import json
from collections import defaultdict
import numpy as np
import io
import requests

# Configure page with better defaults
st.set_page_config(
    page_title="Batik Gallery Admin",
    page_icon="🎨",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://example.com/help',
        'Report a bug': "https://example.com/bug",
        'About': "# Premium Batik Gallery Admin"
    }
)

# --- CONSTANTS ---
DEFAULT_IMAGE = "https://via.placeholder.com/300x300.png?text=Image+Not+Found"
GOOGLE_DRIVE_FOLDER_ID = "1J1sAKu1nUkZFoBVMgcDnmugI1-5Xz1Lf"
SPREADSHEET_ID = "19rQZ2FEBN9FFynlsOdi0okjjAaPSu5lBkGhSJfhg2hg"  # ID dari URL spreadsheet Anda
IMAGE_DIR = "images"
ACTIVITIES_DIR = "activities"
AWARDS_DIR = "awards"
INVENTORY_DIR = "inventory"

# --- LANGUAGE SETTINGS ---
LANGUAGES = {
    "English": {
        "title": "Bamboo Lucky Batik Gallery",
        "subtitle": "Preserving Indonesian Traditional Batik Art",
        "welcome": "Welcome to Our Batik Gallery",
        "description": "Professional management system for hand-drawn batik collections.",
        "featured": "Featured Products",
        "filter": "🔍 Filter Products",
        "search": "Search by name",
        "category": "Category filter",
        "price_range": "Price range (IDR)",
        "all": "All",
        "available": "Available on",
        "manage": "Product Management",
        "activities_manage": "Activities Management",
        "awards_manage": "Awards Management",
        "inventory_manage": "Inventory Management",
        "finance_manage": "Financial Management",
        "production_costs": "Production Costs",
        "hpp_calculator": "HPP Calculator",
        "add": "Add",
        "edit": "Edit",
        "delete": "Delete",
        "login": "Admin Login",
        "logout": "🔒 Logout",
        "dashboard": "Dashboard",
        "analytics": "Analytics",
        "settings": "Settings",
        "view_details": "View Details",
        "description_label": "Description",
        "premium": "Premium Collection",
        "buy_now": "Buy Now",
        "available_on": "Available on:",
        "visitors": "Visitor Statistics",
        "total_visitors": "Total Visitors",
        "unique_visitors": "Unique Visitors",
        "page_views": "Page Views",
        "activities": "Gallery Activities",
        "awards": "Awards & Achievements",
        "location": "Our Location",
        "other_settings": "Other Settings",
        "backup": "Backup Data",
        "restore": "Restore Data",
        "notifications": "Notification Settings",
        "title_label": "Title",
        "date_label": "Date",
        "image_label": "Image",
        "organization_label": "Organization",
        "year_label": "Year",
        "inventory_items": "Inventory Items",
        "current_stock": "Current Stock",
        "minimum_stock": "Minimum Stock",
        "unit": "Unit",
        "add_stock": "Add Stock",
        "reduce_stock": "Reduce Stock",
        "stock_history": "Stock History",
        "transaction_date": "Transaction Date",
        "amount": "Amount",
        "notes": "Notes",
        "inventory_warning": "Inventory Warning",
        "low_stock": "Low Stock Items",
        "out_of_stock": "Out of Stock Items",
        "financial_transactions": "Financial Transactions",
        "income": "Income",
        "expense": "Expense",
        "transaction_type": "Transaction Type",
        "category": "Category",
        "description": "Description",
        "value": "Value (IDR)",
        "balance": "Current Balance",
        "financial_report": "Financial Report",
        "cost_components": "Cost Components",
        "material_cost": "Material Cost",
        "labor_cost": "Labor Cost",
        "overhead_cost": "Overhead Cost",
        "profit_margin": "Profit Margin (%)",
        "calculate_price": "Calculate Selling Price",
        "selling_price": "Selling Price",
        "item_name": "Item Name",
        "item_type": "Item Type",
        "supplier": "Supplier",
        "price_per_unit": "Price Per Unit",
        "total_value": "Total Value",
        "transaction_id": "Transaction ID",
        "inventory_report": "Inventory Report",
        "stock_movement": "Stock Movement",
        "financial_dashboard": "Financial Dashboard",
        "total_income": "Total Income",
        "total_expense": "Total Expense",
        "net_profit": "Net Profit",
        "cost_analysis": "Cost Analysis",
        "add_transaction": "Add Transaction",
        "edit_transaction": "Edit Transaction",
        "delete_transaction": "Delete Transaction",
        "add_component": "Add Component",
        "edit_component": "Edit Component",
        "delete_component": "Delete Component"
    },
    "Indonesia": {
        "title": "Galeri Batik Bambu Mujur",
        "subtitle": "Melestarikan Seni Batik Tradisional Indonesia",
        "welcome": "Selamat Datang di Galeri Batik Kami",
        "description": "Sistem manajemen profesional untuk koleksi batik tulis.",
        "featured": "Produk Unggulan",
        "filter": "🔍 Filter Produk",
        "search": "Cari berdasarkan nama",
        "category": "Filter kategori",
        "price_range": "Rentang harga (Rp)",
        "all": "Semua",
        "available": "Tersedia di",
        "manage": "Kelola Produk",
        "activities_manage": "Kelola Kegiatan",
        "awards_manage": "Kelola Penghargaan",
        "inventory_manage": "Kelola Inventaris",
        "finance_manage": "Kelola Keuangan",
        "production_costs": "Biaya Produksi",
        "hpp_calculator": "Kalkulator HPP",
        "add": "Tambah",
        "edit": "Edit",
        "delete": "Hapus",
        "login": "Login Admin",
        "logout": "🔒 Logout",
        "dashboard": "Dasbor",
        "analytics": "Analitik",
        "settings": "Pengaturan",
        "view_details": "Lihat Detail",
        "description_label": "Deskripsi",
        "premium": "Koleksi Premium",
        "buy_now": "Beli Sekarang",
        "available_on": "Tersedia di:",
        "visitors": "Statistik Pengunjung",
        "total_visitors": "Total Pengunjung",
        "unique_visitors": "Pengunjung Unik",
        "page_views": "Tayangan Halaman",
        "activities": "Galeri Kegiatan",
        "awards": "Penghargaan & Prestasi",
        "location": "Lokasi Kami",
        "other_settings": "Pengaturan Lain",
        "backup": "Backup Data",
        "restore": "Restore Data",
        "notifications": "Pengaturan Notifikasi",
        "title_label": "Judul",
        "date_label": "Tanggal",
        "image_label": "Gambar",
        "organization_label": "Organisasi",
        "year_label": "Tahun",
        "inventory_items": "Item Inventaris",
        "current_stock": "Stok Saat Ini",
        "minimum_stock": "Stok Minimum",
        "unit": "Satuan",
        "add_stock": "Tambah Stok",
        "reduce_stock": "Kurangi Stok",
        "stock_history": "Riwayat Stok",
        "transaction_date": "Tanggal Transaksi",
        "amount": "Jumlah",
        "notes": "Catatan",
        "inventory_warning": "Peringatan Inventaris",
        "low_stock": "Item Stok Rendah",
        "out_of_stock": "Item Stok Habis",
        "financial_transactions": "Transaksi Keuangan",
        "income": "Pemasukan",
        "expense": "Pengeluaran",
        "transaction_type": "Jenis Transaksi",
        "category": "Kategori",
        "description": "Deskripsi",
        "value": "Nilai (Rp)",
        "balance": "Saldo Saat Ini",
        "financial_report": "Laporan Keuangan",
        "cost_components": "Komponent Biaya",
        "material_cost": "Biaya Material",
        "labor_cost": "Biaya Tenaga Kerja",
        "overhead_cost": "Biaya Overhead",
        "profit_margin": "Margin Keuntungan (%)",
        "calculate_price": "Hitung Harga Jual",
        "selling_price": "Harga Jual",
        "item_name": "Nama Item",
        "item_type": "Jenis Item",
        "supplier": "Pemasok",
        "price_per_unit": "Harga Per Unit",
        "total_value": "Total Nilai",
        "transaction_id": "ID Transaksi",
        "inventory_report": "Laporan Inventaris",
        "stock_movement": "Pergerakan Stok",
        "financial_dashboard": "Dasbor Keuangan",
        "total_income": "Total Pemasukan",
        "total_expense": "Total Pengeluaran",
        "net_profit": "Laba Bersih",
        "cost_analysis": "Analisis Biaya",
        "add_transaction": "Tambah Transaksi",
        "edit_transaction": "Edit Transaksi",
        "delete_transaction": "Hapus Transaksi",
        "add_component": "Tambah Komponen",
        "edit_component": "Edit Komponen",
        "delete_component": "Hapus Komponen"
    }
}

# --- ADMIN CONFIGURATION ---
ADMIN_CREDENTIALS = {
    "username": "admin",
    "password": "240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9"  # SHA-256 of "admin123"
}

# --- VISITOR TRACKING ---
if 'visitor_data' not in st.session_state:
    st.session_state.visitor_data = {
        'total_visits': 0,
        'unique_visitors': set(),
        'page_views': 0,
        'daily_stats': defaultdict(lambda: {
            'visits': 0,
            'unique_ips': set(),
            'page_views': 0
        })
    }

def track_visitor():
    """Track visitor statistics with session management"""
    # Generate a unique identifier for this visitor
    visitor_id = str(uuid.uuid4())
    
    # Get current date
    today = datetime.now().date().isoformat()
    
    # Update visitor data
    st.session_state.visitor_data['total_visits'] += 1
    st.session_state.visitor_data['unique_visitors'].add(visitor_id)
    st.session_state.visitor_data['page_views'] += 1
    
    # Update daily stats
    st.session_state.visitor_data['daily_stats'][today]['visits'] += 1
    st.session_state.visitor_data['daily_stats'][today]['unique_ips'].add(visitor_id)
    st.session_state.visitor_data['daily_stats'][today]['page_views'] += 1

# --- HELPER FUNCTIONS ---
def format_price(price, language):
    """Format price with proper currency formatting"""
    if language == "English":
        return f"IDR {price:,.0f}"
    return f"Rp {price:,.0f}".replace(",", ".")

def get_price_step(max_price):
    """Determine appropriate step size based on price range"""
    if max_price > 10000000:  # For premium products (>10jt)
        return 500000
    elif max_price > 1000000:  # For mid-range products (1-10jt)
        return 100000
    else:  # For lower-priced products
        return 10000

def check_admin_credentials(username, password):
    """Verify admin credentials"""
    hashed_input = hashlib.sha256(password.encode()).hexdigest()
    return (username == ADMIN_CREDENTIALS["username"] and 
            hashed_input == ADMIN_CREDENTIALS["password"])

def show_login_form(language):
    """Display admin login form with light styling"""
    with st.form("admin_login"):
        st.subheader(LANGUAGES[language]["login"])
        
        username = st.text_input("Username", key="login_username")
        password = st.text_input("Password", type="password", key="login_password")
        
        submitted = st.form_submit_button("Login", 
                                         type="primary")
        
        if submitted:
            if check_admin_credentials(username, password):
                st.session_state["is_admin"] = True
                st.success("Login successful!" if language == "English" else "Login berhasil!")
                time.sleep(1)
                st.rerun()
            else:
                st.error("Incorrect username or password" if language == "English" else "Username atau password salah")

# --- SIMPLE DATA STORAGE (Fallback) ---
def get_local_data(filename, default_data=None):
    """Get data from local JSON file"""
    try:
        if os.path.exists(filename):
            with open(filename, 'r', encoding='utf-8') as f:
                return json.load(f)
    except:
        pass
    return default_data or []

def save_local_data(filename, data):
    """Save data to local JSON file"""
    try:
        os.makedirs(os.path.dirname(filename) if os.path.dirname(filename) else '.', exist_ok=True)
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        st.error(f"Error saving local data: {str(e)}")
        return False

# --- IMAGE HANDLING ---
def generate_unique_filename(original_name):
    """Generate unique filename to prevent collisions"""
    ext = original_name.split('.')[-1]
    unique_id = uuid.uuid4().hex[:8]
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{timestamp}_{unique_id}.{ext}"

def save_image_local(uploaded_file, directory=IMAGE_DIR):
    """Save uploaded image locally"""
    try:
        # Create directory if it doesn't exist
        os.makedirs(directory, exist_ok=True)
        
        # Generate unique filename
        unique_filename = generate_unique_filename(uploaded_file.name)
        file_path = os.path.join(directory, unique_filename)
        
        # Save file
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        return file_path
        
    except Exception as e:
        st.error(f"❌ Failed to save image locally: {str(e)}")
        return DEFAULT_IMAGE

def get_image_path(image_path):
    """Get image path - return default if not found"""
    if not image_path or image_path == DEFAULT_IMAGE:
        return DEFAULT_IMAGE
    
    # If it's already a URL, return it
    if image_path.startswith('http'):
        return image_path
    
    # If it's a local path, check if file exists
    if os.path.exists(image_path):
        return image_path
    else:
        return DEFAULT_IMAGE

def display_image(image_path, width=300):
    """Safe function to display image"""
    try:
        if not image_path or image_path == DEFAULT_IMAGE:
            st.image(DEFAULT_IMAGE, width=width)
            return False
        
        actual_path = get_image_path(image_path)
        if actual_path == DEFAULT_IMAGE:
            st.image(DEFAULT_IMAGE, width=width)
            return False
        
        st.image(actual_path, width=width)
        return True
            
    except Exception as img_error:
        st.error(f"Error gambar: {str(img_error)}")
        st.image(DEFAULT_IMAGE, width=width)
        return False

# --- DATA OPERATIONS ---
def get_all_products():
    """Get all products from local storage"""
    return get_local_data('data/products.json', get_fallback_products())

def save_all_products(products):
    """Save products to local storage"""
    return save_local_data('data/products.json', products)

def get_all_activities():
    """Get all activities from local storage"""
    return get_local_data('data/activities.json', [])

def save_all_activities(activities):
    """Save activities to local storage"""
    return save_local_data('data/activities.json', activities)

def get_all_awards():
    """Get all awards from local storage"""
    return get_local_data('data/awards.json', [])

def save_all_awards(awards):
    """Save awards to local storage"""
    return save_local_data('data/awards.json', awards)

def get_all_inventory():
    """Get all inventory from local storage"""
    return get_local_data('data/inventory.json', [])

def save_all_inventory(inventory):
    """Save inventory to local storage"""
    return save_local_data('data/inventory.json', inventory)

def get_inventory_history():
    """Get inventory history from local storage"""
    return get_local_data('data/inventory_history.json', [])

def save_inventory_history(history):
    """Save inventory history to local storage"""
    return save_local_data('data/inventory_history.json', history)

def get_financial_transactions():
    """Get financial transactions from local storage"""
    return get_local_data('data/financial_transactions.json', [])

def save_financial_transactions(transactions):
    """Save financial transactions to local storage"""
    return save_local_data('data/financial_transactions.json', transactions)

# --- FALLBACK DATA ---
def get_fallback_products():
    """Return fallback products data"""
    sample_data = [
        {
            "id": 1,
            "name": "Batik Parang Classic",
            "description": "Batik Parang klasik dengan motif tradisional",
            "price": 450000,
            "discount": 0,
            "category": "Traditional",
            "materials": "Katun Prima",
            "creation_date": "2024-01-15",
            "image_path": DEFAULT_IMAGE,
            "shopee_link": "",
            "tokopedia_link": "",
            "other_link": "",
            "payment_methods": "Transfer Bank, COD"
        },
        {
            "id": 2,
            "name": "Batik Mega Mendung",
            "description": "Batik Mega Mendung dengan warna cerah",
            "price": 550000,
            "discount": 10,
            "category": "Traditional",
            "materials": "Sutra Alam",
            "creation_date": "2024-02-20",
            "image_path": DEFAULT_IMAGE,
            "shopee_link": "",
            "tokopedia_link": "",
            "other_link": "",
            "payment_methods": "Transfer Bank"
        },
        {
            "id": 3,
            "name": "Batik Kawung",
            "description": "Batik Kawung motif geometris elegan",
            "price": 350000,
            "discount": 5,
            "category": "Geometric",
            "materials": "Katun Jepang",
            "creation_date": "2024-01-30",
            "image_path": DEFAULT_IMAGE,
            "shopee_link": "",
            "tokopedia_link": "",
            "other_link": "",
            "payment_methods": "Transfer Bank, E-Wallet"
        }
    ]
    return sample_data

# --- VISITOR STATISTICS ---
def get_visitor_data():
    """Get real visitor data from session state"""
    daily_stats = st.session_state.visitor_data['daily_stats']
    
    # Convert to DataFrame for easier plotting
    dates = []
    visits = []
    unique_visitors = []
    page_views = []
    
    for date, stats in daily_stats.items():
        dates.append(date)
        visits.append(stats['visits'])
        unique_visitors.append(len(stats['unique_ips']))
        page_views.append(stats['page_views'])
    
    df = pd.DataFrame({
        'date': pd.to_datetime(dates),
        'visitors': visits,
        'unique_visitors': unique_visitors,
        'page_views': page_views
    }).sort_values('date')
    
    return df

# --- INVENTORY MANAGEMENT FUNCTIONS ---
def update_inventory_item(item_id, amount, transaction_type, notes=""):
    """Update inventory item stock and create history record"""
    try:
        inventory_data = get_all_inventory()
        inventory_df = pd.DataFrame(inventory_data)
        
        # Find item
        item_index = None
        for i, item in enumerate(inventory_data):
            if item['id'] == item_id:
                item_index = i
                break
        
        if item_index is None:
            st.error("Item not found")
            return False
        
        item = inventory_data[item_index]
        
        # Calculate new stock
        if transaction_type == "add":
            new_stock = float(item['current_stock']) + float(amount)
        elif transaction_type == "reduce":
            new_stock = float(item['current_stock']) - float(amount)
            if new_stock < 0:
                st.warning("Stock cannot be negative. Transaction cancelled.")
                return False
        else:
            st.error("Invalid transaction type")
            return False
        
        # Update inventory record
        inventory_data[item_index]['current_stock'] = new_stock
        inventory_data[item_index]['total_value'] = new_stock * float(item['price_per_unit'])
        inventory_data[item_index]['last_updated'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        if save_all_inventory(inventory_data):
            # Create history record
            history_data = get_inventory_history()
            new_history_id = max([h.get('id', 0) for h in history_data], default=0) + 1
            
            history_record = {
                "id": new_history_id,
                "item_id": item_id,
                "transaction_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "transaction_type": transaction_type,
                "amount": amount,
                "notes": notes,
                "unit_price": item['price_per_unit'],
                "total_value": float(amount) * float(item['price_per_unit'])
            }
            
            history_data.append(history_record)
            if save_inventory_history(history_data):
                return True
        return False
    except Exception as e:
        st.error(f"Error updating inventory: {str(e)}")
        return False

# --- FINANCIAL MANAGEMENT FUNCTIONS ---
def calculate_financial_balance():
    """Calculate current financial balance"""
    transactions = get_financial_transactions()
    if not transactions:
        return 0
    
    df = pd.DataFrame(transactions)
    income = df[df['transaction_type'] == 'income']['value'].sum()
    expense = df[df['transaction_type'] == 'expense']['value'].sum()
    return income - expense

# --- HPP CALCULATOR FUNCTIONS ---
def show_hpp_calculator(language):
    """HPP Calculator for Batik Tulis with detailed cost breakdown"""
    st.markdown(f"""
    <h2 style="margin-bottom: 1rem; color: #000000;">Kalkulator HPP Batik Tulis</h2>
    <p style="color: #555; font-size: 16px;">Hitung Harga Pokok Produksi dan Harga Jual untuk Batik Tulis</p>
    """, unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs([
        "🖌️ Input Data Produksi",
        "🧮 Kalkulasi HPP",
        "📊 Hasil & Rekomendasi"
    ])
    
    with tab1:
        input_production_data(language)
    with tab2:
        calculate_hpp(language)
    with tab3:
        show_results(language)

def input_production_data(language):
    """Input production data for HPP calculation"""
    st.markdown(f"<h3 style='color: #000000; margin-bottom: 1.5rem;'>Data Dasar Produksi</h3>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        product_name = st.text_input("Nama Produk Batik", "Batik Tulis Cap Kencana")
        batik_type = st.selectbox(
            "Jenis Batik",
            ["Batik Tulis Pewarna Alami", "Batik Tulis Pewarna Sintetis", "Batik Tulis Kombinasi"],
            help="Pilih jenis batik berdasarkan pewarna yang digunakan"
        )
        fabric_type = st.selectbox(
            "Jenis Kain",
            ["Katun Primissima", "Katun Dobby", "Katun Mori", "Sutera Alam", "Sutera Satin"],
            index=0
        )
    
    with col2:
        fabric_length = st.number_input("Panjang Kain (meter)", min_value=0.1, value=2.5, step=0.1)
        fabric_width = st.number_input("Lebar Kain (meter)", min_value=0.1, value=1.1, step=0.1)
        production_quantity = st.number_input("Jumlah Produksi (pcs)", min_value=1, value=1, step=1)
    
    st.markdown("---")
    st.markdown(f"<h4 style='color: #000000; margin-bottom: 1rem;'>Biaya Bahan Baku</h4>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        fabric_price_per_meter = st.number_input(
            "Harga Kain per Meter (Rp)",
            min_value=0,
            value=45000,
            step=1000,
            help="Harga kain per meter persegi"
        )
    with col2:
        wax_quantity = st.number_input(
            "Kebutuhan Lilin (gram)",
            min_value=0.0,
            value=150.0,
            step=10.0,
            help="Total lilin yang dibutuhkan untuk proses membatik"
        )
        wax_price_per_kg = st.number_input(
            "Harga Lilin per Kg (Rp)",
            min_value=0,
            value=25000,
            step=1000
        )
    with col3:
        dye_type = st.selectbox(
            "Jenis Pewarna",
            ["Pewarna Alami", "Pewarna Sintetis", "Kombinasi"],
            index=1 if "Sintetis" in batik_type else 0
        )
        
        if "Alami" in dye_type:
            dye_price = st.number_input("Harga Pewarna Alami (Rp)", min_value=0, value=150000, step=10000)
        else:
            dye_price = st.number_input("Harga Pewarna per Set (Rp)", min_value=0, value=75000, step=5000)
    
    st.markdown("---")
    st.markdown(f"<h4 style='color: #000000; margin-bottom: 1rem;'>Biaya Tenaga Kerja</h4>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        design_hours = st.number_input(
            "Waktu Membuat Pola (jam)",
            min_value=0.0,
            value=8.0,
            step=0.5,
            help="Waktu yang dibutuhkan untuk membuat pola batik"
        )
        design_hourly_rate = st.number_input(
            "Upah Perancang per Jam (Rp)",
            min_value=0,
            value=25000,
            step=1000
        )
    
    with col2:
        waxing_hours = st.number_input(
            "Waktu Membatik (jam)",
            min_value=0.0,
            value=40.0,
            step=1.0,
            help="Waktu yang dibutuhkan untuk proses membatik dengan lilin"
        )
        batik_artist_hourly_rate = st.number_input(
            "Upah Pembatik per Jam (Rp)",
            min_value=0,
            value=20000,
            step=1000
        )
    
    with col3:
        dyeing_processes = st.number_input(
            "Jumlah Proses Pewarnaan",
            min_value=1,
            value=3,
            step=1,
            help="Berapa kali proses pewarnaan dilakukan"
        )
        dyeing_hours_per_process = st.number_input(
            "Waktu Pewarnaan per Proses (jam)",
            min_value=0.0,
            value=2.0,
            step=0.5
        )
        dyeing_hourly_rate = st.number_input(
            "Upah Pewarna per Jam (Rp)",
            min_value=0,
            value=15000,
            step=1000
        )
    
    st.markdown("---")
    st.markdown(f"<h4 style='color: #000000; margin-bottom: 1rem;'>Biaya Produksi Lainnya</h4>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        boiling_process = st.selectbox(
            "Proses Pelorodan",
            ["Manual", "Semi-Otomatis", "Otomatis"],
            index=1
        )
        boiling_cost = st.number_input(
            "Biaya Pelorodan (Rp)",
            min_value=0,
            value=15000,
            step=1000,
            help="Biaya untuk proses melorod/mencelup lilin"
        )
    
    with col2:
        color_fixing = st.number_input(
            "Biaya Pengunci Warna (Rp)",
            min_value=0,
            value=10000,
            step=1000,
            help="Biaya bahan untuk mengunci warna"
        )
        drying_cost = st.number_input(
            "Biaya Pengeringan (Rp)",
            min_value=0,
            value=5000,
            step=1000
        )
    
    with col3:
        packaging_cost = st.number_input(
            "Biaya Kemasan (Rp)",
            min_value=0,
            value=15000,
            step=1000,
            help="Biaya packaging dan label"
        )
        overhead_percentage = st.number_input(
            "Overhead (%)",
            min_value=0.0,
            value=15.0,
            step=1.0,
            help="Biaya overhead sebagai persentase dari total biaya"
        )
    
    # Save all inputs to session state
    st.session_state.hpp_data = {
        'product_name': product_name,
        'batik_type': batik_type,
        'fabric_type': fabric_type,
        'fabric_length': fabric_length,
        'fabric_width': fabric_width,
        'production_quantity': production_quantity,
        'fabric_price_per_meter': fabric_price_per_meter,
        'wax_quantity': wax_quantity,
        'wax_price_per_kg': wax_price_per_kg,
        'dye_type': dye_type,
        'dye_price': dye_price,
        'design_hours': design_hours,
        'design_hourly_rate': design_hourly_rate,
        'waxing_hours': waxing_hours,
        'batik_artist_hourly_rate': batik_artist_hourly_rate,
        'dyeing_processes': dyeing_processes,
        'dyeing_hours_per_process': dyeing_hours_per_process,
        'dyeing_hourly_rate': dyeing_hourly_rate,
        'boiling_process': boiling_process,
        'boiling_cost': boiling_cost,
        'color_fixing': color_fixing,
        'drying_cost': drying_cost,
        'packaging_cost': packaging_cost,
        'overhead_percentage': overhead_percentage
    }

def calculate_hpp(language):
    """Calculate HPP based on input data"""
    if 'hpp_data' not in st.session_state:
        st.warning("Silakan input data produksi terlebih dahulu di tab 'Input Data Produksi'")
        return
    
    data = st.session_state.hpp_data
    
    st.markdown(f"<h3 style='color: #000000; margin-bottom: 1.5rem;'>Kalkulasi Harga Pokok Produksi</h3>", unsafe_allow_html=True)
    
    # Calculate material costs
    fabric_area = data['fabric_length'] * data['fabric_width']
    fabric_cost = fabric_area * data['fabric_price_per_meter']
    wax_cost = (data['wax_quantity'] / 1000) * data['wax_price_per_kg']
    dye_cost = data['dye_price']
    
    material_costs = fabric_cost + wax_cost + dye_cost
    
    # Calculate labor costs
    design_labor_cost = data['design_hours'] * data['design_hourly_rate']
    waxing_labor_cost = data['waxing_hours'] * data['batik_artist_hourly_rate']
    dyeing_labor_cost = data['dyeing_processes'] * data['dyeing_hours_per_process'] * data['dyeing_hourly_rate']
    
    labor_costs = design_labor_cost + waxing_labor_cost + dyeing_labor_cost
    
    # Calculate other production costs
    other_costs = (
        data['boiling_cost'] + 
        data['color_fixing'] + 
        data['drying_cost'] + 
        data['packaging_cost']
    )
    
    # Calculate total direct costs
    total_direct_costs = material_costs + labor_costs + other_costs
    
    # Calculate overhead
    overhead_cost = total_direct_costs * (data['overhead_percentage'] / 100)
    
    # Calculate total production cost
    total_production_cost = total_direct_costs + overhead_cost
    
    # Calculate HPP per unit
    hpp_per_unit = total_production_cost / data['production_quantity'] if data['production_quantity'] > 0 else total_production_cost
    
    # Save calculations to session state
    st.session_state.hpp_calculations = {
        'material_costs': material_costs,
        'labor_costs': labor_costs,
        'other_costs': other_costs,
        'overhead_cost': overhead_cost,
        'total_production_cost': total_production_cost,
        'hpp_per_unit': hpp_per_unit,
        'fabric_area': fabric_area
    }
    
    # Display cost breakdown
    st.markdown("### 📊 Rincian Biaya Produksi")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("Biaya Bahan Baku", format_price(material_costs, language))
        st.metric("Biaya Tenaga Kerja", format_price(labor_costs, language))
        st.metric("Biaya Lainnya", format_price(other_costs, language))
    
    with col2:
        st.metric("Overhead", format_price(overhead_cost, language))
        st.metric("Total Biaya Produksi", format_price(total_production_cost, language), 
                 delta=f"Untuk {data['production_quantity']} pcs")
        st.metric("HPP per Unit", format_price(hpp_per_unit, language))

def show_results(language):
    """Show HPP results and pricing recommendations"""
    if 'hpp_calculations' not in st.session_state:
        st.warning("Silakan lakukan kalkulasi HPP terlebih dahulu di tab 'Kalkulasi HPP'")
        return
    
    data = st.session_state.hpp_data
    calculations = st.session_state.hpp_calculations
    
    st.markdown(f"<h3 style='color: #000000; margin-bottom: 1.5rem;'>Rekomendasi Harga Jual</h3>", unsafe_allow_html=True)
    
    # Profit margin input
    profit_margin = st.slider(
        "Margin Keuntungan yang Diinginkan (%)",
        min_value=10,
        max_value=100,
        value=40,
        step=5,
        help="Persentase keuntungan yang ingin diperoleh dari HPP"
    )
    
    # Calculate selling price
    selling_price = calculations['hpp_per_unit'] * (1 + profit_margin / 100)
    
    # Display pricing
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Harga Pokok Produksi", format_price(calculations['hpp_per_unit'], language))
    with col2:
        st.metric("Margin Keuntungan", f"{profit_margin}%")
    with col3:
        st.metric("Harga Jual Recommended", format_price(selling_price, language), 
                 delta=format_price(selling_price - calculations['hpp_per_unit'], language))

# --- UI COMPONENTS ---
def apply_professional_style():
    """Apply a clean white-ui professional styling with dark text"""
    st.markdown("""
    <style>
        .stApp {
            background-color: #f5f5f5;
        }
        .main .block-container {
            padding-top: 2rem;
        }
        h1, h2, h3, h4, h5, h6 {
            color: #000000;
        }
        p, div, span {
            color: #000000;
        }
        .stButton button {
            background-color: #4a6fa5;
            color: white;
            border: none;
            padding: 0.5rem 1rem;
            border-radius: 0.5rem;
        }
        .stButton button:hover {
            background-color: #3a5a85;
        }
    </style>
    """, unsafe_allow_html=True)

def display_header(language):
    """Display premium app header with responsive logo and title"""
    col1, col2 = st.columns([1, 4])
    with col1:
        st.image(DEFAULT_IMAGE, width=120, caption="Logo")
    with col2:
        st.markdown(f"""
        <h1 style="margin-bottom: 0; color: #000000;">{LANGUAGES[language]["title"]}</h1>
        <p style="color: #4a6fa5; font-size: 16px; margin-top: 0.5rem;">{LANGUAGES[language]["subtitle"]}</p>
        """, unsafe_allow_html=True)

# --- PRODUCT CARD ---
def product_card(product, language):
    """Display product card"""
    try:
        product_id = str(product.get("id", uuid.uuid4().hex[:8]))
        product_name = product.get("name", "Unknown Product")
        product_price = float(product.get("price", 0))
        discount = float(product.get("discount", 0))
        discounted_price = product_price * (1 - discount/100) if discount > 0 else product_price
        product_category = product.get("category", "Uncategorized")
        product_description = product.get("description", "No description available")
        product_materials = product.get("materials", "")
        creation_date = product.get("creation_date", "")
        image_path = product.get("image_path", DEFAULT_IMAGE)
        shopee_link = product.get("shopee_link", "")
        tokopedia_link = product.get("tokopedia_link", "")
        other_link = product.get("other_link", "")
        is_premium = product_price > 1500000
        
        # Create card container
        with st.container():
            # Product Image
            display_image(image_path)
            
            # Product Info
            st.markdown(f"<h3 style='color: #000000; margin-bottom: 0.5rem;'>{product_name}</h3>", unsafe_allow_html=True)
            
            # Category and Premium Badge
            col1, col2 = st.columns([3, 1])
            with col1:
                st.markdown(
                    f"""<div style="
                        background: #f0f8ff;
                        color: #4a6fa5;
                        padding: 4px 8px;
                        border-radius: 12px;
                        font-size: 12px;
                        display: inline-block;
                        margin-bottom: 8px;
                    ">{product_category}</div>""",
                    unsafe_allow_html=True
                )
            with col2:
                if is_premium:
                    st.markdown(
                        """<div style="
                            background: linear-gradient(135deg, #FFD700, #DAA520);
                            color: black;
                            padding: 4px 8px;
                            border-radius: 12px;
                            font-size: 12px;
                            text-align: center;
                            margin-bottom: 8px;
                        ">Premium</div>""",
                        unsafe_allow_html=True
                    )
            
            # Price Display with discount
            if discount > 0:
                st.markdown(f"<div style='font-size: 20px; font-weight: 700; color: #e63946;'>{format_price(discounted_price, language)}</div>", unsafe_allow_html=True)
                st.markdown(
                    f"""<div style="
                        text-decoration: line-through;
                        color: #999;
                        font-size: 14px;
                    ">{format_price(product_price, language)}</div>""",
                    unsafe_allow_html=True
                )
                st.markdown(
                    f"""<div style="
                        background: #e63946;
                        color: white;
                        padding: 2px 6px;
                        border-radius: 4px;
                        font-size: 12px;
                        display: inline-block;
                        margin-bottom: 8px;
                    ">{discount}% OFF</div>""",
                    unsafe_allow_html=True
                )
            else:
                st.markdown(f"<div style='font-size: 20px; font-weight: 700; color: #e63946;'>{format_price(product_price, language)}</div>", unsafe_allow_html=True)
            
            # Product Details
            st.markdown(f"<p style='color: #555; font-size: 14px;'><strong>Materials:</strong> {product_materials}</p>", unsafe_allow_html=True)
            st.markdown(f"<p style='color: #555; font-size: 14px; margin-bottom: 12px;'><strong>Creation Date:</strong> {creation_date}</p>", unsafe_allow_html=True)
            
            # Marketplace Links
            if shopee_link or tokopedia_link or other_link:
                st.markdown(f"<p style='color: #555; font-size: 14px; margin-bottom: 8px;'><strong>{LANGUAGES[language]['available_on']}</strong></p>", unsafe_allow_html=True)
                
                links = []
                if shopee_link:
                    links.append(f"[Shopee]({shopee_link})")
                if tokopedia_link:
                    links.append(f"[Tokopedia]({tokopedia_link})")
                if other_link:
                    links.append(f"[Lainnya]({other_link})")
                
                st.markdown(" | ".join(links))
            
            # Description with expander
            with st.expander(LANGUAGES[language]["description_label"]):
                st.write(product_description)
            
            # Only show edit button for admin
            if st.session_state.get("is_admin", False):
                if st.button(
                    "✏️ Edit Product",
                    key=f"edit_{product_id}"
                ):
                    st.session_state['edit_product'] = product_id
    
    except Exception as e:
        st.error(f"Error displaying product: {str(e)}")
        with st.container():
            display_image(DEFAULT_IMAGE)
            st.subheader("Product")
            st.write(f"Price: {format_price(0, language)}")
            st.button("Details", key=f"fallback_{product_id}")

# --- ACTIVITY CARD ---
def activity_card(activity, language):
    """Display an activity card with image and details"""
    try:
        with st.container():
            # Activity Image
            image_path = activity.get("image_path", DEFAULT_IMAGE)
            display_image(image_path)
            
            # Activity Info
            st.markdown(f"<h3 style='color: #000000; margin-bottom: 0.5rem;'>{activity.get('title', 'Unknown Activity')}</h3>", unsafe_allow_html=True)
            
            # Date
            st.markdown(f"<p style='color: #555; font-size: 14px;'><strong>Date:</strong> {activity.get('date', 'Unknown')}</p>", unsafe_allow_html=True)
            
            # Description with expander
            with st.expander(LANGUAGES[language]["description_label"]):
                st.write(activity.get('description', 'No description available'))
            
            # Only show edit button for admin
            if st.session_state.get("is_admin", False):
                if st.button(
                    "✏️ Edit Activity",
                    key=f"edit_activity_{activity.get('id', '')}"
                ):
                    st.session_state['edit_activity'] = activity.get('id', '')
    
    except Exception as e:
        st.error(f"Error displaying activity: {str(e)}")

# --- AWARD CARD ---
def award_card(award, language):
    """Display an award card with image and details"""
    try:
        with st.container():
            # Award Image
            image_path = award.get("image_path", DEFAULT_IMAGE)
            display_image(image_path)
            
            # Award Info
            st.markdown(f"<h3 style='color: #000000; margin-bottom: 0.5rem;'>{award.get('title', 'Unknown Award')}</h3>", unsafe_allow_html=True)
            
            # Organization and Year
            st.markdown(f"<p style='color: #555; font-size: 14px;'><strong>Organization:</strong> {award.get('organization', 'Unknown')}</p>", unsafe_allow_html=True)
            st.markdown(f'<p style="color: #555; font-size: 14px; margin-bottom: 12px;"><strong>Year:</strong> {award.get("year", "Unknown")}</p>', unsafe_allow_html=True)

            # Only show edit button for admin
            if st.session_state.get("is_admin", False):
                if st.button(
                    "✏️ Edit Award",
                    key=f"edit_award_{award.get('id', '')}"
                ):
                    st.session_state['edit_award'] = award.get('id', '')
    
    except Exception as e:
        st.error(f"Error displaying award: {str(e)}")

# --- HOME PAGE ---
def show_home_page(language):
    """Premium home page with featured products and additional sections"""
    try:
        st.markdown(f"""
        <h2 style="margin-bottom: 0.5rem; color: #000000;">{LANGUAGES[language]['welcome']}</h2>
        <p style="color: #555; font-size: 16px; margin-bottom: 2rem;">{LANGUAGES[language]['description']}</p>
        """, unsafe_allow_html=True)
        
        with st.spinner("Memuat produk..."):
            products_data = get_all_products()
        
        if not products_data:
            st.warning("Belum ada produk tersedia")
        else:
            st.markdown(f"""
            <h3 style="margin-bottom: 1rem; color: #000000;">{LANGUAGES[language]["featured"]}</h3>
            """, unsafe_allow_html=True)
            
            sample_size = min(6, len(products_data))
            if sample_size > 0:
                featured = random.sample(products_data, sample_size)
                
                # Display products in a grid
                for i in range(0, len(featured), 3):
                    cols = st.columns(3)
                    for j in range(3):
                        if i + j < len(featured):
                            with cols[j]:
                                product_card(featured[i + j], language)
                        else:
                            with cols[j]:
                                st.empty()
            
        # Gallery Activities Section
        st.markdown("---")
        st.markdown(f"""
        <h3 style="margin-bottom: 1rem; color: #000000;">{LANGUAGES[language]["activities"]}</h3>
        """, unsafe_allow_html=True)
        
        activities_data = get_all_activities()
        if not activities_data:
            st.warning("No activities available" if language == "English" else "Tidak ada kegiatan tersedia")
        else:
            for i in range(0, len(activities_data), 2):
                cols = st.columns(2)
                for j in range(2):
                    if i + j < len(activities_data):
                        with cols[j]:
                            activity_card(activities_data[i + j], language)
        
        # Awards Section
        st.markdown("---")
        st.markdown(f"""
        <h3 style="margin-bottom: 1rem; color: #000000;">{LANGUAGES[language]["awards"]}</h3>
        """, unsafe_allow_html=True)
        
        awards_data = get_all_awards()
        if not awards_data:
            st.warning("No awards available" if language == "English" else "Tidak ada penghargaan tersedia")
        else:
            for i in range(0, len(awards_data), 3):
                cols = st.columns(3)
                for j in range(3):
                    if i + j < len(awards_data):
                        with cols[j]:
                            award_card(awards_data[i + j], language)
        
        # Location Map
        st.markdown("---")
        st.markdown(f"""
        <h3 style="margin-bottom: 1rem; color: #000000;">{LANGUAGES[language]["location"]}</h3>
        """, unsafe_allow_html=True)
        
        # Create a map centered on Indonesia
        m = folium.Map(location=[-6.2088, 106.8456], zoom_start=12, width="100%")
        
        # Add marker for our location
        folium.Marker(
            [-6.2088, 106.8456],
            popup="Bamboo Lucky Batik Gallery",
            tooltip="Our Main Store"
        ).add_to(m)
        
        # Display the map - full width
        folium_static(m, width=None, height=400)
            
    except Exception as e:
        st.error(f"Terjadi kesalahan: {str(e)}")
        if st.button("Coba Lagi"):
            st.rerun()

# --- GALLERY PAGE ---
def show_gallery_page(language):
    """Show all products with filtering options"""
    st.markdown(f"""
    <h2 style="margin-bottom: 1rem; color: #000000;">{LANGUAGES[language]["featured"]}</h2>
    """, unsafe_allow_html=True)
    
    with st.spinner("Memuat produk..."):
        products_data = get_all_products()
    
    if not products_data:
        st.warning("Belum ada produk tersedia")
        return
    
    df = pd.DataFrame(products_data)
    
    # Filter section
    with st.expander(LANGUAGES[language]["filter"], expanded=True):
        col1, col2 = st.columns(2)
        with col1:
            search_query = st.text_input(LANGUAGES[language]["search"], key="product_search")
            category_filter = st.selectbox(
                LANGUAGES[language]["category"],
                ["All"] + df["category"].unique().tolist(),
                key="category_filter"
            )
        with col2:
            max_price = df["price"].max()
            price_range = st.slider(
                LANGUAGES[language]["price_range"],
                0, int(max_price + 100000),
                (0, int(max_price)),
                step=get_price_step(max_price),
                key="price_filter"
            )
    
    # Apply filters
    filtered_data = products_data.copy()
    if search_query:
        filtered_data = [p for p in filtered_data if search_query.lower() in p["name"].lower()]
    if category_filter != "All":
        filtered_data = [p for p in filtered_data if p["category"] == category_filter]
    filtered_data = [p for p in filtered_data if price_range[0] <= p["price"] <= price_range[1]]
    
    if not filtered_data:
        st.warning("No products match the filters" if language == "English" else "Tidak ada produk yang sesuai dengan filter")
    else:
        # Display filtered products in a grid
        for i in range(0, len(filtered_data), 3):
            cols = st.columns(3)
            for j in range(3):
                if i + j < len(filtered_data):
                    with cols[j]:
                        product_card(filtered_data[i + j], language)
                else:
                    with cols[j]:
                        st.empty()

# --- ANALYTICS DASHBOARD ---
def show_analytics_dashboard(language):
    """Show visitor analytics and statistics"""
    st.markdown(f"""
    <h2 style="margin-bottom: 1rem; color: #000000;">{LANGUAGES[language]["analytics"]}</h2>
    """, unsafe_allow_html=True)
    
    # Track visitor for this page view
    track_visitor()
    
    # Get visitor data
    visitor_df = get_visitor_data()
    
    # Display key metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(LANGUAGES[language]["total_visitors"], st.session_state.visitor_data['total_visits'])
    with col2:
        st.metric(LANGUAGES[language]["unique_visitors"], len(st.session_state.visitor_data['unique_visitors']))
    with col3:
        st.metric(LANGUAGES[language]["page_views"], st.session_state.visitor_data['page_views'])
    
    # Visitor trends chart
    if not visitor_df.empty:
        st.markdown(f"""
        <h3 style="margin-top: 2rem; margin-bottom: 1rem; color: #000000;">{LANGUAGES[language]["visitors"]}</h3>
        """, unsafe_allow_html=True)
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=visitor_df['date'],
            y=visitor_df['visitors'],
            mode='lines+markers',
            name='Visits',
            line=dict(color='#4a6fa5')
        ))
        fig.add_trace(go.Scatter(
            x=visitor_df['date'],
            y=visitor_df['unique_visitors'],
            mode='lines+markers',
            name='Unique Visitors',
            line=dict(color='#e63946')
        ))
        fig.add_trace(go.Scatter(
            x=visitor_df['date'],
            y=visitor_df['page_views'],
            mode='lines+markers',
            name='Page Views',
            line=dict(color='#2a9d8f')
        ))
        
        fig.update_layout(
            xaxis_title='Date',
            yaxis_title='Count',
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color="#000000")
        )
        
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("No visitor data available" if language == "English" else "Tidak ada data pengunjung tersedia")

# --- PRODUCT MANAGEMENT PAGE ---
def show_manage_page(language):
    """Product management page for admin"""
    st.markdown(f"""
    <h2 style="margin-bottom: 1rem; color: #000000;">{LANGUAGES[language]["manage"]}</h2>
    """, unsafe_allow_html=True)
    
    operation = st.radio(
        f"{'Select operation:' if language == 'English' else 'Pilih operasi:'}",
        [LANGUAGES[language]["add"], LANGUAGES[language]["edit"], LANGUAGES[language]["delete"]],
        horizontal=True,
        key="product_operation"
    )
    
    products_data = get_all_products()
    
    if operation == LANGUAGES[language]["add"]:
        with st.form("add_product_form", clear_on_submit=True):
            st.markdown(f"<h3 style='color: #000000; margin-bottom: 1.5rem;'>{LANGUAGES[language]['add']} Product</h3>", unsafe_allow_html=True)
            
            col1, col2 = st.columns(2)
            with col1:
                name = st.text_input(f"{'Name' if language == 'English' else 'Nama'}*")
                category = st.text_input(f"{'Category' if language == 'English' else 'Kategori'}*")
                materials = st.text_input(f"{'Materials' if language == 'English' else 'Bahan'}*")
            with col2:
                price = st.number_input(f"{'Price (IDR)' if language == 'English' else 'Harga (Rp)'}*", min_value=0)
                discount = st.number_input(f"{'Discount (%)' if language == 'English' else 'Diskon (%)'}", min_value=0, max_value=100, value=0)
                creation_date = st.date_input(f"{'Creation Date' if language == 'English' else 'Tanggal Pembuatan'}", datetime.now())
            
            description = st.text_area(f"{'Description' if language == 'English' else 'Deskripsi'}*")
            
            # Marketplace links
            st.markdown(f"<h4 style='color: #000000; margin-bottom: 1rem;'>{'Marketplace Links' if language == 'English' else 'Link Marketplace'}</h4>", unsafe_allow_html=True)
            col1, col2, col3 = st.columns(3)
            with col1:
                shopee_link = st.text_input("Shopee")
            with col2:
                tokopedia_link = st.text_input("Tokopedia")
            with col3:
                other_link = st.text_input(f"{'Other' if language == 'English' else 'Lainnya'}")
            
            # Image upload
            uploaded_image = st.file_uploader(
                f"{'Product Image' if language == 'English' else 'Gambar Produk'}", 
                type=["jpg", "jpeg", "png", "webp"]
            )
            
            submitted = st.form_submit_button(f"{'Save Product' if language == 'English' else 'Simpan Produk'}")
            
            if submitted:
                if not all([name, category, materials, price, description]):
                    st.error(f"{'Please fill required fields' if language == 'English' else 'Harap isi field wajib'} (*)")
                else:
                    image_path = DEFAULT_IMAGE
                    if uploaded_image:
                        saved_path = save_image_local(uploaded_image, IMAGE_DIR)
                        if saved_path:
                            image_path = saved_path
                    
                    new_id = max([p.get('id', 0) for p in products_data], default=0) + 1
                    product_data = {
                        "id": new_id,
                        "name": name,
                        "description": description,
                        "price": price,
                        "discount": discount,
                        "category": category,
                        "materials": materials,
                        "creation_date": creation_date.strftime("%Y-%m-%d"),
                        "image_path": image_path,
                        "shopee_link": shopee_link,
                        "tokopedia_link": tokopedia_link,
                        "other_link": other_link,
                        "payment_methods": "Cash, Bank Transfer"
                    }
                    
                    products_data.append(product_data)
                    if save_all_products(products_data):
                        st.success(f"{'Product added successfully!' if language == 'English' else 'Produk berhasil ditambahkan!'}")
                        st.balloons()

    elif operation == LANGUAGES[language]["edit"]:
        if not products_data:
            st.warning(f"{'No products available' if language == 'English' else 'Tidak ada produk tersedia'}")
        else:
            product_names = [p["name"] for p in products_data]
            product_to_edit = st.selectbox(
                f"{'Select product to edit:' if language == 'English' else 'Pilih produk untuk diedit:'}",
                product_names
            )
            
            product_data = next((p for p in products_data if p["name"] == product_to_edit), None)
            
            if product_data:
                with st.form("edit_product_form"):
                    st.markdown(f"<h3 style='color: #000000; margin-bottom: 1.5rem;'>{LANGUAGES[language]['edit']} Product: {product_data['name']}</h3>", unsafe_allow_html=True)
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        name = st.text_input(f"{'Name' if language == 'English' else 'Nama'}*", value=product_data["name"])
                        category = st.text_input(f"{'Category' if language == 'English' else 'Kategori'}*", value=product_data["category"])
                        materials = st.text_input(f"{'Materials' if language == 'English' else 'Bahan'}*", value=product_data["materials"])
                    with col2:
                        price = st.number_input(f"{'Price (IDR)' if language == 'English' else 'Harga (Rp)'}*", min_value=0, value=int(product_data["price"]))
                        discount = st.number_input(f"{'Discount (%)' if language == 'English' else 'Diskon (%)'}", min_value=0, max_value=100, value=int(product_data["discount"]))
                        creation_date = st.date_input(f"{'Creation Date' if language == 'English' else 'Tanggal Pembuatan'}", datetime.strptime(product_data["creation_date"], "%Y-%m-%d").date())
                    
                    description = st.text_area(f"{'Description' if language == 'English' else 'Deskripsi'}*", value=product_data["description"])
                    
                    # Marketplace links
                    st.markdown(f"<h4 style='color: #000000; margin-bottom: 1rem;'>{'Marketplace Links' if language == 'English' else 'Link Marketplace'}</h4>", unsafe_allow_html=True)
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        shopee_link = st.text_input("Shopee", value=product_data.get("shopee_link", ""))
                    with col2:
                        tokopedia_link = st.text_input("Tokopedia", value=product_data.get("tokopedia_link", ""))
                    with col3:
                        other_link = st.text_input(f"{'Other' if language == 'English' else 'Lainnya'}", value=product_data.get("other_link", ""))
                    
                    # Image upload
                    current_image = product_data.get("image_path", DEFAULT_IMAGE)
                    if current_image and current_image != DEFAULT_IMAGE:
                        display_image(current_image, width=200)
                    else:
                        display_image(DEFAULT_IMAGE, width=200)
                    
                    uploaded_image = st.file_uploader(
                        f"{'New Product Image' if language == 'English' else 'Gambar Produk Baru'}", 
                        type=["jpg", "jpeg", "png", "webp"]
                    )
                    
                    submitted = st.form_submit_button(f"{'Update Product' if language == 'English' else 'Update Produk'}")
                    
                    if submitted:
                        if not all([name, category, materials, price, description]):
                            st.error(f"{'Please fill required fields' if language == 'English' else 'Harap isi field wajib'} (*)")
                        else:
                            image_path = current_image
                            if uploaded_image:
                                saved_path = save_image_local(uploaded_image, IMAGE_DIR)
                                if saved_path:
                                    image_path = saved_path
                            
                            # Update product data
                            product_data.update({
                                "name": name,
                                "description": description,
                                "price": price,
                                "discount": discount,
                                "category": category,
                                "materials": materials,
                                "creation_date": creation_date.strftime("%Y-%m-%d"),
                                "image_path": image_path,
                                "shopee_link": shopee_link,
                                "tokopedia_link": tokopedia_link,
                                "other_link": other_link
                            })
                            
                            if save_all_products(products_data):
                                st.success(f"{'Product updated successfully!' if language == 'English' else 'Produk berhasil diupdate!'}")

    elif operation == LANGUAGES[language]["delete"]:
        if not products_data:
            st.warning(f"{'No products available' if language == 'English' else 'Tidak ada produk tersedia'}")
        else:
            product_names = [p["name"] for p in products_data]
            product_to_delete = st.selectbox(
                f"{'Select product to delete:' if language == 'English' else 'Pilih produk untuk dihapus:'}",
                product_names
            )
            
            product_data = next((p for p in products_data if p["name"] == product_to_delete), None)
            
            if product_data:
                st.markdown(f"""
                <h3 style="color: #000000; margin-bottom: 1rem;">⚠️ {'Are you sure you want to delete' if language == 'English' else 'Apakah Anda yakin ingin menghapus'} <span style="color: #e63946;">{product_data['name']}</span>?</h3>
                <p style="color: #555;">{'This action cannot be undone. Product data will be permanently removed.' if language == 'English' else 'Tindakan ini tidak dapat dibatalkan. Data produk akan dihapus permanen.'}</p>
                """, unsafe_allow_html=True)
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button(f"{'Confirm Delete' if language == 'English' else 'Konfirmasi Hapus'}", type="primary"):
                        products_data = [p for p in products_data if p["name"] != product_to_delete]
                        if save_all_products(products_data):
                            st.success(f"{'Product deleted successfully!' if language == 'English' else 'Produk berhasil dihapus!'}")
                            st.rerun()
                with col2:
                    if st.button(f"{'Cancel' if language == 'English' else 'Batal'}"):
                        st.rerun()

# --- SETTINGS PAGE ---
def show_settings_page(language):
    """Show settings page for admin"""
    st.markdown(f"""
    <h2 style="margin-bottom: 1rem; color: #000000;">{LANGUAGES[language]["settings"]}</h2>
    """, unsafe_allow_html=True)
    
    st.markdown(f"<h3 style='color: #000000; margin-bottom: 1.5rem;'>{LANGUAGES[language]['other_settings']}</h3>", unsafe_allow_html=True)
    
    # Admin password change
    st.markdown("---")
    st.markdown(f"<h4 style='color: #000000; margin-bottom: 1rem;'>Change Admin Password</h4>", unsafe_allow_html=True)
    
    with st.form("change_password_form"):
        current_password = st.text_input("Current Password", type="password")
        new_password = st.text_input("New Password", type="password")
        confirm_password = st.text_input("Confirm New Password", type="password")
        
        submitted = st.form_submit_button("Change Password")
        
        if submitted:
            if not all([current_password, new_password, confirm_password]):
                st.error("Please fill all fields")
            elif new_password != confirm_password:
                st.error("New passwords don't match")
            elif not check_admin_credentials(ADMIN_CREDENTIALS["username"], current_password):
                st.error("Incorrect current password")
            else:
                # Update password
                hashed_password = hashlib.sha256(new_password.encode()).hexdigest()
                ADMIN_CREDENTIALS["password"] = hashed_password
                st.success("Password changed successfully!")

# --- INVENTORY MANAGEMENT PAGES ---
def show_inventory_management(language):
    """Inventory management page with stock tracking"""
    st.markdown(f"""
    <h2 style="margin-bottom: 1rem; color: #000000;">{LANGUAGES[language]["inventory_manage"]}</h2>
    """, unsafe_allow_html=True)
    
    st.info("Fitur manajemen inventaris akan segera hadir!")

# --- FINANCIAL MANAGEMENT PAGES ---
def show_financial_management(language):
    """Financial management page with transactions and reports"""
    st.markdown(f"""
    <h2 style="margin-bottom: 1rem; color: #000000;">{LANGUAGES[language]["finance_manage"]}</h2>
    """, unsafe_allow_html=True)
    
    st.info("Fitur manajemen keuangan akan segera hadir!")

# --- MAIN APP ---
def main():    
    # Initialize session state
    if "is_admin" not in st.session_state:
        st.session_state["is_admin"] = False
    if "language" not in st.session_state:
        st.session_state["language"] = "Indonesia"
    
    # Apply premium styling
    apply_professional_style()
    
    # Sidebar navigation
    with st.sidebar:
        st.image(DEFAULT_IMAGE, width=120, caption="Logo")
        
        st.markdown("---")
        
        language = st.selectbox("🌐 Language / Bahasa", 
                              ["Indonesia", "English"],
                              index=0 if st.session_state["language"] == "Indonesia" else 1)
        st.session_state["language"] = language
        
        st.markdown("---")
        
        menu_options = [
            LANGUAGES[language]["dashboard"],
            LANGUAGES[language]["featured"],
            LANGUAGES[language]["analytics"]
        ]
        
        if st.session_state["is_admin"]:
            menu_options.extend([
                LANGUAGES[language]["manage"],
                LANGUAGES[language]["inventory_manage"],
                LANGUAGES[language]["finance_manage"],
                LANGUAGES[language]["hpp_calculator"],
                LANGUAGES[language]["settings"]
            ])
        
        selected_menu = st.radio(
            "Navigation",
            menu_options,
            label_visibility="collapsed"
        )
        
        st.markdown("---")
        
        if st.session_state["is_admin"]:
            if st.button(f"🚪 {LANGUAGES[language]['logout']}"):
                st.session_state["is_admin"] = False
                st.rerun()
        else:
            # Show login form directly in sidebar if not admin
            show_login_form(language)
    
    # Display header
    display_header(language)
    
    # Page routing
    if selected_menu == LANGUAGES[language]["dashboard"]:
        show_home_page(language)
    elif selected_menu == LANGUAGES[language]["featured"]:
        show_gallery_page(language)
    elif selected_menu == LANGUAGES[language]["analytics"]:
        show_analytics_dashboard(language)
    elif selected_menu == LANGUAGES[language]["manage"]:
        if st.session_state["is_admin"]:
            show_manage_page(language)
        else:
            st.warning("Admin access required" if language == "English" else "Diperlukan akses admin")
            show_login_form(language)
    elif selected_menu == LANGUAGES[language]["inventory_manage"]:
        if st.session_state["is_admin"]:
            show_inventory_management(language)
        else:
            st.warning("Admin access required" if language == "English" else "Diperlukan akses admin")
            show_login_form(language)
    elif selected_menu == LANGUAGES[language]["finance_manage"]:
        if st.session_state["is_admin"]:
            show_financial_management(language)
        else:
            st.warning("Admin access required" if language == "English" else "Diperlukan akses admin")
            show_login_form(language)
    elif selected_menu == LANGUAGES[language]["hpp_calculator"]:
        if st.session_state["is_admin"]:
            show_hpp_calculator(language)
        else:
            st.warning("Admin access required" if language == "English" else "Diperlukan akses admin")
            show_login_form(language)
    elif selected_menu == LANGUAGES[language]["settings"]:
        if st.session_state["is_admin"]:
            show_settings_page(language)
        else:
            st.warning("Admin access required" if language == "English" else "Diperlukan akses admin")
            show_login_form(language)
    
    # Main footer
    st.markdown("""
    <div style="text-align: center; color: #666; font-size: 14px; padding: 20px; margin-top: 2rem;">
        © 2025 Batik Bambu Mujur - Batik Tulis Premium
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()