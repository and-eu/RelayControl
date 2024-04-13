import inspect
import logging
import os
import shutil
import subprocess
import sys
import time

import pyautogui as pgui
import pytest
import serial

import tools

current_config = None

scenarios = [
    ('config_no_serial', "Start with config but no serial"),
    ('config', "Start with config"),
    ('no_config', "Start without config")
]


@pytest.fixture(scope="session", params=scenarios, ids=[config[1] for config in scenarios])
def start_application(request):
    global current_config
    config_name, _ = request.param
    current_config = config_name
    config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'config.json')
    test_config_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'test_resources', 'config.json')
    test_backup_config_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'test_resources',
                                           'backup_config.json')
    main_path = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'main.py')
    recover = False
    serials = []
    match config_name:
        case "config":
            if os.path.exists(config_path):
                shutil.copyfile(config_path, test_backup_config_path)
                os.remove(config_path)
                shutil.copyfile(test_config_path, config_path)
                recover = True
            else:
                shutil.copyfile(test_config_path, config_path)
        case "config_no_serial":
            ports = tools.get_ports()
            for port in ports:
                serials.append(serial.Serial(port=port, baudrate=9600, timeout=1))
            if os.path.exists(config_path):
                shutil.copyfile(config_path, test_backup_config_path)
                os.remove(config_path)
                shutil.copyfile(test_config_path, config_path)
                recover = True
            else:
                shutil.copyfile(test_config_path, config_path)
        case "no_config":
            if os.path.exists(config_path):
                shutil.copyfile(config_path, test_backup_config_path)
                os.remove(config_path)
                recover = True

    process = subprocess.Popen([sys.executable, main_path])
    time.sleep(4)
    yield
    time.sleep(2)
    process.terminate()
    process.wait()
    if recover:
        shutil.copyfile(test_backup_config_path, config_path)
        os.remove(test_backup_config_path)
    if len(serials) > 0:
        for ser in serials:
            ser.close()
        serials.clear()


@pytest.fixture
def app_window(start_application):
    windows = [window for window in pgui.getWindowsWithTitle('RelayControl') if window.title == 'RelayControl']
    return windows[0]


@pytest.mark.dependency(name='test_application_start')
def test_application_start(start_application):
    windows = [window for window in pgui.getWindowsWithTitle('RelayControl') if window.title == 'RelayControl']
    if len(windows) != 1:
        logging.error(f"Expected 1 'RelayControl' window, found {len(windows)}")
        logging.error(f"Name of the windows: {[window.title for window in windows]}")
        logging.info(f"All windows: {pgui.getAllTitles()}")
    assert len(windows) == 1, "RelayControl window not found"


@pytest.mark.dependency(depends=['test_application_start'], name='test_window_visible')
def test_window_visible(start_application, app_window, report_directory):
    app_window.activate()
    image_check('test_window_visible.png', report_directory)


@pytest.mark.skipif("current_config not in ['config', 'config_no_serial']", reason="Runs only with config file")
@pytest.mark.dependency(depends=["test_window_visible"], name='test_start_with_config')
def test_start_with_config(start_application, app_window, report_directory):
    if current_config == 'config':
        app_window.activate()
        image_check('start_with_config.png', report_directory)


@pytest.mark.skipif("current_config != 'config'", reason="Runs only with config file")
@pytest.mark.dependency(depends=["test_start_with_config"])
def test_start_with_config_serial_ok(start_application, app_window, report_directory):
    if current_config == 'config':
        app_window.activate()
        image_check('start_without_config_serial_ok.png', report_directory)


@pytest.mark.skipif("current_config != 'config_no_serial'",
                    reason="Runs only with config file and serial not available")
@pytest.mark.dependency(depends=["test_start_with_config"])
def test_start_with_config_serial_not_ok(start_application, app_window, report_directory):
    if current_config == 'config':
        app_window.activate()
        image_check('start_without_config_serial_not_ok.png', report_directory)


@pytest.mark.skipif("current_config != 'no_config'", reason="Runs only without config file")
@pytest.mark.dependency(depends=["test_window_visible"], name='test_start_without_config')
def test_start_without_config(start_application, app_window, report_directory):
    if current_config == 'no_config':
        app_window.activate()
        image_check('start_without_config.png', report_directory)


@pytest.mark.skipif("current_config != 'no_config'", reason="Runs only without config file")
@pytest.mark.dependency(depends=["test_start_without_config"])
def test_new_card(start_application, app_window, report_directory):
    if current_config == 'no_config':
        app_window.activate()
        button_location = locate_image('new_card_btn.png', report_directory)
        if button_location is not None:
            pgui.click(button_location, button='left')
        else:
            assert 0, "Button new card not found"
        time.sleep(0.5)
        image_check('new_card_img.png', report_directory, 0.6)


@pytest.mark.skipif("current_config != 'no_config'", reason="Runs only without config file")
@pytest.mark.dependency(depends=["test_start_without_config"], name='test_connect_btn_available')
def test_connect_btn_available(start_application, app_window, report_directory):
    if current_config == 'no_config':
        app_window.activate()
        button_location = locate_image('port_btn.png', report_directory)
        if button_location is not None:
            pgui.click(button_location, button='left')
            pgui.press('down', presses=2)
            pgui.press('enter')
        else:
            assert 0, "Button port not found"
        button_location = locate_image('baudrate_btn.png', report_directory)
        if button_location is not None:
            pgui.click(button_location, button='left')
            pgui.press('down', presses=6)
            pgui.press('enter')
        else:
            assert 0, "Button baudrate not found"
        image_check('connect_btn.png', report_directory)


