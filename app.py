import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

# ตั้งค่าหน้าตาของ Web Application
st.set_page_config(
    page_title="Dashboard สถิติการท่องเที่ยวรายจังหวัด",
    page_icon="✈️",
    layout="wide"
)

# ส่วนหัวของ Dashboard
st.title("✈️ Dashboard สถิติการท่องเที่ยวรายจังหวัด")
st.caption("ระบบวิเคราะห์เชิงลึก: ปริมาณนักท่องเที่ยว รายได้ และสัดส่วนจำแนกตามภูมิภาค")

# สร้างชุดข้อมูลจำลองแบบละเอียด (มีทั้ง ภูมิภาค, จังหวัด, เดือน, นักท่องเที่ยวไทย/ต่างชาติ, รายได้)
@st.cache_data
def load_data():
    np.random.seed(42)
    months = ["มกราคม", "กุมภาพันธ์", "มีนาคม", "เมษายน", "พฤษภาคม", "มิถุนายน", 
              "กรกฎาคม", "สิงหาคม", "กันยายน", "ตุลาคม", "พฤศจิกายน", "ธันวาคม"]
    
    data_provinces = {
        "ภาคเหนือ": ["เชียงใหม่", "เชียงราย", "แม่ฮ่องสอน", "น่าน"],
        "ภาคกลาง": ["กรุงเทพมหานคร", "พระนครศรีอยุธยา", "กาญจนบุรี"],
        "ภาคใต้": ["ภูเก็ต", "กระบี่", "สุราษฎร์ธานี", "พังงา"],
        "ภาคตะวันออก": ["ชลบุรี", "ระยอง", "ตราด"]
    }
    
    rows = []
    for region, provs in data_provinces.items():
        for p in provs:
            for m in months:
                thai = np.random.randint(15000, 120000)
                foreign = np.random.randint(8000, 180000)
                rev_per_head = np.random.randint(1500, 4500)
                total = thai + foreign
                revenue = total * rev_per_head
                
                rows.append({
                    "ปี": "2568",
                    "ภูมิภาค": region,
                    "จังหวัด": p,
                    "เดือน": m,
                    "นักท่องเที่ยวไทย (คน)": thai,
                    "นักท่องเที่ยวต่างชาติ (คน)": foreign,
                    "นักท่องเที่ยวรวม (คน)": total,
                    "รายได้รวม (บาท)": revenue
                })
    return pd.DataFrame(rows)

df = load_data()

# ---------------------------------------------------------
# Sidebar Filters (ตัวกรองข้อมูลหลายระดับ)
# ---------------------------------------------------------
st.sidebar.header("🔍 Filter ข้อมูล")

selected_region = st.sidebar.multiselect(
    "ภูมิภาค:", 
    options=df["ภูมิภาค"].unique(), 
    default=df["ภูมิภาค"].unique()
)

available_provinces = df[df["ภูมิภาค"].isin(selected_region)]["จังหวัด"].unique()
selected_provinces = st.sidebar.multiselect(
    "จังหวัด:", 
    options=available_provinces, 
    default=available_provinces
)

selected_months = st.sidebar.multiselect(
    "เดือน:", 
    options=df["เดือน"].unique(), 
    default=df["เดือน"].unique()
)

# กรองข้อมูล
filtered_df = df[
    (df["ภูมิภาค"].isin(selected_region)) & 
    (df["จังหวัด"].isin(selected_provinces)) & 
    (df["เดือน"].isin(selected_months))
]

# ---------------------------------------------------------
# 1. สรุปข้อมูล (KPI Metrics 5 กล่อง)
# ---------------------------------------------------------
st.subheader("📊 สรุปข้อมูล")
c1, c2, c3, c4, c5 = st.columns(5)

total_tourists = filtered_df["นักท่องเที่ยวรวม (คน)"].sum()
thai_tourists = filtered_df["นักท่องเที่ยวไทย (คน)"].sum()
foreign_tourists = filtered_df["นักท่องเที่ยวต่างชาติ (คน)"].sum()
total_rev = filtered_df["รายได้รวม (บาท)"].sum()
avg_rev_per_head = total_rev / total_tourists if total_tourists > 0 else 0

c1.metric("นักท่องเที่ยวรวม", f"{total_tourists:,.0f} คน")
c2.metric("นักท่องเที่ยวไทย", f"{thai_tourists:,.0f} คน")
c3.metric("นักท่องเที่ยวต่างชาติ", f"{foreign_tourists:,.0f} คน")
c4.metric("รายได้รวมทั้งหมด", f"{total_rev/1e6:,.2f} ลบ.")
c5.metric("รายได้เฉลี่ยต่อคน", f"{avg_rev_per_head:,.0f} บาท")

st.markdown("---")

