import os
import tempfile

import pytest

import agrogasm
import crop_advisory
import market_data


@pytest.fixture()
def client():
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    os.environ["AGROGASM_DB"] = path
    agrogasm.app.config["TESTING"] = True
    with agrogasm.app.test_client() as c:
        with agrogasm.app.app_context():
            agrogasm.init_db(seed=True)
        yield c
    try:
        os.unlink(path)
    except FileNotFoundError:
        pass
    for suffix in ("-wal", "-shm", "-journal"):
        try:
            os.unlink(path + suffix)
        except FileNotFoundError:
            pass


def test_health(client):
    assert client.get("/health").get_json() == {"status": "ok"}


def test_list_pagination(client):
    r = client.get("/?limit=1&offset=0")
    assert r.status_code == 200
    body = r.get_json()
    assert len(body["data"]["posts"]) == 1
    assert body["meta"]["total"] >= 3


def test_search_and_sort(client):
    r = client.get("/?q=spinach&sort=top")
    assert r.status_code == 200
    assert any("spinach" in p["title"].lower() for p in r.get_json()["data"]["posts"])


def test_create_vote_comment(client):
    r = client.post("/community/new", json={"author": "t", "title": "t", "description": "d"})
    assert r.status_code == 201
    pid = r.get_json()["post"]["pid"]
    assert client.post(f"/community/{pid}/vote", json={"direction": "up"}).status_code == 200
    assert client.post(f"/community/{pid}/vote", json={"direction": "x"}).status_code == 400
    assert client.post(f"/community/{pid}/comment", json={"author": "a", "description": "nice"}).status_code == 201
    assert client.get(f"/community/{pid}").status_code == 200


def test_validation(client):
    assert client.post("/community/new", json={}).status_code == 400
    assert client.get("/?sort=nope").status_code == 400


def test_crop_calendar():
    from datetime import date
    cal = crop_advisory.get_crop_calendar(date(2024, 6, 1))
    assert any("Rice" in item["crop"] for item in cal)
    pest = crop_advisory.get_pest_watch(date(2024, 6, 1))
    assert any("Stem borer" in item["pest"] for item in pest)


def test_should_spray():
    ok = crop_advisory.should_spray(wind_speed=5, humidity=60, condition="clear", forecast_rain_4h=False)
    assert ok["verdict"] == "ok"
    bad = crop_advisory.should_spray(wind_speed=15, humidity=90, condition="rain", forecast_rain_4h=True)
    assert bad["verdict"] == "avoid"


def test_advisory_endpoints(client):
    assert client.get("/advisory/crop-calendar").status_code == 200
    assert client.get("/advisory/pest-watch").status_code == 200
    assert client.post("/advisory/spray", json={"wind": 5, "humidity": 60, "condition": "clear"}).status_code == 200
    assert client.post("/advisory/irrigation", json={"temp": 32, "condition": "sunny", "rainfall_mm": 10}).status_code == 200
    assert client.get("/advisory/pesticide?q=neem").status_code == 200
    assert client.get("/advisory/pesticide?q=zzz").get_json()["found"] is False


def test_market_prices(client):
    assert client.get("/market/prices").status_code == 200
    r = client.get("/market/prices?q=rice")
    assert r.status_code == 200
    assert any("rice" in p["crop"].lower() for p in r.get_json()["prices"])


def test_groups(client):
    assert client.get("/groups").status_code == 200
    r = client.post("/groups/new", json={"name": "TestBlock"})
    assert r.status_code == 201
    gid = r.get_json()["group_id"]
    assert client.post("/groups/join", json={"group_id": gid, "user_id": "u1"}).status_code == 200


def test_upload(client):
    from io import BytesIO
    data = {"file": (BytesIO(b"fake png data"), "test.png")}
    r = client.post("/uploads/photo", data=data, content_type="multipart/form-data")
    assert r.status_code == 201
    url = r.get_json()["url"]
    assert url.startswith("/static/uploads/")
    # cleanup
    try:
        import agrogasm as a
        os.unlink(os.path.join(a.app.root_path, "static", "uploads", url.split("/")[-1]))
    except Exception:
        pass


def test_market_prices():
    prices = market_data.get_prices()
    assert len(prices) > 0
    assert market_data.search_prices("rice")
