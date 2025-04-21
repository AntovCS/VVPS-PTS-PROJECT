def register():
    print("\n--- Register ---")
    role = input("Select role (1: User, 2: Repair Shop): ").strip()
    if role not in ['1', '2']:
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
        if role == '1':
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
        else:
            location = input("Enter location (city in Bulgaria): ").strip()
            specialization = input("Enter specialization (comma-separated car brands): ").strip()
            oil_price = input("Enter oil change price: ").strip()
            water_pump_price = input("Enter water pump change price: ").strip()
            belt_price = input("Enter belt change price: ").strip()
            pulleys_price = input("Enter pulleys price: ").strip()
            filter_price = input("Enter filter change price: ").strip()
            oil_time = input("Enter oil change time (minutes): ").strip()
            water_pump_time = input("Enter water pump change time (minutes): ").strip()
            belt_time = input("Enter belt change time (minutes): ").strip()
            pulleys_time = input("Enter pulleys change time (minutes): ").strip()
            filter_time = input("Enter filter change time (minutes): ").strip()
            query = """
            INSERT INTO repair_shops (username, email, password, location, specialization,
                                     oil_change_price, water_pump_price, belt_change_price,
                                     pulleys_price, filter_change_price,
                                     oil_change_time, water_pump_time, belt_change_time,
                                     pulleys_time, filter_change_time)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            values = (username, email, hashed_password, location, specialization,
                      float(oil_price) if oil_price else None,
                      float(water_pump_price) if water_pump_price else None,
                      float(belt_price) if belt_price else None,
                      float(pulleys_price) if pulleys_price else None,
                      float(filter_price) if filter_price else None,
                      int(oil_time) if oil_time else None,
                      int(water_pump_time) if water_pump_time else None,
                      int(belt_time) if belt_time else None,
                      int(pulleys_time) if pulleys_time else None,
                      int(filter_time) if filter_time else None)

        cursor.execute(query, values)
        conn.commit()
        print("Registration successful!")
    except mysql.connector.Error as err:
        print(f"Error: {err}")
    finally:
        cursor.close()
        conn.close()
