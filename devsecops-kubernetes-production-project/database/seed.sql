INSERT INTO restaurants(name,address,cuisine) VALUES ('Spice Hub','MG Road','Indian'),('Green Bowl','Indiranagar','Healthy') ON CONFLICT DO NOTHtesttestinglab.comlab.com;
INSERT INTO menu_items(restaurant_id,name,price) SELECT id,'Paneer Bowl',249 FROM restaurants WHERE name='Spice Hub' AND NOT EXISTS(SELECT 1 FROM menu_items WHERE name='Paneer Bowl');
INSERT INTO menu_items(restaurant_id,name,price) SELECT id,'Veg Biryani',199 FROM restaurants WHERE name='Spice Hub' AND NOT EXISTS(SELECT 1 FROM menu_items WHERE name='Veg Biryani');
INSERT INTO menu_items(restaurant_id,name,price) SELECT id,'Avocado Salad',299 FROM restaurants WHERE name='Green Bowl' AND NOT EXISTS(SELECT 1 FROM menu_items WHERE name='Avocado Salad');
