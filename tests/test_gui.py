import subprocess
import pyautogui as pgui
import logging
import pytest
import time
import sys
import os

from pprint import pprint  # needed for debug


@pytest.fixture(scope="session", autouse=True)
def config_logging():
    log_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'test_results',
                            time.strftime("%Y-%m-%d_%H-%M-%S"))
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    log_path = os.path.join(log_dir, "test_gui_logs.log")
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[logging.FileHandler(log_path), logging.StreamHandler()]
    )


@pytest.fixture(scope="session", autouse=True)
def start_main_application():
    main_path = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'main.py')
    process = subprocess.Popen([sys.executable, main_path])
    time.sleep(5)
    yield
    time.sleep(5)
    process.terminate()
    process.wait()


@pytest.mark.dependency()
def test_application_start():
    windows = [window for window in pgui.getWindowsWithTitle('RelayControl') if window.title == 'RelayControl']
    if len(windows) != 1:
        logging.error(f"Expected 1 'RelayControl' window, found {len(windows)}")
        logging.error(f"Name of the windows: {[window.title for window in windows]}")
        logging.info(f"All windows: {pgui.getAllTitles()}")
    assert len(windows) == 1, "RelayControl window not found"



@pytest.fixture
def app_window():
    windows = [window for window in pgui.getWindowsWithTitle('RelayControl') if window.title == 'RelayControl']
    return windows[0]


@pytest.mark.dependency(depends=["test_application_start"])
def test_window_visible(app_window):
    app_window.activate()
    local_path = os.path.dirname(os.path.realpath(__file__))
    img_path = os.path.join(local_path, 'test_resources', 'test_window_visible.png')
    logging.info(f"Image search with path {img_path}")
    img_location = None
    try:
        img_location = pgui.locateOnScreen(img_path)
        if img_location is None:
            logging.error(f"Failed to locate window using image: {img_path}")
            screenshot_path = os.path.join(local_path, 'test_resources', 'test_window_visible.png')
            pgui.screenshot(screenshot_path)
            logging.error(f"Captured screenshot of current screen state to: {screenshot_path}")
    except Exception as e:
        logging.error(f"An error occurred during locateOnScreen: {e}")
    assert img_location is not None
