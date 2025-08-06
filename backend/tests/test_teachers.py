import pytest
from fastapi import status

pytestmark = pytest.mark.teachers

class TestTeacherManagement:
    """Test teacher management endpoints"""
    
    def test_create_teacher_success(self, client, auth_headers, test_teacher_data):
        """Test successful teacher creation"""
        response = client.post("/api/v1/teachers/", json=test_teacher_data, headers=auth_headers)
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["employee_id"] == test_teacher_data["employee_id"]
        assert data["full_name"] == test_teacher_data["full_name"]
        assert data["email"] == test_teacher_data["email"]
        assert "id" in data
    
    def test_create_teacher_duplicate_employee_id(self, client, auth_headers, test_teacher_data):
        """Test creating teacher with duplicate employee ID"""
        # Create first teacher
        response = client.post("/api/v1/teachers/", json=test_teacher_data, headers=auth_headers)
        assert response.status_code == status.HTTP_201_CREATED
        
        # Try to create with same employee ID
        duplicate_data = test_teacher_data.copy()
        duplicate_data["email"] = "different@example.com"
        response = client.post("/api/v1/teachers/", json=duplicate_data, headers=auth_headers)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_create_teacher_invalid_data(self, client, auth_headers):
        """Test creating teacher with invalid data"""
        invalid_data = {
            "employee_id": "TCH001",
            "full_name": "",  # Empty name
            "email": "invalid-email",
            "salary": "invalid-salary"  # Should be number
        }
        response = client.post("/api/v1/teachers/", json=invalid_data, headers=auth_headers)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_get_teachers_list(self, client, auth_headers, test_teacher_data):
        """Test getting list of teachers"""
        # Create a teacher first
        response = client.post("/api/v1/teachers/", json=test_teacher_data, headers=auth_headers)
        assert response.status_code == status.HTTP_201_CREATED
        
        # Get teachers list
        response = client.get("/api/v1/teachers/", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert "page" in data
        assert "size" in data
        assert len(data["items"]) > 0
    
    def test_get_teacher_by_id(self, client, auth_headers, test_teacher_data):
        """Test getting teacher by ID"""
        # Create a teacher
        response = client.post("/api/v1/teachers/", json=test_teacher_data, headers=auth_headers)
        assert response.status_code == status.HTTP_201_CREATED
        teacher_id = response.json()["id"]
        
        # Get teacher by ID
        response = client.get(f"/api/v1/teachers/{teacher_id}", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == teacher_id
        assert data["employee_id"] == test_teacher_data["employee_id"]
    
    def test_get_teacher_not_found(self, client, auth_headers):
        """Test getting non-existent teacher"""
        response = client.get("/api/v1/teachers/999", headers=auth_headers)
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_update_teacher_success(self, client, auth_headers, test_teacher_data):
        """Test successful teacher update"""
        # Create a teacher
        response = client.post("/api/v1/teachers/", json=test_teacher_data, headers=auth_headers)
        assert response.status_code == status.HTTP_201_CREATED
        teacher_id = response.json()["id"]
        
        # Update teacher
        update_data = {
            "full_name": "Updated Teacher Name",
            "phone": "9876543210",
            "salary": 60000.0
        }
        response = client.put(f"/api/v1/teachers/{teacher_id}", json=update_data, headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["full_name"] == update_data["full_name"]
        assert data["phone"] == update_data["phone"]
        assert data["salary"] == update_data["salary"]
    
    def test_update_teacher_not_found(self, client, auth_headers):
        """Test updating non-existent teacher"""
        update_data = {"full_name": "Updated Name"}
        response = client.put("/api/v1/teachers/999", json=update_data, headers=auth_headers)
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_delete_teacher_success(self, client, auth_headers, test_teacher_data):
        """Test successful teacher deletion"""
        # Create a teacher
        response = client.post("/api/v1/teachers/", json=test_teacher_data, headers=auth_headers)
        assert response.status_code == status.HTTP_201_CREATED
        teacher_id = response.json()["id"]
        
        # Delete teacher
        response = client.delete(f"/api/v1/teachers/{teacher_id}", headers=auth_headers)
        assert response.status_code == status.HTTP_204_NO_CONTENT
        
        # Verify teacher is deleted
        response = client.get(f"/api/v1/teachers/{teacher_id}", headers=auth_headers)
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_delete_teacher_not_found(self, client, auth_headers):
        """Test deleting non-existent teacher"""
        response = client.delete("/api/v1/teachers/999", headers=auth_headers)
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_search_teachers(self, client, auth_headers, test_teacher_data):
        """Test searching teachers"""
        # Create a teacher
        response = client.post("/api/v1/teachers/", json=test_teacher_data, headers=auth_headers)
        assert response.status_code == status.HTTP_201_CREATED
        
        # Search by name
        response = client.get("/api/v1/teachers/search?q=Test", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data["items"]) > 0
    
    def test_get_teachers_by_subject(self, client, auth_headers, test_teacher_data):
        """Test getting teachers by subject"""
        # Create a teacher
        response = client.post("/api/v1/teachers/", json=test_teacher_data, headers=auth_headers)
        assert response.status_code == status.HTTP_201_CREATED
        
        # Get teachers by subject
        response = client.get("/api/v1/teachers/subject/Mathematics", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "items" in data
    
    def test_unauthorized_access(self, client, test_teacher_data):
        """Test unauthorized access to teacher endpoints"""
        # Try to create teacher without authentication
        response = client.post("/api/v1/teachers/", json=test_teacher_data)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        
        # Try to get teachers without authentication
        response = client.get("/api/v1/teachers/")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED 