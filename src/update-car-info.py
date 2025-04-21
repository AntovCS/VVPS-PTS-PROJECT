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