# ---------------------------------------------------------
# 2. ปริมาณนักท่องเที่ยวรายเดือน (Line Chart)
# ---------------------------------------------------------
st.subheader("📈 ปริมาณนักท่องเที่ยวรายเดือน")
month_order = ["มกราคม", "กุมภาพันธ์", "มีนาคม", "เมษายน", "พฤษภาคม", "มิถุนายน", 
               "กรกฎาคม", "สิงหาคม", "กันยายน", "ตุลาคม", "พฤศจิกายน", "ธันวาคม"]

trend_df = filtered_df.groupby("เดือน", as_index=False)[["นักท่องเที่ยวไทย (คน)", "นักท่องเที่ยวต่างชาติ (คน)", "นักท่องเที่ยวรวม (คน)"]].sum()
trend_df["เดือน"] = pd.Categorical(trend_df["เดือน"], categories=month_order, ordered=True)
trend_df = trend_df.sort_values("เดือน")

fig_line = px.line(
    trend_df, x="เดือน", 
    y=["นักท่องเที่ยวรวม (คน)", "นักท่องเที่ยวไทย (คน)", "นักท่องเที่ยวต่างชาติ (คน)"],
    markers=True,
    title="แนวโน้มปริมาณนักท่องเที่ยวแต่ละประเภทในรอบปี"
)
st.plotly_chart(fig_line, use_container_width=True)

# ---------------------------------------------------------
# 3. ปริมาณตามจังหวัด (Grouped Bar Chart แนวยาว)
# ---------------------------------------------------------
st.subheader("🏛️ ปริมาณนักท่องเที่ยวตามจังหวัด")
prov_df = filtered_df.groupby("จังหวัด", as_index=False)[["นักท่องเที่ยวไทย (คน)", "นักท่องเที่ยวต่างชาติ (คน)"]].sum()
prov_melted = prov_df.melt(id_vars=["จังหวัด"], var_name="ประเภท", value_name="จำนวน (คน)")

fig_bar = px.bar(
    prov_melted, x="จังหวัด", y="จำนวน (คน)", color="ประเภท",
    barmode="group", title="เปรียบเทียบปริมาณนักท่องเที่ยวไทย vs ต่างชาติ แยกตามจังหวัด"
)
st.plotly_chart(fig_bar, use_container_width=True)

# ---------------------------------------------------------
# 4. การวิเคราะห์สัดส่วนและอันดับ (Donut Chart + Horizontal Bar)
# ---------------------------------------------------------
st.subheader("🍩 การวิเคราะห์สัดส่วนและอันดับ")
col_left, col_right = st.columns(2)

with col_left:
    reg_df = filtered_df.groupby("ภูมิภาค", as_index=False)["นักท่องเที่ยวรวม (คน)"].sum()
    fig_donut = px.pie(
        reg_df, values="นักท่องเที่ยวรวม (คน)", names="ภูมิภาค",
        hole=0.4, title="สัดส่วนนักท่องเที่ยวแบ่งตามภูมิภาค"
    )
    st.plotly_chart(fig_donut, use_container_width=True)

with col_right:
    top_rev = filtered_df.groupby("จังหวัด", as_index=False)["รายได้รวม (บาท)"].sum().sort_values("รายได้รวม (บาท)", ascending=True).tail(7)
    fig_hbar = px.bar(
        top_rev, x="รายได้รวม (บาท)", y="จังหวัด", orientation="h",
        title="7 อันดับจังหวัดที่สร้างรายได้สูงสุด (บาท)", text_auto='.2s'
    )
    st.plotly_chart(fig_hbar, use_container_width=True)

# ---------------------------------------------------------
# 5. รายได้รายเดือน
# ---------------------------------------------------------
st.subheader("💰 แนวโน้มรายได้การท่องเที่ยวรายเดือน")
rev_month = filtered_df.groupby("เดือน", as_index=False)["รายได้รวม (บาท)"].sum()
rev_month["เดือน"] = pd.Categorical(rev_month["เดือน"], categories=month_order, ordered=True)
rev_month = rev_month.sort_values("เดือน")

fig_rev_bar = px.bar(
    rev_month, x="เดือน", y="รายได้รวม (บาท)",
    title="มูลค่ารายได้การท่องเที่ยวรวมรายเดือน (บาท)", color="รายได้รวม (บาท)"
)
st.plotly_chart(fig_rev_bar, use_container_width=True)

# ---------------------------------------------------------
# 6. รายละเอียดข้อมูล (Data Table)
# ---------------------------------------------------------
st.subheader("📋 รายละเอียดข้อมูล")
with st.expander("แสดงตารางข้อมูลฉบับเต็ม", expanded=True):
    st.dataframe(filtered_df, use_container_width=True)
    
    csv = filtered_df.to_csv(index=False).encode('utf-8-sig')
    st.download_button(
        label="📥 ดาวน์โหลดข้อมูลเป็นไฟล์ CSV",
        data=csv,
        file_name="tourism_data.csv",
        mime="text/csv"
    )