import pytest
from fastapi import status

pytestmark = pytest.mark.classes

class TestClassManagement:
    """Test class management endpoints"""
    
    def test_create_class_success(self, client, auth_headers, sample_classes):
        """Test successful class creation"""
        class_data = sample_classes[0]
        response = client.post("/api/v1/classes/", json=class_data, headers=auth_headers)
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["name"] == class_data["name"]
        assert data["level"] == class_data["level"]
        assert data["capacity"] == class_data["capacity"]
        assert "id" in data
    
    def test_create_class_duplicate_name(self, client, auth_headers, sample_classes):
        """Test creating class with duplicate name"""
        class_data = sample_classes[0]
        # Create first class
        response = client.post("/api/v1/classes/", json=class_data, headers=auth_headers)
        assert response.status_code == status.HTTP_201_CREATED
        
        # Try to create with same name
        duplicate_data = class_data.copy()
        duplicate_data["room_number"] = "102"
        response = client.post("/api/v1/classes/", json=duplicate_data, headers=auth_headers)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_create_class_invalid_data(self, client, auth_headers):
        """Test creating class with invalid data"""
        invalid_data = {
            "name": "",  # Empty name
            "level": "invalid_level",
            "capacity": -10  # Negative capacity
        }
        response = client.post("/api/v1/classes/", json=invalid_data, headers=auth_headers)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_get_classes_list(self, client, auth_headers, sample_classes):
        """Test getting list of classes"""
        # Create a class first
        class_data = sample_classes[0]
        response = client.post("/api/v1/classes/", json=class_data, headers=auth_headers)
        assert response.status_code == status.HTTP_201_CREATED
        
        # Get classes list
        response = client.get("/api/v1/classes/", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert "page" in data
        assert "size" in data
        assert len(data["items"]) > 0
    
    def test_get_class_by_id(self, client, auth_headers, sample_classes):
        """Test getting class by ID"""
        # Create a class
        class_data = sample_classes[0]
        response = client.post("/api/v1/classes/", json=class_data, headers=auth_headers)
        assert response.status_code == status.HTTP_201_CREATED
        class_id = response.json()["id"]
        
        # Get class by ID
        response = client.get(f"/api/v1/classes/{class_id}", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == class_id
        assert data["name"] == class_data["name"]
    
    def test_get_class_not_found(self, client, auth_headers):
        """Test getting non-existent class"""
        response = client.get("/api/v1/classes/999", headers=auth_headers)
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_update_class_success(self, client, auth_headers, sample_classes):
        """Test successful class update"""
        # Create a class
        class_data = sample_classes[0]
        response = client.post("/api/v1/classes/", json=class_data, headers=auth_headers)
        assert response.status_code == status.HTTP_201_CREATED
        class_id = response.json()["id"]
        
        # Update class
        update_data = {
            "name": "Updated Class Name",
            "capacity": 35,
            "room_number": "103"
        }
        response = client.put(f"/api/v1/classes/{class_id}", json=update_data, headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["name"] == update_data["name"]
        assert data["capacity"] == update_data["capacity"]
        assert data["room_number"] == update_data["room_number"]
    
    def test_update_class_not_found(self, client, auth_headers):
        """Test updating non-existent class"""
        update_data = {"name": "Updated Name"}
        response = client.put("/api/v1/classes/999", json=update_data, headers=auth_headers)
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_delete_class_success(self, client, auth_headers, sample_classes):
        """Test successful class deletion"""
        # Create a class
        class_data = sample_classes[0]
        response = client.post("/api/v1/classes/", json=class_data, headers=auth_headers)
        assert response.status_code == status.HTTP_201_CREATED
        class_id = response.json()["id"]
        
        # Delete class
        response = client.delete(f"/api/v1/classes/{class_id}", headers=auth_headers)
        assert response.status_code == status.HTTP_204_NO_CONTENT
        
        # Verify class is deleted
        response = client.get(f"/api/v1/classes/{class_id}", headers=auth_headers)
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_delete_class_not_found(self, client, auth_headers):
        """Test deleting non-existent class"""
        response = client.delete("/api/v1/classes/999", headers=auth_headers)
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_get_classes_by_level(self, client, auth_headers, sample_classes):
        """Test getting classes by level"""
        # Create classes
        for class_data in sample_classes:
            response = client.post("/api/v1/classes/", json=class_data, headers=auth_headers)
            assert response.status_code == status.HTTP_201_CREATED
        
        # Get classes by level
        response = client.get("/api/v1/classes/level/o_level", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "items" in data
        assert len(data["items"]) > 0
    
    def test_get_class_statistics(self, client, auth_headers, sample_classes):
        """Test getting class statistics"""
        # Create a class
        class_data = sample_classes[0]
        response = client.post("/api/v1/classes/", json=class_data, headers=auth_headers)
        assert response.status_code == status.HTTP_201_CREATED
        class_id = response.json()["id"]
        
        # Get class statistics
        response = client.get(f"/api/v1/classes/{class_id}/statistics", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "total_students" in data
        assert "capacity" in data
        assert "occupancy_rate" in data
    
    def test_unauthorized_access(self, client, sample_classes):
        """Test unauthorized access to class endpoints"""
        class_data = sample_classes[0]
        # Try to create class without authentication
        response = client.post("/api/v1/classes/", json=class_data)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        
        # Try to get classes without authentication
        response = client.get("/api/v1/classes/")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED 