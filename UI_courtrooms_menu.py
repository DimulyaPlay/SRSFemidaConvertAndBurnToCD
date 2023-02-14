
from Utils import *
import datetime


class Courtrooms_menu(customtkinter.CTkToplevel):
    def __init__(self,root, sqlite):
        super().__init__(root)
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root = root
        self.sqlite = sqlite
        self.geometry('760x600')
        self.resizable(False,False)
        self.title("Залы")
        self.courtrooms_dict = sqlite.get_courtrooms_dict()
        self.cr_list = list(self.courtrooms_dict.keys())
        self.periods_list = ['ЗА НЕДЕЛЮ', 'ЗА МЕСЯЦ', 'ЗА ГОД', 'ВСЕ']
        self.periods_list_to_query = {'ЗА НЕДЕЛЮ':"7day", 'ЗА МЕСЯЦ':"30day", 'ЗА ГОД':"365day", 'ВСЕ':None}
        self.cases_to_burn = []
        self.cached_tables = {}
        self.create_cr_combobox()

    def create_cr_combobox(self):

        def combobox_callback(choice):
            self.sbf.destroy()
            self.create_ch_table(combobox_cr.get(), combobox_period.get())

        combobox_cr = customtkinter.CTkOptionMenu(master=self,width=350,
                                             values=self.cr_list,
                                             command=combobox_callback,font=('roboto', 16))
        combobox_cr.grid(row=0, column=0, padx=10, pady=10, sticky='nw')
        if self.cr_list:
            combobox_cr.set(self.cr_list[0])
        else:
            combobox_cr.set('Залы не добавлены')
            return
        combobox_period = customtkinter.CTkOptionMenu(master=self,width=160,
                                             values=self.periods_list,
                                             command=combobox_callback,font=('roboto', 16))
        combobox_period.place(x=370,y=10)
        combobox_period.set(self.periods_list[0])
        customtkinter.CTkButton(master=self, text='НАЧАТЬ ЗАПИСЬ', corner_radius=10, command=self.write_to_disk, font=('roboto', 16)).place(x=600, y=10)
        self.ch_frame_hat = customtkinter.CTkFrame(master=self, width=760, corner_radius=10, bg_color='transparent',fg_color='transparent')
        self.ch_frame_hat.grid(padx=5, pady=0, sticky='nw')
        self.ch_frame_hat_name = customtkinter.CTkFrame(master=self.ch_frame_hat, bg_color='transparent',
                                                    width=250,
                                                    corner_radius=10)
        self.ch_frame_hat_name.grid(row=0, column=0, padx=5, pady=5, sticky='n')
        self.ch_frame_hat_date = customtkinter.CTkFrame(master=self.ch_frame_hat, bg_color='transparent',
                                                    width=90,
                                                    corner_radius=10)
        self.ch_frame_hat_date.grid(row=0, column=1,padx=5, pady=0, sticky='n')
        self.ch_frame_hat_duration = customtkinter.CTkFrame(master=self.ch_frame_hat, bg_color='transparent',
                                                    width=90,
                                                    corner_radius=10)
        self.ch_frame_hat_duration.grid(row=0, column=2, padx=5, pady=0, sticky='n')
        self.ch_frame_hat_to_burn = customtkinter.CTkFrame(master=self.ch_frame_hat, bg_color='transparent',
                                                    width=90,
                                                    corner_radius=10)
        self.ch_frame_hat_to_burn.grid(row=0, column=3, padx=5, pady=0, sticky='n')
        customtkinter.CTkLabel(self.ch_frame_hat_name, text='ДЕЛО №', font=('roboto', 16), width=200).grid(sticky='n', padx = 5)
        customtkinter.CTkLabel(self.ch_frame_hat_date, text='ДАТА', font=('roboto', 16), width=80).grid(sticky='n', padx = 5)
        customtkinter.CTkLabel(self.ch_frame_hat_duration, text='ДЛИТ', font=('roboto', 16), width=80).grid(sticky='n', padx = 5)
        self.count_to_burn_lb = customtkinter.CTkLabel(self.ch_frame_hat_to_burn, text = 'ВЫБРАНО ДЛЯ ЗАПИСИ: 0', font=('roboto', 16), width=80)
        self.count_to_burn_lb.grid(sticky='n', padx = 5)
        self.create_ch_table(self.cr_list[0], 'ЗА НЕДЕЛЮ')

    def create_ch_table(self, courtroom, period):

        def add_remove_to_list(btn, mp3path):
            if not mp3path == '':
                if mp3path in self.cases_to_burn:
                    self.cases_to_burn.remove(mp3path)
                    btn.configure(fg_color='#1F6AA5', hover_color='#14375e', text='ДОБАВИТЬ ДЛЯ ЗАПИСИ')
                    self.count_to_burn_lb.configure(text = f'ВЫБРАНО ДЛЯ ЗАПИСИ: {len(self.cases_to_burn)}')
                else:
                    self.cases_to_burn.append(mp3path)
                    btn.configure(fg_color='red', hover_color='darkred', text=' В СПИСКЕ ДЛЯ ЗАПИСИ ')
                    self.count_to_burn_lb.configure(text=f'ВЫБРАНО ДЛЯ ЗАПИСИ: {len(self.cases_to_burn)}')
        if courtroom in self.cached_tables.keys():
            ch_table = self.cached_tables[courtroom]
        else:
            ch_table = sqlite.get_courthearings_by_courtroom(courtroom)
            self.cached_tables[courtroom] = ch_table
        if period != 'ВСЕ':
            ch_table = ch_table[ch_table.date > datetime.datetime.now() - pd.to_timedelta(self.periods_list_to_query[period])]
        self.sbf = VerticalScrolledFrame(self)
        self.sbf.grid(row=2, column=0, sticky='nsew', padx=5)
        self.grid_rowconfigure(2, weight=1)
        self.grid_columnconfigure(0, weight=1)
        frame = self.sbf
        self.ch_frame_case = customtkinter.CTkFrame(master=frame,
                                       width=210,
                                       corner_radius=10, bg_color='gray14')
        self.ch_frame_case.grid(column=0, row=2, sticky='nw', padx = 5, pady = 5)
        self.ch_frame_date = customtkinter.CTkFrame(master=frame,
                                       width=90,
                                       corner_radius=10, bg_color='gray14')
        self.ch_frame_date.grid(column=1, row=2, sticky='n', padx = 5, pady = 5)
        self.ch_frame_duration = customtkinter.CTkFrame(master=frame,
                                       width=90,
                                       corner_radius=10, bg_color='gray14')
        self.ch_frame_duration.grid(column=2, row=2, sticky='n', padx = 5, pady = 5)
        self.ch_frame_buttons = customtkinter.CTkFrame(master=frame,
                                       width=310,
                                       corner_radius=10, bg_color='gray14')
        self.ch_frame_buttons.grid(column=3, row=2, sticky='n', padx = 5, pady = 5)
        for idx, row in ch_table.iterrows():

            customtkinter.CTkLabel(self.ch_frame_case, text=row['case'].replace('$2F', '/'), font=('roboto', 14), width=200).grid(padx = 5, pady = 5, column=0, row=idx, sticky = 'w')
            customtkinter.CTkLabel(self.ch_frame_date, text=row['date'].strftime('%d-%m-%Y'), font=('roboto', 14), width=80).grid(padx = 5, pady = 5, column=1, row=idx, sticky = 'n')
            if row["mp3duration"] != '':
                duration_text = f'{int(int(row["mp3duration"])/60)} мин'
                customtkinter.CTkLabel(self.ch_frame_duration, text=duration_text, font=('roboto', 14), width=80).grid(padx=5,
                                                                                                             pady=5,
                                                                                                             column=2,
                                                                                                             row=idx,
                                                                                                             sticky='n')
            btn_listen = customtkinter.CTkButton(self.ch_frame_buttons, text='ПРОСЛУШАТЬ',width=50, font=('roboto', 14),command=lambda e=row['mp3path']: open_mp3(e))
            btn_listen.grid(padx=5, pady=5, column=0, row=idx, sticky='w')
            btn_add_remove = customtkinter.CTkButton(self.ch_frame_buttons, text='ДОБАВИТЬ ДЛЯ ЗАПИСИ', font=('roboto', 14))
            btn_add_remove.configure(command=lambda b=btn_add_remove, e=row['mp3path']:add_remove_to_list(b,e))
            if row['mp3path'] in self.cases_to_burn:
                btn_add_remove.configure(fg_color='red', hover_color='darkred', text=' В СПИСКЕ ДЛЯ ЗАПИСИ ')
            btn_add_remove.grid(padx = 5, pady = 5, column=1, row=idx, sticky = 'e')

    def write_to_disk(self):
        print(self.cases_to_burn)
        if len(self.cases_to_burn) == 0:
            print('nothing to write')
            return
        #burn_mp3_files_to_disk(self.cases_to_burn)
        self.cases_to_burn = []
        self.count_to_burn_lb.configure(text=f'ВЫБРАНО ДЛЯ ЗАПИСИ: 0')
        self.create_ch_table(self.cr_list[0])
        return

    def on_closing(self):
        self.root.deiconify()
        self.destroy()
