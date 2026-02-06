import sys
import os

# Add parent directory to path to allow importing app modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
from app.logic import (
    # Dashboard
    get_daily_revenue_last_30_days,
    get_top_selling_products,
    get_database_statistics,
    # Products
    get_all_products_with_stock,
    search_products,
    get_product_by_id,
    get_all_categories,
    create_product,
    update_product,
    delete_product,
    # Customers
    create_customer,
    update_customer,
    delete_customer,
    search_customers,
    get_customer_by_id,
    # Employees
    create_employee,
    update_employee,
    delete_employee,
    search_employees,
    get_employee_by_id,
    get_all_positions,
    # Suppliers
    create_supplier,
    update_supplier,
    delete_supplier,
    get_all_suppliers,
    get_supplier_by_id,
    # Inventory
    get_products_in_warehouse,
    get_all_counters,
    transfer_inventory,
    update_stock_after_sale,
    # Reports
    get_low_stock_on_counter,
    get_products_need_refill,
    get_out_of_stock_warehouse_but_avail_counter,
    get_total_stock_all,
    get_products_by_category_sorted,
    # Expiry
    get_near_expiry_products,
    get_expired_products,
    get_products_for_auto_discount,
    apply_discount_near_expiry,
    # Revenue
    get_product_rankings_by_revenue_month,
    # Rankings
    get_customer_rankings,
    get_employee_rankings_by_month,
    get_supplier_rankings,
    get_supplier_rankings_by_sales,
    # POS
    create_invoice,
    add_invoice_detail,
    get_random_customer,
    get_random_customer,
    get_random_employee,
    calculate_employee_salary
)

st.set_page_config(page_title="Hệ thống Quản lý Siêu thị", layout="wide", page_icon="🛒")

st.title("🛒 Hệ thống Quản lý Siêu thị")

# Sidebar
menu = st.sidebar.radio("📌 Chức năng", [
    "🏠 Tổng quan", 
    "💳 Bán hàng (POS)", 
    "📦 Kho & Quầy hàng", 
    "🗂 Quản lý Dữ liệu", 
    "📈 Báo cáo & Xếp hạng"
])

# ============================================================
# 1. DASHBOARD
# ============================================================
if menu == "🏠 Tổng quan":
    st.header("📊 Tổng quan Kinh doanh (30 ngày qua)")
    
    rev_data = get_daily_revenue_last_30_days()
    
    # Metrics Row
    col1, col2, col3, col4 = st.columns(4)
    
    if rev_data:
        df_rev = pd.DataFrame(rev_data)
        total_revenue = df_rev['Revenue'].sum()
        col1.metric("💰 Tổng Doanh thu", f"{total_revenue:,.0f} VND")
    else:
        col1.metric("💰 Tổng Doanh thu", "0 VND")
    
    low_stock = get_low_stock_on_counter(threshold=10)
    col2.metric("⚠️ Hàng sắp hết trên quầy", f"{len(low_stock) if low_stock else 0}")
    
    near_expiry = get_near_expiry_products(days_threshold=7)
    col3.metric("⏰ Hàng sắp hết hạn", f"{len(near_expiry) if near_expiry else 0}")
    
    need_refill = get_products_need_refill(threshold=10)
    col4.metric("🔄 Cần bổ sung lên quầy", f"{len(need_refill) if need_refill else 0}")

    # Revenue Chart
    if rev_data:
        fig = px.line(df_rev, x='Date', y='Revenue', title="Biểu đồ Doanh thu theo Ngày", markers=True)
        fig.update_layout(xaxis_title="Ngày", yaxis_title="Doanh thu (VND)")
        st.plotly_chart(fig, use_container_width=True)
    
    # Top Products
    st.subheader("🏆 Top 10 Sản phẩm bán chạy")
    top_products = get_top_selling_products(10)
    if top_products:
        df_top = pd.DataFrame(top_products)
        fig2 = px.bar(df_top, x='ProductName', y='TotalQuantity', title="Số lượng bán", color='TotalRevenue')
        st.plotly_chart(fig2, use_container_width=True)

    # Warnings Section
    st.divider()
    c1, c2 = st.columns(2)
    
    with c1:
        st.subheader("⚠️ Cảnh báo Tồn kho Quầy")
        if low_stock:
            st.dataframe(pd.DataFrame(low_stock), use_container_width=True)
        else:
            st.success("✅ Tồn kho trên quầy ổn định.")
            
    with c2:
        st.subheader("⏰ Cảnh báo Hết hạn (Thực phẩm)")
        if near_expiry:
            df_exp = pd.DataFrame(near_expiry)
            st.dataframe(df_exp, use_container_width=True)
        else:
            st.success("✅ Không có hàng sắp hết hạn (dưới 7 ngày).")
    
    # Database Statistics Section (for Report Screenshot)
    st.divider()
    st.subheader("📊 Tổng quan Dữ liệu Hệ thống")
    st.caption("Số lượng bản ghi trong các bảng quan trọng của CSDL")
    
    db_stats = get_database_statistics()
    if db_stats:
        df_stats = pd.DataFrame(db_stats)
        
        # Split into 3 columns for better layout
        col1, col2, col3 = st.columns(3)
        
        # Calculate split points
        n = len(df_stats)
        split1 = n // 3
        split2 = 2 * n // 3
        
        with col1:
            st.dataframe(df_stats.iloc[:split1], use_container_width=True, hide_index=True)
        with col2:
            st.dataframe(df_stats.iloc[split1:split2], use_container_width=True, hide_index=True)
        with col3:
            st.dataframe(df_stats.iloc[split2:], use_container_width=True, hide_index=True)

