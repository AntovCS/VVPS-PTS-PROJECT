def login():
    global failed_attempts, lockout_until
    if is_locked_out():
        return None, None

    print("\n--- Login ---")
    username = input("Enter username: ").strip()
    password = input("Enter password: ").strip()

    # Check for admin login
    if username == ADMIN_USERNAME and verify_password(password, ADMIN_PASSWORD_HASH):
        reset_lockout()
        print("Logged in as admin!")
        return {'username': ADMIN_USERNAME, 'id': 0}, 'admin'

    conn = connect_db()
    if not conn:
        return None, None
    cursor = conn.cursor(dictionary=True)

    try:
        for table, role in [('users', 'user'), ('repair_shops', 'repair_shop')]:
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
