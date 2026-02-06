-- 1. Tạo CSDL và thiết lập charset
CREATE DATABASE IF NOT EXISTS SupermarketManagement CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE SupermarketManagement;

-- =================================================================
-- PHẦN 1: CÁC BẢNG DANH MỤC & ĐỐI TƯỢNG ĐỘC LẬP
-- =================================================================

-- 1. Bảng Chủng loại hàng hóa (CATEGORY)
CREATE TABLE CATEGORY (
    CategoryID INT AUTO_INCREMENT PRIMARY KEY,
    CategoryName VARCHAR(100) NOT NULL,
    Description TEXT
);

-- 2. Bảng Kho hàng (WAREHOUSE)
CREATE TABLE WAREHOUSE (
    WarehouseID INT AUTO_INCREMENT PRIMARY KEY,
    WarehouseName VARCHAR(100) NOT NULL,
    Address VARCHAR(255) NOT NULL
);

-- 3. Bảng Vị trí công việc (POSITION)
-- (Tách từ EMPLOYEE để đạt chuẩn BCNF theo báo cáo)
CREATE TABLE POSITION (
    PositionID INT AUTO_INCREMENT PRIMARY KEY,
    PositionName VARCHAR(50) NOT NULL,
    BaseSalary DECIMAL(15, 2) NOT NULL CHECK (BaseSalary > 0),
    HourlyRate DECIMAL(15, 2) NOT NULL CHECK (HourlyRate > 0)
);

-- 4. Bảng Nhà cung cấp (SUPPLIER - Lớp cha)
CREATE TABLE SUPPLIER (
    SupplierID INT AUTO_INCREMENT PRIMARY KEY,
    SupplierName VARCHAR(100) NOT NULL,
    Address VARCHAR(255),
    TotalRevenue DECIMAL(15, 2) DEFAULT 0
);

-- 5. Bảng Khách hàng (CUSTOMER)
CREATE TABLE CUSTOMER (
    CustomerID INT AUTO_INCREMENT PRIMARY KEY,
    FullName VARCHAR(100) NOT NULL,
    Phone VARCHAR(15) UNIQUE,
    Points INT DEFAULT 0,
    Tier VARCHAR(20) DEFAULT 'Member' -- Hạng thành viên (Member, Silver, Gold...)
);

-- =================================================================
-- PHẦN 2: CÁC BẢNG LIÊN KẾT CẤP 1 (Có khóa ngoại)
-- =================================================================

-- 6. Bảng Quầy hàng (COUNTER)
CREATE TABLE COUNTER (
    CounterID INT AUTO_INCREMENT PRIMARY KEY,
    CounterName VARCHAR(50) NOT NULL,
    CategoryID INT NOT NULL, -- Mỗi quầy chỉ bán 1 loại hàng
    FOREIGN KEY (CategoryID) REFERENCES CATEGORY(CategoryID)
);

-- 7. Bảng Sản phẩm (PRODUCT - Lớp cha)
CREATE TABLE PRODUCT (
    ProductID INT AUTO_INCREMENT PRIMARY KEY,
    ProductName VARCHAR(150) NOT NULL,
    ImportPrice DECIMAL(15, 2) NOT NULL CHECK (ImportPrice >= 0),
    SellingPrice DECIMAL(15, 2) NOT NULL,
    Unit VARCHAR(20),
    CategoryID INT,
    FOREIGN KEY (CategoryID) REFERENCES CATEGORY(CategoryID),
    CONSTRAINT CHK_Price CHECK (SellingPrice > ImportPrice) -- Quy tắc nghiệp vụ
);

-- 8. Bảng Nhân viên (EMPLOYEE)
-- Lương được tham chiếu từ bảng POSITION
CREATE TABLE EMPLOYEE (
    EmployeeID INT AUTO_INCREMENT PRIMARY KEY,
    FullName VARCHAR(100) NOT NULL,
    DateOfBirth DATE,
    Address VARCHAR(255),
    Phone VARCHAR(15),
    PositionID INT NOT NULL,
    ManagerID INT, -- Quan hệ đệ quy (Quản lý)
    FOREIGN KEY (PositionID) REFERENCES `POSITION`(PositionID),
    FOREIGN KEY (ManagerID) REFERENCES EMPLOYEE(EmployeeID)
);

-- 9. Bảng Số điện thoại Nhà cung cấp (SUPPLIER_PHONE - Đa trị)
CREATE TABLE SUPPLIER_PHONE (
    SupplierID INT,
    Phone VARCHAR(15),
    PRIMARY KEY (SupplierID, Phone),
    FOREIGN KEY (SupplierID) REFERENCES SUPPLIER(SupplierID) ON DELETE CASCADE
);

-- =================================================================
-- PHẦN 3: CÁC BẢNG KHUYẾN MÃI (Theo Logical Diagram)
-- (Không có bảng cha PROMOTION, thuộc tính chung được copy xuống)
-- =================================================================

