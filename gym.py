import sys
import mysql.connector
from mysql.connector import Error

# ---------------------------------------------------------
# DATABASE CONNECTION
# ---------------------------------------------------------

print("""
________________________________________
            GYM MANAGEMENT
________________________________________
""")

try:
    mydb = mysql.connector.connect(
        host="localhost",
        user="root",
        passwd="Whythough12e?"      # 
    )
except Error as e:
    print("Could not connect to MySQL:", e)
    sys.exit(1)

# buffered=True fixes "Unread result found" errors
mycursor = mydb.cursor(buffered=True)

# Create and select database
mycursor.execute("CREATE DATABASE IF NOT EXISTS gym")
mycursor.execute("USE gym")


# ---------------------------------------------------------
# CREATE TABLES
# ---------------------------------------------------------

mycursor.execute("""
    CREATE TABLE IF NOT EXISTS fees (
        silver INT NOT NULL,
        gold INT NOT NULL,
        platinum INT NOT NULL
    )
""")

mycursor.execute("""
    CREATE TABLE IF NOT EXISTS login (
        username VARCHAR(25) NOT NULL,
        password VARCHAR(255) NOT NULL
    )
""")

mycursor.execute("""
    CREATE TABLE IF NOT EXISTS members (
        id INT PRIMARY KEY,
        name VARCHAR(25) NOT NULL,
        gender CHAR(1),
        category VARCHAR(25),
        amt INT
    )
""")

mycursor.execute("""
    CREATE TABLE IF NOT EXISTS sno (
        id INT NOT NULL,
        did INT NOT NULL
    )
""")

mycursor.execute("""
    CREATE TABLE IF NOT EXISTS trainer (
        id INT PRIMARY KEY,
        name VARCHAR(25) NOT NULL,
        age INT,
        gender CHAR(1),
        salary INT
    )
""")

mydb.commit()


# ---------------------------------------------------------
# INSERT DEFAULT DATA
# ---------------------------------------------------------

# Default login
mycursor.execute("SELECT * FROM login")
if mycursor.fetchone() is None:
    mycursor.execute(
        "INSERT INTO login (username, password) VALUES (%s, %s)",
        ("admin", "shaurya")
    )
    mydb.commit()

# Default serial numbers
mycursor.execute("SELECT * FROM sno")
if mycursor.fetchone() is None:
    mycursor.execute(
        "INSERT INTO sno (id, did) VALUES (%s, %s)",
        (0, 0)
    )
    mydb.commit()

# Default fees
mycursor.execute("SELECT * FROM fees")
if mycursor.fetchone() is None:
    mycursor.execute(
        "INSERT INTO fees (silver, gold, platinum) VALUES (%s, %s, %s)",
        (700, 600, 500)
    )
    mydb.commit()


# ---------------------------------------------------------
# HELPER FUNCTIONS
# ---------------------------------------------------------

def get_serial_numbers():
    mycursor.execute("SELECT id, did FROM sno")
    return mycursor.fetchone()


def update_serial_numbers(trainer_id=None, member_id=None):
    current_id, current_did = get_serial_numbers()

    if trainer_id is None:
        trainer_id = current_id

    if member_id is None:
        member_id = current_did

    mycursor.execute(
        "UPDATE sno SET id=%s, did=%s",
        (trainer_id, member_id)
    )
    mydb.commit()


def get_fees():
    mycursor.execute("SELECT silver, gold, platinum FROM fees")
    return mycursor.fetchone()


def valid_gender(gender):
    return gender.upper() in ("M", "F")


# ---------------------------------------------------------
# ADD TRAINER
# ---------------------------------------------------------

def add_trainer():

    print("\n---------- ADD TRAINER ----------")

    name = input("Name: ").strip()

    if not name:
        print("Name cannot be empty.")
        return

    try:
        age = int(input("Age: "))

        if age <= 0:
            print("Invalid age.")
            return

        gender = input("Gender (M/F): ").strip().upper()

        if not valid_gender(gender):
            print("Invalid gender.")
            return

        salary = int(input("Salary: "))

        if salary < 0:
            print("Salary cannot be negative.")
            return

    except ValueError:
        print("Please enter valid numerical values.")
        return

    trainer_id, member_id = get_serial_numbers()
    trainer_id += 1

    mycursor.execute("""
        INSERT INTO trainer
        (id, name, age, gender, salary)
        VALUES (%s, %s, %s, %s, %s)
    """, (trainer_id, name, age, gender, salary))

    update_serial_numbers(trainer_id, member_id)  # also commits

    print("\nTrainer added successfully.")
    print(f"Trainer ID: {trainer_id}")


