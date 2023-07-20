import customtkinter as ctk
import tkinter as tk

from tkinter import messagebox, filedialog
from CTkToolTip import *
from CTkListbox import *
from PIL import Image

import webbrowser
import threading
import keyboard
import requests
import shutil
import random
import os

PROJECT_NAME = 'Stringify'
PROJECT_VERSION = __version__ = '1.0.1'


class Function:
    def __init__(self):
        pass

    @staticmethod
    def check_diff(text1: str, text2: str):
        if len(text1) != len(text2):
            return ''
        for x, y in zip(list(text1), list(text2)):
            if x != y:
                return x, y

    @staticmethod
    def surround(text: str, surrounder: str, sep: str = ''):
        return f'{surrounder}{sep}{text}{sep}{surrounder}'

    @staticmethod
    def rreplace(text: str, old: str, new: str, occurence: int = 1):
        return text[::-1].replace(old[::-1], new[::-1], occurence)[::-1]

    @staticmethod
    def iscapitalize(text: str):
        if text[0].isupper() and text[1:].islower():
            return True
        return False

    @staticmethod
    def check_plural(quantity: int, plural_text: str = 's'):
        return plural_text if quantity > 1 else ''


class Storage:
    def __init__(self):
        self.THEME = 'blue'
        self.APPEARANCE_MODE = 'system'
        self.UPDATE_req = False

        self.THEME_OBJECT = ctk.ThemeManager.theme

        self._start_prefix = self._stp = '.CONFIG\n.LOAD.CONFIGURATION'
        self._end_suffix = self._eds = '.CONFIG.END(\"CONFIGURATION\")\n<endl>'
        self._config_template = self._cfg = '''.CONFIG
.LOAD.CONFIGURATION

@theme {}
@mode {}

@placeholder {}
@corner_radius {}
@punctuations {}
@numbers {}

@undo {}
@max_undo {}

@topmost {}
@sticky {}

.CONFIG.END(\"CONFIGURATION\")
<endl>'''
        self.placeholder = 'Your text'
        self.corner_radius = 7
        self.punctuations = '`-=[]\\;\',./~_+{}|:\"<>?!@#$%^&*()'
        self.numbers = '0123456789'
        self.text_cases = ['Original', 'Sentence case', 'UPPER CASE', 'lower case', 'iNVERSE cASE']

        self.undo = False
        self.max_undo = 0

        self.topmost = False
        self.sticky_setting = True

        self.current_text = ''

    @staticmethod
    def check_update(widget: ctk.CTkLabel = None):
        try:
            test = requests.get('https://client-data.w3spaces.com').text.strip().split('\n')
        except requests.exceptions.ConnectionError:
            widget.configure(text='Failed to check version...') if widget is not None else None
            STORAGE.UPDATE_req = []
            return
        for i in test:
            uvar, uval = [k.strip() for k in i.strip().split(':')]
            if uvar == PROJECT_NAME.strip().lower():
                if not uval == PROJECT_VERSION.strip().lower():
                    STORAGE.UPDATE_req = uval

    class _Utilities:
        is_find: bool | ctk.CTkToplevel | ctk.CTk = False
        find_case_sensitive = True

    class _Windows:
        ROOT: ctk.CTk = False
        SETTING: ctk.CTkToplevel = False
        THEME_EDITOR: ctk.CTkToplevel = False
        PLUGIN_EDITOR: ctk.CTkToplevel = False


FUNCTION = Function()
STORAGE = Storage()

with open('data\\config.txt', 'r') as config_read:
    file_read = config_read.read()
    config_read.seek(0)
    lines_read = [i.strip().split(maxsplit=1) for i in config_read.readlines() if i not in ' \n' and i[0] not in '#.<']
    if file_read.startswith(STORAGE._stp) and file_read.endswith(STORAGE._eds):
        for line in lines_read:
            if len(line) < 2:
                messagebox.showerror('[Error] Error',
                                     f'Not enough arguments were passed. Expected 2, got {len(line)}.\n{line}')
                quit()
            var, val = line
            if var == '@theme':
                STORAGE.THEME = val
            elif var == '@mode':
                STORAGE.APPEARANCE_MODE = val
            elif var == '@placeholder':
                STORAGE.placeholder = val
            elif var == '@corner_radius':
                if val.isdigit():
                    STORAGE.corner_radius = int(val)
                else:
                    messagebox.showwarning('[Error] Warning',
                                           f'Corner radius must be an integer. Expected an int, got: {val}.')
            elif var == '@undo':
                if val.lower() == 'true':
                    STORAGE.undo = True
                elif val.lower() == 'false':
                    STORAGE.undo = False
                else:
                    messagebox.showwarning('[Error] Warning', f'Undo argument expected true or false, got: {val}')
            elif var == '@max_undo':
                if val.isdigit():
                    if int(val) > 0:
                        STORAGE.max_undo = int(val)
                else:
                    if val in ['-all', '-unlimited', '-unlimited', '-full']:
                        STORAGE.max_undo = 0
                    else:
                        messagebox.showwarning('[Error] Warning', f'Invalid max_undo number: {val}')
            elif var in ['@punctuations', '@punctuation']:
                STORAGE.punctuations = ''.join(list(set(val)))
            elif var in ['@numbers', '@punctuation']:
                STORAGE.numbers = ''.join(list(set(val)))
            elif var == '@topmost':
                if val.lower() == 'true':
                    STORAGE.topmost = True
                elif val.lower() == 'false':
                    STORAGE.topmost = False
                else:
                    messagebox.showwarning('[Error] Warning', f'Topmost argument expected true or false, got: {val}')
            elif var in ['@stick', '@sticky']:
                if val.lower() == 'true':
                    STORAGE.sticky_setting = True
                elif val.lower() == 'false':
                    STORAGE.sticky_setting = False
                else:
                    messagebox.showwarning('[Error] Warning', f'Sticky argument expected true or false, got: {val}')
            else:
                messagebox.showwarning('[Error] Warning',
                                       f'Unknown command: {"@" if not var.startswith("@") else ""}{var}')

    else:
        messagebox.showerror('Error', 'Unable to read config file.')
        quit()

ctk.set_appearance_mode(STORAGE.APPEARANCE_MODE)
ctk.set_default_color_theme(STORAGE.THEME)