-- 10. Khuyến mãi sự kiện (EVENT_PROMOTION)
CREATE TABLE EVENT_PROMOTION (
    PromotionID INT AUTO_INCREMENT PRIMARY KEY,
    PromotionName VARCHAR(100) NOT NULL,
    StartDate DATE NOT NULL,
    EndDate DATE NOT NULL,
    PaymentMethod VARCHAR(50),
    DiscountPercent FLOAT CHECK (DiscountPercent > 0 AND DiscountPercent <= 100),
    EventName VARCHAR(150),
    MinOrderValue DECIMAL(15, 2),
    CHECK (EndDate >= StartDate)
);

-- 11. Ưu đãi thành viên (MEMBERSHIP_BENEFIT)
CREATE TABLE MEMBERSHIP_BENEFIT (
    PromotionID INT AUTO_INCREMENT PRIMARY KEY,
    PromotionName VARCHAR(100) NOT NULL,
    StartDate DATE NOT NULL,
    EndDate DATE NOT NULL,
    PaymentMethod VARCHAR(50),
    DiscountPercent FLOAT CHECK (DiscountPercent > 0 AND DiscountPercent <= 100),
    RequiredTier VARCHAR(50), -- Hạng yêu cầu
    CHECK (EndDate >= StartDate)
);

-- 12. Giảm giá hết hạn (EXPIRY_DISCOUNT)
-- Dành cho hàng cận date (thực phẩm)
CREATE TABLE EXPIRY_DISCOUNT (
    PromotionID INT AUTO_INCREMENT PRIMARY KEY,
    PromotionName VARCHAR(100) NOT NULL,
    StartDate DATE NOT NULL,
    EndDate DATE NOT NULL,
    PaymentMethod VARCHAR(50),
    DiscountPercent FLOAT CHECK (DiscountPercent > 0 AND DiscountPercent <= 100),
    DaysBeforeExpiry INT NOT NULL, -- Số ngày trước khi hết hạn
    CHECK (EndDate >= StartDate)
);

-- =================================================================
-- PHẦN 4: CÁC BẢNG PHÂN CẤP (SUBCLASSES) & QUAN HỆ ĐẶC BIỆT
-- =================================================================

-- 13. Phân cấp NCC: Nông dân địa phương (LOCAL_FARMER)
CREATE TABLE LOCAL_FARMER (
    SupplierID INT PRIMARY KEY,
    MainProduct VARCHAR(150),
    FOREIGN KEY (SupplierID) REFERENCES SUPPLIER(SupplierID) ON DELETE CASCADE
);

-- 14. Phân cấp NCC: Nhà sản xuất công nghiệp (INDUSTRIAL_MANUFACTURER)
CREATE TABLE INDUSTRIAL_MANUFACTURER (
    SupplierID INT PRIMARY KEY,
    QualityCertification VARCHAR(100),
    BusinessRegistration VARCHAR(100),
    FOREIGN KEY (SupplierID) REFERENCES SUPPLIER(SupplierID) ON DELETE CASCADE
);

-- 15. Phân cấp SP: Thực phẩm (FOOD_ITEM)
-- Có liên kết tới EXPIRY_DISCOUNT để giảm giá hàng cận date
CREATE TABLE FOOD_ITEM (
    ProductID INT PRIMARY KEY,
    ExpiryDays INT,
    StorageTemperature FLOAT,
    SafetyThreshold INT,
    PromotionID INT, -- Khóa ngoại trỏ tới bảng Giảm giá hết hạn
    FOREIGN KEY (ProductID) REFERENCES PRODUCT(ProductID) ON DELETE CASCADE,
    FOREIGN KEY (PromotionID) REFERENCES EXPIRY_DISCOUNT(PromotionID)
);

-- 16. Phân cấp SP: Điện tử (ELECTRONIC_ITEM)
CREATE TABLE ELECTRONIC_ITEM (
    ProductID INT PRIMARY KEY,
    WarrantyMonths INT,
    SupplierID INT, -- Nhà sản xuất chịu trách nhiệm bảo hành
    FOREIGN KEY (ProductID) REFERENCES PRODUCT(ProductID) ON DELETE CASCADE,
    FOREIGN KEY (SupplierID) REFERENCES SUPPLIER(SupplierID)
);

-- 17. Quan hệ Cung cấp đặc biệt (SPECIAL_SUPPLY)
-- (Giữa Nông dân và Thực phẩm)
CREATE TABLE SPECIAL_SUPPLY (
    SupplierID INT,
    ProductID INT,
    PRIMARY KEY (SupplierID, ProductID),
    FOREIGN KEY (SupplierID) REFERENCES LOCAL_FARMER(SupplierID),
    FOREIGN KEY (ProductID) REFERENCES FOOD_ITEM(ProductID)
);

