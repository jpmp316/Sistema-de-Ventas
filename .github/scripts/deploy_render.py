"""Deploy the tested Git SHA and wait for Render. Uses only the Python stdlib."""

import json
import os
import sys
import time
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen


def request_json(url, api_key, payload=None):
    request = Request(
        url,
        data=json.dumps(payload).encode() if payload is not None else None,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        },
    )
    with urlopen(request, timeout=30) as response:
        return json.load(response)


def deploy(api_key, service_id, commit, timeout=1500):
    url = f"https://api.render.com/v1/services/{quote(service_id, safe='')}/deploys"
    # Do not retry POST automatically: a timeout may still have created a deployment.
    created = request_json(url, api_key, {"commitId": commit})
    deploy_id = created["id"]
    print(f"Render deployment {deploy_id} started for {commit}", flush=True)
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        try:
            result = request_json(f"{url}/{quote(deploy_id, safe='')}", api_key)
        except HTTPError as error:
            if error.code != 429 and error.code < 500:
                raise
            print(f"Render status temporarily unavailable (HTTP {error.code})", flush=True)
            time.sleep(20)
            continue
        except URLError:
            print("Temporary network error while checking Render", flush=True)
            time.sleep(20)
            continue
        status = result["status"]
        print(f"Render status: {status}", flush=True)
        if status == "live":
            return
        if status in {"build_failed", "update_failed", "pre_deploy_failed", "canceled", "deactivated"}:
            raise RuntimeError(f"Render deployment ended with status {status}")
        time.sleep(15)
    raise TimeoutError("Render did not become live within 25 minutes. Check its dashboard.")


def main():
    settings = {name: os.environ.get(name) for name in (
        "RENDER_API_KEY", "RENDER_SERVICE_ID", "GITHUB_SHA",
    )}
    missing = [name for name, value in settings.items() if not value]
    if missing:
        raise RuntimeError("Missing deployment settings: " + ", ".join(missing))
    deploy(settings["RENDER_API_KEY"], settings["RENDER_SERVICE_ID"], settings["GITHUB_SHA"])


if __name__ == "__main__":
    try:
        main()
    except HTTPError as error:
        print(f"::error::Render API returned HTTP {error.code}. Check credentials and service.")
        sys.exit(1)
    except (RuntimeError, TimeoutError, URLError, KeyError, ValueError) as error:
        print(f"::error::{error}")
        sys.exit(1)
