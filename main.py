import mysql.connector
import bcrypt
import time
from datetime import datetime, timedelta

# Database connection configuration
db_config = {
    'host': 'localhost',
    'user': 'your_username',  # Replace with your MySQL username
    'password': 'your_password',  # Replace with your MySQL password
    'database': 'car_repair_app'
}

# Lockout variables
failed_attempts = 0
lockout_until = None
LOCKOUT_DURATION = 300  # 5 minutes in seconds

def connect_db():
    try:
        return mysql.connector.connect(**db_config)
    except mysql.connector.Error as err:
        print(f"Database connection error: {err}")
        return None

def hash_password(password):
    # Hash the password and convert bytes to string for storage
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(password, hashed):
    # Convert stored hashed password (string) back to bytes for verification
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

def is_locked_out():
    global lockout_until
    if lockout_until and datetime.now() < lockout_until:
        remaining = (lockout_until - datetime.now()).seconds
        print(f"Too many failed attempts. Try again in {remaining} seconds.")
        return True
    if lockout_until and datetime.now() >= lockout_until:
        reset_lockout()
    return False

def reset_lockout():
    global failed_attempts, lockout_until
    failed_attempts = 0
    lockout_until = None

def register():
    print("\n--- Register ---")
    role = input("Select role (1: User, 2: Admin, 3: Repair Shop): ").strip()
    if role not in ['1', '2', '3']:
        print("Invalid role.")
        return

    username = input("Enter username: ").strip()
    email = input("Enter email: ").strip()
    password = input("Enter password: ").strip()

    if not username or not email or not password:
        print("All fields are required.")
        return

    hashed_password = hash_password(password)
    conn = connect_db()
    if not conn:
        return
    cursor = conn.cursor()

    try:
        if role == '1':  # User
            car_brand = input("Enter car brand: ").strip()
            car_model = input("Enter car model: ").strip()
            car_year = input("Enter car year (1900-2025): ").strip()
            if not car_year.isdigit() or int(car_year) < 1900 or int(car_year) > 2025:
                print("Invalid car year.")
                return
            query = """
            INSERT INTO users (username, email, password, car_brand, car_model, car_year)
            VALUES (%s, %s, %s, %s, %s, %s)
            """
            values = (username, email, hashed_password, car_brand, car_model, int(car_year))
        elif role == '2':  # Admin
            query = """
            INSERT INTO admins (username, email, password)
            VALUES (%s, %s, %s)
            """
            values = (username, email, hashed_password)
        else:  # Repair Shop
            location = input("Enter location (city in Bulgaria): ").strip()
            specialization = input("Enter specialization (comma-separated car brands): ").strip()
            oil_price = input("Enter oil change price: ").strip()
            water_pump_price = input("Enter water pump change price: ").strip()
            belt_price = input("Enter belt change price: ").strip()
            pulleys_price = input("Enter pulleys price: ").strip()
            filter_price = input("Enter filter change price: ").strip()
            query = """
            INSERT INTO repair_shops (username, email, password, location, specialization,
                                     oil_change_price, water_pump_price, belt_change_price,
                                     pulleys_price, filter_change_price)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            values = (username, email, hashed_password, location, specialization,
                      float(oil_price) if oil_price else None,
                      float(water_pump_price) if water_pump_price else None,
                      float(belt_price) if belt_price else None,
                      float(pulleys_price) if pulleys_price else None,
                      float(filter_price) if filter_price else None)

        cursor.execute(query, values)
        conn.commit()
        print("Registration successful!")
    except mysql.connector.Error as err:
        print(f"Error: {err}")
    finally:
        cursor.close()
        conn.close()

def login():
    global failed_attempts, lockout_until
    if is_locked_out():
        return None, None

    print("\n--- Login ---")
    username = input("Enter username: ").strip()
    password = input("Enter password: ").strip()

    conn = connect_db()
    if not conn:
        return None, None
    cursor = conn.cursor(dictionary=True)

    try:
        # Check all tables
        for table, role in [('users', 'user'), ('admins', 'admin'), ('repair_shops', 'repair_shop')]:
            query = f"SELECT * FROM {table} WHERE username = %s"
            cursor.execute(query, (username,))
            user = cursor.fetchone()
            if user and verify_password(password, user['password']):
                reset_lockout()
                print(f"Logged in as {role}!")
                return user, role
        failed_attempts += 1
        if failed_attempts >= 5:
            lockout_until = datetime.now() + timedelta(seconds=LOCKOUT_DURATION)
            print(f"Too many failed attempts. Locked out for {LOCKOUT_DURATION} seconds.")
        else:
            print(f"Invalid username or password. {5 - failed_attempts} attempts remaining.")
        return None, None
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return None, None
    finally:
        cursor.close()
        conn.close()

def list_repair_shops(user):
    conn = connect_db()
    if not conn:
        return
    cursor = conn.cursor(dictionary=True)

    try:
        # Get available locations
        cursor.execute("SELECT DISTINCT location FROM repair_shops")
        locations = [row['location'] for row in cursor.fetchall()]
        if not locations:
            print("No repair shops registered.")
            return

        print("\nAvailable locations:", ", ".join(locations))
        location = input("Enter location (or press Enter for all): ").strip()
        sort_by = input("Sort by (1: Price, 2: Rating): ").strip()

        query = """
        SELECT * FROM repair_shops
        WHERE FIND_IN_SET(%s, specialization)
        """
        params = [user['car_brand']]
        if location:
            query += " AND location = %s"
            params.append(location)

        if sort_by == '1':
            service = input("Sort by price of (1: Oil Change, 2: Water Pump, 3: Belt, 4: Pulleys, 5: Filter): ").strip()
            service_map = {
                '1': 'oil_change_price', '2': 'water_pump_price', '3': 'belt_change_price',
                '4': 'pulleys_price', '5': 'filter_change_price'
            }
            if service not in service_map:
                print("Invalid service.")
                return
            query += f" ORDER BY {service_map[service]} ASC"
        else:
            query += " ORDER BY user_rating DESC"

        cursor.execute(query, params)
        shops = cursor.fetchall()
        if not shops:
            print("No matching repair shops found.")
            return

        for shop in shops:
            print(f"\nShop: {shop['username']}, Location: {shop['location']}, Rating: {shop['user_rating']}")
            print(f"Specialization: {shop['specialization']}")
            print(f"Prices: Oil: {shop['oil_change_price']}, Water Pump: {shop['water_pump_price']}, "
                  f"Belt: {shop['belt_change_price']}, Pulleys: {shop['pulleys_price']}, "
                  f"Filter: {shop['filter_change_price']}")
    except mysql.connector.Error as err:
        print(f"Error: {err}")
    finally:
        cursor.close()
        conn.close()

def update_car_info(user):
    conn = connect_db()
    if not conn:
        return
    cursor = conn.cursor()

    try:
        car_brand = input("Enter new car brand (or press Enter to keep current): ").strip()
        car_model = input("Enter new car model (or press Enter to keep current): ").strip()
        car_year = input("Enter new car year (1900-2025, or press Enter to keep current): ").strip()

        updates = []
        params = []
        if car_brand:
            updates.append("car_brand = %s")
            params.append(car_brand)
        if car_model:
            updates.append("car_model = %s")
            params.append(car_model)
        if car_year:
            if not car_year.isdigit() or int(car_year) < 1900 or int(car_year) > 2025:
                print("Invalid car year.")
                return
            updates.append("car_year = %s")
            params.append(int(car_year))

        if updates:
            params.append(user['id'])
            query = f"UPDATE users SET {', '.join(updates)} WHERE id = %s"
            cursor.execute(query, params)
            conn.commit()
            print("Car information updated!")
        else:
            print("No changes made.")
    except mysql.connector.Error as err:
        print(f"Error: {err}")
    finally:
        cursor.close()
        conn.close()

def rate_repair_shop(user):
    conn = connect_db()
    if not conn:
        return
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute("SELECT id, username, location FROM repair_shops")
        shops = cursor.fetchall()
        if not shops:
            print("No repair shops available.")
            return

        print("\nAvailable repair shops:")
        for shop in shops:
            print(f"ID: {shop['id']}, Name: {shop['username']}, Location: {shop['location']}")
        shop_id = input("Enter shop ID to rate: ").strip()
        rating = input("Enter rating (1-5): ").strip()

        if not rating.isdigit() or int(rating) < 1 or int(rating) > 5:
            print("Invalid rating.")
            return

        # Update or insert rating (assuming a separate ratings table for simplicity)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS shop_ratings (
            user_id INT,
            shop_id INT,
            rating INT,
            PRIMARY KEY (user_id, shop_id),
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (shop_id) REFERENCES repair_shops(id)
        )
        """)
        cursor.execute("""
        INSERT INTO shop_ratings (user_id, shop_id, rating)
        VALUES (%s, %s, %s)
        ON DUPLICATE KEY UPDATE rating = %s
        """, (user['id'], shop_id, rating, rating))

        # Update average rating in repair_shops
        cursor.execute("""
        UPDATE repair_shops rs
        SET user_rating = (
            SELECT AVG(rating)
            FROM shop_ratings
            WHERE shop_id = rs.id
        )
        WHERE id = %s
        """, (shop_id,))
        conn.commit()
        print("Rating submitted!")
    except mysql.connector.Error as err:
        print(f"Error: {err}")
    finally:
        cursor.close()
        conn.close()

