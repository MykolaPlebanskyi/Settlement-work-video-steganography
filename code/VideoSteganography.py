import os
import pickle
import shutil
import subprocess
import numpy as np
import cv2
import tkinter as tk
from tkinter import filedialog
import tkinter.simpledialog as sd


class VideoSteganography:
    def msgtobinary(self, msg):
        if type(msg) == str:
            result = ''.join([format(ord(i), "08b") for i in msg])
        elif type(msg) == bytes or type(msg) == np.ndarray:
            result = [format(i, "08b") for i in msg]
        elif type(msg) == int or type(msg) == np.uint8:
            result = format(msg, "08b")
        else:
            raise TypeError("Input type is not supported in this function")
        return result

    def KSA(self, key):
        key_length = len(key)
        S = list(range(256))
        j = 0
        for i in range(256):
            j = (j + S[i] + key[i % key_length]) % 256
            S[i], S[j] = S[j], S[i]
        return S

    def PRGA(self, S, n):
        i = 0
        j = 0
        key = []
        while n > 0:
            n = n - 1
            i = (i + 1) % 256
            j = (j + S[i]) % 256
            S[i], S[j] = S[j], S[i]
            K = S[(S[i] + S[j]) % 256]
            key.append(K)
        return key

    def preparing_key_array(self, s):
        return [ord(c) for c in s]

    def encryption(self, plaintext):
        key = sd.askstring("Key", prompt="Enter the key :", )
        key = self.preparing_key_array(key)

        S = self.KSA(key)

        keystream = np.array(self.PRGA(S, len(plaintext)))
        plaintext = np.array([ord(i) for i in plaintext])

        cipher = keystream ^ plaintext
        ctext = ''
        for c in cipher:
            ctext = ctext + chr(c)
        return ctext

    def decryption(self, ciphertext):
        key = sd.askstring("Key", prompt="Enter the key :")
        key = self.preparing_key_array(key)

        S = self.KSA(key)

        keystream = np.array(self.PRGA(S, len(ciphertext)))
        ciphertext = np.array([ord(i) for i in ciphertext])

        decoded = keystream ^ ciphertext
        dtext = ''
        for c in decoded:
            dtext = dtext + chr(c)
        return dtext

    def embed(self, frame):
        data = sd.askstring("Ask data", prompt="Enter the data to be Encoded in Video :")
        data = self.encryption(data)
        print("The encrypted data is : ", data)
        if len(data) == 0:
            raise ValueError('Data entered to be encoded is empty')

        data += '*^*^*'

        binary_data = self.msgtobinary(data)
        length_data = len(binary_data)

        index_data = 0

        for i in frame:
            for pixel in i:
                r, g, b = self.msgtobinary(pixel)
                if index_data < length_data:
                    pixel[0] = int(r[:-1] + binary_data[index_data], 2)
                    index_data += 1
                if index_data < length_data:
                    pixel[1] = int(g[:-1] + binary_data[index_data], 2)
                    index_data += 1
                if index_data < length_data:
                    pixel[2] = int(b[:-1] + binary_data[index_data], 2)
                    index_data += 1
                if index_data >= length_data:
                    break
        return frame

    def extract(self, frame):
        data_binary = ""
        final_decoded_msg = ""
        for i in frame:
            for pixel in i:
                r, g, b = self.msgtobinary(pixel)
                data_binary += r[-1]
                data_binary += g[-1]
                data_binary += b[-1]

                if len(data_binary) >= 1000:
                    break

                total_bytes = [data_binary[i: i + 8] for i in range(0, len(data_binary), 8)]
                decoded_data = ""
                for byte in total_bytes:
                    decoded_data += chr(int(byte, 2))
                    if decoded_data[-5:] == "*^*^*":
                        for i in range(0, len(decoded_data) - 5):
                            final_decoded_msg += decoded_data[i]
                        decrypted_msg = self.decryption(final_decoded_msg)
                        return decrypted_msg

    def encode_vid_data(self, file_path):
        print(os.getcwd())
        cap = cv2.VideoCapture(file_path)
        vidcap = cv2.VideoCapture(file_path)
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        frame_width = int(vidcap.get(3))
        frame_height = int(vidcap.get(4))

        size = (frame_width, frame_height)
        if not os.path.exists("./temp"):
            os.makedirs("temp")
        fps = vidcap.get(cv2.CAP_PROP_FPS)
        out = cv2.VideoWriter('temp/Output_video.mp4', fourcc, fps, size)
        max_frame = 0
        while cap.isOpened():
            ret, frame = cap.read()
            if ret == False:
                break
            max_frame += 1
        cap.release()

        frame_number = sd.askinteger("Frame number",
                                     prompt=f'Total number of Frames in selected Video: {max_frame} \nEnter the frame '
                                            f'number where you want to embed data :', minvalue=0, maxvalue=max_frame)
        frame_count = 0

        while vidcap.isOpened():
            frame_count += 1
            ret, frame = vidcap.read()
            if ret == False:
                break
            if frame_count == frame_number:
                change_frame_with = self.embed(frame)
                frame_ = change_frame_with
                frame = change_frame_with
                if not os.path.exists("./data"):
                    os.makedirs("data")
                with open("data/frame_data.pkl", "wb") as file:
                    pickle.dump(frame_, file)
            out.write(frame)
        return frame_

    def decode_vid_data(self, file_path):
        cap = cv2.VideoCapture(file_path)
        max_frame = 0
        while cap.isOpened():
            ret, frame = cap.read()
            if ret == False:
                break
            max_frame += 1
        frame_number = sd.askinteger("Frame number",
                                     prompt=f'Total number of Frames in selected Video: {max_frame} \nEnter the frame '
                                            f'number where you want to extract data :', minvalue=0, maxvalue=max_frame)
        vidcap = cv2.VideoCapture(file_path)
        frame_count = 0

        while vidcap.isOpened():
            frame_count += 1
            ret, frame = vidcap.read()
            if not ret or frame_count > frame_number:
                break
            if frame_count == frame_number:
                with open("data/frame_data.pkl", "rb") as file:
                    frame_ = pickle.load(file)
                frame = self.extract(frame_)
                return frame

        cap.release()
        cv2.destroyAllWindows()

        print("Invalid frame number. Extraction failed.")

    def clean_temp(self, path=".\\temp"):
        if os.path.exists(path):
            shutil.rmtree(path)

    def transfer_sound(self, file_path, file_path_out):
        file_path = file_path.replace("/", "\\")
        file_path_out = file_path_out.replace("/", "\\")
        if os.path.isfile("Output_video.mp4"):
            os.remove("Output_video.mp4")
        ffmpeg_command = ["ffmpeg", "-i", file_path, "-vn", "-acodec", "copy", "audio.aac"]
        subprocess.run(ffmpeg_command, capture_output=True)

        ffmpeg_command = ["ffmpeg", "-i", "audio.aac", "-vn", "-acodec", "aac", "-ab", "128k", "output.aac"]
        subprocess.run(ffmpeg_command, capture_output=True)

        ffmpeg_command = ["ffmpeg", "-i", "temp/Output_video.mp4", "-i", "output.aac", "-c:v", "copy", "-c:a", "aac",
                          "-b:a", "128k", file_path_out]
        subprocess.run(ffmpeg_command, capture_output=True)

        os.remove("audio.aac")
        os.remove("output.aac")
        self.clean_temp()

    global_frame = None

    def set_frame(self, frame):
        global global_frame
        global_frame = frame

    def get_frame(self):
        global global_frame
        return global_frame