-- 18. Quan hệ Cung cấp chung (SUPPLIES)
CREATE TABLE SUPPLIES (
    SupplierID INT,
    ProductID INT,
    PRIMARY KEY (SupplierID, ProductID),
    FOREIGN KEY (SupplierID) REFERENCES SUPPLIER(SupplierID),
    FOREIGN KEY (ProductID) REFERENCES PRODUCT(ProductID)
);

-- =================================================================
-- PHẦN 5: NGHIỆP VỤ KHO, BÁN HÀNG & CHẤM CÔNG
-- =================================================================

-- 19. Bảng Lô hàng / Tồn kho (INVENTORY)
-- Sử dụng InventoryID để phân biệt các lô hàng nhập khác ngày của cùng 1 SP
CREATE TABLE INVENTORY (
    InventoryID INT AUTO_INCREMENT PRIMARY KEY,
    ImportDate DATE NOT NULL,
    Quantity INT NOT NULL CHECK (Quantity >= 0),
    WarehouseID INT NOT NULL,
    ProductID INT NOT NULL,
    FOREIGN KEY (WarehouseID) REFERENCES WAREHOUSE(WarehouseID),
    FOREIGN KEY (ProductID) REFERENCES PRODUCT(ProductID)
);

-- 20. Bảng Trưng bày (DISPLAYS)
-- Quản lý hàng trên quầy, lấy từ lô hàng nào (InventoryID)
CREATE TABLE DISPLAYS (
    InventoryID INT,
    CounterID INT,
    Position VARCHAR(50), -- Vị trí trên quầy
    MaxQuantity INT NOT NULL CHECK (MaxQuantity > 0),
    CurrentQuantity INT NOT NULL CHECK (CurrentQuantity >= 0),
    PRIMARY KEY (InventoryID, CounterID),
    FOREIGN KEY (InventoryID) REFERENCES INVENTORY(InventoryID),
    FOREIGN KEY (CounterID) REFERENCES COUNTER(CounterID),
    CONSTRAINT CHK_DisplayLimit CHECK (CurrentQuantity <= MaxQuantity)
);

-- 21. Bảng Chấm công (TIMEKEEPING)
CREATE TABLE TIMEKEEPING (
    TimekeepingID INT AUTO_INCREMENT PRIMARY KEY,
    Date DATE NOT NULL,
    WorkHours FLOAT NOT NULL CHECK (WorkHours >= 0),
    EmployeeID INT NOT NULL,
    FOREIGN KEY (EmployeeID) REFERENCES EMPLOYEE(EmployeeID)
);

-- 22. Bảng Hóa đơn (INVOICE)
CREATE TABLE INVOICE (
    InvoiceID INT AUTO_INCREMENT PRIMARY KEY,
    CreatedAt DATETIME DEFAULT CURRENT_TIMESTAMP,
    PaymentMethod VARCHAR(50),
    TotalAmount DECIMAL(15, 2) DEFAULT 0, -- Dẫn xuất (tính từ Invoice_Detail)
    EmployeeID INT,
    CustomerID INT,
    FOREIGN KEY (EmployeeID) REFERENCES EMPLOYEE(EmployeeID),
    FOREIGN KEY (CustomerID) REFERENCES CUSTOMER(CustomerID)
);

-- 23. Bảng Chi tiết hóa đơn (INVOICE_DETAIL)
CREATE TABLE INVOICE_DETAIL (
    InvoiceID INT,
    ProductID INT,
    Quantity INT NOT NULL CHECK (Quantity > 0),
    SellingPrice DECIMAL(15, 2) NOT NULL, -- Giá tại thời điểm bán
    PRIMARY KEY (InvoiceID, ProductID),
    FOREIGN KEY (InvoiceID) REFERENCES INVOICE(InvoiceID),
    FOREIGN KEY (ProductID) REFERENCES PRODUCT(ProductID)
);

-- =================================================================
-- PHẦN 6: ÁP DỤNG KHUYẾN MÃI (BẢNG TRUNG GIAN)
-- =================================================================

-- 24. Áp dụng Khuyến mãi sự kiện cho Sản phẩm
CREATE TABLE EVENT_PROMOTION_PRODUCT (
    PromotionID INT,
    ProductID INT,
    PRIMARY KEY (PromotionID, ProductID),
    FOREIGN KEY (PromotionID) REFERENCES EVENT_PROMOTION(PromotionID) ON DELETE CASCADE,
    FOREIGN KEY (ProductID) REFERENCES PRODUCT(ProductID) ON DELETE CASCADE
);

-- 25. Áp dụng Ưu đãi thành viên cho Sản phẩm
CREATE TABLE MEMBERSHIP_BENEFIT_PROMOTION_PRODUCT (
    PromotionID INT,
    ProductID INT,
    PRIMARY KEY (PromotionID, ProductID),
    FOREIGN KEY (PromotionID) REFERENCES MEMBERSHIP_BENEFIT(PromotionID) ON DELETE CASCADE,
    FOREIGN KEY (ProductID) REFERENCES PRODUCT(ProductID) ON DELETE CASCADE
);