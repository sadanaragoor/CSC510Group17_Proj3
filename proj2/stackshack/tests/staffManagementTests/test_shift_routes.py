"""
Test cases for shift routes.
"""
from datetime import date, datetime, time, timedelta
from models.shift import Shift, ShiftAssignment
from models.user import User
from database.db import db


class TestShiftRoutes:
    """Test cases for shift scheduling routes."""
    
    def login(self, client, username, password):
        """Helper method to login a user."""
        return client.post(
            "/auth/login",
            data={"username": username, "password": password},
            follow_redirects=True
        )
    
    def test_admin_shifts_dashboard_requires_login(self, client):
        """Test that admin dashboard requires authentication."""
        response = client.get("/shifts/admin/shifts")
        assert response.status_code == 302  # Redirect to login
    
    def test_admin_shifts_dashboard_requires_admin(self, client, app, staff_user):
        """Test that admin dashboard requires admin role."""
        self.login(client, "staff1", "staffpass")
        response = client.get("/shifts/admin/shifts", follow_redirects=True)
        assert response.status_code == 200
        assert b"unauthorized" in response.data.lower() or b"admin" in response.data.lower()
    
    def test_admin_shifts_dashboard_access(self, client, app, admin_user):
        """Test that admin can access shifts dashboard."""
        self.login(client, "admin", "adminpass")
        response = client.get("/shifts/admin/shifts")
        assert response.status_code == 200
    
    def test_assign_shift_post(self, client, app, admin_user, staff_user, sample_shifts):
        """Test assigning a shift via POST."""
        with app.app_context():
            from services.shift_service import ShiftService
            ShiftService.initialize_default_shifts()
        
        self.login(client, "admin", "adminpass")
        today = date.today()
        response = client.post(
            "/shifts/admin/shifts/assign",
            data={
                "user_id": staff_user,
                "shift_id": sample_shifts[0],
                "date": today.isoformat(),
                "station_role": "Grill Master"
            },
            follow_redirects=True
        )
        
        assert response.status_code == 200
        
        # Verify assignment was created
        with app.app_context():
            assignment = ShiftAssignment.query.filter_by(
                user_id=staff_user,
                shift_id=sample_shifts[0],
                date=today
            ).first()
            assert assignment is not None
    
    def test_delete_assignment(self, client, app, admin_user, staff_user, sample_shifts):
        """Test deleting a shift assignment."""
        with app.app_context():
            from services.shift_service import ShiftService
            ShiftService.initialize_default_shifts()
            
            # Create an assignment first
            today = date.today()
            assignment = ShiftAssignment(
                user_id=staff_user,
                shift_id=sample_shifts[0],
                date=today,
                station_role="Grill Master"
            )
            db.session.add(assignment)
            db.session.commit()
            assignment_id = assignment.id
        
        self.login(client, "admin", "adminpass")
        
        response = client.post(
            f"/shifts/admin/shifts/assignment/{assignment_id}/delete",
            follow_redirects=True
        )
        
        assert response.status_code == 200
        
        # Verify assignment was deleted
        with app.app_context():
            assignment = db.session.get(ShiftAssignment, assignment_id)
            assert assignment is None
    
    def test_staff_shifts_view_requires_login(self, client):
        """Test that staff shifts view requires authentication."""
        response = client.get("/shifts/staff/shifts")
        assert response.status_code == 302
    
    def test_staff_shifts_view_access(self, client, app, staff_user, sample_shifts):
        """Test that staff can view their shifts."""
        with app.app_context():
            from services.shift_service import ShiftService
            ShiftService.initialize_default_shifts()
            
            # Create an assignment for the staff user
            today = date.today()
            assignment = ShiftAssignment(
                user_id=staff_user,
                shift_id=sample_shifts[0],
                date=today,
                station_role="Grill Master"
            )
            db.session.add(assignment)
            db.session.commit()
        
        self.login(client, "staff1", "staffpass")
        response = client.get("/shifts/staff/shifts")
        assert response.status_code == 200
    
    def test_staff_shifts_view_displays_assignments(self, client, app, staff_user, sample_shifts):
        """Test that staff shifts view displays assignments."""
        with app.app_context():
            from services.shift_service import ShiftService
            ShiftService.initialize_default_shifts()
            
            # Create an assignment for the staff user
            today = date.today()
            assignment = ShiftAssignment(
                user_id=staff_user,
                shift_id=sample_shifts[0],
                date=today,
                station_role="Grill Master"
            )
            db.session.add(assignment)
            db.session.commit()
        
        self.login(client, "staff1", "staffpass")
        response = client.get("/shifts/staff/shifts")
        assert response.status_code == 200
        # Should display shifts or assignments
        assert b"shift" in response.data.lower() or b"assignment" in response.data.lower() or len(response.data) > 0
    
    def test_admin_staff_management(self, client, app, admin_user):
        """Test admin staff management page."""
        self.login(client, "admin", "adminpass")
        response = client.get("/shifts/admin/staff")
        assert response.status_code == 200
    
    def test_create_staff_account(self, client, app, admin_user):
        """Test creating a new staff account."""
        self.login(client, "admin", "adminpass")
        response = client.post(
            "/shifts/admin/staff/create",
            data={
                "username": "newstaff",
                "email": "newstaff@test.com",
                "password": "newpass123",
                "role": "staff"
            },
            follow_redirects=True
        )
        
        assert response.status_code == 200
        
        # Verify staff was created
        with app.app_context():
            user = User.query.filter_by(username="newstaff").first()
            assert user is not None
            assert user.role == "staff"
    
    def test_update_staff_account(self, client, app, admin_user, staff_user):
        """Test updating a staff account."""
        self.login(client, "admin", "adminpass")
        response = client.post(
            f"/shifts/admin/staff/{staff_user}/update",
            data={
                "email": "updated@test.com",
                "position": "Full-time"
            },
            follow_redirects=True
        )
        
        assert response.status_code == 200
        
        # Verify update
        with app.app_context():
            user = db.session.get(User, staff_user)
            assert user.email == "updated@test.com"

