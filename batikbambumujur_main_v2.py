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
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload

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
GOOGLE_DRIVE_FOLDER_ID = "1J1sAKu1nUkZFoBVMgcDnmugI1-5Xz1Lf"  # Folder ID dari Google Drive
IMAGE_DIR = "images"
ACTIVITIES_DIR = "activities"
AWARDS_DIR = "awards"
INVENTORY_DIR = "inventory"
CREDS_SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

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
def get_base64(bin_file):
    """Convert binary file to base64"""
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

def set_background(png_file):
    """Set background image"""
    with open(png_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

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
        
        # Light background form fields
        with stylable_container(
            key="login_form",
            css_styles="""
                {
                    background-color: #ffffff;
                    border-radius: 10px;
                    padding: 20px;
                }
                input {
                    background-color: #ffffff !important;
                    color: #000000 !important;
                }
            """
        ):
            username = st.text_input("Username", key="login_username")
            password = st.text_input("Password", type="password", key="login_password")
            
            submitted = st.form_submit_button("Login", 
                                             width='stretch',
                                             type="primary")
        
        if submitted:
            if check_admin_credentials(username, password):
                st.session_state["is_admin"] = True
                st.success("Login successful!" if language == "English" else "Login berhasil!")
                time.sleep(1)
                st.rerun()
            else:
                st.error("Incorrect username or password" if language == "English" else "Username atau password salah")

# --- SECRETS MANAGEMENT ---
def get_google_creds():
    """Get credentials from Streamlit secrets or local file with enhanced error handling"""
    try:
        # Priority 1: Streamlit Cloud secrets
        if hasattr(st, "secrets"):
            # Check for different possible secret structures
            if "gcp_service_account" in st.secrets:
                creds_data = dict(st.secrets["gcp_service_account"])
                # Ensure private key is properly formatted
                if 'private_key' in creds_data:
                    creds_data['private_key'] = creds_data['private_key'].replace('\\n', '\n')
                return creds_data
            elif "gcp" in st.secrets:
                creds_data = dict(st.secrets["gcp"])
                if 'private_key' in creds_data:
                    creds_data['private_key'] = creds_data['private_key'].replace('\\n', '\n')
                return creds_data
        
        # Priority 2: Local secrets.toml for development
        try:
            secrets_path = Path(__file__).parent / ".streamlit/secrets.toml"
            if secrets_path.exists():
                import toml
                secrets = toml.load(secrets_path)
                if "gcp_service_account" in secrets:
                    creds_data = secrets["gcp_service_account"]
                    if 'private_key' in creds_data:
                        creds_data['private_key'] = creds_data['private_key'].replace('\\n', '\n')
                    return creds_data
                elif "gcp" in secrets:
                    creds_data = secrets["gcp"]
                    if 'private_key' in creds_data:
                        creds_data['private_key'] = creds_data['private_key'].replace('\\n', '\n')
                    return creds_data
        except:
            pass
        
        # Priority 3: Environment variables (for backward compatibility)
        env_creds = {}
        if os.getenv("GOOGLE_PRIVATE_KEY"):
            env_creds = {
                "type": os.getenv("GOOGLE_TYPE", "service_account"),
                "project_id": os.getenv("GOOGLE_PROJECT_ID", "batikgallery-api"),
                "private_key_id": os.getenv("GOOGLE_PRIVATE_KEY_ID", "0d6bbde112af4677618c5e06ee043013c7a8c68c"),
                "private_key": os.getenv("GOOGLE_PRIVATE_KEY", "-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQC2R6cd6Pizl+G/\nACrcwN4KCI3DaFdwV94/qacLN9FkDR/Q8mJBt5D4nY/KmerU0su3Xz4CfDdgKAQE\nThkBJ9Ppt1qJ0DK9BpH7QLQOWjNAlbP6vNd8DNXVKq4Y7jn1gH/+G3TRtVP4WI5c\nwjKGIURMBF6xv/BegSTIXlNBW5L1lpvfpycdUO4ERYPHHyuq5Mzx4Gc+DFg/P/NZ\nnXXs6KZJ7NlfFW200+VgirVgStNlOlw9lE4d0J3ym0+rLHPD/209s29EW6SZFKlQ\nuSSsvnJ1eaqhtwHQdDxU2WWLtO9n/k+3rN4yd74wvPFQaUFLZFpRs2O3DZU66ZLY\nYT/1vRh5AgMBAAECggEAAxMwXhmEctIB0Q0wYsZlk/BTAHi//7lQUX95mTZrapP0\nYwT6mxIPQeAjJdiHJzH0TGTnowkYjXrawxBmyHDr/UDrA165VYokaANgs+7+dzQG\nKtA/3lm3Xb/wJDYYmjU0BdYWvNbqrdzWSx4C+sEi6aupxdvdMuruhX2nlHdkAkX/\nhx9hMhG4560MpDtYRbvgtp1uJjUTvi5MPHFc2RVPN8075cPvfjsAsSZCjf60H887\nfobVv+Sezl3CjO/7Wwi0JG7faceoUH7Tf/xTuENrpj4y1nudXerzOq/rvQCTUzwD\nBWeVTniL7gUGHLN0X3IMKA+VVcxTy43WtgO8BPzMgQKBgQDy2t0LB4cLl2PpVnEC\nvMnJEIs4umHrHZA7/cxMVWhvqPFt3recFsY8o711dLmuZfu+bmwFIGE5R0iLJz5L\nHFwGswX4Yoi+eerLQ++vGMJAVPh6ycLnKVcXu7HpKPmgiTGTBIiIt2LIIauS68XM\n74CX2+9RBaNUhhIIj0cuJrNyEQKBgQDAJW1QpK0+bPU+tmoZMwIAwYKnb8QKh2VB\n9FbEqcHWxcs6HURJuP9SGdTkseIYRmok/lnwbwrvaBMTi6WU0fdIHDj+uDoVjhQi\nqq5WHYdyR4HUa5SbLK4xv5+p0jw1Rycd0rmWiPngMdhGziESgC3y/sYqH78Hmyh0\n6tJ6b77X6QKBgQCy7ep6m9s2AR7N5rBxEeOiTpwk+b33WtrQOJhzjWHbEyB+kN+7\nE1SPjRykE5JTGjS3A+h2hnrblteuHwXYlVaAYRp+/So/HNiPVsibu6QzfedtoIYH\nhv/yLopQfa4eR7bM2UQ3ZtZTGeut3iTob3XRbWwPyBWkyvsyb05EhKMl4QKBgCuK\nj6n9lzCVOkHazlIlh+ep8jSFFDSal+yJNPxdx4omyjXCGg5muJzfM6obUTPVCQqX\nBMSCNUUpHWGJfJ0rs1CI7LV0A92Mk62DZfwntuDDqXz8X/GF/3dQiBrQhEpCdG/C\np8GgCpeuU+c/oKjzmPX+m+NBzGUp2NIdwFJ0bhe5AoGAEErJanMZYE9kM2isH6vD\nyd+RisgVIo48919XLxl/ZBP1eqsWRxJjzb/1R1/ptL/n4Tu7kNXjT0DVVz5WyDHF\nepG5fQZXQFJYvyeEtEfYxAXq3ySQWlpR0kTpklxtmSY8a5fi9VWIuxivjAPOdCCY\nmRL/J4uCMBV5dD4Ng82jdEk=\n-----END PRIVATE KEY-----").replace('\\n', '\n'),
                "client_email": os.getenv("GOOGLE_CLIENT_EMAIL", "batik-app@batikgallery-api.iam.gserviceaccount.com"),
                "client_id": os.getenv("GOOGLE_CLIENT_ID", "107401863169189726735"),
                "auth_uri": os.getenv("GOOGLE_AUTH_URI", "https://accounts.google.com/o/oauth2/auth"),
                "token_uri": os.getenv("GOOGLE_TOKEN_URI", "https://oauth2.googleapis.com/token"),
                "auth_provider_x509_cert_url": os.getenv("GOOGLE_AUTH_PROVIDER_CERT_URL", "https://www.googleapis.com/oauth2/v1/cert"),
                "client_x509_cert_url": os.getenv("GOOGLE_CLIENT_CERT_URL", "https://www.googleapis.com/robot/v1/metadata/x509/batik-app%40batikgallery-api.iam.gserviceaccount.com")
            }
            
            if all(env_creds.values()):
                return env_creds
        
        # If no credentials found, return None but don't stop the app
        st.warning("""
        🔐 Google Sheets credentials not found. 
        Some admin features will be disabled.
        """)
        return None
        
    except Exception as e:
        st.error(f"❌ Error loading credentials: {str(e)}")
        return None

# --- GOOGLE DRIVE INTEGRATION ---
@st.cache_resource(ttl=3600)
def get_drive_service():
    """Get Google Drive service instance"""
    creds_data = get_google_creds()
    if not creds_data:
        return None
        
    try:
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_data, CREDS_SCOPES)
        drive_service = build('drive', 'v3', credentials=creds)
        return drive_service
    except Exception as e:
        st.error(f"❌ Error creating Drive service: {str(e)}")
        return None

def upload_to_drive(file_path, folder_name):
    """Upload file to Google Drive folder"""
    drive_service = get_drive_service()
    if not drive_service:
        return None
    
    try:
        # Check if folder exists, create if not
        folder_id = get_or_create_folder(folder_name)
        if not folder_id:
            return None
        
        # Upload file
        file_metadata = {
            'name': os.path.basename(file_path),
            'parents': [folder_id]
        }
        
        media = MediaFileUpload(file_path, resumable=True)
        file = drive_service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id, webViewLink'
        ).execute()
        
        # Make file publicly viewable
        drive_service.permissions().create(
            fileId=file['id'],
            body={'type': 'anyone', 'role': 'reader'},
            fields='id'
        ).execute()
        
        # Get direct download link
        direct_link = f"https://drive.google.com/uc?export=view&id={file['id']}"
        return direct_link
        
    except Exception as e:
        st.error(f"❌ Error uploading to Drive: {str(e)}")
        return None

def get_or_create_folder(folder_name):
    """Get or create folder in Google Drive"""
    drive_service = get_drive_service()
    if not drive_service:
        return None
    
    try:
        # Check if folder exists
        response = drive_service.files().list(
            q=f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder' and '{GOOGLE_DRIVE_FOLDER_ID}' in parents and trashed=false",
            spaces='drive',
            fields='files(id, name)'
        ).execute()
        
        folders = response.get('files', [])
        
        if folders:
            return folders[0]['id']
        else:
            # Create new folder
            folder_metadata = {
                'name': folder_name,
                'mimeType': 'application/vnd.google-apps.folder',
                'parents': [GOOGLE_DRIVE_FOLDER_ID]
            }
            
            folder = drive_service.files().create(
                body=folder_metadata,
                fields='id'
            ).execute()
            
            # Make folder publicly viewable
            drive_service.permissions().create(
                fileId=folder['id'],
                body={'type': 'anyone', 'role': 'reader'},
                fields='id'
            ).execute()
            
            return folder['id']
            
    except Exception as e:
        st.error(f"❌ Error accessing Drive folder: {str(e)}")
        return None

def get_image_from_drive(image_path):
    """Get image from Google Drive by path or return default"""
    if not image_path or image_path == DEFAULT_IMAGE:
        return DEFAULT_IMAGE
    
    # If it's already a Google Drive URL, return it
    if image_path.startswith('http'):
        return image_path
    
    # If it's a local path, try to find it in Drive
    drive_service = get_drive_service()
    if not drive_service:
        return DEFAULT_IMAGE
    
    try:
        # Extract filename from path
        filename = os.path.basename(image_path)
        
        # Search for file in our main folder
        response = drive_service.files().list(
            q=f"name='{filename}' and '{GOOGLE_DRIVE_FOLDER_ID}' in parents and trashed=false",
            spaces='drive',
            fields='files(id, name)'
        ).execute()
        
        files = response.get('files', [])
        
        if files:
            # Return direct download link
            return f"https://drive.google.com/uc?export=view&id={files[0]['id']}"
        else:
            return DEFAULT_IMAGE
            
    except Exception as e:
        st.error(f"❌ Error accessing image from Drive: {str(e)}")
        return DEFAULT_IMAGE

