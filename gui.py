import tkinter
import tkinter.messagebox
import customtkinter
import threading
import os
from PIL import Image
from functools import partial

import tools
from card import Card


class CardFrame(customtkinter.CTkFrame):
    ports = tools.get_ports()
    baud_list = ['1200', '1800', '2400', '4800', '9600', '19200', '38400', '57600', '115200']

    def __init__(self, app, master, frame_id, card, **kwargs):
        super().__init__(master, **kwargs)
        self.app = app
        self._frame_id = frame_id
        self.card = card
        self.pad = App.padding
        self.disconnect_state_buttons = []

        image_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "images")
        self.bin_icon_image = customtkinter.CTkImage(Image.open(os.path.join(image_path, "bin.png")), size=(20, 20))

        self.grid_columnconfigure(0, weight=1)
        self.tframe = customtkinter.CTkFrame(self, height=40, corner_radius=0)
        self.tframe.grid(row=0, column=0, sticky="new")
        self.tframe.grid_columnconfigure(8, weight=1)

        self.label = customtkinter.CTkLabel(self.tframe, text=f"Card {self._frame_id}")
        self.label.grid(row=0, column=8)

        self.port_var = customtkinter.StringVar(value="Port")
        self.port_optmenu = customtkinter.CTkOptionMenu(self.tframe, values=['Port'] + CardFrame.ports, width=80,
                                                        command=self.set_card_port, variable=self.port_var)
        self.port_optmenu.grid(row=0, column=0, padx=(self.pad * 2, 0), pady=self.pad)

        self.baud_var = customtkinter.StringVar(value='Baudrate')
        self.baud_optmenu = customtkinter.CTkOptionMenu(self.tframe, values=['Baudrate'] + CardFrame.baud_list,
                                                        width=80,
                                                        command=self.set_card_baudrate, variable=self.baud_var)
        self.baud_optmenu.grid(row=0, column=1, padx=(self.pad, 0), pady=self.pad)

        self.connect_button = customtkinter.CTkButton(self.tframe, text="Connect", command=self.card_connect, width=80,
                                                      state="disabled")
        self.connect_button.grid(row=0, column=2, padx=(self.pad, 0), pady=self.pad)
        self.disconnect_button = customtkinter.CTkButton(self.tframe, text="Disconnect", command=self.card_disconnect,
                                                         width=80, state="disabled")
        self.disconnect_button.grid(row=0, column=3, padx=(self.pad, 0), pady=self.pad)
        self.disconnect_state_buttons.append(self.disconnect_button)

        self.read_card_button = customtkinter.CTkButton(self.tframe, text="Read Card", command=self.read_card,
                                                         width=80, state="disabled")
        self.read_card_button.grid(row=0, column=4, padx=(self.pad, 0), pady=self.pad)
        self.disconnect_state_buttons.append(self.read_card_button)

        self.blink_led_button = customtkinter.CTkButton(self.tframe, text="Blink LED", command=self.blink_led_event,
                                                         width=80, state="disabled")
        self.blink_led_button.grid(row=0, column=9, padx=self.pad, pady=self.pad)
        self.disconnect_state_buttons.append(self.blink_led_button)

        self.rename_button = customtkinter.CTkButton(self.tframe, text="Rename Relays", command=self.rename_dialog_event,
                                                     width=100)
        self.rename_button.grid(row=0, column=10, padx=self.pad, pady=self.pad)

        self.delete_button = customtkinter.CTkButton(self.tframe, text="", command=self.delete_card, width=28,
                                                     image=self.bin_icon_image, fg_color='dark red', hover_color='red')
        self.delete_button.grid(row=0, column=11, padx=self.pad * 2)

        self.bframe = customtkinter.CTkFrame(self, height=140, corner_radius=0)
        self.bframe.grid(row=1, column=0, sticky="nsew")
        self.bframe.grid_columnconfigure((0, 1, 2, 3, 4, 5, 6, 7), weight=1)

        self.relay_buttons = []
        for i in range(8):
            callback = partial(self.button_press, i)
            relay_button = customtkinter.CTkButton(self.bframe, text=self.card.get_button_name(i), width=120,
                                                        height=120, command=callback, state="disabled", fg_color='gray')
            relay_button.grid(row=0, column=i, pady=(10, 17))
            self.relay_buttons.append(relay_button)

    @property
    def frame_id(self):
        return self._frame_id

    def set_card_port(self, choice):
        if choice != "Port":
            self.card.port(choice)
            self.app.add_text(f'Card {self._frame_id}, port {choice} selected.')
            self.update_button_enable_states()

    def set_card_baudrate(self, choice):
        if choice != "Baudrate":
            self.card.baudrate(int(choice))
            self.app.add_text(f'Card {self._frame_id}, baudrate {choice} selected.')
            self.update_button_enable_states()

    def card_connect(self):
        if self.card.connect():
            self.connect_button.configure(fg_color="green", hover_color="green")
            self.update_button_enable_states()
            self.app.add_text(f'Card {self._frame_id} connected.')
        else:
            self.app.add_text(f"Card {self._frame_id} can't connect.")

    def card_disconnect(self):
        self.card.disconnect()
        if not self.card.is_connected():
            self.connect_button.configure(fg_color=('#3B8ED0', '#1F6AA5'), hover_color=('#36719F', '#144870'))
            self.update_button_enable_states()
            self.app.add_text(f'Card {self._frame_id} disconnected.')

    def read_card(self):
        if self.card.read_relays():
            self.app.add_text(f'Card {self._frame_id}, read relays ok.')
            self.update_relay_button_color()
        else:
            self.app.add_text(f"Card {self._frame_id}, can't read relays.")

    def blink_led_event(self):
        dialog = customtkinter.CTkInputDialog(text=f"How many sec to blink?\nHit no for 15sec.", title="Blink182")
        response = dialog.get_input()
        if response:
            self.card.blink_led(int(response))
            self.app.add_text(f'Card {self._frame_id}, LED blinking {response}sec.')
        else:
            self.card.blink_led()
            self.app.add_text(f'Card {self._frame_id}, LED blinking 15sec.')

    def rename_dialog_event(self):
        rename_count = 0
        for i in range(1, 9):
            dialog = customtkinter.CTkInputDialog(text=f"Enter relay {i} name.\nHit cancel to skip renaming this relay.\nThis will work only if card is connected.",
                                                  title="Rename relay")
            response = dialog.get_input()
            if response is not None:
                self.card.set_button_name(i-1, response)
                rename_count += 1
        if rename_count > 0:
            self.update_relay_button_names()
            self.app.add_text(f'Card {self._frame_id}, relay buttons renamed')

    def update_relay_button_names(self):
        for i, button in enumerate(self.relay_buttons):
            current_name = self.card.get_button_name(i)
            button.configure(text=current_name)
    def button_press(self, index):
        self.card.press_button(index)
        self.update_relay_button_color(index)
        self.app.message_time = 0.75
        self.app.add_text(f'Card {self._frame_id}, pressed {self.card.get_button_name(index)}')
        self.app.message_time = 5

    def update_button_enable_states(self):
        port_set = self.port_var.get() != "Port"
        baud_set = self.baud_var.get() != "Baudrate"
        is_connected = self.card.is_connected()

        if port_set and baud_set and not is_connected:
            self.connect_button.configure(state="normal")
        else:
            self.connect_button.configure(state="disabled")

        if is_connected:
            for button in self.disconnect_state_buttons:
                button.configure(state="normal")
            self.port_optmenu.configure(state="disabled")
            self.baud_optmenu.configure(state="disabled")
            for button in self.relay_buttons:
                button.configure(state="normal")

        else:
            for button in self.disconnect_state_buttons:
                button.configure(state="disabled")
            self.port_optmenu.configure(state="normal")
            self.baud_optmenu.configure(state="normal")
            for button in self.relay_buttons:
                button.configure(state="disabled", fg_color='gray')

    def update_relay_button_color(self, index=None):
        if index is None:
            for i, button in enumerate(self.relay_buttons):
                if self.card.get_button_state(i) is True:
                    button.configure(fg_color='green', hover_color='green')
                elif self.card.get_button_state(i) is False:
                    button.configure(fg_color='red', hover_color='red')
        else:
            if self.card.get_button_state(index) is True:
                self.relay_buttons[index].configure(fg_color='green', hover_color='green')
            elif self.card.get_button_state(index) is False:
                self.relay_buttons[index].configure(fg_color='red', hover_color='red')


    def delete_card(self):
        self.app.delete_card_frame(self._frame_id)



