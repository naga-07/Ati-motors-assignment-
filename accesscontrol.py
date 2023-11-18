import psycopg2
import threading
from contextlib import contextmanager

# Establish a connection to the PostgreSQL database
connection = psycopg2.connect(
    dbname="Project",
    user="postgres",
    password="psql@123",
    host="localhost",
    port="5432"
)

@contextmanager
def get_cursor():
    with connection:
        with connection.cursor() as cursor:
            yield cursor

# Function to request access to a resource
def request_access(device_id, resource_id):
    with get_cursor() as cursor:
        cursor.execute("SELECT category FROM resources WHERE resource_id = %s;", (resource_id,))
        category = cursor.fetchone()[0]

        if category == 'exclusive':
            # Check if the resource is already in use
            cursor.execute("SELECT COUNT(*) FROM resources WHERE resource_id = %s AND category = 'exclusive';", (resource_id,))
            count = cursor.fetchone()[0]

            if count == 0:
                # Grant access to the exclusive resource
                cursor.execute("UPDATE resources SET linked_resources = array_append(linked_resources, %s) WHERE resource_id = %s;", (device_id, resource_id,))
                print(f"Device {device_id} granted access to exclusive resource {resource_id}.")
            else:
                print(f"Exclusive resource {resource_id} is already in use.")

        elif category == 'shared':
            # Check if linked resources are available
            cursor.execute("SELECT linked_resources FROM resources WHERE resource_id = %s;", (resource_id,))
            linked_resources = cursor.fetchone()[0]

            if not linked_resources or all(linked_device == device_id for linked_device in linked_resources):
                # Grant access to the shared resource
                cursor.execute("UPDATE resources SET linked_resources = array_append(linked_resources, %s) WHERE resource_id = %s;", (device_id, resource_id,))
                print(f"Device {device_id} granted access to shared resource {resource_id}.")
            else:
                print(f"Device {device_id} cannot access linked shared resources until the first device releases its access.")
        else:
            print("Invalid resource category.")

# Function to release access to a resource
def release_access(device_id, resource_id):
    with get_cursor() as cursor:
        cursor.execute("UPDATE resources SET linked_resources = array_remove(linked_resources, %s) WHERE resource_id = %s;", (device_id, resource_id,))
        print(f"Device {device_id} released access to resource {resource_id}.")

# Example usage:
for resource_id in range(1, 51):
    request_access(1, resource_id)
    request_access(2, resource_id)

# Release access to resources
for resource_id in range(1, 51):
    release_access(1, resource_id)
    release_access(2, resource_id)