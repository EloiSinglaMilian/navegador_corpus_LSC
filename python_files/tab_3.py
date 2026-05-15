import os
import tkinter as tk
from tkinter import ttk
from config_utils import EAF_TEMP_PATH


def setup_tab3(self):
    self.tab3.columnconfigure(0, weight=1)
    self.tab3.columnconfigure(1, weight=1)
    self.tab3.rowconfigure(1, weight=1)
    af = ttk.LabelFrame(self.tab3, text="Aparença", padding=15)
    af.grid(row=0, column=0, sticky="ew", padx=20, pady=20)
    ttk.Checkbutton(
        af,
        text="Mode Fosc",
        variable=self.dark_mode_var,
        command=self.toggle_dark_mode,
    ).pack(anchor="w")
    of = ttk.LabelFrame(self.tab3, text="Fitxers EAF sense vídeo", padding=15)
    of.grid(row=1, column=0, columnspan=2, sticky="nsew", padx=20, pady=(0, 20))
    self.orphan_listbox = tk.Listbox(of, font=("Consolas", 10))
    os_sc = ttk.Scrollbar(of, orient="vertical", command=self.orphan_listbox.yview)
    self.orphan_listbox.config(yscrollcommand=os_sc.set)
    os_sc.pack(side="right", fill="y")
    self.orphan_listbox.pack(side="left", fill="both", expand=True)
    ttk.Button(of, text="Actualitzar llista", command=self.check_orphaned_eafs).pack(
        side="bottom", pady=(10, 0)
    )
    self.check_orphaned_eafs()


def check_orphaned_eafs(self):
    self.orphan_listbox.delete(0, tk.END)
    if not os.path.exists(EAF_TEMP_PATH):
        return
    eafs = [
        f.replace(".eaf", "")
        for f in os.listdir(EAF_TEMP_PATH)
        if f.lower().endswith(".eaf")
    ]
    know = [info.get("Nom_fitxer", "") for info in self.metadata.values()]
    orph = sorted([f for f in eafs if f not in know])
    if not orph:
        self.orphan_listbox.insert(tk.END, "✓ Tot correcte!")
    else:
        [self.orphan_listbox.insert(tk.END, f"{o}.eaf") for o in orph]


def toggle_dark_mode(self, save=True):
    if save:
        self.save_config()

    style = ttk.Style()
    is_dark = self.dark_mode_var.get()
    
    bg = "#2b2b2b" if is_dark else "#f0f0f0"
    fg = "#ffffff" if is_dark else "#000000"
    eb = "#3c3f41" if is_dark else "#ffffff"
    active_bg = "#4a6984" if is_dark else "#0078D7"

    if is_dark:
        style.theme_use("clam")
    else:
        style.theme_use("vista")

    style.configure(".", 
        background=bg, 
        foreground=fg, 
        fieldbackground=eb, 
        font=("Segoe UI", 10)
    )

    if is_dark:
        style.map("TCheckbutton",
            background=[('active', bg)],
            foreground=[('active', fg)]
        )
        
        style.configure("TEntry", fieldbackground=eb, foreground=fg, insertcolor="white")
        
        style.configure("Treeview", background=eb, fieldbackground=eb, foreground=fg)
        style.map("Treeview", background=[("selected", active_bg)])
        
        style.configure("TLabelframe", background=bg, foreground=fg)
        style.configure("TLabelframe.Label", background=bg, foreground=fg)

    self.root.tk_setPalette(background=bg, foreground=fg)
    
    self.filter_canvas.config(bg=bg)
    self.v_search_canvas.config(bg=bg)
    self.orphan_listbox.config(bg=eb, fg=fg, borderwidth=1, highlightthickness=0)

    for e in self.meta_labels.values():
        e.config(
            readonlybackground=bg if is_dark else "#f0f0f0",
            fg="cyan" if (is_dark and e.cget("cursor") == "hand2") else ("blue" if e.cget("cursor") == "hand2" else fg),
            bg=eb
        )