# ============================================================
# 2. POS
# ============================================================
elif menu == "💳 Bán hàng (POS)":
    st.header("💳 Điểm Bán Hàng")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("👤 Thông tin Khách & NV")
        
        # Customer
        if 'current_customer' not in st.session_state:
            st.session_state['current_customer'] = None
             
        cust_search = st.text_input("🔍 Tìm Khách hàng (SĐT/Tên)")
        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            if st.button("Tìm kiếm", use_container_width=True):
                res = search_customers(cust_search)
                if res:
                    st.session_state['current_customer'] = res[0]
                else:
                    st.error("Không tìm thấy")
        with col_btn2:
            if st.button("🎲 Ngẫu nhiên", use_container_width=True):
                st.session_state['current_customer'] = get_random_customer()

        if st.session_state['current_customer']:
            c = st.session_state['current_customer']
            st.success(f"👤 {c['FullName']} ({c['Tier']})")
        else:
            st.warning("Vui lòng chọn khách hàng")

        st.divider()
        
        # Employee
        if 'current_employee' not in st.session_state:
            st.session_state['current_employee'] = get_random_employee()
        
        emp = st.session_state['current_employee']
        if emp:
            st.info(f"🧑‍💼 Thu ngân: {emp['FullName']}")

    with col2:
        st.subheader("🛒 Giỏ hàng")
        
        if 'basket' not in st.session_state:
            st.session_state['basket'] = []
            
        prod_input = st.text_input("📦 Quét mã / Nhập tên SP", key="pos_search")
        if st.button("➕ Thêm vào giỏ"):
            if prod_input.isdigit():
                prod = get_product_by_id(int(prod_input))
            else:
                results = search_products(prod_input)
                prod = results[0] if results else None
                
            if prod:
                st.session_state['basket'].append({
                    'ProductID': prod['ProductID'],
                    'ProductName': prod['ProductName'],
                    'SellingPrice': float(prod['SellingPrice']),
                    'Quantity': 1
                })
                st.toast(f"✅ Đã thêm {prod['ProductName']}")
            else:
                st.error("Không tìm thấy sản phẩm")

        if st.session_state['basket']:
            df_basket = pd.DataFrame(st.session_state['basket'])
            st.dataframe(df_basket, use_container_width=True)
            
            total = df_basket['SellingPrice'].sum() 
            st.metric("💵 Tổng tiền", f"{total:,.0f} VND")
            
            col_pay1, col_pay2 = st.columns(2)
            with col_pay1:
                if st.button("✅ Thanh toán", type="primary", use_container_width=True):
                    if st.session_state['current_customer']:
                        inv_id = create_invoice(
                            st.session_state['current_customer']['CustomerID'],
                            st.session_state['current_employee']['EmployeeID'],
                            "Tiền mặt", total
                        )
                        
                        if inv_id:
                            for item in st.session_state['basket']:
                                add_invoice_detail(inv_id, item['ProductID'], item['Quantity'], item['SellingPrice'])
                                update_stock_after_sale(item['ProductID'], item['Quantity'])
                            
                            st.success("🎉 Giao dịch thành công! Đã cập nhật tồn kho.")
                            st.session_state['basket'] = []
                            st.rerun()
                        else:
                            st.error("Lỗi tạo hóa đơn")
                    else:
                        st.error("Chưa có thông tin khách hàng")
            with col_pay2:
                if st.button("🗑️ Xóa giỏ", use_container_width=True):
                    st.session_state['basket'] = []
                    st.rerun()

