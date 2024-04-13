import pytest, os
from gui import App
from argparse import ArgumentParser
from tests.clean_raport import clean_html_report


def run_cli():
    print("not implemented")

def run_web():
    print("not implemented")


if __name__ == '__main__':
    parser = ArgumentParser(prog='RelayControl', description='Open in CLI, GUI or WEB')
    parser.add_argument("--cli", help="Run the application in CLI mode", action="store_true")
    parser.add_argument("--web", help="Run the application in WEB mode", action="store_true")
    parser.add_argument("--testgui", help="Run the tests for the GUI version", action="store_true")
    parser.add_argument("--testall", help="Run all the tests available", action="store_true")
    args = parser.parse_args()

    if args.cli:
        run_cli()
    elif args.web:
        run_web()
    elif args.testgui:
        pytest.main(['-v', '-s', '-rxXs', '--log-file-level=INFO', '--log-cli-level=ERROR', 'tests/test_gui.py'])
        txt_file = os.path.join(os.getcwd(), 'tests', 'test_results', 'lastrun.txt')
        if os.path.exists(txt_file):
            with open(txt_file, 'r') as txt:
                report_dir = txt.read()
            html_file = os.path.join(report_dir, 'report.html')
            clean_html_report(html_file)
            os.remove(txt_file)
    elif args.testall:
        pytest.main(['-v', '-s', '--log-file-level=INFO', '--log-cli-level=ERROR', 'tests'])
    else:
        pass
        app = App()
        app.mainloop()
