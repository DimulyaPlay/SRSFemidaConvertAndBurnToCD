import customtkinter


class Settings_menu(customtkinter.CTkToplevel):
    def __init__(self,root, sqlite):
        super().__init__(root)
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root = root
        self.sqlite = sqlite
        self.geometry('800x500')
        self.resizable(False,False)
        self.title("Параметры")
        crrooms_table = self.sqlite.fetch_num_records('Courtrooms')

        tabview = customtkinter.CTkTabview(master=self, corner_radius=10)
        tabview.pack()
        tabview.configure(width=780, height=490)
        crrooms = tabview.add("ЗАЛЫ")  # add tab at the end
        schedule = tabview.add("РАСПИСАНИЕ")  # add tab at the end
        extra = tabview.add("ДОПОЛНИТЕЛЬНО")  # set currently visible tab


    def on_closing(self):
        self.root.deiconify()
        self.destroy()

