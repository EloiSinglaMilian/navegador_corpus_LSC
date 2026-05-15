import tkinter as tk
from tkinter import ttk
from config_utils import SUB_FILES_PATH
import os


def setup_tab1(self):
    self.tab1.columnconfigure(0, weight=1, uniform="group1")
    self.tab1.columnconfigure(1, weight=1, uniform="group1")
    self.tab1.columnconfigure(2, weight=1, uniform="group1")
    self.tab1.rowconfigure(0, weight=1)

    left_col = ttk.Frame(self.tab1, padding=10)
    left_col.grid(row=0, column=0, sticky="nsew")
    search_frame = ttk.Frame(left_col)
    search_frame.pack(fill="x", pady=(0, 5))
    ttk.Label(search_frame, text="Cerca per nom:").pack(side="left")
    self.search_entry = ttk.Entry(search_frame, textvariable=self.search_var)
    self.search_entry.pack(side="left", fill="x", expand=True, padx=(5, 0))
    self.search_var.trace_add("write", lambda *args: self.refresh_list())

    selection_header = ttk.Frame(left_col)
    selection_header.pack(fill="x", pady=(5, 5))
    ttk.Label(
        selection_header,
        textvariable=self.counter_var,
        font=("TkDefaultFont", 10, "bold"),
    ).pack(side="left")
    btn_sel_frame = ttk.Frame(selection_header)
    btn_sel_frame.pack(side="right")
    ttk.Button(
        btn_sel_frame,
        text="Seleccionar-los tots",
        command=self.select_all_visible,
        style="Small.TButton",
    ).pack(fill="x")
    ttk.Button(
        btn_sel_frame,
        text="Deseleccionar-los tots",
        command=self.deselect_all_visible,
        style="Small.TButton",
    ).pack(fill="x")

    style = ttk.Style()
    style.configure("Small.TButton", font=("TkDefaultFont", 7))

    list_container = ttk.Frame(left_col)
    list_container.pack(fill="both", expand=True, pady=5)
    self.scrollbar = ttk.Scrollbar(list_container, orient="vertical")
    self.video_tree = ttk.Treeview(
        list_container,
        columns=("nom", "durada", "eaf", "cercahi"),
        show="headings",
        selectmode="browse",
    )
    self.video_tree.heading(
        "nom",
        text="Nom del fitxer",
        command=lambda: self.treeview_sort_column("nom", False),
    )
    self.video_tree.heading(
        "durada",
        text="Durada",
        command=lambda: self.treeview_sort_column("durada", False),
    )
    self.video_tree.heading(
        "eaf",
        text="Arxiu .eaf",
        command=lambda: self.treeview_sort_column("eaf", False),
    )
    self.video_tree.heading("cercahi", text="Cerca-hi")
    self.video_tree.column("nom", width=180, anchor="w")
    self.video_tree.column("durada", width=50, anchor="center")
    self.video_tree.column("eaf", width=70, anchor="center")
    self.video_tree.column("cercahi", width=60, anchor="center")
    self.scrollbar.config(command=self.video_tree.yview)
    self.video_tree.config(yscrollcommand=self.scrollbar.set)
    self.scrollbar.pack(side="right", fill="y")
    self.video_tree.pack(side="left", fill="both", expand=True)
    self.video_tree.bind("<<TreeviewSelect>>", self.on_video_select)
    self.video_tree.bind("<ButtonRelease-1>", self.on_treeview_click)

    self.meta_frame = ttk.LabelFrame(left_col, text="Metadades", padding=10)
    self.meta_frame.pack(side="bottom", fill="x", pady=5)
    self.meta_frame.columnconfigure(1, weight=1)
    self.meta_labels = {}
    fields = [
        ("Nom_fitxer", "Nom:"),
        ("Activitat", "Activitat:"),
        ("lloc_de_gravacio", "Lloc:"),
        ("grup_edat", "Edat:"),
        ("codi_informant", "Informant:"),
        ("Gènere discursiu", "Gènere:"),
        ("data_enregistrament", "Data:"),
        ("length", "Durada:"),
        ("YouTube_logotips", "URL:"),
    ]
    for i, (key, label_text) in enumerate(fields):
        ttk.Label(
            self.meta_frame, text=label_text, font=("TkDefaultFont", 9, "bold")
        ).grid(row=i, column=0, sticky="nw")
        val_entry = tk.Entry(
            self.meta_frame,
            relief="flat",
            readonlybackground=self.root.cget("background"),
            font=("TkDefaultFont", 9),
            width=35,
        )
        if key == "YouTube_logotips":
            val_entry.config(fg="blue", cursor="hand2")
            val_entry.bind("<Button-1>", lambda e: self.open_url())
        val_entry.insert(0, "-")
        val_entry.config(state="readonly")
        val_entry.grid(row=i, column=1, sticky="ew", padx=10)
        self.meta_labels[key] = val_entry

    mid_col_container = ttk.Frame(self.tab1, padding=10)
    mid_col_container.grid(row=0, column=1, sticky="nsew")
    mid_col_container.rowconfigure(0, weight=1)
    mid_col_container.columnconfigure(0, weight=1)

    self.main_filter_frame = ttk.LabelFrame(
        mid_col_container, text="Filtres", padding=10
    )
    self.main_filter_frame.grid(row=0, column=0, sticky="nsew")
    self.main_filter_frame.columnconfigure(0, weight=1)
    self.main_filter_frame.rowconfigure(1, weight=1)

    ttk.Button(
        self.main_filter_frame, text="Netejar Filtres", command=self.reset_filters
    ).pack(side="top", fill="x", pady=(0, 10))

    scroll_container = ttk.Frame(self.main_filter_frame)
    scroll_container.pack(fill="both", expand=True)

    self.filter_canvas = tk.Canvas(scroll_container, highlightthickness=0)
    filter_scroll = ttk.Scrollbar(
        scroll_container, orient="vertical", command=self.filter_canvas.yview
    )
    self.filter_scrollable_frame = ttk.Frame(self.filter_canvas)
    self.filter_scrollable_frame.bind(
        "<Configure>",
        lambda e: self.filter_canvas.configure(
            scrollregion=self.filter_canvas.bbox("all")
        ),
    )
    self.filter_canvas.bind(
        "<Configure>",
        lambda e: self.filter_canvas.itemconfig(self.canvas_window, width=e.width),
    )
    self.canvas_window = self.filter_canvas.create_window(
        (0, 0), window=self.filter_scrollable_frame, anchor="nw"
    )
    self.filter_canvas.configure(yscrollcommand=filter_scroll.set)

    self.filter_canvas.bind(
        "<Enter>", lambda e: self.root.bind_all("<MouseWheel>", self._on_mousewheel)
    )
    self.filter_canvas.bind("<Leave>", lambda e: self.root.unbind_all("<MouseWheel>"))

    filter_scroll.pack(side="right", fill="y")
    self.filter_canvas.pack(side="left", fill="both", expand=True)

    top_grid = ttk.Frame(self.filter_scrollable_frame)
    top_grid.pack(fill="x", pady=2)
    top_grid.columnconfigure(0, weight=1)
    top_grid.columnconfigure(1, weight=1)
    top_grid.rowconfigure(0, weight=1)

    lt_sub = ttk.Frame(top_grid)
    lt_sub.grid(row=0, column=0, sticky="nsew", padx=(0, 2))
    self.add_filter_stack(lt_sub, "Arxiu .eaf", self.subs_filter_dict, "#d8bfd8")
    self.add_filter_stack(lt_sub, "Edat", self.age_filters, "lightblue")

    rt_sub = ttk.Frame(top_grid)
    rt_sub.grid(row=0, column=1, sticky="nsew", padx=(2, 0))
    self.add_filter_stack(rt_sub, "Gènere", self.gen_filters, "#ffcccb")

    self.add_filter_grid_stack(
        self.filter_scrollable_frame, "Activitat", self.act_filters, "#f0e68c", 1
    )
    self.loc_buttons = self.add_filter_grid_stack(
        self.filter_scrollable_frame, "Lloc", self.loc_filters, "lightgreen", 1
    )

    self.add_filter_grid_stack(
        self.filter_scrollable_frame,
        "Data enregistrament",
        self.date_filters,
        "#e1e1e1",
        4,
    )

    self.right_col = ttk.Frame(self.tab1, padding=10)
    self.right_col.grid(row=0, column=2, sticky="nsew")

    self.player_frame = ttk.LabelFrame(self.root, text="Reproductor", padding=5)
    self.player_frame.pack(
        in_=self.right_col, side="top", fill="both", expand=True, pady=(0, 10)
    )
    self.media_container = tk.Frame(self.player_frame, bg="black")
    self.media_container.pack(fill="both", expand=True)
    self.thumbnail_label = ttk.Label(
        self.media_container,
        text="Cap vídeo seleccionat",
        background="black",
        foreground="white",
        anchor="center",
    )
    self.thumbnail_label.pack(fill="both", expand=True)
    self.video_container = tk.Frame(self.media_container, bg="black")

    cp = ttk.Frame(self.player_frame)
    cp.pack(fill="x", pady=5)
    pf = ttk.Frame(cp)
    pf.pack(fill="x", pady=(0, 5))
    self.progress_var = tk.DoubleVar()
    self.progress_slider = ttk.Scale(
        pf,
        variable=self.progress_var,
        from_=0,
        to=100,
        orient="horizontal",
        command=self.on_slider_drag,
    )
    self.progress_slider.pack(side="left", fill="x", expand=True, padx=(0, 10))
    self.progress_slider.bind("<ButtonRelease-1>", self.on_slider_release)
    self.time_label = ttk.Label(pf, text="00:00.00 / 00:00.00", font=("Consolas", 9))
    self.time_label.pack(side="right")

    bf = ttk.Frame(cp)
    bf.pack(fill="x")
    ttk.Button(bf, text="▶ Carregar", command=self.load_video_to_player).pack(
        side="left", padx=2
    )
    ttk.Button(bf, text="▶/⏸ Pausa", command=self.toggle_pause).pack(
        side="left", padx=2
    )
    ttk.Button(bf, text="⏹ Stop", command=self.stop_video).pack(side="left", padx=2)
    ttk.Button(bf, text="Velocitat", command=self.cycle_speed).pack(
        side="left", padx=(10, 2)
    )
    self.speed_label = ttk.Label(bf, text="1.0x")
    self.speed_label.pack(side="left", padx=2)
    ttk.Button(bf, text="Pantalla completa", command=self.toggle_fullscreen).pack(
        side="right", padx=2
    )

    subs_frame = ttk.LabelFrame(self.right_col, text="Ajustos de subtítols", padding=10)
    subs_frame.pack(side="bottom", fill="x", pady=5)

    top_row_frame = ttk.Frame(subs_frame)
    top_row_frame.pack(fill="x", pady=(0, 10))

    self.sub_delay_var = tk.StringVar(value="0")

    ttk.Checkbutton(
        top_row_frame,
        text="Mostrar subtítols",
        variable=self.subs_enabled_var,
        command=self.toggle_subtitles_visibility,
    ).pack(side="left", padx=(0, 25))

    ttk.Label(top_row_frame, text="Retard dels subtítols (s):").pack(side="left")

    delay_entry = ttk.Entry(
        top_row_frame, textvariable=self.sub_delay_var, width=5, justify="center"
    )
    delay_entry.pack(side="left", padx=5)

    delay_entry.bind("<Return>", self.update_sub_delay)
    delay_entry.bind("<FocusOut>", self.update_sub_delay)

    ttk.Label(subs_frame, text="Distància inferior (Vertical):").pack(anchor="w")
    v_scale = ttk.Scale(
        subs_frame,
        from_=0,
        to=1080,
        variable=self.margin_v_var,
        orient="horizontal",
    )
    v_scale.pack(fill="x", pady=(0, 10))
    v_scale.bind("<ButtonRelease-1>", self.on_subs_slider_release)
    ttk.Label(subs_frame, text="Distància lateral (Vora):").pack(anchor="w")
    edge_scale = ttk.Scale(
        subs_frame,
        from_=0,
        to=900,
        variable=self.margin_edge_var,
        orient="horizontal",
    )
    edge_scale.pack(fill="x", pady=(0, 10))
    edge_scale.bind("<ButtonRelease-1>", self.on_subs_slider_release)
    ttk.Label(subs_frame, text="Mida de la lletra:").pack(anchor="w")
    font_scale = ttk.Scale(
        subs_frame,
        from_=10,
        to=150,
        variable=self.font_size_var,
        orient="horizontal",
    )
    font_scale.pack(fill="x")
    font_scale.bind("<ButtonRelease-1>", self.on_subs_slider_release)


