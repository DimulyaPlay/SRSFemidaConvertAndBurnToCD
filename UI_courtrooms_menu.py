import customtkinter
from Utils import *


class Courtrooms_menu(customtkinter.CTkToplevel):
    def __init__(self,root, sqlite):
        super().__init__(root)
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root = root
        self.sqlite = sqlite
        self.geometry('800x600')
        self.resizable(False,False)
        self.title("Залы")
        cr_table = get_cr_table()
        self.cr_list = list(cr_table.courtroomname)
        self.create_cr_combobox()
        self.cases_to_burn = []

    def create_cr_combobox(self):

        def combobox_callback(choice):
            self.ch_frame_case.destroy()
            self.ch_frame_date.destroy()
            self.ch_frame_duration.destroy()
            self.create_ch_table(choice)

        combobox = customtkinter.CTkOptionMenu(master=self,width=580,
                                             values=self.cr_list,
                                             command=combobox_callback,font=('roboto', 16))
        combobox.grid(padx=10, pady=10, sticky='nw')
        combobox.set(self.cr_list[0])
        self.create_ch_table(self.cr_list[0])

    def create_ch_table(self, courtroom):

        def add_remove_to_list(mp3path):
            if not mp3path == '':
                if mp3path in self.cases_to_burn:
                    self.cases_to_burn.remove(mp3path)
                else:
                    self.cases_to_burn.append(mp3path)
            print(self.cases_to_burn)

        ch_table = get_ch_table_by_cr_name(courtroom)
        sbf = ScrollbarFrame(self)
        sbf.grid(row=1, column=0, sticky='nsew')
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)
        frame = sbf.scrolled_frame
        customtkinter.CTkLabel(frame, text='ДЕЛО №', font=('roboto', 16)).grid(column=0, row=0)
        customtkinter.CTkLabel(frame, text='ДАТА', font=('roboto', 16)).grid(column=1, row=0)
        customtkinter.CTkLabel(frame, text='ДЛИТ', font=('roboto', 16)).grid(column=2, row=0)
        self.ch_frame_case = customtkinter.CTkFrame(master=frame,
                                       width=250, height=500,
                                       corner_radius=10)
        self.ch_frame_case.grid(column=0, row=1, sticky='n', padx = 5, pady = 5)
        self.ch_frame_case.grid_propagate(0)
        self.ch_frame_date = customtkinter.CTkFrame(master=frame,
                                       width=90, height=500,
                                       corner_radius=10)
        self.ch_frame_date.grid(column=1, row=1, sticky='n', padx = 5, pady = 5)
        self.ch_frame_date.grid_propagate(0)
        self.ch_frame_duration = customtkinter.CTkFrame(master=frame,
                                       width=90, height=500,
                                       corner_radius=10)
        self.ch_frame_duration.grid(column=2, row=1, sticky='n', padx = 5, pady = 5)
        self.ch_frame_duration.grid_propagate(0)
        self.ch_frame_buttons = customtkinter.CTkFrame(master=frame,
                                       width=310, height=500,
                                       corner_radius=10)
        self.ch_frame_buttons.grid(column=3, row=1, sticky='n', padx = 5, pady = 5)
        self.ch_frame_buttons.grid_propagate(0)
        for idx, row in ch_table.iterrows():

            customtkinter.CTkLabel(self.ch_frame_case, text=row['case'].replace('$2F', '/'), font=('roboto', 14)).grid(padx = 5, pady = 5, column=0, row=idx, sticky = 'w')
            customtkinter.CTkLabel(self.ch_frame_date, text=row['date'], font=('roboto', 14)).grid(padx = 10, pady = 5, column=1, row=idx, sticky = 'n')
            if row["mp3duration"] != '':
                duration_text = f'{int(int(row["mp3duration"])/60)} мин'
                customtkinter.CTkLabel(self.ch_frame_duration, text=duration_text, font=('roboto', 14)).grid(padx=20,
                                                                                                             pady=5,
                                                                                                             column=2,
                                                                                                             row=idx,
                                                                                                             sticky='n')
                state = 'normal'

            else:
                customtkinter.CTkButton(self.ch_frame_duration, text='В MP3', font=('roboto', 14), width=50,
                                        command=lambda e=row['foldername'], a=row['courtroomname']: convert_to_mp3(e, a)).grid(padx=5, pady=5, column=2,
                                                                                           row=idx, sticky='n')
                state = 'disabled'
            customtkinter.CTkButton(self.ch_frame_buttons, text='ПРОСЛУШАТЬ',width=50, font=('roboto', 14), state=state,
                                    command=lambda e=row['mp3path']: open_mp3(e)).grid(padx=5, pady=5, column=0, row=idx, sticky='w')
            customtkinter.CTkButton(self.ch_frame_buttons, text='ДОБАВИТЬ ДЛЯ ЗАПИСИ', font=('roboto', 14), state = state, command=lambda e=row['mp3path']:add_remove_to_list(e)).grid(padx = 5, pady = 5, column=1, row=idx, sticky = 'e')

    def on_closing(self):
        self.root.deiconify()
        self.destroy()

