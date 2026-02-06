import sys
import os

# Add parent directory to path to allow importing app modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import random
from faker import Faker
from datetime import date, timedelta
import mysql.connector
from app.database import get_connection

# Update Faker to use Vietnamese locale
fake = Faker('vi_VN')

# ============================================================
# REALISTIC PRODUCT DATA BY CATEGORY
# ============================================================

PRODUCTS_BY_CATEGORY = {
    "Thực phẩm": [
        # Rau củ
        {"name": "Rau cải xanh", "unit": "Bó", "import_price": 8000, "expiry_days": 5, "safety_threshold": 5},
        {"name": "Cà chua", "unit": "Kg", "import_price": 15000, "expiry_days": 7, "safety_threshold": 7},
        {"name": "Khoai tây", "unit": "Kg", "import_price": 20000, "expiry_days": 30, "safety_threshold": 30},
        {"name": "Hành tây", "unit": "Kg", "import_price": 18000, "expiry_days": 30, "safety_threshold": 30},
        {"name": "Cà rốt", "unit": "Kg", "import_price": 12000, "expiry_days": 14, "safety_threshold": 14},
        {"name": "Bắp cải", "unit": "Cái", "import_price": 15000, "expiry_days": 10, "safety_threshold": 10},
        {"name": "Cà rốt", "unit": "Kg", "import_price": 18000, "expiry_days": 14, "safety_threshold": 14},
        {"name": "Bắp cải", "unit": "Kg", "import_price": 12000, "expiry_days": 10, "safety_threshold": 10},
        {"name": "Dưa leo", "unit": "Kg", "import_price": 15000, "expiry_days": 7, "safety_threshold": 7},
        {"name": "Ớt chuông", "unit": "Kg", "import_price": 25000, "expiry_days": 10, "safety_threshold": 10},
        
        # Trái cây
        {"name": "Táo Fuji", "unit": "Kg", "import_price": 45000, "expiry_days": 20, "safety_threshold": 20},
        {"name": "Cam sành", "unit": "Kg", "import_price": 30000, "expiry_days": 14, "safety_threshold": 14},
        {"name": "Chuối tiêu", "unit": "Nải", "import_price": 25000, "expiry_days": 7, "safety_threshold": 7},
        {"name": "Nho đen không hạt", "unit": "Kg", "import_price": 80000, "expiry_days": 10, "safety_threshold": 10},
        {"name": "Dưa hấu", "unit": "Kg", "import_price": 12000, "expiry_days": 7, "safety_threshold": 7},
        {"name": "Xoài cát Hòa Lộc", "unit": "Kg", "import_price": 55000, "expiry_days": 10, "safety_threshold": 10},
        
        # Thịt, cá
        {"name": "Thịt heo ba chỉ", "unit": "Kg", "import_price": 95000, "expiry_days": 3, "safety_threshold": 3},
        {"name": "Thịt bò Úc", "unit": "Kg", "import_price": 180000, "expiry_days": 5, "safety_threshold": 5},
        {"name": "Cá hồi Nauy", "unit": "Kg", "import_price": 220000, "expiry_days": 2, "safety_threshold": 2},
        {"name": "Sườn non heo", "unit": "Kg", "import_price": 110000, "expiry_days": 3, "safety_threshold": 3},
        
        # Sữa & Trứng
        {"name": "Sữa tươi Vinamilk", "unit": "Hộp", "import_price": 38000, "expiry_days": 60, "safety_threshold": 30},
        {"name": "Trứng gà sạch", "unit": "Vỉ", "import_price": 28000, "expiry_days": 25, "safety_threshold": 25},
        {"name": "Sữa chua Vinamilk", "unit": "Lốc", "import_price": 32000, "expiry_days": 45, "safety_threshold": 30},
        {"name": "Phô mai lát Anchor", "unit": "Hộp", "import_price": 65000, "expiry_days": 180, "safety_threshold": 90},
        
        # Đồ khô
        {"name": "Gạo ST25", "unit": "Kg", "import_price": 28000, "expiry_days": 365, "safety_threshold": 365},
        {"name": "Mì ăn liền Hảo Hảo", "unit": "Gói", "import_price": 3500, "expiry_days": 180, "safety_threshold": 90},
        {"name": "Dầu ăn Neptune", "unit": "Chai", "import_price": 48000, "expiry_days": 365, "safety_threshold": 180},
        {"name": "Tương ớt Chinsu", "unit": "Chai", "import_price": 22000, "expiry_days": 730, "safety_threshold": 365},
        {"name": "Bột ngọt Ajinomoto", "unit": "Gói", "import_price": 12000, "expiry_days": 730, "safety_threshold": 365},
    ],
    
    "Đồ uống": [
        {"name": "Coca Cola", "unit": "Lon", "import_price": 8000, "expiry_days": 180, "safety_threshold": 90},
        {"name": "Pepsi", "unit": "Lon", "import_price": 8000, "expiry_days": 180, "safety_threshold": 90},
        {"name": "Sting dâu", "unit": "Chai", "import_price": 7000, "expiry_days": 180, "safety_threshold": 90},
        {"name": "Nước suối Lavie", "unit": "Chai", "import_price": 3000, "expiry_days": 365, "safety_threshold": 180},
        {"name": "Trà xanh 0 độ", "unit": "Chai", "import_price": 6500, "expiry_days": 180, "safety_threshold": 90},
        {"name": "C2 chanh", "unit": "Chai", "import_price": 6500, "expiry_days": 180, "safety_threshold": 90},
        {"name": "Revive chanh muối", "unit": "Chai", "import_price": 7000, "expiry_days": 180, "safety_threshold": 90},
        {"name": "Cafe G7 3in1", "unit": "Hộp", "import_price": 75000, "expiry_days": 365, "safety_threshold": 180},
        {"name": "Number 1 chanh muối", "unit": "Chai", "import_price": 7500, "expiry_days": 180, "safety_threshold": 90},
        {"name": "Trà Olong Tea Plus", "unit": "Chai", "import_price": 6500, "expiry_days": 180, "safety_threshold": 90},
    ],
    
    "Điện tử": [
        {"name": "Tai nghe Sony WH-1000XM5", "unit": "Cái", "import_price": 6500000, "warranty_months": 12},
        {"name": "Loa JBL Flip 6", "unit": "Cái", "import_price": 2200000, "warranty_months": 12},
        {"name": "Chuột Logitech MX Master 3", "unit": "Cái", "import_price": 1800000, "warranty_months": 24},
        {"name": "Bàn phím cơ Logitech G Pro", "unit": "Cái", "import_price": 2500000, "warranty_months": 24},
        {"name": "USB Samsung 128GB", "unit": "Cái", "import_price": 250000, "warranty_months": 60},
        {"name": "SSD Samsung 1TB", "unit": "Cái", "import_price": 1800000, "warranty_months": 60},
        {"name": "Webcam Logitech C920", "unit": "Cái", "import_price": 1200000, "warranty_months": 24},
        {"name": "Sạc dự phòng Anker 20000mAh", "unit": "Cái", "import_price": 850000, "warranty_months": 18},
        {"name": "Cáp sạc Anker USB-C", "unit": "Sợi", "import_price": 180000, "warranty_months": 18},
        {"name": "Đèn LED Philips thông minh", "unit": "Bóng", "import_price": 180000, "warranty_months": 24},
        {"name": "Camera IP Xiaomi 360", "unit": "Cái", "import_price": 550000, "warranty_months": 12},
        {"name": "Ổ cứng di động WD 2TB", "unit": "Cái", "import_price": 1500000, "warranty_months": 36},
    ],
    
    "Gia dụng": [
        {"name": "Nồi cơm điện Panasonic 1.8L", "unit": "Cái", "import_price": 850000, "warranty_months": 12},
        {"name": "Bình đun siêu tốc Philips", "unit": "Cái", "import_price": 450000, "warranty_months": 24},
        {"name": "Quạt đứng Hatari", "unit": "Cái", "import_price": 650000, "warranty_months": 12},
        {"name": "Máy xay sinh tố Philips", "unit": "Cái", "import_price": 1200000, "warranty_months": 24},
        {"name": "Bàn ủi hơi nước Philips", "unit": "Cái", "import_price": 550000, "warranty_months": 24},
        {"name": "Máy hút bụi Electrolux", "unit": "Cái", "import_price": 2500000, "warranty_months": 24},
        {"name": "Nồi áp suất Sunhouse", "unit": "Cái", "import_price": 1200000, "warranty_months": 12},
        {"name": "Lò vi sóng Electrolux", "unit": "Cái", "import_price": 1800000, "warranty_months": 12},
        {"name": "Máy ép trái cây Philips", "unit": "Cái", "import_price": 1500000, "warranty_months": 24},
    ],
    
    "Chăm sóc cá nhân": [
        {"name": "Dầu gội Head & Shoulders", "unit": "Chai", "import_price": 95000, "expiry_days": 1095, "safety_threshold": 365},
        {"name": "Sữa tắm Dove", "unit": "Chai", "import_price": 85000, "expiry_days": 1095, "safety_threshold": 365},
        {"name": "Kem đánh răng Colgate", "unit": "Tuýp", "import_price": 28000, "expiry_days": 730, "safety_threshold": 365},
        {"name": "Bàn chải đánh răng Oral-B", "unit": "Cái", "import_price": 35000, "expiry_days": 1825, "safety_threshold": 365},
        {"name": "Dầu xả Sunsilk", "unit": "Chai", "import_price": 88000, "expiry_days": 1095, "safety_threshold": 365},
        {"name": "Băng vệ sinh Kotex", "unit": "Gói", "import_price": 35000, "expiry_days": 1095, "safety_threshold": 365},
        {"name": "Lăn khử mùi Rexona", "unit": "Chai", "import_price": 55000, "expiry_days": 730, "safety_threshold": 365},
        {"name": "Kem dưỡng da Nivea", "unit": "Hũ", "import_price": 75000, "expiry_days": 730, "safety_threshold": 365},
        {"name": "Nước rửa tay Lifebuoy", "unit": "Chai", "import_price": 42000, "expiry_days": 730, "safety_threshold": 365},
        {"name": "Khăn giấy Tempo", "unit": "Gói", "import_price": 18000, "expiry_days": 1095, "safety_threshold": 365},
    ],
}

