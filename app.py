import streamlit as st
import urllib.request
import random
from datetime import datetime, timedelta
from email.utils import parsedate_to_datetime

# --- IMPORT THƯ VIỆN ÂM LỊCH (XỬ LÝ LỖI NẾU CHƯA CÀI) ---
try:
    from lunardate import LunarDate
    HAS_LUNAR_LIB = True
except ImportError:
    HAS_LUNAR_LIB = False

# --- CẤU HÌNH TRANG ---
st.set_page_config(
    page_title="NEU DAA Digital Team - Phong Thủy",
    page_icon="🔮",
    layout="centered"
)

# --- CSS TÙY CHỈNH ---
st.markdown("""
<style>
    .big-font {
        font-size:30px !important;
        font-weight: bold;
        color: #D32F2F;
        text-align: center;
        margin-bottom: 5px;
    }
    .result-box {
        border: 2px solid #1565C0;
        padding: 20px;
        border-radius: 10px;
        text-align: center;
        background-color: #f0f8ff;
        margin-top: 20px;
    }
    .intro-text {
        font-family: "Times New Roman";
        font-size: 18px;
        font-style: italic;
        text-align: justify;
        color: #455A64;
        background-color: #eceff1;
        padding: 15px;
        border-radius: 5px;
        border-left: 5px solid #607d8b;
    }
    .element-text {
        font-size: 14px;
        color: #555;
        font-weight: bold;
    }
    .menh-info {
        font-size: 18px; 
        color: #2E7D32; 
        font-weight: bold; 
        margin-bottom: 15px;
        text-transform: uppercase;
    }
    .summary-box {
        margin-top: 15px;
        padding: 10px;
        background-color: #FFF3E0;
        border-radius: 5px;
        border: 1px dashed #FF9800;
    }
</style>
""", unsafe_allow_html=True)

# --- HÀM LOGIC PHONG THỦY ---

def get_lunar_year_number(date_obj):
    """Chuyển đổi ngày dương sang năm âm lịch"""
    if HAS_LUNAR_LIB:
        lunar = LunarDate.fromSolarDate(date_obj.year, date_obj.month, date_obj.day)
        return lunar.year
    else:
        # Fallback nếu không có thư viện: Giả định năm dương = năm âm (sai số ở tháng 1, 2)
        return date_obj.year

def calculate_menh_nien(year):
    """
    Tính mệnh niên (Ngũ hành nạp âm) dựa trên Can Chi.
    Công thức: Can + Chi = Mệnh. (Nếu > 5 thì trừ 5)
    Quy ước:
    - Mệnh: 1=Kim, 2=Thủy, 3=Hỏa, 4=Thổ, 5=Mộc
    """
    # 1. Tính Can (Year % 10)
    # Canh=0, Tân=1, Nhâm=2, Quý=3, Giáp=4, Ất=5, Bính=6, Đinh=7, Mậu=8, Kỷ=9
    # Giá trị quy đổi Can: Giáp/Ất=1, Bính/Đinh=2, Mậu/Kỷ=3, Canh/Tân=4, Nhâm/Quý=5
    can_values = {4:1, 5:1, 6:2, 7:2, 8:3, 9:3, 0:4, 1:4, 2:5, 3:5}
    can_val = can_values[year % 10]
    
    # 2. Tính Chi (Year % 12)
    # Thân=0, Dậu=1, Tuất=2, Hợi=3, Tý=4, Sửu=5, Dần=6, Mão=7, Thìn=8, Tỵ=9, Ngọ=10, Mùi=11
    # Giá trị quy đổi Chi:
    # Tý, Sửu, Ngọ, Mùi (4,5,10,11) = 0
    # Dần, Mão, Thân, Dậu (6,7,0,1) = 1
    # Thìn, Tỵ, Tuất, Hợi (8,9,2,3) = 2
    chi_mod = year % 12
    if chi_mod in [4, 5, 10, 11]: chi_val = 0
    elif chi_mod in [6, 7, 0, 1]: chi_val = 1
    else: chi_val = 2
    
    # 3. Tính tổng
    total = can_val + chi_val
    if total > 5:
        total -= 5
        
    menh_map = {1: "Kim", 2: "Thủy", 3: "Hỏa", 4: "Thổ", 5: "Mộc"}
    return menh_map[total]

def get_number_element(number_str):
    """Lấy hành của con số dựa trên Hà Đồ (số cuối)"""
    last_digit = int(number_str[-1])
    if last_digit in [1, 6]: return "Thủy"
    if last_digit in [2, 7]: return "Hỏa"
    if last_digit in [3, 8]: return "Mộc"
    if last_digit in [4, 9]: return "Kim"
    return "Thổ" # 0, 5

def check_compatibility(user_menh, num_menh):
    """
    Kiểm tra tương sinh.
    Quy luật Tương sinh: Kim->Thủy->Mộc->Hỏa->Thổ->Kim
    Hợp = Tương Sinh (Số sinh Người) hoặc Bình Hòa (Cùng mệnh)
    """
    tuong_sinh = {
        "Kim": "Thủy", # Kim sinh Thủy
        "Thủy": "Mộc",
        "Mộc": "Hỏa",
        "Hỏa": "Thổ",
        "Thổ": "Kim"
    }
    
    # Trường hợp 1: Bình hòa (Cùng mệnh) - Tốt
    if user_menh == num_menh:
        return True, "Bình Hòa"
    
    # Trường hợp 2: Tương sinh (Số sinh cho Người - Rất tốt)
    # Tức là: num_menh là mẹ của user_menh
    if tuong_sinh.get(num_menh) == user_menh:
        return True, "Tương Sinh"
        
    return False, "Không Hợp"