class Load(ctk.CTkToplevel):
    def __init__(self, parent):
        ctk.CTkToplevel.__init__(self, parent)
        self.after(250, lambda: [self.lift(), self.iconbitmap('assets\\icon\\icon.ico')])

        self.title('Initialization')
        self.resizable(False, False)

        self.grid_columnconfigure(3, weight=1)

        self.mainProgressbar = ctk.CTkProgressBar(self, orientation='horizontal', mode='indeterminate', width=350)

        self.loadingText = ctk.CTkLabel(self, text='Checking for updates...')
        self.loadingText.grid(row=2, column=3, sticky='s', pady=(15, 5))
        self.loadingText.cget('font').configure(size=20, weight='bold')

        self.mainProgressbar.grid(row=3, column=3, sticky='ew', padx=15, pady=(0, 25))
        self.mainProgressbar.start()

        self.check_update_thread = threading.Thread(target=STORAGE.check_update, args=[self.loadingText])
        self.check_update_thread.start()
        self.check_update_finished()

        self.protocol('WM_DELETE_WINDOW', lambda: [self.destroy(), root.destroy()])

    def done(self):
        self.mainProgressbar.stop()
        self.mainProgressbar.configure(mode='determinate')
        self.mainProgressbar.set(1)
        self.after(random.randint(1000, 3000), self.end)

    def end(self):
        self.destroy()
        if STORAGE.UPDATE_req:
            if messagebox.askyesno('Update',
                                   f'A new update ({STORAGE.UPDATE_req}) is ready. Do you want update {PROJECT_NAME}?',
                                   icon='warning'):
                webbrowser.open('https://github.com/ItsHungg/Stringify/releases')
                return
        elif isinstance(STORAGE.UPDATE_req, list):
            messagebox.showwarning('[Error] Warning',
                                   'Unable to access server client. Please check your internet connection.')
            root.noSignalButton.grid(row=0, column=3, sticky='en', padx=5, pady=(5, 0))
        root.deiconify()

        for file in os.listdir('data\\plugins'):
            if file.endswith('.py'):
                __import__(f'data.plugins.{file[:-3]}')

    def check_update_finished(self):
        if self.check_update_thread.is_alive():
            self.after(1000, self.check_update_finished)
        else:
            self.loadingText.configure(text='Initializing...')
            self.after(random.randint(3000, 5000), self.done)


