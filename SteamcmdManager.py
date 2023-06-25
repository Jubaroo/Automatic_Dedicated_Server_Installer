import os
import subprocess
import tempfile
import threading
import time
import zipfile
from tkinter import messagebox

import requests
from tqdm import tqdm


class SteamCmdManager:
    @staticmethod
    def progress_animation(progress, target, stop_event):
        """
        Animate the progress bar until it reaches the target value.
        Args:
            progress (ttk.Progressbar): The progress bar to animate.
            target (int): The target value for the progress bar.
            stop_event (threading.Event): An event that will stop the progress bar when set.
        """
        while progress['value'] < target and not stop_event.is_set():
            time.sleep(0.1)  # Delay between each increment
            progress['value'] += 0.2  # Increment the progress bar

    @staticmethod
    def install(progress):
        """
        Create a new thread to install SteamCMD.
        """
        stop_event = threading.Event()
        t = threading.Thread(target=SteamCmdManager._install_steamcmd, args=(progress, stop_event))
        t.start()

    @staticmethod
    def _install_steamcmd(progress, stop_event):
        """
        Download and install SteamCMD.
        """
        try:
            # Download the SteamCMD installation zip file
            url = "https://steamcdn-a.akamaihd.net/client/installer/steamcmd.zip"
            steamcmd_zip_path = os.path.join(tempfile.gettempdir(), "steamcmd.zip")

            response = requests.get(url, stream=True)
            total_size = int(response.headers.get('content-length', 0))
            block_size = 1024

            # Create a progress bar to display the download progress
            progress_bar = tqdm(total=total_size, unit='iB', unit_scale=True)

            with open(steamcmd_zip_path, 'wb') as file:
                # Download the file in chunks and update the progress bar
                for data in response.iter_content(block_size):
                    progress_bar.update(len(data))
                    progress['value'] += len(data) / total_size * 100  # update GUI progress bar
                    file.write(data)
            progress_bar.close()

            print('Downloaded the steamcmd.zip file...')

            # Set the directory to SteamCMD
            steamcmd_dir = 'C:\\SteamCMD'

            # If the directory does not exist, create it
            if not os.path.exists(steamcmd_dir):
                os.makedirs(steamcmd_dir)

            # Extract the contents of the downloaded zip file
            with zipfile.ZipFile(steamcmd_zip_path, 'r') as zip_ref:
                # Extract the contents to the SteamCMD directory
                zip_ref.extractall(steamcmd_dir)

            print('Unzipped the steamcmd.zip file...')

            # Set the working directory to the extracted SteamCMD directory
            os.chdir(steamcmd_dir)

            print('Changed the directory to SteamCMD...')

            progress['value'] = 0  # 0% progress
            threading.Thread(target=SteamCmdManager.progress_animation, args=(progress, 100, stop_event)).start()

            # Run the command
            process = subprocess.Popen('steamcmd +quit', shell=True)
            process.wait()

            # Stop the progress bar when the command is done
            stop_event.set()
            progress['value'] = 100  # 100% progress
            progress.stop()

            # Show a success message if the installation was successful
            if process.returncode in (7, 0):
                messagebox.showinfo("SteamCMD Installation", "SteamCMD installed successfully.")

            else:
                messagebox.showerror('Server Installation',
                                     f'There was an error installing the server. Error code: {process.returncode}')
        except Exception as e:
            # Show an error message if the installation failed
            print(f"An error occurred: {str(e)}")
            messagebox.showerror("SteamCMD Installation", "There was an error installing SteamCMD.")
