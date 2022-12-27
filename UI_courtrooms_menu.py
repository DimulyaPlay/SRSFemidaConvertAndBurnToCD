import customtkinter


class Courtrooms_menu(customtkinter.CTkToplevel):
    def __init__(self,root, sqlite):
        super().__init__(root)
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root = root
        self.sqlite = sqlite
        self.geometry('800x500')
        self.resizable(False,False)
        self.title("Залы")

    def on_closing(self):
        self.root.deiconify()
        self.destroy()

