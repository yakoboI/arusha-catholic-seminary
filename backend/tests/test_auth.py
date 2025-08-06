import pytest
from fastapi import status

pytestmark = pytest.mark.auth

class TestAuthentication:
    """Test authentication endpoints"""
    
    def test_register_user_success(self, client, test_user_data):
        """Test successful user registration"""
        response = client.post("/api/v1/auth/register", json=test_user_data)
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["username"] == test_user_data["username"]
        assert data["email"] == test_user_data["email"]
        assert data["full_name"] == test_user_data["full_name"]
        assert data["role"] == test_user_data["role"]
        assert "id" in data
        assert "password" not in data
    
    def test_register_user_duplicate_username(self, client, test_user_data):
        """Test registration with duplicate username"""
        # Register first user
        response = client.post("/api/v1/auth/register", json=test_user_data)
        assert response.status_code == status.HTTP_201_CREATED
        
        # Try to register with same username
        duplicate_data = test_user_data.copy()
        duplicate_data["email"] = "different@example.com"
        response = client.post("/api/v1/auth/register", json=duplicate_data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_register_user_duplicate_email(self, client, test_user_data):
        """Test registration with duplicate email"""
        # Register first user
        response = client.post("/api/v1/auth/register", json=test_user_data)
        assert response.status_code == status.HTTP_201_CREATED
        
        # Try to register with same email
        duplicate_data = test_user_data.copy()
        duplicate_data["username"] = "differentuser"
        response = client.post("/api/v1/auth/register", json=duplicate_data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_register_user_invalid_data(self, client):
        """Test registration with invalid data"""
        invalid_data = {
            "username": "test",
            "email": "invalid-email",
            "password": "123"  # Too short
        }
        response = client.post("/api/v1/auth/register", json=invalid_data)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_login_success(self, client, test_user_data):
        """Test successful login"""
        # Register user first
        response = client.post("/api/v1/auth/register", json=test_user_data)
        assert response.status_code == status.HTTP_201_CREATED
        
        # Login
        login_data = {
            "username": test_user_data["username"],
            "password": test_user_data["password"]
        }
        response = client.post("/api/v1/auth/login", data=login_data)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "access_token" in data
        assert "token_type" in data
        assert data["token_type"] == "bearer"
        assert "user" in data
        assert data["user"]["username"] == test_user_data["username"]
    
    def test_login_invalid_credentials(self, client, test_user_data):
        """Test login with invalid credentials"""
        # Register user first
        response = client.post("/api/v1/auth/register", json=test_user_data)
        assert response.status_code == status.HTTP_201_CREATED
        
        # Try to login with wrong password
        login_data = {
            "username": test_user_data["username"],
            "password": "wrongpassword"
        }
        response = client.post("/api/v1/auth/login", data=login_data)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_login_nonexistent_user(self, client):
        """Test login with nonexistent user"""
        login_data = {
            "username": "nonexistent",
            "password": "password123"
        }
        response = client.post("/api/v1/auth/login", data=login_data)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_get_current_user(self, client, auth_headers):
        """Test getting current user information"""
        response = client.get("/api/v1/auth/me", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "id" in data
        assert "username" in data
        assert "email" in data
        assert "full_name" in data
        assert "role" in data
        assert "password" not in data
    
    def test_get_current_user_invalid_token(self, client):
        """Test getting current user with invalid token"""
        headers = {"Authorization": "Bearer invalid_token"}
        response = client.get("/api/v1/auth/me", headers=headers)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_get_current_user_no_token(self, client):
        """Test getting current user without token"""
        response = client.get("/api/v1/auth/me")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_change_password(self, client, auth_headers, test_user_data):
        """Test changing password"""
        password_data = {
            "current_password": test_user_data["password"],
            "new_password": "newpassword123",
            "confirm_password": "newpassword123"
        }
        response = client.post("/api/v1/auth/change-password", 
                             json=password_data, 
                             headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        
        # Try to login with new password
        login_data = {
            "username": test_user_data["username"],
            "password": "newpassword123"
        }
        response = client.post("/api/v1/auth/login", data=login_data)
        assert response.status_code == status.HTTP_200_OK
    
    def test_change_password_wrong_current(self, client, auth_headers):
        """Test changing password with wrong current password"""
        password_data = {
            "current_password": "wrongpassword",
            "new_password": "newpassword123",
            "confirm_password": "newpassword123"
        }
        response = client.post("/api/v1/auth/change-password", 
                             json=password_data, 
                             headers=auth_headers)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_change_password_mismatch(self, client, auth_headers, test_user_data):
        """Test changing password with mismatched new passwords"""
        password_data = {
            "current_password": test_user_data["password"],
            "new_password": "newpassword123",
            "confirm_password": "differentpassword"
        }
        response = client.post("/api/v1/auth/change-password", 
                             json=password_data, 
                             headers=auth_headers)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_update_profile(self, client, auth_headers):
        """Test updating user profile"""
        profile_data = {
            "full_name": "Updated Name",
            "email": "updated@example.com",
            "phone": "9876543210",
            "address": "Updated Address"
        }
        response = client.put("/api/v1/auth/update-profile", 
                            json=profile_data, 
                            headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["full_name"] == profile_data["full_name"]
        assert data["email"] == profile_data["email"]
    
    def test_update_profile_invalid_email(self, client, auth_headers):
        """Test updating profile with invalid email"""
        profile_data = {
            "full_name": "Updated Name",
            "email": "invalid-email",
            "phone": "9876543210"
        }
        response = client.put("/api/v1/auth/update-profile", 
                            json=profile_data, 
                            headers=auth_headers)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestAuthorization:
    """Test authorization and role-based access"""
    
    def test_admin_access(self, client, auth_headers):
        """Test admin user access to protected endpoints"""
        # Test access to admin-only endpoint
        response = client.get("/api/v1/users", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
    
    def test_teacher_access(self, client):
        """Test teacher user access"""
        # Create teacher user
        teacher_data = {
            "username": "teacher",
            "email": "teacher@example.com",
            "full_name": "Test Teacher",
            "password": "password123",
            "role": "teacher"
        }
        response = client.post("/api/v1/auth/register", json=teacher_data)
        assert response.status_code == status.HTTP_201_CREATED
        
        # Login as teacher
        login_data = {
            "username": "teacher",
            "password": "password123"
        }
        response = client.post("/api/v1/auth/login", data=login_data)
        assert response.status_code == status.HTTP_200_OK
        token = response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Test access to teacher endpoints
        response = client.get("/api/v1/students", headers=headers)
        assert response.status_code == status.HTTP_200_OK
    
    def test_student_access(self, client):
        """Test student user access"""
        # Create student user
        student_data = {
            "username": "student",
            "email": "student@example.com",
            "full_name": "Test Student",
            "password": "password123",
            "role": "student"
        }
        response = client.post("/api/v1/auth/register", json=student_data)
        assert response.status_code == status.HTTP_201_CREATED
        
        # Login as student
        login_data = {
            "username": "student",
            "password": "password123"
        }
        response = client.post("/api/v1/auth/login", data=login_data)
        assert response.status_code == status.HTTP_200_OK
        token = response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Test access to student endpoints
        response = client.get("/api/v1/students/me", headers=headers)
        assert response.status_code == status.HTTP_200_OK
    
    def test_unauthorized_access(self, client):
        """Test unauthorized access to protected endpoints"""
        # Try to access protected endpoint without token
        response = client.get("/api/v1/users")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        
        # Try to access with invalid token
        headers = {"Authorization": "Bearer invalid_token"}
        response = client.get("/api/v1/users", headers=headers)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestTokenValidation:
    """Test JWT token validation"""
    
    def test_token_expiration(self, client, test_user_data):
        """Test token expiration (requires time manipulation)"""
        # Register and login user
        response = client.post("/api/v1/auth/register", json=test_user_data)
        assert response.status_code == status.HTTP_201_CREATED
        
        login_data = {
            "username": test_user_data["username"],
            "password": test_user_data["password"]
        }
        response = client.post("/api/v1/auth/login", data=login_data)
        assert response.status_code == status.HTTP_200_OK
        token = response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Token should be valid initially
        response = client.get("/api/v1/auth/me", headers=headers)
        assert response.status_code == status.HTTP_200_OK
    
    def test_token_format(self, client, test_user_data):
        """Test token format and structure"""
        # Register and login user
        response = client.post("/api/v1/auth/register", json=test_user_data)
        assert response.status_code == status.HTTP_201_CREATED
        
        login_data = {
            "username": test_user_data["username"],
            "password": test_user_data["password"]
        }
        response = client.post("/api/v1/auth/login", data=login_data)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        # Check token format
        token = data["access_token"]
        assert isinstance(token, str)
        assert len(token) > 0
        assert data["token_type"] == "bearer" 