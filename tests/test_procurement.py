def test_procurement_page(client, db):
    from app.models.user import User
    user = User(username="proc_test", email="proc@test.com")
    user.set_password("test")
    db.session.add(user)
    db.session.commit()
    client.post("/auth/login", data={"username": "proc_test", "password": "test"})
    response = client.get("/procurement/")
    assert response.status_code == 200
