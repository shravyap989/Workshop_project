CREATE TABLE IF NOT EXISTS menu_items (
    id SERIAL PRIMARY KEY,
    name VARCHAR(120) NOT NULL,
    description VARCHAR(255),
    price NUMERIC(10,2) NOT NULL
);

CREATE TABLE IF NOT EXISTS orders (
    id SERIAL PRIMARY KEY,
    status VARCHAR(30) NOT NULL DEFAULT 'PLACED',
    total NUMERIC(10,2) NOT NULL DEFAULT 0,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS order_items (
    id SERIAL PRIMARY KEY,
    order_id INTEGER NOT NULL REFERENCES orders(id) ON DELETE CASCADE,
    menu_item_id INTEGER NOT NULL,
    item_name VARCHAR(120) NOT NULL,
    quantity INTEGER NOT NULL,
    price NUMERIC(10,2) NOT NULL
);

INSERT INTO menu_items (name, description, price)
SELECT 'Veg Meals', 'Rice, curry, vegetables and sides', 70
WHERE NOT EXISTS (SELECT 1 FROM menu_items WHERE name = 'Veg Meals');

INSERT INTO menu_items (name, description, price)
SELECT 'Masala Dosa', 'Crispy dosa with potato masala', 55
WHERE NOT EXISTS (SELECT 1 FROM menu_items WHERE name = 'Masala Dosa');

INSERT INTO menu_items (name, description, price)
SELECT 'Idli Vada', 'Three idlis with one vada and sambar', 45
WHERE NOT EXISTS (SELECT 1 FROM menu_items WHERE name = 'Idli Vada');

INSERT INTO menu_items (name, description, price)
SELECT 'Paneer Fried Rice', 'Fried rice with paneer and vegetables', 100
WHERE NOT EXISTS (SELECT 1 FROM menu_items WHERE name = 'Paneer Fried Rice');

INSERT INTO menu_items (name, description, price)
SELECT 'Chicken Biriyani', 'Aromatic chicken biriyani', 140
WHERE NOT EXISTS (SELECT 1 FROM menu_items WHERE name = 'Chicken Biriyani');

INSERT INTO menu_items (name, description, price)
SELECT 'Veg Sandwich', 'Grilled vegetable sandwich', 60
WHERE NOT EXISTS (SELECT 1 FROM menu_items WHERE name = 'Veg Sandwich');

INSERT INTO menu_items (name, description, price)
SELECT 'Fresh Lime', 'Fresh lime juice', 35
WHERE NOT EXISTS (SELECT 1 FROM menu_items WHERE name = 'Fresh Lime');

INSERT INTO menu_items (name, description, price)
SELECT 'Tea', 'Hot milk tea', 15
WHERE NOT EXISTS (SELECT 1 FROM menu_items WHERE name = 'Tea');
