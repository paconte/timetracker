# Coppyright (c) 2020 Francisco Javier Revilla Linares to present.
# All rights reserved.
import tkinter as tk
import logging

from cysystemd import journal
from datetime import datetime
from PIL import Image
from PIL import ImageTk
from time import sleep
from tkinter import font as tkfont
from tkinter import messagebox
from random import random

from ctes import COLUMN_USERNAME_MAX_LENGTH
from ctes import COLUMN_USERNAME_MIN_LENGTH
from ctes import WIFI_CONFIG_NO_PASSWD
from ctes import WIFI_CONFIG
from ctes import WIFI_TMP_CONFIG_FILE
from ctes import WIFI_CONFIG_HEADER

from models import session_factory
from models import get_user_by_template
from models import add_login2
from models import add_logout2

from FingerprintController import FingerprintController
from utils import get_logging_dict_config
from utils import delete_file
from utils import export_data_to_usb
from utils import create_wifi_executable
from utils import update_wifi_configuration


# logging configuration
logging.config.dictConfig(get_logging_dict_config())
logger = logging.getLogger('timetracker')


b_height = 4
b_width = 50


def update_clock(frame):
    time_string = datetime.now().strftime("%H:%M:%S  %d-%m-%Y")
    frame.clock.config(text=time_string)
    frame.clock.after(1*1000, frame.update_clock)


class SampleApp(tk.Tk):
    fc = None

    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)

        self.clock_font = tkfont.Font(family='Helvetica', size=30, weight="bold", slant="italic")
        self.title_font = tkfont.Font(family='Helvetica', size=18, weight="bold", slant="italic")

        # the container is where we'll stack a bunch of frames
        # on top of each other, then the one we want visible
        # will be raised above the others
        #container = tk.Frame(self, padx=100, pady=100)
        self.container = tk.Frame(self)

        self.container.pack(side="top", fill="both", expand=True)
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        self.frames = {}
        for F in (InfoPage, StartPage, ClockinPage, ClockoutPage,
                    AddUserPage, DeleteUserPage, ExportDataPage,
                    ConfigureWifiPage):

            page_name = F.__name__
            frame = F(parent=self.container, controller=self)
            self.frames[page_name] = frame

            # put all of the pages in the same location;
            # the one on the top of the stacking order
            # will be the one that is visible.
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame("StartPage")

    def show_frame(self, page_name):
        '''Show a frame for the given page name'''
        frame = self.frames[page_name]

        if page_name in ['AddUserPage', 'DeleteUserPage', 'ConfigureWifiPage']:
            frame.entry_username.focus()
        elif 'StartPage' == page_name:
            frame.focus()

        frame.tkraise()

    def show_info(self, text, error=False):
        frame = self.frames['InfoPage']
        if error:
            frame.set_title_error()
        else:
            frame.set_title_success()
        frame.set_text(text)

        self.show_frame('InfoPage')

    def init_fc(self):
        self.fc = FingerprintController()

    def show_add_user_step_one(self, username):
        page_name = AddUserFirstStepPage.__name__
        frame = AddUserFirstStepPage(
            parent=self.container, controller=self, username=username)
        self.frames[page_name] = frame
        frame.grid(row=0, column=0, sticky="nsew")
        self.show_frame(page_name)

    def show_add_user_step_two(self, username):
        page_name = AddUserSecondStepPage.__name__
        frame = AddUserSecondStepPage(
            parent=self.container, controller=self, username=username)
        self.frames[page_name] = frame
        frame.grid(row=0, column=0, sticky="nsew")
        self.frames['AddUserFirstStepPage'].destroy()
        self.show_frame(page_name)

    '''
    def finish_add_user(self, username):
        txt = "Usuario {username} añadido."
        self.frames['AddUserSecondStepPage'].destroy()
        del self.fc
        self.controller.show_info(txt.format(username=self.username))
    '''


