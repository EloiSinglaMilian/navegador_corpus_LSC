import config_utils
import tkinter as tk
from app_logic import CorpusApp
import ctypes

def main():
    myappid = 'navegador.corpus.lsc.v1.0'
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

    root = tk.Tk()
    app = CorpusApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
