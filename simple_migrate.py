"""
Simple Database Migration Script

This script provides a simple way to apply database schema changes
without requiring Flask-Migrate. It directly executes SQL commands.

Usage:
    python simple_migrate.py
"""

import sys
import os

# Add the backend directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from application import Application


def check_column_exists(db, table_name, column_name):
    """Check if a column exists in a table."""
    try:
        # For SQLite
        if 'sqlite' in str(db.engine.url):
            result = db.engine.execute(f"PRAGMA table_info({table_name})")
            columns = [row[1] for row in result]
            return column_name in columns
        
        # For PostgreSQL
        elif 'postgresql' in str(db.engine.url):
            result = db.engine.execute("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = %s AND column_name = %s
            """, (table_name, column_name))
            return result.rowcount > 0
        
        # For MySQL
        elif 'mysql' in str(db.engine.url):
            result = db.engine.execute("""
                SELECT COLUMN_NAME 
                FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_NAME = %s AND COLUMN_NAME = %s
            """, (table_name, column_name))
            return result.rowcount > 0
        
        else:
            print(f"Unknown database type: {db.engine.url}")
            return False
            
    except Exception as e:
        print(f"Error checking column existence: {str(e)}")
        return False


def remove_role_and_is_active_columns():
    """Remove role and is_active columns from users table."""
    print("Applying migration: Remove role and is_active columns from users table")
    print("=" * 70)
    
    app_instance = Application()
    app = app_instance.create_app()
    
    with app.app_context():
        from application import db
        
        try:
            # Check if users table exists
            inspector = db.inspect(db.engine)
            tables = inspector.get_table_names()
            
            if 'users' not in tables:
                print("✓ Users table doesn't exist yet - no migration needed")
                return True
            
            # Get current columns
            columns = [col['name'] for col in inspector.get_columns('users')]
            print(f"Current columns in users table: {', '.join(columns)}")
            
            migrations_applied = []
            
            # Remove role column if it exists
            if 'role' in columns:
                print("\n1. Removing 'role' column...")
                try:
                    if 'sqlite' in str(db.engine.url):
                        # SQLite doesn't support DROP COLUMN directly
                        print("   SQLite detected - using table recreation method")
                        db.engine.execute("""
                            CREATE TABLE users_new (
                                id INTEGER PRIMARY KEY AUTOINCREMENT,
                                name VARCHAR(100) NOT NULL,
                                email VARCHAR(120) NOT NULL UNIQUE,
                                github_username VARCHAR(50) NOT NULL UNIQUE,
                                password_hash VARCHAR(255) NOT NULL,
                                created_at DATETIME,
                                updated_at DATETIME
                            )
                        """)
                        db.engine.execute("""
                            INSERT INTO users_new (id, name, email, github_username, password_hash, created_at, updated_at)
                            SELECT id, name, email, github_username, password_hash, created_at, updated_at
                            FROM users
                        """)
                        db.engine.execute("DROP TABLE users")
                        db.engine.execute("ALTER TABLE users_new RENAME TO users")
                    else:
                        # PostgreSQL, MySQL support DROP COLUMN
                        db.engine.execute("ALTER TABLE users DROP COLUMN role")
                    
                    migrations_applied.append("role column removed")
                    print("   ✓ 'role' column removed successfully")
                except Exception as e:
                    print(f"   ✗ Error removing 'role' column: {str(e)}")
                    return False
            else:
                print("\n1. ✓ 'role' column already removed")
            
            # Remove is_active column if it exists (and we haven't already recreated the table)
            if 'is_active' in columns and 'role column removed' not in migrations_applied:
                print("\n2. Removing 'is_active' column...")
                try:
                    if 'sqlite' in str(db.engine.url):
                        # SQLite doesn't support DROP COLUMN directly
                        print("   SQLite detected - using table recreation method")
                        db.engine.execute("""
                            CREATE TABLE users_new (
                                id INTEGER PRIMARY KEY AUTOINCREMENT,
                                name VARCHAR(100) NOT NULL,
                                email VARCHAR(120) NOT NULL UNIQUE,
                                github_username VARCHAR(50) NOT NULL UNIQUE,
                                password_hash VARCHAR(255) NOT NULL,
                                created_at DATETIME,
                                updated_at DATETIME
                            )
                        """)
                        db.engine.execute("""
                            INSERT INTO users_new (id, name, email, github_username, password_hash, created_at, updated_at)
                            SELECT id, name, email, github_username, password_hash, created_at, updated_at
                            FROM users
                        """)
                        db.engine.execute("DROP TABLE users")
                        db.engine.execute("ALTER TABLE users_new RENAME TO users")
                    else:
                        # PostgreSQL, MySQL support DROP COLUMN
                        db.engine.execute("ALTER TABLE users DROP COLUMN is_active")
                    
                    migrations_applied.append("is_active column removed")
                    print("   ✓ 'is_active' column removed successfully")
                except Exception as e:
                    print(f"   ✗ Error removing 'is_active' column: {str(e)}")
                    return False
            else:
                print("\n2. ✓ 'is_active' column already removed")
            
            # Verify final state
            print("\n" + "=" * 40)
            print("Verifying migration results...")
            
            final_columns = [col['name'] for col in inspector.get_columns('users')]
            print(f"Final columns in users table: {', '.join(final_columns)}")
            
            expected_columns = ['id', 'name', 'email', 'github_username', 'password_hash', 'created_at', 'updated_at']
            missing_expected = [col for col in expected_columns if col not in final_columns]
            unexpected_columns = [col for col in final_columns if col not in expected_columns]
            
            if missing_expected:
                print(f"⚠️  Missing expected columns: {', '.join(missing_expected)}")
            
            if unexpected_columns:
                print(f"⚠️  Unexpected columns found: {', '.join(unexpected_columns)}")
            
            if not missing_expected and not unexpected_columns:
                print("✓ Schema verification successful!")
            
            print("\n🎉 Migration completed successfully!")
            print(f"Applied changes: {', '.join(migrations_applied) if migrations_applied else 'No changes needed'}")
            
            return True
            
        except Exception as e:
            print(f"✗ Migration failed: {str(e)}")
            return False


def main():
    """Main function."""
    print("=" * 70)
    print("Simple Database Migration Tool")
    print("Remove role and is_active columns from users table")
    print("=" * 70)
    
    print("\nThis migration will:")
    print("- Remove 'role' column from users table (if exists)")
    print("- Remove 'is_active' column from users table (if exists)")
    print("- Preserve all other user data")
    print("\n⚠️  Make sure to backup your database before proceeding!")
    
    confirmation = input("\nDo you want to proceed with the migration? (yes/no): ")
    
    if confirmation.lower() != 'yes':
        print("Migration cancelled.")
        return
    
    success = remove_role_and_is_active_columns()
    
    if success:
        print("\n✅ Migration completed successfully!")
        print("Your User model is now aligned with the current schema.")
    else:
        print("\n❌ Migration failed!")
        print("Please check the error messages above and try again.")
        print("You may need to manually fix any issues or restore from backup.")


if __name__ == '__main__':
    main()