class InfoPage(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller

        self.label1 = tk.Label(self, text="ERROR", font=controller.title_font)
        self.label1.pack(side="top", fill="x")

        self.label2 = tk.Label(self, text="", font=controller.title_font)
        self.label2.pack(side="top", fill="x", pady=10)

        button1 = tk.Button(self, text="Volver",
                           height=b_height, width=b_width,
                           command=lambda: controller.show_frame("StartPage"))
        button1.pack(pady=10)

    def set_title_error(self):
        self.label1.config(text="ERROR")

    def set_title_success(self):
        self.label1.config(text="EXITO")

    def set_text(self, text):
        self.label2.config(text=text)


class StartPage(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller

        row1 = tk.Frame(self)
        button1 = tk.Button(row1, text="Fichar entrada",
                            height=b_height, width=b_width,
                            command=lambda: controller.show_frame("ClockinPage"))
        button2 = tk.Button(row1, text="Fichar salida",
                            height=b_height, width=b_width,
                            command=lambda: controller.show_frame("ClockoutPage"))

        row2 = tk.Frame(self)
        button3 = tk.Button(row2, text="Añadir usuario",
                            height=b_height, width=int(b_width/2),
                            command=lambda: controller.show_frame("AddUserPage"))
        button4 = tk.Button(row2, text="Borrar usuario",
                            height=b_height, width=int(b_width/2),
                            command=lambda: controller.show_frame("DeleteUserPage"))

        row3 = tk.Frame(self)
        button5 = tk.Button(row3, text="Exportar datos",
                            height=b_height, width=int(b_width/2),
                            command=lambda: controller.show_frame("ExportDataPage"))
        button6 = tk.Button(row3, text="Configurar Wifi",
                            height=b_height, width=int(b_width/2),
                            command=lambda: controller.show_frame("ConfigureWifiPage"))

        row1.pack()
        button1.pack(pady=30)
        button2.pack(pady=15)
        row2.pack()
        button3.pack(side="left")
        button4.pack(side="right", padx=15)
        row3.pack(pady=15)
        button5.pack(side="left")
        button6.pack(side="right", padx=15)

    def update_clock(self):
        update_clock(self)


class ClockinPage(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller

        self.clock = tk.Label(self, font=controller.clock_font)

        label1 = tk.Label(
            self,
            text="Pulsa escanear e introduce tu huella",
            font=controller.title_font)
        button1 = tk.Button(self, text="Escanear",
                            height=b_height, width=b_width,
                            command=self.clockin)
        button2 = tk.Button(self, text="Volver",
                            height=b_height, width=b_width,
                            command=lambda: controller.show_frame("StartPage"))

        self.clock.pack(side="top", fill="x")
        self.update_clock()

        label1.pack(side="top", fill="x", pady=50)
        button1.pack(pady=10)
        button2.pack(pady=10)

    def update_clock(self):
        update_clock(self)

    def clockin(self):
        logger.info('Clockin starts.')

        fc = FingerprintController()
        if fc == None:
            logger.info('pyfingerprint could not be initialized')
            self.controller.show_info("Vuelve a intentarlo", True)
        else:
            template = fc.search_user()
            del fc

            # check template found
            if template < 0:
                self.controller.show_info("Usuario desconocido.", True)
                return

            user = get_user_by_template(template, session_factory())
            username = user.name
            result = add_login2(user, session_factory())

            if result:
                txt = "Bienvenido/a {username}"
                self.controller.show_info(txt.format(username=username))
            else:
                txt = "{username} no se puede fichar la entrada dos veces consecutivas"
                self.controller.show_info(txt.format(username=user.name), True)

        logger.info('Clockin finished.')


class ClockoutPage(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller

        self.clock = tk.Label(self, font=controller.clock_font)

        label1 = tk.Label(
            self,
            text="Pulsa escanear e introduce tu huella",
            font=controller.title_font)
        button1 = tk.Button(self, text="Escanear",
                            height=b_height, width=b_width,
                            command=self.clockout)
        button2 = tk.Button(self, text="Volver",
                            height=b_height, width=b_width,
                            command=lambda: controller.show_frame("StartPage"))

        self.clock.pack(side="top", fill="x")
        self.update_clock()

        label1.pack(side="top", fill="x", pady=50)
        button1.pack(pady=10)
        button2.pack(pady=10)

    def update_clock(self):
        update_clock(self)

    def clockout(self):
        logger.info('Clockout starts.')

        fc = FingerprintController()
        if fc == None:
            self.controller.show_info("Vuelve a intentarlo", True)
        else:
            template = fc.search_user()
            del fc

            # check template found
            if template < 0:
                self.controller.show_info("Usuario desconocido", True)
                return

            user = get_user_by_template(template, session_factory())
            username = user.name
            result = add_logout2(user, session_factory())

            if 0 == result:
                txt = "Hasta pronto {username}"
                self.controller.show_info(txt.format(username=username))
            elif 1 == result:
                txt = "{username} primero tienes que entrar"
                self.controller.show_info(txt.format(username=username), True)
            elif 2 == result:
                txt = "{username} no puedes salir dos veces consecutivas"
                self.controller.show_info(txt.format(username=username), True)
            else:
                self.controller.show_info("Fallo desconocido", True)

        logger.info('Clockout finished.')


class AddUserPage(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller

        # title
        label1 = tk.Label(self, text="Añade un usuario", font=controller.title_font)
        label1.pack(side="top", fill="x")

        # frame with user name entry
        self.row_username = tk.Frame(self)
        label2 = tk.Label(self.row_username, text="Nombre de usuario", height=b_height, width=20)
        self.entry_username = tk.Entry(self.row_username)

        self.row_username.pack(side=tk.TOP, fill=tk.X, pady=10)
        label2.pack(side=tk.LEFT)
        self.entry_username.pack(side=tk.RIGHT, expand=tk.YES, fill=tk.X)
        self.entry_username.focus()

        button1 = tk.Button(self,
                            text="Siguiente",
                            height=b_height, width=b_width,
                            command=lambda: self.action())

        button2 = tk.Button(self, text="Volver",
                            height=b_height, width=b_width,
                            command=self.back)

        button1.pack(pady=10)
        button2.pack(pady=10)

    def action(self):
        logger.info('Add user starts.')

        username = self.entry_username.get()
        self.entry_username.delete(0, len(username))

        # check username chars
        if len(username) < COLUMN_USERNAME_MIN_LENGTH or len(username) > COLUMN_USERNAME_MAX_LENGTH:
            print('dentro de username')
            txt = "El nombre de usuario ha de tener entre {} y {} caracteres."
            self.controller.show_info(
                txt.format(COLUMN_USERNAME_MIN_LENGTH, COLUMN_USERNAME_MAX_LENGTH),
                True)
            return

        # check fingerprint reader
        self.controller.init_fc()
        if self.controller.fc == None:
            print('dentro de check reader')
            self.controller.show_info("Vuelve a intentarlo", True)
            return

        # check username in database
        if self.controller.fc.exists_user(username):
            txt = "El usuario {username} ya existe"
            self.controller.show_info(txt.format(username=username), True)
            return

        # show next frame
        self.controller.show_add_user_step_one(username)

    def back(self):
        username = self.entry_username.get()
        self.entry_username.delete(0, len(username))
        self.controller.show_frame("StartPage")
        return


class AddUserFirstStepPage(tk.Frame):

    def __init__(self, parent, controller, username):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        self.username = username

        # title
        label1 = tk.Label(self, text="Añade un usuario", font=controller.title_font)
        label1.pack(side="top", fill="x")


        self.button1 = tk.Button(self,
                            text="Pulsa para leer huella",
                            height=b_height, width=b_width,
                            command=lambda: self.action())

        button2 = tk.Button(self, text="Volver",
                            height=b_height, width=b_width,
                            command=lambda: controller.show_frame("StartPage"))

        self.button1.pack(pady=10)
        button2.pack(pady=10)

    def action(self):
        #self.button1.config(state="disabled")
        # check user fingerprint
        logger.info('Reading new user\'s finderprint.')
        result = self.controller.fc.add_user_step1()
        if 0 == result:
            self.controller.show_add_user_step_two(self.username)
        elif self.controller.fc.RESULT_TEMPLATE_ALREADY_EXISTS == result:
            self.controller.show_info("Ya existe.", True)
        else:
            self.controller.show_info("Error leyendo dedo.", True)

        logger.info('Add user finished.')
        return


class AddUserSecondStepPage(tk.Frame):

    def __init__(self, parent, controller, username):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        self.username = username

        # title
        label1 = tk.Label(self, text="Añade un usuario", font=controller.title_font)
        label1.pack(side="top", fill="x")

        self.button1 = tk.Button(self,
                            text="Pulsa para volver a leer huella",
                            height=b_height, width=b_width,
                            command=lambda: self.action())

        button2 = tk.Button(self, text="Volver",
                            height=b_height, width=b_width,
                            command=lambda: controller.show_frame("StartPage"))

        self.button1.pack(pady=10)
        button2.pack(pady=10)

    def action(self):
        self.button1.config(state="disabled")
        result = self.controller.fc.add_user_step2(self.username)
        if 0 == result:
            txt = "Usuario {username} añadido."
            self.controller.show_info(txt.format(username=self.username))
        elif self.controller.fc.RESULT_FINGER_DO_NOT_MATCH == result:
            self.controller.show_info("Las huellas no coinciden.", True)
        else:
            self.controller.show_info("Error leyendo dedo.", True)

        del self.controller.fc
        logger.info('Add user finished.')
        return


class ClockinPage2(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller

        self.label = tk.Label(
            self,
            text="Leyendo huella...",
            font=controller.title_font)
        self.label.pack(side="top", fill="x")

        image = Image.open("fingerprintscanner300x300.jpg")
        photo = ImageTk.PhotoImage(image)
        label = tk.Label(self, image=photo)
        label.image = photo # keep a reference!
        label.pack(pady=10, fill='both')


        button1 = tk.Button(self, text="Volver",
                            height=b_height, width=b_width,
                            command=lambda: controller.show_frame("StartPage"))
        button1.pack(pady=10)


class DeleteUserPage(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller

        # title
        label1 = tk.Label(self, text="Borra un usuario", font=controller.title_font)
        label1.pack(side="top", fill="x")

        # frame with user name entry
        self.row_username = tk.Frame(self)
        label2 = tk.Label(self.row_username, text="Nombre de usuario", height=b_height, width=20)
        self.entry_username = tk.Entry(self.row_username)

        self.row_username.pack(side=tk.TOP, fill=tk.X, pady=10)
        label2.pack(side=tk.LEFT)
        self.entry_username.pack(side=tk.RIGHT, expand=tk.YES, fill=tk.X)
        self.entry_username.focus()

        button1 = tk.Button(self,
                            text="Siguiente",
                            height=b_height, width=b_width,
                            command=lambda: self.action())

        button2 = tk.Button(self, text="Volver",
                            height=b_height, width=b_width,
                            command=self.back)

        button1.pack(pady=10)
        button2.pack(pady=10)

    def back(self):
        username = self.entry_username.get()
        self.entry_username.delete(0, len(username))
        self.controller.show_frame("StartPage")
        return

    def action(self):
        username = self.entry_username.get()
        self.entry_username.delete(0, len(username))

        # check fingerprint reader
        self.controller.init_fc()
        if self.controller.fc == None:
            self.controller.show_info("Vuelve a intentarlo", True)
            return

        # check username in database
        if not self.controller.fc.exists_user(username):
            txt = "El usuario {username} no existe"
            self.controller.show_info(txt.format(username=username), True)
            return

        # delete user
        self.controller.fc.delete_user(username)

        # show next frame
        txt = "El usuario {username} ha sido borrado"
        self.controller.show_info(txt.format(username=username))


class ExportDataPage(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller

        # title
        label1 = tk.Label(self, text="Exportar datos", font=controller.title_font)
        label1.pack(side="top", fill="x")


        label2 = tk.Label(self, text="Introduce una memoria usb y pulsa siguiente")
        label2.pack(pady=20)

        button1 = tk.Button(self,
                            text="Siguiente",
                            height=b_height, width=b_width,
                            command=lambda: self.action())
        button2 = tk.Button(self, text="Volver",
                            height=b_height, width=b_width,
                            command=lambda: self.controller.show_frame("StartPage"))

        button1.pack(pady=10)
        button2.pack(pady=10)

    def action(self):
        result = export_data_to_usb()

        if 0 == result: # success
            txt = "Datos exportados correctamente. Extrae tu USB."
            self.controller.show_info(txt)
            return

        if result in [2, 3]: # error mounting usb
            txt = "Error montando el USB."
            self.controller.show_info(txt, True)
            return

        # show error frame
        txt = "Se ha producido un error desconocido."
        self.controller.show_info(txt, True)


class ConfigureWifiPage(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller

        # title
        label1 = tk.Label(self, text="Configurar WiFi", font=controller.title_font)
        label1.pack()

        # frame with user SSID
        row1 = tk.Frame(self)
        label2 = tk.Label(row1, text="SSID (Nombre del WiFi)", height=b_height, width=20)
        self.entry_username = tk.Entry(row1)

        row1.pack(side=tk.TOP, fill=tk.X, pady=10)
        label2.pack(side=tk.LEFT)
        self.entry_username.pack(side=tk.RIGHT, expand=tk.YES, fill=tk.X)
        self.entry_username.focus()

        # frame with PASSWORD
        row2 = tk.Frame(self)
        label3 = tk.Label(row2, text="Password", height=b_height, width=20)
        self.password = tk.Entry(row2)

        row2.pack()
        label3.pack(side=tk.LEFT)
        self.password.pack(side=tk.RIGHT, expand=tk.YES, fill=tk.X)

        # next and back buttons
        button1 = tk.Button(self,
                            text="Siguiente",
                            height=b_height, width=b_width,
                            command=lambda: self.action())

        button2 = tk.Button(self, text="Volver",
                            height=b_height, width=b_width,
                            command=self.back)

        button1.pack(pady=10)
        button2.pack(pady=10)

    def back(self):
        username = self.entry_username.get()
        password = self.password.get()
        self.entry_username.delete(0, len(username))
        self.password.delete(0, len(password))

        self.controller.show_frame("StartPage")
        return

    def action(self):
        ssid = self.entry_username.get()
        self.entry_username.delete(0, len(ssid))
        passwd = self.password.get()
        self.password.delete(0, len(passwd))

        # check ssid length
        if 0 == len(ssid):
            txt = "El SSID introducido es incorrecto"
            self.controller.show_info(txt, True)

        # execute uiid script
        update_wifi_configuration(ssid, passwd)

        # delete file
        delete_file(WIFI_TMP_CONFIG_FILE)

        # show next frame
        txt = "Wifi actualizada a {ssid}"
        self.controller.show_info(txt.format(ssid=ssid))



if __name__ == "__main__":
    logging.info('Starting application')
    create_wifi_executable()
    app = SampleApp()
    app.attributes("-fullscreen", True)
    app.mainloop()
    logging.info('Finish starting application')
