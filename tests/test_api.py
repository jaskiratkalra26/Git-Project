def test_root(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to the API"}

def test_ping(client):
    response = client.get("/ping")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_auth_route(client):
    response = client.get("/auth/test")
    assert response.status_code == 200
    assert response.json() == {"message": "ok"}

def test_repos_route(client):
    response = client.get("/repos/test")
    assert response.status_code == 200
    assert response.json() == {"message": "ok"}

def test_projects_route(client):
    response = client.get("/projects/test")
    assert response.status_code == 200
    assert response.json() == {"message": "ok"}
