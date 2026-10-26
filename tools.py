
import sqlite3


from database import DATABASE



# ----------------------------------------
# TOOL 1: CHECK INSTALLATION STATUS
# ----------------------------------------

def check_installation_status(customer_id):

    connection = sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row

    try:
        cursor = connection.cursor()

        cursor.execute("""
            SELECT customer_id, customer_name,
                   installation_date, status
            FROM installations
            WHERE customer_id = ?
        """, (customer_id,))

        customer = cursor.fetchone()

        if customer is None:
            return {"error": "Customer not found"}

        return dict(customer)

    finally:
        connection.close()


# ----------------------------------------
# TOOL 2: CREATE SUPPORT TICKET
# ----------------------------------------

def create_support_ticket(customer_id, description, priority):

    if priority not in ("low", "medium", "high"):
        raise ValueError("Invalid ticket priority")

    if not description.strip():
        raise ValueError("Ticket description cannot be empty")

    connection = sqlite3.connect(DATABASE)

    try:
        cursor = connection.cursor()

        # Confirm the fictional customer exists
        cursor.execute(
            "SELECT customer_id FROM installations WHERE customer_id = ?",
            (customer_id,)
        )

        if cursor.fetchone() is None:
            return {"error": "Customer not found"}

        # Save a new support ticket
        cursor.execute("""
            INSERT INTO support_tickets
            (customer_id, description, priority, status)
            VALUES (?, ?, ?, ?)
        """, (
            customer_id,
            description,
            priority,
            "Open"
        ))

        ticket_id = cursor.lastrowid
        connection.commit()

        return {
            "ticket_id": ticket_id,
            "customer_id": customer_id,
            "description": description,
            "priority": priority,
            "status": "Open"
        }

    finally:
        connection.close()


# ----------------------------------------
# TEST INSTALLATION LOOKUP
# ----------------------------------------

if __name__ == "__main__":

    result = check_installation_status(101)
    print("Installation Result:")
    print(result)
