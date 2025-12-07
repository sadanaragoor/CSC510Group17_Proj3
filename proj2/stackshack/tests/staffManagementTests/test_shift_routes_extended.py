"""
Extended shift route tests to increase coverage.
"""
from datetime import date, datetime, time
from models.shift import Shift, ShiftAssignment
from models.user import User
from database.db import db


class TestShiftRoutesExtended:
    """Extended shift route tests."""
    
    def login(self, client, username, password):
        """Helper method to login."""
        return client.post(
            "/auth/login",
            data={"username": username, "password": password},
            follow_redirects=True
        )
    
    def test_api_get_shifts(self, client, app, admin_user, sample_shifts):
        """Test API endpoint to get all shifts."""
        self.login(client, "admin", "adminpass")
        response = client.get("/shifts/api/shifts")
        
        assert response.status_code == 200
        data = response.get_json()
        assert "shifts" in data
        assert len(data["shifts"]) > 0
    
    def test_api_get_assignments_invalid_date(self, client, app, admin_user):
        """Test API endpoint with invalid date."""
        self.login(client, "admin", "adminpass")
        response = client.get("/shifts/api/assignments?start_date=invalid")
        
        assert response.status_code == 400
    
    def test_admin_shifts_dashboard_with_date(self, client, app, admin_user):
        """Test admin dashboard with specific date."""
        self.login(client, "admin", "adminpass")
        today = date.today()
        response = client.get(f"/shifts/admin/shifts?date={today.isoformat()}")
        
        assert response.status_code == 200
    
    def test_admin_shifts_dashboard_invalid_date(self, client, app, admin_user):
        """Test admin dashboard with invalid date."""
        self.login(client, "admin", "adminpass")
        response = client.get("/shifts/admin/shifts?date=invalid")
        
        assert response.status_code == 200  # Should default to today
    
    def test_assign_shift_missing_fields(self, client, app, admin_user):
        """Test assigning shift with missing fields."""
        self.login(client, "admin", "adminpass")
        response = client.post(
            "/shifts/admin/shifts/assign",
            data={},
            follow_redirects=True
        )
        
        assert response.status_code == 200
    
    def test_assign_shift_invalid_date(self, client, app, admin_user, staff_user, sample_shifts):
        """Test assigning shift with invalid date."""
        self.login(client, "admin", "adminpass")
        response = client.post(
            "/shifts/admin/shifts/assign",
            data={
                "user_id": staff_user,
                "shift_id": sample_shifts[0],
                "date": "invalid",
                "station_role": "Grill Master"
            },
            follow_redirects=True
        )
        
        assert response.status_code == 200

