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
                        print("4. Submit feedback")
                        print("5. Request appointment")
                        print("6. View appointment status")
                        print("7. Logout")
                        user_choice = input("Select option: ").strip()
                        if user_choice == '1':
                            list_repair_shops(user)
                        elif user_choice == '2':
                            update_car_info(user)
                        elif user_choice == '3':
                            rate_repair_shop(user)
                        elif user_choice == '4':
                            submit_feedback(user)
                        elif user_choice == '5':
                            request_appointment(user)
                        elif user_choice == '6':
                            view_appointment_status(user)
                        elif user_choice == '7':
                            break
                        else:
                            print("Invalid option.")
                    elif role == 'repair_shop':
                        print("\n--- Repair Shop Menu ---")
                        print("1. View rating")
                        print("2. Update prices and times")
                        print("3. Manage availability")
                        print("4. View appointment requests")
                        print("5. Logout")
                        shop_choice = input("Select option: ").strip()
                        if shop_choice == '1':
                            view_shop_rating(user)
                        elif shop_choice == '2':
                            update_shop_prices(user)
                        elif shop_choice == '3':
                            manage_shop_availability(user)
                        elif shop_choice == '4':
                            view_appointment_requests(user)
                        elif shop_choice == '5':
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
