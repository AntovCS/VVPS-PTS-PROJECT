def view_appointment_requests(shop):
    conn = connect_db()
    if not conn:
        return
    cursor = conn.cursor(dictionary=True)

    try:
        query = """
        SELECT ar.id, u.username, u.car_brand, u.car_model, u.car_year,
               ar.service_type, ar.requested_time, ar.status
        FROM appointment_requests ar
        JOIN users u ON ar.user_id = u.id
        WHERE ar.shop_id = %s AND ar.status = 'pending'
        """
        cursor.execute(query, (shop['id'],))
        requests = cursor.fetchall()

        if not requests:
            print("No pending appointment requests.")
            return

        print("\n--- Pending Appointment Requests ---")
        for req in requests:
            print(f"Request ID: {req['id']}")
            print(f"User: {req['username']}")
            print(f"Car: {req['car_brand']} {req['car_model']} ({req['car_year']})")
            print(f"Service: {req['service_type'].replace('_', ' ').title()}")
            print(f"Time: {req['requested_time']}")
            print("---")

        request_id = input("Enter request ID to approve/deny (or press Enter to exit): ").strip()
        if request_id:
            action = input("Action (1: Approve, 2: Deny): ").strip()
            if action not in ['1', '2']:
                print("Invalid action.")
                return

            status = 'approved' if action == '1' else 'denied'
            cursor.execute("""
            UPDATE appointment_requests
            SET status = %s
            WHERE id = %s AND shop_id = %s
            """, (status, request_id, shop['id']))
            if cursor.rowcount > 0:
                conn.commit()
                print(f"Request {status} successfully!")
            else:
                print("Invalid request ID.")
    except mysql.connector.Error as err:
        print(f"Error: {err}")
    finally:
        cursor.close()
        conn.close()
