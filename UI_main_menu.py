import customtkinter
from UI_settings_menu import Settings_menu


class App(customtkinter.CTk):
    def __init__(self, sqlite, admin_mode=False):
        super().__init__()
        self.title("SRS Femida. Экспорт аудиозаписей")
        self.geometry = f"{330}x{180}"
        self.resizable(False, False)
        self.button_courtrooms = customtkinter.CTkButton(master=self, command=self.open_cr_menu, width=320, height=90, text="ОТКРЫТЬ ЗАЛЫ", font=('roboto', 24))
        self.button_courtrooms.grid(row=0, column=0, padx=20, pady=10, sticky="s")
        self.button_search = customtkinter.CTkButton(master=self, command=self.open_search_menu, width=320, height=90, text="ИСКАТЬ ПО ДЕЛУ", font=('roboto', 24))
        self.button_search.grid(row=1, column=0, padx=20, pady=10, sticky="s")
        self.button_settings = customtkinter.CTkButton(master=self, command=self.open_settings, width=320, height=90, text="ПАРАМЕТРЫ", font=('roboto', 24), state='normal' if admin_mode else "disabled")
        self.button_settings.grid(row=2, column=0, padx=20, pady=10, sticky="s")
        self.sqlite = sqlite

    def open_cr_menu(self):

        return

    def open_search_menu(self):

        return

    def open_settings(self):
        self.withdraw()
        Settings_menu(self, self.sqlite)
        return
