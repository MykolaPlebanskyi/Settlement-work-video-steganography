import tkinter as tk

from App import VideoSteganographyApp


def main():
    root = tk.Tk()
    app = VideoSteganographyApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
