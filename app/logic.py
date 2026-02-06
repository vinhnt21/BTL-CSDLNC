from app.database import execute_query, get_connection
import mysql.connector

# --- Database Statistics ---
def get_database_statistics():
    """Get row count statistics for all main tables"""
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Vietnamese names mapping
    table_names_vn = {
        "CATEGORY": "Danh mục",
        "PRODUCT": "Sản phẩm",
        "SUPPLIER": "Nhà cung cấp",
        "WAREHOUSE": "Kho hàng",
        "COUNTER": "Quầy hàng",
        "EMPLOYEE": "Nhân viên",
        "CUSTOMER": "Khách hàng",
        "POSITION": "Vị trí / Chức vụ",
        "INVENTORY": "Lô hàng / Tồn kho",
        "DISPLAYS": "Trưng bày",
        "TIMEKEEPING": "Chấm công",
        "INVOICE": "Hóa đơn",
        "INVOICE_DETAIL": "Chi tiết hóa đơn",
        "FOOD_ITEM": "Thực phẩm",
        "ELECTRONIC_ITEM": "Điện tử",
        "LOCAL_FARMER": "Nông dân địa phương",
        "INDUSTRIAL_MANUFACTURER": "Nhà sản xuất công nghiệp"
    }
    
    tables = [
        "CATEGORY", "PRODUCT", "SUPPLIER", "WAREHOUSE", "COUNTER",
        "EMPLOYEE", "CUSTOMER", "POSITION", "INVENTORY", "DISPLAYS",
        "TIMEKEEPING", "INVOICE", "INVOICE_DETAIL", "FOOD_ITEM", "ELECTRONIC_ITEM",
        "LOCAL_FARMER", "INDUSTRIAL_MANUFACTURER"
    ]
    
    stats = []
    for table in tables:
        try:
            cursor.execute(f"SELECT COUNT(*) as count FROM {table}")
            count = cursor.fetchone()['count']
            stats.append({
                "Bảng": table, 
                "Tên bảng": table_names_vn.get(table, table),
                "Số bản ghi": count
            })
        except:
            pass
    
    cursor.close()
    conn.close()
    return stats

# --- Dashboard Queries ---
def get_daily_revenue_last_30_days():
    query = """
    SELECT 
        DATE(CreatedAt) as Date, 
        SUM(TotalAmount) as Revenue 
    FROM INVOICE 
    WHERE CreatedAt >= DATE_SUB(CURDATE(), INTERVAL 30 DAY)
    GROUP BY DATE(CreatedAt)
    ORDER BY Date;
    """
    return execute_query(query, fetch=True)

def get_top_selling_products(limit=10):
    query = """
    SELECT 
        P.ProductName, 
        SUM(ID.Quantity) as TotalQuantity,
        SUM(ID.Quantity * ID.SellingPrice) as TotalRevenue
    FROM INVOICE_DETAIL ID
    JOIN PRODUCT P ON ID.ProductID = P.ProductID
    JOIN INVOICE I ON ID.InvoiceID = I.InvoiceID
    WHERE I.CreatedAt >= DATE_SUB(CURDATE(), INTERVAL 30 DAY)
    GROUP BY P.ProductID, P.ProductName
    ORDER BY TotalQuantity DESC
    LIMIT %s;
    """
    return execute_query(query, (limit,), fetch=True)

# --- Product & Inventory Queries ---
def get_all_products_with_stock():
    query = """
    SELECT 
        P.ProductID, 
        P.ProductName, 
        P.SellingPrice, 
        P.Unit,
        C.CategoryName,
        IFNULL(SUM(I.Quantity), 0) as WarehouseStock
    FROM PRODUCT P
    LEFT JOIN INVENTORY I ON P.ProductID = I.ProductID
    JOIN CATEGORY C ON P.CategoryID = C.CategoryID
    GROUP BY P.ProductID, P.ProductName, P.SellingPrice, P.Unit, C.CategoryName
    LIMIT 100;
    """
    return execute_query(query, fetch=True)

