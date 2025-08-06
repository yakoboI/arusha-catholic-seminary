import pytest
from fastapi import status

pytestmark = pytest.mark.students

class TestStudentManagement:
    """Test student management endpoints"""
    
    def test_create_student_success(self, client, auth_headers, test_student_data):
        """Test successful student creation"""
        response = client.post("/api/v1/students/", json=test_student_data, headers=auth_headers)
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["admission_number"] == test_student_data["admission_number"]
        assert data["full_name"] == test_student_data["full_name"]
        assert data["email"] == test_student_data["email"]
        assert "id" in data
    
    def test_create_student_duplicate_admission(self, client, auth_headers, test_student_data):
        """Test creating student with duplicate admission number"""
        # Create first student
        response = client.post("/api/v1/students/", json=test_student_data, headers=auth_headers)
        assert response.status_code == status.HTTP_201_CREATED
        
        # Try to create with same admission number
        duplicate_data = test_student_data.copy()
        duplicate_data["email"] = "different@example.com"
        response = client.post("/api/v1/students/", json=duplicate_data, headers=auth_headers)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_create_student_invalid_data(self, client, auth_headers):
        """Test creating student with invalid data"""
        invalid_data = {
            "admission_number": "STU001",
            "full_name": "",  # Empty name
            "email": "invalid-email",
            "date_of_birth": "invalid-date"
        }
        response = client.post("/api/v1/students/", json=invalid_data, headers=auth_headers)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_get_students_list(self, client, auth_headers, test_student_data):
        """Test getting list of students"""
        # Create a student first
        response = client.post("/api/v1/students/", json=test_student_data, headers=auth_headers)
        assert response.status_code == status.HTTP_201_CREATED
        
        # Get students list
        response = client.get("/api/v1/students/", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert "page" in data
        assert "size" in data
        assert len(data["items"]) > 0
    
    def test_get_student_by_id(self, client, auth_headers, test_student_data):
        """Test getting student by ID"""
        # Create a student
        response = client.post("/api/v1/students/", json=test_student_data, headers=auth_headers)
        assert response.status_code == status.HTTP_201_CREATED
        student_id = response.json()["id"]
        
        # Get student by ID
        response = client.get(f"/api/v1/students/{student_id}", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == student_id
        assert data["admission_number"] == test_student_data["admission_number"]
    
    def test_get_student_not_found(self, client, auth_headers):
        """Test getting non-existent student"""
        response = client.get("/api/v1/students/999", headers=auth_headers)
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_update_student_success(self, client, auth_headers, test_student_data):
        """Test successful student update"""
        # Create a student
        response = client.post("/api/v1/students/", json=test_student_data, headers=auth_headers)
        assert response.status_code == status.HTTP_201_CREATED
        student_id = response.json()["id"]
        
        # Update student
        update_data = {
            "full_name": "Updated Student Name",
            "phone": "9876543210",
            "address": "Updated Address"
        }
        response = client.put(f"/api/v1/students/{student_id}", json=update_data, headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["full_name"] == update_data["full_name"]
        assert data["phone"] == update_data["phone"]
        assert data["address"] == update_data["address"]
    
    def test_update_student_not_found(self, client, auth_headers):
        """Test updating non-existent student"""
        update_data = {"full_name": "Updated Name"}
        response = client.put("/api/v1/students/999", json=update_data, headers=auth_headers)
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_delete_student_success(self, client, auth_headers, test_student_data):
        """Test successful student deletion"""
        # Create a student
        response = client.post("/api/v1/students/", json=test_student_data, headers=auth_headers)
        assert response.status_code == status.HTTP_201_CREATED
        student_id = response.json()["id"]
        
        # Delete student
        response = client.delete(f"/api/v1/students/{student_id}", headers=auth_headers)
        assert response.status_code == status.HTTP_204_NO_CONTENT
        
        # Verify student is deleted
        response = client.get(f"/api/v1/students/{student_id}", headers=auth_headers)
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_delete_student_not_found(self, client, auth_headers):
        """Test deleting non-existent student"""
        response = client.delete("/api/v1/students/999", headers=auth_headers)
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_search_students(self, client, auth_headers, test_student_data):
        """Test searching students"""
        # Create a student
        response = client.post("/api/v1/students/", json=test_student_data, headers=auth_headers)
        assert response.status_code == status.HTTP_201_CREATED
        
        # Search by name
        response = client.get("/api/v1/students/search?q=Test", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data["items"]) > 0
    
    def test_get_students_by_class(self, client, auth_headers, test_student_data):
        """Test getting students by class"""
        # Create a student
        response = client.post("/api/v1/students/", json=test_student_data, headers=auth_headers)
        assert response.status_code == status.HTTP_201_CREATED
        
        # Get students by class
        response = client.get("/api/v1/students/class/1", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "items" in data
    
    def test_unauthorized_access(self, client, test_student_data):
        """Test unauthorized access to student endpoints"""
        # Try to create student without authentication
        response = client.post("/api/v1/students/", json=test_student_data)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        
        # Try to get students without authentication
        response = client.get("/api/v1/students/")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED 