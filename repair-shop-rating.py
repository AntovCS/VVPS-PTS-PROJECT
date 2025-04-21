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