# noinspection PyTypeChecker
class Settings(ctk.CTkToplevel):
    def __init__(self, parent: ctk.CTk | ctk.CTkToplevel):
        ctk.CTkToplevel.__init__(self, parent)
        self.parent = parent
        self.after(250, lambda: [self.lift(), self.iconbitmap('assets\\icon\\icon.ico')])

        self.title(f'Settings')
        self.resizable(False, False)
        self.geometry(
            f'+{parent.winfo_width() + parent.winfo_x() + 10}+{parent.winfo_y()}') if STORAGE.sticky_setting else None

        # HEADER FRAME
        self.headerFrame = ctk.CTkFrame(self, corner_radius=0, fg_color='transparent')
        self.headerFrame.grid(row=3, column=3, sticky='nsew')

        self.headerFrame.grid_columnconfigure(3, weight=1)
        self.headerText = ctk.CTkLabel(self.headerFrame, text=f'Settings', font=('Calibri', 25, 'bold'))
        self.headerText.grid(row=3, column=3, sticky='nsew', pady=(15, 10))

        ctk.CTkFrame(self.headerFrame, fg_color=('black', 'gray'), corner_radius=25, height=2, width=0).grid(row=5,
                                                                                                             column=3,
                                                                                                             sticky='ew',
                                                                                                             padx=5)

        self.mainSettingFrame = ctk.CTkFrame(self, fg_color='transparent')
        self.mainSettingFrame.grid(row=7, column=3)

        # THEME FRAME
        self.themeFrame = ctk.CTkFrame(self.mainSettingFrame, fg_color='transparent', width=0, height=0)
        self.themeFrame.grid(row=5, column=3, sticky='nsew', padx=15, pady=5)

        ctk.CTkLabel(self.themeFrame, text='Themes', font=('Calibri', 20, 'bold')).grid(row=1, column=3, pady=(0, 5),
                                                                                        columnspan=2)

        self.themeFrame.grid_columnconfigure((3, 4), weight=1)
        ctk.CTkLabel(self.themeFrame, text='Edit your theme:').grid(row=3, column=3, padx=10)
        self.chooseThemeButton = ctk.CTkButton(self.themeFrame, text='Theme Editor', width=100, cursor='hand2',
                                               command=self.themeEditor)
        self.chooseThemeButton.grid(row=3, column=4, padx=(0, 10))

        # PLUGIN FRAME
        self.pluginFrame = ctk.CTkFrame(self.mainSettingFrame, fg_color='transparent', width=0, height=0)
        self.pluginFrame.grid(row=7, column=3, sticky='nsew', padx=15, pady=5)

        ctk.CTkLabel(self.pluginFrame, text='Plugin', font=('Calibri', 20, 'bold')).grid(row=1, column=3, pady=(0, 5),
                                                                                         columnspan=2)

        self.pluginFrame.grid_columnconfigure((3, 4), weight=1)
        ctk.CTkLabel(self.pluginFrame, text='Manage plugins:').grid(row=3, column=3, padx=10)
        self.choosePluginButton = ctk.CTkButton(self.pluginFrame, text='Plugin Editor', width=100, cursor='hand2',
                                                command=self.pluginEditor)
        self.choosePluginButton.grid(row=3, column=4, padx=(0, 10))

        # MODE FRAME
        self.modeFrame = ctk.CTkFrame(self.mainSettingFrame, fg_color='transparent', width=0, height=0)
        self.modeFrame.grid(row=9, column=3, sticky='nsew', padx=15, pady=(0, 15))

        ctk.CTkLabel(self.modeFrame, text='Mode', font=('Calibri', 20, 'bold')).grid(row=1, column=3, pady=(0, 5),
                                                                                     columnspan=2)

        self.modeFrame.grid_columnconfigure((3, 4), weight=1)
        ctk.CTkLabel(self.modeFrame, text='Choose your mode:').grid(row=3, column=3, padx=10)
        self.chooseModeMenu = ctk.CTkOptionMenu(self.modeFrame, values=['Light', 'Dark', 'System'], width=100,
                                                command=lambda _: Utilities.change_mode(
                                                    self.chooseModeMenu.get().lower(), True))
        self.chooseModeMenu.set(STORAGE.APPEARANCE_MODE.capitalize())
        self.chooseModeMenu.grid(row=3, column=4, padx=(0, 10))

        # MISC FRAME
        self.miscFrame = ctk.CTkFrame(self.mainSettingFrame, fg_color='transparent', width=0, height=0)
        self.miscFrame.grid(row=11, column=3, sticky='nsew', padx=15, pady=(0, 15))

        self.miscFrame.grid_columnconfigure(3, weight=1)
        ctk.CTkLabel(self.miscFrame, text='Miscellaneous', font=('Calibri', 20, 'bold')).grid(row=1, column=3,
                                                                                              pady=(0, 5))

        self.rootOnTopSwitch = ctk.CTkSwitch(self.miscFrame, text='Always on top',
                                             command=lambda: Utilities.change_topmost(STORAGE.topmost))
        self.rootOnTopSwitch.select() if STORAGE.topmost else None
        CTkToolTip(self.rootOnTopSwitch, message='Make the root window always on top.').attributes(
            '-topmost', True)
        self.rootOnTopSwitch.grid(row=3, column=3, sticky='w', padx=5)

        self.stickySettingSwitch = ctk.CTkSwitch(self.miscFrame, text='Sticky setting  [BETA]',
                                                 command=lambda: Utilities.change_sticky(STORAGE.sticky_setting))
        self.stickySettingSwitch.select() if STORAGE.sticky_setting else None
        CTkToolTip(self.stickySettingSwitch, message='Stick positions of windows. (BETA)').attributes(
            '-topmost', True)
        self.stickySettingSwitch.grid(row=5, column=3, sticky='w', padx=5)

        self.numbersFrame = ctk.CTkFrame(self.miscFrame, fg_color='transparent')
        self.numbersFrame.grid(row=11, column=3, sticky='ew', pady=(15, 1))

        self.numbersFrame.grid_columnconfigure((3, 4), weight=1)
        self.numbersText = ctk.CTkLabel(self.numbersFrame, text='Numbers:')
        self.numbersText.grid(row=3, column=3, sticky='e', padx=5)

        self.numbersEntry = ctk.CTkEntry(self.numbersFrame, height=25)
        self.numbersEntry.insert(0, ''.join(sorted(STORAGE.numbers)))
        self.numbersEntry.configure(validate='key', validatecommand=(self.register(Utilities.numbersBind), '%P'))
        self.numbersEntry.grid(row=3, column=4, sticky='e', padx=5)

        self.punctuationsFrame = ctk.CTkFrame(self.miscFrame, fg_color='transparent')
        self.punctuationsFrame.grid(row=13, column=3, sticky='ew', pady=1)

        self.punctuationsFrame.grid_columnconfigure((3, 4), weight=1)
        self.punctuationsText = ctk.CTkLabel(self.punctuationsFrame, text='Punctuations:')
        self.punctuationsText.grid(row=3, column=3, sticky='e', padx=5)

        self.punctuationsEntry = ctk.CTkEntry(self.punctuationsFrame, height=25)
        self.punctuationsEntry.insert(0, ''.join(sorted(STORAGE.punctuations)))
        self.punctuationsEntry.configure(validate='key',
                                         validatecommand=(self.register(Utilities.punctuationsBind), '%P'))
        self.punctuationsEntry.grid(row=3, column=4, sticky='e', padx=5)

        self.footerFrame = ctk.CTkFrame(self, fg_color='transparent')
        self.footerFrame.grid(row=9, column=3, sticky='ew')

        self.footerFrame.grid_columnconfigure((3, 4, 5, 6, 7), weight=1)
        ctk.CTkFrame(self.footerFrame, fg_color=('black', 'gray'), corner_radius=25, height=2, width=0).grid(row=1,
                                                                                                             column=3,
                                                                                                             columnspan=5,
                                                                                                             sticky='ew',
                                                                                                             padx=5)
        self.githubLabel = ctk.CTkLabel(self.footerFrame, text=f'GitHub', cursor='hand2')
        Utilities.hyperlinksBind(self.githubLabel, 'https://github.com/ItsHungg/Stringify')
        self.githubLabel.grid(row=3, column=3, sticky='e')

        ctk.CTkLabel(self.footerFrame, text='-').grid(row=3, column=4)

        self.websiteLabel = ctk.CTkLabel(self.footerFrame, text=f'Website', cursor='hand2')
        Utilities.hyperlinksBind(self.websiteLabel, 'https://sites.google.com/view/py-stringify')
        self.websiteLabel.grid(row=3, column=5, sticky='ew')

        ctk.CTkLabel(self.footerFrame, text='-').grid(row=3, column=6)

        self.changelogLabel = ctk.CTkLabel(self.footerFrame, text=f'Changelog', cursor='hand2')
        Utilities.hyperlinksBind(self.changelogLabel, 'https://github.com/ItsHungg/Stringify/releases')
        self.changelogLabel.grid(row=3, column=7, sticky='w')

        self.parent.bind('<Configure>',
                         lambda _: Utilities.move_window(self, self.parent)) if STORAGE.sticky_setting else None
        self.protocol('WM_DELETE_WINDOW', self.on_exit)

    def on_exit(self):
        self.parent.unbind('<Configure>')
        STORAGE._Windows.SETTING = False
        STORAGE._Windows.THEME_EDITOR = False
        STORAGE._Windows.PLUGIN_EDITOR = False
        Utilities.save_file()
        self.destroy()

    def themeEditor(self):
        if STORAGE._Windows.THEME_EDITOR:
            STORAGE._Windows.THEME_EDITOR.deiconify()
            STORAGE._Windows.THEME_EDITOR.lift()
            return

        themeEditWindow = STORAGE._Windows.THEME_EDITOR = ctk.CTkToplevel(self)
        themeEditWindow.title('Theme Editor 1.1')
        themeEditWindow.resizable(False, False)

        themeEditWindow.attributes('-topmost', STORAGE.topmost)
        if STORAGE._Windows.PLUGIN_EDITOR:
            themeEditWindow.geometry(
                f'+{STORAGE._Windows.PLUGIN_EDITOR.winfo_x() + 35}+{STORAGE._Windows.PLUGIN_EDITOR.winfo_y() + 35}') if STORAGE.sticky_setting else None
        else:
            themeEditWindow.geometry(
                f'+{self.parent.winfo_x() + 35}+{self.parent.winfo_y() + 35}') if STORAGE.sticky_setting else None

        self.after(250, lambda: [themeEditWindow.lift(), themeEditWindow.iconbitmap('assets\\icon\\icon.ico')])
        ctk.CTkLabel(themeEditWindow, text='Theme Editor', font=('Calibri', 25, 'bold')).grid(row=1, column=3,
                                                                                              columnspan=3, pady=15)

        # EDIT FRAME
        editFrame = ctk.CTkFrame(themeEditWindow)
        editFrame.grid(row=3, column=3, padx=(15, 7), pady=(5, 10), rowspan=5)

        ctk.CTkLabel(editFrame, text='Viewer:').grid(row=1, column=3, sticky='ew', pady=5)
        editValue = ctk.CTkTextbox(editFrame, height=250, wrap='word')
        editValue.insert('0.0', f'Welcome to Theme Editor!')
        editValue.grid(row=3, column=3, sticky='nsew', padx=15, pady=(0, 15))

        # PATH FRAME
        def validator(item):
            savePathButton.configure(state='normal', cursor='hand2')
            if item.strip() == '':
                savePathButton.configure(state='disabled', cursor='')
                return True
            elif item.count(':') > 1:
                return False
            elif any(k in item for k in '<>\"|?*'):
                return False
            return True

        def load_path():
            try:
                editValue.delete('0.0', 'end')
                if pathEntry.get().strip() != STORAGE.THEME:
                    saveThemeButton.configure(state='normal', cursor='hand2')
                else:
                    saveThemeButton.configure(state='disabled', cursor='')
                if pathEntry.get() in ['blue', 'dark-blue', 'green']:
                    editValue.insert('0.0', f'Default theme: {pathEntry.get()}')
                    return
                with open(pathEntry.get(), 'r') as json_data:
                    editValue.insert('0.0', json_data.read().strip())
            except (FileNotFoundError, UnicodeError) as error:
                editValue.insert('0.0', f'[Error] {error}')
                saveThemeButton.configure(state='disabled', cursor='')
                messagebox.showerror('Error', f'Couldn\'t read file.\n[Error] {error}', parent=themeEditWindow)

        def openfile():
            filename = filedialog.askopenfilename(title='Choose a theme', initialdir='\\',
                                                  filetypes=[('JSON files', '*.json')], parent=themeEditWindow)
            themeEditWindow.lift()
            if filename != '':
                pathEntry.delete(0, 'end')
                pathEntry.insert(0, filename)
                load_path()

        def saveTheme():
            # noinspection PyBroadException
            try:
                new_theme = pathEntry.get().strip()
                ctk.set_default_color_theme(new_theme)
                STORAGE.THEME = new_theme

                Utilities.save_file()
            except Exception as error:
                messagebox.showerror('Error', f'Something went wrong. Please try again.\n[Error] {str(error)}')
                return

            messagebox.showwarning('Warning', f'You need to restart {PROJECT_NAME} to see the changes.')

            for child in [editValue, pathEntry, savePathButton, openPathButton, cancelButton]:
                child.configure(state='disabled')
            cancelButton.configure(fg_color='gray70')
            saveThemeButton.configure(text='Saved Theme', state='disabled', cursor='')
            self.after(1000, self.on_exit)

        pathFrame = ctk.CTkFrame(themeEditWindow)
        pathFrame.grid(row=3, column=5, sticky='n', padx=(7, 15), pady=10)

        savePathButton = ctk.CTkButton(pathFrame, text='Load', width=75, height=25, cursor='hand2', command=load_path)
        savePathButton.configure(state='disabled')
        savePathButton.grid(row=5, column=3, pady=(0, 15), padx=7, sticky='e')

        openPathButton = ctk.CTkButton(pathFrame, text='Open', width=75, height=25, cursor='hand2', command=openfile)
        openPathButton.grid(row=5, column=4, pady=(0, 15), padx=7, sticky='w')

        ctk.CTkLabel(pathFrame, text='Path (.json):').grid(row=1, column=3, sticky='ew', pady=5, columnspan=2)
        pathEntry = ctk.CTkEntry(pathFrame, width=175, validate='key', validatecommand=(self.register(validator), '%P'))
        pathEntry.insert(0, STORAGE.THEME)
        pathEntry.grid(row=3, column=3, sticky='nsew', padx=15, pady=(0, 10), columnspan=2)

        saveFrame = ctk.CTkFrame(themeEditWindow)
        saveFrame.grid(row=7, column=5, sticky='sew', padx=(7, 15), pady=10)

        saveThemeButton = ctk.CTkButton(saveFrame, text='Save Theme', width=125, state='disabled', command=saveTheme)
        saveThemeButton.grid(row=3, column=3, padx=(15, 5), pady=15)

        cancelButton = ctk.CTkButton(saveFrame, text='',
                                     image=ctk.CTkImage(Image.open('assets\\textures\\trashbin.png')), width=40,
                                     fg_color='#f52f2f', hover_color='#d62929', cursor='hand2',
                                     command=lambda: [saveThemeButton.configure(state='disabled', cursor=''),
                                                      editValue.delete('0.0', 'end'),
                                                      savePathButton.configure(state='disabled', cursor=''),
                                                      pathEntry.delete(0, 'end'), pathEntry.focus()])
        cancelButton.grid(row=3, column=5, sticky='e', pady=15, padx=(5, 15))

        def exitEditor():
            themeEditWindow.destroy()
            STORAGE._Windows.THEME_EDITOR = False

        themeEditWindow.protocol('WM_DELETE_WINDOW', exitEditor)

    def pluginEditor(self):
        if STORAGE._Windows.PLUGIN_EDITOR:
            STORAGE._Windows.PLUGIN_EDITOR.deiconify()
            STORAGE._Windows.PLUGIN_EDITOR.lift()
            return
        PLUGIN_MANAGER: ctk.CTkToplevel | bool = False

        pluginEditWindow = STORAGE._Windows.PLUGIN_EDITOR = ctk.CTkToplevel(self)
        pluginEditWindow.title('Plugin Editor 1.0')
        pluginEditWindow.resizable(False, False)

        pluginEditWindow.attributes('-topmost', STORAGE.topmost)
        if STORAGE._Windows.THEME_EDITOR:
            pluginEditWindow.geometry(
                f'+{STORAGE._Windows.THEME_EDITOR.winfo_x() + 35}+{STORAGE._Windows.THEME_EDITOR.winfo_y() + 35}') if STORAGE.sticky_setting else None
        else:
            pluginEditWindow.geometry(
                f'+{self.parent.winfo_x() + 35}+{self.parent.winfo_y() + 35}') if STORAGE.sticky_setting else None

        self.after(250, lambda: [pluginEditWindow.lift(), pluginEditWindow.iconbitmap('assets\\icon\\icon.ico')])
        ctk.CTkLabel(pluginEditWindow, text='Plugin Editor', font=('Calibri', 25, 'bold')).grid(row=1, column=3,
                                                                                                columnspan=3, pady=15)
        pluginEditWindow.grid_columnconfigure(3, weight=1)

        def loadfile(filename: str, parent, show_warning: bool = False):
            try:
                with open(filename, 'r') as plugin_data:
                    editValue.configure(state='normal')
                    editValue.delete('0.0', 'end')
                    editValue.insert('0.0', plugin_data.read().strip())
                    editValue.configure(state='disabled')
            except UnicodeError as error:
                editValue.configure(state='normal')
                editValue.delete('0.0', 'end')
                editValue.insert('0.0', f'[Error] {error}')
                editValue.configure(state='disabled')
                if show_warning:
                    messagebox.showwarning('[Error] Warning', f'Couldn\'t read file.\n[Error] {error}', parent=parent)
                return False
            return True

        def bind_pathEntry(_):
            if os.path.isfile(pathEntry.get()):
                if loadfile(pathEntry.get(), pluginEditWindow):
                    pathEntry.bind('<Double-Button-1>', lambda _: Utilities.open(pathEntry.get(), True))
                    pathEntry.bind('<Double-Button-2>', lambda _: Utilities.open(pathEntry.get()))
                    addPluginButton.configure(state='normal', fg_color=STORAGE.THEME_OBJECT['CTkButton']['fg_color'])
            else:
                addPluginButton.configure(state='disabled', fg_color='gray75')
                pathEntry.unbind('<Double-Button-1>')
                pathEntry.unbind('<Double-Button-2>')

        def openfile():
            filename = filedialog.askopenfilename(title='Choose a theme', initialdir='\\',
                                                  filetypes=[('Python files', '*.py')], parent=pluginEditWindow)
            pluginEditWindow.lift()
            if filename != '':
                pathEntry.delete(0, 'end')
                pathEntry.insert(0, filename)
                addPluginButton.configure(state='normal', fg_color=STORAGE.THEME_OBJECT['CTkButton']['fg_color'])

                loadfile(filename, pluginEditWindow, True)

        def addPlugin():
            if pathEntry.get().endswith('.py'):
                try:
                    if not messagebox.askyesno('Warning',
                                               f'Are you sure to add this plugin?\nPath: {os.path.realpath(pathEntry.get())}',
                                               parent=pluginEditWindow):
                        return
                    with open(f'{pathEntry.get()}', 'r') as check_while:
                        read_plugin_lines = [i for i in check_while.readlines() if not i.lstrip().startswith('#')]
                        for line_in_plugin in read_plugin_lines:
                            if 'while' in line_in_plugin:
                                if not messagebox.askyesno('Warning',
                                                           'We detected a potential while loop that can freeze this program. Would you still like to add plugin file?',
                                                           icon='warning', parent=pluginEditWindow):
                                    return
                    if os.path.basename(pathEntry.get()) in [os.path.basename(file) for file in
                                                             os.listdir('data\\plugins')]:
                        if messagebox.askyesno('Warning',
                                               f'A file named "{os.path.basename(pathEntry.get())}" has already existed.\nDo you want to overwrite it?',
                                               icon='warning', default='no', parent=pluginEditWindow):
                            shutil.copy(pathEntry.get(), 'data\\plugins')
                        else:
                            return
                    else:
                        shutil.copy(pathEntry.get(), 'data\\plugins')
                except shutil.SameFileError as error:
                    messagebox.showwarning('[Error] Warning', f'An error has been raised.\n[Error] {error}',
                                           parent=pluginEditWindow)
                    return
                addPluginButton.configure(state='disabled', fg_color='gray75')

        def manage_plugins():
            nonlocal PLUGIN_MANAGER
            if PLUGIN_MANAGER:
                PLUGIN_MANAGER.lift()
                return

            PLUGIN_MANAGER = managePluginWindow = ctk.CTkToplevel(pluginEditWindow)
            managePluginWindow.title('Plugin Manager 1.0')
            managePluginWindow.resizable(False, False)

            managePluginWindow.attributes('-topmost', STORAGE.topmost)
            managePluginWindow.geometry(
                f'+{pluginEditWindow.winfo_x() + 35}+{pluginEditWindow.winfo_y() + 35}') if STORAGE.sticky_setting else None

            self.after(250,
                       lambda: [managePluginWindow.lift(), managePluginWindow.iconbitmap('assets\\icon\\icon.ico')])

            # MANAGE HEADER FRAME
            manageHeaderFrame = ctk.CTkFrame(managePluginWindow, fg_color='transparent')
            manageHeaderFrame.grid(row=3, column=3)

            ctk.CTkLabel(manageHeaderFrame, text='Plugin Manager', font=('Calibri', 25, 'bold')).grid(row=1, column=3,
                                                                                                      columnspan=3,
                                                                                                      pady=15)

            # PLUGIN LIST FRAME
            pluginListFrame = ctk.CTkFrame(managePluginWindow, fg_color='transparent')
            pluginListFrame.grid(row=5, column=3)

            ctk.CTkLabel(pluginListFrame, text='Plugins:').grid(row=1, column=3, pady=5)
            managePluginListbox = CTkListbox(pluginListFrame, text_color=('black', 'white'))
            managePluginListbox.grid(row=3, column=3)
            if '__init__.py' not in os.listdir('data\\plugins'):
                if messagebox.askyesno('Warning',
                                       'Couldn\'t find the __init__.py configuration file.\nDo you want to automatically create one?',
                                       parent=managePluginWindow):
                    open('data\\plugins\\__init__.py', 'w').close()

            for file in os.listdir('data\\plugins'):
                if file == '__init__.py':
                    managePluginListbox.insert(0, file)
                    continue
                if file.endswith('.py'):
                    managePluginListbox.insert('end', file)

            for button in managePluginListbox.buttons.values():
                if button.cget('text') == '__init__.py':
                    button.configure(state='disabled')
                    continue
                button.bind('<Double-Button-1>', lambda _: Utilities.open('data\\plugins'))

            def exit_manager():
                nonlocal PLUGIN_MANAGER

                PLUGIN_MANAGER = False
                managePluginWindow.destroy()

            managePluginWindow.protocol('WM_DELETE_WINDOW', exit_manager)

        # PATH FRAME
        pathFrame = ctk.CTkFrame(pluginEditWindow)
        pathFrame.grid(row=3, column=3, sticky='ew', padx=15, pady=10)
        pathFrame.grid_columnconfigure((3, 4, 5), weight=1)

        openPluginFolder = ctk.CTkButton(pathFrame, text='Plugin Folder', width=0, height=25, cursor='hand2',
                                         command=lambda: Utilities.open('data\\plugins'))
        openPluginFolder.grid(row=5, column=3, pady=(0, 15), padx=(15, 2), sticky='ew', ipadx=7)

        openPathButton = ctk.CTkButton(pathFrame, text='Open', width=0, height=25, cursor='hand2', command=openfile)
        openPathButton.grid(row=5, column=4, pady=(0, 15), padx=2, sticky='ew')

        addPluginButton = ctk.CTkButton(pathFrame, text='Add', width=0, height=25, cursor='hand2', state='disabled',
                                        fg_color='gray75', text_color_disabled='gray60',
                                        command=addPlugin)
        addPluginButton.grid(row=5, column=5, pady=(0, 15), padx=(2, 15), sticky='ew')

        ctk.CTkLabel(pathFrame, text='Path (.py):').grid(row=1, column=3, sticky='ew', pady=5, columnspan=3)
        pathEntry = ctk.CTkEntry(pathFrame, width=0,
                                 validate='key')  # , validatecommand=(self.register(validator), '%P'))
        pathEntry.grid(row=3, column=3, sticky='nsew', padx=15, pady=(0, 10), columnspan=3)

        # EDIT FRAME
        editFrame = ctk.CTkFrame(pluginEditWindow)
        editFrame.grid(row=5, column=3, padx=15, pady=10, rowspan=5, sticky='ew')
        editFrame.grid_columnconfigure(3, weight=1)

        ctk.CTkLabel(editFrame, text='Code preview:').grid(row=1, column=3, sticky='ew', pady=5)
        editValue = ctk.CTkTextbox(editFrame, height=150, wrap='word')
        editValue.insert('0.0', f'Welcome to Plugin Editor!')
        editValue.configure(state='disabled')
        editValue.grid(row=3, column=3, sticky='nsew', padx=15, pady=(0, 15))

        # BOTTOM
        managePluginButton = ctk.CTkButton(pluginEditWindow, text='Manage plugins', cursor='hand2',
                                           command=manage_plugins)
        managePluginButton.grid(row=11, column=3, sticky='ew', padx=15, pady=(5, 15))

        def exitEditor():
            pluginEditWindow.destroy()
            STORAGE._Windows.PLUGIN_EDITOR = False

        pathEntry.bind('<KeyRelease>', bind_pathEntry)
        pluginEditWindow.protocol('WM_DELETE_WINDOW', exitEditor)

    @staticmethod
    def run():
        if STORAGE._Windows.SETTING:
            if STORAGE._Windows.SETTING.state() == 'iconic':
                STORAGE._Windows.SETTING.wm_state('normal')
                return
            STORAGE._Windows.ROOT.unbind('<Configure>')
            STORAGE._Windows.SETTING.destroy()
            STORAGE._Windows.SETTING = False
            STORAGE._Windows.THEME_EDITOR = False
            return
        STORAGE._Windows.SETTING = Settings(STORAGE._Windows.ROOT)
        STORAGE._Windows.SETTING.attributes('-topmost', STORAGE.topmost)