@pytest.mark.skipif("current_config != 'no_config'", reason="Runs only without config file")
@pytest.mark.dependency(depends=["test_connect_btn_available"], name='test_connect')
def test_connect(start_application, app_window, report_directory):
    if current_config == 'no_config':
        app_window.activate()
        button_location = locate_image('connect_btn.png', report_directory)
        if button_location is not None:
            pgui.click(button_location, button='left')
            time.sleep(1)
        else:
            assert 0, "Button connect not found"
        image_check('start_without_config_serial_ok.png', report_directory)


@pytest.mark.skipif("current_config != 'no_config'", reason="Runs only without config file")
@pytest.mark.dependency(depends=["test_connect"], name='test_read_card')
def test_read_card(start_application, app_window, report_directory):
    if current_config == 'no_config':
        app_window.activate()
        button_location = locate_image('read_card_btn.png', report_directory)
        if button_location is not None:
            pgui.click(button_location, button='left')
            time.sleep(3)
        else:
            assert 0, "Button read card not found"
        image_check('all_btn_red.png', report_directory, 0.7)


@pytest.mark.skipif("current_config != 'no_config'", reason="Runs only without config file")
@pytest.mark.dependency(depends=["test_read_card"])
def test_press_button(start_application, app_window, report_directory):
    if current_config == 'no_config':
        app_window.activate()
        button_locations = locate_all_images('button_red.png', report_directory, 0.95)
        if button_locations is not None:
            pgui.click(button_locations[0], button='left')
            time.sleep(1)
        else:
            assert 0, "Button not found"
        green_btns = locate_all_images('button_green.png', report_directory, 0.95)
        assert len(green_btns) > 0
        # ser = tools.get_ports()[0]
        time.sleep(1)
        if len(green_btns) > 0:
            pgui.click(button_locations[0], button='left')
            time.sleep(1)


@pytest.mark.skipif("current_config != 'no_config'", reason="Runs only without config file")
@pytest.mark.dependency(depends=["test_connect"])
def test_save_config(start_application, app_window, report_directory):
    if current_config == 'no_config':
        app_window.activate()
        button_location = locate_image('save_config_btn.png', report_directory)
        if button_location is not None:
            pgui.click(button_location, button='left')
        else:
            assert 0, "Button save config not found"
        config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'config.json')
        assert os.path.exists(config_path)
        if os.path.exists(config_path):
            os.remove(config_path)


@pytest.mark.skipif("current_config != 'no_config'", reason="Runs only without config file")
@pytest.mark.dependency(depends=["test_connect"])
def test_delete_card(start_application, app_window, report_directory):
    if current_config == 'no_config':
        app_window.activate()
        button_location = locate_image('delete_card_btn.png', report_directory, 0.8)
        if button_location is not None:
            pgui.click(button_location, button='left')
            time.sleep(0.5)
        else:
            assert 0, "Button delete card not found"
        image_check('start_without_config.png', report_directory)


def image_check(img_file, report_directory, confi=0.95):
    caller_frame = inspect.stack()[1]
    caller_name = caller_frame.function
    local_path = os.path.dirname(os.path.realpath(__file__))
    img_path = os.path.join(local_path, 'test_resources', img_file)
    logging.info(f"Image search with path {img_path}")
    img_location = None
    try:
        img_location = pgui.locateOnScreen(img_path, confidence=confi, grayscale=False)
        if img_location is None:
            logging.error(f"Failed to locate window using image: {img_path}")
            screenshot_path = os.path.join(report_directory, caller_name + '.png')
            pgui.screenshot(screenshot_path)
            logging.error(f"Captured screenshot of current screen state to: {screenshot_path}")
    except Exception as e:
        logging.error(f"An error occurred during locateOnScreen: {e}")
    assert img_location is not None


def locate_image(img_file, report_directory, confi=0.95):
    caller_frame = inspect.stack()[1]
    caller_name = caller_frame.function
    local_path = os.path.dirname(os.path.realpath(__file__))
    img_path = os.path.join(local_path, 'test_resources', img_file)
    img_location = None
    try:
        img_location = pgui.locateOnScreen(img_path, confidence=confi, grayscale=False)
        if img_location is None:
            logging.error(f"Failed to locate window using image: {img_path}")
            screenshot_path = os.path.join(report_directory, caller_name + '.png')
            pgui.screenshot(screenshot_path)
            logging.error(f"Captured screenshot of current screen state to: {screenshot_path}")
    except Exception as e:
        logging.error(f"An error occurred during locateOnScreen: {e}")
    return img_location


def locate_all_images(img_file, report_directory, confi=0.95):
    caller_frame = inspect.stack()[1]
    caller_name = caller_frame.function
    local_path = os.path.dirname(os.path.realpath(__file__))
    img_path = os.path.join(local_path, 'test_resources', img_file)
    img_locations = None
    try:
        img_locations = list(pgui.locateAllOnScreen(img_path, confidence=confi, grayscale=False))
        if img_locations is None:
            logging.error(f"Failed to locate window using image: {img_path}")
            screenshot_path = os.path.join(report_directory, caller_name + '.png')
            pgui.screenshot(screenshot_path)
            logging.error(f"Captured screenshot of current screen state to: {screenshot_path}")
    except Exception as e:
        logging.error(f"An error occurred during locateAllOnScreen: {e}")
    return img_locations
