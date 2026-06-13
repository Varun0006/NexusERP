def test_manufacturing_page(client, db):
    from app.models.user import User
    user = User(username="mf_test", email="mf@test.com")
    user.set_password("test")
    db.session.add(user)
    db.session.commit()
    client.post("/auth/login", data={"username": "mf_test", "password": "test"})
    response = client.get("/manufacturing/")
    assert response.status_code == 200
