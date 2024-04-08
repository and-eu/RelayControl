import serial


class Card:
    num_cards = [0]

    def __init__(self, com_port=None, baudrate=0, **kwargs):
        if 'id' in kwargs:
            self._card_id = kwargs['id']
            Card.num_cards.append(kwargs['id'])
        else:
            index = 0
            while index in Card.num_cards:
                index += 1
            Card.num_cards.append(index)
            self._card_id = index
        self._ser = serial.Serial(timeout=1)
        self._buttons = [Button(i, f"Button {i}") for i in range(1, 9)]
        self._ser.port = com_port
        self._ser.baudrate = baudrate
        self._masks = {}

    def get_buttons(self):
        return self._buttons

    def get_button_name(self, button_index):
        if 0 <= button_index < 8:
            return self._buttons[button_index].name
        else:
            raise ValueError("Button number must be between 1 and 8.")

    def set_button_name(self, button_index, b_name):
        if 0 <= button_index < 8:
            self._buttons[button_index].name = b_name
        else:
            raise ValueError("Button number must be between 1 and 8.")

    def get_button_state(self, button_index):
        if 0 <= button_index < 8:
            return self._buttons[button_index].state
        else:
            raise ValueError("Button number must be between 1 and 8.")

    def set_button_state(self, button_index, state):
        if 0 <= button_index < 8:
            self._buttons[button_index].state(state)
        else:
            raise ValueError("Button number must be between 1 and 8.")

    @property
    def card_id(self):
        return self._card_id

    def port(self, port):
        self._ser.port = port

    def baudrate(self, baudrate):
        self._ser.baudrate = baudrate

    def save_mask(self, name):
        self._masks[name] = [button.state for button in self._buttons]

    def apply_mask(self, name):
        """
        Sets relays and buttons state according to saved state.
        don't forget to update buttons color after calling
        :param name: name of mask
        :return: -
        """
        if name in self._masks.values():
            if self.is_connected():
                for index, mask_states in enumerate(self._masks[name]):
                    relay_state = self.read_relay(index + 1)
                    if relay_state is True and mask_states[index] is True:
                        self._buttons[index].state(mask_states[index])
                    elif relay_state is True and mask_states[index] is not True:
                        self._ser.write(f'1,{index + 1},0\n'.encode('utf-8'))
                        self._buttons[index].state(mask_states[index])
                    elif relay_state is not True and mask_states[index] is True:
                        self._ser.write(f'1,{index + 1},1\n'.encode('utf-8'))
                        self._buttons[index].state(mask_states[index])
                    elif relay_state is not True and mask_states[index] is not True:
                        self._buttons[index].state(mask_states[index])
            else:
                print("Please connect to the board.")
        else:
            print('Mask name not available')

    def connect(self):
        if (self._ser.baudrate != 0) and (self._ser.port is not None):
            try:
                self._ser.open()
                return True
            except serial.serialutil.SerialException:
                print("Port is not accessible!")
                return False
        elif self._ser.baudrate == 0:
            print("Set the baudrate")
            return False
        elif self._ser.port is None:
            print("Set the port")
            return False

    def disconnect(self):
        if self._ser.is_open:
            self._ser.close()

    def is_connected(self):
        return self._ser.is_open

    def blink_led(self, time=15):
        if self._ser.is_open:
            if time > 0:
                self._ser.write(f'99,{time}\n'.encode('utf-8'))
            else:
                print("Time can't be 0.")
        else:
            print("Please connect to the board.")

    def read_relays(self):
        if self._ser.is_open:
            self._ser.write('2,00\n'.encode('utf-8'))
            states = [bool(int(element.decode('utf-8')[6:-2])) for element in self._ser.readlines()]
            for button in self._buttons:
                index = button.button_id - 1
                button.state = states[index]
            return True
        else:
            print("Please connect to the board.")
            return False

    def read_relay(self, relay_num):
        if self._ser.is_open:
            if 0 < relay_num < 9:
                self._ser.write(f'2,{relay_num}\n'.encode('utf-8'))
                return bool(int(self._ser.readline().decode('utf-8')[6:-2]))
            else:
                raise ValueError("Relay must be 1 to 8.")
        else:
            print("Please connect to the board.")

    def press_button(self, button_index):
        if self._ser.is_open:
            if 0 <= button_index < 8:
                self._buttons[button_index].press(self._ser)
            else:
                raise ValueError("Button number must be between 1 and 8.")
        else:
            print("Please connect to the board.")

    def rename_buttons(self, name_list):
        if len(name_list) == 8:
            for index, button in enumerate(self._buttons):
                button.state(name_list[index])

    def rename_button(self, button_nr, name):
        if 0 < button_nr < 9:
            self._buttons[button_nr].name(name)
        else:
            raise ValueError("Button number must be between 1 and 8.")


class Button:
    def __init__(self, button_id, name, state=None):
        self._button_id = button_id
        self._name = name
        self._state = state

    @property
    def button_id(self):
        return self._button_id

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name):
        self._name = name

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, state):
        if state in [True, False, None]:
            self._state = state
        else:
            raise ValueError("State cant be other than True, False or None.")

    def press(self, ser):
        if self._state is None:
            ser.write((f'1,{self._button_id},1\n'.encode('utf-8')))
            response = ser.readline()
            if response:
                self._state = bool(int(response.decode('utf-8')[6:-2]))
                return self._state
            else:
                print("No response from card")
        elif self._state is True:
            ser.write((f'1,{self._button_id},0\n'.encode('utf-8')))
            response = ser.readline()
            if response:
                self._state = bool(int(response.decode('utf-8')[6:-2]))
                return self._state
            else:
                print("No response from card")
        elif self._state is False:
            ser.write((f'1,{self._button_id},1\n'.encode('utf-8')))
            response = ser.readline()
            if response:
                self._state = bool(int(response.decode('utf-8')[6:-2]))
                return self._state
            else:
                print("No response from card")
        else:
            print("Button state aberrant")
