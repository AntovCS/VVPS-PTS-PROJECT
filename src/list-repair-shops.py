def list_repair_shops(user):
    conn = connect_db()
    if not conn:
        return
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute("SELECT DISTINCT location FROM repair_shops")
        locations = [row['location'] for row in cursor.fetchall()]
        if not locations:
            print("No repair shops registered.")
            return

        print("\nAvailable locations:", ", ".join(locations))
        location = input("Enter location (or press Enter for all): ").strip()
        sort_by = input("Sort by (1: Price, 2: Rating, 3: Time): ").strip()

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
        elif sort_by == '3':
            service = input("Sort by time of (1: Oil Change, 2: Water Pump, 3: Belt, 4: Pulleys, 5: Filter): ").strip()
            service_map = {
                '1': 'oil_change_time', '2': 'water_pump_time', '3': 'belt_change_time',
                '4': 'pulleys_time', '5': 'filter_change_time'
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
            print(f"Times (minutes): Oil: {shop['oil_change_time']}, Water Pump: {shop['water_pump_time']}, "
                  f"Belt: {shop['belt_change_time']}, Pulleys: {shop['pulleys_time']}, "
                  f"Filter: {shop['filter_change_time']}")
    except mysql.connector.Error as err:
        print(f"Error: {err}")
    finally:
        cursor.close()
        conn.close()
