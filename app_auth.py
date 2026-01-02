# app_auth.py - Flask Backend with Authentication and MS SQL Server

from flask import Flask, request, jsonify
from flask_cors import CORS
import pyodbc
import hashlib
import json
from datetime import datetime

app = Flask(__name__)
CORS(app)

# MS SQL Server Configuration (Windows Authentication)
DB_CONFIG = {
    'server': 'DESKTOP-EJQET3M\\SQLEXPRESS',  # Change to your server name
    'database': 'Resume',
    'driver': '{ODBC Driver 17 for SQL Server}'
}

def get_db_connection():
    """Create and return database connection"""
    try:
        conn_str = (
            f"DRIVER={DB_CONFIG['driver']};"
            f"SERVER={DB_CONFIG['server']};"
            f"DATABASE={DB_CONFIG['database']};"
            "Trusted_Connection=yes;"
        )
        conn = pyodbc.connect(conn_str)
        return conn
    except Exception as e:
        print(f"Database connection error: {str(e)}")
        raise

def hash_password(password):
    """Hash password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def init_db():
    """Initialize database with tables"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Create users table
        cursor.execute('''
            IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='users' AND xtype='U')
            CREATE TABLE users (
                id INT IDENTITY(1,1) PRIMARY KEY,
                username NVARCHAR(100) UNIQUE NOT NULL,
                password NVARCHAR(255) NOT NULL,
                first_name NVARCHAR(100) NOT NULL,
                last_name NVARCHAR(100) NOT NULL,
                email NVARCHAR(255) UNIQUE NOT NULL,
                phone NVARCHAR(50) NOT NULL,
                created_at DATETIME DEFAULT GETDATE(),
                updated_at DATETIME DEFAULT GETDATE()
            )
        ''')
        
        # Create resumes table with user_id
        cursor.execute('''
            IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='resumes' AND xtype='U')
            CREATE TABLE resumes (
                id INT IDENTITY(1,1) PRIMARY KEY,
                user_id INT NOT NULL,
                name NVARCHAR(255) NOT NULL,
                email NVARCHAR(255) NOT NULL,
                phone NVARCHAR(50) NOT NULL,
                dob NVARCHAR(50),
                linkedin NVARCHAR(500),
                github NVARCHAR(500),
                objective NVARCHAR(MAX),
                profile_picture NVARCHAR(MAX),
                created_at DATETIME DEFAULT GETDATE(),
                updated_at DATETIME DEFAULT GETDATE(),
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        ''')
        
        # Create work_experience table
        cursor.execute('''
            IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='work_experience' AND xtype='U')
            CREATE TABLE work_experience (
                id INT IDENTITY(1,1) PRIMARY KEY,
                resume_id INT NOT NULL,
                company NVARCHAR(255) NOT NULL,
                position NVARCHAR(255) NOT NULL,
                start_date NVARCHAR(50) NOT NULL,
                end_date NVARCHAR(50) NOT NULL,
                experience NVARCHAR(100),
                description NVARCHAR(MAX),
                FOREIGN KEY (resume_id) REFERENCES resumes(id) ON DELETE CASCADE
            )
        ''')
        
        # Create education table
        cursor.execute('''
            IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='education' AND xtype='U')
            CREATE TABLE education (
                id INT IDENTITY(1,1) PRIMARY KEY,
                resume_id INT NOT NULL,
                institution NVARCHAR(255) NOT NULL,
                degree NVARCHAR(255) NOT NULL,
                year NVARCHAR(50) NOT NULL,
                details NVARCHAR(MAX),
                FOREIGN KEY (resume_id) REFERENCES resumes(id) ON DELETE CASCADE
            )
        ''')
        
        # Create projects table
        cursor.execute('''
            IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='projects' AND xtype='U')
            CREATE TABLE projects (
                id INT IDENTITY(1,1) PRIMARY KEY,
                resume_id INT NOT NULL,
                title NVARCHAR(255) NOT NULL,
                description NVARCHAR(MAX) NOT NULL,
                technologies NVARCHAR(MAX) NOT NULL,
                FOREIGN KEY (resume_id) REFERENCES resumes(id) ON DELETE CASCADE
            )
        ''')
        
        # Create skills table
        cursor.execute('''
            IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='skills' AND xtype='U')
            CREATE TABLE skills (
                id INT IDENTITY(1,1) PRIMARY KEY,
                resume_id INT NOT NULL,
                category NVARCHAR(255) NOT NULL,
                skills_list NVARCHAR(MAX) NOT NULL,
                FOREIGN KEY (resume_id) REFERENCES resumes(id) ON DELETE CASCADE
            )
        ''')
        
        # Create hobbies table
        cursor.execute('''
            IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='hobbies' AND xtype='U')
            CREATE TABLE hobbies (
                id INT IDENTITY(1,1) PRIMARY KEY,
                resume_id INT NOT NULL,
                hobby NVARCHAR(255) NOT NULL,
                FOREIGN KEY (resume_id) REFERENCES resumes(id) ON DELETE CASCADE
            )
        ''')
        
        # Create certifications table
        cursor.execute('''
            IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='certifications' AND xtype='U')
            CREATE TABLE certifications (
                id INT IDENTITY(1,1) PRIMARY KEY,
                resume_id INT NOT NULL,
                name NVARCHAR(255) NOT NULL,
                issuer NVARCHAR(255) NOT NULL,
                year NVARCHAR(50) NOT NULL,
                FOREIGN KEY (resume_id) REFERENCES resumes(id) ON DELETE CASCADE
            )
        ''')
        
        conn.commit()
        cursor.close()
        conn.close()
        print("✅ Database initialized successfully!")
        print(f"✅ Connected to: {DB_CONFIG['server']} - {DB_CONFIG['database']}")
        
    except Exception as e:
        print(f"❌ Error initializing database: {str(e)}")

