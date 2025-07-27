import mysql.connector
from datetime import datetime

def process_final_logic():
    try:
        # MySQL connection
        conn = mysql.connector.connect(
            host="mysql",
            user="root",
            password="pass",
            database="ETL"
        )
        cursor = conn.cursor()

        # Define the sysrundate to process
        target_date = '2025-07-06'
        last_update_time = '2025-07-06 23:50:00'

        # STEP 1: Insert into masterdata
        insert_query = """
        INSERT INTO masterdata (
            sysrundate, order_id, lat, lon, product_id, warehouse_id, quantity, price,
            customer_id, courier_id, order_ts, gps_ts, delivery_ts,
            sameday_order_status, sameday_delivery_status,
            final_order_status, final_delivery_status, ordercycle_indicator
        )
        SELECT
            o.sysrundate,
            o.order_id,
            d.lat,
            d.lon,
            o.product_id,
            o.inventory_source AS warehouse_id,
            o.quantity,
            o.price,
            o.customer_id,
            d.courier_id,
            o.order_ts,
            d.gps_ts,
            d.delivery_ts,
            o.sameday_order_status,
            d.sameday_delivery_status,
            '', '', ''
        FROM orders o
        JOIN delivery d
            ON o.order_id = d.order_id AND o.customer_id = d.customer_id
        WHERE o.sysrundate = %s AND d.sysrundate = %s
        """
        cursor.execute(insert_query, (target_date, target_date))
        print(f"✅ Inserted {cursor.rowcount} rows into masterdata.")

        # STEP 2: Update inventory table
        # Get all inventory rows
        cursor.execute("SELECT product_id, warehouse_id, stock_level FROM inventory")
        inventory_data = cursor.fetchall()

        # Get ordered quantities per product_id + warehouse_id
        cursor.execute("""
            SELECT product_id, inventory_source AS warehouse_id, SUM(quantity) AS total_qty
            FROM orders
            WHERE sysrundate = %s
            GROUP BY product_id, inventory_source
        """, (target_date,))
        order_qty_rows = cursor.fetchall()

        # Build a dict: {(product_id, warehouse_id): total_qty}
        order_qty_map = {
            (product_id, warehouse_id): total_qty
            for product_id, warehouse_id, total_qty in order_qty_rows
        }

        # Update inventory row by row
        update_query = """
        UPDATE inventory
        SET last_order_qty = %s,
            remain_inventory = %s,
            Last_updatetime = %s
        WHERE product_id = %s AND warehouse_id = %s
        """

        updated_count = 0
        for product_id, warehouse_id, stock_level in inventory_data:
            total_qty = order_qty_map.get((product_id, warehouse_id), 0)
            remain_inventory = stock_level - total_qty
            cursor.execute(update_query, (total_qty, remain_inventory, last_update_time, product_id, warehouse_id))
            updated_count += cursor.rowcount

        print(f"✅ Updated {updated_count} rows in inventory.")

        # Finalize
        conn.commit()
        print("✅ Process_final_logic execution completed successfully.")

    except Exception as e:
        print(f"Error occurred: {e}")
        if conn:
            conn.rollback()
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