def search_products(keyword):
    search_term = f"%{keyword}%"
    query = """
    SELECT 
        P.ProductID, 
        P.ProductName, 
        P.SellingPrice, 
        P.Unit,
        C.CategoryName
    FROM PRODUCT P
    JOIN CATEGORY C ON P.CategoryID = C.CategoryID
    WHERE P.ProductName LIKE %s OR C.CategoryName LIKE %s
    LIMIT 20;
    """
    return execute_query(query, (search_term, search_term), fetch=True)

def get_product_by_id(product_id):
    query = "SELECT * FROM PRODUCT WHERE ProductID = %s"
    return execute_query(query, (product_id,), fetch_one=True)

def get_all_categories():
    query = "SELECT CategoryID, CategoryName FROM CATEGORY ORDER BY CategoryName"
    return execute_query(query, fetch=True)

# ============================================================
# CRUD OPERATIONS
# ============================================================

# --- Product CRUD ---
def create_product(name, import_price, selling_price, unit, category_id):
    query = """
    INSERT INTO PRODUCT (ProductName, ImportPrice, SellingPrice, Unit, CategoryID) 
    VALUES (%s, %s, %s, %s, %s)
    """
    return execute_query(query, (name, import_price, selling_price, unit, category_id))

def update_product(product_id, name, import_price, selling_price, unit, category_id):
    query = """
    UPDATE PRODUCT 
    SET ProductName=%s, ImportPrice=%s, SellingPrice=%s, Unit=%s, CategoryID=%s 
    WHERE ProductID=%s
    """
    return execute_query(query, (name, import_price, selling_price, unit, category_id, product_id))

def delete_product(product_id):
    query = "DELETE FROM PRODUCT WHERE ProductID = %s"
    return execute_query(query, (product_id,))

# --- Customer CRUD ---
def create_customer(fullname, phone, tier="Thành viên"):
    query = "INSERT INTO CUSTOMER (FullName, Phone, Tier) VALUES (%s, %s, %s)"
    return execute_query(query, (fullname, phone, tier))

def update_customer(customer_id, fullname, phone, tier):
    query = "UPDATE CUSTOMER SET FullName=%s, Phone=%s, Tier=%s WHERE CustomerID=%s"
    return execute_query(query, (fullname, phone, tier, customer_id))

def delete_customer(customer_id):
    query = "DELETE FROM CUSTOMER WHERE CustomerID = %s"
    return execute_query(query, (customer_id,))

def search_customers(keyword):
    search_term = f"%{keyword}%"
    query = "SELECT * FROM CUSTOMER WHERE FullName LIKE %s OR Phone LIKE %s LIMIT 50"
    return execute_query(query, (search_term, search_term), fetch=True)

def get_customer_by_id(customer_id):
    query = "SELECT * FROM CUSTOMER WHERE CustomerID = %s"
    return execute_query(query, (customer_id,), fetch_one=True)

# --- Employee CRUD ---
def create_employee(fullname, dob, address, phone, position_id, manager_id=None):
    query = """
    INSERT INTO EMPLOYEE (FullName, DateOfBirth, Address, Phone, PositionID, ManagerID) 
    VALUES (%s, %s, %s, %s, %s, %s)
    """
    return execute_query(query, (fullname, dob, address, phone, position_id, manager_id))

def update_employee(employee_id, fullname, dob, address, phone, position_id, manager_id=None):
    query = """
    UPDATE EMPLOYEE 
    SET FullName=%s, DateOfBirth=%s, Address=%s, Phone=%s, PositionID=%s, ManagerID=%s 
    WHERE EmployeeID=%s
    """
    return execute_query(query, (fullname, dob, address, phone, position_id, manager_id, employee_id))

def delete_employee(employee_id):
    query = "DELETE FROM EMPLOYEE WHERE EmployeeID = %s"
    return execute_query(query, (employee_id,))

