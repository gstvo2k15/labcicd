CREATE TABLE IF NOT EXISTS users (
 id SERIAL PRIMARY KEY,
 email TEXT UNIQUE NOT NULL,
 password_hash TEXT NOT NULL,
 name TEXT NOT NULL,
 role TEXT NOT NULL DEFAULT 'USER' CHECK(role IN ('USER','ADMIN','RESTAURANT')),
 created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE TABLE IF NOT EXISTS restaurants (
 id SERIAL PRIMARY KEY,
 name TEXT NOT NULL,
 cuisine TEXT NOT NULL,
 address TEXT NOT NULL,
 rating NUMERIC(2,1) NOT NULL DEFAULT 4.0 CHECK(rating BETWEEN 0 AND 5)
);
CREATE TABLE IF NOT EXISTS menu_items (
 id SERIAL PRIMARY KEY,
 restaurant_id INT NOT NULL REFERENCES restaurants(id) ON DELETE CASCADE,
 name TEXT NOT NULL,
 description TEXT,
 price NUMERIC(10,2) NOT NULL CHECK(price>0)
);
CREATE TABLE IF NOT EXISTS orders (
 id SERIAL PRIMARY KEY,
 user_id INT NOT NULL REFERENCES users(id),
 restaurant_id INT NOT NULL REFERENCES restaurants(id),
 total_amount NUMERIC(10,2) NOT NULL CHECK(total_amount>=0),
 status TEXT NOT NULL DEFAULT 'CREATED',
 created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
 updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE TABLE IF NOT EXISTS order_items (
 id SERIAL PRIMARY KEY,
 order_id INT NOT NULL REFERENCES orders(id) ON DELETE CASCADE,
 menu_item_id INT NOT NULL REFERENCES menu_items(id),
 quantity INT NOT NULL CHECK(quantity>0),
 unit_price NUMERIC(10,2) NOT NULL CHECK(unit_price>0)
);
CREATE TABLE IF NOT EXISTS payments (
 id SERIAL PRIMARY KEY,
 order_id INT NOT NULL REFERENCES orders(id) ON DELETE CASCADE,
 amount NUMERIC(10,2) NOT NULL,
 status TEXT NOT NULL,
 provider_reference TEXT NOT NULL,
 created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE TABLE IF NOT EXISTS notifications (
 id SERIAL PRIMARY KEY,
 user_id INT NOT NULL REFERENCES users(id),
 order_id INT REFERENCES orders(id) ON DELETE SET NULL,
 message TEXT NOT NULL,
 status TEXT NOT NULL,
 created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_orders_user_created ON orders(user_id,created_at DESC);
CREATE INDEX IF NOT EXISTS idx_menu_restaurant ON menu_items(restaurant_id);
CREATE INDEX IF NOT EXISTS idx_notifications_user ON notifications(user_id,created_at DESC);