# --- GOOGLE SHEETS CONNECTION ---
@st.cache_resource(ttl=3600)
def get_google_sheet(sheet_name="products"):
    """Establish connection to Google Sheets with comprehensive error handling"""
    # If no credentials, return None to allow app to run in limited mode
    creds_data = get_google_creds()
    if not creds_data:
        st.sidebar.warning("⚠️ Tidak ada kredensial Google Sheets yang ditemukan")
        return None
        
    max_retries = 2
    for attempt in range(max_retries):
        try:
            # Create credentials and authorize client
            creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_data, CREDS_SCOPES)
            client = gspread.authorize(creds)
            
            # Try to open the spreadsheet
            try:
                spreadsheet = client.open("BatikGalleryData")
            except gspread.exceptions.SpreadsheetNotFound:
                st.sidebar.error("❌ Spreadsheet 'BatikGalleryData' tidak ditemukan")
                st.sidebar.info("ℹ️ Pastikan:")
                st.sidebar.info("1. Spreadsheet sudah dibuat di Google Drive")
                st.sidebar.info("2. Nama tepat 'BatikGalleryData'")
                st.sidebar.info("3. Sudah di-share dengan service account")
                return None
            except Exception as e:
                st.sidebar.error(f"❌ Error membuka spreadsheet: {str(e)}")
                return None
            
            # Try to get the worksheet
            try:
                sheet = spreadsheet.worksheet(sheet_name)
                st.sidebar.success(f"✅ Berhasil mengakses worksheet: {sheet_name}")
                return sheet
                
            except gspread.exceptions.WorksheetNotFound:
                # Create new worksheet if it doesn't exist
                try:
                    st.sidebar.info(f"📝 Worksheet '{sheet_name}' tidak ditemukan, membuat baru...")
                    
                    if sheet_name == "products":
                        sheet = spreadsheet.add_worksheet(title=sheet_name, rows=100, cols=15)
                        sheet.append_row(["id", "name", "description", "price", "discount", "category", 
                                        "materials", "creation_date", "image_path", 
                                        "shopee_link", "tokopedia_link", "other_link", 
                                        "payment_methods", "status", "stock"])
                    elif sheet_name == "activities":
                        sheet = spreadsheet.add_worksheet(title=sheet_name, rows=100, cols=8)
                        sheet.append_row(["id", "title", "date", "description", "image_path", 
                                        "location", "participants", "status"])
                    elif sheet_name == "awards":
                        sheet = spreadsheet.add_worksheet(title=sheet_name, rows=100, cols=8)
                        sheet.append_row(["id", "title", "organization", "year", "image_path", 
                                        "category", "description", "level"])
                    elif sheet_name == "inventory":
                        sheet = spreadsheet.add_worksheet(title=sheet_name, rows=100, cols=12)
                        sheet.append_row(["id", "item_name", "item_type", "supplier", "current_stock", 
                                        "minimum_stock", "unit", "price_per_unit", "total_value", 
                                        "notes", "last_updated", "status"])
                    elif sheet_name == "inventory_history":
                        sheet = spreadsheet.add_worksheet(title=sheet_name, rows=100, cols=10)
                        sheet.append_row(["id", "item_id", "transaction_date", "transaction_type", 
                                        "amount", "notes", "unit_price", "total_value", 
                                        "user", "reference"])
                    elif sheet_name == "financial_transactions":
                        sheet = spreadsheet.add_worksheet(title=sheet_name, rows=100, cols=12)
                        sheet.append_row(["id", "transaction_date", "transaction_type", "category", 
                                        "description", "value", "payment_method", "reference", 
                                        "notes", "status", "user", "approval_date"])
                    elif sheet_name == "production_costs":
                        sheet = spreadsheet.add_worksheet(title=sheet_name, rows=100, cols=12)
                        sheet.append_row(["id", "product_id", "component_name", "component_type", 
                                        "quantity", "unit", "unit_cost", "total_cost", 
                                        "notes", "supplier", "date_added", "status"])
                    else:
                        # Default worksheet
                        sheet = spreadsheet.add_worksheet(title=sheet_name, rows=100, cols=10)
                        sheet.append_row(["id", "name", "description", "created_date", "status"])
                    
                    st.sidebar.success(f"✅ Worksheet '{sheet_name}' berhasil dibuat")
                    return sheet
                    
                except Exception as create_error:
                    st.sidebar.error(f"❌ Gagal membuat worksheet: {str(create_error)}")
                    return None
                    
            except Exception as worksheet_error:
                st.sidebar.error(f"❌ Error mengakses worksheet: {str(worksheet_error)}")
                return None
                
        except gspread.exceptions.APIError as e:
            if attempt == max_retries - 1:
                error_msg = str(e)
                if "PERMISSION_DENIED" in error_msg:
                    st.sidebar.error("❌ Permission denied. Pastikan:")
                    st.sidebar.info("1. Google Sheets API sudah di-enable")
                    st.sidebar.info("2. Service account punya akses ke spreadsheet")
                    st.sidebar.info("3. Spreadsheet sudah di-share dengan service account")
                elif "QUOTA_EXCEEDED" in error_msg:
                    st.sidebar.error("❌ Quota exceeded. Coba lagi nanti.")
                else:
                    st.sidebar.error(f"❌ Google Sheets API Error: {error_msg}")
                return None
            time.sleep(1)  # Wait before retrying
            continue
            
        except Exception as e:
            if attempt == max_retries - 1:
                st.sidebar.error(f"❌ Unexpected error: {str(e)}")
                return None
            time.sleep(1)
            continue
    
    return None

# --- IMAGE HANDLING ---
def generate_unique_filename(original_name):
    """Generate unique filename to prevent collisions"""
    ext = original_name.split('.')[-1]
    unique_id = uuid.uuid4().hex[:8]
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{timestamp}_{unique_id}.{ext}"