# ---------------------------------------------------------
# ADD MEMBER
# ---------------------------------------------------------

def add_member():

    print("\n---------- ADD MEMBER ----------")

    name = input("Name: ").strip()

    if not name:
        print("Name cannot be empty.")
        return

    gender = input("Gender (M/F): ").strip().upper()

    if not valid_gender(gender):
        print("Invalid gender.")
        return

    silver, gold, platinum = get_fees()

    print(f"""
1. Silver     - Rs. {silver} per month
2. Gold       - Rs. {gold} per month
3. Platinum   - Rs. {platinum} per month
""")

    try:
        choice = int(input("Enter your choice: "))
    except ValueError:
        print("Invalid choice.")
        return

    if choice == 1:
        category = "Silver"
        amount = silver

    elif choice == 2:
        category = "Gold"
        amount = gold

    elif choice == 3:
        category = "Platinum"
        amount = platinum

    else:
        print("Invalid plan.")
        return

    trainer_id, member_id = get_serial_numbers()
    member_id += 1

    mycursor.execute("""
        INSERT INTO members
        (id, name, gender, category, amt)
        VALUES (%s, %s, %s, %s, %s)
    """, (member_id, name, gender, category, amount))

    update_serial_numbers(trainer_id, member_id)  # also commits

    print("\nMember added successfully.")
    print(f"Member ID: {member_id}")


# ---------------------------------------------------------
# REMOVE TRAINER
# ---------------------------------------------------------

def remove_trainer():

    print("\n---------- REMOVE TRAINER ----------")

    try:
        trainer_id = int(input("Enter trainer ID: "))
    except ValueError:
        print("Invalid ID.")
        return

    mycursor.execute("SELECT id FROM trainer WHERE id=%s", (trainer_id,))

    if mycursor.fetchone() is None:
        print("Trainer ID not found.")
        return

    mycursor.execute("DELETE FROM trainer WHERE id=%s", (trainer_id,))
    mydb.commit()

    print("Trainer successfully removed.")


# ---------------------------------------------------------
# REMOVE MEMBER
# ---------------------------------------------------------

def remove_member():

    print("\n---------- REMOVE MEMBER ----------")

    try:
        member_id = int(input("Enter member ID: "))
    except ValueError:
        print("Invalid ID.")
        return

    mycursor.execute("SELECT id FROM members WHERE id=%s", (member_id,))

    if mycursor.fetchone() is None:
        print("Member ID not found.")
        return

    mycursor.execute("DELETE FROM members WHERE id=%s", (member_id,))
    mydb.commit()

    print("Member successfully removed.")


# ---------------------------------------------------------
# MODIFY FEES
# ---------------------------------------------------------

def modify_plans():

    print("""
---------- MODIFY PLANS ----------

1. Silver
2. Gold
3. Platinum
""")

    try:
        choice = int(input("Enter your choice: "))
        amount = int(input("Enter new monthly amount: "))

        if amount < 0:
            print("Amount cannot be negative.")
            return

    except ValueError:
        print("Please enter valid numbers.")
        return

    if choice == 1:
        mycursor.execute("UPDATE fees SET silver=%s", (amount,))

    elif choice == 2:
        mycursor.execute("UPDATE fees SET gold=%s", (amount,))

    elif choice == 3:
        mycursor.execute("UPDATE fees SET platinum=%s", (amount,))

    else:
        print("Invalid choice.")
        return

    mydb.commit()

    print("Plan amount successfully updated.")


# ---------------------------------------------------------
# MODIFY TRAINER
# ---------------------------------------------------------

