-- ============================================================
-- TRIGGERS CHO HỆ THỐNG QUẢN LÝ SIÊU THỊ
-- ============================================================
-- Hướng dẫn: Chạy file này trong MySQL Workbench sau khi đã tạo schema
-- ============================================================

USE SupermarketManagement;

-- ============================================================
-- 1. TRIGGER: Tự động cập nhật TotalAmount trong INVOICE
-- Khi thêm hoặc sửa INVOICE_DETAIL
-- ============================================================

DELIMITER //

CREATE TRIGGER trg_after_insert_invoice_detail
AFTER INSERT ON INVOICE_DETAIL
FOR EACH ROW
BEGIN
    UPDATE INVOICE 
    SET TotalAmount = (
        SELECT IFNULL(SUM(Quantity * SellingPrice), 0)
        FROM INVOICE_DETAIL 
        WHERE InvoiceID = NEW.InvoiceID
    )
    WHERE InvoiceID = NEW.InvoiceID;
END //

CREATE TRIGGER trg_after_update_invoice_detail
AFTER UPDATE ON INVOICE_DETAIL
FOR EACH ROW
BEGIN
    UPDATE INVOICE 
    SET TotalAmount = (
        SELECT IFNULL(SUM(Quantity * SellingPrice), 0)
        FROM INVOICE_DETAIL 
        WHERE InvoiceID = NEW.InvoiceID
    )
    WHERE InvoiceID = NEW.InvoiceID;
END //

CREATE TRIGGER trg_after_delete_invoice_detail
AFTER DELETE ON INVOICE_DETAIL
FOR EACH ROW
BEGIN
    UPDATE INVOICE 
    SET TotalAmount = (
        SELECT IFNULL(SUM(Quantity * SellingPrice), 0)
        FROM INVOICE_DETAIL 
        WHERE InvoiceID = OLD.InvoiceID
    )
    WHERE InvoiceID = OLD.InvoiceID;
END //

DELIMITER ;

-- ============================================================
-- 2. TRIGGER: Tự động cộng điểm và cập nhật hạng cho CUSTOMER
-- Quy tắc tính điểm: 1 điểm cho mỗi 10,000 VND
-- Quy tắc xếp hạng:
--   - Points < 100: Thành viên
--   - Points 100-499: Bạc
--   - Points 500-999: Vàng
--   - Points >= 1000: Kim cương
-- ============================================================

DELIMITER //

CREATE TRIGGER trg_after_update_invoice_total
AFTER UPDATE ON INVOICE
FOR EACH ROW
BEGIN
    DECLARE v_new_points INT;
    DECLARE v_new_tier VARCHAR(20);
    
    -- Chỉ cập nhật khi TotalAmount thay đổi và CustomerID tồn tại
    IF NEW.TotalAmount != OLD.TotalAmount AND NEW.CustomerID IS NOT NULL THEN
        -- Tính điểm mới
        SELECT Points + FLOOR((NEW.TotalAmount - OLD.TotalAmount) / 10000) 
        INTO v_new_points
        FROM CUSTOMER 
        WHERE CustomerID = NEW.CustomerID;
        
        -- Xác định hạng mới dựa trên điểm
        SET v_new_tier = CASE
            WHEN v_new_points >= 1000 THEN 'Kim cương'
            WHEN v_new_points >= 500 THEN 'Vàng'
            WHEN v_new_points >= 100 THEN 'Bạc'
            ELSE 'Thành viên'
        END;
        
        -- Cập nhật cả điểm và hạng trong 1 lần (tránh trigger lồng)
        UPDATE CUSTOMER 
        SET Points = v_new_points,
            Tier = v_new_tier
        WHERE CustomerID = NEW.CustomerID;
    END IF;
END //

DELIMITER ;

-- ============================================================
-- 3. TRIGGER: Cập nhật TotalRevenue của SUPPLIER
-- Khi bán hàng (áp dụng cho TẤT CẢ loại hàng qua bảng SUPPLIES)
-- ============================================================

DELIMITER //

CREATE TRIGGER trg_after_insert_invoice_detail_supplier
AFTER INSERT ON INVOICE_DETAIL
FOR EACH ROW
BEGIN
    -- Cập nhật doanh thu cho TẤT CẢ nhà cung cấp của sản phẩm này
    -- Sử dụng bảng SUPPLIES (quan hệ cung cấp chung)
    UPDATE SUPPLIER S
    JOIN SUPPLIES SP ON S.SupplierID = SP.SupplierID
    SET S.TotalRevenue = S.TotalRevenue + (NEW.Quantity * NEW.SellingPrice)
    WHERE SP.ProductID = NEW.ProductID;
END //

DELIMITER ;

-- ============================================================
-- 4. TRIGGER: Kiểm tra ràng buộc CurrentQuantity <= MaxQuantity trên DISPLAYS
-- (Bổ sung cho CHECK constraint)
-- ============================================================

DELIMITER //

CREATE TRIGGER trg_before_update_displays
BEFORE UPDATE ON DISPLAYS
FOR EACH ROW
BEGIN
    IF NEW.CurrentQuantity > NEW.MaxQuantity THEN
        SIGNAL SQLSTATE '45000' 
        SET MESSAGE_TEXT = 'Số lượng hiện tại không được vượt quá số lượng tối đa trên quầy';
    END IF;
    
    IF NEW.CurrentQuantity < 0 THEN
        SIGNAL SQLSTATE '45000' 
        SET MESSAGE_TEXT = 'Số lượng hiện tại không được âm';
    END IF;
END //

DELIMITER ;

-- ============================================================
-- 5. TRIGGER: Kiểm tra Giá bán > Giá nhập khi UPDATE PRODUCT
-- (Bổ sung cho CHECK constraint)
-- ============================================================

DELIMITER //

CREATE TRIGGER trg_before_update_product_price
BEFORE UPDATE ON PRODUCT
FOR EACH ROW
BEGIN
    IF NEW.SellingPrice <= NEW.ImportPrice THEN
        SIGNAL SQLSTATE '45000' 
        SET MESSAGE_TEXT = 'Giá bán phải lớn hơn giá nhập';
    END IF;
END //

DELIMITER ;

-- ============================================================
-- GHI CHÚ QUAN TRỌNG
-- ============================================================
-- 
-- 1. Chạy file SQL.md trước để tạo schema
-- 2. Chạy seeder.py để tạo dữ liệu mẫu
-- 3. Sau đó chạy file triggers.sql này
--
-- Nếu gặp lỗi "Trigger already exists", có thể xóa trigger cũ:
--   DROP TRIGGER IF EXISTS trg_after_insert_invoice_detail;
--   DROP TRIGGER IF EXISTS trg_after_update_invoice_detail;
--   DROP TRIGGER IF EXISTS trg_after_delete_invoice_detail;
--   DROP TRIGGER IF EXISTS trg_after_update_invoice_total;
--   DROP TRIGGER IF EXISTS trg_after_insert_invoice_detail_supplier;
--   DROP TRIGGER IF EXISTS trg_before_update_displays;
--   DROP TRIGGER IF EXISTS trg_before_update_product_price;
-- ============================================================