# --- HÀM LẤY GIỜ GOOGLE ---
def get_google_time_hanoi():
    try:
        req = urllib.request.Request("https://www.google.com", method='HEAD')
        with urllib.request.urlopen(req, timeout=5) as response:
            date_str = response.headers['Date']
            utc_time = parsedate_to_datetime(date_str)
            hanoi_time = utc_time + timedelta(hours=7)
            return hanoi_time.replace(tzinfo=None), True
    except Exception as e:
        return datetime.now(), False

# --- GIAO DIỆN CHÍNH ---

st.title("NEU DAA Digital Team")
st.subheader("DỰ ĐOÁN SỐ MAY MẮN & PHONG THỦY")

st.markdown("""
<div class="intro-text">
    Ngẫu nhiên không được tạo ra. Nó được khai sinh.<br>
    Sử dụng Entropy thời gian thực kết hợp với <b>Ngũ Hành Bát Quái</b> để tìm ra con số không chỉ ngẫu nhiên mà còn hòa hợp với vận mệnh của bạn.
</div>
""", unsafe_allow_html=True)

if not HAS_LUNAR_LIB:
    st.warning("⚠️ Chưa cài đặt thư viện 'lunardate'. Hệ thống sẽ tính Mệnh dựa trên năm Dương lịch (có thể sai lệch nếu sinh vào tháng 1, 2 âm lịch). Vui lòng cài đặt: `pip install lunardate`")

st.divider()

with st.form("main_form"):
    st.markdown("**1. Ngày sinh (Để tính Mệnh)**")
    dob = st.date_input("Chọn ngày sinh của bạn", min_value=datetime(1900, 1, 1), value=datetime(2000, 1, 1))

    st.markdown("**2. Bạn chọn số cho ngày nào?**")
    target_date = st.date_input("Chọn ngày muốn dự đoán", value=datetime.now())

    st.markdown("**3. Những con số bạn đang nghĩ tới (Tối đa 5 số)**")
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
            if not f.isdigit() or len(f) != 2:
                errors.append(f"Số thứ {i} ('{f}') không hợp lệ (Phải là 2 chữ số).")
            else:
                valid_favs.append(f)
    
    if errors:
        for e in errors:
            st.error(e)
    else:
        with st.spinner("Đang kết nối Google Server & Tính toán Ngũ hành..."):
            now_dt, is_online = get_google_time_hanoi()
            
            # --- TÍNH TOÁN PHONG THỦY ---
            lunar_year = get_lunar_year_number(dob)
            user_menh = calculate_menh_nien(lunar_year)
            
            # --- TẠO SEED ---
            dob_str = dob.strftime("%d%m%Y")
            target_date_str = target_date.strftime("%d%m%Y")
            fav_string = "".join(valid_favs)
            seed_val = f"{dob_str}{target_date_str}{now_dt.strftime('%d%m%Y%H%M%S')}{fav_string}"
            
            random.seed(seed_val)
            kq = [f"{random.randint(0,99):02d}" for _ in range(5)]
            
            # --- HIỂN THỊ KẾT QUẢ ---
            st.markdown(f"""
            <div class="result-box">
                <div class="menh-info">BẠN SINH NĂM {lunar_year} (Âm Lịch) - MỆNH {user_menh}</div>
                <h3>KẾT QUẢ PHÂN TÍCH</h3>
            """, unsafe_allow_html=True)
            
            # Hiển thị từng số và mệnh của nó
            cols = st.columns(5)
            compatible_count = 0
            
            for idx, num in enumerate(kq):
                num_menh = get_number_element(num)
                is_hop, ly_do = check_compatibility(user_menh, num_menh)
                
                color = "black"
                if is_hop:
                    compatible_count += 1
                    color = "#D32F2F" # Đỏ nếu hợp
                
                with cols[idx]:
                    st.markdown(f"""
                    <div style="text-align: center;">
                        <div class="big-font" style="color: {color}">{num}</div>
                        <div class="element-text">Hành: {num_menh}</div>
                        <div style="font-size: 12px; color: {'green' if is_hop else '#999'}">{ly_do}</div>
                    </div>
                    """, unsafe_allow_html=True)
            
            # Đóng thẻ div result-box (bằng cách mở markdown mới để tránh lỗi render columns)
            st.markdown("</div>", unsafe_allow_html=True)
            
            # Phần thống kê
            st.markdown(f"""
            <div class="summary-box">
                <b>🔮 LUẬN GIẢI:</b><br>
                Có <b>{compatible_count}/5</b> con số hợp mệnh với bạn (Tương sinh hoặc Tương hỗ).<br>
                <i>(Mệnh của số tính theo chữ số tận cùng - thuật Hà Đồ)</i>
            </div>
            """, unsafe_allow_html=True)
            
            # Time check footer
            time_color = "green" if is_online else "red"
            source_text = "Google Server" if is_online else "Offline Mode"
            st.caption(f"Time check: {now_dt.strftime('%H:%M:%S')} ({source_text})")