def view_shop_rating(shop):
    print(f"\nCurrent rating for {shop['username']}: {shop['user_rating']} stars")

def update_shop_prices(shop):
    conn = connect_db()
    if not conn:
        return
    cursor = conn.cursor()

    try:
        print("\nEnter new prices (press Enter to keep current):")
        oil_price = input(f"Oil change ({shop['oil_change_price']}): ").strip()
        water_pump_price = input(f"Water pump ({shop['water_pump_price']}): ").strip()
        belt_price = input(f"Belt ({shop['belt_change_price']}): ").strip()
        pulleys_price = input(f"Pulleys ({shop['pulleys_price']}): ").strip()
        filter_price = input(f"Filter ({shop['filter_change_price']}): ").strip()

        updates = []
        params = []
        if oil_price:
            updates.append("oil_change_price = %s")
            params.append(float(oil_price))
        if water_pump_price:
            updates.append("water_pump_price = %s")
            params.append(float(water_pump_price))
        if belt_price:
            updates.append("belt_change_price = %s")
            params.append(float(belt_price))
        if pulleys_price:
            updates.append("pulleys_price = %s")
            params.append(float(pulleys_price))
        if filter_price:
            updates.append("filter_change_price = %s")
            params.append(float(filter_price))

        if updates:
            params.append(shop['id'])
            query = f"UPDATE repair_shops SET {', '.join(updates)} WHERE id = %s"
            cursor.execute(query, params)
            conn.commit()
            print("Prices updated!")
        else:
            print("No changes made.")
    except (mysql.connector.Error, ValueError) as err:
        print(f"Error: {err}")
    finally:
        cursor.close()
        conn.close()

def admin_queries():
    conn = connect_db()
    if not conn:
        return
    cursor = conn.cursor(dictionary=True)

    try:
        while True:
            print("\n--- Admin Queries ---")
            print("1. Users by car brand")
            print("2. Repair shops by location")
            print("3. Average service prices")
            print("4. Highest service prices")
            print("5. Lowest service prices")
            print("6. Most popular car brand")
            print("7. Highest rated repair shop")
            print("8. Lowest rated repair shop")
            print("9. Average rating by location")
            print("10. Exit")
            choice = input("Select option: ").strip()

            if choice == '1':
                car_brand = input("Enter car brand: ").strip()
                cursor.execute("SELECT COUNT(*) as count FROM users WHERE car_brand = %s", (car_brand,))
                print(f"Users with {car_brand}: {cursor.fetchone()['count']}")
            elif choice == '2':
                location = input("Enter location: ").strip()
                cursor.execute("SELECT COUNT(*) as count FROM repair_shops WHERE location = %s", (location,))
                print(f"Repair shops in {location}: {cursor.fetchone()['count']}")
            elif choice == '3':
                cursor.execute("""
                SELECT AVG(oil_change_price) as oil, AVG(water_pump_price) as water_pump,
                       AVG(belt_change_price) as belt, AVG(pulleys_price) as pulleys,
                       AVG(filter_change_price) as filter
                FROM repair_shops
                """)
                prices = cursor.fetchone()
                print("Average prices:", {k: round(v, 2) if v else 'N/A' for k, v in prices.items()})
            elif choice == '4':
                cursor.execute("""
                SELECT MAX(oil_change_price) as oil, MAX(water_pump_price) as water_pump,
                       MAX(belt_change_price) as belt, MAX(pulleys_price) as pulleys,
                       MAX(filter_change_price) as filter
                FROM repair_shops
                """)
                prices = cursor.fetchone()
                print("Highest prices:", {k: v if v else 'N/A' for k, v in prices.items()})
            elif choice == '5':
                cursor.execute("""
                SELECT MIN(oil_change_price) as oil, MIN(water_pump_price) as water_pump,
                       MIN(belt_change_price) as belt, MIN(pulleys_price) as pulleys,
                       MIN(filter_change_price) as filter
                FROM repair_shops
                """)
                prices = cursor.fetchone()
                print("Lowest prices:", {k: v if v else 'N/A' for k, v in prices.items()})
            elif choice == '6':
                cursor.execute("""
                SELECT car_brand, COUNT(*) as count
                FROM users
                GROUP BY car_brand
                ORDER BY count DESC
                LIMIT 1
                """)
                result = cursor.fetchone()
                if result:
                    print(f"Most popular car brand: {result['car_brand']} ({result['count']} users)")
                else:
                    print("No users registered.")
            elif choice == '7':
                cursor.execute("SELECT username, user_rating FROM repair_shops ORDER BY user_rating DESC LIMIT 1")
                result = cursor.fetchone()
                if result:
                    print(f"Highest rated shop: {result['username']} ({result['user_rating']} stars)")
                else:
                    print("No repair shops registered.")
            elif choice == '8':
                cursor.execute("SELECT username, user_rating FROM repair_shops WHERE user_rating > 0 ORDER BY user_rating ASC LIMIT 1")
                result = cursor.fetchone()
                if result:
                    print(f"Lowest rated shop: {result['username']} ({result['user_rating']} stars)")
                else:
                    print("No rated repair shops.")
            elif choice == '9':
                location = input("Enter location: ").strip()
                cursor.execute("SELECT AVG(user_rating) as avg_rating FROM repair_shops WHERE location = %s", (location,))
                result = cursor.fetchone()
                print(f"Average rating in {location}: {round(result['avg_rating'], 1) if result['avg_rating'] else 'N/A'} stars")
            elif choice == '10':
                break
            else:
                print("Invalid option.")
    except mysql.connector.Error as err:
        print(f"Error: {err}")
    finally:
        cursor.close()
        conn.close()

def main():
    while True:
        print("\n--- Car Repair App ---")
        print("1. Register")
        print("2. Login")
        print("3. Exit")
        choice = input("Select option: ").strip()

        if choice == '1':
            register()
        elif choice == '2':
            user, role = login()
            if user:
                while True:
                    if role == 'user':
                        print("\n--- User Menu ---")
                        print("1. List repair shops")
                        print("2. Update car info")
                        print("3. Rate repair shop")
                        print("4. Logout")
                        user_choice = input("Select option: ").strip()
                        if user_choice == '1':
                            list_repair_shops(user)
                        elif user_choice == '2':
                            update_car_info(user)
                        elif user_choice == '3':
                            rate_repair_shop(user)
                        elif user_choice == '4':
                            break
                        else:
                            print("Invalid option.")
                    elif role == 'repair_shop':
                        print("\n--- Repair Shop Menu ---")
                        print("1. View rating")
                        print("2. Update prices")
                        print("3. Logout")
                        shop_choice = input("Select option: ").strip()
                        if shop_choice == '1':
                            view_shop_rating(user)
                        elif shop_choice == '2':
                            update_shop_prices(user)
                        elif shop_choice == '3':
                            break
                        else:
                            print("Invalid option.")
                    elif role == 'admin':
                        print("\n--- Admin Menu ---")
                        print("1. Run queries")
                        print("2. Logout")
                        admin_choice = input("Select option: ").strip()
                        if admin_choice == '1':
                            admin_queries()
                        elif admin_choice == '2':
                            break
                        else:
                            print("Invalid option.")
        elif choice == '3':
            print("Goodbye!")
            break
        else:
            print("Invalid option.")

if __name__ == "__main__":
    main()
