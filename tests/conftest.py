import pytest
import logging
import os
from datetime import datetime


report_dir = None

def pytest_configure(config):
    global report_dir
    if not hasattr(config, 'workerinput'):
        current_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        report_dir = os.path.join(config.rootpath, 'tests', 'test_results', current_time)
        if not os.path.exists(report_dir):
            os.makedirs(report_dir)
        print(f"Session report directory set to: {report_dir}")

        report_path = os.path.join(report_dir, 'report.html')
        config.option.htmlpath = report_path
        print(f"HTML report will be saved to: {report_path}")
    config.addinivalue_line("markers", "skipif: conditionally skip certain tests")
    config.addinivalue_line("markers", "dependency: mark tests as dependent on other tests")


@pytest.fixture(scope="session", autouse=True)
def config_logging():
    global report_dir
    if report_dir is None:
        raise RuntimeError("Report directory not initialized")
    log_path = os.path.join(report_dir, "test_gui_error_logs.log")
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)
    logging.basicConfig(
        level=logging.ERROR,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[logging.FileHandler(log_path), logging.StreamHandler()]
    )


@pytest.fixture(scope="session")
def report_directory():
    global report_dir
    test_res_dir = os.path.join(os.getcwd(), 'tests', 'test_results')
    if not os.path.exists(test_res_dir):
        os.makedirs(test_res_dir)
    with open(os.path.join(test_res_dir,'lastrun.txt'), 'w') as txt:
        txt.write(report_dir)
    return report_dir


