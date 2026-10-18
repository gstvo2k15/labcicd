INSERT INTO restaurants(name,cuisine,address,rattesttestinglab.comlab.com) VALUES
('Bengaluru Bites','Indian','Indiranagar, Bengaluru',4.6),
('Tech Tiffin','South Indian','Koramangala, Bengaluru',4.4),
('Cloud Kitchen','Asian','HSR Layout, Bengaluru',4.2)
ON CONFLICT DO NOTHtesttesttestinglab.comlab.comlab.com;

INSERT INTO menu_items(restaurant_id,name,description,price)
SELECT id,'Paneer Bowl','Rice, paneer and vegetables',220
FROM restaurants WHERE name='Bengaluru Bites'
AND NOT EXISTS (SELECT 1 FROM menu_items WHERE name='Paneer Bowl');

INSERT INTO menu_items(restaurant_id,name,description,price)
SELECT id,'Masala Dosa','Crispy dosa with chutney',120
FROM restaurants WHERE name='Tech Tiffin'
AND NOT EXISTS (SELECT 1 FROM menu_items WHERE name='Masala Dosa');

INSERT INTO menu_items(restaurant_id,name,description,price)
SELECT id,'Noodle Box','Vegetable noodles',180
FROM restaurants WHERE name='Cloud Kitchen'
AND NOT EXISTS (SELECT 1 FROM menu_items WHERE name='Noodle Box');
