import os
import socket
import subprocess
import time

import pytest
from playwright.sync_api import sync_playwright


def _wait_for_port(host: str, port: int, timeout: float = 20.0) -> None:
    start = time.time()
    while time.time() - start < timeout:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(1.0)
            if sock.connect_ex((host, port)) == 0:
                return
        time.sleep(0.2)
    raise RuntimeError(f"Server at {host}:{port} did not start")


@pytest.fixture(scope="session")
def app_server():
    env = os.environ.copy()
    env["DATABASE_URL"] = "sqlite:///prototype_test.db"
    env["FLASK_ENV"] = "production"

    process = subprocess.Popen(
        ["python", "-m", "flask", "--app", "run.py", "run", "--port", "5055"],
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    try:
        _wait_for_port("127.0.0.1", 5055, timeout=30.0)
        yield "http://127.0.0.1:5055"
    finally:
        process.terminate()
        process.wait(timeout=10)


def test_rooms_render_and_have_mixed_statuses(app_server):
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto(app_server)

        room_cards = page.locator(".room-card")
        assert room_cards.count() >= 20

        assert page.locator(".status-paid").count() > 0
        assert page.locator(".status-current_unpaid").count() > 0
        assert page.locator(".status-overdue").count() > 0
        browser.close()


def test_payment_history_dropdown_opens(app_server):
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto(app_server)

        first_summary = page.locator(".room-card details summary").first
        first_summary.click()

        first_list = page.locator(".room-card details .history-list").first
        assert first_list.is_visible()
        assert first_list.locator("li").count() >= 3
        browser.close()
