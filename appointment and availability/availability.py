def manage_shop_availability(shop):
    conn = connect_db()
    if not conn:
        return
    cursor = conn.cursor(dictionary=True)

    try:
        print("\n--- Manage Availability ---")
        date_input = input("Enter date (YYYY-MM-DD, or press Enter for today): ").strip()
        available_date = date.today() if not date_input else date.fromisoformat(date_input)

        start_time = input("Enter start time (HH:MM): ").strip()
        end_time = input("Enter end time (HH:MM): ").strip()

        try:
            start_time = datetime.strptime(start_time, "%H:%M").time()
            end_time = datetime.strptime(end_time, "%H:%M").time()
        except ValueError:
            print("Invalid time format. Use HH:MM.")
            return

        if start_time >= end_time:
            print("Start time must be before end time.")
            return

        query = """
        INSERT INTO shop_availability (shop_id, available_date, start_time, end_time)
        VALUES (%s, %s, %s, %s)
        """
        cursor.execute(query, (shop['id'], available_date, start_time, end_time))
        conn.commit()
        print("Availability added successfully!")
    except mysql.connector.Error as err:
        print(f"Error: {err}")
    finally:
        cursor.close()
        conn.close()
