# Name: Tsegawit Gebremedhin
# Date: October 2, 2026
# Assignment: Performance Assessment - Python Application Accessing a Column Family Database
# Purpose: Interactive menu-driven CRUD application using cassandra-driver to manipulate Amazon datasets.

import json
from cassandra.cluster import Cluster

def main():
    print("Connecting to local Cassandra database...")
    cluster = Cluster()
    session = cluster.connect()

    # *Create a new keyspace in the Cassandra database named Amazon
    session.execute("""
        CREATE KEYSPACE IF NOT EXISTS Amazon WITH 
        replication = {'class': 'SimpleStrategy', 'replication_factor': 1};
    """)
    session.execute("USE Amazon;")

    # *Create a new table in the Cassandra database named Reviews
    session.execute("""
        CREATE TABLE IF NOT EXISTS Reviews (
            review_id text PRIMARY KEY,
            product_id text,
            reviewer_id text,
            stars int,
            review_body text,
            review_title text,
            product_category text
        );
    """)

    # *Create a new table in the Cassandra database named ProductCategories
    session.execute("""
        CREATE TABLE IF NOT EXISTS ProductCategories (
            product_category text,
            stars int,
            product_id text,
            language text,
            PRIMARY KEY ((product_category), stars, product_id)
        );
    """)

    # *Insert data from the JSON file into the Reviews and ProductCategories tables
    print("Importing dataset records...")
    try:
        for line in open('dataset_en_dev.json', 'r'):
            data = json.loads(line)
            
            # Insert into Reviews
            session.execute("""
                INSERT INTO Reviews (review_id, product_id, reviewer_id, stars, review_body, review_title, product_category)
                VALUES (%s, %s, %s, %s, %s, %s, %s);
            """, (data["review_id"], data["product_id"], data["reviewer_id"], int(data["stars"]), data["review_body"], data["review_title"], data["product_category"]))
            
            # Insert into ProductCategories
            session.execute("""
                INSERT INTO ProductCategories (product_category, stars, product_id, language)
                VALUES (%s, %s, %s, %s);
            """, (data["product_category"], int(data["stars"]), data["product_id"], data["language"]))
        print("Data imported successfully!\n")
    except FileNotFoundError:
        print("Dataset file not found in current directory. Continuing to menu...\n")

    while True:
        # Menu options matching professor's sample images exactly
        print("Type a number and press enter to execute the menu option.")
        print("1. Display product category list")
        print("2. Display high (4+) star review count")
        print("3. Display low (1) star review count")
        print("4. Enter a query")
        print("5. Add/Remove table columns")
        print("6. Delete tables")
        print("7. Delete keyspace")
        print("8. Exit the program")
        
        choice = input().strip()

        # *Display all distinct product categories from the ProductCategories table
        if choice == "1":
            print("\nProduct Category List:")
            results = session.execute("SELECT DISTINCT product_category FROM ProductCategories;")
            for row in results:
                print(f"Row(category='{row.product_category}')")
            print()

        # *Display the count of 4-star and higher reviews for a user-entered product category
        elif choice == "2":
            category = input("Which category would you like to check the high review count of?\n").strip()
            query = "SELECT COUNT(*) FROM ProductCategories WHERE product_category = %s AND stars >= 4;"
            result = session.execute(query, [category])
            print(f"\nNumber of 4 and 5 star reviews in the {category} category: Row(count={result.one()[0]})\n")

        # *Display the count of 1-star reviews for a user-entered product category
        elif choice == "3":
            category = input("Which category would you like to check the low review count of?\n").strip()
            query = "SELECT COUNT(*) FROM ProductCategories WHERE product_category = %s AND stars = 1;"
            result = session.execute(query, [category])
            print(f"\nNumber of 1 star reviews in the {category} category: Row(count={result.one()[0]})\n")

        # *Allow the user to type in and execute CQL SELECT statements
        elif choice == "4":
            user_query = input("Enter the query you wish to run on the Amazon keyspace:\n").strip()
            try:
                results = session.execute(user_query)
                for row in results:
                    print(row)
            except Exception as e:
                print(f"Error executing query: {e}")
            print()

        # *Allow the user to add and remove columns from the Reviews and ProductCategories tables
        elif choice == "5":
            table = input("Which table would you like to alter?\n").strip()
            action = input("Type 1 to add a new column, or 2 to remove a column.\n").strip()
            
            if action == "1":
                col_name = input("Enter the name of the column you wish to add:\n").strip()
                col_type = input("Enter the data type of the column:\n").strip()
                session.execute(f"ALTER TABLE {table} ADD {col_name} {col_type};")
                print("Complete!\n")
            elif action == "2":
                col_name = input("Enter the name of the column you wish to remove:\n").strip()
                session.execute(f"ALTER TABLE {table} DROP {col_name};")
                print("Complete!\n")

        # *Allow the user to delete the Reviews and ProductCategories tables
        elif choice == "6":
            session.execute("DROP TABLE IF EXISTS Reviews;")
            session.execute("DROP TABLE IF EXISTS ProductCategories;")
            print("Reviews and ProductCategories tables removed!\n")

        # *Allow the user to delete the Amazon keyspace
        elif choice == "7":
            session.execute("DROP KEYSPACE IF EXISTS Amazon;")
            print("Amazon keyspace removed!\n")

        elif choice == "8":
            print("Exiting application.")
            break
        else:
            print("Invalid numerical selection. Choose 1-8.\n")

    cluster.shutdown()

if __name__ == "__main__":
    main()
