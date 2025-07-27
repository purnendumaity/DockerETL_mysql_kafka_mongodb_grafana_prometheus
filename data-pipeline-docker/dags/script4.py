import mysql.connector

def update_ordercycle_logic():
    try:
        conn = mysql.connector.connect(
            host="mysql",
            user="root",
            password="pass",
            database="ETL"
        )
        cursor = conn.cursor()
        target_date = '2025-07-06'

        update_logic_queries = [
            # Logic 1
            ("""
            UPDATE masterdata
            SET final_order_status = 'Complete',
                final_delivery_status = 'Complete',
                ordercycle_indicator = 'Order Cycle End'
            WHERE sysrundate = %s
              AND DATE(order_ts) < %s
              AND sameday_order_status = 'Complete'
              AND sameday_delivery_status = 'Delivered'
            """, (target_date, target_date)),

            # Logic 2
            ("""
            UPDATE masterdata
            SET final_order_status = 'Cancelled',
                final_delivery_status = 'Cancelled',
                ordercycle_indicator = 'Delivery Cancelled'
            WHERE sysrundate = %s
              AND DATE(order_ts) = %s
              AND sameday_order_status = 'Cancelled'
              AND sameday_delivery_status = 'Cancelled'
            """, (target_date, target_date)),

            # Logic 3
            ("""
            UPDATE masterdata
            SET final_order_status = 'Complete',
                final_delivery_status = 'Delivered',
                ordercycle_indicator = 'Same Day Delivery Complete'
            WHERE sysrundate = %s
              AND DATE(order_ts) = %s
              AND sameday_order_status = 'Complete'
              AND sameday_delivery_status = 'Delivered'
            """, (target_date, target_date)),

            # Logic 4
            ("""
            UPDATE masterdata
            SET final_order_status = sameday_order_status,
                final_delivery_status = sameday_delivery_status,
                ordercycle_indicator = 'Order Cycle Start'
            WHERE sysrundate = %s
              AND DATE(order_ts) = %s
              AND sameday_order_status IN ('Processing', 'Shipped')
            """, (target_date, target_date)),
        ]

        for query, params in update_logic_queries:
            cursor.execute(query, params)

        conn.commit()
        print("✅ update_order_cycle_logic executed successfully.")

    except Exception as e:
        print(f"Error: {e}")
        if conn:
            conn.rollback()
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()