import customtkinter
import tkinter
import os
from Utils import *


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
        self.courtrooms_table = sqlite.get_courtrooms_dict()
        self.settings = sqlite.get_settings()
        tabview.configure(width=780, height=490)
        crooms = tabview.add("ЗАЛЫ")  # add tab at the end
        schedule = tabview.add("РАСПИСАНИЕ")  # add tab at the end
        extra = tabview.add("ДОПОЛНИТЕЛЬНО")  # set currently visible tab
        """
        Courtrooms settings START
        """
        add_croom_btn = customtkinter.CTkButton(crooms, text='Добавить зал', corner_radius=10, command=self.add_croom)
        add_croom_btn.place(x=10, y=10)
        gather_now_btn = customtkinter.CTkButton(crooms, text='Запустить сборщик записей', corner_radius=10, command=gather_all)
        gather_now_btn.place(x=160, y=10)
        if not self.courtrooms_table:
            customtkinter.CTkLabel(master = crooms,text='Залов пока нет, добавьте первый зал',font=('roboto', 20)).place(x=200, y=100)
        else:
            self.names = {}
            self.paths = {}
            self.dels = {}
            lbnamecol = customtkinter.CTkLabel(master = crooms, text='Название зала', font=('roboto', 14))
            lbnamecol.place(x=10, y=40)
            lbpathcol = customtkinter.CTkLabel(master = crooms, text='Путь к залу', font=('roboto', 14))
            lbpathcol.place(x=170, y=40)
            y = 70
            for name, path in self.courtrooms_table.items():
                lbname = customtkinter.CTkLabel(master=crooms, text=name, font=('roboto', 14))
                lbname.place(x=10, y=y)
                self.names[name] = lbname
                lbpath = customtkinter.CTkLabel(master=crooms, text=path, font=('roboto', 14))
                lbpath.place(x=170, y=y)
                self.paths[name] = lbpath
                xbtn = customtkinter.CTkButton(master=crooms, text='X',font=('roboto', 14), command=lambda a=name: self.del_room_from_base(a), width=25, height=15, fg_color ='red', hover_color='darkred')
                xbtn.place(x=720, y=y)
                self.dels[name] = xbtn
                y += 25
        """
        Courtrooms settings END
        
        Schedule settings START
        """
        customtkinter.CTkLabel(schedule, text="\nВ разработке\n\nСбор записей можно осуществлять в автоматическом режиме, \nсоздав задачу в планировщике windows на запуск программы с параметром '-gather'.", font=('roboto', 16)).pack()

        """
        Schedule settings END
        
        Extra settings START
        """
        self.convert_var = tkinter.IntVar()
        self.convert_var.set(self.settings['audio_convert'])
        self.mp3_path_var = tkinter.StringVar()
        self.mp3_path_var.set(self.settings['mp3_path'])
        convert_switch = customtkinter.CTkSwitch(master=extra, text='Конвертировать в MP3 при обновлении списков', font=('roboto', 14), variable=self.convert_var, command=self.save_settings_to_base, offvalue=0, onvalue=1)
        convert_switch.place(x=10,y=20)
        customtkinter.CTkLabel(master=extra, text='Путь сохранения сконвертированных файлов').place(x=10,y=60)
        self.mp3_entry = customtkinter.CTkEntry(master=extra, textvariable=self.mp3_path_var, width=470, height=30)
        self.mp3_entry.place(x=10,y=90)

    def add_croom(self):
        self.add_room_menu = customtkinter.CTkToplevel(self.root)
        self.add_room_menu.geometry('350x175')
        self.add_room_menu.resizable(False, False)
        self.add_room_menu.title("Добавить зал")
        lb = customtkinter.CTkLabel(self.add_room_menu, text='Добавление нового зала', font=('roboto', 20))
        lb.pack(anchor='n', padx = 10, pady = 10)
        frame_name = customtkinter.CTkFrame(self.add_room_menu, height=40, width=330)
        frame_name.place(x=10,y=45)
        add_btn = customtkinter.CTkButton(self.add_room_menu, text='Добавить зал', corner_radius=10, command=self.add_room_to_base)
        add_btn.pack(anchor='s', pady = 10,side='bottom')
        self.entry_name = customtkinter.CTkEntry(master=frame_name, placeholder_text="Название зала", width=320, height=30)
        self.entry_name.pack(padx=5, pady=5)
        self.entry_path = customtkinter.CTkEntry(master=frame_name, placeholder_text=r"\\Srsfemida\архив судебных заседаний\Зал №5", width=320, height=30)
        self.entry_path.pack(padx=5, pady=5)

    def add_room_to_base(self):
        name = fr'{self.entry_name.get()}'.strip()
        path = fr'{self.entry_path.get()}'
        if os.path.exists(path):
            if sqlite.add_courtroom(name, path):
                print(f'New courtroom {name, path} added')
            else:
                print(f'New courtroom {name, path} not added')
            self.add_room_menu.destroy()
            self.destroy()
            self.__init__(self.root, sqlite)
        else:
            print('Директория недоступна')

    def save_settings_to_base(self):
        self.settings['mp3_path'] = fr'{self.mp3_entry.get()}'
        self.settings['audio_convert'] = self.convert_var.get()
        sqlite.update_settings(self.settings)

    def del_room_from_base(self, name):
        sqlite.remove_courtroom(name)
        self.names[name].configure(state='disabled')
        self.paths[name].configure(state='disabled')
        self.dels[name].configure(state='disabled')

    def on_closing(self):
        self.save_settings_to_base()
        self.root.deiconify()
        self.destroy()