# ============================================================
# 3. INVENTORY
# ============================================================
elif menu == "📦 Kho & Quầy hàng":
    st.header("📦 Quản lý Kho & Trưng bày")
    
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📋 Tồn kho Chi tiết", 
        "🔄 Chuyển hàng lên Quầy", 
        "⚠️ Cần Bổ sung",
        "📊 Tổng Tồn kho",
        "🚨 Hết trong Kho"
    ])
    
    with tab1:
        st.subheader("Danh sách Sản phẩm & Tồn kho")
        products = get_all_products_with_stock()
        if products:
            df = pd.DataFrame(products)
            
            # Filter
            categories = get_all_categories()
            cat_names = ["Tất cả"] + [c['CategoryName'] for c in categories] if categories else ["Tất cả"]
            selected_cat = st.selectbox("Lọc theo Danh mục", cat_names)
            
            if selected_cat != "Tất cả":
                df = df[df['CategoryName'] == selected_cat]
            
            st.dataframe(df, use_container_width=True)
        
    with tab2:
        st.subheader("🔄 Bổ sung hàng hoá từ Kho lên Quầy")
        
        wh_items = get_products_in_warehouse()
        if wh_items:
            st.write("**Hàng sẵn có trong kho:**")
            st.dataframe(pd.DataFrame(wh_items), use_container_width=True)
            
            counters = get_all_counters()
            counter_options = {f"{c['CounterName']} ({c['CategoryName']})": c['CounterID'] for c in counters} if counters else {}
            
            with st.form("transfer_form"):
                st.write("**Nhập thông tin chuyển hàng:**")
                c1, c2 = st.columns(2)
                with c1:
                    f_inv = st.number_input("ID Lô hàng (InventoryID)", min_value=1, step=1)
                    f_prod = st.number_input("ID Sản phẩm (ProductID)", min_value=1, step=1)
                with c2:
                    f_count_name = st.selectbox("Chọn Quầy", list(counter_options.keys()) if counter_options else [])
                    f_qty = st.number_input("Số lượng chuyển", min_value=1, value=10, step=1)
                
                f_pos = st.text_input("Vị trí kệ (VD: A1)", "A1")
                
                if st.form_submit_button("✅ Xác nhận chuyển", type="primary"):
                    if f_count_name and counter_options:
                        f_count = counter_options[f_count_name]
                        success, msg = transfer_inventory(f_inv, f_count, f_qty, f_pos)
                        if success:
                            st.success(msg)
                        else:
                            st.error(msg)
        else:
            st.info("Không có hàng trong kho.")
                    
    with tab3:
        st.subheader("⚠️ Hàng cần bổ sung (Sắp hết trên quầy nhưng còn trong kho)")
        threshold = st.slider("Ngưỡng cảnh báo", 1, 20, 10)
        need_refill = get_products_need_refill(threshold)
        if need_refill:
            st.dataframe(pd.DataFrame(need_refill), use_container_width=True)
        else:
            st.success("✅ Tất cả hàng trên quầy đều đủ số lượng.")
            
    with tab4:
        st.subheader("📊 Tổng Tồn kho (Kho + Quầy)")
        total_stock = get_total_stock_all()
        if total_stock:
            df = pd.DataFrame(total_stock)
            st.dataframe(df, use_container_width=True)
            
            fig = px.bar(df.head(20), x='ProductName', y='TotalStock', 
                        title="Top 20 Sản phẩm tồn kho thấp nhất", color='CategoryName')
            st.plotly_chart(fig, use_container_width=True)
        
    with tab5:
        st.subheader("🚨 Hết trong Kho nhưng còn trên Quầy")
        urgent = get_out_of_stock_warehouse_but_avail_counter()
        if urgent:
            st.warning("⚠️ Các sản phẩm này cần nhập hàng gấp!")
            st.dataframe(pd.DataFrame(urgent), use_container_width=True)
        else:
            st.success("✅ Không có sản phẩm nào hết hàng trong kho.")