def on_mousewheel(self, event):
    self.filter_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")


def on_search_mousewheel(self, event):
    self.v_search_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")


def select_all_visible(self):
    for idx in self.filtered_indices:
        nom = self.metadata[idx]["Nom_fitxer"]
        if os.path.exists(os.path.join(SUB_FILES_PATH, f"{nom}.ass")):
            self.videos_per_cerca.add(nom)
    self.refresh_list()
    self.update_tab2_list()


def deselect_all_visible(self):
    for idx in self.filtered_indices:
        nom = self.metadata[idx]["Nom_fitxer"]
        if nom in self.videos_per_cerca:
            self.videos_per_cerca.remove(nom)
    self.refresh_list()
    self.update_tab2_list()


def add_filter_stack(self, p, t, d, c):
    f = ttk.LabelFrame(p, text=t, padding=5)
    f.pack(fill="both", expand=True, pady=2)
    for tx, v in d.items():
        tk.Checkbutton(
            f,
            text=tx,
            variable=v,
            indicatoron=False,
            command=self.refresh_list,
            selectcolor=c,
            relief="flat",
            borderwidth=1,
        ).pack(fill="x")


def add_filter_grid_stack(self, p, t, d, c, cl):
    f = ttk.LabelFrame(p, text=t, padding=5)
    f.pack(fill="x", pady=2)
    for i in range(cl):
        f.columnconfigure(i, weight=1)
    btns = {}
    for i, (tx, v) in enumerate(d.items()):
        b = tk.Checkbutton(
            f,
            text=tx,
            variable=v,
            indicatoron=False,
            command=self.refresh_list,
            selectcolor=c,
            relief="flat",
            borderwidth=1,
            font=("TkDefaultFont", 8 if cl == 4 else 9),
        )
        b.grid(row=i // cl, column=i % cl, padx=1, pady=1, sticky="nsew")
        btns[tx] = b
    return btns


def treeview_sort_column(self, col, reverse):
    l = [(self.video_tree.set(k, col), k) for k in self.video_tree.get_children("")]
    if col == "durada":

        def t_s(ts):
            try:
                m, s = map(int, ts.split(":"))
                return m * 60 + s
            except:
                return 0

        l.sort(key=lambda x: t_s(x[0]), reverse=reverse)
    else:
        l.sort(reverse=reverse)
    for i, (v, k) in enumerate(l):
        self.video_tree.move(k, "", i)
    self.video_tree.heading(
        col, command=lambda: self.treeview_sort_column(col, not reverse)
    )
