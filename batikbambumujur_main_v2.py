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
import random
import time
import folium
from streamlit_folium import folium_static
import json
from collections import defaultdict
import numpy as np
import requests

# Configure page with better defaults
st.set_page_config(
    page_title="Batik Gallery Admin",
    page_icon="🎨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CONSTANTS ---
DEFAULT_IMAGE = "https://via.placeholder.com/300x300.png?text=Image+Not+Found"
SPREADSHEET_ID = "19rQZ2FEBN9FFynlsOdi0okjjAaPSu5lBkGhSJfhg2hg"  # ID dari URL spreadsheet Anda

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
    visitor_id = str(uuid.uuid4())
    today = datetime.now().date().isoformat()
    
    st.session_state.visitor_data['total_visits'] += 1
    st.session_state.visitor_data['unique_visitors'].add(visitor_id)
    st.session_state.visitor_data['page_views'] += 1
    
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
    if max_price > 10000000:
        return 500000
    elif max_price > 1000000:
        return 100000
    else:
        return 10000

def check_admin_credentials(username, password):
    """Verify admin credentials"""
    hashed_input = hashlib.sha256(password.encode()).hexdigest()
    return (username == ADMIN_CREDENTIALS["username"] and 
            hashed_input == ADMIN_CREDENTIALS["password"])

def show_login_form(language):
    """Display admin login form"""
    with st.form("admin_login"):
        st.subheader(LANGUAGES[language]["login"])
        
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        
        submitted = st.form_submit_button("Login", type="primary")
        
        if submitted:
            if check_admin_credentials(username, password):
                st.session_state["is_admin"] = True
                st.success("Login successful!" if language == "English" else "Login berhasil!")
                time.sleep(1)
                st.rerun()
            else:
                st.error("Incorrect username or password" if language == "English" else "Username atau password salah")

# --- GOOGLE SHEETS CONNECTION ---
@st.cache_resource
def get_google_sheet():
    """Establish connection to Google Sheets"""
    try:
        # Get credentials from Streamlit secrets
        if 'gcp_service_account' in st.secrets:
            creds_dict = dict(st.secrets['gcp_service_account'])
            # Ensure private key is properly formatted
            if 'private_key' in creds_dict:
                creds_dict['private_key'] = creds_dict['private_key'].replace('\\n', '\n')
        else:
            st.error("Google Sheets credentials not found in secrets")
            return None

        scope = ['https://spreadsheets.google.com/feeds',
                'https://www.googleapis.com/auth/drive']
        
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
        client = gspread.authorize(creds)
        
        # Open spreadsheet by ID
        spreadsheet = client.open_by_key(SPREADSHEET_ID)
        return spreadsheet
        
    except Exception as e:
        st.error(f"Error connecting to Google Sheets: {str(e)}")
        return None

def get_sheet_data(sheet_name):
    """Get data from specific sheet"""
    try:
        spreadsheet = get_google_sheet()
        if not spreadsheet:
            return []
            
        worksheet = spreadsheet.worksheet(sheet_name)
        records = worksheet.get_all_records()
        return records
    except Exception as e:
        st.error(f"Error reading sheet {sheet_name}: {str(e)}")
        return []

def update_sheet_data(sheet_name, data):
    """Update data in specific sheet"""
    try:
        spreadsheet = get_google_sheet()
        if not spreadsheet:
            return False
            
        worksheet = spreadsheet.worksheet(sheet_name)
        
        # Clear existing data and write new data
        worksheet.clear()
        if data:
            # Convert to list of lists
            headers = list(data[0].keys())
            values = [headers] + [[item.get(header, '') for header in headers] for item in data]
            worksheet.update(values)
        return True
    except Exception as e:
        st.error(f"Error updating sheet {sheet_name}: {str(e)}")
        return False

def add_row_to_sheet(sheet_name, row_data):
    """Add a single row to sheet"""
    try:
        spreadsheet = get_google_sheet()
        if not spreadsheet:
            return False
            
        worksheet = spreadsheet.worksheet(sheet_name)
        worksheet.append_row(list(row_data.values()))
        return True
    except Exception as e:
        st.error(f"Error adding row to {sheet_name}: {str(e)}")
        return False

# --- DATA OPERATIONS ---
def get_all_products():
    """Get all products from Google Sheets"""
    return get_sheet_data('products')

def save_all_products(products):
    """Save products to Google Sheets"""
    return update_sheet_data('products', products)

def add_product(product_data):
    """Add a single product"""
    return add_row_to_sheet('products', product_data)

def get_all_activities():
    """Get all activities from Google Sheets"""
    return get_sheet_data('activities')

def get_all_awards():
    """Get all awards from Google Sheets"""
    return get_sheet_data('awards')

# --- IMAGE HANDLING ---
def generate_unique_filename(original_name):
    """Generate unique filename"""
    ext = original_name.split('.')[-1]
    unique_id = uuid.uuid4().hex[:8]
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{timestamp}_{unique_id}.{ext}"

def save_image_local(uploaded_file):
    """Save uploaded image locally (for Streamlit Cloud)"""
    try:
        # In Streamlit Cloud, we can only save temporarily
        # For production, you might want to use a cloud storage service
        unique_filename = generate_unique_filename(uploaded_file.name)
        return unique_filename  # Return filename for reference
    except Exception as e:
        st.error(f"Error saving image: {str(e)}")
        return None

def display_image(image_path, width=300):
    """Display image - for now using placeholder"""
    try:
        st.image(DEFAULT_IMAGE, width=width)
        return True
    except Exception as img_error:
        st.error(f"Error displaying image: {str(img_error)}")
        st.image(DEFAULT_IMAGE, width=width)
        return False

# --- VISITOR STATISTICS ---
def get_visitor_data():
    """Get real visitor data from session state"""
    daily_stats = st.session_state.visitor_data['daily_stats']
    
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

# --- HPP CALCULATOR FUNCTIONS ---
def show_hpp_calculator(language):
    """HPP Calculator for Batik Tulis"""
    st.markdown(f"""
    <h2 style="margin-bottom: 1rem; color: #000000;">Kalkulator HPP Batik Tulis</h2>
    <p style="color: #555; font-size: 16px;">Hitung Harga Pokok Produksi dan Harga Jual untuk Batik Tulis</p>
    """, unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["🖌️ Input Data", "🧮 Kalkulasi HPP", "📊 Hasil"])
    
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
        fabric_type = st.selectbox("Jenis Kain", ["Katun Primissima", "Katun Dobby", "Katun Mori", "Sutera Alam"])
    
    with col2:
        fabric_length = st.number_input("Panjang Kain (meter)", min_value=0.1, value=2.5, step=0.1)
        fabric_width = st.number_input("Lebar Kain (meter)", min_value=0.1, value=1.1, step=0.1)
        production_quantity = st.number_input("Jumlah Produksi (pcs)", min_value=1, value=1)
    
    st.markdown("---")
    st.markdown(f"<h4 style='color: #000000; margin-bottom: 1rem;'>Biaya Bahan Baku</h4>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        fabric_price_per_meter = st.number_input("Harga Kain per Meter (Rp)", min_value=0, value=45000, step=1000)
    with col2:
        wax_quantity = st.number_input("Kebutuhan Lilin (gram)", min_value=0.0, value=150.0, step=10.0)
        wax_price_per_kg = st.number_input("Harga Lilin per Kg (Rp)", min_value=0, value=25000, step=1000)
    with col3:
        dye_price = st.number_input("Harga Pewarna (Rp)", min_value=0, value=75000, step=5000)
    
    st.markdown("---")
    st.markdown(f"<h4 style='color: #000000; margin-bottom: 1rem;'>Biaya Tenaga Kerja</h4>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        design_hours = st.number_input("Waktu Membuat Pola (jam)", min_value=0.0, value=8.0, step=0.5)
        design_hourly_rate = st.number_input("Upah Perancang per Jam (Rp)", min_value=0, value=25000, step=1000)
    with col2:
        waxing_hours = st.number_input("Waktu Membatik (jam)", min_value=0.0, value=40.0, step=1.0)
        batik_artist_hourly_rate = st.number_input("Upah Pembatik per Jam (Rp)", min_value=0, value=20000, step=1000)
    
    st.markdown("---")
    st.markdown(f"<h4 style='color: #000000; margin-bottom: 1rem;'>Biaya Produksi Lainnya</h4>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        boiling_cost = st.number_input("Biaya Pelorodan (Rp)", min_value=0, value=15000, step=1000)
        packaging_cost = st.number_input("Biaya Kemasan (Rp)", min_value=0, value=15000, step=1000)
    with col2:
        overhead_percentage = st.number_input("Overhead (%)", min_value=0.0, value=15.0, step=1.0)
    
    # Save to session state
    st.session_state.hpp_data = {
        'product_name': product_name,
        'fabric_type': fabric_type,
        'fabric_length': fabric_length,
        'fabric_width': fabric_width,
        'production_quantity': production_quantity,
        'fabric_price_per_meter': fabric_price_per_meter,
        'wax_quantity': wax_quantity,
        'wax_price_per_kg': wax_price_per_kg,
        'dye_price': dye_price,
        'design_hours': design_hours,
        'design_hourly_rate': design_hourly_rate,
        'waxing_hours': waxing_hours,
        'batik_artist_hourly_rate': batik_artist_hourly_rate,
        'boiling_cost': boiling_cost,
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
    
    # Calculate costs
    fabric_area = data['fabric_length'] * data['fabric_width']
    fabric_cost = fabric_area * data['fabric_price_per_meter']
    wax_cost = (data['wax_quantity'] / 1000) * data['wax_price_per_kg']
    dye_cost = data['dye_price']
    
    material_costs = fabric_cost + wax_cost + dye_cost
    
    design_labor_cost = data['design_hours'] * data['design_hourly_rate']
    waxing_labor_cost = data['waxing_hours'] * data['batik_artist_hourly_rate']
    
    labor_costs = design_labor_cost + waxing_labor_cost
    other_costs = data['boiling_cost'] + data['packaging_cost']
    
    total_direct_costs = material_costs + labor_costs + other_costs
    overhead_cost = total_direct_costs * (data['overhead_percentage'] / 100)
    total_production_cost = total_direct_costs + overhead_cost
    
    hpp_per_unit = total_production_cost / data['production_quantity'] if data['production_quantity'] > 0 else total_production_cost
    
    # Save calculations
    st.session_state.hpp_calculations = {
        'material_costs': material_costs,
        'labor_costs': labor_costs,
        'other_costs': other_costs,
        'overhead_cost': overhead_cost,
        'total_production_cost': total_production_cost,
        'hpp_per_unit': hpp_per_unit
    }
    
    # Display results
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Biaya Bahan Baku", format_price(material_costs, language))
        st.metric("Biaya Tenaga Kerja", format_price(labor_costs, language))
        st.metric("Biaya Lainnya", format_price(other_costs, language))
    with col2:
        st.metric("Overhead", format_price(overhead_cost, language))
        st.metric("Total Biaya Produksi", format_price(total_production_cost, language))
        st.metric("HPP per Unit", format_price(hpp_per_unit, language))

def show_results(language):
    """Show HPP results and pricing recommendations"""
    if 'hpp_calculations' not in st.session_state:
        st.warning("Silakan lakukan kalkulasi HPP terlebih dahulu di tab 'Kalkulasi HPP'")
        return
    
    calculations = st.session_state.hpp_calculations
    
    st.markdown(f"<h3 style='color: #000000; margin-bottom: 1.5rem;'>Rekomendasi Harga Jual</h3>", unsafe_allow_html=True)
    
    profit_margin = st.slider("Margin Keuntungan (%)", min_value=10, max_value=100, value=40, step=5)
    selling_price = calculations['hpp_per_unit'] * (1 + profit_margin / 100)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Harga Pokok Produksi", format_price(calculations['hpp_per_unit'], language))
    with col2:
        st.metric("Margin Keuntungan", f"{profit_margin}%")
    with col3:
        st.metric("Harga Jual Recommended", format_price(selling_price, language))

# --- UI COMPONENTS ---
def apply_professional_style():
    """Apply professional styling"""
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
        .stButton button {
            background-color: #4a6fa5;
            color: white;
            border: none;
            padding: 0.5rem 1rem;
            border-radius: 0.5rem;
        }
    </style>
    """, unsafe_allow_html=True)

def display_header(language):
    """Display app header"""
    col1, col2 = st.columns([1, 4])
    with col1:
        st.image(DEFAULT_IMAGE, width=120)
    with col2:
        st.markdown(f"""
        <h1 style="margin-bottom: 0; color: #000000;">{LANGUAGES[language]["title"]}</h1>
        <p style="color: #4a6fa5; font-size: 16px; margin-top: 0.5rem;">{LANGUAGES[language]["subtitle"]}</p>
        """, unsafe_allow_html=True)

def product_card(product, language):
    """Display product card"""
    try:
        product_name = product.get("name", "Unknown Product")
        product_price = float(product.get("price", 0))
        discount = float(product.get("discount", 0))
        discounted_price = product_price * (1 - discount/100) if discount > 0 else product_price
        product_category = product.get("category", "Uncategorized")
        product_description = product.get("description", "No description available")
        
        with st.container():
            display_image(DEFAULT_IMAGE)
            
            st.markdown(f"<h3 style='color: #000000; margin-bottom: 0.5rem;'>{product_name}</h3>", unsafe_allow_html=True)
            
            # Category
            st.markdown(f"""<div style="background: #f0f8ff; color: #4a6fa5; padding: 4px 8px; border-radius: 12px; font-size: 12px; display: inline-block; margin-bottom: 8px;">{product_category}</div>""", unsafe_allow_html=True)
            
            # Price
            if discount > 0:
                st.markdown(f"<div style='font-size: 20px; font-weight: 700; color: #e63946;'>{format_price(discounted_price, language)}</div>", unsafe_allow_html=True)
                st.markdown(f"""<div style="text-decoration: line-through; color: #999; font-size: 14px;">{format_price(product_price, language)}</div>""", unsafe_allow_html=True)
                st.markdown(f"""<div style="background: #e63946; color: white; padding: 2px 6px; border-radius: 4px; font-size: 12px; display: inline-block;">{discount}% OFF</div>""", unsafe_allow_html=True)
            else:
                st.markdown(f"<div style='font-size: 20px; font-weight: 700; color: #e63946;'>{format_price(product_price, language)}</div>", unsafe_allow_html=True)
            
            # Description
            with st.expander(LANGUAGES[language]["description_label"]):
                st.write(product_description)
            
            # Edit button for admin
            if st.session_state.get("is_admin", False):
                if st.button("✏️ Edit Product", key=f"edit_{product.get('id', '')}"):
                    st.session_state['edit_product'] = product.get('id', '')
    
    except Exception as e:
        st.error(f"Error displaying product: {str(e)}")

# --- PAGES ---
def show_home_page(language):
    """Home page with featured products"""
    try:
        st.markdown(f"""
        <h2 style="margin-bottom: 0.5rem; color: #000000;">{LANGUAGES[language]['welcome']}</h2>
        <p style="color: #555; font-size: 16px; margin-bottom: 2rem;">{LANGUAGES[language]['description']}</p>
        """, unsafe_allow_html=True)
        
        products_data = get_all_products()
        
        if not products_data:
            st.warning("Belum ada produk tersedia. Silakan login sebagai admin untuk menambah produk.")
        else:
            st.markdown(f"""
            <h3 style="margin-bottom: 1rem; color: #000000;">{LANGUAGES[language]["featured"]}</h3>
            """, unsafe_allow_html=True)
            
            # Display products in grid
            for i in range(0, len(products_data), 3):
                cols = st.columns(3)
                for j in range(3):
                    if i + j < len(products_data):
                        with cols[j]:
                            product_card(products_data[i + j], language)
                    else:
                        with cols[j]:
                            st.empty()
        
        # Activities and Awards sections
        activities_data = get_all_activities()
        awards_data = get_all_awards()
        
        if activities_data:
            st.markdown("---")
            st.markdown(f"""
            <h3 style="margin-bottom: 1rem; color: #000000;">{LANGUAGES[language]["activities"]}</h3>
            """, unsafe_allow_html=True)
            st.info(f"{len(activities_data)} kegiatan tersedia")
        
        if awards_data:
            st.markdown("---")
            st.markdown(f"""
            <h3 style="margin-bottom: 1rem; color: #000000;">{LANGUAGES[language]["awards"]}</h3>
            """, unsafe_allow_html=True)
            st.info(f"{len(awards_data)} penghargaan tersedia")
            
    except Exception as e:
        st.error(f"Terjadi kesalahan: {str(e)}")

def show_gallery_page(language):
    """Gallery page with all products"""
    st.markdown(f"""
    <h2 style="margin-bottom: 1rem; color: #000000;">{LANGUAGES[language]["featured"]}</h2>
    """, unsafe_allow_html=True)
    
    products_data = get_all_products()
    
    if not products_data:
        st.warning("Belum ada produk tersedia")
        return
    
    # Simple filter
    search_query = st.text_input(LANGUAGES[language]["search"])
    
    filtered_data = products_data
    if search_query:
        filtered_data = [p for p in products_data if search_query.lower() in p.get("name", "").lower()]
    
    if not filtered_data:
        st.warning("Tidak ada produk yang sesuai dengan pencarian")
    else:
        # Display products
        for i in range(0, len(filtered_data), 3):
            cols = st.columns(3)
            for j in range(3):
                if i + j < len(filtered_data):
                    with cols[j]:
                        product_card(filtered_data[i + j], language)
                else:
                    with cols[j]:
                        st.empty()

def show_analytics_dashboard(language):
    """Analytics dashboard"""
    st.markdown(f"""
    <h2 style="margin-bottom: 1rem; color: #000000;">{LANGUAGES[language]["analytics"]}</h2>
    """, unsafe_allow_html=True)
    
    track_visitor()
    
    # Display metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(LANGUAGES[language]["total_visitors"], st.session_state.visitor_data['total_visits'])
    with col2:
        st.metric(LANGUAGES[language]["unique_visitors"], len(st.session_state.visitor_data['unique_visitors']))
    with col3:
        st.metric(LANGUAGES[language]["page_views"], st.session_state.visitor_data['page_views'])
    
    # Visitor chart
    visitor_df = get_visitor_data()
    if not visitor_df.empty:
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=visitor_df['date'], y=visitor_df['visitors'], name='Visitors'))
        fig.update_layout(title='Visitor Trends', xaxis_title='Date', yaxis_title='Visitors')
        st.plotly_chart(fig, use_container_width=True)

def show_manage_page(language):
    """Product management page"""
    st.markdown(f"""
    <h2 style="margin-bottom: 1rem; color: #000000;">{LANGUAGES[language]["manage"]}</h2>
    """, unsafe_allow_html=True)
    
    operation = st.radio("Pilih operasi:", [LANGUAGES[language]["add"], LANGUAGES[language]["edit"]], horizontal=True)
    
    products_data = get_all_products()
    
    if operation == LANGUAGES[language]["add"]:
        with st.form("add_product_form"):
            st.subheader("Tambah Produk Baru")
            
            col1, col2 = st.columns(2)
            with col1:
                name = st.text_input("Nama Produk*")
                category = st.text_input("Kategori*")
                price = st.number_input("Harga (Rp)*", min_value=0)
            with col2:
                discount = st.number_input("Diskon (%)", min_value=0, max_value=100, value=0)
                materials = st.text_input("Bahan")
                creation_date = st.date_input("Tanggal Pembuatan", datetime.now())
            
            description = st.text_area("Deskripsi*")
            
            submitted = st.form_submit_button("Simpan Produk")
            
            if submitted:
                if not all([name, category, price, description]):
                    st.error("Harap isi semua field yang wajib (*)")
                else:
                    new_product = {
                        "id": len(products_data) + 1,
                        "name": name,
                        "description": description,
                        "price": price,
                        "discount": discount,
                        "category": category,
                        "materials": materials,
                        "creation_date": creation_date.strftime("%Y-%m-%d"),
                        "image_path": DEFAULT_IMAGE,
                        "shopee_link": "",
                        "tokopedia_link": "",
                        "other_link": "",
                        "payment_methods": "Transfer Bank"
                    }
                    
                    if add_product(new_product):
                        st.success("Produk berhasil ditambahkan!")
                        st.balloons()
                    else:
                        st.error("Gagal menambah produk")
    
    elif operation == LANGUAGES[language]["edit"]:
        if not products_data:
            st.warning("Tidak ada produk tersedia")
        else:
            product_names = [p["name"] for p in products_data]
            selected_product = st.selectbox("Pilih produk untuk diedit:", product_names)
            
            if selected_product:
                st.info("Fitur edit akan segera hadir")
                # Implementation for edit would go here

def show_settings_page(language):
    """Settings page"""
    st.markdown(f"""
    <h2 style="margin-bottom: 1rem; color: #000000;">{LANGUAGES[language]["settings"]}</h2>
    """, unsafe_allow_html=True)
    
    # Password change
    with st.form("change_password"):
        st.subheader("Ubah Password Admin")
        current_pw = st.text_input("Password Saat Ini", type="password")
        new_pw = st.text_input("Password Baru", type="password")
        confirm_pw = st.text_input("Konfirmasi Password Baru", type="password")
        
        if st.form_submit_button("Ubah Password"):
            if not all([current_pw, new_pw, confirm_pw]):
                st.error("Harap isi semua field")
            elif new_pw != confirm_pw:
                st.error("Password baru tidak cocok")
            elif not check_admin_credentials("admin", current_pw):
                st.error("Password saat ini salah")
            else:
                # In a real app, you'd want to persist this change
                st.success("Password berhasil diubah!")

# --- MAIN APP ---
def main():    
    # Initialize session state
    if "is_admin" not in st.session_state:
        st.session_state["is_admin"] = False
    if "language" not in st.session_state:
        st.session_state["language"] = "Indonesia"
    
    # Apply styling
    apply_professional_style()
    
    # Sidebar
    with st.sidebar:
        st.image(DEFAULT_IMAGE, width=100)
        st.markdown("---")
        
        language = st.selectbox("🌐 Bahasa", ["Indonesia", "English"], 
                              index=0 if st.session_state["language"] == "Indonesia" else 1)
        st.session_state["language"] = language
        
        st.markdown("---")
        
        # Navigation
        menu_options = [
            LANGUAGES[language]["dashboard"],
            LANGUAGES[language]["featured"], 
            LANGUAGES[language]["analytics"]
        ]
        
        if st.session_state["is_admin"]:
            menu_options.extend([
                LANGUAGES[language]["manage"],
                LANGUAGES[language]["hpp_calculator"],
                LANGUAGES[language]["settings"]
            ])
        
        selected_menu = st.radio("Navigasi", menu_options)
        
        st.markdown("---")
        
        # Login/Logout
        if st.session_state["is_admin"]:
            if st.button(f"🚪 {LANGUAGES[language]['logout']}"):
                st.session_state["is_admin"] = False
                st.rerun()
        else:
            show_login_form(language)
    
    # Header
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
            st.warning("Diperlukan akses admin")
    elif selected_menu == LANGUAGES[language]["hpp_calculator"]:
        if st.session_state["is_admin"]:
            show_hpp_calculator(language)
        else:
            st.warning("Diperlukan akses admin")
    elif selected_menu == LANGUAGES[language]["settings"]:
        if st.session_state["is_admin"]:
            show_settings_page(language)
        else:
            st.warning("Diperlukan akses admin")
    
    # Footer
    st.markdown("---")
    st.markdown(
        "<div style='text-align: center; color: #666;'>© 2024 Batik Bambu Mujur</div>",
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()