# noinspection PyTypeChecker
class Application(ctk.CTk):
    def __init__(self):
        super().__init__()

        # DEFINE VARIABLES
        self.MISC = Utilities(self)

        # DEFINE WINDOW PROPERTIES
        self.title(f'{PROJECT_NAME} {PROJECT_VERSION}')
        self.iconbitmap('assets\\icon\\icon.ico')
        self.resizable(False, False)
        self.geometry('+25+25')

        self.grid_rowconfigure(0, weight=1)
        self.settingButton = ctk.CTkButton(self, text='',
                                           image=ctk.CTkImage(Image.open('assets\\textures\\setting_light.png'),
                                                              Image.open('assets\\textures\\setting_dark.png')),
                                           width=0, fg_color='transparent', hover=False, cursor='hand2',
                                           command=Settings.run)
        self.settingButton.grid(row=0, column=3, sticky='wn', padx=5, pady=(5, 0))
        self.noSignalButton = ctk.CTkButton(self, text='',
                                            image=ctk.CTkImage(Image.open('assets\\textures\\no_signal.png')),
                                            width=0, fg_color='transparent', hover=False)
        # HEADER FRAME
        self.headerFrame = ctk.CTkFrame(self, fg_color='transparent')
        self.headerFrame.grid(row=3, column=3, pady=(0, 15))

        ctk.CTkLabel(self.headerFrame, text=PROJECT_NAME, fg_color='transparent', font=('Helvetica', 45, 'bold')).grid(
            row=3, column=3)

        # MAIN FRAME
        self.mainFrame = ctk.CTkFrame(self, corner_radius=STORAGE.corner_radius)
        self.mainFrame.grid(row=5, column=3, padx=25, pady=(15, 0))

        self.mainTextbox = ctk.CTkTextbox(self.mainFrame, width=500, height=250, corner_radius=STORAGE.corner_radius,
                                          wrap='word', undo=STORAGE.undo, maxundo=STORAGE.max_undo,
                                          text_color='gray50')
        self.mainTextbox.grid(row=3, column=3, padx=15, pady=15, sticky='ew')
        self.mainTextbox.insert('0.0', STORAGE.placeholder)
        self.MISC._textbox_placeholder(STORAGE.placeholder, color='gray50')
        self.MISC._textbox_quitcheck()

        # ACTION FRAME
        self.actionFrame = ctk.CTkFrame(self, corner_radius=STORAGE.corner_radius, fg_color='transparent')
        self.actionFrame.grid(row=7, column=3, sticky='new', padx=25, pady=(3, 5))

        self.actionFrame.grid_columnconfigure(3, weight=1)
        self.actionButton = ctk.CTkSegmentedButton(self.actionFrame, values=STORAGE.text_cases,
                                                   unselected_color=('gray65', 'gray29'),
                                                   fg_color=self.cget('fg_color'), command=self.MISC._bind_action,
                                                   state='disabled')
        self.actionButton.grid(row=3, column=3, sticky='ew')
        self.actionButton.set('Original')

        # RESULT FRAME
        self.resultFrame = ctk.CTkFrame(self, corner_radius=STORAGE.corner_radius)
        self.resultFrame.grid(row=9, column=3, sticky='ew', padx=25, pady=25)

        self.subresultFrame = ctk.CTkFrame(self.resultFrame, fg_color='transparent')
        self.subresultFrame.grid(row=3, column=3, sticky='ew')

        self.subresultFrame.grid_columnconfigure((3, 4, 5), weight=1)
        self.firstResultFrame = ctk.CTkFrame(self.subresultFrame, fg_color='transparent')
        self.firstResultFrame.grid(row=3, column=3, sticky='w')

        self.secondResultFrame = ctk.CTkFrame(self.subresultFrame, fg_color='transparent')
        self.secondResultFrame.grid(row=3, column=5, sticky='e')

        self.resultFrame.grid_columnconfigure(3, weight=1)
        ctk.CTkLabel(self.resultFrame, text='Statistics', font=('Calibri', 25, 'bold')).grid(row=1, column=3,
                                                                                             sticky='ew',
                                                                                             pady=(15, 0))

        self.wordsStats = ctk.CTkLabel(self.firstResultFrame, text=f'Words: 0', justify='left', anchor='s')
        self.wordsStats.grid(row=5, column=3, sticky='sw', padx=20, pady=2)
        self.wordsStatsTooltips = CTkToolTip(self.wordsStats, delay=0.5, message=f'''Words: 0
UPPERCASE | lowercase | Capitalize: 0 | 0 | 0 (0% | 0% | 0%)''', justify='left')

        self.charactersStats = ctk.CTkLabel(self.firstResultFrame, text=f'Characters: 0', justify='left', anchor='n')
        self.charactersStats.grid(row=6, column=3, sticky='nw', padx=20, pady=2)
        self.charactersStatsTooltip = CTkToolTip(self.charactersStats, delay=0.5, message=f'''Characters without blank spaces: 0 (0.0%)
Characters without line breaks: 0 (0.0%)
Characters without spaces/line-breaks: 0 (0.0%)''', justify='left')

        self.numbersStats = ctk.CTkLabel(self.secondResultFrame, text=f'Numbers: 0', justify='right', anchor='s')
        self.numbersStats.grid(row=5, column=5, sticky='se', padx=20, pady=2)
        self.numbersStatsTooltips = CTkToolTip(self.numbersStats, delay=0.5, message=f'Numbers: 0 (0.0%)')

        self.punctuationsStats = ctk.CTkLabel(self.secondResultFrame, text=f'Punctuations: 0', justify='right',
                                              anchor='n')
        self.punctuationsStats.grid(row=6, column=5, sticky='se', padx=20, pady=2)
        self.punctuationsStatsTooltips = CTkToolTip(self.punctuationsStats, delay=0.5,
                                                    message=f'Punctuations: 0 (0.0%)')

        self.MISC._bind_result()


