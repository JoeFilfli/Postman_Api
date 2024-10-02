#!/usr/bin/python
import sqlite3
from flask import Flask, request, jsonify
from flask_cors import CORS
import json
# Database Functions
def connect_to_db():
    conn = sqlite3.connect('database.db')
    return conn

def create_db_table():
    try:
        conn = connect_to_db()
        conn.execute('''
        CREATE TABLE users (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            phone TEXT NOT NULL,
            address TEXT NOT NULL,
            country TEXT NOT NULL
        );
        ''')
        conn.commit()
        print("User table created successfully")
    except Exception as e:
        print(f"User table creation failed: {e}")
    finally:
        conn.close()

def drop_table():
    try:
        conn = connect_to_db()
        conn.execute('DROP TABLE IF EXISTS users;')
        conn.commit()
        print("Table dropped successfully")
    except Exception as e:
        print(f"Failed to drop table: {e}")
    finally:
        conn.close()


def insert_user(user):
    inserted_user = {}
    try:
        conn = connect_to_db()
        cur = conn.cursor()
        
        # Attempt to insert the user
        cur.execute(
            "INSERT INTO users (name, email, phone, address, country) VALUES (?, ?, ?, ?, ?)", 
            (user['name'], user['email'], user['phone'], user['address'], user['country'])
        )
        conn.commit()

        # Check the last inserted row ID
        last_id = cur.lastrowid
        print(f"Last inserted row ID: {last_id}")  # Debugging statement

        if last_id:
            inserted_user = get_user_by_id(last_id)
        else:
            print("Insertion failed: lastrowid is None")
    except Exception as e:
        print(f"Failed to insert user: {e}")  # Detailed error output
        conn.rollback()
    finally:
        conn.close()
    
    return inserted_user

def get_users():
    users = []
    try:
        conn = connect_to_db()
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute("SELECT * FROM users")
        rows = cur.fetchall()
        
        # Convert row objects to dictionary
        for i in rows:
            user = {
                "user_id": i["user_id"],
                "name": i["name"],
                "email": i["email"],
                "phone": i["phone"],
                "address": i["address"],
                "country": i["country"]
            }
            users.append(user)
    except Exception as e:
        print(f"Failed to get users: {e}")
    return users

def get_user_by_id(user_id):
    user = {}
    try:
        conn = connect_to_db()
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
        row = cur.fetchone()

        # Check if the row is not None
        if row:
            # Convert row object to dictionary
            user = {
                "user_id": row["user_id"],
                "name": row["name"],
                "email": row["email"],
                "phone": row["phone"],
                "address": row["address"],
                "country": row["country"]
            }
        else:
            print(f"No user found with user_id: {user_id}")
    except Exception as e:
        print(f"Failed to get user by id: {e}")
    finally:
        conn.close()
    
    return user


def update_user(user):
    updated_user = {}
    try:
        conn = connect_to_db()
        cur = conn.cursor()
        cur.execute("UPDATE users SET name = ?, email = ?, phone = ?, address = ?, country = ? WHERE user_id = ?",
                    (user["name"], user["email"], user["phone"], user["address"], user["country"], user["user_id"]))
        conn.commit()
        # Return the updated user
        updated_user = get_user_by_id(user["user_id"])
    except Exception as e:
        print(f"Failed to update user: {e}")
        conn.rollback()
    finally:
        conn.close()
    return updated_user

def delete_user(user_id):
    message = {}
    try:
        conn = connect_to_db()
        conn.execute("DELETE FROM users WHERE user_id = ?", (user_id,))
        conn.commit()
        message["status"] = "User deleted successfully"
    except Exception as e:
        print(f"Failed to delete user: {e}")
        conn.rollback()
        message["status"] = "Cannot delete user"
    finally:
        conn.close()
    return message

# PATCH User Function
def patch_user(user_data):
    updated_user = {}
    try:
        conn = connect_to_db()
        cur = conn.cursor()

        # Construct the SQL query dynamically based on the provided fields
        query = "UPDATE users SET "
        fields = []
        values = []

        if 'name' in user_data:
            fields.append("name = ?")
            values.append(user_data['name'])
        if 'email' in user_data:
            fields.append("email = ?")
            values.append(user_data['email'])
        if 'phone' in user_data:
            fields.append("phone = ?")
            values.append(user_data['phone'])
        if 'address' in user_data:
            fields.append("address = ?")
            values.append(user_data['address'])
        if 'country' in user_data:
            fields.append("country = ?")
            values.append(user_data['country'])

        # If no fields are provided, return an error
        if not fields:
            return {"error": "No fields to update provided"}, 400

        # Append user_id to the values list for the WHERE clause
        query += ", ".join(fields) + " WHERE user_id = ?"
        values.append(user_data['user_id'])

        # Execute the query
        cur.execute(query, values)
        conn.commit()

        # Retrieve and return the updated user
        updated_user = get_user_by_id(user_data['user_id'])
    except Exception as e:
        print(f"Failed to update user: {e}")
        conn.rollback()
    finally:
        conn.close()

    return updated_user

# REST API Implementation
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})
@app.route('/')
def home():
    return "Welcome to the User Management API!"

@app.route('/api/users', methods=['GET'])
def api_get_users():
    return jsonify(get_users())

@app.route('/api/users/<user_id>', methods=['GET'])
def api_get_user(user_id):
    return jsonify(get_user_by_id(user_id))

@app.route('/api/users/add', methods=['POST'])
def api_add_user():
    user = request.get_json()
    return jsonify(insert_user(user))

@app.route('/api/users/update', methods=['PUT'])
def api_update_user():
    user = request.get_json()
    return jsonify(update_user(user))

@app.route('/api/users/delete/<user_id>', methods=['DELETE'])
def api_delete_user(user_id):
    return jsonify(delete_user(user_id))

@app.route('/api/users/update', methods=['PATCH'])
def api_patch_user():
    user_data = request.get_json()
    return jsonify(patch_user(user_data))

if __name__ == "__main__":
    app.run()