def search_employees(keyword):
    search_term = f"%{keyword}%"
    query = """
    SELECT E.*, P.PositionName 
    FROM EMPLOYEE E 
    JOIN POSITION P ON E.PositionID = P.PositionID
    WHERE E.FullName LIKE %s LIMIT 50
    """
    return execute_query(query, (search_term,), fetch=True)

def get_employee_by_id(employee_id):
    query = """
    SELECT E.*, P.PositionName 
    FROM EMPLOYEE E 
    JOIN POSITION P ON E.PositionID = P.PositionID
    WHERE E.EmployeeID = %s
    """
    return execute_query(query, (employee_id,), fetch_one=True)

def get_all_positions():
    query = "SELECT PositionID, PositionName, BaseSalary, HourlyRate FROM POSITION"
    return execute_query(query, fetch=True)

# --- Supplier CRUD ---
def create_supplier(name, address):
    query = "INSERT INTO SUPPLIER (SupplierName, Address) VALUES (%s, %s)"
    return execute_query(query, (name, address))

def update_supplier(supplier_id, name, address):
    query = "UPDATE SUPPLIER SET SupplierName=%s, Address=%s WHERE SupplierID=%s"
    return execute_query(query, (name, address, supplier_id))

def delete_supplier(supplier_id):
    query = "DELETE FROM SUPPLIER WHERE SupplierID = %s"
    return execute_query(query, (supplier_id,))

def get_all_suppliers():
    query = "SELECT * FROM SUPPLIER LIMIT 50"
    return execute_query(query, fetch=True)

def get_supplier_by_id(supplier_id):
    query = "SELECT * FROM SUPPLIER WHERE SupplierID = %s"
    return execute_query(query, (supplier_id,), fetch_one=True)

# ============================================================
# INVENTORY & COUNTER OPERATIONS
# ============================================================

def get_products_in_warehouse(product_id=None):
    if product_id:
        query = "SELECT SUM(Quantity) as qty FROM INVENTORY WHERE ProductID = %s"
        res = execute_query(query, (product_id,), fetch_one=True)
        return res['qty'] if res and res['qty'] else 0
    else:
        query = """
        SELECT I.InventoryID, P.ProductID, P.ProductName, I.Quantity, I.ImportDate 
        FROM INVENTORY I JOIN PRODUCT P ON I.ProductID = P.ProductID 
        WHERE I.Quantity > 0 ORDER BY I.ImportDate ASC
        """
        return execute_query(query, fetch=True)

def get_all_counters():
    query = """
    SELECT C.CounterID, C.CounterName, CAT.CategoryName 
    FROM COUNTER C 
    JOIN CATEGORY CAT ON C.CategoryID = CAT.CategoryID
    """
    return execute_query(query, fetch=True)

def call_stored_procedure(proc_name, args):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        result_args = cursor.callproc(proc_name, args)
        
        # Determine if we need to fetch result sets or just output parameters
        # For simplicity and specific SP usage:
        # sp_calculate_employee_salary has OUT param as last arg. 
        # cursor.callproc returns the modified sequence of arguments.
        
        conn.commit()
        return result_args
    except mysql.connector.Error as err:
        print(f"Error calling {proc_name}: {err}")
        raise err # Re-raise to handle in UI
    finally:
        cursor.close()
        conn.close()

# --- Transfer Inventory ---
def transfer_inventory(inventory_id, counter_id, quantity, position):
    """
    Calls Stored Procedure sp_transfer_to_counter
    """
    try:
        # Note: sp_transfer_to_counter(inv_id, counter_id, qty, pos)
        # Báo cáo SP signature: (p_inventory_id, p_counter_id, p_product_id?? No, checked SQL)
        # My generated SQL: sp_transfer_to_counter(inventory_id, counter_id, quantity, position)
        call_stored_procedure('sp_transfer_to_counter', [inventory_id, counter_id, quantity, position])
        return True, "Chuyển hàng thành công!"
    except Exception as e:
        return False, f"Lỗi: {e}"