# ============================================================
# 4. MANAGEMENT
# ============================================================
elif menu == "🗂 Quản lý Dữ liệu":
    st.header("🗂 Quản lý Dữ liệu")
    
    type_ = st.selectbox("Chọn đối tượng quản lý", ["📦 Sản phẩm", "👤 Khách hàng", "👷 Nhân viên", "🏭 Nhà cung cấp"])
    
    # ========================
    # PRODUCTS
    # ========================
    if type_ == "📦 Sản phẩm":
        tab_list, tab_add = st.tabs(["📋 Danh sách", "➕ Thêm mới"])
        
        with tab_list:
            search = st.text_input("🔍 Tìm kiếm sản phẩm...")
            if search:
                data = search_products(search)
            else:
                data = get_all_products_with_stock()
                
            if data:
                df = pd.DataFrame(data)
                st.dataframe(df, use_container_width=True)
                
                # Edit/Delete
                st.divider()
                st.write("**Sửa/Xóa sản phẩm:**")
                prod_id = st.number_input("Nhập ID sản phẩm", min_value=1, step=1)
                
                prod = get_product_by_id(prod_id) if prod_id else None
                if prod:
                    categories = get_all_categories()
                    cat_options = {c['CategoryName']: c['CategoryID'] for c in categories} if categories else {}
                    
                    with st.form("edit_product"):
                        new_name = st.text_input("Tên SP", prod['ProductName'])
                        c1, c2 = st.columns(2)
                        with c1:
                            new_import = st.number_input("Giá nhập", value=float(prod['ImportPrice']), step=1000.0)
                            new_unit = st.text_input("Đơn vị", prod['Unit'])
                        with c2:
                            new_selling = st.number_input("Giá bán", value=float(prod['SellingPrice']), step=1000.0)
                            new_cat = st.selectbox("Danh mục", list(cat_options.keys()))
                        
                        col_btn1, col_btn2 = st.columns(2)
                        with col_btn1:
                            if st.form_submit_button("💾 Cập nhật", type="primary"):
                                if new_selling > new_import:
                                    update_product(prod_id, new_name, new_import, new_selling, new_unit, cat_options[new_cat])
                                    st.success("✅ Đã cập nhật sản phẩm!")
                                    st.rerun()
                                else:
                                    st.error("Giá bán phải lớn hơn giá nhập!")
                        with col_btn2:
                            if st.form_submit_button("🗑️ Xóa"):
                                delete_product(prod_id)
                                st.success("✅ Đã xóa sản phẩm!")
                                st.rerun()
                                
        with tab_add:
            st.subheader("➕ Thêm Sản phẩm mới")
            categories = get_all_categories()
            cat_options = {c['CategoryName']: c['CategoryID'] for c in categories} if categories else {}
            
            with st.form("add_product"):
                name = st.text_input("Tên sản phẩm")
                c1, c2 = st.columns(2)
                with c1:
                    import_price = st.number_input("Giá nhập (VND)", min_value=0, step=1000)
                    unit = st.text_input("Đơn vị (Cái, Kg, Hộp...)")
                with c2:
                    selling_price = st.number_input("Giá bán (VND)", min_value=0, step=1000)
                    category = st.selectbox("Danh mục", list(cat_options.keys()) if cat_options else [])
                
                if st.form_submit_button("➕ Thêm sản phẩm", type="primary"):
                    if name and selling_price > import_price and category:
                        create_product(name, import_price, selling_price, unit, cat_options[category])
                        st.success(f"✅ Đã thêm sản phẩm: {name}")
                    else:
                        st.error("Vui lòng điền đầy đủ thông tin. Giá bán phải > Giá nhập.")
    
    # ========================
    # CUSTOMERS
    # ========================
    elif type_ == "👤 Khách hàng":
        tab_list, tab_add = st.tabs(["📋 Danh sách", "➕ Thêm mới"])
        
        with tab_list:
            search = st.text_input("🔍 Tìm kiếm (Tên/SĐT)...")
            data = search_customers(search) if search else search_customers("")
                
            if data:
                st.dataframe(pd.DataFrame(data), use_container_width=True)
                
                st.divider()
                st.write("**Sửa/Xóa khách hàng:**")
                cust_id = st.number_input("Nhập ID khách hàng", min_value=1, step=1)
                
                cust = get_customer_by_id(cust_id) if cust_id else None
                if cust:
                    with st.form("edit_customer"):
                        new_name = st.text_input("Họ tên", cust['FullName'])
                        new_phone = st.text_input("SĐT", cust['Phone'])
                        new_tier = st.selectbox("Hạng", ['Thành viên', 'Bạc', 'Vàng', 'Kim cương'], 
                                               index=['Thành viên', 'Bạc', 'Vàng', 'Kim cương'].index(cust['Tier']) if cust['Tier'] in ['Thành viên', 'Bạc', 'Vàng', 'Kim cương'] else 0)
                        
                        col_btn1, col_btn2 = st.columns(2)
                        with col_btn1:
                            if st.form_submit_button("💾 Cập nhật", type="primary"):
                                update_customer(cust_id, new_name, new_phone, new_tier)
                                st.success("✅ Đã cập nhật!")
                                st.rerun()
                        with col_btn2:
                            if st.form_submit_button("🗑️ Xóa"):
                                delete_customer(cust_id)
                                st.success("✅ Đã xóa!")
                                st.rerun()
                                
        with tab_add:
            st.subheader("➕ Thêm Khách hàng mới")
            with st.form("add_customer"):
                name = st.text_input("Họ tên")
                phone = st.text_input("Số điện thoại")
                tier = st.selectbox("Hạng thành viên", ['Thành viên', 'Bạc', 'Vàng', 'Kim cương'])
                
                if st.form_submit_button("➕ Thêm khách hàng", type="primary"):
                    if name and phone:
                        create_customer(name, phone, tier)
                        st.success(f"✅ Đã thêm khách hàng: {name}")
                    else:
                        st.error("Vui lòng điền đầy đủ thông tin.")
    
    # ========================
    # EMPLOYEES
    # ========================
    elif type_ == "👷 Nhân viên":
        tab_list, tab_add = st.tabs(["📋 Danh sách", "➕ Thêm mới"])
        
        with tab_list:
            search = st.text_input("🔍 Tìm kiếm tên nhân viên...")
            data = search_employees(search) if search else search_employees("")
                
            if data:
                st.dataframe(pd.DataFrame(data), use_container_width=True)
                
                st.divider()
                st.write("**Sửa/Xóa nhân viên:**")
                emp_id = st.number_input("Nhập ID nhân viên", min_value=1, step=1)
                
                emp = get_employee_by_id(emp_id) if emp_id else None
                if emp:
                    positions = get_all_positions()
                    pos_options = {p['PositionName']: p['PositionID'] for p in positions} if positions else {}
                    
                    with st.form("edit_employee"):
                        new_name = st.text_input("Họ tên", emp['FullName'])
                        c1, c2 = st.columns(2)
                        with c1:
                            new_dob = st.date_input("Ngày sinh", emp['DateOfBirth'] if emp['DateOfBirth'] else datetime.now())
                            new_phone = st.text_input("SĐT", emp['Phone'] if emp['Phone'] else "")
                        with c2:
                            new_address = st.text_input("Địa chỉ", emp['Address'] if emp['Address'] else "")
                            new_pos = st.selectbox("Vị trí", list(pos_options.keys()))
                        
                        col_btn1, col_btn2 = st.columns(2)
                        with col_btn1:
                            if st.form_submit_button("💾 Cập nhật", type="primary"):
                                update_employee(emp_id, new_name, new_dob, new_address, new_phone, pos_options[new_pos])
                                st.success("✅ Đã cập nhật!")
                                st.rerun()
                        with col_btn2:
                            if st.form_submit_button("🗑️ Xóa"):
                                delete_employee(emp_id)
                                st.success("✅ Đã xóa!")
                                st.rerun()
                                
        with tab_add:
            st.subheader("➕ Thêm Nhân viên mới")
            positions = get_all_positions()
            pos_options = {p['PositionName']: p['PositionID'] for p in positions} if positions else {}
            
            with st.form("add_employee"):
                name = st.text_input("Họ tên")
                c1, c2 = st.columns(2)
                with c1:
                    dob = st.date_input("Ngày sinh")
                    phone = st.text_input("Số điện thoại")
                with c2:
                    address = st.text_input("Địa chỉ")
                    position = st.selectbox("Vị trí", list(pos_options.keys()) if pos_options else [])
                
                if st.form_submit_button("➕ Thêm nhân viên", type="primary"):
                    if name and position:
                        create_employee(name, dob, address, phone, pos_options[position])
                        st.success(f"✅ Đã thêm nhân viên: {name}")
                    else:
                        st.error("Vui lòng điền đầy đủ thông tin.")
    
    # ========================
    # SUPPLIERS
    # ========================
    elif type_ == "🏭 Nhà cung cấp":
        tab_list, tab_add = st.tabs(["📋 Danh sách", "➕ Thêm mới"])
        
        with tab_list:
            data = get_all_suppliers()
            if data:
                st.dataframe(pd.DataFrame(data), use_container_width=True)
                
                st.divider()
                st.write("**Sửa/Xóa nhà cung cấp:**")
                sup_id = st.number_input("Nhập ID nhà cung cấp", min_value=1, step=1)
                
                sup = get_supplier_by_id(sup_id) if sup_id else None
                if sup:
                    with st.form("edit_supplier"):
                        new_name = st.text_input("Tên NCC", sup['SupplierName'])
                        new_address = st.text_input("Địa chỉ", sup['Address'] if sup['Address'] else "")
                        
                        col_btn1, col_btn2 = st.columns(2)
                        with col_btn1:
                            if st.form_submit_button("💾 Cập nhật", type="primary"):
                                update_supplier(sup_id, new_name, new_address)
                                st.success("✅ Đã cập nhật!")
                                st.rerun()
                        with col_btn2:
                            if st.form_submit_button("🗑️ Xóa"):
                                delete_supplier(sup_id)
                                st.success("✅ Đã xóa!")
                                st.rerun()
                                
        with tab_add:
            st.subheader("➕ Thêm Nhà cung cấp mới")
            with st.form("add_supplier"):
                name = st.text_input("Tên nhà cung cấp")
                address = st.text_input("Địa chỉ")
                
                if st.form_submit_button("➕ Thêm NCC", type="primary"):
                    if name:
                        create_supplier(name, address)
                        st.success(f"✅ Đã thêm: {name}")
                    else:
                        st.error("Vui lòng nhập tên nhà cung cấp.")