def modify_trainer():

    try:
        trainer_id = int(input("Enter trainer ID to edit: "))
    except ValueError:
        print("Invalid ID.")
        return

    mycursor.execute("SELECT * FROM trainer WHERE id=%s", (trainer_id,))

    if mycursor.fetchone() is None:
        print("Trainer ID not found.")
        return

    print("""
1. Name
2. Age
3. Gender
4. Salary
""")

    try:
        choice = int(input("Enter your choice: "))
    except ValueError:
        print("Invalid choice.")
        return

    if choice == 1:

        name = input("Enter updated name: ").strip()

        if not name:
            print("Name cannot be empty.")
            return

        mycursor.execute(
            "UPDATE trainer SET name=%s WHERE id=%s",
            (name, trainer_id)
        )

    elif choice == 2:

        try:
            age = int(input("Enter updated age: "))

            if age <= 0:
                print("Invalid age.")
                return

        except ValueError:
            print("Invalid age.")
            return

        mycursor.execute(
            "UPDATE trainer SET age=%s WHERE id=%s",
            (age, trainer_id)
        )

    elif choice == 3:

        gender = input("Enter updated gender (M/F): ").strip().upper()

        if not valid_gender(gender):
            print("Invalid gender.")
            return

        mycursor.execute(
            "UPDATE trainer SET gender=%s WHERE id=%s",
            (gender, trainer_id)
        )

    elif choice == 4:

        try:
            salary = int(input("Enter updated salary: "))

            if salary < 0:
                print("Salary cannot be negative.")
                return

        except ValueError:
            print("Invalid salary.")
            return

        mycursor.execute(
            "UPDATE trainer SET salary=%s WHERE id=%s",
            (salary, trainer_id)
        )

    else:
        print("Invalid choice.")
        return

    mydb.commit()

    print("Trainer information successfully updated.")


# ---------------------------------------------------------
# MODIFY MEMBER
# ---------------------------------------------------------

def modify_member():

    try:
        member_id = int(input("Enter member ID to edit: "))
    except ValueError:
        print("Invalid ID.")
        return

    mycursor.execute("SELECT * FROM members WHERE id=%s", (member_id,))

    if mycursor.fetchone() is None:
        print("Member ID not found.")
        return

    print("""
1. Name
2. Gender
3. Category
""")

    try:
        choice = int(input("Enter your choice: "))
    except ValueError:
        print("Invalid choice.")
        return

    if choice == 1:

        name = input("Enter updated name: ").strip()

        if not name:
            print("Name cannot be empty.")
            return

        mycursor.execute(
            "UPDATE members SET name=%s WHERE id=%s",
            (name, member_id)
        )

    elif choice == 2:

        gender = input("Enter updated gender (M/F): ").strip().upper()

        if not valid_gender(gender):
            print("Invalid gender.")
            return

        mycursor.execute(
            "UPDATE members SET gender=%s WHERE id=%s",
            (gender, member_id)
        )

    elif choice == 3:

        print("""
1. Silver
2. Gold
3. Platinum
""")

        try:
            plan = int(input("Enter your choice: "))
        except ValueError:
            print("Invalid choice.")
            return

        silver, gold, platinum = get_fees()

        if plan == 1:
            category = "Silver"
            amount = silver

        elif plan == 2:
            category = "Gold"
            amount = gold

        elif plan == 3:
            category = "Platinum"
            amount = platinum

        else:
            print("Invalid plan.")
            return

        mycursor.execute("""
            UPDATE members
            SET category=%s, amt=%s
            WHERE id=%s
        """, (category, amount, member_id))

    else:
        print("Invalid choice.")
        return

    mydb.commit()

    print("Member information successfully updated.")


# ---------------------------------------------------------
# MODIFY MENU
# ---------------------------------------------------------

def modify():

    while True:

        print("""
---------- MODIFY ----------

1. Plans
2. Trainer Information
3. Member Information
4. Main Menu
""")

        try:
            choice = int(input("Enter your choice: "))
        except ValueError:
            print("Invalid choice.")
            continue

        if choice == 1:
            modify_plans()

        elif choice == 2:
            modify_trainer()

        elif choice == 3:
            modify_member()

        elif choice == 4:
            break

        else:
            print("Invalid choice.")


# ---------------------------------------------------------
# CHANGE PASSWORD
# ---------------------------------------------------------