# --- Salary Calculation ---
def calculate_employee_salary(employee_id, month, year):
    """
    Calls sp_calculate_employee_salary
    """
    try:
        # Args: (emp_id, month, year, out_salary)
        # Note: input 0 for OUT param placeholder
        args = [employee_id, month, year, 0] 
        result = call_stored_procedure('sp_calculate_employee_salary', args)
        # result[3] is the p_total_salary
        return result[3] if result else 0
    except Exception as e:
        print(f"Salary calc error: {e}")
        return None

def update_stock_after_sale(product_id, quantity_sold):
    """Trừ hàng trên quầy sau khi bán"""
    query_find = """
    SELECT D.CounterID, D.InventoryID, D.CurrentQuantity 
    FROM DISPLAYS D
    JOIN INVENTORY I ON D.InventoryID = I.InventoryID
    WHERE I.ProductID = %s AND D.CurrentQuantity > 0
    ORDER BY D.CurrentQuantity DESC
    """
    counters = execute_query(query_find, (product_id,), fetch=True)
    
    remaining_to_deduct = quantity_sold
    
    if not counters:
        return False
        
    for c in counters:
        if remaining_to_deduct <= 0:
            break
        
        deduct = min(c['CurrentQuantity'], remaining_to_deduct)
        execute_query("UPDATE DISPLAYS SET CurrentQuantity = CurrentQuantity - %s WHERE CounterID = %s AND InventoryID = %s",
                      (deduct, c['CounterID'], c['InventoryID']))
        remaining_to_deduct -= deduct
        
    return True

# ============================================================
# INVENTORY REPORTS
# ============================================================

def get_low_stock_on_counter(threshold=5):
    """Hàng sắp hết trên quầy"""
    query = """
    SELECT D.CounterID, C.CounterName, P.ProductName, D.CurrentQuantity
    FROM DISPLAYS D
    JOIN INVENTORY I ON D.InventoryID = I.InventoryID
    JOIN PRODUCT P ON I.ProductID = P.ProductID
    JOIN COUNTER C ON D.CounterID = C.CounterID
    WHERE D.CurrentQuantity < %s AND D.CurrentQuantity > 0
    """
    return execute_query(query, (threshold,), fetch=True)

def get_products_need_refill(threshold=10):
    """Hàng sắp hết trên quầy NHƯNG vẫn còn trong kho (cần bổ sung)"""
    query = """
    SELECT 
        P.ProductID,
        P.ProductName, 
        IFNULL(SUM(D.CurrentQuantity), 0) as OnCounter,
        IFNULL(SUM(I.Quantity), 0) as InWarehouse,
        C.CounterName
    FROM PRODUCT P
    LEFT JOIN INVENTORY I ON P.ProductID = I.ProductID
    LEFT JOIN DISPLAYS D ON I.InventoryID = D.InventoryID
    LEFT JOIN COUNTER C ON D.CounterID = C.CounterID
    WHERE D.CurrentQuantity IS NOT NULL
    GROUP BY P.ProductID, P.ProductName, C.CounterName
    HAVING OnCounter < %s AND InWarehouse > 0
    ORDER BY OnCounter ASC
    """
    return execute_query(query, (threshold,), fetch=True)

def get_out_of_stock_warehouse_but_avail_counter():
    """Hết trong kho nhưng còn trên quầy"""
    query = """
    SELECT DISTINCT P.ProductID, P.ProductName, SUM(D.CurrentQuantity) as OnCounter
    FROM DISPLAYS D
    JOIN INVENTORY I_disp ON D.InventoryID = I_disp.InventoryID
    JOIN PRODUCT P ON I_disp.ProductID = P.ProductID
    WHERE D.CurrentQuantity > 0 
    AND NOT EXISTS (
        SELECT 1 FROM INVENTORY I_wh 
        WHERE I_wh.ProductID = P.ProductID AND I_wh.Quantity > 0
    )
    GROUP BY P.ProductID, P.ProductName
    """
    return execute_query(query, fetch=True)

