-- ============================================================
-- STORED PROCEDURES CHO HỆ THỐNG QUẢN LÝ SIÊU THỊ
-- ============================================================

USE SupermarketManagement;

DROP PROCEDURE IF EXISTS sp_calculate_employee_salary;
DROP PROCEDURE IF EXISTS sp_transfer_to_counter;

DELIMITER //

-- 1. Procedure: Tính lương nhân viên
CREATE PROCEDURE sp_calculate_employee_salary(
    IN p_employee_id INT,
    IN p_month INT,
    IN p_year INT,
    OUT p_total_salary DECIMAL(15,2)
)
BEGIN
    DECLARE v_base_salary DECIMAL(15,2);
    DECLARE v_hourly_rate DECIMAL(15,2);
    DECLARE v_work_hours FLOAT;

    -- Lấy lương cơ bản và lương giờ từ vị trí của nhân viên
    SELECT P.BaseSalary, P.HourlyRate INTO v_base_salary, v_hourly_rate
    FROM EMPLOYEE E
    JOIN POSITION P ON E.PositionID = P.PositionID
    WHERE E.EmployeeID = p_employee_id;

    -- Tính tổng giờ làm trong tháng
    SELECT IFNULL(SUM(WorkHours), 0) INTO v_work_hours
    FROM TIMEKEEPING
    WHERE EmployeeID = p_employee_id
    AND MONTH(Date) = p_month
    AND YEAR(Date) = p_year;

    -- Tính tổng lương: Lương cơ bản + (Lương giờ * Số giờ làm)
    SET p_total_salary = v_base_salary + (v_hourly_rate * v_work_hours);
END //

-- 2. Procedure: Bổ sung hàng từ kho lên quầy
CREATE PROCEDURE sp_transfer_to_counter(
    IN p_inventory_id INT,
    IN p_counter_id INT,
    IN p_quantity INT,
    IN p_position VARCHAR(50)
)
BEGIN
    DECLARE v_available_qty INT;
    DECLARE v_product_id INT;
    DECLARE v_current_qty INT;
    DECLARE v_max_qty INT;
    DECLARE v_existing_inventory_id INT;

    -- Lấy ProductID và kiểm tra số lượng tồn kho
    SELECT Quantity, ProductID INTO v_available_qty, v_product_id
    FROM INVENTORY
    WHERE InventoryID = p_inventory_id;

    IF v_available_qty IS NULL OR v_available_qty < p_quantity THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Không đủ hàng trong kho để chuyển';
    END IF;

    -- Kiểm tra quầy đã có lô hàng này chưa (với khóa chính là InventoryID, CounterID)
    -- Lưu ý: Logic gốc trong báo cáo insert dòng mới nếu chưa có.
    -- Tuy nhiên, DISPLAYS.Primary Key là (InventoryID, CounterID).
    -- Nếu chuyển cùng 1 lô hàng 2 lần vào cùng 1 quầy, ta phải UPDATE, không INSERT.
    
    SELECT CurrentQuantity, MaxQuantity INTO v_current_qty, v_max_qty
    FROM DISPLAYS
    WHERE InventoryID = p_inventory_id AND CounterID = p_counter_id;

    IF v_current_qty IS NULL THEN
        -- Chưa có lô này trên quầy -> Thêm mới
        -- Mặc định MaxQuantity = p_quantity * 2 (như báo cáo đề xuất) hoặc tham số khác
        -- Ở đây ta du di theo báo cáo: MaxQuantity = p_quantity * 2
        INSERT INTO DISPLAYS (InventoryID, CounterID, Position, MaxQuantity, CurrentQuantity)
        VALUES (p_inventory_id, p_counter_id, p_position, p_quantity * 2, p_quantity);
    ELSE
        -- Đã có lô này trên quầy -> Cập nhật số lượng
        IF v_current_qty + p_quantity > v_max_qty THEN
            SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Vượt quá sức chứa tối đa của quầy';
        END IF;

        UPDATE DISPLAYS
        SET CurrentQuantity = CurrentQuantity + p_quantity
        WHERE InventoryID = p_inventory_id AND CounterID = p_counter_id;
    END IF;

    -- Trừ số lượng trong kho
    UPDATE INVENTORY
    SET Quantity = Quantity - p_quantity
    WHERE InventoryID = p_inventory_id;
END //

DELIMITER ;
