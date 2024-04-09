import pytest
from gui import App
from argparse import ArgumentParser


def run_cli():
    print("not implemented")

def run_web():
    print("not implemented")


if __name__ == '__main__':
    parser = ArgumentParser(prog='RelayControl', description='Open in CLI, GUI or WEB')
    parser.add_argument("--cli", help="Run the application in CLI mode", action="store_true")
    parser.add_argument("--web", help="Run the application in WEB mode", action="store_true")
    parser.add_argument("--testgui", help="Run the tests for the GUI version", action="store_true")
    args = parser.parse_args()

    if args.cli:
        run_cli()
    elif args.web:
        run_web()
    elif args.testgui:
        pytest.main(['-v', '-s', '--log-file-level=INFO', '--log-cli-level=ERROR', 'tests'])
    else:
        pass
        app = App()
        app.mainloop()



    # card1 = Card('COM3', 9600)
    # card1.connect()
    # card1.press_button(1)
    # print(card1.get_button_state(1))

    # card1.readRelays()
    # for button in card1.getButtons():
    #     print(f"button button_id {button.getID()} with state {button.getState()}")


    # cards = [Card() for i in range(4)]
    # for card in cards:
    #     for button in card.getButtons():
    #         print(f"card ID {card.getID} with button ID: {button.getID()}, name: {button.getName()} and state: {button.getState()}")

    # ser = serial.Serial('COM3', 9600, timeout=1)
    # print(ser)
    # ser.port = 'COM11'
    # print(ser)
    # ser1 = serial.Serial(timeout=1)
    # print(ser1)
    # ser1.port = 'COM10'
    # print(ser1)

    # print(ser.name)
    # ser.write(b'1,7,1\n')
    # asd = ser.read(20).decode('utf-8')[:-2]
    # print(asd)
    # time.Sleep(1)
