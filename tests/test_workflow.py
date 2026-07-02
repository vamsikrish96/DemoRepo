import pytest


def test_submit_claim_success(client, clear_store, employee_token):
    client.post(
        "/claims",
        json={
            "amount": 100.0,
            "description": "This is a test expense claim",
            "receipt_path": "/receipts/receipt.pdf"
        },
        headers={"Authorization": f"Bearer {employee_token}"}
    )

    response = client.put(
        "/claims/CLM00001/submit",
        headers={"Authorization": f"Bearer {employee_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "submitted"
    assert data["submission_date"] is not None


def test_submit_non_draft_claim_forbidden(client, clear_store, employee_token):
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

    response = client.put(
        "/claims/CLM00001/submit",
        headers={"Authorization": f"Bearer {employee_token}"}
    )
    assert response.status_code == 409


def test_approve_claim_success(client, clear_store, employee_token, manager_token):
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

    response = client.put(
        "/claims/CLM00001/approve",
        json={"approval_reason": "Approved for business purposes"},
        headers={"Authorization": f"Bearer {manager_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "approved"
    assert data["approval_reason"] == "Approved for business purposes"


def test_approve_claim_not_manager(client, clear_store, employee_token):
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

    response = client.put(
        "/claims/CLM00001/approve",
        json={"approval_reason": "Approved"},
        headers={"Authorization": f"Bearer {employee_token}"}
    )
    assert response.status_code == 403


def test_reject_claim_success(client, clear_store, employee_token, manager_token):
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

    response = client.put(
        "/claims/CLM00001/reject",
        json={"approval_reason": "Insufficient documentation"},
        headers={"Authorization": f"Bearer {manager_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "rejected"
    assert data["rejection_reason"] == "Insufficient documentation"


def test_process_claim_success(client, clear_store, employee_token, manager_token, finance_token):
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

    client.put(
        "/claims/CLM00001/approve",
        json={"approval_reason": "Approved"},
        headers={"Authorization": f"Bearer {manager_token}"}
    )

    response = client.put(
        "/claims/CLM00001/process",
        headers={"Authorization": f"Bearer {finance_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "processed"
    assert data["processed_date"] is not None


def test_process_claim_not_finance(client, clear_store, employee_token, manager_token):
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

    client.put(
        "/claims/CLM00001/approve",
        json={"approval_reason": "Approved"},
        headers={"Authorization": f"Bearer {manager_token}"}
    )

    response = client.put(
        "/claims/CLM00001/process",
        headers={"Authorization": f"Bearer {employee_token}"}
    )
    assert response.status_code == 403


def test_cancel_draft_claim(client, clear_store, employee_token):
    client.post(
        "/claims",
        json={
            "amount": 100.0,
            "description": "This is a test expense claim",
            "receipt_path": "/receipts/receipt.pdf"
        },
        headers={"Authorization": f"Bearer {employee_token}"}
    )

    response = client.put(
        "/claims/CLM00001/cancel",
        headers={"Authorization": f"Bearer {employee_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "cancelled"


def test_cancel_submitted_claim(client, clear_store, employee_token):
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

    response = client.put(
        "/claims/CLM00001/cancel",
        headers={"Authorization": f"Bearer {employee_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "cancelled"


def test_cancel_processed_claim_forbidden(client, clear_store, employee_token, manager_token, finance_token):
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

    client.put(
        "/claims/CLM00001/approve",
        json={"approval_reason": "Approved"},
        headers={"Authorization": f"Bearer {manager_token}"}
    )

    client.put(
        "/claims/CLM00001/process",
        headers={"Authorization": f"Bearer {finance_token}"}
    )

    response = client.put(
        "/claims/CLM00001/cancel",
        headers={"Authorization": f"Bearer {employee_token}"}
    )
    assert response.status_code == 409


def test_happy_path_workflow(client, clear_store, employee_token, manager_token, finance_token):
    # Employee creates claim
    create_response = client.post(
        "/claims",
        json={
            "amount": 100.0,
            "description": "Business travel for conference",
            "receipt_path": "/receipts/travel.pdf"
        },
        headers={"Authorization": f"Bearer {employee_token}"}
    )
    assert create_response.status_code == 201

    # Employee submits claim
    submit_response = client.put(
        "/claims/CLM00001/submit",
        headers={"Authorization": f"Bearer {employee_token}"}
    )
    assert submit_response.status_code == 200

    # Manager approves claim
    approve_response = client.put(
        "/claims/CLM00001/approve",
        json={"approval_reason": "Approved for business purposes"},
        headers={"Authorization": f"Bearer {manager_token}"}
    )
    assert approve_response.status_code == 200

    # Finance processes claim
    process_response = client.put(
        "/claims/CLM00001/process",
        headers={"Authorization": f"Bearer {finance_token}"}
    )
    assert process_response.status_code == 200
    data = process_response.json()
    assert data["status"] == "processed"
