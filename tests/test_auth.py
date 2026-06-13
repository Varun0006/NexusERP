def test_login_page(client):
    response = client.get("/auth/login")
    assert response.status_code == 200


def test_register(client, db):
    from app.models.user import User
    from app.models.role import Role
    role = Role(name="Staff", description="Staff role")
    db.session.add(role)
    db.session.commit()
    response = client.post("/auth/register", data={
        "username": "testuser",
        "email": "test@example.com",
        "full_name": "Test User",
        "password": "password123",
        "confirm_password": "password123",
    }, follow_redirects=True)
    assert response.status_code == 200
    assert User.query.filter_by(username="testuser").first() is not None