def change_password():

    print("\n---------- CHANGE PASSWORD ----------")

    old_password = input("Enter old password: ")

    mycursor.execute(
        "SELECT password FROM login WHERE username=%s",
        ("admin",)
    )

    result = mycursor.fetchone()

    if result is None:
        print("Login information not found.")
        return

    if old_password != result[0]:
        print("Wrong password.")
        return

    new_password = input("Enter new password: ")

    if not new_password:
        print("Password cannot be empty.")
        return

    mycursor.execute(
        "UPDATE login SET password=%s WHERE username=%s",
        (new_password, "admin")
    )
    mydb.commit()

    print("Password successfully changed.")


# ---------------------------------------------------------
# DISPLAY MEMBERS
# ---------------------------------------------------------

def display_members():

    mycursor.execute("SELECT * FROM members")
    members = mycursor.fetchall()

    print("\n---------- MEMBERS ----------")

    if not members:
        print("No members found.")
        return

    print(
        f"{'ID':<5}"
        f"{'Name':<20}"
        f"{'Gender':<10}"
        f"{'Category':<15}"
        f"{'Amount':<10}"
    )

    print("-" * 60)

    for member in members:
        print(
            f"{member[0]:<5}"
            f"{member[1]:<20}"
            f"{str(member[2]):<10}"
            f"{str(member[3]):<15}"
            f"{str(member[4]):<10}"
        )


# ---------------------------------------------------------
# DISPLAY TRAINERS
# ---------------------------------------------------------

def display_trainers():

    mycursor.execute("SELECT * FROM trainer")
    trainers = mycursor.fetchall()

    print("\n---------- TRAINERS ----------")

    if not trainers:
        print("No trainers found.")
        return

    print(
        f"{'ID':<5}"
        f"{'Name':<20}"
        f"{'Age':<8}"
        f"{'Gender':<10}"
        f"{'Salary':<10}"
    )

    print("-" * 55)

    for trainer in trainers:
        print(
            f"{trainer[0]:<5}"
            f"{trainer[1]:<20}"
            f"{str(trainer[2]):<8}"
            f"{str(trainer[3]):<10}"
            f"{str(trainer[4]):<10}"
        )


# ---------------------------------------------------------
# LOGIN
# ---------------------------------------------------------

def login():

    print("\n---------- LOGIN ----------")

    username = input("Username: ")
    password = input("Password: ")

    mycursor.execute(
        "SELECT username, password FROM login WHERE username=%s",
        (username,)
    )

    result = mycursor.fetchone()

    if result is None or result[1] != password:
        print("Invalid username or password.")
        return False

    print("\nLogin successful.")
    return True


# ---------------------------------------------------------
# ADMIN MENU
# ---------------------------------------------------------

def admin_menu():

    while True:

        print("""
________________________________________
              ADMIN MENU
________________________________________

1. Add Trainer
2. Add Member
3. Remove Trainer
4. Remove Member
5. Modify
6. Change Password
7. Display Trainers
8. Display Members
9. Main Menu
""")

        try:
            choice = int(input("Enter your choice: "))
        except ValueError:
            print("Please enter a valid number.")
            continue

        if choice == 1:
            add_trainer()

        elif choice == 2:
            add_member()

        elif choice == 3:
            remove_trainer()

        elif choice == 4:
            remove_member()

        elif choice == 5:
            modify()

        elif choice == 6:
            change_password()

        elif choice == 7:
            display_trainers()

        elif choice == 8:
            display_members()

        elif choice == 9:
            break

        else:
            print("Invalid choice.")


# ---------------------------------------------------------
# MAIN PROGRAM
# ---------------------------------------------------------

try:

    while True:

        print("""
________________________________________
              MAIN MENU
________________________________________

1. Login
2. Exit
""")

        try:
            choice = int(input("Enter your choice: "))
        except ValueError:
            print("Please enter a valid number.")
            continue

        if choice == 1:

            if login():
                admin_menu()

        elif choice == 2:

            print("\nThank you for using Gym Management System.")
            break

        else:
            print("Invalid choice.")

except KeyboardInterrupt:
    print("\nExiting...")

finally:

    mycursor.close()
    mydb.close()