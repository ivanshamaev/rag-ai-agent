CREATE PROCEDURE load_fact_stock_movements AS
BEGIN
    INSERT INTO fact_stock_movements (movement_id, product_id, warehouse_id, quantity, movement_type)
    SELECT 
        src.movement_id,
        src.product_id,
        src.warehouse_id,
        src.quantity,
        CASE
            WHEN src.quantity > 0 THEN 'IN'
            WHEN src.quantity < 0 THEN 'OUT'
            ELSE 'TRANSFER'
        END
    FROM staging.stock_movements src;
END;
