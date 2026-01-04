import streamlit as st
import urllib.request
import random
from datetime import datetime, timedelta
from email.utils import parsedate_to_datetime

# --- IMPORT ÂM LỊCH ---
try:
    from lunardate import LunarDate
    HAS_LUNAR_LIB = True
except ImportError:
    HAS_LUNAR_LIB = False

# --- CONFIG ---
st.set_page_config(
    page_title="18h30 Team - Phong Thủy",
    page_icon="🔮",
    layout="centered"
)

# --- CSS MOBILE-FIRST ---
st.markdown("""
<style>
.lucky-card {
    background-color: #f7fbff;
    padding: 12px;
    border-radius: 12px;
    text-align: center;
    margin-bottom: 8px;
    box-shadow: 0 3px 5px rgba(0,0,0,0.1);
    color: #000 !important;
}

.big-number {
    font-size: 42px;
    font-weight: 900;
    line-height: 1;
}

.mini-text {
    font-size: 14px;
    font-weight: 600;
}

.result-header-box {
    padding: 10px;
    border-radius: 10px;
    background: #E3F2FD;
    text-align: center;
    margin: 12px 0;
    font-weight: bold;
    color: #0d47a1;
}

.summary-box {
    margin-top: 15px;
    padding: 10px;
    background: #FFF3E0;
    border-radius: 8px;
    text-align: center;
    font-weight: bold;
}

.footer {
    text-align: center;
    margin-top: 30px;
    font-size: 12px;
    color: #888;
}
</style>
""", unsafe_allow_html=True)

# --- LOGIC ---
def get_lunar_year_number(date_obj):
    if HAS_LUNAR_LIB:
        lunar = LunarDate.fromSolarDate(date_obj.year, date_obj.month, date_obj.day)
        return lunar.year
    return date_obj.year

def calculate_menh_nien(year):
    can_values = {4:1,5:1,6:2,7:2,8:3,9:3,0:4,1:4,2:5,3:5}
    can_val = can_values[year % 10]
    chi = year % 12
    chi_val = 0 if chi in [4,5,10,11] else 1 if chi in [6,7,0,1] else 2
    total = can_val + chi_val
    if total > 5: total -= 5
    return {1:"Kim",2:"Thủy",3:"Hỏa",4:"Thổ",5:"Mộc"}[total]

def get_number_element(num):
    d = int(num[-1])
    return ("Thủy" if d in [1,6] else
            "Hỏa" if d in [2,7] else
            "Mộc" if d in [3,8] else
            "Kim"  if d in [4,9] else "Thổ")

def check_compatibility(user, num):
    sinh = {"Kim":"Thủy","Thủy":"Mộc","Mộc":"Hỏa","Hỏa":"Thổ","Thổ":"Kim"}
    if user == num: return True, "Bình hòa"
    if sinh.get(num) == user: return True, "Tương sinh"
    return False, "Không hợp"

def get_google_time_hanoi():
    try:
        req = urllib.request.Request("https://www.google.com", method='HEAD')
        with urllib.request.urlopen(req, timeout=5) as r:
            dt = parsedate_to_datetime(r.headers['Date'])
            return (dt + timedelta(hours=7)).replace(tzinfo=None), True
    except:
        return datetime.now(), False

# --- UI ---
st.title("🔮 18h30 Team")
st.caption("Dự đoán số may mắn theo Entropy & Ngũ Hành")

with st.form("main"):
    dob = st.date_input("Ngày sinh", value=datetime(2000,1,1))
    target = st.date_input("Ngày dự đoán", value=datetime.now())
    cols = st.columns(5)
    favs = [c.text_input(f"S{i+1}", max_chars=2) for i,c in enumerate(cols)]
    submit = st.form_submit_button("PHÂN TÍCH", use_container_width=True)

if submit:
    favs = [f for f in favs if f.isdigit() and len(f)==2]
    now, online = get_google_time_hanoi()
    lunar_year = get_lunar_year_number(dob)
    menh = calculate_menh_nien(lunar_year)

    random.seed(dob.strftime("%d%m%Y")+target.strftime("%d%m%Y")+now.strftime("%H%M%S")+"".join(favs))
    results = [f"{random.randint(0,99):02d}" for _ in range(5)]

    st.markdown(f"""
    <div class="result-header-box">
        Sinh năm <b>{lunar_year}</b> – Mệnh <b>{menh}</b>
    </div>
    """, unsafe_allow_html=True)

    # 👉 2 CỘT – RẤT GỌN CHO MOBILE
    cols = st.columns(2)
    hop = 0

    for i, num in enumerate(results):
        hanh = get_number_element(num)
        ok, txt = check_compatibility(menh, hanh)
        if ok: hop += 1
        border = "3px solid #2E7D32" if ok else "1px solid #B0BEC5"

        with cols[i % 2]:
            st.markdown(f"""
            <div class="lucky-card" style="border:{border}">
                <div class="big-number">{num}</div>
                <div class="mini-text">{hanh} · {txt}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="summary-box">
        Hợp mệnh: {hop}/5 · ⏱ {now.strftime('%H:%M:%S')}
    </div>
    """, unsafe_allow_html=True)

st.markdown('<div class="footer">Created by MinhMup</div>', unsafe_allow_html=True)
