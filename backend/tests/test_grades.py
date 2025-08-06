import pytest
from fastapi import status

pytestmark = pytest.mark.grades

class TestGradeManagement:
    """Test grade management endpoints"""
    
    def test_create_grade_success(self, client, auth_headers, sample_grades):
        """Test successful grade creation"""
        grade_data = sample_grades[0]
        response = client.post("/api/v1/grades/", json=grade_data, headers=auth_headers)
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["student_id"] == grade_data["student_id"]
        assert data["subject_id"] == grade_data["subject_id"]
        assert data["term"] == grade_data["term"]
        assert "id" in data
    
    def test_create_grade_duplicate(self, client, auth_headers, sample_grades):
        """Test creating duplicate grade for same student/subject/term"""
        grade_data = sample_grades[0]
        # Create first grade
        response = client.post("/api/v1/grades/", json=grade_data, headers=auth_headers)
        assert response.status_code == status.HTTP_201_CREATED
        
        # Try to create duplicate grade
        response = client.post("/api/v1/grades/", json=grade_data, headers=auth_headers)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_create_grade_invalid_data(self, client, auth_headers):
        """Test creating grade with invalid data"""
        invalid_data = {
            "student_id": 1,
            "subject_id": 1,
            "term": "",  # Empty term
            "test_score": 150,  # Score > 100
            "exam_score": -10  # Negative score
        }
        response = client.post("/api/v1/grades/", json=invalid_data, headers=auth_headers)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_get_grades_list(self, client, auth_headers, sample_grades):
        """Test getting list of grades"""
        # Create a grade first
        grade_data = sample_grades[0]
        response = client.post("/api/v1/grades/", json=grade_data, headers=auth_headers)
        assert response.status_code == status.HTTP_201_CREATED
        
        # Get grades list
        response = client.get("/api/v1/grades/", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert "page" in data
        assert "size" in data
        assert len(data["items"]) > 0
    
    def test_get_grade_by_id(self, client, auth_headers, sample_grades):
        """Test getting grade by ID"""
        # Create a grade
        grade_data = sample_grades[0]
        response = client.post("/api/v1/grades/", json=grade_data, headers=auth_headers)
        assert response.status_code == status.HTTP_201_CREATED
        grade_id = response.json()["id"]
        
        # Get grade by ID
        response = client.get(f"/api/v1/grades/{grade_id}", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == grade_id
        assert data["student_id"] == grade_data["student_id"]
    
    def test_get_grade_not_found(self, client, auth_headers):
        """Test getting non-existent grade"""
        response = client.get("/api/v1/grades/999", headers=auth_headers)
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_update_grade_success(self, client, auth_headers, sample_grades):
        """Test successful grade update"""
        # Create a grade
        grade_data = sample_grades[0]
        response = client.post("/api/v1/grades/", json=grade_data, headers=auth_headers)
        assert response.status_code == status.HTTP_201_CREATED
        grade_id = response.json()["id"]
        
        # Update grade
        update_data = {
            "test_score": 90,
            "exam_score": 95,
            "assignment_score": 92,
            "total_score": 92.5,
            "grade": "A+",
            "remarks": "Outstanding performance"
        }
        response = client.put(f"/api/v1/grades/{grade_id}", json=update_data, headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["test_score"] == update_data["test_score"]
        assert data["exam_score"] == update_data["exam_score"]
        assert data["grade"] == update_data["grade"]
    
    def test_update_grade_not_found(self, client, auth_headers):
        """Test updating non-existent grade"""
        update_data = {"test_score": 90}
        response = client.put("/api/v1/grades/999", json=update_data, headers=auth_headers)
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_delete_grade_success(self, client, auth_headers, sample_grades):
        """Test successful grade deletion"""
        # Create a grade
        grade_data = sample_grades[0]
        response = client.post("/api/v1/grades/", json=grade_data, headers=auth_headers)
        assert response.status_code == status.HTTP_201_CREATED
        grade_id = response.json()["id"]
        
        # Delete grade
        response = client.delete(f"/api/v1/grades/{grade_id}", headers=auth_headers)
        assert response.status_code == status.HTTP_204_NO_CONTENT
        
        # Verify grade is deleted
        response = client.get(f"/api/v1/grades/{grade_id}", headers=auth_headers)
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_delete_grade_not_found(self, client, auth_headers):
        """Test deleting non-existent grade"""
        response = client.delete("/api/v1/grades/999", headers=auth_headers)
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_get_student_grades(self, client, auth_headers, sample_grades):
        """Test getting grades for a specific student"""
        # Create a grade
        grade_data = sample_grades[0]
        response = client.post("/api/v1/grades/", json=grade_data, headers=auth_headers)
        assert response.status_code == status.HTTP_201_CREATED
        
        # Get student grades
        student_id = grade_data["student_id"]
        response = client.get(f"/api/v1/grades/student/{student_id}", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "items" in data
        assert len(data["items"]) > 0
    
    def test_get_class_grades(self, client, auth_headers, sample_grades):
        """Test getting grades for a specific class"""
        # Create a grade
        grade_data = sample_grades[0]
        response = client.post("/api/v1/grades/", json=grade_data, headers=auth_headers)
        assert response.status_code == status.HTTP_201_CREATED
        
        # Get class grades
        class_id = grade_data["class_id"]
        response = client.get(f"/api/v1/grades/class/{class_id}", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "items" in data
    
    def test_get_subject_grades(self, client, auth_headers, sample_grades):
        """Test getting grades for a specific subject"""
        # Create a grade
        grade_data = sample_grades[0]
        response = client.post("/api/v1/grades/", json=grade_data, headers=auth_headers)
        assert response.status_code == status.HTTP_201_CREATED
        
        # Get subject grades
        subject_id = grade_data["subject_id"]
        response = client.get(f"/api/v1/grades/subject/{subject_id}", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "items" in data
    
    def test_get_grade_statistics(self, client, auth_headers, sample_grades):
        """Test getting grade statistics"""
        # Create a grade
        grade_data = sample_grades[0]
        response = client.post("/api/v1/grades/", json=grade_data, headers=auth_headers)
        assert response.status_code == status.HTTP_201_CREATED
        
        # Get grade statistics
        response = client.get("/api/v1/grades/statistics", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "average_score" in data
        assert "grade_distribution" in data
        assert "total_grades" in data
    
    def test_unauthorized_access(self, client, sample_grades):
        """Test unauthorized access to grade endpoints"""
        grade_data = sample_grades[0]
        # Try to create grade without authentication
        response = client.post("/api/v1/grades/", json=grade_data)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        
        # Try to get grades without authentication
        response = client.get("/api/v1/grades/")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED 