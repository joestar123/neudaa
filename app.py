import streamlit as st
import urllib.request
import random
from datetime import datetime, timedelta
from email.utils import parsedate_to_datetime

# --- IMPORT THƯ VIỆN ÂM LỊCH ---
try:
    from lunardate import LunarDate
    HAS_LUNAR_LIB = True
except ImportError:
    HAS_LUNAR_LIB = False

# --- CẤU HÌNH TRANG ---
st.set_page_config(
    page_title="18h30 Team - Phong Thủy",
    page_icon="🔮",
    layout="centered"
)

# --- CSS FIX LỖI DARK MODE & UI MOBILE ---
st.markdown("""
<style>
    /* 1. Container bao quanh các thẻ kết quả */
    .result-container {
        display: flex;
        flex-wrap: wrap; /* Cho phép xuống dòng nếu hết chỗ */
        justify-content: center; /* Căn giữa */
        gap: 10px; /* Khoảng cách giữa các thẻ */
    }

    /* 2. Class cho thẻ kết quả (Card) */
    .lucky-card {
        background-color: #f0f8ff;
        padding: 10px; /* Giảm padding cho gọn */
        border-radius: 10px;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        color: #000000 !important;
        
        /* QUAN TRỌNG: Responsive */
        flex: 1 0 40%; /* Mobile: Mỗi thẻ chiếm khoảng 40-45% -> 2 thẻ/hàng */
        min-width: 120px; /* Đảm bảo không bị bé quá */
        max-width: 180px; /* Trên PC cũng không bị to quá */
    }

    /* Ép màu chữ bên trong */
    .lucky-card div, .lucky-card p, .lucky-card span {
        color: #000000 !important;
    }

    /* 3. Style cho số to - Giảm size một chút cho mobile */
    .big-number {
        font-size: 32px !important; /* Giảm từ 36 xuống 32 */
        font-weight: 900 !important;
        margin-bottom: 2px;
        line-height: 1.2;
    }

    /* Style phụ */
    .card-element { font-size: 14px; font-weight: bold; color: #424242 !important; }
    .card-note { font-size: 12px; margin-top: 2px; font-weight: bold; }

    /* 4. Style cho box thông tin Mệnh ở trên */
    .result-header-box {
        border: 2px solid #1565C0;
        padding: 10px;
        border-radius: 10px;
        text-align: center;
        background-color: #E3F2FD;
        color: #0d47a1 !important;
        margin-top: 10px;
        margin-bottom: 15px;
    }
    
    /* 5. Style cho Intro text */
    .intro-text {
        font-family: "Times New Roman";
        font-size: 16px;
        font-style: italic;
        text-align: justify;
        background-color: #eceff1;
        color: #37474f !important;
        padding: 10px;
        border-radius: 5px;
        border-left: 5px solid #607d8b;
    }

    /* 6. Style cho Summary box */
    .summary-box {
        margin-top: 20px;
        padding: 15px;
        background-color: #FFF3E0;
        border: 1px dashed #FF9800;
        border-radius: 5px;
        color: #333 !important;
    }
    .summary-box b, .summary-box div { color: #000000 !important; }

    .footer { text-align: center; margin-top: 30px; font-size: 12px; color: #888; font-style: italic; }
</style>
""", unsafe_allow_html=True)

# --- HÀM LOGIC (GIỮ NGUYÊN) ---
def get_lunar_year_number(date_obj):
    if HAS_LUNAR_LIB:
        lunar = LunarDate.fromSolarDate(date_obj.year, date_obj.month, date_obj.day)
        return lunar.year
    else:
        return date_obj.year

def calculate_menh_nien(year):
    can_values = {4:1, 5:1, 6:2, 7:2, 8:3, 9:3, 0:4, 1:4, 2:5, 3:5}
    can_val = can_values[year % 10]
    chi_mod = year % 12
    if chi_mod in [4, 5, 10, 11]: chi_val = 0
    elif chi_mod in [6, 7, 0, 1]: chi_val = 1
    else: chi_val = 2
    total = can_val + chi_val
    if total > 5: total -= 5
    menh_map = {1: "Kim", 2: "Thủy", 3: "Hỏa", 4: "Thổ", 5: "Mộc"}
    return menh_map[total]

def get_number_element(number_str):
    last_digit = int(number_str[-1])
    if last_digit in [1, 6]: return "Thủy"
    if last_digit in [2, 7]: return "Hỏa"
    if last_digit in [3, 8]: return "Mộc"
    if last_digit in [4, 9]: return "Kim"
    return "Thổ"

def check_compatibility(user_menh, num_menh):
    tuong_sinh = {"Kim": "Thủy", "Thủy": "Mộc", "Mộc": "Hỏa", "Hỏa": "Thổ", "Thổ": "Kim"}
    if user_menh == num_menh: return True, "Bình Hòa"
    if tuong_sinh.get(num_menh) == user_menh: return True, "Tương Sinh"
    return False, "Không Hợp"

