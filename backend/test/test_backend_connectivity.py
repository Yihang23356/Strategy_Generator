import json
import urllib.error
import urllib.request


BASE_URL = "http://127.0.0.1:8000"


def get_json(path: str):
    req = urllib.request.Request(f"{BASE_URL}{path}", method="GET")
    with urllib.request.urlopen(req, timeout=8) as resp:
        body = resp.read().decode("utf-8")
        return resp.status, json.loads(body)


def post_json(path: str, payload: dict):
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        f"{BASE_URL}{path}",
        method="POST",
        data=data,
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=8) as resp:
        body = resp.read().decode("utf-8")
        return resp.status, json.loads(body)


def main():
    status, health = get_json("/health")
    assert status == 200 and health.get("status") == "ok", "health check failed"
    print("[OK] /health")

    # 发送空 body 到 /run，期望返回 422，说明接口已注册并可访问。
    try:
        post_json("/api/review/run", {})
        raise AssertionError("expected 422, but got 2xx")
    except urllib.error.HTTPError as exc:
        assert exc.code == 422, f"/api/review/run expected 422, got {exc.code}"
        print("[OK] /api/review/run route reachable (422 as expected)")

    print("Backend connectivity test passed.")


if __name__ == "__main__":
    main()
