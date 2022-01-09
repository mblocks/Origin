# -*- coding: utf-8 -*-


def test_get_index(client):
    response = client.get("/welcome")
    assert response.status_code == 200


def test_post_join(client):
    response = client.post(
        "/welcome/join",
        json={"user_name": "test", "password": "test", "display_name": "asdf"}
    )
    assert response.status_code == 200


def test_post_login(client):
    client.post(
        "/welcome/join",
        json={"user_name": "test_login",
              "password": "test111111", "display_name": "asdf"}
    )
    response = client.post(
        "/welcome/login",
        json={"user_name": "test_login", "password": "test111111"}
    )
    assert response.status_code == 200


def test_get_admin_apps(client):
    response = client.get("/admin/apps")
    assert response.status_code == 200


def test_post_admin_apps(client):
    response = client.post("/admin/apps",
                           json={
                               "name": "hello",
                               "image": "nginx:alpine"
                           })
    assert response.status_code == 200


def test_post_admin_app_update(client):
    creaded_app = client.post("/admin/apps",
                              json={
                                  "name": "hello_update",
                                  "image": "nginx:alpine"
                              }).json()
    response = client.post("/admin/apps/{}".format(creaded_app.get("id")),
                           json={"image": "nginx:alpine"})
    assert response.status_code == 200


def test_post_admin_app_delete(client):
    creaded_app = client.post("/admin/apps",
                              json={
                                  "name": "hello_delete",
                                  "image": "nginx:alpine"
                              }).json()
    response = client.post(
        "/admin/apps/{}/delete".format(creaded_app.get("id")))
    assert response.status_code == 200


def test_get_admin_app_roles(client):
    creaded_app = client.post("/admin/apps",
                              json={
                                  "name": "hello_roles",
                                  "image": "nginx:alpine"
                              }).json()
    response = client.get("/admin/apps/{}/roles".format(creaded_app.get("id")))
    assert response.status_code == 200


def test_post_admin_app_roles(client):
    creaded_app = client.post("/admin/apps",
                              json={
                                  "name": "hello_roles_create",
                                  "image": "nginx:alpine"
                              }).json()
    url = "/admin/apps/{}/roles".format(creaded_app.get("id"))
    response = client.post(url,
                           json={
                               "title": "string",
                               "auth": {
                                        "query": {
                                            "title": "arole",
                                            "conditions": [
                                                {"name": "user_id", "value": 10}
                                            ]
                                        }
                               },
                               "description": "string",
                               "enabled": True,
                           }
                           )

    assert response.status_code == 200


def test_post_admin_app_role_update(client):
    creaded_app = client.post("/admin/apps",
                              json={
                                  "name": "hello_roles_update",
                                  "image": "nginx:alpine"
                              }).json()
    url = "/admin/apps/{}/roles".format(creaded_app.get("id"))
    created_role = client.post(url,
                               json={
                                   "title": "string",
                                   "auth": {
                                       "query": {
                                           "title": "arole",
                                                    "conditions": [
                                                        {"name": "user_id",
                                                            "value": 10}
                                                    ]
                                       }
                                   },
                                   "description": "string",
                                   "enabled": True,
                               }
                               ).json()
    response = client.post(url + "/{}".format(created_role.get("id")),
                           json={
                               "title": "role_title_updated",
                               "auth": {
                                        "query": {
                                            "title": "updated_arole",
                                            "conditions": [
                                                {"name": "user_id", "value": 10}
                                            ]
                                        }
                               },
                               "description": "string",
                               "enabled": True,
    }
    )
    assert response.status_code == 200
    assert response.json().get('title') == "role_title_updated"


def test_post_admin_app_role_delete(client):
    creaded_app = client.post("/admin/apps",
                              json={
                                  "name": "hello_roles_delete",
                                  "image": "nginx:alpine"
                              }).json()
    url = "/admin/apps/{}/roles".format(creaded_app.get("id"))
    created_role = client.post(url,
                               json={
                                   "title": "string",
                                   "auth": {
                                       "query": {
                                           "title": "delete_arole",
                                                    "conditions": [
                                                        {"name": "user_id",
                                                            "value": 10}
                                                    ]
                                       }
                                   },
                                   "description": "string",
                                   "enabled": True,
                               }
                               ).json()
    response = client.post(url + "/{}/delete".format(created_role.get('id')))
    assert response.status_code == 200


def test_get_admin_users(client):
    response = client.get("/admin/users")
    assert response.status_code == 200


def test_post_admin_users(client):
    response = client.post("/admin/users",
                           json={
                               "user_name": "created_user",
                               "display_name": "string",
                               "email": "string"
                           })
    created_user = response.json()
    assert response.status_code == 200
    assert created_user.get('user_name') == "created_user"


def test_get_admin_user(client):
    creaded_user = client.post("/admin/users",
                               json={
                                   "user_name": "created_user2",
                                   "display_name": "string",
                                   "email": "string"
                               }).json()
    response = client.get("/admin/users/{}".format(creaded_user.get("id")))
    find_user = response.json()
    assert response.status_code == 200
    assert find_user.get('user_name') == "created_user2"


def test_post_admin_user(client):
    creaded_user = client.post("/admin/users",
                               json={
                                   "user_name": "created_user3",
                                   "display_name": "string",
                                   "email": "string"
                               }).json()
    response = client.post("/admin/users/{}".format(creaded_user.get("id")),
                           json={
                               "user_name": "created_user3_updated",
                               "display_name": "string_updated",
    })
    find_user = response.json()
    assert response.status_code == 200
    assert find_user.get('user_name') == "created_user3_updated"


def test_post_admin_user_delete(client):
    creaded_user = client.post("/admin/users",
                               json={
                                   "user_name": "created_user4",
                                   "display_name": "string",
                                   "email": "string"
                               }).json()
    response = client.post(
        "/admin/users/{}/delete".format(creaded_user.get("id")))
    delete_user = response.json()
    assert response.status_code == 200
    assert delete_user.get('user_name') == "created_user4"


def test_post_admin_user_authorized(client):
    creaded_app = client.post(
        "/admin/apps",
        json={
            "name": "hello_user_authorized",
            "image": "nginx:alpine"
        }).json()
    url = "/admin/apps/{}/roles".format(creaded_app.get("id"))
    created_role = client.post(
        url,
        json={
            "title": "string",
            "auth": {
                "query": {
                    "title": "updated_arole",
                    "conditions": [
                        {"name": "user_id", "value": 10}
                    ]
                }
            },
            "description": "string",
            "enabled": True,
        }
    ).json()
    response = client.post(
        "/admin/users/{}/authorized/apps/{}".format(1, creaded_app.get("id")),
        json=[created_role.get("id")])
    authorized = response.json()
    assert response.status_code == 200
    assert created_role.get("id") in (
        [item.get('id') for item in authorized[0].get('roles')])
