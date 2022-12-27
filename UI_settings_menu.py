import customtkinter
import tkinter


class Settings_menu(customtkinter.CTkToplevel):
    def __init__(self,root, sqlite):
        super().__init__(root)
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root = root
        self.sqlite = sqlite
        self.geometry('800x500')
        self.resizable(False,False)
        self.title("Параметры")
        tabview = customtkinter.CTkTabview(master=self, corner_radius=10)
        tabview.pack()
        tabview.configure(width=780, height=490)
        crooms = tabview.add("ЗАЛЫ")  # add tab at the end
        schedule = tabview.add("РАСПИСАНИЕ")  # add tab at the end
        extra = tabview.add("ДОПОЛНИТЕЛЬНО")  # set currently visible tab
        add_croom_btn = customtkinter.CTkButton(crooms, text='Добавить зал', corner_radius=10, command=self.add_croom)
        add_croom_btn.pack(anchor='w', padx=10)

    def add_croom(self):
        add_room_menu = customtkinter.CTkToplevel(self.root)
        add_room_menu.geometry('500x170')
        add_room_menu.resizable(False, False)
        add_room_menu.title("Добавить зал")
        lb = customtkinter.CTkLabel(add_room_menu, text='Добавление нового зала', font=('roboto', 20))
        lb.pack(anchor='nw', padx = 10, pady = 10)
        frame_name = customtkinter.CTkFrame(add_room_menu, height=150, width=180)
        frame_name.pack(anchor='w', fill='y', padx=10, pady=10)
        frame_path = customtkinter.CTkFrame(add_room_menu, height=150, width=380)
        frame_path.pack(anchor='e', fill='y', padx=10, pady=10)
        # lb_name = customtkinter.CTkLabel(frame_name, text='Название', font=('roboto', 14))
        # lb_path = customtkinter.CTkLabel(frame_path, text='Путь', font=('roboto', 14))
        # lb_name.grid(column=0, row=0, sticky='nw')
        # lb_path.grid(column=1, row=0, sticky='ne')

    def on_closing(self):
        self.root.deiconify()
        self.destroy()

