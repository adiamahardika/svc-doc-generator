"""
Flask OOP Application Test Runner

This script contains unit tests for the Flask OOP application.
Run this to test the functionality of your models, services, and controllers.
"""

import unittest
import sys
import os

# Add the backend directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from application import Application
from app.models.user import User
from app.services.user_service import UserService


class TestUserModel(unittest.TestCase):
    """Test cases for User model."""
    
    @classmethod
    def setUpClass(cls):
        """Set up test environment."""
        cls.app_instance = Application('testing')
        cls.app = cls.app_instance.create_app()
        cls.app_context = cls.app.app_context()
        cls.app_context.push()
        
        from application import db
        db.create_all()
    
    @classmethod
    def tearDownClass(cls):
        """Clean up test environment."""
        from application import db
        db.session.remove()
        db.drop_all()
        cls.app_context.pop()
    
    def setUp(self):
        """Set up each test."""
        from application import db
        # Clean up any existing data
        User.query.delete()
        db.session.commit()
    
    def test_user_creation(self):
        """Test user creation."""
        user_data = {
            'name': 'Test User',
            'email': 'test@example.com',
            'github_username': 'testuser',
            'password': 'password123'
        }
        
        user = User(**user_data)
        user.save()
        
        self.assertIsNotNone(user.id)
        self.assertEqual(user.email, 'test@example.com')
        self.assertEqual(user.name, 'Test User')
        self.assertEqual(user.github_username, 'testuser')
    
    def test_password_hashing(self):
        """Test password hashing and verification."""
        user = User(
            name='Test User',
            email='test@example.com',
            github_username='testuser',
            password='password123'
        )
        
        # Password should be hashed
        self.assertNotEqual(user.password_hash, 'password123')
        
        # Should be able to verify correct password
        self.assertTrue(user.check_password('password123'))
        
        # Should reject incorrect password
        self.assertFalse(user.check_password('wrongpassword'))
    
    def test_email_validation(self):
        """Test email validation."""
        # Valid email should work
        user = User(
            name='Test User',
            email='valid@example.com',
            github_username='validuser',
            password='password123'
        )
        user.save()
        self.assertEqual(user.email, 'valid@example.com')
        
        # Invalid email should raise ValueError
        with self.assertRaises(ValueError):
            invalid_user = User(
                name='Test User',
                email='invalid-email',
                github_username='invaliduser',
                password='password123'
            )
    
    def test_find_by_email(self):
        """Test finding user by email."""
        user = User(
            name='Find Me',
            email='findme@example.com',
            github_username='findme',
            password='password123'
        )
        user.save()
        
        found_user = User.find_by_email('findme@example.com')
        self.assertIsNotNone(found_user)
        self.assertEqual(found_user.email, 'findme@example.com')
        
        not_found = User.find_by_email('notfound@example.com')
        self.assertIsNone(not_found)