SUPPLIER_DATA = {
    "farmers": [
        {"name": "HTX Rau sạch Đà Lạt", "address": "123 Đường Trần Phú, Đà Lạt, Lâm Đồng", "main_product": "Rau củ quả sạch"},
        {"name": "Trang trại hữu cơ Phú Yên", "address": "456 Quốc lộ 1A, Tuy Hòa, Phú Yên", "main_product": "Rau hữu cơ"},
        {"name": "Hợp tác xã Nông sản Bình Dương", "address": "789 Đường Mỹ Phước, Bình Dương", "main_product": "Trái cây tươi"},
        {"name": "Nông trại gà sạch Long An", "address": "321 Huyện Đức Hòa, Long An", "main_product": "Thịt gà, Trứng gà"},
        {"name": "Làng cá Cần Giờ", "address": "555 Xã Cần Thạnh, Cần Giờ, TP.HCM", "main_product": "Hải sản tươi sống"},
    ],
    "manufacturers": [
        {"name": "Sony Vietnam", "address": "Lô A1, KCN Biên Hòa 2, Đồng Nai", "cert": "ISO 9001:2015", "reg": "0312345678"},
        {"name": "Logitech Việt Nam", "address": "Tầng 15, Bitexco Tower, TP.HCM", "cert": "ISO 14001:2015", "reg": "0398765432"},
        {"name": "Samsung Electronics VN", "address": "KCN Yên Phong, Bắc Ninh", "cert": "ISO 9001:2015", "reg": "0287654321"},
        {"name": "Anker Technology VN", "address": "Lô B2, KCN VSIP, Bình Dương", "cert": "ISO 9001:2015", "reg": "0356789012"},
        {"name": "JBL Audio Vietnam", "address": "KCN Thăng Long, Hà Nội", "cert": "ISO 14001:2015", "reg": "0123456789"},
    ],
}

POSITIONS = [
    ("Quản lý cửa hàng", 18000000, 60000),
    ("Nhân viên bán hàng", 8500000, 30000), # Merged Thu ngân & Bán hàng
    ("Nhân viên kho", 9000000, 32000),
    ("Bảo vệ", 7500000, 25000),
]

CUSTOMER_TIERS = ['Thành viên', 'Bạc', 'Vàng', 'Kim cương']

def run_seeder():
    try:
        conn = get_connection()
        cursor = conn.cursor()
    except mysql.connector.Error as err:
        print(f"Lỗi kết nối CSDL: {err}")
        return
    
    print("=" * 60)
    print("BẮT ĐẦU SINH DỮ LIỆU MẪU CHO SIÊU THỊ")
    print("=" * 60)
    
    # Disable FK checks to allow truncation
    cursor.execute("SET FOREIGN_KEY_CHECKS = 0;")
    
    tables = [
        "INVOICE_DETAIL", "INVOICE", "DISPLAYS", "INVENTORY", "TIMEKEEPING",
        "SPECIAL_SUPPLY", "SUPPLIES", "ELECTRONIC_ITEM", "FOOD_ITEM", "PRODUCT",
        "SUPPLIER_PHONE", "INDUSTRIAL_MANUFACTURER", "LOCAL_FARMER", "SUPPLIER",
        "EMPLOYEE", "POSITION", "CUSTOMER", "COUNTER", "WAREHOUSE", "CATEGORY",
        "EVENT_PROMOTION", "MEMBERSHIP_BENEFIT", "EXPIRY_DISCOUNT",
        "EVENT_PROMOTION_PRODUCT", "MEMBERSHIP_BENEFIT_PROMOTION_PRODUCT"
    ]
    
    for table in tables:
        try:
            cursor.execute(f"TRUNCATE TABLE {table};")
        except mysql.connector.Error as err:
            print(f"Cảnh báo: Không thể xóa bảng {table}: {err}")
        
    cursor.execute("SET FOREIGN_KEY_CHECKS = 1;")
    conn.commit()
    
    # ============================================================
    # 1. CATEGORIES
    # ============================================================
    print("\n[1/10] Tạo Danh mục sản phẩm...")
    category_ids = {}
    for cat_name in PRODUCTS_BY_CATEGORY.keys():
        cursor.execute(
            "INSERT INTO CATEGORY (CategoryName, Description) VALUES (%s, %s)", 
            (cat_name, f"Các sản phẩm thuộc danh mục {cat_name}")
        )
        category_ids[cat_name] = cursor.lastrowid
    conn.commit()
    
    # ============================================================
    # 2. WAREHOUSES
    # ============================================================
    print("[2/10] Tạo Kho hàng...")
    cursor.execute(
        "INSERT INTO WAREHOUSE (WarehouseName, Address) VALUES (%s, %s)", 
        ("Kho Tổng Thủ Đức", "123 Đường Võ Văn Ngân, Thủ Đức, TP.HCM")
    )
    warehouse_id = cursor.lastrowid
    conn.commit()
    
    # ============================================================
    # 3. POSITIONS
    # ============================================================
    print("[3/10] Tạo Vị trí công việc...")
    position_ids = {}
    for pos_name, salary, rate in POSITIONS:
        cursor.execute(
            "INSERT INTO POSITION (PositionName, BaseSalary, HourlyRate) VALUES (%s, %s, %s)", 
            (pos_name, salary, rate)
        )
        position_ids[pos_name] = cursor.lastrowid
    conn.commit()
    
    # ============================================================
    # 4. COUNTERS
    # ============================================================
    print("[4/10] Tạo Quầy hàng...")
    counter_ids = {}
    for cat_name, cat_id in category_ids.items():
        cursor.execute(
            "INSERT INTO COUNTER (CounterName, CategoryID) VALUES (%s, %s)", 
            (f"Quầy {cat_name}", cat_id)
        )
        counter_ids[cat_name] = cursor.lastrowid
    conn.commit()
    
    # ============================================================
    # 5. SUPPLIERS
    # ============================================================
    print("[5/10] Tạo Nhà cung cấp...")
    farmer_ids = []
    manufacturer_ids = []
    
    # Local Farmers
    for farmer in SUPPLIER_DATA["farmers"]:
        cursor.execute(
            "INSERT INTO SUPPLIER (SupplierName, Address) VALUES (%s, %s)", 
            (farmer["name"], farmer["address"])
        )
        sid = cursor.lastrowid
        farmer_ids.append(sid)
        cursor.execute(
            "INSERT INTO LOCAL_FARMER (SupplierID, MainProduct) VALUES (%s, %s)", 
            (sid, farmer["main_product"])
        )
        # Phone
        cursor.execute(
            "INSERT INTO SUPPLIER_PHONE (SupplierID, Phone) VALUES (%s, %s)", 
            (sid, fake.phone_number()[:15])
        )
    
    # Industrial Manufacturers
    for mfr in SUPPLIER_DATA["manufacturers"]:
        cursor.execute(
            "INSERT INTO SUPPLIER (SupplierName, Address) VALUES (%s, %s)", 
            (mfr["name"], mfr["address"])
        )
        sid = cursor.lastrowid
        manufacturer_ids.append(sid)
        cursor.execute(
            "INSERT INTO INDUSTRIAL_MANUFACTURER (SupplierID, QualityCertification, BusinessRegistration) VALUES (%s, %s, %s)", 
            (sid, mfr["cert"], mfr["reg"])
        )
        cursor.execute(
            "INSERT INTO SUPPLIER_PHONE (SupplierID, Phone) VALUES (%s, %s)", 
            (sid, fake.phone_number()[:15])
        )
    conn.commit()
    
    # ============================================================
    # 6. EMPLOYEES
    # ============================================================
    print("[6/10] Tạo Nhân viên...")
    # Manager first
    cursor.execute(
        "INSERT INTO EMPLOYEE (FullName, DateOfBirth, Address, Phone, PositionID) VALUES (%s, %s, %s, %s, %s)",
        ("Nguyễn Văn An", date(1985, 5, 15), "456 Nguyễn Trãi, Quận 5, TP.HCM", "0901234567", position_ids["Quản lý cửa hàng"])
    )
    manager_id = cursor.lastrowid
    
    employee_ids = [manager_id]
    employee_names = [
        "Trần Thị Bình", "Lê Văn Cường", "Phạm Thị Dung", "Hoàng Văn Em",
        "Ngô Thị Phương", "Đỗ Văn Giang", "Vũ Thị Hoa", "Bùi Văn Inh", "Lý Thị Kim"
    ]
    other_positions = [p for p in position_ids.keys() if p != "Quản lý cửa hàng"]
    
    for name in employee_names:
        pos = random.choice(other_positions)
        cursor.execute(
            "INSERT INTO EMPLOYEE (FullName, DateOfBirth, Address, Phone, PositionID, ManagerID) VALUES (%s, %s, %s, %s, %s, %s)",
            (name, fake.date_of_birth(minimum_age=20, maximum_age=35), fake.address()[:200], fake.phone_number()[:15], position_ids[pos], manager_id)
        )
        employee_ids.append(cursor.lastrowid)
    conn.commit()
    
    # ============================================================
    # 7. CUSTOMERS (Tăng số lượng và đa dạng hóa hạng)
    # ============================================================
    print("[7/10] Tạo Khách hàng...")
    customer_ids = []
    # Tăng lên 150 khách hàng với phân bố hạng cân đối hơn
    for _ in range(150):
        tier = random.choices(CUSTOMER_TIERS, weights=[40, 30, 20, 10])[0]  # Cân đối hơn
        points = {"Thành viên": random.randint(0, 99), "Bạc": random.randint(100, 499), 
                  "Vàng": random.randint(500, 999), "Kim cương": random.randint(1000, 2500)}[tier]
        cursor.execute(
            "INSERT INTO CUSTOMER (FullName, Phone, Points, Tier) VALUES (%s, %s, %s, %s)", 
            (fake.name(), fake.phone_number()[:15], points, tier)
        )
        customer_ids.append(cursor.lastrowid)
    conn.commit()
    
    # ============================================================
    # 8. PRODUCTS
    # ============================================================
    print("[8/10] Tạo Sản phẩm...")
    product_ids = []
    food_product_ids = []
    electronic_product_ids = []
    
    for cat_name, products in PRODUCTS_BY_CATEGORY.items():
        cat_id = category_ids[cat_name]
        
        for prod in products:
            import_price = prod["import_price"]
            selling_price = round(import_price * random.uniform(1.2, 1.5), -3)  # 20-50% margin
            
            cursor.execute(
                "INSERT INTO PRODUCT (ProductName, ImportPrice, SellingPrice, Unit, CategoryID) VALUES (%s, %s, %s, %s, %s)",
                (prod["name"], import_price, selling_price, prod["unit"], cat_id)
            )
            pid = cursor.lastrowid
            product_ids.append(pid)
            
            # Food items
            if "expiry_days" in prod:
                cursor.execute(
                    "INSERT INTO FOOD_ITEM (ProductID, ExpiryDays, SafetyThreshold) VALUES (%s, %s, %s)",
                    (pid, prod["expiry_days"], prod.get("safety_threshold", 7))
                )
                food_product_ids.append(pid)
                
                # Link to farmer supplier via SPECIAL_SUPPLY
                if cat_name in ["Thực phẩm", "Đồ uống"]:
                    farmer_sid = random.choice(farmer_ids)
                    try:
                        cursor.execute(
                            "INSERT INTO SPECIAL_SUPPLY (SupplierID, ProductID) VALUES (%s, %s)",
                            (farmer_sid, pid)
                        )
                    except:
                        pass  # Ignore duplicate key
            
            # Electronic items
            elif "warranty_months" in prod:
                mfr_sid = random.choice(manufacturer_ids)
                cursor.execute(
                    "INSERT INTO ELECTRONIC_ITEM (ProductID, WarrantyMonths, SupplierID) VALUES (%s, %s, %s)",
                    (pid, prod["warranty_months"], mfr_sid)
                )
                electronic_product_ids.append(pid)
            
            # General supplies link
            supplier_id = random.choice(farmer_ids + manufacturer_ids)
            try:
                cursor.execute(
                    "INSERT INTO SUPPLIES (SupplierID, ProductID) VALUES (%s, %s)",
                    (supplier_id, pid)
                )
            except:
                pass
    conn.commit()
    
    # ============================================================
    # 9. PROMOTIONS
    # ============================================================
    print("[9/10] Tạo Khuyến mãi...")
    today = date.today()
    
    # Event Promotions
    events = [
        ("Khuyến mãi Tết Nguyên Đán", 20, "Tiền mặt", 500000, "Tết Nguyên Đán 2026"),
        ("Sale Black Friday", 30, None, 200000, "Black Friday"),
        ("Giảm giá Quốc khánh", 15, None, 100000, "Quốc khánh 2/9"),
    ]
    event_promo_ids = []
    for name, discount, payment, min_order, event_name in events:
        cursor.execute(
            """INSERT INTO EVENT_PROMOTION 
               (PromotionName, StartDate, EndDate, PaymentMethod, DiscountPercent, EventName, MinOrderValue) 
               VALUES (%s, %s, %s, %s, %s, %s, %s)""",
            (name, today - timedelta(days=10), today + timedelta(days=20), payment, discount, event_name, min_order)
        )
        event_promo_ids.append(cursor.lastrowid)
    
    # Membership Benefits
    memberships = [
        ("Ưu đãi Thành viên Vàng", 10, "Vàng"),
        ("Ưu đãi Thành viên Kim cương", 15, "Kim cương"),
    ]
    membership_promo_ids = []
    for name, discount, tier in memberships:
        cursor.execute(
            """INSERT INTO MEMBERSHIP_BENEFIT 
               (PromotionName, StartDate, EndDate, DiscountPercent, RequiredTier) 
               VALUES (%s, %s, %s, %s, %s)""",
            (name, today - timedelta(days=30), today + timedelta(days=60), discount, tier)
        )
        membership_promo_ids.append(cursor.lastrowid)
    
    # Expiry Discounts
    expiry_discounts = [
        ("Giảm giá đồ khô sắp hết hạn", 50, 5),
        ("Giảm giá rau củ sắp hết hạn", 50, 1),
        ("Giảm giá thịt sắp hết hạn", 40, 1),
    ]
    for name, discount, days_before in expiry_discounts:
        cursor.execute(
            """INSERT INTO EXPIRY_DISCOUNT 
               (PromotionName, StartDate, EndDate, DiscountPercent, DaysBeforeExpiry) 
               VALUES (%s, %s, %s, %s, %s)""",
            (name, today - timedelta(days=365), today + timedelta(days=365), discount, days_before)
        )
    
    # Link promotions to products
    for promo_id in event_promo_ids:
        for pid in random.sample(product_ids, min(10, len(product_ids))):
            try:
                cursor.execute(
                    "INSERT INTO EVENT_PROMOTION_PRODUCT (PromotionID, ProductID) VALUES (%s, %s)",
                    (promo_id, pid)
                )
            except:
                pass
    
    for promo_id in membership_promo_ids:
        for pid in random.sample(product_ids, min(15, len(product_ids))):
            try:
                cursor.execute(
                    "INSERT INTO MEMBERSHIP_BENEFIT_PROMOTION_PRODUCT (PromotionID, ProductID) VALUES (%s, %s)",
                    (promo_id, pid)
                )
            except:
                pass
    conn.commit()
    
    # ============================================================
    # 10. OPERATIONS (30 DAYS) - REALISTIC VOLUME
    # ============================================================
    print("[10/10] Sinh dữ liệu giao dịch 30 ngày (khối lượng lớn)...")
    start_date = today - timedelta(days=30)
    
    total_invoices_created = 0
    total_revenue_generated = 0
    
    for day_offset in range(31):
        current_date = start_date + timedelta(days=day_offset)
        is_weekend = current_date.weekday() >= 5  # Cuối tuần đông hơn
        
        # Import Inventory - nhiều hơn
        for _ in range(random.randint(10, 20)):
            prod_id = random.choice(product_ids)
            qty = random.randint(50, 200)
            cursor.execute(
                "INSERT INTO INVENTORY (ImportDate, Quantity, WarehouseID, ProductID) VALUES (%s, %s, %s, %s)",
                (current_date, qty, warehouse_id, prod_id)
            )
            inv_id = cursor.lastrowid
            
            # Transfer 60% to counter
            cursor.execute("SELECT CategoryID FROM PRODUCT WHERE ProductID = %s", (prod_id,))
            result = cursor.fetchone()
            if result:
                cat_id = result[0]
                cursor.execute("SELECT CounterID FROM COUNTER WHERE CategoryID = %s LIMIT 1", (cat_id,))
                counter_result = cursor.fetchone()
                if counter_result:
                    counter_id = counter_result[0]
                    # Ensure transfer_qty <= MaxQuantity (100)
                    max_display = 100
                    transfer_qty = min(int(qty * 0.5), max_display)
                    if transfer_qty > 0:
                        cursor.execute(
                            "UPDATE INVENTORY SET Quantity = Quantity - %s WHERE InventoryID = %s", 
                            (transfer_qty, inv_id)
                        )
                        cursor.execute(
                            """INSERT INTO DISPLAYS (InventoryID, CounterID, Position, MaxQuantity, CurrentQuantity) 
                               VALUES (%s, %s, %s, %s, %s)""",
                            (inv_id, counter_id, f"Kệ {random.choice(['A', 'B', 'C', 'D'])}{random.randint(1, 10)}", max_display, transfer_qty)
                        )
        
        # Timekeeping
        for emp_id in employee_ids:
            if random.random() < 0.92:  # 92% attendance
                hours = random.uniform(7, 10)
                cursor.execute(
                    "INSERT INTO TIMEKEEPING (Date, WorkHours, EmployeeID) VALUES (%s, %s, %s)",
                    (current_date, round(hours, 1), emp_id)
                )
        
        # Create Invoices - MODERATE (giảm xuống cho demo hợp lý)
        # DEMO: ~30-50 hóa đơn/ngày (hợp lý hơn cho báo cáo)
        # Cuối tuần đông hơn 50%
        base_invoices = random.randint(30, 50)
        num_invoices = int(base_invoices * 1.5) if is_weekend else base_invoices
        
        # Get Sales Staff IDs only
        cursor.execute("""
            SELECT E.EmployeeID 
            FROM EMPLOYEE E 
            JOIN POSITION P ON E.PositionID = P.PositionID 
            WHERE P.PositionName = 'Nhân viên bán hàng'
        """)
        sales_staff_ids = [row[0] for row in cursor.fetchall()]

        if not sales_staff_ids:
            # Fallback if no sales staff (shouldn't happen)
            sales_staff_ids = employee_ids

        for _ in range(num_invoices):
            cust_id = random.choice(customer_ids)
            emp_id = random.choice(sales_staff_ids) # Only Sales Staff make invoices
            payment = random.choices(
                ['Tiền mặt', 'Thẻ', 'QR Code', 'Ví điện tử'],
                weights=[40, 25, 25, 10]  # Tiền mặt phổ biến nhất
            )[0]
            
            cursor.execute(
                "INSERT INTO INVOICE (CreatedAt, PaymentMethod, TotalAmount, EmployeeID, CustomerID) VALUES (%s, %s, 0, %s, %s)",
                (current_date, payment, emp_id, cust_id)
            )
            invoice_id = cursor.lastrowid
            total_invoices_created += 1
            
            total_amount = 0
            # Mỗi hóa đơn có 3-12 sản phẩm (thực tế hơn)
            num_items = random.randint(3, 12)
            chosen_products = random.sample(product_ids, min(num_items, len(product_ids)))
            
            for pid in chosen_products:
                # Số lượng mỗi sản phẩm: 1-8 (mua nhiều hơn cho thực phẩm)
                qty = random.choices(
                    [1, 2, 3, 4, 5, 6, 7, 8],
                    weights=[20, 30, 20, 15, 8, 4, 2, 1]  # 1-2 phổ biến nhất
                )[0]
                
                cursor.execute("SELECT SellingPrice FROM PRODUCT WHERE ProductID = %s", (pid,))
                price_result = cursor.fetchone()
                if price_result:
                    price = price_result[0]
                    try:
                        cursor.execute(
                            "INSERT INTO INVOICE_DETAIL (InvoiceID, ProductID, Quantity, SellingPrice) VALUES (%s, %s, %s, %s)",
                            (invoice_id, pid, qty, price)
                        )
                        total_amount += float(price) * qty
                    except:
                        pass  # Skip duplicate
            
            cursor.execute("UPDATE INVOICE SET TotalAmount = %s WHERE InvoiceID = %s", (total_amount, invoice_id))
            total_revenue_generated += total_amount
        
        # Commit mỗi ngày để tránh transaction quá lớn
        if day_offset % 5 == 0:
            conn.commit()
            print(f"   ... Đã xử lý {day_offset + 1}/31 ngày")
    
    conn.commit()
    
    print("\n" + "=" * 60)
    print("HOÀN TẤT SINH DỮ LIỆU THÀNH CÔNG!")
    print("=" * 60)
    print(f"- Danh mục: {len(category_ids)}")
    print(f"- Sản phẩm: {len(product_ids)} (Thực phẩm: {len(food_product_ids)}, Điện tử: {len(electronic_product_ids)})")
    print(f"- Nhà cung cấp: {len(farmer_ids) + len(manufacturer_ids)}")
    print(f"- Nhân viên: {len(employee_ids)}")
    print(f"- Khách hàng: {len(customer_ids)}")
    print(f"- Hóa đơn: {total_invoices_created:,}")
    print(f"- Tổng doanh thu: {total_revenue_generated:,.0f} VND")
    print("- Dữ liệu giao dịch: 30 ngày")
    print("=" * 60)
    
    conn.close()

if __name__ == "__main__":
    run_seeder()
