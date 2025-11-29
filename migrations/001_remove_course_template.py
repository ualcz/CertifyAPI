"""
Migration: Remove certificate_template from courses and add timestamp columns

This migration:
1. Removes the certificate_template column from courses (now in Class)
2. Adds created_at and updated_at columns with proper defaults

IMPORTANT: Run this after deploying the new code.
"""

import sqlite3
import os
from datetime import datetime


def migrate():
    """Execute the migration."""
    db_path = "certify.db"
    
    if not os.path.exists(db_path):
        print(f"❌ Database file {db_path} not found!")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("🔄 Applying migration...")
        current_timestamp = datetime.now().isoformat()
        
        # ========== MIGRATE COURSES TABLE ==========
        cursor.execute("PRAGMA table_info(courses)")
        course_columns = [row[1] for row in cursor.fetchall()]
        
        if 'certificate_template' in course_columns:
            print("   📦 Migrating courses table...")
            
            # Get existing data
            cursor.execute("SELECT id, name, description, workload, is_active FROM courses")
            courses_data = cursor.fetchall()
            
            # Drop and recreate with timestamps
            cursor.execute("DROP TABLE courses")
            cursor.execute("""
                CREATE TABLE courses (
                    id INTEGER PRIMARY KEY,
                    name VARCHAR NOT NULL,
                    description VARCHAR,
                    workload FLOAT NOT NULL,
                    is_active BOOLEAN NOT NULL DEFAULT 1,
                    created_at TIMESTAMP NOT NULL,
                    updated_at TIMESTAMP NOT NULL
                )
            """)
            
            # Reinsert data with timestamps
            for row in courses_data:
                cursor.execute("""
                    INSERT INTO courses (id, name, description, workload, is_active, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (*row, current_timestamp, current_timestamp))
            
            # Recreate indexes
            cursor.execute("CREATE INDEX ix_courses_id ON courses (id)")
            cursor.execute("CREATE INDEX ix_courses_name ON courses (name)")
            
            print("   ✅ Courses table migrated (removed certificate_template, added timestamps)")
        else:
            print("   ℹ️  Courses table already migrated")
        
        # ========== MIGRATE CLASSES TABLE ==========
        cursor.execute("PRAGMA table_info(classes)")
        class_columns = [row[1] for row in cursor.fetchall()]
        
        if 'created_at' not in class_columns:
            print("   📦 Adding timestamps to classes table...")
            
            # SQLite workaround: recreate table
            cursor.execute("SELECT * FROM classes")
            classes_data = cursor.fetchall()
            cursor.execute("PRAGMA table_info(classes)")
            original_columns = [row[1] for row in cursor.fetchall()]
            
            # Backup and recreate
            cursor.execute("ALTER TABLE classes RENAME TO classes_old")
            
            cursor.execute("""
                CREATE TABLE classes (
                    id INTEGER PRIMARY KEY,
                    course_id INTEGER NOT NULL,
                    name VARCHAR NOT NULL,
                    total_slots INTEGER NOT NULL,
                    available_slots INTEGER NOT NULL,
                    certificate_template VARCHAR NOT NULL DEFAULT 'default',
                    is_open BOOLEAN NOT NULL DEFAULT 1,
                    is_active BOOLEAN NOT NULL DEFAULT 1,
                    start_date TIMESTAMP,
                    end_date TIMESTAMP,
                    created_at TIMESTAMP NOT NULL,
                    updated_at TIMESTAMP NOT NULL,
                    FOREIGN KEY (course_id) REFERENCES courses(id)
                )
            """)
            
            # Copy data
            for row in classes_data:
                cursor.execute(f"""
                    INSERT INTO classes ({', '.join(original_columns)}, created_at, updated_at)
                    VALUES ({', '.join(['?' for _ in original_columns])}, ?, ?)
                """, (*row, current_timestamp, current_timestamp))
            
            cursor.execute("DROP TABLE classes_old")
            print("   ✅ Classes table updated with timestamps")
        else:
            print("   ℹ️  Classes table already has timestamps")
        
        # ========== MIGRATE STUDENTS TABLE ==========
        cursor.execute("PRAGMA table_info(students)")
        student_columns = [row[1] for row in cursor.fetchall()]
        
        if 'created_at' not in student_columns:
            print("   📦 Adding timestamps to students table...")
            
            cursor.execute("SELECT * FROM students")
            students_data = cursor.fetchall()
            cursor.execute("PRAGMA table_info(students)")
            original_columns = [row[1] for row in cursor.fetchall()]
            
            cursor.execute("ALTER TABLE students RENAME TO students_old")
            
            cursor.execute("""
                CREATE TABLE students (
                    id INTEGER PRIMARY KEY,
                    name VARCHAR NOT NULL,
                    email VARCHAR UNIQUE NOT NULL,
                    cpf VARCHAR UNIQUE NOT NULL,
                    authorized BOOLEAN NOT NULL DEFAULT 1,
                    hashed_password VARCHAR,
                    is_active BOOLEAN NOT NULL DEFAULT 1,
                    created_at TIMESTAMP NOT NULL,
                    updated_at TIMESTAMP NOT NULL
                )
            """)
            
            for row in students_data:
                cursor.execute(f"""
                    INSERT INTO students ({', '.join(original_columns)}, created_at, updated_at)
                    VALUES ({', '.join(['?' for _ in original_columns])}, ?, ?)
                """, (*row, current_timestamp, current_timestamp))
            
            cursor.execute("DROP TABLE students_old")
            cursor.execute("CREATE UNIQUE INDEX ix_students_email ON students (email)")
            cursor.execute("CREATE UNIQUE INDEX ix_students_cpf ON students (cpf)")
            cursor.execute("CREATE INDEX ix_students_name ON students (name)")
            
            print("   ✅ Students table updated with timestamps")
        else:
            print("   ℹ️  Students table already has timestamps")
        
        conn.commit()
        print("\n✅ Migration completed successfully!")
        print("   Summary:")
        print("   - Removed certificate_template from courses")
        print("   - Added created_at/updated_at to courses, classes, students")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        import traceback
        traceback.print_exc()
        if 'conn' in locals():
            conn.rollback()
            conn.close()
        return False


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "rollback":
        print("❌ Rollback not implemented. Please restore from database backup if needed.")
        sys.exit(1)
    else:
        if migrate():
            print("\n🎉 Migration successful! The server should restart automatically.")
        else:
            print("\n⚠️  Migration failed. Please check the errors above.")
            sys.exit(1)
