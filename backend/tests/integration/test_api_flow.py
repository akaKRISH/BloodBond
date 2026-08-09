from fastapi import status


def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["status"] == "healthy"


def test_full_matching_flow(client):
    # 1. Register Donor User
    user1_resp = client.post(
        "/api/v1/users",
        json={
            "name": "Arjun Sharma",
            "email": "arjun@example.com",
            "phone": "+919876543210",
            "role": "DONOR",
        },
    )
    assert user1_resp.status_code == status.HTTP_201_CREATED
    donor_user_id = user1_resp.json()["id"]

    # 2. Create Donor Profile (O- Universal Donor in Delhi)
    donor_resp = client.post(
        "/api/v1/donors",
        json={
            "user_id": donor_user_id,
            "blood_group": "O-",
            "city": "Delhi",
            "latitude": 28.6139,
            "longitude": 77.2090,
            "is_available": True,
        },
    )
    assert donor_resp.status_code == status.HTTP_201_CREATED

    # 3. Register Requester User
    user2_resp = client.post(
        "/api/v1/users",
        json={
            "name": "Priya Singh",
            "email": "priya@example.com",
            "phone": "+919876543211",
            "role": "REQUESTER",
        },
    )
    assert user2_resp.status_code == status.HTTP_201_CREATED
    requester_user_id = user2_resp.json()["id"]

    # 4. Create Emergency Blood Request (A+ needed at AIIMS Delhi ~ 5.2 km away)
    req_resp = client.post(
        "/api/v1/requests",
        json={
            "requester_id": requester_user_id,
            "patient_name": "Priya's Mother",
            "blood_group": "A+",
            "units_needed": 2,
            "urgency": "CRITICAL",
            "hospital_name": "AIIMS Delhi",
            "city": "Delhi",
            "latitude": 28.5672,
            "longitude": 77.2100,
        },
    )
    assert req_resp.status_code == status.HTTP_201_CREATED
    request_id = req_resp.json()["id"]

    # 5. Trigger Matching Engine (10km radius)
    match_resp = client.post(f"/api/v1/requests/{request_id}/match?radius_km=10.0")
    assert match_resp.status_code == status.HTTP_200_OK
    matches = match_resp.json()
    assert len(matches) == 1
    assert matches[0]["is_compatible"] is True
    assert matches[0]["distance_km"] < 10.0

    # 6. Verify Frontend DTO endpoint returns the donor
    dto_resp = client.get("/api/v1/donors/frontend-dto")
    assert dto_resp.status_code == status.HTTP_200_OK
    dto_data = dto_resp.json()
    assert len(dto_data) == 1
    assert dto_data[0]["name"] == "Arjun Sharma"
    assert dto_data[0]["bt"] == "O-"