class App(customtkinter.CTk):
    padding = 7

    def __init__(self):
        super().__init__()

        WIDTH = 1200
        HEIGHT = 500

        customtkinter.set_appearance_mode("dark")  # Modes: "System" (standard), "Dark", "Light"
        customtkinter.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"

        self.title("RelayControl")
        self.geometry(f"{WIDTH}x{HEIGHT}")
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self.message_time = 5

        # MARKER top frame
        top_frame_h = 40
        self.top_frame = customtkinter.CTkFrame(self, height=top_frame_h, corner_radius=0)
        self.top_frame.grid(row=0, column=0, sticky="new")
        self.top_frame.grid_columnconfigure(0, weight=1)

        self.message_frame = customtkinter.CTkFrame(self.top_frame, height=top_frame_h - App.padding * 2)
        self.message_frame.grid(row=0, column=0, padx=(App.padding * 2, App.padding), pady=App.padding, sticky="ew")
        self.text_output = tkinter.Text(self.message_frame, height=1, wrap='word', state='disabled',
                                        bg='#333333', fg='white', padx=7)
        self.text_output.grid(row=0, column=0)
        self.message_timer = None

        self.new_card_btn = customtkinter.CTkButton(self.top_frame, text="+ New Card", command=self.add_new_card,
                                                    width=100)
        self.new_card_btn.grid(row=0, column=1, padx=App.padding)

        self.save_config_btn = customtkinter.CTkButton(self.top_frame, text="Save config", command=self.save_config,
                                                       width=100)
        self.save_config_btn.grid(row=0, column=2, padx=(App.padding, App.padding // 2), pady=App.padding)
        self.load_config_btn = customtkinter.CTkButton(self.top_frame, text="Load config", command=self.load_config,
                                                       width=100)
        self.load_config_btn.grid(row=0, column=3, padx=(App.padding // 2, App.padding), pady=App.padding)

        self.appearance_mode_optmenu = customtkinter.CTkOptionMenu(self.top_frame, values=["Light", "Dark", "System"],
                                                                   width=100, command=self.change_appearance_mode_event)
        self.appearance_mode_optmenu.grid(row=0, column=4, padx=(App.padding, App.padding // 2), pady=App.padding)
        self.scaling_optmenu = customtkinter.CTkOptionMenu(self.top_frame,
                                                           values=["80%", "90%", "100%", "110%", "120%"],
                                                           width=100, command=self.change_scaling_event)
        self.scaling_optmenu.grid(row=0, column=5, padx=(App.padding // 2, App.padding * 2), pady=App.padding)

        # MARKER next frame
        self.main_frame = customtkinter.CTkScrollableFrame(self, corner_radius=0, fg_color="transparent")
        self.main_frame.grid(row=1, column=0, sticky="nsew")
        self.main_frame.grid_columnconfigure(0, weight=1)

        self._card_frames = []

        # MARKER defaults
        self.appearance_mode_optmenu.set("Dark")
        self.scaling_optmenu.set("100%")

        # MARKER autoload config
        if tools.config_exist():
            self.load_config()
            self.add_text("Autoload config")
        else:
            self.add_text("Config file do not exist")

    def change_appearance_mode_event(self, new_appearance_mode: str):
        customtkinter.set_appearance_mode(new_appearance_mode)

    def change_scaling_event(self, new_scaling: str):
        new_scaling_float = int(new_scaling.replace("%", "")) / 100
        customtkinter.set_widget_scaling(new_scaling_float)

    def add_new_card(self):
        new_card = Card()
        card_id = new_card.card_id
        new_card_frame = CardFrame(self, self.main_frame, corner_radius=6, frame_id=card_id, card=new_card)
        new_card_frame.grid(row=card_id - 1, column=0, padx=App.padding, pady=App.padding, sticky="ew")
        self._card_frames.append(new_card_frame)
        self.add_text(f'Card {card_id} was created.')

    def delete_card_frame(self, frame_id):
        for i, card_frame in enumerate(self._card_frames):
            if card_frame.frame_id == frame_id:
                self.add_text(f'Card {frame_id} was deleted.')
                card_frame.destroy()
                del self._card_frames[i]
                Card.num_cards.remove(frame_id)
                break

    def save_config(self):
        #config = {'card1': {'id': 1, 'port': 'COM3', 'baudrate': '9600', 'buttons': []}, 'card2': {}}
        config = {}
        for card_frame in self._card_frames:
            config[f'card{card_frame.frame_id}'] = {'card_id': card_frame.frame_id, 'port': card_frame.port_var.get(),
                                                    'baudrate': card_frame.baud_var.get(),
                                                    'buttons': [bname.name for bname in card_frame.card.get_buttons()]}
        response = tools.save_config(config)
        self.add_text(response)


    def load_config(self):
        config = tools.load_config()
        cards = 0
        if isinstance(config, dict):
            for key, value in config.items():

                if int(key[-1]) == value['card_id']:
                    new_card = Card(id=value['card_id'])
                    new_card_frame = CardFrame(self, self.main_frame, corner_radius=6, frame_id=value['card_id'], card=new_card)
                    new_card_frame.grid(row=value['card_id'] - 1, column=0, padx=App.padding, pady=App.padding, sticky="ew")
                    new_card_frame.set_card_port(value['port'])
                    new_card_frame.set_card_baudrate(value['baudrate'])
                    for i, val in enumerate(value['buttons']):
                        new_card_frame.card.set_button_name(i, val)
                    new_card_frame.update_relay_button_names()
                    self._card_frames.append(new_card_frame)
                    cards += 1
                else:
                    self.add_text('Config json not correctly formated.')
            if len(self._card_frames)>0:
                for card_frame in self._card_frames:
                    card_frame.card_connect()
                    card_frame.read_card()
            if cards > 0:
                self.add_text('Config loaded.')
        else:
            self.add_text(config)

    def add_text(self, message):
        if self.message_timer:
            self.message_timer.cancel()

        self.text_output.configure(state='normal')
        self.text_output.delete(1.0, tkinter.END)
        self.text_output.insert(tkinter.END, message)
        self.text_output.configure(state='disabled')

        # Set a timer to clear the message after ## seconds
        self.message_timer = threading.Timer(self.message_time, self.clear_text)
        self.message_timer.start()

    def clear_text(self):
        self.text_output.configure(state='normal')
        self.text_output.delete(1.0, tkinter.END)
        self.text_output.configure(state='disabled')