# Initialize database on startup
try:
    init_db()
except Exception as e:
    print(f"⚠️ Warning: Could not initialize database - {str(e)}")

# ==================== AUTHENTICATION ENDPOINTS ====================

@app.route('/')
def home():
    return jsonify({
        "message": "Resume Builder API with Authentication",
        "database": "MS SQL Server",
        "authentication": "Windows Authentication"
    })

# REGISTER - Create new user account
@app.route('/api/register', methods=['POST'])
def register():
    try:
        data = request.json
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if username already exists
        cursor.execute('SELECT id FROM users WHERE username = ?', (data['username'],))
        if cursor.fetchone():
            return jsonify({
                "success": False,
                "message": "Username already exists"
            }), 400
        
        # Check if email already exists
        cursor.execute('SELECT id FROM users WHERE email = ?', (data['email'],))
        if cursor.fetchone():
            return jsonify({
                "success": False,
                "message": "Email already registered"
            }), 400
        
        # Hash password
        hashed_password = hash_password(data['password'])
        
        # Insert new user
        cursor.execute('''
            INSERT INTO users (username, password, first_name, last_name, email, phone)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            data['username'],
            hashed_password,
            data['firstName'],
            data['lastName'],
            data['email'],
            data['phone']
        ))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({
            "success": True,
            "message": "Account created successfully!"
        }), 201
        
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Error creating account: {str(e)}"
        }), 500

# LOGIN - Authenticate user
@app.route('/api/login', methods=['POST'])
def login():
    try:
        data = request.json
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Hash the provided password
        hashed_password = hash_password(data['password'])
        
        # Find user
        cursor.execute('''
            SELECT id, username, first_name, last_name, email, phone, created_at
            FROM users 
            WHERE username = ? AND password = ?
        ''', (data['username'], hashed_password))
        
        row = cursor.fetchone()
        
        if not row:
            return jsonify({
                "success": False,
                "message": "Invalid username or password"
            }), 401
        
        # Create user object
        user = {
            "id": row[0],
            "username": row[1],
            "firstName": row[2],
            "lastName": row[3],
            "email": row[4],
            "phone": row[5],
            "created_at": row[6].isoformat() if row[6] else None
        }
        
        cursor.close()
        conn.close()
        
        return jsonify({
            "success": True,
            "message": "Login successful!",
            "user": user
        }), 200
        
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Error logging in: {str(e)}"
        }), 500

# ==================== RESUME ENDPOINTS ====================

# CREATE - Save new resume (with user_id)
@app.route('/api/resume', methods=['POST'])
def create_resume():
    try:
        data = request.json
        user_id = data.get('user_id')
        
        if not user_id:
            return jsonify({
                "success": False,
                "message": "User ID is required"
            }), 400
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Insert basic information
        cursor.execute('''
            INSERT INTO resumes (user_id, name, email, phone, dob, linkedin, github, objective, profile_picture)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            user_id,
            data['name'],
            data['email'],
            data['phone'],
            data.get('dob', ''),
            data.get('linkedin', ''),
            data.get('github', ''),
            data.get('objective', ''),
            data.get('profilePicture', '')
        ))
        
        cursor.execute('SELECT @@IDENTITY')
        resume_id = cursor.fetchone()[0]
        
        # Insert work experience
        for work in data.get('workExperience', []):
            cursor.execute('''
                INSERT INTO work_experience (resume_id, company, position, start_date, end_date, experience, description)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (resume_id, work['company'], work['position'], work['startDate'], 
                  work['endDate'], work['experience'], work['description']))
        
        # Insert education
        for edu in data.get('education', []):
            cursor.execute('''
                INSERT INTO education (resume_id, institution, degree, year, details)
                VALUES (?, ?, ?, ?, ?)
            ''', (resume_id, edu['institution'], edu['degree'], edu['year'], edu.get('details', '')))
        
        # Insert projects
        for project in data.get('projects', []):
            cursor.execute('''
                INSERT INTO projects (resume_id, title, description, technologies)
                VALUES (?, ?, ?, ?)
            ''', (resume_id, project['title'], project['description'], project['technologies']))
        
        # Insert skills
        for skill in data.get('skills', []):
            cursor.execute('''
                INSERT INTO skills (resume_id, category, skills_list)
                VALUES (?, ?, ?)
            ''', (resume_id, skill['category'], skill['items']))
        
        # Insert hobbies
        for hobby in data.get('hobbies', []):
            cursor.execute('''
                INSERT INTO hobbies (resume_id, hobby)
                VALUES (?, ?)
            ''', (resume_id, hobby['hobby']))
        
        # Insert certifications
        for cert in data.get('certifications', []):
            cursor.execute('''
                INSERT INTO certifications (resume_id, name, issuer, year)
                VALUES (?, ?, ?, ?)
            ''', (resume_id, cert['name'], cert['issuer'], cert['year']))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({
            "success": True,
            "message": "Resume saved successfully!",
            "resume_id": int(resume_id)
        }), 201
        
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Error saving resume: {str(e)}"
        }), 500

# GET - Get all resumes for a user
@app.route('/api/user/<int:user_id>/resumes', methods=['GET'])
def get_user_resumes(user_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM resumes WHERE user_id = ? ORDER BY created_at DESC', (user_id,))
        columns = [column[0] for column in cursor.description]
        resumes = []
        
        for row in cursor.fetchall():
            resumes.append(dict(zip(columns, row)))
        
        cursor.close()
        conn.close()
        
        return jsonify({
            "success": True,
            "count": len(resumes),
            "resumes": resumes
        }), 200
        
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Error fetching resumes: {str(e)}"
        }), 500

# GET - Get single resume by ID
@app.route('/api/resume/<int:resume_id>', methods=['GET'])
def get_resume(resume_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM resumes WHERE id = ?', (resume_id,))
        columns = [column[0] for column in cursor.description]
        row = cursor.fetchone()
        
        if not row:
            return jsonify({
                "success": False,
                "message": "Resume not found"
            }), 404
        
        resume = dict(zip(columns, row))
        
        # Get all related data
        cursor.execute('SELECT * FROM work_experience WHERE resume_id = ?', (resume_id,))
        columns = [column[0] for column in cursor.description]
        resume['workExperience'] = [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        cursor.execute('SELECT * FROM education WHERE resume_id = ?', (resume_id,))
        columns = [column[0] for column in cursor.description]
        resume['education'] = [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        cursor.execute('SELECT * FROM projects WHERE resume_id = ?', (resume_id,))
        columns = [column[0] for column in cursor.description]
        resume['projects'] = [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        cursor.execute('SELECT * FROM skills WHERE resume_id = ?', (resume_id,))
        columns = [column[0] for column in cursor.description]
        resume['skills'] = [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        cursor.execute('SELECT * FROM hobbies WHERE resume_id = ?', (resume_id,))
        columns = [column[0] for column in cursor.description]
        resume['hobbies'] = [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        cursor.execute('SELECT * FROM certifications WHERE resume_id = ?', (resume_id,))
        columns = [column[0] for column in cursor.description]
        resume['certifications'] = [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        cursor.close()
        conn.close()
        
        return jsonify({
            "success": True,
            "resume": resume
        }), 200
        
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Error fetching resume: {str(e)}"
        }), 500

# DELETE - Delete resume
@app.route('/api/resume/<int:resume_id>', methods=['DELETE'])
def delete_resume(resume_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM resumes WHERE id = ?', (resume_id,))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({
            "success": True,
            "message": "Resume deleted successfully!"
        }), 200
        
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Error deleting resume: {str(e)}"
        }), 500

if __name__ == '__main__':
    print("="*60)
    print("Resume Builder API - Authentication Enabled")
    print("="*60)
    print(f"Server: {DB_CONFIG['server']}")
    print(f"Database: {DB_CONFIG['database']}")
    print(f"Authentication: Windows Authentication")
    print("="*60)
    print("API running at: http://localhost:5000")
    print("="*60)
    app.run(debug=True, host='0.0.0.0', port=5000)
