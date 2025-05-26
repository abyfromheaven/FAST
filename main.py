import customtkinter as ctk
from gui import setup_gui

def main():
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")
    root = ctk.CTk()
    root.title("FaceSentri - Absensi Berbasis Wajah")
    root.geometry("800x600")
    setup_gui(root)
    root.mainloop()

if __name__ == "__main__":
    main()
