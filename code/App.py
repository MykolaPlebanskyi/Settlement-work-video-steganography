import os
import pickle
import shutil
import subprocess
import numpy as np
import cv2
import tkinter as tk
from tkinter import filedialog
import tkinter.simpledialog as sd

from VideoSteganography import VideoSteganography


class VideoSteganographyApp(VideoSteganography):
    def __init__(self, root):
        self.root = root
        self.root.title("Video Steganography App")

        self.label = tk.Label(root, text="VIDEO STEGANOGRAPHY OPERATIONS", font=('Helvetica', 16))
        self.label.pack(pady=10)

        self.encode_button = tk.Button(root, text="Embed data in a video", command=self.encode_video)
        self.encode_button.pack(pady=10)

        self.decode_button = tk.Button(root, text="Extract data from a video", command=self.extract_data)
        self.decode_button.pack(pady=10)

        self.exit_button = tk.Button(root, text="Exit", command=root.destroy)
        self.exit_button.pack(pady=10)

        self.info_label = tk.Label(root, text="", font=('Helvetica', 12))
        self.info_label.pack(pady=10)

        # self.video_steganography = VideoSteganography(app_instance=self)

    def encode_menu(self):
        encode_window = tk.Toplevel(self.root)
        encode_window.title("Encode Menu")

        encode_label = tk.Label(encode_window, text="ENCODE MENU", font=('Helvetica', 14))
        encode_label.pack(pady=10)

        encode_button = tk.Button(encode_window, text="Embed data in a video", command=self.encode_video)
        encode_button.pack(pady=10)

        self.root.withdraw()

    def encode_video(self):
        file_path = filedialog.askopenfilename(title="Select Video File", filetypes=[("MP4 files", "*.mp4")])
        if file_path:
            frame_ = self.encode_vid_data(file_path)
            self.set_frame(frame_)
            initial_file = "Output_video.mp4"
            file_path_out = filedialog.asksaveasfilename(initialdir=file_path, initialfile=initial_file)
            self.transfer_sound(file_path, file_path_out)
            message = "Encoded data successfully."
            self.display_info_window(message)

    def display_info_window(self, message):
        info_window = tk.Toplevel(self.root)
        info_window.title("Information")

        label = tk.Label(info_window, text=message, font=('Helvetica', 12))
        label.pack(padx=20, pady=10)

        ok_button = tk.Button(info_window, text="OK", command=info_window.destroy)
        ok_button.pack(pady=10)

    def extract_data(self):
        file_path = filedialog.askopenfilename(title="Select Video File")
        if file_path:
            decoded_data = self.decode_vid_data(file_path)
            if decoded_data is not None:
                message = "Decode data is: " + str(decoded_data)
            else:
                message = "Failed to extract data from the video."
            self.display_info_window(message)

    def display_error_message(self, message):
        error_window = tk.Toplevel(self.root)
        error_window.title("Error")

        label = tk.Label(error_window, text=message, font=('Helvetica', 12), fg='red')
        label.pack(padx=20, pady=10)

        ok_button = tk.Button(error_window, text="OK", command=error_window.destroy)
        ok_button.pack(pady=10)

    def display_error_message(self, message):
        error_window = tk.Toplevel(self.root)
        error_window.title("Error")

        label = tk.Label(error_window, text=message, font=('Helvetica', 12), fg='red')
        label.pack(padx=20, pady=10)

        ok_button = tk.Button(error_window, text="OK", command=error_window.destroy)
        ok_button.pack(pady=10)
