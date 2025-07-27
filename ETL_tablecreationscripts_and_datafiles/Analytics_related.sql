analytics_requirement:
1.how many order_id per day (sysrundate) from masterdata
2.average cart value( quantity x price) across sysrundate from masterdata
3.average of delivery_time( delivery_ts - order_ts ) from masterdata
  where ordercycle_indicator = 'Same Day Delivery Complete'
4.select distinct product_name,warehouse_id from inventory where remain_inventory < 30
5.for each warehouse_id which product_id has max quantity across sysrundate
  from masterdata
6.Percent of each order_type
7.Delivery Location map 

1.====Daily Orders====
SELECT sysrundate, COUNT(DISTINCT order_id) AS Total_Orders
FROM masterdata
GROUP BY sysrundate
ORDER BY sysrundate;

2.===Daily Average Cart Value===
SELECT sysrundate, AVG(quantity * price) AS Average_Cart_Value
FROM masterdata
GROUP BY sysrundate
ORDER BY sysrundate

3.===Average Dailyvery time====
SELECT sysrundate,
       AVG(TIMESTAMPDIFF(MINUTE, order_ts, delivery_ts)) AS Average_Delivery_Time_in_Minutes
FROM masterdata
WHERE ordercycle_indicator = 'Same Day Delivery Complete'
GROUP BY sysrundate
ORDER BY sysrundate;


4.===Low Inventory==
SELECT product_name, remain_inventory,warehouse_id 
FROM inventory
WHERE remain_inventory < 30
ORDER BY remain_inventory ASC

5.==Most Selling Product per warehouse==
SELECT m.warehouse_id, m.product_id, i.product_name,SUM(m.quantity) AS total_qty
FROM masterdata m
Inner join inventory i
on m.product_id = i.product_id
GROUP BY m.warehouse_id, m.product_id,i.product_name
HAVING total_qty = (
    SELECT MAX(total)
    FROM (
        SELECT SUM(quantity) AS total
        FROM masterdata
        WHERE warehouse_id = m.warehouse_id
        GROUP BY product_id
    ) sub
)
ORDER BY warehouse_id

6.===Delivery Type Segmentation===
SELECT 
  CASE 
    WHEN ordercycle_indicator 
	IN ('Order Cycle End', 'Order Cycle Start') 
    THEN 'Next Day Delivery'
    ELSE ordercycle_indicator
  END AS delivery_type,
  COUNT(*) * 100.0 / (
						SELECT COUNT(*) 
						FROM masterdata 
						WHERE ordercycle_indicator IN (
						  'Delivery Cancelled', 'Same Day Delivery Complete', 
						  'Order Cycle End', 'Order Cycle Start' )
					  ) AS percentage
FROM masterdata
WHERE ordercycle_indicator IN (
  'Delivery Cancelled', 'Same Day Delivery Complete', 
  'Order Cycle End', 'Order Cycle Start')
GROUP BY delivery_type;


7.===location of delivery==:
SELECT
  courier_id AS Delivery_Location,
  CAST(lat AS DOUBLE) AS latitude,
  CAST(lon AS DOUBLE) AS longitude
FROM (
    SELECT courier_id, lat, lon,
           ROW_NUMBER() OVER (PARTITION BY courier_id ORDER BY gps_ts DESC) AS rn
    FROM delivery
) sub
WHERE rn = 1