class Utilities:
    def __init__(self, parent: Application | ctk.CTk | ctk.CTkToplevel):
        super().__init__()

        self.object = parent

    def _textbox_placeholder(self, text: str, widget: ctk.CTkTextbox = None, color: tuple | str = 'gray50'):
        if widget is None:
            widget = self.object.mainTextbox

        def __focusin(_):
            # DISAPPEAR
            if self.object.focus_displayof() != self.object:
                return
            if widget.cget('text_color') == color:
                widget.focus()
                widget.configure(autoseparators=False)
                widget.delete('0.0', 'end')

        def __focusout(_):
            # APPEAR
            if widget.get('0.0', 'end-1c') == '' and not keyboard.is_pressed('shift'):
                self.object.actionButton.set('Original')
                self.object.focus()
                widget.insert('0.0', text)
                widget.configure(text_color=color)

        def __textfocus(_):
            if widget.cget('text_color') == color:
                widget.delete('0.0', 'end')
            Utilities.set_widget_color(widget)

        widget.bind('<Enter>', __focusin)
        widget.bind('<Leave>', __focusout)
        widget._textbox.bind('<FocusIn>', __textfocus)

    def _textbox_quitcheck(self, key: str = 'esc', widget: ctk.CTkTextbox = None):
        if widget is None:
            widget = self.object.mainTextbox

        def __bind_return(_):
            if keyboard.is_pressed(key):
                self.object.focus()

        widget.bind('<KeyPress>', __bind_return)

    def _bind_result(self, widget: ctk.CTkTextbox = None):
        if widget is None:
            widget = self.object.mainTextbox

        __one_million = False

        def __result_bind(_):
            nonlocal __one_million
            if self.object.actionButton.get() != 'Original':
                self.object.actionButton.set('Original')

            ___item: str = widget.get('0.0', 'end-1c')
            if len(___item) and self.object.actionButton._state == 'disabled':
                self.object.actionButton.configure(state='normal')
            if not len(___item) and self.object.actionButton._state == 'normal':
                self.object.actionButton.configure(state='disabled')
            STORAGE.current_text = ___item

            ___words = len(___item.split())
            ___without_punctuations = len([i for i in ___item.split() if not any(
                q in STORAGE.punctuations for q in i[:-1]) and i not in STORAGE.punctuations])
            ___w_uppercase = len([i for i in ___item.split() if i.isupper()])
            ___w_lowercase = len([i for i in ___item.split() if i.islower()])
            ___w_capitalize = len([i for i in ___item.split() if FUNCTION.iscapitalize(i)])

            ___characters = len(___item)
            ___without_linebreaks = len(___item.replace('\n', ''))
            ___without_blankspaces = len(___item.replace(' ', ''))
            ___without_both = len(___item.replace(' ', '').replace('\n', ''))
            ___c_uppercase = len([i for i in list(___item) if i.isupper()])
            ___c_lowercase = len([i for i in list(___item) if i.islower()])

            ___numbers = sum((___item.count(num) for num in STORAGE.numbers))

            ___punctuations = sum((___item.count(char) for char in STORAGE.punctuations))

            widget.see('insert')
            self.object.wordsStats.configure(text=f'Words: {___words:,}')
            self.object.wordsStatsTooltips.configure(
                message=f'''Words without punctuations: {___without_punctuations:,} ({0 if not ___words else ___without_punctuations / ___words * 100:.1f}%)
UPPERCASE | lowercase | Capitalize: {___w_uppercase} | {___w_lowercase} | {___w_capitalize} ({0 if not ___words else ___w_uppercase / ___words * 100:.1f}% | {0 if not ___words else ___w_lowercase / ___words * 100:.1f}% | {0 if not ___words else ___w_capitalize / ___words * 100:.1f}%)''')

            self.object.charactersStats.configure(text=f'Characters: {___characters:,}')
            self.object.charactersStatsTooltip.configure(
                message=f'''Characters without blank spaces: {___without_blankspaces:,} ({0 if not ___characters else ___without_blankspaces / ___characters * 100:.1f}%)
Characters without line breaks: {___without_linebreaks:,} ({0 if not ___characters else ___without_linebreaks / ___characters * 100:.1f}%)
Characters without spaces/line-breaks: {___without_both:,} ({0 if not ___characters else ___without_both / ___characters * 100:.1f}%)
UPPERCASE | lowercase: {___c_uppercase} | {___c_lowercase} ({0 if not ___characters else ___c_uppercase / ___characters * 100:.1f}% | {0 if not ___characters else ___c_lowercase / ___characters * 100:.1f}%)''')
            self.object.numbersStats.configure(text=f'Numbers: {___numbers}')
            self.object.numbersStatsTooltips.configure(
                message=f'Numbers: {___numbers} ({0 if not ___characters else ___numbers / ___characters * 100:.1f}%)')

            self.object.punctuationsStats.configure(text=f'Punctuations: {___punctuations}')
            self.object.punctuationsStatsTooltips.configure(
                message=f'Punctuations: {___punctuations} ({0 if not ___characters else ___punctuations / ___characters * 100:.1f}%)')

            if len(___item) > 1000000 and not __one_million:
                __one_million = True
                messagebox.showwarning('Warning',
                                       f'You have reached more than 1 million characters.\nPlease remember that {PROJECT_NAME} might run slower or freeze with a huge number of characters.')
            elif len(___item) < 1000000:
                __one_million = False

        widget.bind('<KeyRelease>', __result_bind)

    def _bind_action(self, value, widget: ctk.CTkTextbox = None):
        if widget is None:
            widget = self.object.mainTextbox
        index = STORAGE.text_cases.index(value)
        new = STORAGE.current_text if STORAGE.current_text != '' else STORAGE.placeholder
        widget.delete('0.0', 'end')
        if index == 0:
            widget.insert('0.0', new)
        elif index == 1:
            widget.insert('0.0', new.capitalize())
        elif index == 2:
            widget.insert('0.0', new.upper())
        elif index == 3:
            widget.insert('0.0', new.lower())
        elif index == 4:
            widget.insert('0.0', new.swapcase())
        self._bind_result()

    @staticmethod
    def exit():
        root.destroy()

    @staticmethod
    def find(shift_pressed=False):
        if STORAGE._Utilities.is_find:
            STORAGE._Utilities.is_find.lift()
            return
        if root.focus_get() != root.mainTextbox._textbox:
            return
        if root.mainTextbox.get('0.0', 'end-1c') == '':
            return
        sel_first, sel_last = False, False
        case_sensitive = True
        root.focus()

        STORAGE._Utilities.is_find = findWindow = ctk.CTkToplevel(root)
        findWindow.title('Find')
        findWindow.focus()
        findWindow.resizable(False, False)
        findWindow.attributes('-topmost', STORAGE.topmost)
        findWindow.after(250, findWindow.lift)

        def change_case():
            nonlocal case_sensitive
            case_sensitive = False if case_sensitive else True
            find_text()

        findMenu = tk.Menu(findWindow, tearoff=0)
        findMenu.add_checkbutton(label='Case sensitive', command=change_case)

        mainFindFrame = ctk.CTkFrame(findWindow, fg_color='transparent')
        mainFindFrame.grid(row=3, column=3, padx=15, pady=(10, 0))

        findEntry = ctk.CTkEntry(mainFindFrame, width=250,
                                 placeholder_text=f'Find')
        findEntry.grid(row=3, column=3)

        resultLabel = ctk.CTkLabel(mainFindFrame, text='Result: 0 (0.0%)')
        resultToolTip = CTkToolTip(resultLabel, message='0/0 (0.0%)')
        resultToolTip.attributes('-topmost', True)
        resultLabel.grid(row=5, column=2, columnspan=4)

        def find_text(event=None):
            item = findEntry.get()
            if event is not None and event.keycode == 13:
                return
            root.mainTextbox.tag_delete('chosen')

            idx = '0.0'
            edx = 'end-1c'
            occurrence = 0
            positions = []
            index_positions = 0

            def next_position(_):
                nonlocal index_positions
                start_highlight_index, end_highlight_index = positions[index_positions]
                if index_positions < 0:
                    resultLabel.configure(
                        text=f'Result: {occurrence} ({0 if not len(text) else occurrence * len(item) / len(text) * 100:.1f}%)')
                    root.mainTextbox.tag_delete('chosen')
                    index_positions += 1
                    return
                root.mainTextbox.yview(start_highlight_index)
                root.mainTextbox.tag_delete('chosen')
                root.mainTextbox.tag_add('chosen', start_highlight_index, end_highlight_index)
                root.mainTextbox.tag_config('chosen', background='lime', foreground='black')

                index_positions += 1
                resultLabel.configure(
                    text=f'Result: {index_positions}/{occurrence} ({0 if not len(text) else occurrence * len(item) / len(text) * 100:.1f}%)')
                if index_positions == len(positions):
                    index_positions = -1

            if shift_pressed and sel_first and sel_last:
                idx, edx = sel_first, sel_last
            text = root.mainTextbox.get(idx, edx)
            resultLabel.configure(text=f'Searching in {len(text)} characters...') if len(text) else None
            if item != '' and item in text:
                findEntry.configure(text_color=('black', 'white'))
                root.mainTextbox.tag_delete('found')
                while True:
                    idx = root.mainTextbox.search(item, idx, stopindex=edx, nocase=1 if case_sensitive else 0)
                    if findEntry.get() != item:
                        return
                    if not idx:
                        break
                    lastidx = '%s+%dc' % (idx, len(item))

                    root.mainTextbox.tag_add('found', idx, lastidx)
                    positions.append((idx, lastidx))
                    idx = lastidx

                    occurrence += 1
                    root.update()
                root.mainTextbox.yview(root.mainTextbox.search(item, '0.0', stopindex='end'))
                root.mainTextbox.tag_config('found', background='blue', foreground='white')

                findEntry.bind('<Return>', next_position)
            else:
                # messagebox.showwarning('Result', 'Couldn\'t find any matches.', parent=findWindow)
                findEntry.configure(text_color='red' if item != '' else ('black', 'white'))
                root.mainTextbox.tag_delete('found')
            resultLabel.configure(
                text=f'Result: {occurrence} ({0 if not len(text) else occurrence * len(item) / len(text) * 100:.1f}%)')
            resultToolTip.configure(
                message=f'{occurrence * len(item)}/{len(text)} ({0 if not len(text) else occurrence * len(item) / len(text) * 100:.1f}%)')

        if root.mainTextbox.tag_ranges("sel"):
            sel_first, sel_last = root.mainTextbox.tag_ranges("sel")
            findEntry.configure(placeholder_text='Find (In selected text)')
            if shift_pressed:
                root.mainTextbox.tag_add('selected', sel_first, sel_last)
                root.mainTextbox.tag_config('selected', background='yellow', foreground='black')
                root.mainTextbox.yview(sel_first)
            else:
                findEntry.insert(0, root.mainTextbox.get(sel_first, sel_last))
                find_text()
        else:
            root.focus()

        def clear_text():
            findEntry.delete(0, 'end')
            root.mainTextbox.tag_delete('found')
            root.mainTextbox.tag_delete('chosen')
            resultLabel.configure(text='Result: 0 (0.0%)')
            findWindow.focus()

        findEntry.bind('<KeyRelease>', find_text)
        findEntry.bind("<Button-3>", lambda event: findMenu.post(event.x_root, event.y_root))

        clearButton = ctk.CTkButton(mainFindFrame, text='', width=0, cursor='hand2', fg_color='red',
                                    hover_color='#cf1508', command=clear_text,
                                    image=ctk.CTkImage(Image.open('assets\\textures\\trashbin.png'), size=(18, 18)))
        clearButton.grid(row=3, column=4)

        def close_find():
            for tag in root.mainTextbox.tag_names():
                root.mainTextbox.tag_delete(tag)
            root.mainTextbox.unbind('<KeyRelease>')
            Utilities(root)._bind_result()
            STORAGE._Utilities.is_find = False
            root.mainTextbox.focus()
            findWindow.destroy()

        root.mainTextbox.bind('<KeyRelease>', find_text)
        findWindow.protocol('WM_DELETE_WINDOW', close_find)

    @staticmethod
    def set_widget_color(widget: ctk.CTkTextbox, color=STORAGE.THEME_OBJECT['CTkTextbox']['text_color']):
        widget.configure(text_color=color, autoseparators=True)

    @staticmethod
    def change_mode(mode: str, save: bool = False):
        ctk.set_appearance_mode(mode)
        STORAGE.APPEARANCE_MODE = mode
        if save:
            Utilities.save_file()

    @staticmethod
    def change_topmost(value: bool):
        value = False if value else True

        for win in [STORAGE._Windows.ROOT, STORAGE._Windows.SETTING]:
            win.attributes('-topmost', value)
        STORAGE.topmost = value
        Utilities.save_file()

    @staticmethod
    def change_sticky(value: bool):
        value = False if value else True
        if value:
            Utilities.move_window(STORAGE._Windows.SETTING, STORAGE._Windows.ROOT)
            STORAGE._Windows.ROOT.bind('<Configure>',
                                       lambda _: Utilities.move_window(STORAGE._Windows.SETTING, STORAGE._Windows.ROOT))
        else:
            STORAGE._Windows.ROOT.unbind('<Configure>')

        STORAGE.sticky_setting = value
        Utilities.save_file()

    @staticmethod
    def move_window(window: ctk.CTk | ctk.CTkToplevel, parent: ctk.CTk | ctk.CTkToplevel = STORAGE._Windows.ROOT):
        window.geometry(f'+{parent.winfo_width() + parent.winfo_x() + 10}+{parent.winfo_y()}')

    @staticmethod
    def save_file():
        with open('data\\config.txt', 'w') as save:
            save.write(
                STORAGE._config_template.format(STORAGE.THEME, STORAGE.APPEARANCE_MODE, STORAGE.placeholder,
                                                STORAGE.corner_radius, STORAGE.punctuations, STORAGE.numbers,
                                                STORAGE.undo,
                                                '-unlimited' if STORAGE.max_undo <= 0 else STORAGE.max_undo,
                                                STORAGE.topmost, STORAGE.sticky_setting))

    @staticmethod
    def open(path: str, select: bool = False):
        if select:
            os.system(f'explorer /select,\"{path}\"')
        else:
            os.startfile(os.path.realpath(path))

    @staticmethod
    def punctuationsBind(character):
        if len(character) > 50:
            return False
        if set(character) == set(STORAGE.punctuations):
            return False
        if len(character):
            STORAGE.punctuations = character
            Utilities.save_file()
        return True

    @staticmethod
    def numbersBind(character):
        if set(character) == set(STORAGE.numbers):
            return False
        if character != '' and not character.isdigit():
            return False
        if len(character):
            STORAGE.numbers = character
            Utilities.save_file()
        return True

    @staticmethod
    def hyperlinksBind(widget: ctk.CTkLabel, link: str, weight: str = 'bold', size: int = 11):
        widget.cget('font').configure(weight=weight, size=size)

        widget.bind('<Button-1>', lambda _: webbrowser.open(link))
        widget.bind('<Button-2>',
                    lambda _: messagebox.showinfo('Hyperlink',
                                                  f'Link: {link}'))
        widget.bind('<Enter>', lambda _: widget.cget('font').configure(underline=True))
        widget.bind('<Leave>', lambda _: widget.cget('font').configure(underline=False))

    def configure(self, parent: Application | ctk.CTk | ctk.CTkToplevel = None):
        if parent is None:
            parent = self.object

        self.object = parent


root = STORAGE._Windows.ROOT = Application()
root.withdraw()
root.attributes('-topmost', STORAGE.topmost)

Load(root)

keyboard.add_hotkey('ctrl+shift+f', Utilities.find, args=[True])
keyboard.add_hotkey('ctrl+f', Utilities.find)
root.protocol('WM_DELETE_WINDOW', Utilities.exit)
root.mainloop()
