import pytest


def test_create_claim_success(client, clear_store, employee_token):
    response = client.post(
        "/claims",
        json={
            "amount": 100.0,
            "description": "This is a test expense claim",
            "receipt_path": "/receipts/receipt.pdf",
            "category": "Travel"
        },
        headers={"Authorization": f"Bearer {employee_token}"}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["claim_id"] == "CLM00001"
    assert data["employee_id"] == "emp1"
    assert data["amount"] == 100.0
    assert data["status"] == "draft"
    assert data["manager_id"] == "mgr1"


def test_create_claim_invalid_amount(client, clear_store, employee_token):
    response = client.post(
        "/claims",
        json={
            "amount": 0,
            "description": "This is a test expense claim",
            "receipt_path": "/receipts/receipt.pdf"
        },
        headers={"Authorization": f"Bearer {employee_token}"}
    )
    assert response.status_code == 422


def test_create_claim_invalid_description(client, clear_store, employee_token):
    response = client.post(
        "/claims",
        json={
            "amount": 100.0,
            "description": "Short",
            "receipt_path": "/receipts/receipt.pdf"
        },
        headers={"Authorization": f"Bearer {employee_token}"}
    )
    assert response.status_code == 422


def test_create_claim_missing_receipt(client, clear_store, employee_token):
    response = client.post(
        "/claims",
        json={
            "amount": 100.0,
            "description": "This is a test expense claim",
            "receipt_path": ""
        },
        headers={"Authorization": f"Bearer {employee_token}"}
    )
    assert response.status_code == 422


def test_create_claim_manager_only(client, clear_store, manager_token):
    response = client.post(
        "/claims",
        json={
            "amount": 100.0,
            "description": "This is a test expense claim",
            "receipt_path": "/receipts/receipt.pdf"
        },
        headers={"Authorization": f"Bearer {manager_token}"}
    )
    assert response.status_code == 403


def test_get_claim_success(client, clear_store, employee_token):
    client.post(
        "/claims",
        json={
            "amount": 100.0,
            "description": "This is a test expense claim",
            "receipt_path": "/receipts/receipt.pdf"
        },
        headers={"Authorization": f"Bearer {employee_token}"}
    )

    response = client.get(
        "/claims/CLM00001",
        headers={"Authorization": f"Bearer {employee_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["claim_id"] == "CLM00001"


def test_get_claim_not_found(client, clear_store, employee_token):
    response = client.get(
        "/claims/CLM99999",
        headers={"Authorization": f"Bearer {employee_token}"}
    )
    assert response.status_code == 404


def test_get_claim_forbidden_for_other_employee(client, clear_store, employee_token, other_employee_token):
    client.post(
        "/claims",
        json={
            "amount": 100.0,
            "description": "This is a test expense claim",
            "receipt_path": "/receipts/receipt.pdf"
        },
        headers={"Authorization": f"Bearer {employee_token}"}
    )

    response = client.get(
        "/claims/CLM00001",
        headers={"Authorization": f"Bearer {other_employee_token}"}
    )
    assert response.status_code == 403


def test_list_claims_employee_own_only(client, clear_store, employee_token, other_employee_token):
    client.post(
        "/claims",
        json={
            "amount": 100.0,
            "description": "This is a test expense claim",
            "receipt_path": "/receipts/receipt.pdf"
        },
        headers={"Authorization": f"Bearer {employee_token}"}
    )

    client.post(
        "/claims",
        json={
            "amount": 200.0,
            "description": "Another test expense claim",
            "receipt_path": "/receipts/receipt2.pdf"
        },
        headers={"Authorization": f"Bearer {other_employee_token}"}
    )

    response = client.get(
        "/claims",
        headers={"Authorization": f"Bearer {employee_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["employee_id"] == "emp1"


def test_list_claims_manager_assigned_only(client, clear_store, employee_token, manager_token):
    client.post(
        "/claims",
        json={
            "amount": 100.0,
            "description": "This is a test expense claim",
            "receipt_path": "/receipts/receipt.pdf"
        },
        headers={"Authorization": f"Bearer {employee_token}"}
    )

    response = client.get(
        "/claims",
        headers={"Authorization": f"Bearer {manager_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1


def test_list_claims_finance_all(client, clear_store, employee_token, other_employee_token, finance_token):
    client.post(
        "/claims",
        json={
            "amount": 100.0,
            "description": "This is a test expense claim",
            "receipt_path": "/receipts/receipt.pdf"
        },
        headers={"Authorization": f"Bearer {employee_token}"}
    )

    client.post(
        "/claims",
        json={
            "amount": 200.0,
            "description": "Another test expense claim",
            "receipt_path": "/receipts/receipt2.pdf"
        },
        headers={"Authorization": f"Bearer {other_employee_token}"}
    )

    response = client.get(
        "/claims",
        headers={"Authorization": f"Bearer {finance_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2


def test_list_claims_filter_by_status(client, clear_store, employee_token, manager_token):
    client.post(
        "/claims",
        json={
            "amount": 100.0,
            "description": "This is a test expense claim",
            "receipt_path": "/receipts/receipt.pdf"
        },
        headers={"Authorization": f"Bearer {employee_token}"}
    )

    client.put(
        "/claims/CLM00001/submit",
        headers={"Authorization": f"Bearer {employee_token}"}
    )

    response = client.get(
        "/claims?status=submitted",
        headers={"Authorization": f"Bearer {employee_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1

    response = client.get(
        "/claims?status=draft",
        headers={"Authorization": f"Bearer {employee_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 0


def test_update_draft_claim_success(client, clear_store, employee_token):
    client.post(
        "/claims",
        json={
            "amount": 100.0,
            "description": "This is a test expense claim",
            "receipt_path": "/receipts/receipt.pdf"
        },
        headers={"Authorization": f"Bearer {employee_token}"}
    )

    response = client.patch(
        "/claims/CLM00001",
        json={
            "amount": 150.0,
            "description": "Updated test expense claim"
        },
        headers={"Authorization": f"Bearer {employee_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["amount"] == 150.0


def test_update_submitted_claim_forbidden(client, clear_store, employee_token):
    client.post(
        "/claims",
        json={
            "amount": 100.0,
            "description": "This is a test expense claim",
            "receipt_path": "/receipts/receipt.pdf"
        },
        headers={"Authorization": f"Bearer {employee_token}"}
    )

    client.put(
        "/claims/CLM00001/submit",
        headers={"Authorization": f"Bearer {employee_token}"}
    )

    response = client.patch(
        "/claims/CLM00001",
        json={"amount": 150.0},
        headers={"Authorization": f"Bearer {employee_token}"}
    )
    assert response.status_code == 409