class TestUserService(unittest.TestCase):
    """Test cases for User service."""
    
    @classmethod
    def setUpClass(cls):
        """Set up test environment."""
        cls.app_instance = Application('testing')
        cls.app = cls.app_instance.create_app()
        cls.app_context = cls.app.app_context()
        cls.app_context.push()
        
        from application import db
        db.create_all()
    
    @classmethod
    def tearDownClass(cls):
        """Clean up test environment."""
        from application import db
        db.session.remove()
        db.drop_all()
        cls.app_context.pop()
    
    def setUp(self):
        """Set up each test."""
        from application import db
        # Clean up any existing data
        User.query.delete()
        db.session.commit()
        
        self.user_service = UserService()
    
    def test_create_user(self):
        """Test user creation through service."""
        user_data = {
            'name': 'Service Test',
            'email': 'service@example.com',
            'github_username': 'servicetest',
            'password': 'password123'
        }
        
        user = self.user_service.create_user(user_data)
        
        self.assertIsNotNone(user.id)
        self.assertEqual(user.email, 'service@example.com')
        self.assertEqual(user.github_username, 'servicetest')
        
        # Should not be able to create duplicate email
        with self.assertRaises(ValueError):
            self.user_service.create_user(user_data)
    
    def test_authenticate_user(self):
        """Test user authentication."""
        user_data = {
            'name': 'Auth Test',
            'email': 'auth@example.com',
            'github_username': 'authtest',
            'password': 'password123'
        }
        
        user = self.user_service.create_user(user_data)
        
        # Valid credentials should work
        authenticated_user = self.user_service.authenticate_user(
            'auth@example.com', 'password123'
        )
        self.assertEqual(authenticated_user.id, user.id)
        
        # Invalid password should raise ValueError
        with self.assertRaises(ValueError):
            self.user_service.authenticate_user(
                'auth@example.com', 'wrongpassword'
            )
        
        # Non-existent user should raise ValueError
        with self.assertRaises(ValueError):
            self.user_service.authenticate_user(
                'notfound@example.com', 'password123'
            )
    
    def test_update_user(self):
        """Test user update."""
        user_data = {
            'name': 'Update Test',
            'email': 'update@example.com',
            'github_username': 'updatetest',
            'password': 'password123'
        }
        
        user = self.user_service.create_user(user_data)
        
        # Update user information
        update_data = {
            'name': 'Updated Name',
            'github_username': 'updateduser'
        }
        
        updated_user = self.user_service.update_user(user.id, update_data)
        
        self.assertEqual(updated_user.name, 'Updated Name')
        self.assertEqual(updated_user.github_username, 'updateduser')
    
    def test_delete_user(self):
        """Test user deletion (soft delete)."""
        user_data = {
            'name': 'Delete Test',
            'email': 'delete@example.com',
            'github_username': 'deletetest',
            'password': 'password123'
        }
        
        user = self.user_service.create_user(user_data)
        self.assertTrue(user.is_active)
        
        # Delete user (soft delete)
        deleted_user = self.user_service.delete_user(user.id)
        self.assertFalse(deleted_user.is_active)


class TestAPIEndpoints(unittest.TestCase):
    """Test cases for API endpoints."""
    
    @classmethod
    def setUpClass(cls):
        """Set up test environment."""
        cls.app_instance = Application('testing')
        cls.app = cls.app_instance.create_app()
        cls.app_context = cls.app.app_context()
        cls.app_context.push()
        cls.client = cls.app.test_client()
        
        from application import db
        db.create_all()
    
    @classmethod
    def tearDownClass(cls):
        """Clean up test environment."""
        from application import db
        db.session.remove()
        db.drop_all()
        cls.app_context.pop()
    
    def setUp(self):
        """Set up each test."""
        from application import db
        # Clean up any existing data
        User.query.delete()
        db.session.commit()
    
    def test_health_check(self):
        """Test health check endpoint."""
        response = self.client.get('/health')
        self.assertEqual(response.status_code, 200)
        
        data = response.get_json()
        self.assertTrue(data['success'])
        self.assertEqual(data['data']['status'], 'healthy')
    
    def test_api_status(self):
        """Test API status endpoint."""
        response = self.client.get('/api/status')
        self.assertEqual(response.status_code, 200)
        
        data = response.get_json()
        self.assertTrue(data['success'])
        self.assertEqual(data['data']['api'], 'Flask OOP Backend')
    
    def test_user_registration(self):
        """Test user registration."""
        user_data = {
            'name': 'New User',
            'email': 'newuser@example.com',
            'github_username': 'newuser',
            'password': 'password123'
        }
        
        response = self.client.post('/api/users', json=user_data)
        self.assertEqual(response.status_code, 201)
        
        data = response.get_json()
        self.assertTrue(data['success'])
        self.assertEqual(data['data']['email'], 'newuser@example.com')
        self.assertEqual(data['data']['github_username'], 'newuser')


def run_tests():
    """Run all tests."""
    print("=" * 60)
    print("Running Flask OOP Application Tests")
    print("=" * 60)
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test cases
    suite.addTests(loader.loadTestsFromTestCase(TestUserModel))
    suite.addTests(loader.loadTestsFromTestCase(TestUserService))
    suite.addTests(loader.loadTestsFromTestCase(TestAPIEndpoints))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    
    if result.failures:
        print("\nFailures:")
        for test, traceback in result.failures:
            print(f"- {test}: {traceback}")
    
    if result.errors:
        print("\nErrors:")
        for test, traceback in result.errors:
            print(f"- {test}: {traceback}")
    
    if result.wasSuccessful():
        print("\n🎉 All tests passed!")
        return True
    else:
        print("\n❌ Some tests failed!")
        return False


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)
