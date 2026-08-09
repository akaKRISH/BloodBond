from datetime import timedelta
from fastapi import status
from app.core.security import create_access_token
from app.models.user import User


def test_registration(client):
    res = client.post(
        "/api/v1/auth/register",
        json={
            "name": "Karan Johar",
            "email": "karan@example.com",
            "phone": "+919876500001",
            "role": "DONOR",
            "password": "SecurePassword123!",
        },
    )
    assert res.status_code == status.HTTP_201_CREATED
    data = res.json()
    assert data["email"] == "karan@example.com"
    assert "password" not in data
    assert "password_hash" not in data
    assert data["is_active"] is True


def test_login_success(client):
    # Register
    client.post(
        "/api/v1/auth/register",
        json={
            "name": "Rohit Sharma",
            "email": "rohit@example.com",
            "phone": "+919876500002",
            "role": "DONOR",
            "password": "MyPassword123!",
        },
    )

    # Login via OAuth2 Form
    res_form = client.post(
        "/api/v1/auth/login",
        data={"username": "rohit@example.com", "password": "MyPassword123!"},
    )
    assert res_form.status_code == status.HTTP_200_OK
    assert "access_token" in res_form.json()

    # Login via JSON body
    res_json = client.post(
        "/api/v1/auth/login/json",
        json={"email": "rohit@example.com", "password": "MyPassword123!"},
    )
    assert res_json.status_code == status.HTTP_200_OK
    assert "access_token" in res_json.json()


def test_login_incorrect_password(client):
    client.post(
        "/api/v1/auth/register",
        json={
            "name": "Suresh Raina",
            "email": "suresh@example.com",
            "phone": "+919876500003",
            "role": "DONOR",
            "password": "CorrectPassword123!",
        },
    )

    res = client.post(
        "/api/v1/auth/login/json",
        json={"email": "suresh@example.com", "password": "WrongPassword123!"},
    )
    assert res.status_code == status.HTTP_401_UNAUTHORIZED
    assert res.json()["detail"] == "Incorrect email or password"


def test_invalid_token(client):
    res = client.get(
        "/api/v1/users/me",
        headers={"Authorization": "Bearer invalid_garbage_token_123"},
    )
    assert res.status_code == status.HTTP_401_UNAUTHORIZED


def test_expired_token(client):
    # Register user
    reg = client.post(
        "/api/v1/auth/register",
        json={
            "name": "Virat Kohli",
            "email": "virat@example.com",
            "phone": "+919876500004",
            "role": "DONOR",
            "password": "Password123!",
        },
    ).json()

    # Generate an expired token (-1 minute)
    expired_token = create_access_token(
        subject=reg["id"],
        expires_delta=timedelta(minutes=-1),
    )

    res = client.get(
        "/api/v1/users/me",
        headers={"Authorization": f"Bearer {expired_token}"},
    )
    assert res.status_code == status.HTTP_401_UNAUTHORIZED


def test_protected_endpoint_without_token(client):
    res = client.get("/api/v1/users/me")
    assert res.status_code == status.HTTP_401_UNAUTHORIZED


def test_donor_access_own_profile(client):
    reg = client.post(
        "/api/v1/auth/register",
        json={
            "name": "Jasprit Bumrah",
            "email": "bumrah@example.com",
            "phone": "+919876500005",
            "role": "DONOR",
            "password": "Password123!",
        },
    ).json()

    login = client.post(
        "/api/v1/auth/login/json",
        json={"email": "bumrah@example.com", "password": "Password123!"},
    ).json()

    headers = {"Authorization": f"Bearer {login['access_token']}"}

    # Access self via GET /me
    me_res = client.get("/api/v1/users/me", headers=headers)
    assert me_res.status_code == status.HTTP_200_OK
    assert me_res.json()["email"] == "bumrah@example.com"

    # Create Donor profile for self
    donor_res = client.post(
        "/api/v1/donors",
        json={
            "blood_group": "B+",
            "city": "Mumbai",
            "latitude": 19.0760,
            "longitude": 72.8777,
            "is_available": True,
        },
        headers=headers,
    )
    assert donor_res.status_code == status.HTTP_201_CREATED
    donor_id = donor_res.json()["id"]

    # Toggle availability for self
    toggle_res = client.patch(
        f"/api/v1/donors/{donor_id}/availability?is_available=false",
        headers=headers,
    )
    assert toggle_res.status_code == status.HTTP_200_OK
    assert toggle_res.json()["is_available"] is False


def test_donor_attempting_to_modify_another_donor(client):
    # Donor 1
    client.post(
        "/api/v1/auth/register",
        json={
            "name": "Donor One",
            "email": "donor1@example.com",
            "phone": "+919876500006",
            "role": "DONOR",
            "password": "Password123!",
        },
    )
    token1 = client.post(
        "/api/v1/auth/login/json",
        json={"email": "donor1@example.com", "password": "Password123!"},
    ).json()["access_token"]
    headers1 = {"Authorization": f"Bearer {token1}"}

    donor1_profile = client.post(
        "/api/v1/donors",
        json={
            "blood_group": "O+",
            "city": "Delhi",
            "latitude": 28.6139,
            "longitude": 77.2090,
        },
        headers=headers1,
    ).json()

    # Donor 2
    client.post(
        "/api/v1/auth/register",
        json={
            "name": "Donor Two",
            "email": "donor2@example.com",
            "phone": "+919876500007",
            "role": "DONOR",
            "password": "Password123!",
        },
    )
    token2 = client.post(
        "/api/v1/auth/login/json",
        json={"email": "donor2@example.com", "password": "Password123!"},
    ).json()["access_token"]
    headers2 = {"Authorization": f"Bearer {token2}"}

    # Donor 2 attempts to toggle Donor 1's availability
    res = client.patch(
        f"/api/v1/donors/{donor1_profile['id']}/availability?is_available=false",
        headers=headers2,
    )
    assert res.status_code == status.HTTP_403_FORBIDDEN


