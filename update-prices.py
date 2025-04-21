def update_shop_prices(shop):
    conn = connect_db()
    if not conn:
        return
    cursor = conn.cursor()

    try:
        print("\nEnter new prices and times (press Enter to keep current):")
        oil_price = input(f"Oil change price ({shop['oil_change_price']}): ").strip()
        water_pump_price = input(f"Water pump price ({shop['water_pump_price']}): ").strip()
        belt_price = input(f"Belt price ({shop['belt_change_price']}): ").strip()
        pulleys_price = input(f"Pulleys price ({shop['pulleys_price']}): ").strip()
        filter_price = input(f"Filter price ({shop['filter_change_price']}): ").strip()
        oil_time = input(f"Oil change time (minutes) ({shop['oil_change_time']}): ").strip()
        water_pump_time = input(f"Water pump time (minutes) ({shop['water_pump_time']}): ").strip()
        belt_time = input(f"Belt time (minutes) ({shop['belt_change_time']}): ").strip()
        pulleys_time = input(f"Pulleys time (minutes) ({shop['pulleys_time']}): ").strip()
        filter_time = input(f"Filter time (minutes) ({shop['filter_change_time']}): ").strip()

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
        if oil_time:
            updates.append("oil_change_time = %s")
            params.append(int(oil_time))
        if water_pump_time:
            updates.append("water_pump_time = %s")
            params.append(int(water_pump_time))
        if belt_time:
            updates.append("belt_change_time = %s")
            params.append(int(belt_time))
        if pulleys_time:
            updates.append("pulleys_time = %s")
            params.append(int(pulleys_time))
        if filter_time:
            updates.append("filter_change_time = %s")
            params.append(int(filter_time))

        if updates:
            params.append(shop['id'])
            query = f"UPDATE repair_shops SET {', '.join(updates)} WHERE id = %s"
            cursor.execute(query, params)
            conn.commit()
            print("Prices and times updated!")
        else:
            print("No changes made.")
    except (mysql.connector.Error, ValueError) as err:
        print(f"Error: {err}")
    finally:
        cursor.close()
        conn.close()
