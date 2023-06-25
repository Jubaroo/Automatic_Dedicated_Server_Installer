import json
import threading
from tkinter import messagebox

import requests


class ApiManager:
    @staticmethod
    def get_dedicated_servers_thread(app_ids, server_menu, server_var, show_selected_appid):
        """
        Create a new thread to fetch dedicated servers data from the API.
        Args:
            app_ids (dict): A dictionary to store the server names and their corresponding App IDs.
            server_menu (ttk.Combobox): The server menu combobox widget.
            server_var (tk.StringVar): The server selection variable.
            show_selected_appid (function): Function to update the selected_appId_var.

        Returns:
            threading.Thread: The created thread.
        """
        # Create a new thread that executes the _get_dedicated_servers function
        t = threading.Thread(target=ApiManager._get_dedicated_servers, args=(app_ids, server_menu, server_var,
                                                                             show_selected_appid))
        return t

    @staticmethod
    def _get_dedicated_servers(app_ids, server_menu, server_var, show_selected_appid):
        """
        Fetch the dedicated servers data from the Steam API.
        Args:
            app_ids (dict): A dictionary to store the server names and their corresponding App IDs.
            server_menu (ttk.Combobox): The server menu combobox widget.
            server_var (tk.StringVar): The server selection variable.
            show_selected_appid (function): Function to update the selected_appId_var.
        """
        try:
            # Send a request to the Steam API to get the list of apps
            response = requests.get("https://api.steampowered.com/ISteamApps/GetAppList/v2/")
            if response.status_code == 200:
                # Parse the response and extract the dedicated servers
                apps = json.loads(response.text)["applist"]["apps"]
                dedicated_servers = [app for app in apps if "dedicated server" in app["name"].lower()]

                # Store the server names and App IDs in the app_ids dictionary
                for dedicated_server in dedicated_servers:
                    app_ids[dedicated_server["name"]] = dedicated_server["appid"]

                # Sort the server names alphabetically
                sorted_server_names = sorted(app_ids.keys())

                # Update the server menu and selection variable
                server_var.set("Choose a game server")
                server_menu["values"] = sorted_server_names

                # Update the selected_appId_var to display the selected server's App ID
                show_selected_appid()
            else:
                # Show an error message if there was an error contacting the Steam API
                messagebox.showerror("API Error", "There was an error contacting the Steam API.")
        except Exception as e:
            # Show an error message if there was an error processing the API response
            messagebox.showerror("API Error", f"There was an error processing the API response: {str(e)}")