def get_google_time_hanoi():
    try:
        req = urllib.request.Request("https://www.google.com", method='HEAD')
        with urllib.request.urlopen(req, timeout=5) as response:
            date_str = response.headers['Date']
            utc_time = parsedate_to_datetime(date_str)
            return (utc_time + timedelta(hours=7)).replace(tzinfo=None), True
    except:
        return datetime.now(), False

# --- UI CHÍNH ---

st.title("18h30 Team")
st.subheader("DỰ ĐOÁN SỐ MAY MẮN")

st.markdown("""
<div class="intro-text">
    Ngẫu nhiên không được tạo ra. Nó được khai sinh.<br>
    Sử dụng Entropy & Ngũ Hành để tìm con số hòa hợp vận mệnh.
</div>
""", unsafe_allow_html=True)

if not HAS_LUNAR_LIB:
    st.warning("⚠️ Chưa cài 'lunardate'. Chạy: pip install lunardate")

st.divider()

with st.form("main_form"):
    st.markdown("**1. Ngày sinh (Tính Mệnh)**")
    dob = st.date_input("Chọn ngày sinh", min_value=datetime(1900, 1, 1), value=datetime(2000, 1, 1))

    st.markdown("**2. Ngày dự đoán**")
    target_date = st.date_input("Chọn ngày", value=datetime.now())

    st.markdown("**3. Số bạn đang nghĩ (Tối đa 5)**")
    cols = st.columns(5)
    fav_inputs = []
    for i, col in enumerate(cols):
        with col:
            val = st.text_input(f"Số {i+1}", max_chars=2, placeholder="--")
            fav_inputs.append(val)

    submitted = st.form_submit_button("PHÂN TÍCH & LUẬN GIẢI", use_container_width=True, type="primary")

if submitted:
    valid_favs = []
    errors = []
    for i, f in enumerate(fav_inputs, 1):
        f = f.strip()
        if f:
            if not f.isdigit() or len(f) != 2: errors.append(f"Số thứ {i} ('{f}') không hợp lệ.")
            else: valid_favs.append(f)
    
    if errors:
        for e in errors: st.error(e)
    else:
        with st.spinner("Đang tính toán..."):
            now_dt, is_online = get_google_time_hanoi()
            lunar_year = get_lunar_year_number(dob)
            user_menh = calculate_menh_nien(lunar_year)
            
            dob_str = dob.strftime("%d%m%Y")
            target_str = target_date.strftime("%d%m%Y")
            seed_val = f"{dob_str}{target_str}{now_dt.strftime('%d%m%Y%H%M%S')}{''.join(valid_favs)}"
            random.seed(seed_val)
            kq = [f"{random.randint(0,99):02d}" for _ in range(5)]
            
            # HEADER
            st.markdown(f"""
            <div class="result-header-box">
                <div style="font-size: 14px; font-weight: bold;">SINH NĂM {lunar_year} (ÂM) - MỆNH {user_menh.upper()}</div>
            </div>
            """, unsafe_allow_html=True)
            
            # --- PHẦN THAY ĐỔI LỚN NHẤT Ở ĐÂY ---
            # Thay vì st.columns, ta tạo 1 chuỗi HTML chứa tất cả thẻ
            html_cards = ""
            compatible_count = 0
            
            for idx, num in enumerate(kq):
                num_menh = get_number_element(num)
                is_hop, ly_do = check_compatibility(user_menh, num_menh)
                
                if is_hop:
                    compatible_count += 1
                    num_color = "#1b5e20"
                    border_css = "3px solid #2E7D32" # Giảm viền xuống 3px cho thanh thoát
                    note_color = "#2E7D32"
                else:
                    num_color = "#212121"
                    border_css = "1px solid #B0BEC5"
                    note_color = "#546E7A"
                
                # Cộng dồn HTML string
                html_cards += f"""
                <div class="lucky-card" style="border: {border_css};">
                    <div class="big-number" style="color: {num_color} !important;">{num}</div>
                    <div class="card-element">Hành: {num_menh}</div>
                    <div class="card-note" style="color: {note_color} !important;">{ly_do}</div>
                </div>
                """
            
            # Render toàn bộ thẻ trong 1 container flex
            st.markdown(f"""
            <div class="result-container">
                {html_cards}
            </div>
            """, unsafe_allow_html=True)
            # -------------------------------------
            
            # SUMMARY
            st.markdown(f"""
            <div class="summary-box">
                <b>🔮 TỔNG KẾT:</b> Có <b>{compatible_count}/5</b> số hợp mệnh.
            </div>
            """, unsafe_allow_html=True)
            
            source = "Google" if is_online else "Offline"
            st.caption(f"Time: {now_dt.strftime('%H:%M:%S')} ({source})")

st.markdown('<div class="footer">Created by MinhMup</div>', unsafe_allow_html=True)