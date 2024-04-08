import subprocess
import pyautogui as pgui
import pytest
import time
import sys
import os
from pprint import pprint  # needed for debug


@pytest.fixture(scope="session", autouse=True)
def start_main_application():
    main_path = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'main.py')
    process = subprocess.Popen([sys.executable, main_path])
    time.sleep(2)
    yield
    time.sleep(2)
    process.terminate()
    process.wait()


@pytest.mark.dependency()
def test_application_start():
    index = 0
    for el in pgui.getAllTitles():
        if el == 'RelayControl':
            index += 1
    assert index == 1


@pytest.mark.dependency(depends=["test_application_start"])
def test_window_visible():
    app_window = pgui.getWindowsWithTitle('RelayControl')
    app_window[0].activate()
    local_path = os.path.dirname(os.path.realpath(__file__))
    img_path = os.path.join(local_path, 'test_resources', 'test_window_visible.png')
    img_location = pgui.locateOnScreen(img_path)
    assert img_location is not None
