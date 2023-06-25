import os
import subprocess
import threading
import time
from tkinter import messagebox


class ServerManager:
    @staticmethod
    def install(selected_appid, install_path, progress):
        """
        Install the server with the given App ID and installation path.
        Args:
            selected_appid (str): The App ID of the selected server.
            install_path (str): The installation path for the server.
            progress (ttk.Progressbar): The progress bar to update.
        """
        # Create the installation path if it doesn't exist
        os.makedirs(install_path, exist_ok=True)
        threading.Thread(target=ServerManager.progress_animation, args=(progress, 25)).start()

        print('Constructing the installation command...')

        # Construct the installation command
        install_command = (
            f'C:/SteamCMD/steamcmd.exe +login anonymous +force_install_dir "{install_path}" '
            f'+app_update {selected_appid} validate +quit'
        )

        print('Constructed the installation command...', install_command)
        threading.Thread(target=ServerManager.progress_animation, args=(progress, 50)).start()

        # Run the installation command using subprocess
        process = subprocess.Popen(install_command, shell=True)
        threading.Thread(target=ServerManager.progress_animation, args=(progress, 75)).start()
        process.wait()

        # Show success message if the installation was successful
        if process.returncode in (0, 1):
            progress['value'] = 100  # 100% progress
            messagebox.showinfo("Server Installation", "Server installed successfully.")
        else:
            # Check for specific error codes and display appropriate error messages
            if process.returncode >= 1:
                messagebox.showerror('Server Installation',
                                     'StemCMD is not installed. Use the button on the bottom left to install SteamCMD')
                try:
                    output = subprocess.check_output(install_command, shell=True, stderr=subprocess.STDOUT)
                except subprocess.CalledProcessError as e:
                    output = e.output
                    messagebox.showerror('Server Installation',
                                         'There was an error installing the server:\n' + output.decode())
                else:
                    messagebox.showinfo("Server Installation", "Server installed successfully.")

    @staticmethod
    def progress_animation(progress, target):
        """
        Animate the progress bar until it reaches the target value.
        Args:
            progress (ttk.Progressbar): The progress bar to animate.
            target (int): The target value for the progress bar.
        """
        while progress['value'] < target:
            time.sleep(0.1)  # Delay between each increment
            progress['value'] += 0.03  # Increment the progress bar