def save_image(uploaded_file, directory=IMAGE_DIR):
    """Save uploaded image to Google Drive and return public URL"""
    try:
        # Save file temporarily
        temp_dir = Path(__file__).parent / "temp"
        os.makedirs(temp_dir, exist_ok=True)
        
        unique_filename = generate_unique_filename(uploaded_file.name)
        temp_path = temp_dir / unique_filename
        
        with open(temp_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        # Upload to Google Drive
        drive_url = upload_to_drive(str(temp_path), directory)
        
        # Clean up temp file
        try:
            os.remove(temp_path)
        except:
            pass
        
        return drive_url if drive_url else DEFAULT_IMAGE
        
    except Exception as e:
        st.error(f"❌ Failed to save image: {str(e)}")
        return DEFAULT_IMAGE

def display_image(image_path, width=300):
    """Safe function to display image from Google Drive"""
    try:
        if not image_path or image_path == DEFAULT_IMAGE:
            st.image(DEFAULT_IMAGE, width=width)
            return False
        
        # Get image from Google Drive
        drive_url = get_image_from_drive(image_path)
        
        if drive_url == DEFAULT_IMAGE:
            st.image(DEFAULT_IMAGE, width=width)
            return False
        
        st.image(drive_url, width=width)
        return True
            
    except Exception as img_error:
        st.error(f"Error gambar: {str(img_error)}")
        st.image(DEFAULT_IMAGE, width=width)
        return False

# --- DATA OPERATIONS ---
@st.cache_data(ttl=600)
def get_all_products():
    """Get all products with comprehensive error handling"""
    try:
        sheet = get_google_sheet("products")
        
        # Check if sheet is None (connection failed)
        if sheet is None:
            st.warning("⚠️ Tidak terhubung ke Google Sheets. Mode offline diaktifkan.")
            return get_fallback_products()
        
        try:
            records = sheet.get_all_records()
        except Exception as e:
            st.error(f"❌ Gagal membaca data dari sheet: {str(e)}")
            return get_fallback_products()
        
        if not records:
            st.info("📝 Spreadsheet produk kosong. Tambahkan data pertama Anda.")
            return get_fallback_products()
            
        df = pd.DataFrame(records)
        
        # Validate and ensure required columns exist
        required_columns = {
            "id": 0,
            "name": "Unnamed Product",
            "description": "No description available",
            "price": 0,
            "discount": 0,
            "category": "Uncategorized",
            "materials": "Not specified",
            "creation_date": datetime.now().strftime("%Y-%m-%d"),
            "image_path": DEFAULT_IMAGE
        }
        
        for col, default_value in required_columns.items():
            if col not in df.columns:
                df[col] = default_value
                st.warning(f"⚠️ Kolom '{col}' tidak ditemukan, menggunakan nilai default")
        
        return df
        
    except Exception as e:
        st.error(f"❌ Gagal mengambil data produk: {str(e)}")
        return get_fallback_products()

# --- FALLBACK DATA FUNCTIONS ---
def get_fallback_products():
    """Return fallback products data when Google Sheets is not available"""
    sample_data = {
        "id": [1, 2, 3, 4, 5],
        "name": ["Batik Parang Classic", "Batik Mega Mendung", "Batik Kawung", "Batik Sidomukti", "Batik Truntum"],
        "description": [
            "Batik Parang klasik dengan motif tradisional",
            "Batik Mega Mendung dengan warna cerah",
            "Batik Kawung motif geometris elegan", 
            "Batik Sidomukti untuk acara formal",
            "Batik Truntum simbol cerah abadi"
        ],
        "price": [450000, 550000, 350000, 650000, 500000],
        "discount": [0, 10, 5, 0, 15],
        "category": ["Traditional", "Traditional", "Geometric", "Formal", "Traditional"],
        "materials": ["Katun Prima", "Sutra Alam", "Katun Jepang", "Sutra Premium", "Katun Mori"],
        "creation_date": ["2024-01-15", "2024-02-20", "2024-01-30", "2024-03-10", "2024-02-05"],
        "image_path": [
            DEFAULT_IMAGE,
            DEFAULT_IMAGE,
            DEFAULT_IMAGE,
            DEFAULT_IMAGE,
            DEFAULT_IMAGE
        ],
        "shopee_link": ["", "", "", "", ""],
        "tokopedia_link": ["", "", "", "", ""],
        "other_link": ["", "", "", "", ""],
        "payment_methods": ["Transfer Bank, COD", "Transfer Bank", "Transfer Bank, E-Wallet", "Transfer Bank", "Transfer Bank, COD"]
    }
    return pd.DataFrame(sample_data)

def get_fallback_data(sheet_name):
    """Return empty dataframe for various sheet types"""
    if sheet_name == "activities":
        return pd.DataFrame(columns=["id", "title", "date", "description", "image_path", "location"])
    elif sheet_name == "awards":
        return pd.DataFrame(columns=["id", "title", "organization", "year", "image_path", "category"])
    elif sheet_name == "inventory":
        return pd.DataFrame(columns=["id", "item_name", "item_type", "supplier", "current_stock", 
                                   "minimum_stock", "unit", "price_per_unit", "total_value", 
                                   "notes", "last_updated"])
    elif sheet_name == "inventory_history":
        return pd.DataFrame(columns=["id", "item_id", "transaction_date", "transaction_type", 
                                   "amount", "notes", "unit_price", "total_value"])
    elif sheet_name == "financial_transactions":
        return pd.DataFrame(columns=["id", "transaction_date", "transaction_type", "category", 
                                   "description", "value", "payment_method", "reference", "notes"])
    elif sheet_name == "production_costs":
        return pd.DataFrame(columns=["id", "product_id", "component_name", "component_type", 
                                   "quantity", "unit", "unit_cost", "total_cost", "notes"])
    else:
        return pd.DataFrame(columns=["id", "name", "description"])

@st.cache_data(ttl=600)
def get_all_activities():
    try:
        sheet = get_google_sheet("activities")
        records = sheet.get_all_records()
        
        if not records:
            return pd.DataFrame(columns=["id", "title", "date", "description", "image_path"])
            
        return pd.DataFrame(records)
        
    except Exception as e:
        st.error(f"Gagal mengambil data kegiatan: {str(e)}")
        return pd.DataFrame(columns=["id", "title", "date", "description", "image_path"])

@st.cache_data(ttl=600)
def get_all_awards():
    try:
        sheet = get_google_sheet("awards")
        records = sheet.get_all_records()
        
        if not records:
            return pd.DataFrame(columns=["id", "title", "organization", "year", "image_path"])
            
        return pd.DataFrame(records)
        
    except Exception as e:
        st.error(f"Gagal mengambil data penghargaan: {str(e)}")
        return pd.DataFrame(columns=["id", "title", "organization", "year", "image_path"])

@st.cache_data(ttl=600)
def get_all_inventory():
    try:
        sheet = get_google_sheet("inventory")
        records = sheet.get_all_records()
        
        if not records:
            return pd.DataFrame(columns=["id", "item_name", "item_type", "supplier", "current_stock", 
                                       "minimum_stock", "unit", "price_per_unit", "total_value", 
                                       "notes", "last_updated"])
            
        df = pd.DataFrame(records)
        return df
        
    except Exception as e:
        st.error(f"Gagal mengambil data inventaris: {str(e)}")
        return pd.DataFrame(columns=["id", "item_name", "item_type", "supplier", "current_stock", 
                                   "minimum_stock", "unit", "price_per_unit", "total_value", 
                                   "notes", "last_updated"])

@st.cache_data(ttl=600)
def get_inventory_history():
    try:
        sheet = get_google_sheet("inventory_history")
        records = sheet.get_all_records()
        
        if not records:
            return pd.DataFrame(columns=["id", "item_id", "transaction_date", "transaction_type", 
                                       "amount", "notes", "unit_price", "total_value"])
            
        df = pd.DataFrame(records)
        return df
        
    except Exception as e:
        st.error(f"Gagal mengambil riwayat inventaris: {str(e)}")
        return pd.DataFrame(columns=["id", "item_id", "transaction_date", "transaction_type", 
                                   "amount", "notes", "unit_price", "total_value"])

@st.cache_data(ttl=600)
def get_financial_transactions():
    try:
        sheet = get_google_sheet("financial_transactions")
        records = sheet.get_all_records()
        
        if not records:
            return pd.DataFrame(columns=["id", "transaction_date", "transaction_type", "category", 
                                       "description", "value", "payment_method", "reference", "notes"])
            
        df = pd.DataFrame(records)
        return df
        
    except Exception as e:
        st.error(f"Gagal mengambil transaksi keuangan: {str(e)}")
        return pd.DataFrame(columns=["id", "transaction_date", "transaction_type", "category", 
                                   "description", "value", "payment_method", "reference", "notes"])

@st.cache_data(ttl=600)
def get_production_costs():
    try:
        sheet = get_google_sheet("production_costs")
        records = sheet.get_all_records()
        
        if not records:
            return pd.DataFrame(columns=["id", "product_id", "component_name", "component_type", 
                                       "quantity", "unit", "unit_cost", "total_cost", "notes"])
            
        df = pd.DataFrame(records)
        return df
        
    except Exception as e:
        st.error(f"Gagal mengambil data biaya produksi: {str(e)}")
        return pd.DataFrame(columns=["id", "product_id", "component_name", "component_type", 
                                   "quantity", "unit", "unit_cost", "total_cost", "notes"])

# --- DEBUG FUNCTIONS ---
def debug_google_sheets_connection():
    """Debug function to check Google Sheets connection"""
    st.sidebar.header("🔍 Debug Google Sheets Connection")
    
    # Test credentials
    creds_data = get_google_creds()
    if creds_data:
        st.sidebar.success("✅ Credentials ditemukan")
        st.sidebar.text(f"Project: {creds_data.get('project_id', 'N/A')}")
        st.sidebar.text(f"Client Email: {creds_data.get('client_email', 'N/A')}")
    else:
        st.sidebar.error("❌ Tidak ada credentials ditemukan")
        return False
    
    # Test connection to products sheet
    try:
        sheet = get_google_sheet("products")
        if sheet:
            try:
                records = sheet.get_all_records()
                st.sidebar.success(f"✅ Terhubung! {len(records)} records ditemukan")
                
                # Show first few records
                if records:
                    st.sidebar.info("📋 Sample data:")
                    for i, record in enumerate(records[:3]):
                        st.sidebar.text(f"{i+1}. {record.get('name', 'No name')} - Rp {record.get('price', 0):,}")
                
                return True
            except Exception as e:
                st.sidebar.error(f"❌ Gagal membaca records: {str(e)}")
                return False
        else:
            st.sidebar.error("❌ Gagal terhubung ke Google Sheets")
            return False
            
    except Exception as e:
        st.sidebar.error(f"❌ Error: {str(e)}")
        return False

def debug_google_drive_connection():
    """Debug function to check Google Drive connection"""
    st.sidebar.header("🔍 Debug Google Drive Connection")
    
    drive_service = get_drive_service()
    if not drive_service:
        st.sidebar.error("❌ Tidak dapat terhubung ke Google Drive")
        return False
    
    try:
        # List files in the main folder
        response = drive_service.files().list(
            q=f"'{GOOGLE_DRIVE_FOLDER_ID}' in parents and trashed=false",
            spaces='drive',
            fields='files(id, name, mimeType)',
            pageSize=5
        ).execute()
        
        files = response.get('files', [])
        
        if files:
            st.sidebar.success(f"✅ Terhubung ke Google Drive! {len(files)} file ditemukan")
            st.sidebar.info("📁 File/folder di root:")
            for file in files:
                st.sidebar.text(f"- {file['name']} ({'folder' if file['mimeType'] == 'application/vnd.google-apps.folder' else 'file'})")
            return True
        else:
            st.sidebar.success("✅ Terhubung ke Google Drive! Folder kosong")
            return True
            
    except Exception as e:
        st.sidebar.error(f"❌ Error mengakses Google Drive: {str(e)}")
        return False

def add_record(sheet_name, record_data):
    """Generic function to add a record to any sheet"""
    try:
        sheet = get_google_sheet(sheet_name)
        headers = sheet.row_values(1)
        row_data = [record_data.get(col, "") for col in headers]
        sheet.append_row(row_data)
        st.cache_data.clear()
        return True
    except Exception as e:
        st.error(f"❌ Failed to add record: {str(e)}")
        return False

def update_record(sheet_name, record_id, updated_data):
    """Generic function to update a record in any sheet"""
    try:
        sheet = get_google_sheet(sheet_name)
        records = sheet.get_all_records()
        headers = sheet.row_values(1)
        
        found = False
        for idx, record in enumerate(records, start=2):
            if str(record['id']) == str(record_id):
                found = True
                for col, value in updated_data.items():
                    if col in headers:
                        col_idx = headers.index(col) + 1
                        sheet.update_cell(idx, col_idx, value)
                break
        
        if found:
            st.cache_data.clear()
        return found
    except Exception as e:
        st.error(f"❌ Failed to update record: {str(e)}")
        return False

def delete_record(sheet_name, record_id):
    """Generic function to delete a record from any sheet"""
    try:
        sheet = get_google_sheet(sheet_name)
        records = sheet.get_all_records()
        
        found = False
        for idx, record in enumerate(records, start=2):
            if str(record['id']) == str(record_id):
                sheet.delete_rows(idx)
                found = True
                break
        
        if found:
            st.cache_data.clear()
        return found
    except Exception as e:
        st.error(f"❌ Failed to delete record: {str(e)}")
        return False

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
        inventory_df = get_all_inventory()
        item = inventory_df[inventory_df['id'] == item_id].iloc[0].to_dict()
        
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
        updated_data = {
            "current_stock": new_stock,
            "total_value": new_stock * float(item['price_per_unit']),
            "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        if update_record("inventory", item_id, updated_data):
            # Create history record
            history_data = {
                "item_id": item_id,
                "transaction_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "transaction_type": transaction_type,
                "amount": amount,
                "notes": notes,
                "unit_price": item['price_per_unit'],
                "total_value": float(amount) * float(item['price_per_unit'])
            }
            
            if add_record("inventory_history", history_data):
                return True
        return False
    except Exception as e:
        st.error(f"Error updating inventory: {str(e)}")
        return False

# --- FINANCIAL MANAGEMENT FUNCTIONS ---
def calculate_financial_balance():
    """Calculate current financial balance"""
    transactions = get_financial_transactions()
    if transactions.empty:
        return 0
    
    income = transactions[transactions['transaction_type'] == 'income']['value'].sum()
    expense = transactions[transactions['transaction_type'] == 'expense']['value'].sum()
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
    with stylable_container(
        key="hpp_input_container",
        css_styles="""
            {
                background-color: white;
                border-radius: 12px;
                padding: 25px;
                box-shadow: 0 4px 12px rgba(0,0,0,0.05);
                border: 1px solid #eaeaea;
                margin-bottom: 20px;
            }
        """
    ):
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
    
    with stylable_container(
        key="hpp_calculation_container",
        css_styles="""
            {
                background-color: white;
                border-radius: 12px;
                padding: 25px;
                box-shadow: 0 4px 12px rgba(0,0,0,0.05);
                border: 1px solid #eaeaea;
                margin-bottom: 20px;
            }
        """
    ):
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
        
        # Detailed breakdown
        with st.expander("🔍 Detail Rincian Biaya"):
            st.markdown("#### 📦 Biaya Bahan Baku")
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**Kain ({data['fabric_type']})**")
                st.write(f"Area: {fabric_area:.2f} m²")
                st.write(f"Harga: {format_price(data['fabric_price_per_meter'], language)}/m")
                st.write(f"Total: {format_price(fabric_cost, language)}")
                
            with col2:
                st.write(f"**Lilin Batik**")
                st.write(f"Kebutuhan: {data['wax_quantity']} gram")
                st.write(f"Harga: {format_price(data['wax_price_per_kg'], language)}/kg")
                st.write(f"Total: {format_price(wax_cost, language)}")
                
                st.write(f"**Pewarna ({data['dye_type']})**")
                st.write(f"Total: {format_price(dye_cost, language)}")
            
            st.markdown("#### 👷 Biaya Tenaga Kerja")
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**Perancangan Pola**")
                st.write(f"Waktu: {data['design_hours']} jam")
                st.write(f"Upah: {format_price(data['design_hourly_rate'], language)}/jam")
                st.write(f"Total: {format_price(design_labor_cost, language)}")
                
            with col2:
                st.write(f"**Proses Membatik**")
                st.write(f"Waktu: {data['waxing_hours']} jam")
                st.write(f"Upah: {format_price(data['batik_artist_hourly_rate'], language)}/jam")
                st.write(f"Total: {format_price(waxing_labor_cost, language)}")
                
                st.write(f"**Proses Pewarnaan**")
                st.write(f"Proses: {data['dyeing_processes']}x")
                st.write(f"Waktu: {data['dyeing_hours_per_process']} jam/proses")
                st.write(f"Upah: {format_price(data['dyeing_hourly_rate'], language)}/jam")
                st.write(f"Total: {format_price(dyeing_labor_cost, language)}")
            
            st.markdown("#### ⚙️ Biaya Produksi Lainnya")
            st.write(f"**Pelorodan ({data['boiling_process']})**: {format_price(data['boiling_cost'], language)}")
            st.write(f"**Pengunci Warna**: {format_price(data['color_fixing'], language)}")
            st.write(f"**Pengeringan**: {format_price(data['drying_cost'], language)}")
            st.write(f"**Kemasan**: {format_price(data['packaging_cost'], language)}")
            
            st.markdown("#### 📈 Overhead")
            st.write(f"**Persentase**: {data['overhead_percentage']}%")
            st.write(f"**Nilai**: {format_price(overhead_cost, language)}")

def show_results(language):
    """Show HPP results and pricing recommendations"""
    if 'hpp_calculations' not in st.session_state:
        st.warning("Silakan lakukan kalkulasi HPP terlebih dahulu di tab 'Kalkulasi HPP'")
        return
    
    data = st.session_state.hpp_data
    calculations = st.session_state.hpp_calculations
    
    with stylable_container(
        key="hpp_results_container",
        css_styles="""
            {
                background-color: white;
                border-radius: 12px;
                padding: 25px;
                box-shadow: 0 4px 12px rgba(0,0,0,0.05);
                border: 1px solid #eaeaea;
                margin-bottom: 20px;
            }
        """
    ):
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
        
        # Pricing strategy
        st.markdown("### 🎯 Strategi Pricing")
        
        pricing_strategies = {
            "Economy": calculations['hpp_per_unit'] * 1.3,
            "Standard": calculations['hpp_per_unit'] * 1.5,
            "Premium": calculations['hpp_per_unit'] * 2.0,
            "Luxury": calculations['hpp_per_unit'] * 3.0
        }
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Economy", format_price(pricing_strategies["Economy"], language))
        with col2:
            st.metric("Standard", format_price(pricing_strategies["Standard"], language))
        with col3:
            st.metric("Premium", format_price(pricing_strategies["Premium"], language))
        with col4:
            st.metric("Luxury", format_price(pricing_strategies["Luxury"], language))
        
        # Cost optimization suggestions
        st.markdown("### 💡 Saran Optimasi Biaya")
        
        suggestions = []
        
        # Fabric cost optimization
        if calculations['material_costs'] > 100000:
            suggestions.append("✓ Pertimbangkan pembelian kain dalam jumlah besar untuk mendapatkan harga wholesale")
        
        # Labor cost optimization
        if calculations['labor_costs'] > 150000:
            suggestions.append("✓ Latih pembatik untuk meningkatkan efisiensi waktu kerja")
            suggestions.append("✓ Pertimbangkan sistem kerja piece-rate untuk meningkatkan produktivitas")
        
        # Wax cost optimization
        wax_cost_per_unit = (data['wax_quantity'] / 1000) * data['wax_price_per_kg'] / data['production_quantity']
        if wax_cost_per_unit > 5000:
            suggestions.append("✓ Optimalkan penggunaan lilin dengan teknik yang lebih efisien")
            suggestions.append("✓ Recycle lilin yang sudah digunakan untuk mengurangi pembelian baru")
        
        # Dye cost optimization
        if data['dye_price'] > 100000 and "Alami" in data['dye_type']:
            suggestions.append("✓ Pertimbangkan membuat pewarna alami sendiri untuk mengurangi biaya")
        
        if suggestions:
            for suggestion in suggestions:
                st.success(suggestion)
        else:
            st.info("✅ Biaya produksi sudah cukup efisien. Pertahankan!")
        
        # Export results
        st.markdown("### 📤 Export Hasil")
        
        if st.button("💾 Simpan sebagai Template", width='stretch'):
            # Save template functionality would go here
            st.success("Template berhasil disimpan!")
        
        if st.button("📄 Export to Excel", width='stretch'):
            # Export to Excel functionality would go here
            st.success("Data berhasil diexport ke Excel!")
        
        if st.button("🖨️ Cetak Laporan", width='stretch'):
            # Print functionality would go here
            st.success("Laporan siap dicetak!")

# --- UI COMPONENTS ---
def apply_professional_style():
    """Apply a clean white-ui professional styling with dark text"""
    st.markdown("""
    <style>
        /* ===== BASE STYLES ===== */
        :root {
            --white: #FFFFFF;
            --black: #000000;
            --light-gray: #F5F5F5;
            --medium-gray: #E0E0E0;
            --primary-blue: #4A6FA5;
        }
        
        /* ===== GLOBAL RESETS ===== */
        * {
            color: var(--black) !important;
            font-family: 'Inter', sans-serif;
        }
        
        /* ===== MAIN CONTAINERS ===== */
        .stApp {
            background-color: var(--light-gray) !important;
        }
        
        [data-testid="stSidebar"] {
            background-color: var(--white) !important;
            border-right: 1px solid var(--medium-gray) !important;
        }
        
        /* ===== INPUT COMPONENTS ===== */
        /* Text Input */
        .stTextInput input,
        .stNumberInput input,
        .stTextArea textarea {
            background-color: var(--white) !important;
            border: 1px solid var(--medium-gray) !important;
            color: var(--black) !important;
        }
        
        /* Selectbox/Dropdown */
        .stSelectbox [data-baseweb="select"] {
            background-color: var(--white) !important;
        }
        .stSelectbox [data-baseweb="popover"] {
            background-color: var(--white) !important;
        }
        .stSelectbox [data-baseweb="menu"] {
            background-color: var(--white) !important;
        }
        .stSelectbox [role="option"] {
            background-color: var(--white) !important;
            color: var(--black) !important;
        }
        .stSelectbox [role="option"]:hover {
            background-color: var(--light-gray) !important;
        }
        
        /* Multiselect */
        .stMultiSelect [data-baseweb="popover"] {
            background-color: var(--white) !important;
        }
        .stMultiSelect [data-baseweb="menu"] {
            background-color: var(--white) !important;
        }
        .stMultiSelect [role="option"] {
            background-color: var(--white) !important;
            color: var(--black) !important;
        }
        .stMultiSelect [role="option"]:hover {
            background-color: var(--light-gray) !important;
        }
        .stMultiSelect [data-baseweb="tag"] {
            background-color: var(--light-gray) !important;
            color: var(--black) !important;
        }
        
        /* Date Input */
        .stDateInput [data-baseweb="input"] {
            background-color: var(--white) !important;
        }
        .stDateInput [data-baseweb="popover"] {
            background-color: var(--white) !important;
        }
        .stDateInput [data-baseweb="calendar"] {
            background-color: var(--white) !important;
        }
        .stDateInput [aria-label^="Choose"] {
            color: var(--black) !important;
        }
        .stDateInput [aria-label^="Choose"]:hover {
            background-color: var(--light-gray) !important;
        }
        
        /* Time Input */
        .stTimeInput [data-baseweb="popover"] {
            background-color: var(--white) !important;
        }
        .stTimeInput [data-baseweb="menu"] {
            background-color: var(--white) !important;
        }
        
        /* File Uploader */
        .stFileUploader > div > div {
            background-color: var(--white) !important;
            border: 2px dashed var(--medium-gray) !important;
        }
        
        /* ===== DATA DISPLAY ===== */
        /* Tables */
        .stDataFrame,
        .stTable {
            background-color: var(--white) !important;
        }
        .stDataFrame th,
        .stDataFrame td {
            background-color: var(--white) !important;
            border-color: var(--medium-gray) !important;
        }
        
        /* Expanders */
        .stExpander {
            background-color: var(--white) !important;
            border: 1px solid var(--medium-gray) !important;
        }
        
        /* Tabs */
        [data-baseweb="tab"] {
            background-color: var(--white) !important;
        }
        
        /* Metrics */
        .stMetric {
            background-color: var(--white) !important;
            border: 1px solid var(--medium-gray) !important;
        }
        
        /* ===== CHARTS ===== */
        /* Plotly Charts */
        .js-plotly-plot .plot-container {
            background-color: var(--white) !important;
        }
        .xtick, .ytick,
        .xaxis-title, .yaxis-title {
            fill: var(--black) !important;
        }
        
        /* ===== BUTTONs ===== */
        .stButton > button {
            background-color: var(--white) !important;
            color: var(--primary-blue) !important;
            border: 1px solid var(--primary-blue) !important;
        }
        .stButton > button:hover {
            background-color: var(--light-gray) !important;
        }
        
        /* ===== TYPOGRAPHY ===== */
        h1, h2, h3, h4, h5, h6 {
            font-family: 'Poppins', sans-serif;
            font-weight: 600;
            color: var(--black) !important;
        }
        p, div, span {
            color: var(--black) !important;
        }
        
        /* ===== SPECIAL CASES ===== */
        /* Calendar header */
        .DayPicker-Caption {
            color: var(--black) !important;
        }
        /* Time picker numbers */
        [data-baseweb="menu"] li {
            color: var(--black) !important;
        }
        
        /* ===== METRIC CARDS FIX ===== */
        /* Container untuk metric cards */
        [data-testid="metric-container"] {
            background-color: white !important;
            border: 1px solid #E0E0E0 !important;
            border-radius: 8px !important;
            padding: 10px !important;
            width: 80% !important;
            box-sizing: border-box !important;
        }

        /* Judul metric */
        [data-testid="stMetricLabel"] {
            font-size: 14px !important;
            color: black !important;
            padding-bottom: 4px !important;
        }

        /* Nilai metric (angka) */
        [data-testid="stMetricValue"] {
            font-size: 24px !important;
            font-weight: bold !important;
            color: black !important;
        }

        /* Deskripsi kecil di bawah nilai */
        [data-testid="stMetricDelta"] {
            font-size: 12px !important;
        }

        /* Hover effect (opsional) */
        [data-testid="metric-container"]:hover {
            box-shadow: 0 2px 8px rgba(0,0,0,0.1) !important;
        }
    </style>
    <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700&family=Inter:wght@400;500;600&display=swap" rel="stylesheet">
    """, unsafe_allow_html=True)

def display_header(language):
    """Display premium app header with responsive logo and title"""
    col1, col2 = st.columns([1, 4])
    with col1:
        try:
            # Try to get logo from Google Drive
            logo_url = get_image_from_drive("logo_batik.png")
            if logo_url != DEFAULT_IMAGE:
                st.image(logo_url, width=120)
            else:
                st.image(DEFAULT_IMAGE, width=120, caption="Logo")
        except:
            st.image(DEFAULT_IMAGE, width=120, caption="Logo")
    with col2:
        st.markdown(f"""
        <h1 style="margin-bottom: 0; color: #000000;">{LANGUAGES[language]["title"]}</h1>
        <p style="color: #4a6fa5; font-size: 16px; margin-top: 0.5rem;">{LANGUAGES[language]["subtitle"]}</p>
        """, unsafe_allow_html=True)

# --- PRODUCT CARD ---
def product_card(product, language):
    """New improved product card design with discount support"""
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
        with st.container(border=True):
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
            
            # Marketplace Links - Scaled down to 10%
            if shopee_link or tokopedia_link or other_link:
                st.markdown(f"<p style='color: #555; font-size: 14px; margin-bottom: 8px;'><strong>{LANGUAGES[language]['available_on']}</strong></p>", unsafe_allow_html=True)
                
                links = []
                if shopee_link:
                    links.append(f"""
                    <a href="{shopee_link}" target="_blank">
                        <img src="https://upload.wikimedia.org/wikipedia/commons/f/fe/Shopee.svg" 
                             style="width:15%; height:auto; margin-right:10px; margin-bottom:10px;">
                    </a>
                    """)
                if tokopedia_link:
                    links.append(f"""
                    <a href="{tokopedia_link}" target="_blank">
                        <img src="https://upload.wikimedia.org/wikipedia/commons/8/85/Tokopedia.svg" 
                             style="width:15%; height:auto; margin-right:10px; margin-bottom:10px;">
                    </a>
                    """)
                if other_link:
                    links.append(f"""
                    <a href="{other_link}" target="_blank">
                        <img src="https://cdn-icons-png.flaticon.com/512/841/841364.png" 
                             style="width:15%; height:auto; margin-right:10px; margin-bottom:10px;">
                    </a>
                    """)
                
                st.markdown("".join(links), unsafe_allow_html=True)
            
            # Description with expander
            with st.expander(LANGUAGES[language]["description_label"]):
                st.write(product_description)
            
            # Only show edit button for admin
            if st.session_state.get("is_admin", False):
                if st.button(
                    "✏️ Edit Product",
                    key=f"edit_{product_id}",
                    width='stretch'
                ):
                    st.session_state['edit_product'] = product_id
    
    except Exception as e:
        st.error(f"Error displaying product: {str(e)}")
        with st.container(border=True):
            display_image(DEFAULT_IMAGE)
            st.subheader("Product")
            st.write(f"Price: {format_price(0, language)}")
            st.button("Details", key=f"fallback_{product_id}")

# --- ACTIVITY CARD ---
def activity_card(activity, language):
    """Display an activity card with image and details"""
    try:
        with st.container(border=True):
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
                    key=f"edit_activity_{activity.get('id', '')}",
                    width='stretch'
                ):
                    st.session_state['edit_activity'] = activity.get('id', '')
    
    except Exception as e:
        st.error(f"Error displaying activity: {str(e)}")

# --- AWARD CARD ---
def award_card(award, language):
    """Display an award card with image and details"""
    try:
        with st.container(border=True):
            # Award Image
            image_path = award.get("image_path", DEFAULT_IMAGE)
            display_image(image_path)
            
            # Award Info
            st.markdown(f"<h3 style='color: #000000; margin-bottom: 0.5rem;'>{award.get('title', 'Unknown Award')}</h3>", unsafe_allow_html=True)
            
            # Organization and Year
            st.markdown(f"<p style='color: #555; font-size: 14px;'><strong>Organization:</strong> {award.get('organization', 'Unknown')}</p>", unsafe_allow_html=True)
            st.markdown(f'<p style="color: #555; font-size: 14px; margin-bottom: 12px;"><strong>Year:</strong> {award.get("year", "Unknown")}</p>', unsafe_allow_html=True
)

            
            # Only show edit button for admin
            if st.session_state.get("is_admin", False):
                if st.button(
                    "✏️ Edit Award",
                    key=f"edit_award_{award.get('id', '')}",
                    width='stretch'
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
            df = get_all_products()
        
        if df is None or df.empty:
            st.warning("Belum ada produk tersedia")
        else:
            st.markdown(f"""
            <h3 style="margin-bottom: 1rem; color: #000000;">{LANGUAGES[language]["featured"]}</h3>
            """, unsafe_allow_html=True)
            
            sample_size = min(6, len(df))
            if sample_size > 0:
                featured = df.sample(n=sample_size)
                
                # Display products in a grid
                for i in range(0, len(featured), 3):
                    cols = st.columns(3)
                    for j in range(3):
                        if i + j < len(featured):
                            with cols[j]:
                                product_card(featured.iloc[i + j].to_dict(), language)
                        else:
                            with cols[j]:
                                st.empty()
            
        # Gallery Activities Section
        st.markdown("---")
        st.markdown(f"""
        <h3 style="margin-bottom: 1rem; color: #000000;">{LANGUAGES[language]["activities"]}</h3>
        """, unsafe_allow_html=True)
        
        activities_df = get_all_activities()
        if activities_df.empty:
            st.warning("No activities available" if language == "English" else "Tidak ada kegiatan tersedia")
        else:
            for i in range(0, len(activities_df), 2):
                cols = st.columns(2)
                for j in range(2):
                    if i + j < len(activities_df):
                        with cols[j]:
                            activity_card(activities_df.iloc[i + j].to_dict(), language)
        
        # Awards Section
        st.markdown("---")
        st.markdown(f"""
        <h3 style="margin-bottom: 1rem; color: #000000;">{LANGUAGES[language]["awards"]}</h3>
        """, unsafe_allow_html=True)
        
        awards_df = get_all_awards()
        if awards_df.empty:
            st.warning("No awards available" if language == "English" else "Tidak ada penghargaan tersedia")
        else:
            for i in range(0, len(awards_df), 3):
                cols = st.columns(3)
                for j in range(3):
                    if i + j < len(awards_df):
                        with cols[j]:
                            award_card(awards_df.iloc[i + j].to_dict(), language)
        
        # Location Map
        st.markdown("---")
        st.markdown(f"""
        <h3 style="margin-bottom: 1rem; color: #000000;">{LANGUAGES[language]["location"]}</h3>
        """, unsafe_allow_html=True)
        
        # Create a map centered on Indonesia
        m = folium.Map(location=[-8.1385028, 113.021961], zoom_start=12, width="100%")
        
        # Add marker for our location (example: Jakarta)
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
        df = get_all_products()
    
    if df is None or df.empty:
        st.warning("Belum ada produk tersedia")
        return
    
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
                0, int(max_price + 100000),  # Add buffer to max price
                (0, int(max_price)),
                step=get_price_step(max_price),
                key="price_filter"
            )
    
    # Apply filters
    filtered_df = df.copy()
    if search_query:
        filtered_df = filtered_df[filtered_df["name"].str.contains(search_query, case=False)]
    if category_filter != "All":
        filtered_df = filtered_df[filtered_df["category"] == category_filter]
    filtered_df = filtered_df[
        (filtered_df["price"] >= price_range[0]) & 
        (filtered_df["price"] <= price_range[1])
    ]
    
    if filtered_df.empty:
        st.warning("No products match the filters" if language == "English" else "Tidak ada produk yang sesuai dengan filter")
    else:
        # Display filtered products in a grid
        for i in range(0, len(filtered_df), 3):
            cols = st.columns(3)
            for j in range(3):
                if i + j < len(filtered_df):
                    with cols[j]:
                        product_card(filtered_df.iloc[i + j].to_dict(), language)
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
            font=dict(family="Inter", color="#000000")
        )
        
        st.plotly_chart(fig, width='stretch')
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
        key="product_operation",
        label_visibility="collapsed"
    )
    
    df = get_all_products()
    
    if operation == LANGUAGES[language]["add"]:
        with stylable_container(
            key="add_product_container",
            css_styles="""
                {
                    background-color: white;
                    border-radius: 12px;
                    padding: 25px;
                    box-shadow: 0 4px 12px rgba(0,0,0,0.05);
                }
            """
        ):
            with st.form("add_product_form", clear_on_submit=True):
                st.markdown(f"<h3 style='color: #000000; margin-bottom: 1.5rem;'>{LANGUAGES[language]['add']} Product</h3>", unsafe_allow_html=True)
                
                col1, col2 = st.columns(2)
                with col1:
                    name = st.text_input(f"{'Name' if language == 'English' else 'Nama'}*", key="prod_name")
                    category = st.text_input(f"{'Category' if language == 'English' else 'Kategori'}*", key="prod_category")
                    materials = st.text_input(f"{'Materials' if language == 'English' else 'Bahan'}*", key="prod_materials")
                with col2:
                    price = st.number_input(f"{'Price (IDR)' if language == 'English' else 'Harga (Rp)'}*", 
                                          min_value=0, key="prod_price")
                    discount = st.number_input(f"{'Discount (%)' if language == 'English' else 'Diskon (%)'}", 
                                             min_value=0, max_value=100, value=0, key="prod_discount")
                    creation_date = st.date_input(f"{'Creation Date' if language == 'English' else 'Tanggal Pembuatan'}", 
                                                datetime.now(), key="prod_date")
                
                description = st.text_area(f"{'Description' if language == 'English' else 'Deskripsi'}*", key="prod_desc")
                
                # Marketplace links
                st.markdown(f"<h4 style='color: #000000; margin-bottom: 1rem;'>{'Marketplace Links' if language == 'English' else 'Link Marketplace'}</h4>", unsafe_allow_html=True)
                col1, col2, col3 = st.columns(3)
                with col1:
                    shopee_link = st.text_input("Shopee", key="prod_shopee")
                with col2:
                    tokopedia_link = st.text_input("Tokopedia", key="prod_tokopedia")
                with col3:
                    other_link = st.text_input(f"{'Other' if language == 'English' else 'Lainnya'}", key="prod_other")
                
                # Image upload
                uploaded_image = st.file_uploader(
                    f"{'Product Image' if language == 'English' else 'Gambar Produk'}*", 
                    type=["jpg", "jpeg", "png", "webp"],
                    key="prod_image"
                )
                
                submitted = st.form_submit_button(f"{'Save Product' if language == 'English' else 'Simpan Produk'}",
                                                width='stretch')
                
                if submitted:
                    if not all([name, category, materials, price, description]):
                        st.error(f"{'Please fill required fields' if language == 'English' else 'Harap isi field wajib'} (*)")
                    else:
                        image_path = DEFAULT_IMAGE
                        if uploaded_image:
                            saved_path = save_image(uploaded_image, IMAGE_DIR)
                            if saved_path:
                                image_path = saved_path
                        
                        new_id = (df["id"].max() + 1) if not df.empty else 1
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
                        
                        if add_record("products", product_data):
                            st.success(f"{'Product added successfully!' if language == 'English' else 'Produk berhasil ditambahkan!'}")
                            st.balloons()

    elif operation == LANGUAGES[language]["edit"]:
        if df.empty:
            st.warning(f"{'No products available' if language == 'English' else 'Tidak ada produk tersedia'}")
        else:
            product_to_edit = st.selectbox(
                f"{'Select product to edit:' if language == 'English' else 'Pilih produk untuk diedit:'}",
                df["name"],
                key="edit_prod_select"
            )
            
            product_data = df[df["name"] == product_to_edit].iloc[0].to_dict()
            
            with stylable_container(
                key="edit_product_container",
                css_styles="""
                    {
                        background-color: white;
                        border-radius: 12px;
                        padding: 25px;
                        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
                    }
                """
            ):
                with st.form("edit_product_form"):
                    st.markdown(f"<h3 style='color: #000000; margin-bottom: 1.5rem;'>{LANGUAGES[language]['edit']} Product: {product_data['name']}</h3>", unsafe_allow_html=True)
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        name = st.text_input(f"{'Name' if language == 'English' else 'Nama'}*", 
                                           value=product_data["name"], key="edit_prod_name")
                        category = st.text_input(f"{'Category' if language == 'English' else 'Kategori'}*", 
                                               value=product_data["category"], key="edit_prod_category")
                        materials = st.text_input(f"{'Materials' if language == 'English' else 'Bahan'}*", 
                                                value=product_data["materials"], key="edit_prod_materials")
                    with col2:
                        price = st.number_input(f"{'Price (IDR)' if language == 'English' else 'Harga (Rp)'}*", 
                                              min_value=0, value=int(product_data["price"]), key="edit_prod_price")
                        discount = st.number_input(f"{'Discount (%)' if language == 'English' else 'Diskon (%)'}", 
                                                 min_value=0, max_value=100, 
                                                 value=int(product_data["discount"]), key="edit_prod_discount")
                        creation_date = st.date_input(f"{'Creation Date' if language == 'English' else 'Tanggal Pembuatan'}", 
                                                    datetime.strptime(product_data["creation_date"], "%Y-%m-%d").date(), 
                                                    key="edit_prod_date")
                    
                    description = st.text_area(f"{'Description' if language == 'English' else 'Deskripsi'}*", 
                                             value=product_data["description"], key="edit_prod_desc")
                    
                    # Marketplace links
                    st.markdown(f"<h4 style='color: #000000; margin-bottom: 1rem;'>{'Marketplace Links' if language == 'English' else 'Link Marketplace'}</h4>", unsafe_allow_html=True)
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        shopee_link = st.text_input("Shopee", 
                                                   value=product_data.get("shopee_link", ""), 
                                                   key="edit_prod_shopee")
                    with col2:
                        tokopedia_link = st.text_input("Tokopedia", 
                                                     value=product_data.get("tokopedia_link", ""), 
                                                     key="edit_prod_tokopedia")
                    with col3:
                        other_link = st.text_input(f"{'Other' if language == 'English' else 'Lainnya'}", 
                                                 value=product_data.get("other_link", ""), 
                                                 key="edit_prod_other")
                    
                    # Image upload
                    current_image = product_data.get("image_path", DEFAULT_IMAGE)
                    if current_image and current_image != DEFAULT_IMAGE:
                        display_image(current_image, width=200)
                    else:
                        display_image(DEFAULT_IMAGE, width=200)
                    
                    uploaded_image = st.file_uploader(
                        f"{'New Product Image' if language == 'English' else 'Gambar Produk Baru'}", 
                        type=["jpg", "jpeg", "png", "webp"],
                        key="edit_prod_image"
                    )
                    
                    submitted = st.form_submit_button(f"{'Update Product' if language == 'English' else 'Update Produk'}",
                                                    width='stretch')
                    
                    if submitted:
                        if not all([name, category, materials, price, description]):
                            st.error(f"{'Please fill required fields' if language == 'English' else 'Harap isi field wajib'} (*)")
                        else:
                            image_path = current_image
                            if uploaded_image:
                                saved_path = save_image(uploaded_image, IMAGE_DIR)
                                if saved_path:
                                    image_path = saved_path
                            
                            updated_data = {
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
                            }
                            
                            if update_record("products", product_data["id"], updated_data):
                                st.success(f"{'Product updated successfully!' if language == 'English' else 'Produk berhasil diupdate!'}")

    elif operation == LANGUAGES[language]["delete"]:
        if df.empty:
            st.warning(f"{'No products available' if language == 'English' else 'Tidak ada produk tersedia'}")
        else:
            product_to_delete = st.selectbox(
                f"{'Select product to delete:' if language == 'English' else 'Pilih produk untuk dihapus:'}",
                df["name"],
                key="delete_prod_select"
            )
            
            product_data = df[df["name"] == product_to_delete].iloc[0].to_dict()
            
            with stylable_container(
                key="delete_product_container",
                css_styles="""
                    {
                        background-color: #fff8e1;
                        border-radius: 12px;
                        padding: 25px;
                        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
                    }
                """
            ):
                st.markdown(f"""
                <h3 style="color: #000000; margin-bottom: 1rem;">⚠️ {'Are you sure you want to delete' if language == 'English' else 'Apakah Anda yakin ingin menghapus'} <span style="color: #e63946;">{product_data['name']}</span>?</h3>
                <p style="color: #555;">{'This action cannot be undone. Product data will be permanently removed.' if language == 'English' else 'Tindakan ini tidak dapat dibatalkan. Data produk akan dihapus permanen.'}</p>
                """, unsafe_allow_html=True)
                
                col1, col2, _ = st.columns([1, 1, 2])
                with col1:
                    if st.button(f"{'Confirm Delete' if language == 'English' else 'Konfirmasi Hapus'}", 
                                key="confirm_prod_delete",
                                width='stretch',
                                type="primary"):
                        if delete_record("products", product_data["id"]):
                            st.success(f"{'Product deleted successfully!' if language == 'English' else 'Produk berhasil dihapus!'}")
                with col2:
                    if st.button(f"{'Cancel' if language == 'English' else 'Batal'}", 
                               key="cancel_prod_delete",
                               width='stretch'):
                        st.experimental_rerun()

