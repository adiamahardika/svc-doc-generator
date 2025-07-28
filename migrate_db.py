"""
Flask Database Migration Script

This script helps you manage database migrations for the Flask OOP application.
It provides easy commands to initialize, create, and apply database migrations.

Usage:
    python migrate_db.py init          # Initialize migration repository
    python migrate_db.py migrate       # Create a new migration
    python migrate_db.py upgrade       # Apply migrations to database
    python migrate_db.py downgrade     # Revert last migration
    python migrate_db.py current       # Show current migration
    python migrate_db.py history       # Show migration history
"""

import sys
import os

# Add the backend directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask.cli import with_appcontext
from flask_migrate import Migrate, init, migrate, upgrade, downgrade, current, history
from application import Application


def init_migrations():
    """Initialize the migration repository."""
    print("Initializing migration repository...")
    
    app_instance = Application()
    app = app_instance.create_app()
    
    with app.app_context():
        from application import db
        migrate_instance = Migrate(app, db)
        init()
        print("✓ Migration repository initialized!")


def create_migration(message=None):
    """Create a new migration."""
    if not message:
        message = input("Enter migration message: ").strip()
        if not message:
            message = "Auto-generated migration"
    
    print(f"Creating migration: {message}")
    
    app_instance = Application()
    app = app_instance.create_app()
    
    with app.app_context():
        from application import db
        migrate_instance = Migrate(app, db)
        migrate(message=message)
        print("✓ Migration created successfully!")


def upgrade_database():
    """Apply migrations to the database."""
    print("Applying migrations to database...")
    
    app_instance = Application()
    app = app_instance.create_app()
    
    with app.app_context():
        from application import db
        migrate_instance = Migrate(app, db)
        upgrade()
        print("✓ Database upgraded successfully!")


def downgrade_database():
    """Revert the last migration."""
    print("⚠️  WARNING: This will revert the last migration!")
    confirmation = input("Type 'yes' to continue: ")
    
    if confirmation.lower() != 'yes':
        print("Downgrade cancelled.")
        return
    
    print("Reverting last migration...")
    
    app_instance = Application()
    app = app_instance.create_app()
    
    with app.app_context():
        from application import db
        migrate_instance = Migrate(app, db)
        downgrade()
        print("✓ Database downgraded successfully!")


def show_current():
    """Show current migration."""
    app_instance = Application()
    app = app_instance.create_app()
    
    with app.app_context():
        from application import db
        migrate_instance = Migrate(app, db)
        current()


def show_history():
    """Show migration history."""
    app_instance = Application()
    app = app_instance.create_app()
    
    with app.app_context():
        from application import db
        migrate_instance = Migrate(app, db)
        history()


def apply_user_schema_migration():
    """Apply the specific migration to remove role and is_active fields."""
    print("Applying User schema migration (removing role and is_active fields)...")
    print("This migration will:")
    print("- Remove 'role' column from users table")
    print("- Remove 'is_active' column from users table")
    print("")
    
    confirmation = input("Do you want to proceed? (yes/no): ")
    if confirmation.lower() != 'yes':
        print("Migration cancelled.")
        return
    
    app_instance = Application()
    app = app_instance.create_app()
    
    with app.app_context():
        from application import db
        
        try:
            # Check if columns exist before attempting to drop them
            inspector = db.inspect(db.engine)
            columns = [col['name'] for col in inspector.get_columns('users')]
            
            if 'role' in columns:
                print("Dropping 'role' column...")
                db.engine.execute('ALTER TABLE users DROP COLUMN role')
                print("✓ 'role' column dropped")
            else:
                print("✓ 'role' column already removed")
            
            if 'is_active' in columns:
                print("Dropping 'is_active' column...")
                db.engine.execute('ALTER TABLE users DROP COLUMN is_active')
                print("✓ 'is_active' column dropped")
            else:
                print("✓ 'is_active' column already removed")
            
            print("\n🎉 User schema migration completed successfully!")
            
        except Exception as e:
            print(f"✗ Error applying migration: {str(e)}")
            print("You may need to apply this migration manually or use Flask-Migrate commands.")


def main():
    """Main function to handle migration commands."""
    print("=" * 60)
    print("Flask Database Migration Manager")
    print("=" * 60)
    
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == 'init':
            init_migrations()
        elif command == 'migrate':
            message = sys.argv[2] if len(sys.argv) > 2 else None
            create_migration(message)
        elif command == 'upgrade':
            upgrade_database()
        elif command == 'downgrade':
            downgrade_database()
        elif command == 'current':
            show_current()
        elif command == 'history':
            show_history()
        elif command == 'apply-user-migration':
            apply_user_schema_migration()
        else:
            print(f"Unknown command: {command}")
            print(__doc__)
    else:
        # Interactive mode
        while True:
            print("\nChoose an option:")
            print("1. Initialize migration repository")
            print("2. Create new migration")
            print("3. Apply migrations (upgrade)")
            print("4. Revert last migration (downgrade)")
            print("5. Show current migration")
            print("6. Show migration history")
            print("7. Apply User schema migration (remove role/is_active)")
            print("8. Exit")
            
            choice = input("\nEnter your choice (1-8): ").strip()
            
            if choice == '1':
                init_migrations()
            elif choice == '2':
                create_migration()
            elif choice == '3':
                upgrade_database()
            elif choice == '4':
                downgrade_database()
            elif choice == '5':
                show_current()
            elif choice == '6':
                show_history()
            elif choice == '7':
                apply_user_schema_migration()
            elif choice == '8':
                print("Goodbye!")
                break
            else:
                print("Invalid choice. Please try again.")


if __name__ == '__main__':
    main()