# ============================================================
# 5. REPORTS
# ============================================================
elif menu == "📈 Báo cáo & Xếp hạng":
    st.header("📈 Báo cáo & Xếp hạng")
    
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "👑 Khách hàng VIP", 
        "🏅 Nhân viên Xuất sắc", 
        "🏭 Nhà cung cấp",
        "📊 Doanh thu Sản phẩm",
        "⏰ Hàng cận Date",
        "💰 Tính lương NV"
    ])
    
    with tab1:
        st.subheader("👑 Khách hàng chi tiêu nhiều nhất")
        data = get_customer_rankings()
        if data:
            df = pd.DataFrame(data)
            st.dataframe(df, use_container_width=True)
            
            fig = px.bar(df.head(10), x='FullName', y='TotalSpent', title="Top 10 Khách hàng VIP", color='Tier')
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Chưa có dữ liệu.")
        
    with tab2:
        st.subheader("🏅 Nhân viên có doanh số cao nhất")
        col1, col2 = st.columns(2)
        m = col1.number_input("Tháng", 1, 12, datetime.now().month, key="emp_month")
        y = col2.number_input("Năm", 2020, 2030, datetime.now().year, key="emp_year")
        
        data = get_employee_rankings_by_month(m, y)
        if data:
            df = pd.DataFrame(data)
            st.dataframe(df, use_container_width=True)
            
            fig = px.bar(df, x='FullName', y='TotalSales', title=f"Doanh số tháng {m}/{y}", color='PositionName')
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Không có dữ liệu tháng này.")
            
    with tab3:
        st.subheader("🏭 Xếp hạng Nhà cung cấp")
        
        rank_type = st.radio("Xếp hạng theo:", ["Giá trị hàng tồn kho", "Doanh thu bán hàng"], horizontal=True)
        
        if rank_type == "Giá trị hàng tồn kho":
            data = get_supplier_rankings()
        else:
            data = get_supplier_rankings_by_sales()
            
        if data:
            st.dataframe(pd.DataFrame(data), use_container_width=True)
        else:
            st.info("Không có dữ liệu.")
            
    with tab4:
        st.subheader("📊 Doanh thu Sản phẩm theo Tháng")
        col1, col2 = st.columns(2)
        m = col1.number_input("Tháng", 1, 12, datetime.now().month, key="prod_month")
        y = col2.number_input("Năm", 2020, 2030, datetime.now().year, key="prod_year")
        
        data = get_product_rankings_by_revenue_month(m, y)
        if data:
            df = pd.DataFrame(data)
            st.dataframe(df, use_container_width=True)
            
            fig = px.bar(df.head(15), x='ProductName', y='Revenue', title=f"Top 15 Sản phẩm doanh thu cao - Tháng {m}/{y}")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Không có dữ liệu tháng này.")
            
    with tab5:
        st.subheader("⏰ Hàng sắp hết hạn & Giảm giá tự động")
        
        sub_tab1, sub_tab2, sub_tab3 = st.tabs(["Sắp hết hạn", "Đã quá hạn", "Gợi ý giảm giá"])
        
        with sub_tab1:
            days = st.slider("Số ngày còn lại", 1, 30, 7)
            near_exp = get_near_expiry_products(days)
            if near_exp:
                st.dataframe(pd.DataFrame(near_exp), use_container_width=True)
            else:
                st.success(f"✅ Không có hàng hết hạn trong {days} ngày tới.")
                
        with sub_tab2:
            expired = get_expired_products()
            if expired:
                st.error("⚠️ Các sản phẩm sau đã quá hạn bán!")
                st.dataframe(pd.DataFrame(expired), use_container_width=True)
            else:
                st.success("✅ Không có sản phẩm quá hạn.")
                
        with sub_tab3:
            st.write("**Quy tắc giảm giá tự động:**")
            st.info("- Đồ khô (HSD > 30 ngày): còn dưới 5 ngày → Giảm 50%\n- Rau quả (HSD < 30 ngày): còn dưới 1 ngày → Giảm 50%")
            
            auto_disc = get_products_for_auto_discount()
            if auto_disc:
                df = pd.DataFrame(auto_disc)
                st.dataframe(df, use_container_width=True)
                
                st.write("**Áp dụng giảm giá:**")
                prod_to_disc = st.selectbox("Chọn sản phẩm", df['ProductName'].unique())
                disc_percent = st.slider("Phần trăm giảm (%)", 10, 70, 50)
                
                if st.button("✅ Áp dụng Giảm giá", type="primary"):
                    pid = df[df['ProductName'] == prod_to_disc]['ProductID'].values[0]
                    apply_discount_near_expiry(pid, disc_percent)
                    st.success(f"✅ Đã giảm giá {disc_percent}% cho {prod_to_disc}")
                    st.rerun()
            else:
                st.success("✅ Không có sản phẩm cần giảm giá theo quy tắc tự động.")
                
    with tab6:
        st.subheader("💰 Tính lương Nhân viên (Theo tháng)")
        
        col1, col2 = st.columns(2)
        with col1:
            emp_input = st.number_input("ID Nhân viên", min_value=1, step=1, key="sal_emp_id")
        with col2:
            s_month = st.number_input("Tháng", 1, 12, datetime.now().month, key="sal_month")
            s_year = st.number_input("Năm", 2020, 2030, datetime.now().year, key="sal_year")
            
        if st.button("🧮 Tính lương", type="primary"):
            emp = get_employee_by_id(emp_input)
            if emp:
                salary = calculate_employee_salary(emp_input, s_month, s_year)
                st.divider()
                st.write(f"**Nhân viên:** {emp['FullName']}")
                st.write(f"**Vị trí:** {emp.get('PositionName', 'N/A')}")
                if salary is not None:
                    st.success(f"💸 Tổng lương tháng {s_month}/{s_year}: **{salary:,.0f} VND**")
                else:
                    st.error("Không thể tính lương (Có thể thiếu dữ liệu chấm công hoặc lỗi Procedure).")
            else:
                st.error("Không tìm thấy nhân viên.")
