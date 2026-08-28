from fastapi.testclient import TestClient

from main import app, DB_PATH, get_db, init_db


client = TestClient(app)


def setup_function() -> None:
    if DB_PATH.exists():
        DB_PATH.unlink()
    init_db()


def test_health() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["fleet_status"] == "OPERATIONAL"


def test_checkin_success_then_duplicate() -> None:
    created = client.post(
        "/api/guests",
        json={"first_name": "Amélie", "last_name": "Laurent", "phone": "+33600000000", "table_number": "Table 03"},
    )
    assert created.status_code == 200
    guest_id = created.json()["id"]

    first = client.post(f"/api/check-in/{guest_id}")
    assert first.status_code == 200
    assert first.json()["status"] == "SUCCESS"
    assert first.json()["table"] == "Table 03"

    duplicate = client.post(f"/api/check-in/{guest_id}")
    assert duplicate.status_code == 200
    assert duplicate.json()["status"] == "ALREADY_SCANNED"


def test_invalid_checkin() -> None:
    response = client.post("/api/check-in/not-a-real-guest")
    assert response.status_code == 200
    assert response.json()["status"] == "INVALID"


def test_dashboard_counts() -> None:
    client.post(
        "/api/guests",
        json={"first_name": "Sofia", "last_name": "Bernard", "phone": "+33600000001", "table_number": "VIP A"},
    )
    stats = client.get("/api/dashboard/stats")
    assert stats.status_code == 200
    assert stats.json()["total"] == 1
    assert stats.json()["present"] == 0


def test_csv_import_and_qr_generation() -> None:
    csv_body = "Nom,Prénom,Téléphone,Table\nDurand,Léa,+33600000002,Table 08\n"
    imported = client.post(
        "/api/import/csv",
        files={"file": ("guests.csv", csv_body, "text/csv")},
    )
    assert imported.status_code == 200
    assert imported.json()["imported"] == 1
    guest = client.get("/api/guests").json()[0]
    qr = client.get(f"/api/qr/{guest['id']}.png")
    assert qr.status_code == 200
    assert qr.headers["content-type"] == "image/png"