def get_total_stock_all():
    """Tổng tồn kho (Quầy + Kho), sắp xếp tăng dần"""
    query = """
    SELECT 
        P.ProductID,
        P.ProductName,
        C.CategoryName,
        IFNULL(SUM(I.Quantity), 0) as WarehouseQty,
        IFNULL((
            SELECT SUM(D2.CurrentQuantity) 
            FROM DISPLAYS D2 
            JOIN INVENTORY I2 ON D2.InventoryID = I2.InventoryID 
            WHERE I2.ProductID = P.ProductID
        ), 0) as CounterQty,
        (IFNULL(SUM(I.Quantity), 0) + IFNULL((
            SELECT SUM(D2.CurrentQuantity) 
            FROM DISPLAYS D2 
            JOIN INVENTORY I2 ON D2.InventoryID = I2.InventoryID 
            WHERE I2.ProductID = P.ProductID
        ), 0)) as TotalStock
    FROM PRODUCT P
    LEFT JOIN INVENTORY I ON P.ProductID = I.ProductID
    LEFT JOIN CATEGORY C ON P.CategoryID = C.CategoryID
    GROUP BY P.ProductID, P.ProductName, C.CategoryName
    ORDER BY TotalStock ASC
    """
    return execute_query(query, fetch=True)

def get_products_by_category_sorted(category_id=None, counter_id=None, sort_by='stock'):
    """Liệt kê hàng theo chủng loại/quầy, sắp xếp theo tồn kho hoặc lượng bán trong ngày"""
    
    if sort_by == 'daily_sales':
        query = """
        SELECT 
            P.ProductID, P.ProductName, 
            IFNULL(SUM(D.CurrentQuantity), 0) as CurrentStock,
            IFNULL((
                SELECT SUM(ID.Quantity) 
                FROM INVOICE_DETAIL ID 
                JOIN INVOICE INV ON ID.InvoiceID = INV.InvoiceID 
                WHERE ID.ProductID = P.ProductID AND DATE(INV.CreatedAt) = CURDATE()
            ), 0) as SoldToday
        FROM PRODUCT P
        LEFT JOIN INVENTORY I ON P.ProductID = I.ProductID
        LEFT JOIN DISPLAYS D ON I.InventoryID = D.InventoryID
        WHERE (%s IS NULL OR P.CategoryID = %s)
          AND (%s IS NULL OR D.CounterID = %s)
        GROUP BY P.ProductID, P.ProductName
        ORDER BY SoldToday DESC
        """
    else:
        query = """
        SELECT 
            P.ProductID, P.ProductName, 
            IFNULL(SUM(D.CurrentQuantity), 0) as CurrentStock
        FROM PRODUCT P
        LEFT JOIN INVENTORY I ON P.ProductID = I.ProductID
        LEFT JOIN DISPLAYS D ON I.InventoryID = D.InventoryID
        WHERE (%s IS NULL OR P.CategoryID = %s)
          AND (%s IS NULL OR D.CounterID = %s)
        GROUP BY P.ProductID, P.ProductName
        ORDER BY CurrentStock ASC
        """
    
    return execute_query(query, (category_id, category_id, counter_id, counter_id), fetch=True)

# ============================================================
# EXPIRY & DISCOUNT
# ============================================================

def get_near_expiry_products(days_threshold=10):
    """Hàng sắp hết hạn (thực phẩm)"""
    query = """
    SELECT 
        P.ProductID,
        P.ProductName, 
        I.ImportDate, 
        F.ExpiryDays, 
        DATEDIFF(NOW(), I.ImportDate) as DaysSinceImport,
        (F.ExpiryDays - DATEDIFF(NOW(), I.ImportDate)) as DaysRemaining
    FROM INVENTORY I
    JOIN PRODUCT P ON I.ProductID = P.ProductID
    JOIN FOOD_ITEM F ON P.ProductID = F.ProductID
    WHERE (F.ExpiryDays - DATEDIFF(NOW(), I.ImportDate)) BETWEEN 0 AND %s
      AND I.Quantity > 0
    ORDER BY DaysRemaining ASC
    """
    return execute_query(query, (days_threshold,), fetch=True)