def test_requester_accessing_own_request(client):
    client.post(
        "/api/v1/auth/register",
        json={
            "name": "Requester One",
            "email": "req1@example.com",
            "phone": "+919876500008",
            "role": "REQUESTER",
            "password": "Password123!",
        },
    )
    token = client.post(
        "/api/v1/auth/login/json",
        json={"email": "req1@example.com", "password": "Password123!"},
    ).json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    req_res = client.post(
        "/api/v1/requests",
        json={
            "patient_name": "Family Member",
            "blood_group": "AB+",
            "units_needed": 1,
            "urgency": "URGENT",
            "hospital_name": "City Hospital",
            "city": "Mumbai",
            "latitude": 19.0760,
            "longitude": 72.8777,
        },
        headers=headers,
    )
    assert req_res.status_code == status.HTTP_201_CREATED
    req_id = req_res.json()["id"]

    # Requester updates own status
    status_res = client.patch(
        f"/api/v1/requests/{req_id}/status?status=CANCELLED",
        headers=headers,
    )
    assert status_res.status_code == status.HTTP_200_OK
    assert status_res.json()["status"] == "CANCELLED"


def test_requester_attempting_to_access_another_user_request(client):
    # Requester 1
    client.post(
        "/api/v1/auth/register",
        json={
            "name": "Req User 1",
            "email": "r1@example.com",
            "phone": "+919876500009",
            "role": "REQUESTER",
            "password": "Password123!",
        },
    )
    t1 = client.post(
        "/api/v1/auth/login/json",
        json={"email": "r1@example.com", "password": "Password123!"},
    ).json()["access_token"]
    h1 = {"Authorization": f"Bearer {t1}"}

    req1_id = client.post(
        "/api/v1/requests",
        json={
            "patient_name": "Patient 1",
            "blood_group": "O+",
            "units_needed": 2,
            "urgency": "URGENT",
            "hospital_name": "Hospital 1",
            "city": "Delhi",
            "latitude": 28.6139,
            "longitude": 77.2090,
        },
        headers=h1,
    ).json()["id"]

    # Requester 2
    client.post(
        "/api/v1/auth/register",
        json={
            "name": "Req User 2",
            "email": "r2@example.com",
            "phone": "+919876500010",
            "role": "REQUESTER",
            "password": "Password123!",
        },
    )
    t2 = client.post(
        "/api/v1/auth/login/json",
        json={"email": "r2@example.com", "password": "Password123!"},
    ).json()["access_token"]
    h2 = {"Authorization": f"Bearer {t2}"}

    # Requester 2 attempts to modify status of Requester 1's request
    res = client.patch(
        f"/api/v1/requests/{req1_id}/status?status=CANCELLED",
        headers=h2,
    )
    assert res.status_code == status.HTTP_403_FORBIDDEN


def test_admin_authorization(client):
    # Admin User
    client.post(
        "/api/v1/auth/register",
        json={
            "name": "System Admin",
            "email": "admin@example.com",
            "phone": "+919876500099",
            "role": "ADMIN",
            "password": "AdminPassword123!",
        },
    )
    t_admin = client.post(
        "/api/v1/auth/login/json",
        json={"email": "admin@example.com", "password": "AdminPassword123!"},
    ).json()["access_token"]
    h_admin = {"Authorization": f"Bearer {t_admin}"}

    # Admin list all users
    list_res = client.get("/api/v1/users", headers=h_admin)
    assert list_res.status_code == status.HTTP_200_OK

    # Non-Admin attempts list users
    client.post(
        "/api/v1/auth/register",
        json={
            "name": "Normal User",
            "email": "normal@example.com",
            "phone": "+919876500011",
            "role": "DONOR",
            "password": "Password123!",
        },
    )
    t_normal = client.post(
        "/api/v1/auth/login/json",
        json={"email": "normal@example.com", "password": "Password123!"},
    ).json()["access_token"]
    h_normal = {"Authorization": f"Bearer {t_normal}"}

    forbidden_res = client.get("/api/v1/users", headers=h_normal)
    assert forbidden_res.status_code == status.HTTP_403_FORBIDDEN


def test_duplicate_email(client):
    client.post(
        "/api/v1/auth/register",
        json={
            "name": "First User",
            "email": "dup@example.com",
            "phone": "+919876500012",
            "role": "DONOR",
            "password": "Password123!",
        },
    )

    dup_res = client.post(
        "/api/v1/auth/register",
        json={
            "name": "Second User",
            "email": "dup@example.com",
            "phone": "+919876500013",
            "role": "DONOR",
            "password": "Password123!",
        },
    )
    assert dup_res.status_code == status.HTTP_400_BAD_REQUEST


def test_inactive_user_rejection(client, db_session):
    reg = client.post(
        "/api/v1/auth/register",
        json={
            "name": "Inactive User",
            "email": "inactive@example.com",
            "phone": "+919876500014",
            "role": "DONOR",
            "password": "Password123!",
        },
    ).json()

    # Manually deactivate user in DB
    user_db = db_session.query(User).filter(User.id == reg["id"]).first()
    user_db.is_active = False
    db_session.commit()

    # Attempt login
    login_res = client.post(
        "/api/v1/auth/login/json",
        json={"email": "inactive@example.com", "password": "Password123!"},
    )
    assert login_res.status_code == status.HTTP_400_BAD_REQUEST
    assert login_res.json()["detail"] == "Inactive user account"
