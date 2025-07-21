#!/usr/bin/env python3
"""
Sample web application demonstrating a basic structure
"""
from flask import Flask, render_template, request, jsonify
import sqlite3
import os

app = Flask(__name__)

class DatabaseManager:
    def __init__(self, db_path='app.db'):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                username TEXT UNIQUE,
                email TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()
        conn.close()
    
    def add_user(self, username, email):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            cursor.execute('INSERT INTO users (username, email) VALUES (?, ?)', 
                         (username, email))
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False
        finally:
            conn.close()
    
    def get_users(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users ORDER BY created_at DESC')
        users = cursor.fetchall()
        conn.close()
        return users

db = DatabaseManager()

@app.route('/')
def home():
    """Main page"""
    return render_template('index.html')

@app.route('/api/users', methods=['GET', 'POST'])
def users_api():
    """Users API endpoint"""
    if request.method == 'POST':
        data = request.get_json()
        username = data.get('username')
        email = data.get('email')
        
        if db.add_user(username, email):
            return jsonify({'success': True, 'message': 'User created'})
        else:
            return jsonify({'success': False, 'message': 'Username already exists'})
    
    else:
        users = db.get_users()
        return jsonify({'users': users})

@app.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy'})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