def get_expired_products():
    """Hàng đã quá hạn bán (DaysRemaining < 0)"""
    query = """
    SELECT 
        P.ProductID,
        P.ProductName, 
        I.ImportDate, 
        F.ExpiryDays, 
        (F.ExpiryDays - DATEDIFF(NOW(), I.ImportDate)) as DaysRemaining,
        I.Quantity as WarehouseQty
    FROM INVENTORY I
    JOIN PRODUCT P ON I.ProductID = P.ProductID
    JOIN FOOD_ITEM F ON P.ProductID = F.ProductID
    WHERE (F.ExpiryDays - DATEDIFF(NOW(), I.ImportDate)) < 0
      AND I.Quantity > 0
    ORDER BY DaysRemaining ASC
    """
    return execute_query(query, fetch=True)

def get_products_for_auto_discount():
    """Lấy danh sách hàng cần giảm giá tự động theo quy tắc:
    - Đồ khô (SafetyThreshold cao, VD: 180 ngày): còn dưới 5 ngày -> giảm 50%
    - Rau quả (SafetyThreshold thấp, VD: 7 ngày): còn dưới 1 ngày -> giảm 50%
    """
    query = """
    SELECT 
        P.ProductID,
        P.ProductName,
        P.SellingPrice,
        F.ExpiryDays,
        F.SafetyThreshold,
        I.ImportDate,
        (F.ExpiryDays - DATEDIFF(NOW(), I.ImportDate)) as DaysRemaining,
        CASE 
            WHEN F.SafetyThreshold IS NULL OR F.SafetyThreshold >= 30 THEN 
                CASE WHEN (F.ExpiryDays - DATEDIFF(NOW(), I.ImportDate)) < 5 THEN 50 ELSE 0 END
            ELSE 
                CASE WHEN (F.ExpiryDays - DATEDIFF(NOW(), I.ImportDate)) < 1 THEN 50 ELSE 0 END
        END as SuggestedDiscount
    FROM INVENTORY I
    JOIN PRODUCT P ON I.ProductID = P.ProductID
    JOIN FOOD_ITEM F ON P.ProductID = F.ProductID
    WHERE I.Quantity > 0
    HAVING SuggestedDiscount > 0
    ORDER BY DaysRemaining ASC
    """
    return execute_query(query, fetch=True)

def apply_discount_near_expiry(product_id, discount_percent):
    """Áp dụng giảm giá cho sản phẩm"""
    query = "UPDATE PRODUCT SET SellingPrice = SellingPrice * (1 - %s/100) WHERE ProductID = %s"
    return execute_query(query, (discount_percent, product_id))

# ============================================================
# REVENUE REPORTS
# ============================================================

def get_product_rankings_by_revenue_month(month, year):
    """Xếp hạng sản phẩm theo doanh thu trong tháng"""
    query = """
    SELECT P.ProductID, P.ProductName, SUM(ID.Quantity * ID.SellingPrice) as Revenue
    FROM INVOICE_DETAIL ID
    JOIN INVOICE I ON ID.InvoiceID = I.InvoiceID
    JOIN PRODUCT P ON ID.ProductID = P.ProductID
    WHERE MONTH(I.CreatedAt) = %s AND YEAR(I.CreatedAt) = %s
    GROUP BY P.ProductID, P.ProductName
    ORDER BY Revenue DESC
    """
    return execute_query(query, (month, year), fetch=True)

# ============================================================
# RANKINGS
# ============================================================

def get_customer_rankings():
    """Xếp hạng khách hàng theo tổng chi tiêu"""
    query = """
    SELECT C.CustomerID, C.FullName, C.Tier, C.Points, SUM(I.TotalAmount) as TotalSpent
    FROM CUSTOMER C
    JOIN INVOICE I ON C.CustomerID = I.CustomerID
    GROUP BY C.CustomerID, C.FullName, C.Tier, C.Points
    ORDER BY TotalSpent DESC
    LIMIT 20
    """
    return execute_query(query, fetch=True)

