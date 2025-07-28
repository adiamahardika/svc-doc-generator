"""
Flask Database Initialization Script

This script provides database management functionality for the Flask OOP application.
Run this to set up your database tables and create initial data.
"""

from application import Application
from app.models.user import User
from app.services.user_service import UserService
import os


def init_database():
    """Initialize database tables."""
    print("Initializing database...")
    
    # Create application instance
    app_instance = Application()
    app = app_instance.create_app()
    
    with app.app_context():
        from application import db
        
        # Create all tables
        db.create_all()
        print("✓ Database tables created successfully!")
        
        # Check if admin user already exists
        admin_email = "admin@example.com"
        existing_admin = User.find_by_email(admin_email)
        
        if not existing_admin:
            # Create admin user
            user_service = UserService()
            admin_data = {
                'name': 'Admin User',
                'email': admin_email,
                'github_username': 'admin-user',
                'password': 'admin123'
            }
            
            try:
                admin_user = user_service.create_user(admin_data)
                print(f"✓ Admin user created: {admin_user.email}")
                print("  Login credentials:")
                print(f"  Email: {admin_email}")
                print("  Password: admin123")
                print("  ⚠️  Please change the default password after first login!")
            except Exception as e:
                print(f"✗ Error creating admin user: {str(e)}")
        else:
            print("✓ Admin user already exists")
        
        print("\n🎉 Database initialization completed!")


def reset_database():
    """Reset database (drop and recreate all tables)."""
    print("⚠️  WARNING: This will delete ALL data in the database!")
    confirmation = input("Type 'yes' to continue: ")
    
    if confirmation.lower() != 'yes':
        print("Database reset cancelled.")
        return
    
    print("Resetting database...")
    
    # Create application instance
    app_instance = Application()
    app = app_instance.create_app()
    
    with app.app_context():
        from application import db
        
        # Drop all tables
        db.drop_all()
        print("✓ All tables dropped")
        
        # Recreate tables
        db.create_all()
        print("✓ Tables recreated")
        
        print("Database reset completed!")


def create_sample_users():
    """Create sample users for testing."""
    print("Creating sample users...")
    
    # Create application instance
    app_instance = Application()
    app = app_instance.create_app()
    
    with app.app_context():
        user_service = UserService()
        
        sample_users = [
            {
                'name': 'John Doe',
                'email': 'john.doe@example.com',
                'github_username': 'johndoe',
                'password': 'password123'
            },
            {
                'name': 'Jane Smith',
                'email': 'jane.smith@example.com',
                'github_username': 'janesmith',
                'password': 'password123'
            },
            {
                'name': 'Test User',
                'email': 'test@example.com',
                'github_username': 'testuser',
                'password': 'password123'
            }
        ]
        
        created_count = 0
        for user_data in sample_users:
            try:
                # Check if user already exists
                existing_user = User.find_by_email(user_data['email'])
                if not existing_user:
                    user = user_service.create_user(user_data)
                    print(f"✓ Created user: {user.email}")
                    created_count += 1
                else:
                    print(f"⚠️  User already exists: {user_data['email']}")
            except Exception as e:
                print(f"✗ Error creating user {user_data['email']}: {str(e)}")
        
        print(f"\n🎉 Created {created_count} sample users!")


def main():
    """Main function to run database management tasks."""
    print("=" * 50)
    print("Flask OOP Database Management")
    print("=" * 50)
    
    while True:
        print("\nChoose an option:")
        print("1. Initialize database (create tables)")
        print("2. Reset database (⚠️  DANGER: deletes all data)")
        print("3. Create sample users")
        print("4. Exit")
        
        choice = input("\nEnter your choice (1-4): ").strip()
        
        if choice == '1':
            init_database()
        elif choice == '2':
            reset_database()
        elif choice == '3':
            create_sample_users()
        elif choice == '4':
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Please try again.")


if __name__ == '__main__':
    main()
