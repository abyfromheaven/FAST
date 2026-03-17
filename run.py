
import os
import sys

# Tambahkan folder 'src' ke dalam path agar bisa diimpor
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from main import App

if __name__ == "__main__":
    app = App()
    app.mainloop()