def get_employee_rankings_by_month(month, year):
    """Xếp hạng nhân viên bán hàng theo doanh số trong tháng"""
    query = """
    SELECT E.EmployeeID, E.FullName, P.PositionName, SUM(I.TotalAmount) as TotalSales
    FROM EMPLOYEE E
    JOIN POSITION P ON E.PositionID = P.PositionID
    JOIN INVOICE I ON E.EmployeeID = I.EmployeeID
    WHERE MONTH(I.CreatedAt) = %s AND YEAR(I.CreatedAt) = %s
    AND P.PositionName IN ('Nhân viên bán hàng', 'Thu ngân')
    GROUP BY E.EmployeeID, E.FullName, P.PositionName
    ORDER BY TotalSales DESC
    """
    return execute_query(query, (month, year), fetch=True)

def get_supplier_rankings():
    """Xếp hạng NCC theo giá trị hàng đang có (qua ELECTRONIC_ITEM)"""
    query = """
    SELECT S.SupplierID, S.SupplierName, S.TotalRevenue,
           SUM(P.ImportPrice * I.Quantity) as CurrentStockValue
    FROM SUPPLIER S
    JOIN ELECTRONIC_ITEM EI ON S.SupplierID = EI.SupplierID
    JOIN PRODUCT P ON EI.ProductID = P.ProductID
    JOIN INVENTORY I ON P.ProductID = I.ProductID
    GROUP BY S.SupplierID, S.SupplierName, S.TotalRevenue
    ORDER BY CurrentStockValue DESC
    """
    return execute_query(query, fetch=True)

def get_supplier_rankings_by_sales():
    """Xếp hạng NCC theo doanh thu hàng bán được (qua INVOICE_DETAIL)"""
    query = """
    SELECT S.SupplierID, S.SupplierName, 
           SUM(ID.Quantity * ID.SellingPrice) as TotalSalesRevenue
    FROM SUPPLIER S
    JOIN ELECTRONIC_ITEM EI ON S.SupplierID = EI.SupplierID
    JOIN PRODUCT P ON EI.ProductID = P.ProductID
    JOIN INVOICE_DETAIL ID ON P.ProductID = ID.ProductID
    GROUP BY S.SupplierID, S.SupplierName
    ORDER BY TotalSalesRevenue DESC
    """
    return execute_query(query, fetch=True)

# ============================================================
# POS (Point of Sale)
# ============================================================

def create_invoice(customer_id, employee_id, payment_method, total_amount):
    query = """
    INSERT INTO INVOICE (CustomerID, EmployeeID, PaymentMethod, TotalAmount, CreatedAt)
    VALUES (%s, %s, %s, %s, NOW())
    """
    return execute_query(query, (customer_id, employee_id, payment_method, total_amount))

def add_invoice_detail(invoice_id, product_id, quantity, selling_price):
    query = """
    INSERT INTO INVOICE_DETAIL (InvoiceID, ProductID, Quantity, SellingPrice)
    VALUES (%s, %s, %s, %s)
    """
    return execute_query(query, (invoice_id, product_id, quantity, selling_price))

def get_random_customer():
    query = "SELECT CustomerID, FullName, Phone, Tier FROM CUSTOMER ORDER BY RAND() LIMIT 1"
    return execute_query(query, fetch_one=True)

def get_random_employee():
    """Chỉ lấy nhân viên bán hàng/thu ngân cho POS"""
    query = """
    SELECT E.EmployeeID, E.FullName 
    FROM EMPLOYEE E 
    JOIN POSITION P ON E.PositionID = P.PositionID
    WHERE P.PositionName IN ('Nhân viên bán hàng', 'Thu ngân')
    ORDER BY RAND() LIMIT 1
    """
    return execute_query(query, fetch_one=True)