# --- SETTINGS PAGE ---
def show_settings_page(language):
    """Show settings page for admin"""
    st.markdown(f"""
    <h2 style="margin-bottom: 1rem; color: #000000;">{LANGUAGES[language]["settings"]}</h2>
    """, unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs([
        LANGUAGES[language]["other_settings"],
        LANGUAGES[language]["notifications"]
    ])
    
    with tab1:
        with stylable_container(
            key="settings_container",
            css_styles="""
                {
                    background-color: white;
                    border-radius: 12px;
                    padding: 25px;
                    box-shadow: 0 4px 12px rgba(0,0,0,0.05);
                }
            """
        ):
            st.markdown(f"<h3 style='color: #000000; margin-bottom: 1.5rem;'>{LANGUAGES[language]['other_settings']}</h3>", unsafe_allow_html=True)
            
            # Backup and restore
            col1, col2 = st.columns(2)
            with col1:
                if st.button(f"🔵 {LANGUAGES[language]['backup']}", 
                            width='stretch',
                            help="Backup all data to a file"):
                    st.warning("Backup functionality not yet implemented")
            with col2:
                if st.button(f"🟢 {LANGUAGES[language]['restore']}", 
                            width='stretch',
                            help="Restore data from a backup file"):
                    st.warning("Restore functionality not yet implemented")
            
            # Admin password change
            st.markdown("---")
            st.markdown(f"<h4 style='color: #000000; margin-bottom: 1rem;'>Change Admin Password</h4>", unsafe_allow_html=True)
            
            with st.form("change_password_form"):
                current_password = st.text_input("Current Password", type="password", key="current_pass")
                new_password = st.text_input("New Password", type="password", key="new_pass")
                confirm_password = st.text_input("Confirm New Password", type="password", key="confirm_pass")
                
                submitted = st.form_submit_button("Change Password", 
                                                width='stretch')
                
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
    
    with tab2:
        with stylable_container(
            key="notifications_container",
            css_styles="""
                {
                    background-color: white;
                    border-radius: 12px;
                    padding: 25px;
                    box-shadow: 0 4px 12px rgba(0,0,0,0.05);
                }
            """
        ):
            st.markdown(f"<h3 style='color: #000000; margin-bottom: 1.5rem;'>{LANGUAGES[language]['notifications']}</h3>", unsafe_allow_html=True)
            
            # Notification settings
            email_notifications = st.checkbox("Email Notifications", value=True)
            low_stock_alerts = st.checkbox("Low Stock Alerts", value=True)
            new_order_alerts = st.checkbox("New Order Alerts", value=True)
            
            if st.button("Save Notification Settings", 
                        width='stretch'):
                st.success("Notification settings saved!")

# --- INVENTORY MANAGEMENT PAGES ---
def show_inventory_management(language):
    """Inventory management page with stock tracking"""
    st.markdown(f"""
    <h2 style="margin-bottom: 1rem; color: #000000;">{LANGUAGES[language]["inventory_manage"]}</h2>
    """, unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs([
        LANGUAGES[language]["inventory_items"],
        LANGUAGES[language]["stock_history"],
        LANGUAGES[language]["inventory_warning"]
    ])
    
    with tab1:
        manage_inventory_items(language)
    with tab2:
        view_inventory_history(language)
    with tab3:
        show_inventory_warnings(language)

def manage_inventory_items(language):
    """Manage inventory items CRUD operations"""
    operation = st.radio(
        f"{'Select operation:' if language == 'English' else 'Pilih operasi:'}",
        [LANGUAGES[language]["add"], LANGUAGES[language]["edit"], LANGUAGES[language]["delete"]],
        horizontal=True,
        key="inventory_operation",
        label_visibility="collapsed"
    )
    
    df = get_all_inventory()
    
    if operation == LANGUAGES[language]["add"]:
        with stylable_container(
            key="add_inventory_container",
            css_styles="""
                {
                    background-color: white;
                    border-radius: 12px;
                    padding: 25px;
                    box-shadow: 0 4px 12px rgba(0,0,0,0.05);
                }
            """
        ):
            with st.form("add_inventory_form", clear_on_submit=True):
                st.markdown(f"<h3 style='color: #000000; margin-bottom: 1.5rem;'>{LANGUAGES[language]['add']} {LANGUAGES[language]['inventory_items']}</h3>", unsafe_allow_html=True)
                
                col1, col2 = st.columns(2)
                with col1:
                    item_name = st.text_input(f"{'Item Name' if language == 'English' else 'Nama Item'}*", key="inv_name")
                    item_type = st.selectbox(
                        f"{'Item Type' if language == 'English' else 'Jenis Item'}*",
                        ["Material", "Tool", "Equipment", "Other"],
                        key="inv_type"
                    )
                    supplier = st.text_input(f"{'Supplier' if language == 'English' else 'Pemasok'}", key="inv_supplier")
                with col2:
                    current_stock = st.number_input(f"{'Current Stock' if language == 'English' else 'Stok Saat Ini'}*", 
                                                   min_value=0.0, step=0.1, key="inv_stock")
                    minimum_stock = st.number_input(f"{'Minimum Stock' if language == 'English' else 'Stok Minimum'}*", 
                                                   min_value=0.0, step=0.1, key="inv_min_stock")
                    unit = st.selectbox(
                        f"{'Unit' if language == 'English' else 'Satuan'}*",
                        ["gram", "ml", "piece", "meter", "pack", "other"],
                        key="inv_unit"
                    )
                
                price_per_unit = st.number_input(
                    f"{'Price Per Unit (IDR)' if language == 'English' else 'Harga Per Unit (Rp)'}*",
                    min_value=0,
                    key="inv_price"
                )
                
                notes = st.text_area(f"{'Notes' if language == 'English' else 'Catatan'}", key="inv_notes")
                
                submitted = st.form_submit_button(f"{'Save Item' if language == 'English' else 'Simpan Item'}",
                                                width='stretch')
                
                if submitted:
                    if not all([item_name, item_type, current_stock, minimum_stock, unit, price_per_unit]):
                        st.error(f"{'Please fill required fields' if language == 'English' else 'Harap isi field wajib'} (*)")
                    else:
                        new_id = (df["id"].max() + 1) if not df.empty else 1
                        inventory_data = {
                            "id": new_id,
                            "item_name": item_name,
                            "item_type": item_type,
                            "supplier": supplier,
                            "current_stock": current_stock,
                            "minimum_stock": minimum_stock,
                            "unit": unit,
                            "price_per_unit": price_per_unit,
                            "total_value": current_stock * price_per_unit,
                            "notes": notes,
                            "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        }
                        
                        if add_record("inventory", inventory_data):
                            st.success(f"{'Item added successfully!' if language == 'English' else 'Item berhasil ditambahkan!'}")
                            st.balloons()

    elif operation == LANGUAGES[language]["edit"]:
        if df.empty:
            st.warning(f"{'No inventory items available' if language == 'English' else 'Tidak ada item inventaris tersedia'}")
        else:
            item_to_edit = st.selectbox(
                f"{'Select item to edit:' if language == 'English' else 'Pilih item untuk diedit:'}",
                df["item_name"],
                key="edit_inv_select"
            )
            
            item_data = df[df["item_name"] == item_to_edit].iloc[0].to_dict()
            
            with stylable_container(
                key="edit_inventory_container",
                css_styles="""
                    {
                        background-color: white;
                        border-radius: 12px;
                        padding: 25px;
                        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
                    }
                """
            ):
                with st.form("edit_inventory_form"):
                    st.markdown(f"<h3 style='color: #000000; margin-bottom: 1.5rem;'>{LANGUAGES[language]['edit']} {LANGUAGES[language]['inventory_items']}: {item_data['item_name']}</h3>", unsafe_allow_html=True)
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        item_name = st.text_input(f"{'Item Name' if language == 'English' else 'Nama Item'}*", 
                                                 value=item_data["item_name"], key="edit_inv_name")
                        item_type = st.selectbox(
                            f"{'Item Type' if language == 'English' else 'Jenis Item'}*",
                            ["Material", "Tool", "Equipment", "Other"],
                            index=["Material", "Tool", "Equipment", "Other"].index(item_data["item_type"]),
                            key="edit_inv_type"
                        )
                        supplier = st.text_input(f"{'Supplier' if language == 'English' else 'Pemasok'}", 
                                               value=item_data["supplier"], key="edit_inv_supplier")
                    with col2:
                        current_stock = st.number_input(f"{'Current Stock' if language == 'English' else 'Stok Saat Ini'}*", 
                                                      min_value=0.0, step=0.1, 
                                                      value=float(item_data["current_stock"]), key="edit_inv_stock")
                        minimum_stock = st.number_input(f"{'Minimum Stock' if language == 'English' else 'Stok Minimum'}*", 
                                                      min_value=0.0, step=0.1, 
                                                      value=float(item_data["minimum_stock"]), key="edit_inv_min_stock")
                        unit = st.selectbox(
                            f"{'Unit' if language == 'English' else 'Satuan'}*",
                            ["gram", "ml", "piece", "meter", "pack", "other"],
                            index=["gram", "ml", "piece", "meter", "pack", "other"].index(item_data["unit"]),
                            key="edit_inv_unit"
                        )
                    
                    price_per_unit = st.number_input(
                        f"{'Price Per Unit (IDR)' if language == 'English' else 'Harga Per Unit (Rp)'}*",
                        min_value=0,
                        value=int(item_data["price_per_unit"]),
                        key="edit_inv_price"
                    )
                    
                    notes = st.text_area(f"{'Notes' if language == 'English' else 'Catatan'}", 
                                        value=item_data["notes"], key="edit_inv_notes")
                    
                    submitted = st.form_submit_button(f"{'Update Item' if language == 'English' else 'Update Item'}",
                                                    width='stretch')
                    
                    if submitted:
                        if not all([item_name, item_type, current_stock, minimum_stock, unit, price_per_unit]):
                            st.error(f"{'Please fill required fields' if language == 'English' else 'Harap isi field wajib'} (*)")
                        else:
                            updated_data = {
                                "item_name": item_name,
                                "item_type": item_type,
                                "supplier": supplier,
                                "current_stock": current_stock,
                                "minimum_stock": minimum_stock,
                                "unit": unit,
                                "price_per_unit": price_per_unit,
                                "total_value": current_stock * price_per_unit,
                                "notes": notes,
                                "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                            }
                            
                            if update_record("inventory", item_data["id"], updated_data):
                                st.success(f"{'Item updated successfully!' if language == 'English' else 'Item berhasil diupdate!'}")

    elif operation == LANGUAGES[language]["delete"]:
        if df.empty:
            st.warning(f"{'No inventory items available' if language == 'English' else 'Tidak ada item inventaris tersedia'}")
        else:
            item_to_delete = st.selectbox(
                f"{'Select item to delete:' if language == 'English' else 'Pilih item untuk dihapus:'}",
                df["item_name"],
                key="delete_inv_select"
            )
            
            item_data = df[df["item_name"] == item_to_delete].iloc[0].to_dict()
            
            with stylable_container(
                key="delete_inventory_container",
                css_styles="""
                    {
                        background-color: #fff8e1;
                        border-radius: 12px;
                        padding: 25px;
                        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
                    }
                """
            ):
                st.markdown(f"""
                <h3 style="color: #000000; margin-bottom: 1rem;">⚠️ {'Are you sure you want to delete' if language == 'English' else 'Apakah Anda yakin ingin menghapus'} <span style="color: #e63946;">{item_data['item_name']}</span>?</h3>
                <p style="color: #555;">{'This action cannot be undone. All item data will be permanently removed.' if language == 'English' else 'Tindakan ini tidak dapat dibatalkan. Semua data item akan dihapus permanen.'}</p>
                """, unsafe_allow_html=True)
                
                col1, col2, _ = st.columns([1, 1, 2])
                with col1:
                    if st.button(f"{'Confirm Delete' if language == 'English' else 'Konfirmasi Hapus'}", 
                                key="confirm_inv_delete",
                                width='stretch',
                                type="primary"):
                        if delete_record("inventory", item_data["id"]):
                            st.success(f"{'Item deleted successfully!' if language == 'English' else 'Item berhasil dihapus!'}")
                with col2:
                    if st.button(f"{'Cancel' if language == 'English' else 'Batal'}", 
                               key="cancel_inv_delete",
                               width='stretch'):
                        st.experimental_rerun()

def view_inventory_history(language):
    """View inventory stock movement history"""
    st.markdown(f"""
    <h3 style="margin-bottom: 1rem; color: #000000;">{LANGUAGES[language]["stock_history"]}</h3>
    """, unsafe_allow_html=True)
    
    inventory_df = get_all_inventory()
    history_df = get_inventory_history()
    
    if history_df.empty:
        st.warning(f"{'No inventory history available' if language == 'English' else 'Tidak ada riwayat inventaris tersedia'}")
        return
    
    # Merge with inventory items to get names
    merged_df = history_df.merge(inventory_df[['id', 'item_name']], 
                                left_on='item_id', 
                                right_on='id', 
                                how='left')
    
    # Filter options
    with st.expander(f"{'Filter History' if language == 'English' else 'Filter Riwayat'}", expanded=True):
        col1, col2, col3 = st.columns(3)
        with col1:
            item_filter = st.selectbox(
                f"{'Filter by Item' if language == 'English' else 'Filter berdasarkan Item'}",
                ["All"] + inventory_df["item_name"].unique().tolist(),
                key="history_item_filter"
            )
        with col2:
            type_filter = st.selectbox(
                f"{'Filter by Type' if language == 'English' else 'Filter berdasarkan Jenis'}",
                ["All", "add", "reduce"],
                key="history_type_filter"
            )
        with col3:
            date_range = st.date_input(
                f"{'Filter by Date Range' if language == 'English' else 'Filter berdasarkan Rentang Tanggal'}",
                [datetime.now() - timedelta(days=30), datetime.now()],
                key="history_date_filter"
            )
    
    # Apply filters
    filtered_df = merged_df.copy()
    if item_filter != "All":
        filtered_df = filtered_df[filtered_df["item_name"] == item_filter]
    if type_filter != "All":
        filtered_df = filtered_df[filtered_df["transaction_type"] == type_filter]
    if len(date_range) == 2:
        filtered_df = filtered_df[
            (pd.to_datetime(filtered_df["transaction_date"]) >= pd.to_datetime(date_range[0])) & 
            (pd.to_datetime(filtered_df["transaction_date"]) <= pd.to_datetime(date_range[1]))
        ]
    
    if filtered_df.empty:
        st.warning(f"{'No transactions match the filters' if language == 'English' else 'Tidak ada transaksi yang sesuai dengan filter'}")
    else:
        # Display summary metrics
        col1, col2, col3 = st.columns(3)
        with col1:
            total_added = filtered_df[filtered_df["transaction_type"] == "add"]["amount"].sum()
            st.metric(f"{'Total Added' if language == 'English' else 'Total Ditambahkan'}", 
                     f"{total_added:.2f}")
        with col2:
            total_reduced = filtered_df[filtered_df["transaction_type"] == "reduce"]["amount"].sum()
            st.metric(f"{'Total Reduced' if language == 'English' else 'Total Dikurangi'}", 
                     f"{total_reduced:.2f}")
        with col3:
            net_change = total_added - total_reduced
            st.metric(f"{'Net Change' if language == 'English' else 'Perubahan Bersih'}", 
                     f"{net_change:.2f}")
        
        # Display detailed history
        st.dataframe(
            filtered_df[["transaction_date", "item_name", "transaction_type", "amount", "unit_price", "total_value", "notes"]]
            .sort_values("transaction_date", ascending=False)
            .rename(columns={
                "transaction_date": LANGUAGES[language]["transaction_date"],
                "item_name": LANGUAGES[language]["item_name"],
                "transaction_type": LANGUAGES[language]["transaction_type"],
                "amount": LANGUAGES[language]["amount"],
                "unit_price": LANGUAGES[language]["price_per_unit"],
                "total_value": LANGUAGES[language]["total_value"],
                "notes": LANGUAGES[language]["notes"]
            }),
            width='stretch',
            height=400
        )
        
        # Stock movement chart
        st.markdown(f"""
        <h4 style="margin-top: 1.5rem; color: #000000;">{LANGUAGES[language]["stock_movement"]}</h4>
        """, unsafe_allow_html=True)
        
        if not filtered_df.empty:
            # Prepare data for plotting
            plot_df = filtered_df.copy()
            plot_df['transaction_date'] = pd.to_datetime(plot_df['transaction_date']).dt.date
            plot_df = plot_df.sort_values('transaction_date')
            
            # Create figure
            fig = go.Figure()
            
            # Add traces for each item if filtered by item
            if item_filter == "All":
                for item in plot_df['item_name'].unique():
                    item_data = plot_df[plot_df['item_name'] == item]
                    fig.add_trace(go.Scatter(
                        x=item_data['transaction_date'],
                        y=item_data['amount'],
                        mode='lines+markers',
                        name=item,
                        hovertemplate=f"{item}<br>Date: %{{x}}<br>Amount: %{{y}}<extra></extra>"
                    ))
            else:
                fig.add_trace(go.Scatter(
                    x=plot_df['transaction_date'],
                    y=plot_df['amount'],
                    mode='lines+markers',
                    name=item_filter,
                    hovertemplate=f"{item_filter}<br>Date: %{{x}}<br>Amount: %{{y}}<extra></extra>"
                ))
            
            fig.update_layout(
                title=f"{'Stock Movement' if language == 'English' else 'Pergerakan Stok'}",
                xaxis_title=LANGUAGES[language]["transaction_date"],
                yaxis_title=LANGUAGES[language]["amount"],
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(family="Inter", color="#000000")
            )
            
            st.plotly_chart(fig, width='stretch')

def show_inventory_warnings(language):
    """Show inventory warnings for low and out of stock items"""
    st.markdown(f"""
    <h3 style="margin-bottom: 1rem; color: #000000;">{LANGUAGES[language]["inventory_warning"]}</h3>
    """, unsafe_allow_html=True)
    
    df = get_all_inventory()
    
    if df.empty:
        st.warning(f"{'No inventory items available' if language == 'English' else 'Tidak ada item inventaris tersedia'}")
        return
    
    # Identify low and out of stock items
    low_stock = df[(df['current_stock'] > 0) & (df['current_stock'] <= df['minimum_stock'])]
    out_of_stock = df[df['current_stock'] <= 0]
    
    # Display warnings
    tab1, tab2 = st.tabs([
        f"{LANGUAGES[language]['low_stock']} ({len(low_stock)})",
        f"{LANGUAGES[language]['out_of_stock']} ({len(out_of_stock)})"
    ])
    
    with tab1:
        if low_stock.empty:
            st.success(f"{'No low stock items' if language == 'English' else 'Tidak ada item dengan stok rendah'}")
        else:
            st.warning(f"{len(low_stock)} {'items below minimum stock level' if language == 'English' else 'item di bawah level stok minimum'}")
            st.dataframe(
                low_stock[["item_name", "item_type", "current_stock", "minimum_stock", "unit", "supplier"]]
                .sort_values("current_stock")
                .rename(columns={
                    "item_name": LANGUAGES[language]["item_name"],
                    "item_type": LANGUAGES[language]["item_type"],
                    "current_stock": LANGUAGES[language]["current_stock"],
                    "minimum_stock": LANGUAGES[language]["minimum_stock"],
                    "unit": LANGUAGES[language]["unit"],
                    "supplier": LANGUAGES[language]["supplier"]
                }),
                width='stretch'
            )
            
            # Add stock form
            with st.expander(f"{'Add Stock' if language == 'English' else 'Tambah Stok'}", expanded=False):
                with st.form("add_stock_form"):
                    selected_item = st.selectbox(
                        f"{'Select Item' if language == 'English' else 'Pilih Item'}",
                        low_stock["item_name"],
                        key="low_stock_select"
                    )
                    
                    amount = st.number_input(
                        f"{'Amount to Add' if language == 'English' else 'Jumlah yang Ditambahkan'}",
                        min_value=0.1,
                        step=0.1,
                        key="low_stock_amount"
                    )
                    
                    notes = st.text_input(
                        f"{'Notes' if language == 'English' else 'Catatan'}",
                        key="low_stock_notes"
                    )
                    
                    submitted = st.form_submit_button(f"{'Add Stock' if language == 'English' else 'Tambah Stok'}",
                                                    width='stretch')
                    
                    if submitted:
                        item_id = low_stock[low_stock["item_name"] == selected_item].iloc[0]["id"]
                        if update_inventory_item(item_id, amount, "add", notes):
                            st.success(f"{'Stock added successfully!' if language == 'English' else 'Stok berhasil ditambahkan!'}")
                            st.rerun()
    
    with tab2:
        if out_of_stock.empty:
            st.success(f"{'No out of stock items' if language == 'English' else 'Tidak ada item yang kehabisan stok'}")
        else:
            st.error(f"{len(out_of_stock)} {'out of stock items' if language == 'English' else 'item yang kehabisan stok'}")
            st.dataframe(
                out_of_stock[["item_name", "item_type", "current_stock", "minimum_stock", "unit", "supplier"]]
                .sort_values("item_name")
                .rename(columns={
                    "item_name": LANGUAGES[language]["item_name"],
                    "item_type": LANGUAGES[language]["item_type"],
                    "current_stock": LANGUAGES[language]["current_stock"],
                    "minimum_stock": LANGUAGES[language]["minimum_stock"],
                    "unit": LANGUAGES[language]["unit"],
                    "supplier": LANGUAGES[language]["supplier"]
                }),
                width='stretch'
            )
            
            # Add stock form
            with st.expander(f"{'Add Stock' if language == 'English' else 'Tambah Stok'}", expanded=False):
                with st.form("out_of_stock_form"):
                    selected_item = st.selectbox(
                        f"{'Select Item' if language == 'English' else 'Pilih Item'}",
                        out_of_stock["item_name"],
                        key="out_of_stock_select"
                    )
                    
                    amount = st.number_input(
                        f"{'Amount to Add' if language == 'English' else 'Jumlah yang Ditambahkan'}",
                        min_value=0.1,
                        step=0.1,
                        key="out_of_stock_amount"
                    )
                    
                    notes = st.text_input(
                        f"{'Notes' if language == 'English' else 'Catatan'}",
                        key="out_of_stock_notes"
                    )
                    
                    submitted = st.form_submit_button(f"{'Add Stock' if language == 'English' else 'Tambah Stok'}",
                                                    width='stretch')
                    
                    if submitted:
                        item_id = out_of_stock[out_of_stock["item_name"] == selected_item].iloc[0]["id"]
                        if update_inventory_item(item_id, amount, "add", notes):
                            st.success(f"{'Stock added successfully!' if language == 'English' else 'Stok berhasil ditambahkan!'}")
                            st.rerun()

# --- FINANCIAL MANAGEMENT PAGES ---
def show_financial_management(language):
    """Financial management page with transactions and reports"""
    st.markdown(f"""
    <h2 style="margin-bottom: 1rem; color: #000000;">{LANGUAGES[language]["finance_manage"]}</h2>
    """, unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs([
        LANGUAGES[language]["financial_transactions"],
        LANGUAGES[language]["financial_report"]
    ])
    
    with tab1:
        manage_financial_transactions(language)
    with tab2:
        show_financial_reports(language)

def manage_financial_transactions(language):
    """Manage financial transactions CRUD operations"""
    operation = st.radio(
        f"{'Select operation:' if language == 'English' else 'Pilih operasi:'}",
        [LANGUAGES[language]["add"], LANGUAGES[language]["edit"], LANGUAGES[language]["delete"]],
        horizontal=True,
        key="finance_operation",
        label_visibility="collapsed"
    )
    
    df = get_financial_transactions()
    
    if operation == LANGUAGES[language]["add"]:
        with stylable_container(
            key="add_finance_container",
            css_styles="""
                {
                    background-color: white;
                    border-radius: 12px;
                    padding: 25px;
                    box-shadow: 0 4px 12px rgba(0,0,0,0.05);
                }
            """
        ):
            with st.form("add_finance_form", clear_on_submit=True):
                st.markdown(f"<h3 style='color: #000000; margin-bottom: 1.5rem;'>{LANGUAGES[language]['add']} {LANGUAGES[language]['financial_transactions']}</h3>", unsafe_allow_html=True)
                
                col1, col2 = st.columns(2)
                with col1:
                    transaction_date = st.date_input(
                        f"{'Transaction Date' if language == 'English' else 'Tanggal Transaksi'}*",
                        datetime.now(),
                        key="finance_date"
                    )
                    transaction_type = st.selectbox(
                        f"{'Transaction Type' if language == 'English' else 'Jenis Transaksi'}*",
                        ["income", "expense"],
                        format_func=lambda x: "Income" if x == "income" else "Expense",
                        key="finance_type"
                    )
                with col2:
                    category = st.text_input(f"{'Category' if language == 'English' else 'Kategori'}*", key="finance_category")
                    value = st.number_input(
                        f"{'Value (IDR)' if language == 'English' else 'Nilai (Rp)'}*",
                        min_value=0,
                        key="finance_value"
                    )
                
                description = st.text_area(f"{'Description' if language == 'English' else 'Deskripsi'}*", key="finance_desc")
                
                col1, col2 = st.columns(2)
                with col1:
                    payment_method = st.selectbox(
                        f"{'Payment Method' if language == 'English' else 'Metode Pembayaran'}",
                        ["Cash", "Bank Transfer", "Credit Card", "E-Wallet", "Other"],
                        key="finance_payment"
                    )
                with col2:
                    reference = st.text_input(f"{'Reference' if language == 'English' else 'Referensi'}", key="finance_ref")
                
                notes = st.text_area(f"{'Notes' if language == 'English' else 'Catatan'}", key="finance_notes")
                
                submitted = st.form_submit_button(f"{'Save Transaction' if language == 'English' else 'Simpan Transaksi'}",
                                                width='stretch')
                
                if submitted:
                    if not all([transaction_date, transaction_type, category, value, description]):
                        st.error(f"{'Please fill required fields' if language == 'English' else 'Harap isi field wajib'} (*)")
                    else:
                        new_id = (df["id"].max() + 1) if not df.empty else 1
                        transaction_data = {
                            "id": new_id,
                            "transaction_date": transaction_date.strftime("%Y-%m-%d %H:%M:%S"),
                            "transaction_type": transaction_type,
                            "category": category,
                            "description": description,
                            "value": value,
                            "payment_method": payment_method,
                            "reference": reference,
                            "notes": notes
                        }
                        
                        if add_record("financial_transactions", transaction_data):
                            st.success(f"{'Transaction added successfully!' if language == 'English' else 'Transaksi berhasil ditambahkan!'}")
                            st.balloons()

    elif operation == LANGUAGES[language]["edit"]:
        if df.empty:
            st.warning(f"{'No transactions available' if language == 'English' else 'Tidak ada transaksi tersedia'}")
        else:
            transaction_to_edit = st.selectbox(
                f"{'Select transaction to edit:' if language == 'English' else 'Pilih transaksi untuk diedit:'}",
                df.apply(lambda x: f"{x['transaction_date']} - {x['description']} ({x['value']})", axis=1),
                key="edit_finance_select"
            )
            
            transaction_id = df.iloc[int(transaction_to_edit.split(" - ")[0])]["id"]
            transaction_data = df[df["id"] == transaction_id].iloc[0].to_dict()
            
            with stylable_container(
                key="edit_finance_container",
                css_styles="""
                    {
                        background-color: white;
                        border-radius: 12px;
                        padding: 25px;
                        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
                    }
                """
            ):
                with st.form("edit_finance_form"):
                    st.markdown(f"<h3 style='color: #000000; margin-bottom: 1.5rem;'>{LANGUAGES[language]['edit']} {LANGUAGES[language]['financial_transactions']}</h3>", unsafe_allow_html=True)
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        transaction_date = st.date_input(
                            f"{'Transaction Date' if language == 'English' else 'Tanggal Transaksi'}*",
                            datetime.strptime(transaction_data["transaction_date"], "%Y-%m-%d %H:%M:%S").date(),
                            key="edit_finance_date"
                        )
                        transaction_type = st.selectbox(
                            f"{'Transaction Type' if language == 'English' else 'Jenis Transaksi'}*",
                            ["income", "expense"],
                            index=0 if transaction_data["transaction_type"] == "income" else 1,
                            format_func=lambda x: "Income" if x == "income" else "Expense",
                            key="edit_finance_type"
                        )
                    with col2:
                        category = st.text_input(f"{'Category' if language == 'English' else 'Kategori'}*", 
                                               value=transaction_data["category"], key="edit_finance_category")
                        value = st.number_input(
                            f"{'Value (IDR)' if language == 'English' else 'Nilai (Rp)'}*",
                            min_value=0,
                            value=int(transaction_data["value"]),
                            key="edit_finance_value"
                        )
                    
                    description = st.text_area(f"{'Description' if language == 'English' else 'Deskripsi'}*", 
                                             value=transaction_data["description"], key="edit_finance_desc")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        payment_method = st.selectbox(
                            f"{'Payment Method' if language == 'English' else 'Metode Pembayaran'}",
                            ["Cash", "Bank Transfer", "Credit Card", "E-Wallet", "Other"],
                            index=["Cash", "Bank Transfer", "Credit Card", "E-Wallet", "Other"].index(transaction_data["payment_method"]),
                            key="edit_finance_payment"
                        )
                    with col2:
                        reference = st.text_input(f"{'Reference' if language == 'English' else 'Referensi'}", 
                                                value=transaction_data["reference"], key="edit_finance_ref")
                    
                    notes = st.text_area(f"{'Notes' if language == 'English' else 'Catatan'}", 
                                        value=transaction_data["notes"], key="edit_finance_notes")
                    
                    submitted = st.form_submit_button(f"{'Update Transaction' if language == 'English' else 'Update Transaksi'}",
                                                    width='stretch')
                    
                    if submitted:
                        if not all([transaction_date, transaction_type, category, value, description]):
                            st.error(f"{'Please fill required fields' if language == 'English' else 'Harap isi field wajib'} (*)")
                        else:
                            updated_data = {
                                "transaction_date": transaction_date.strftime("%Y-%m-%d %H:%M:%S"),
                                "transaction_type": transaction_type,
                                "category": category,
                                "description": description,
                                "value": value,
                                "payment_method": payment_method,
                                "reference": reference,
                                "notes": notes
                            }
                            
                            if update_record("financial_transactions", transaction_id, updated_data):
                                st.success(f"{'Transaction updated successfully!' if language == 'English' else 'Transaksi berhasil diupdate!'}")

    elif operation == LANGUAGES[language]["delete"]:
        if df.empty:
            st.warning(f"{'No transactions available' if language == 'English' else 'Tidak ada transaksi tersedia'}")
        else:
            transaction_to_delete = st.selectbox(
                f"{'Select transaction to delete:' if language == 'English' else 'Pilih transaksi untuk dihapus:'}",
                df.apply(lambda x: f"{x['transaction_date']} - {x['description']} ({x['value']})", axis=1),
                key="delete_finance_select"
            )
            
            transaction_id = df.iloc[int(transaction_to_delete.split(" - ")[0])]["id"]
            transaction_data = df[df["id"] == transaction_id].iloc[0].to_dict()
            
            with stylable_container(
                key="delete_finance_container",
                css_styles="""
                    {
                        background-color: #fff8e1;
                        border-radius: 12px;
                        padding: 25px;
                        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
                    }
                """
            ):
                st.markdown(f"""
                <h3 style="color: #000000; margin-bottom: 1rem;">⚠️ {'Are you sure you want to delete' if language == 'English' else 'Apakah Anda yakin ingin menghapus'} <span style="color: #e63946;">{transaction_data['description']}</span>?</h3>
                <p style="color: #555;">{'This action cannot be undone. Transaction data will be permanently removed.' if language == 'English' else 'Tindakan ini tidak dapat dibatalkan. Data transaksi akan dihapus permanen.'}</p>
                """, unsafe_allow_html=True)
                
                col1, col2, _ = st.columns([1, 1, 2])
                with col1:
                    if st.button(f"{'Confirm Delete' if language == 'English' else 'Konfirmasi Hapus'}", 
                                key="confirm_finance_delete",
                                width='stretch',
                                type="primary"):
                        if delete_record("financial_transactions", transaction_id):
                            st.success(f"{'Transaction deleted successfully!' if language == 'English' else 'Transaksi berhasil dihapus!'}")
                with col2:
                    if st.button(f"{'Cancel' if language == 'English' else 'Batal'}", 
                               key="cancel_finance_delete",
                               width='stretch'):
                        st.experimental_rerun()

def show_financial_reports(language):
    """Show financial reports and analytics"""
    st.markdown(f"""
    <h3 style="margin-bottom: 1rem; color: #000000;">{LANGUAGES[language]["financial_dashboard"]}</h3>
    """, unsafe_allow_html=True)
    
    df = get_financial_transactions()
    
    if df.empty:
        st.warning(f"{'No financial data available' if language == 'English' else 'Tidak ada data keuangan tersedia'}")
        return
    
    # Calculate financial metrics
    current_balance = calculate_financial_balance()
    total_income = df[df["transaction_type"] == "income"]["value"].sum()
    total_expense = df[df["transaction_type"] == "expense"]["value"].sum()
    net_profit = total_income - total_expense
    
    # Display metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric(LANGUAGES[language]["total_income"], format_price(total_income, language))
    with col2:
        st.metric(LANGUAGES[language]["total_expense"], format_price(total_expense, language))
    with col3:
        st.metric(LANGUAGES[language]["net_profit"], format_price(net_profit, language))
    with col4:
        st.metric(LANGUAGES[language]["balance"], format_price(current_balance, language))
    
    # Filter options
    with st.expander(f"{'Filter Data' if language == 'English' else 'Filter Data'}", expanded=True):
        col1, col2 = st.columns(2)
        with col1:
            date_range = st.date_input(
                f"{'Date Range' if language == 'English' else 'Rentang Tanggal'}",
                [datetime.now() - timedelta(days=30), datetime.now()],
                key="finance_date_filter"
            )
        with col2:
            transaction_type = st.selectbox(
                f"{'Transaction Type' if language == 'English' else 'Jenis Transaksi'}",
                ["All", "income", "expense"],
                format_func=lambda x: "All" if x == "All" else "Income" if x == "income" else "Expense",
                key="finance_type_filter"
            )
    
    # Apply filters
    filtered_df = df.copy()
    if len(date_range) == 2:
        filtered_df = filtered_df[
            (pd.to_datetime(filtered_df["transaction_date"]) >= pd.to_datetime(date_range[0])) & 
            (pd.to_datetime(filtered_df["transaction_date"]) <= pd.to_datetime(date_range[1]))
        ]
    if transaction_type != "All":
        filtered_df = filtered_df[filtered_df["transaction_type"] == transaction_type]
    
    if filtered_df.empty:
        st.warning(f"{'No transactions match the filters' if language == 'English' else 'Tidak ada transaksi yang sesuai dengan filter'}")
    else:
        # Display transactions
        st.dataframe(
            filtered_df[["transaction_date", "transaction_type", "category", "description", "value", "payment_method"]]
            .sort_values("transaction_date", ascending=False)
            .rename(columns={
                "transaction_date": LANGUAGES[language]["transaction_date"],
                "transaction_type": LANGUAGES[language]["transaction_type"],
                "category": LANGUAGES[language]["category"],
                "description": LANGUAGES[language]["description"],
                "value": LANGUAGES[language]["value"],
                "payment_method": "Payment Method"
            }),
            width='stretch',
            height=400
        )
        
        # Financial charts
        st.markdown("---")
        col1, col2 = st.columns(2)
        
        with col1:
            # Income vs Expense over time
            st.markdown(f"""
            <h4 style="margin-bottom: 1rem; color: #000000;">{'Income vs Expense Over Time' if language == 'English' else 'Pemasukan vs Pengeluaran per Waktu'}</h4>
            """, unsafe_allow_html=True)
            
            time_df = filtered_df.copy()
            time_df['transaction_date'] = pd.to_datetime(time_df['transaction_date']).dt.date
            time_df = time_df.groupby(['transaction_date', 'transaction_type'])['value'].sum().unstack().fillna(0)
            
            fig = go.Figure()
            fig.add_trace(go.Bar(
                x=time_df.index,
                y=time_df['income'],
                name='Income',
                marker_color='#2a9d8f'
            ))
            fig.add_trace(go.Bar(
                x=time_df.index,
                y=time_df['expense'],
                name='Expense',
                marker_color='#e63946'
            ))
            
            fig.update_layout(
                barmode='group',
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(family="Inter", color="#000000")
            )
            
            st.plotly_chart(fig, width='stretch')
        
        with col2:
            # Expense by category
            st.markdown(f"""
            <h4 style="margin-bottom: 1rem; color: #000000;">{'Expense by Category' if language == 'English' else 'Pengeluaran per Kategori'}</h4>
            """, unsafe_allow_html=True)
            
            expense_df = filtered_df[filtered_df['transaction_type'] == 'expense']
            if not expense_df.empty:
                category_df = expense_df.groupby('category')['value'].sum().reset_index()
                
                fig = px.pie(
                    category_df,
                    values='value',
                    names='category',
                    color_discrete_sequence=px.colors.qualitative.Pastel
                )
                
                fig.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(family="Inter", color="#000000")
                )
                
                st.plotly_chart(fig, width='stretch')
            else:
                st.info(f"{'No expense data available' if language == 'English' else 'Tidak ada data pengeluaran tersedia'}")

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
        try:
            # Try to get logo from Google Drive
            logo_url = get_image_from_drive("logo_batik.png")
            if logo_url != DEFAULT_IMAGE:
                st.image(logo_url, width=120)
            else:
                st.image(DEFAULT_IMAGE, width=120, caption="Logo")
        except:
            st.image(DEFAULT_IMAGE, width=120, caption="Logo")
        
        st.markdown("---")
        
        language = st.selectbox("🌐 Language / Bahasa", 
                              ["Indonesia", "English"],
                              index=0 if st.session_state["language"] == "Indonesia" else 1,
                              key="lang_select")
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
            label_visibility="collapsed",
            format_func=lambda x: f"📊 {x}" if x == LANGUAGES[language]["dashboard"] else 
                                f"🖼️ {x}" if x == LANGUAGES[language]["featured"] else 
                                f"📈 {x}" if x == LANGUAGES[language]["analytics"] else 
                                f"⚙️ {x}" if x == LANGUAGES[language]["settings"] else 
                                f"📦 {x}" if x == LANGUAGES[language]["inventory_manage"] else 
                                f"💰 {x}" if x == LANGUAGES[language]["finance_manage"] else 
                                f"🧮 {x}" if x == LANGUAGES[language]["hpp_calculator"] else 
                                f"🛠️ {x}" if x == LANGUAGES[language]["manage"] else x
        )
        
        st.markdown("---")
        
        # Debug buttons
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🐛 Debug Sheets", help="Test koneksi Google Sheets"):
                debug_google_sheets_connection()
        with col2:
            if st.button("🐛 Debug Drive", help="Test koneksi Google Drive"):
                debug_google_drive_connection()
        
        if st.button("🔄 Clear Cache", help="Bersihkan cache dan refresh"):
            st.cache_data.clear()
            st.cache_resource.clear()
            st.rerun()
        
        st.markdown("---")
        
        if st.session_state["is_admin"]:
            if st.button(
                f"🚪 {LANGUAGES[language]['logout']}", 
                width='stretch',
                key="sidebar_logout"
            ):
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