def test_create_vehicle_container(client, haulier):
    response = client.post(
        "/vehicles-containers",
        json={"type": "vehicle", "identifier": "KTP004", "size": "small", "haulier_id": haulier},
    )
    assert response.status_code == 201
    assert response.json()["status"] == "registered"
    
def test_create_vehicle_container_wrong_type(client, haulier):
    response = client.post(
        "/vehicles-containers",
        json={"type": "truck", "identifier": "KTP004", "size": "small", "haulier_id": haulier},
    )
    assert response.status_code == 422
    
def test_create_vehicle_container_wrong_id(client):
    response = client.post(
        "/vehicles-containers",
        json={"type": "vehicle", "identifier": "KTP004", "size": "small", "haulier_id": 999},
    )
    assert response.status_code == 404
    assert response.json() == {"detail": "no user with that haulier_id"}
    
def test_list_filters_by_type(client, haulier):
    r1 = client.post("/vehicles-containers", json={
        "type": "container",
        "identifier": "MSKU1000001",
        "size": "small",
        "haulier_id": haulier,
    })
    assert r1.status_code == 201
    
    r2 = client.post("/vehicles-containers", json={
        "type": "vehicle",
        "identifier": "KTP005",
        "size": "small",
        "haulier_id": haulier,
    })
    assert r2.status_code == 201
    
    response = client.get("/vehicles-containers", params={"type": "container"})
    assert response.status_code == 200
    
    items = response.json()
    assert len(items) == 1
    assert items[0]["type"] == "container"
    assert items[0]["identifier"] == "MSKU1000001"
    