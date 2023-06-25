import collections
import os
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from APIManager import ApiManager
from SearchableCombobox import SearchableCombobox
from ServerManager import ServerManager
from SteamcmdManager import SteamCmdManager
from Tooltip import Tooltip


class ServerInstaller:
    def __init__(self):
        """
        Initialize the ServerInstaller application.
        """
        self.appIds = {}
        self.appIds = collections.OrderedDict()
        self.window = tk.Tk()
        self.window.title("ADSI - Auto Dedicated Server Installer")
        self.window.geometry("500x400")

        self.window.eval('tk::PlaceWindow %s center' % self.window.winfo_toplevel())

        # Initialize variables and create GUI elements
        self.server_var = tk.StringVar()
        self.server_var.set("Loading servers...")
        self.server_menu = self.server_menu = SearchableCombobox(self.window, textvariable=self.server_var,
                                                                 width=60, state="readonly")
        self.progress = ttk.Progressbar(self.window, length=300, mode='determinate')
        self.install_button = ttk.Button(self.window, text="Install Server", command=self.install, state="disabled")
        self.install_button_tooltip = Tooltip(self.install_button, "")  # Init tooltip for Install Server button
        self.install_path_var = tk.StringVar(value="Choose server installation directory")
        self.install_path_entry = ttk.Entry(self.window, textvariable=self.install_path_var, width=50)
        self.selected_appId_var = tk.StringVar(value="")
        self.selected_appId_label = tk.Label(self.window, textvariable=self.selected_appId_var)
        self.browse_button = ttk.Button(self.window, text="Browse", command=self.browse_install_path)
        self.install_steamcmd_button = ttk.Button(self.window, text="Install SteamCMD",
                                                  command=self.install_steamcmd_async)
        # Init tooltip for Install SteamCMD button
        self.install_steamcmd_button_tooltip = Tooltip(self.install_steamcmd_button, "")

        self.get_servers_thread = ApiManager.get_dedicated_servers_thread(self.appIds, self.server_menu,
                                                                          self.server_var, self.show_selected_appid)

        # Configure GUI layout
        self.server_menu.place(relx=0.5, rely=0.25, anchor=tk.CENTER)
        self.install_button.place(relx=0.5, rely=0.7, anchor=tk.CENTER)
        self.install_path_entry.place(relx=0.42, rely=0.55, anchor=tk.CENTER)
        self.selected_appId_label.place(relx=0.5, rely=0.35, anchor=tk.CENTER)
        self.browse_button.place(relx=0.81, rely=0.55, anchor=tk.CENTER)
        self.install_steamcmd_button.place(relx=0.15, rely=0.9, anchor=tk.CENTER)
        self.progress.place(relx=0.5, rely=0.8, anchor=tk.CENTER)

        # Bind events to GUI elements
        self.server_menu.bind("<<ComboboxSelected>>", self.on_server_select)
        self.install_path_entry.bind("<FocusIn>", self.clear_install_path_var)
        self.install_path_entry.bind("<FocusOut>", self.restore_install_path_var)
        self.install_path_entry.bind("<FocusOut>", self.update_install_button_tooltip)  # Update tooltip on focus out

        self.check_steamcmd()

        # Start the thread to fetch dedicated servers data
        self.get_servers_thread.start()

        self.window.mainloop()

    def clear_install_path_var(self, event):
        """
        Clear the install_path_var when the entry widget is focused.
        """
        self.install_path_var.set("")

    def restore_install_path_var(self, event):
        """
        Restore the install_path_var to default when the entry widget loses focus.
        """
        if not self.install_path_var.get():
            self.install_path_var.set("Choose server installation directory")

    def check_steamcmd(self):
        """
        Check if SteamCMD is installed and disable the install button if it is.
        """
        if os.path.exists('C:\\SteamCMD\\steamcmd.exe'):
            self.install_steamcmd_button['state'] = 'disabled'
            self.install_steamcmd_button_tooltip.text = "SteamCMD is already installed"  # Update tooltip
            self.update_install_button_tooltip()
        else:
            self.install_steamcmd_button['state'] = 'normal'
            self.install_steamcmd_button_tooltip.text = "Please install SteamCMD"  # Update tooltip
            self.update_install_button_tooltip()

    def browse_install_path(self):
        """
        Open a dialog to browse and select the server installation path.
        """
        directory = filedialog.askdirectory()
        if directory:
            self.install_path_var.set(directory)
            if self.server_var.get() != "Choose a game server":
                self.install_button["state"] = "normal"
            else:
                self.install_button["state"] = "disabled"
        elif not self.install_path_var.get():  # If no directory selected, set default text
            self.install_path_var.set("Choose server installation directory")

        self.update_install_button_tooltip()  # Update the tooltip after setting the directory

    def show_selected_appid(self):
        """
        Update the selected_appId_var with the selected server's App ID.
        """
        selected_server = self.server_var.get()
        if selected_server != "Choose a game server":
            selected_appid = self.appIds[selected_server]
            self.selected_appId_var.set(f"Server App ID: {selected_appid}")
        else:
            self.selected_appId_var.set("")
            self.install_button["state"] = "disabled"

        self.update_install_button_tooltip()  # Update the tooltip after updating the selected AppID

    def on_server_select(self, event):
        """
        Event handler for selecting a game server from the server menu.
        """
        self.show_selected_appid()
        if self.install_path_var.get() and self.install_path_var.get() != "Choose server installation directory":
            self.install_button["state"] = "normal"
        else:
            self.install_button["state"] = "disabled"

        self.update_install_button_tooltip()  # Update the tooltip after selecting a server

    # noinspection PyMethodMayBeStatic
    def install_steamcmd_async(self):
        """
        Install SteamCMD asynchronously.
        """
        t = threading.Thread(target=self.install_steamcmd_thread)
        t.start()

    def install_steamcmd_thread(self):
        """
        Thread method for installing SteamCMD.
        """
        self.progress.start()  # Start the progress bar
        SteamCmdManager.install(self.progress)  # Pass the progress variable to SteamCmdManager.install()
        self.progress.stop()  # Stop the progress bar
        self.progress['value'] = 0  # 0% progress

        # Ask Tkinter to call check_steamcmd as soon as it can
        self.window.after(0, self.check_steamcmd)

    def install(self):
        """
        Install the selected server with the chosen installation path.
        """
        selected_appid = self.appIds[self.server_var.get()]
        install_path = os.path.normpath(self.install_path_var.get())
        if install_path != "Choose server installation directory":
            installation_thread = threading.Thread(target=self.perform_installation,
                                                   args=(selected_appid, install_path))
            installation_thread.start()
        else:
            messagebox.showwarning("Path not chosen", "Please choose an installation path.")

    def update_install_button_tooltip(self, event=None):
        """
        Update the tooltip for the install button based on current states.
        """
        if 'disabled' in self.install_steamcmd_button.state() and \
                self.server_var.get() != "Choose a game server" and \
                self.install_path_var.get() != "Choose server installation directory":
            self.install_button_tooltip.text = "You may proceed with the installation"
        else:
            missing = []
            if 'normal' in self.install_steamcmd_button.state():
                missing.append("SteamCMD")
            if self.server_var.get() == "Choose a game server":
                missing.append("game server")
            if self.install_path_var.get() == "Choose server installation directory":
                missing.append("directory")
            self.install_button_tooltip.text = "Please select " + ", ".join(missing)

    def perform_installation(self, selected_appid, install_path):
        """
        Perform the server installation in a separate thread.
        """
        # Perform the installation logic here
        ServerManager.install(selected_appid, install_path, self.progress)


# Create an instance of the ServerInstaller application
ServerInstaller()
