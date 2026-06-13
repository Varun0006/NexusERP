def test_stock_view(client, db):
    from app.models.user import User
    from app.models.role import Role
    user = User(username="test", email="test@test.com")
    user.set_password("test")
    db.session.add(user)
    db.session.commit()
    client.post("/auth/login", data={"username": "test", "password": "test"})
    response = client.get("/inventory/")
    assert response.status_code == 200
