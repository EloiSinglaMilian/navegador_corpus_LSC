import os
import tkinter as tk
from tkinter import ttk
from config_utils import EAF_TEMP_PATH, SUB_FILES_PATH, TIERS
from helpers import build_ass
from process_ELAN import get_linearized_data


def setup_tab2(self):
    self.tab2.columnconfigure(0, weight=1)
    self.tab2.rowconfigure(0, weight=0)
    self.tab2.rowconfigure(1, weight=1)

    self.search_params_frame = ttk.LabelFrame(
        self.tab2, text="Paràmetres de cerca", padding=10
    )
    self.search_params_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=5)

    mode_switcher = ttk.Frame(self.search_params_frame)
    mode_switcher.pack(fill="x", pady=(0, 10))
    ttk.Button(
        mode_switcher,
        text="Cerca lliure (text)",
        command=lambda: self.switch_search_mode(False),
    ).pack(side="left", padx=5)
    ttk.Button(
        mode_switcher,
        text="Cerca per tokens (avançada)",
        command=lambda: self.switch_search_mode(True),
    ).pack(side="left", padx=5)

    self.search_input_container = ttk.Frame(self.search_params_frame)
    self.search_input_container.pack(fill="x", pady=5)
    self.draw_raw_search_ui()

    tier_filter_frame = ttk.Frame(self.search_params_frame)
    tier_filter_frame.pack(fill="x", pady=5)
    ttk.Label(
        tier_filter_frame,
        text="Filtre de carrils:",
        font=("TkDefaultFont", 9, "bold"),
    ).pack(side="left", padx=(0, 10))
    ttk.Checkbutton(tier_filter_frame, text="S1", variable=self.search_s1_var).pack(
        side="left", padx=5
    )
    ttk.Checkbutton(tier_filter_frame, text="S2", variable=self.search_s2_var).pack(
        side="left", padx=5
    )
    ttk.Separator(tier_filter_frame, orient="vertical").pack(
        side="left", fill="y", padx=10
    )
    ttk.Checkbutton(
        tier_filter_frame, text="Activa", variable=self.search_act_var
    ).pack(side="left", padx=5)
    ttk.Checkbutton(
        tier_filter_frame, text="Passiva", variable=self.search_pas_var
    ).pack(side="left", padx=5)

    btn_box = ttk.Frame(self.search_params_frame)
    btn_box.pack(fill="x", pady=(10, 0))
    ttk.Button(btn_box, text="🔍 Executar Cerca", command=self.execute_search).pack(
        side="left", padx=5
    )
    ttk.Button(btn_box, text="🗑️ Netejar resultats", command=self.clear_search).pack(
        side="left", padx=5
    )

    self.content_viewer_frame = ttk.LabelFrame(
        self.tab2, text="Visualitzador de contingut", padding=10
    )
    self.content_viewer_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=5)

    self.controls_bar = ttk.Frame(self.content_viewer_frame)
    self.controls_bar.pack(side="top", fill="x", pady=(0, 5))
    ttk.Checkbutton(
        self.controls_bar,
        text="Mostrar PoS",
        variable=self.show_pos_var,
        style="Toggle.TCheckbutton",
        command=self.force_redraw_strips,
    ).pack(side="left", padx=5)
    ttk.Checkbutton(
        self.controls_bar,
        text="Mostrar temps",
        variable=self.show_time_var,
        style="Toggle.TCheckbutton",
        command=self.force_redraw_strips,
    ).pack(side="left", padx=5)
    style = ttk.Style()
    style.configure("Toggle.TCheckbutton", indicatoron=False, padding=5)

    self.margin_veure_var = tk.StringVar(value="0")

    margin_frame = ttk.Frame(self.controls_bar)
    margin_frame.pack(side="right", padx=(5, 15))

    ttk.Label(margin_frame, text='Marge per a "Veure" (s):').pack(side="left")

    margin_entry = ttk.Entry(
        margin_frame, textvariable=self.margin_veure_var, width=5, justify="center"
    )
    margin_entry.pack(side="left", padx=5)

    self.pagination_frame = ttk.Frame(self.content_viewer_frame)

    self.pagination_center_box = ttk.Frame(self.pagination_frame)
    self.pagination_center_box.pack(expand=True)

    self.prev_btn = ttk.Button(
        self.pagination_center_box, text="← Anterior", command=self.prev_page
    )
    self.next_btn = ttk.Button(
        self.pagination_center_box, text="Següent →", command=self.next_page
    )

    jump_frame = ttk.Frame(self.pagination_center_box)
    ttk.Label(jump_frame, text="Pàgina:").pack(side="left")
    self.page_entry = ttk.Entry(
        jump_frame, textvariable=self.page_input_var, width=4, justify="center"
    )
    self.page_entry.pack(side="left", padx=5)
    self.page_entry.bind("<Return>", lambda e: self.jump_to_page())
    self.total_page_label = ttk.Label(
        jump_frame, text="de 0", font=("TkDefaultFont", 9)
    )
    self.total_page_label.pack(side="left", padx=(0, 10))

    self.res_count_label = ttk.Label(
        self.pagination_center_box,
        text="(0 resultats)",
        font=("TkDefaultFont", 8, "italic"),
        width=25,
        anchor="w",
    )

    self.prev_btn.pack(side="left", padx=5)
    jump_frame.pack(side="left", padx=10)
    self.next_btn.pack(side="left", padx=5)
    self.res_count_label.pack(side="left", padx=15)

    self.v_search_canvas = tk.Canvas(self.content_viewer_frame, highlightthickness=0)
    self.v_search_scrollable_frame = ttk.Frame(self.v_search_canvas)
    self.v_search_scrollable_frame.bind(
        "<Configure>",
        lambda e: self.v_search_canvas.configure(
            scrollregion=self.v_search_canvas.bbox("all")
        ),
    )
    self.v_search_canvas_window = self.v_search_canvas.create_window(
        (0, 0), window=self.v_search_scrollable_frame, anchor="nw"
    )

    self.v_search_canvas.bind(
        "<Configure>",
        lambda e: self.v_search_canvas.itemconfig(
            self.v_search_canvas_window, width=e.width
        ),
    )

    self.v_search_canvas.pack(side="top", fill="both", expand=True)

    self.update_tab2_list()


def switch_search_mode(self, is_advanced):
    self.advanced_search_mode.set(is_advanced)
    for widget in self.search_input_container.winfo_children():
        widget.destroy()
    if is_advanced:
        self.draw_token_search_ui()
    else:
        self.draw_raw_search_ui()


def draw_raw_search_ui(self):
    raw_box = ttk.Frame(self.search_input_container)
    raw_box.pack(fill="x")
    ttk.Label(
        raw_box, text="Cerca lliure (text):", font=("TkDefaultFont", 9, "bold")
    ).pack(side="left", padx=(0, 10))
    self.raw_search_entry_widget = ttk.Entry(
        raw_box, textvariable=self.raw_search_query, width=50
    )
    self.raw_search_entry_widget.pack(side="left", fill="x", expand=True)
    self.raw_search_entry_widget.bind("<Return>", lambda e: self.execute_search())
    ttk.Radiobutton(
        raw_box, text="Text pla", variable=self.search_mode_regex, value=False
    ).pack(side="left", padx=5)
    ttk.Radiobutton(
        raw_box, text="RegEx", variable=self.search_mode_regex, value=True
    ).pack(side="left", padx=5)


def draw_token_search_ui(self):
    ttk.Label(
        self.search_input_container,
        text="[Interfície de cerca per tokens - Properament]",
        foreground="gray",
    ).pack(pady=10)


def display_page(self):
    if (
        hasattr(self, "pre_pagination_frame")
        and self.pre_pagination_frame.winfo_exists()
    ):
        self.pre_pagination_frame.pack_forget()

    for widget in self.v_search_scrollable_frame.winfo_children():
        widget.destroy()
    if not self.search_results:
        ttk.Label(
            self.v_search_scrollable_frame,
            text="No s'han trobat coincidències.",
            padding=20,
        ).pack()
        self.pagination_frame.pack_forget()
        return
    self.pagination_frame.pack(side="bottom", fill="x", pady=5)
    total_pages = (len(self.search_results) - 1) // self.results_per_page + 1
    self.total_page_label.config(text=f"de {total_pages}")
    self.page_input_var.set(str(self.current_page + 1))
    self.res_count_label.config(text=f"({len(self.search_results)} resultats)")
    start_idx = self.current_page * self.results_per_page
    end_idx = start_idx + self.results_per_page
    page_items = self.search_results[start_idx:end_idx]
    self.prev_btn.config(state="normal" if self.current_page > 0 else "disabled")
    self.next_btn.config(
        state="normal" if end_idx < len(self.search_results) else "disabled"
    )
    for match in page_items:
        self.create_match_card(match)


def jump_to_page(self):
    try:
        val = int(self.page_input_var.get())
        total_pages = (len(self.search_results) - 1) // self.results_per_page + 1
        if val < 1:
            val = 1
        if val > total_pages:
            val = total_pages
        self.current_page = val - 1
        self.display_page()
        self.v_search_canvas.yview_moveto(0)
    except ValueError:
        self.page_input_var.set(str(self.current_page + 1))


def prev_page(self):
    if self.current_page > 0:
        self.current_page -= 1
        self.display_page()
        self.v_search_canvas.yview_moveto(0)


def next_page(self):
    if (self.current_page + 1) * self.results_per_page < len(self.search_results):
        self.current_page += 1
        self.display_page()
        self.v_search_canvas.yview_moveto(0)


def create_match_card(self, match_data):
    card = ttk.Frame(self.v_search_scrollable_frame, relief="groove", borderwidth=1)
    card.pack(fill="x", padx=10, pady=5)

    header_frame = ttk.Frame(card)
    header_frame.pack(fill="x", padx=10, pady=(5, 0))

    header = f"{match_data['video']} | {match_data['tier']} | {self.format_ms_to_standard(match_data['start'])}"

    header_entry = tk.Entry(
        header_frame,
        font=("TkDefaultFont", 9, "bold"),
        relief="flat",
        highlightthickness=0,
        cursor="xterm",
    )
    header_entry.pack(side="left", fill="x", expand=True)
    header_entry.insert(0, header)

    default_bg = card.winfo_toplevel().cget("bg")
    header_entry.config(state="readonly", readonlybackground=default_bg)

    def on_veure():
        try:
            m_val = self.margin_veure_var.get().replace(",", ".")
            margin_sec = float(m_val) if m_val else 0.0
        except ValueError:
            margin_sec = 0.0

        margin_ms = int(margin_sec * 1000)
        new_start_ms = max(0, match_data["start"] - margin_ms)

        self.go_to_video(match_data["video"], new_start_ms)

    btn = ttk.Button(
        header_frame,
        text="Veure",
        width=8,
        command=on_veure,
    )
    btn.pack(side="right", padx=(10, 0))

    kwic_text = tk.Text(
        card,
        height=1,
        width=180,
        font=("Consolas", 11),
        wrap="none",
        borderwidth=0,
        highlightthickness=0,
        cursor="xterm",
        background=self.root.cget("bg"),
    )
    kwic_text.pack(pady=10, anchor="center")

    kwic_text.tag_configure("center_align", justify="center")
    kwic_text.tag_config("match", foreground="#d9534f", font=("Consolas", 11, "bold"))

    left_str = match_data.get("left_context", "").rjust(89)
    right_str = match_data.get("right_context", "").ljust(89)

    kwic_text.insert("1.0", left_str, "center_align")
    kwic_text.insert("end", match_data["text"], ("match", "center_align"))
    kwic_text.insert("end", right_str, "center_align")

    kwic_text.bind(
        "<KeyPress>",
        lambda e: (
            "break" if e.char and not (e.state & 4) and not (e.state & 8) else None
        ),
    )
    kwic_text.bind("<BackSpace>", lambda e: "break")
    kwic_text.bind("<Delete>", lambda e: "break")


def clear_search(self):
    self.is_searching = False
    self.raw_search_query.set("")
    self.search_results = []
    self.current_page = 0
    self.pagination_frame.pack_forget()
    self.video_widgets = {}
    for widget in self.v_search_scrollable_frame.winfo_children():
        widget.destroy()
    self.update_tab2_list()


def force_redraw_strips(self):
    if not self.is_searching:
        for video_name in list(self.video_widgets.keys()):
            self.video_widgets[video_name].destroy()
            del self.video_widgets[video_name]
        self.update_tab2_list()


def create_video_strip(self, video_name):
    eaf_path = os.path.join(EAF_TEMP_PATH, f"{video_name}.eaf")
    data = get_linearized_data(eaf_path)
    strip_frame = ttk.LabelFrame(
        self.v_search_scrollable_frame, text=video_name, padding=5
    )
    strip_frame.pack(fill="x", pady=5, padx=5, expand=True)
    self.video_widgets[video_name] = strip_frame
    strip_frame.columnconfigure(1, weight=1)
    legend_canvas = tk.Canvas(strip_frame, width=95, height=120, highlightthickness=0)
    legend_canvas.grid(row=0, column=0, sticky="nw")
    labels = [
        ("S1 Activa", 20),
        ("S1 Passiva", 45),
        ("S2 Activa", 70),
        ("S2 Passiva", 95),
    ]
    for text, y in labels:
        legend_canvas.create_text(
            5, y, text=text, anchor="w", font=("TkDefaultFont", 8, "bold")
        )
    h_canvas = tk.Canvas(strip_frame, height=120, bg="#fdfdfd", highlightthickness=1)
    h_scroll = ttk.Scrollbar(strip_frame, orient="horizontal", command=h_canvas.xview)
    h_canvas.configure(xscrollcommand=h_scroll.set)
    h_canvas.grid(row=0, column=1, sticky="nsew")
    h_scroll.grid(row=1, column=1, sticky="ew")
    self.render_glosses_to_strip(h_canvas, data)


def on_subs_slider_release(self, event):
    self.save_config()
    if not self.selected_video_id:
        return
    nom = self.metadata[self.selected_video_id]["Nom_fitxer"]
    e, a = os.path.join(EAF_TEMP_PATH, f"{nom}.eaf"), os.path.join(
        SUB_FILES_PATH, f"{nom}.ass"
    )
    if os.path.exists(e):
        try:
            build_ass(
                e,
                a,
                TIERS,
                "columns",
                self.margin_v_var.get(),
                self.margin_edge_var.get(),
                self.font_size_var.get(),
            )
            if hasattr(self, "player"):
                self.player.command("sub-reload")
        except:
            pass


def on_treeview_click(self, event):
    region = self.video_tree.identify_region(event.x, event.y)
    if region == "cell" and self.video_tree.identify_column(event.x) == "#4":
        item_id = self.video_tree.identify_row(event.y)
        if item_id:
            nom = self.metadata[self.filtered_indices[int(item_id)]]["Nom_fitxer"]
            if os.path.exists(os.path.join(SUB_FILES_PATH, f"{nom}.ass")):
                if nom in self.videos_per_cerca:
                    self.videos_per_cerca.remove(nom)
                else:
                    self.videos_per_cerca.add(nom)
                self.update_treeview_row(item_id, nom)
                self.update_tab2_list()


def update_treeview_row(self, item_id, nom):
    vals = list(self.video_tree.item(item_id, "values"))
    vals[3] = "☑" if nom in self.videos_per_cerca else "☐"
    self.video_tree.item(item_id, values=vals)


def draw_pre_search_pagination(self, total_pages):
    if total_pages <= 1:
        if (
            hasattr(self, "pre_pagination_frame")
            and self.pre_pagination_frame.winfo_exists()
        ):
            self.pre_pagination_frame.pack_forget()
        return

    if (
        not hasattr(self, "pre_pagination_frame")
        or not self.pre_pagination_frame.winfo_exists()
    ):
        self.pre_page_input_var = tk.StringVar()

        self.pre_pagination_frame = ttk.Frame(self.content_viewer_frame)

        self.pre_center_box = ttk.Frame(self.pre_pagination_frame)
        self.pre_center_box.pack(expand=True)

        self.pre_prev_btn = ttk.Button(
            self.pre_center_box, text="← Anterior", command=self.pre_prev_page
        )

        jump_frame = ttk.Frame(self.pre_center_box)
        ttk.Label(jump_frame, text="Pàgina:").pack(side="left")

        self.pre_page_entry = ttk.Entry(
            jump_frame, textvariable=self.pre_page_input_var, width=4, justify="center"
        )
        self.pre_page_entry.pack(side="left", padx=5)
        self.pre_page_entry.bind("<Return>", lambda e: self.pre_jump_to_page())

        self.pre_total_label = ttk.Label(jump_frame, text="", font=("TkDefaultFont", 9))
        self.pre_total_label.pack(side="left", padx=(0, 10))

        self.pre_next_btn = ttk.Button(
            self.pre_center_box, text="Següent →", command=self.pre_next_page
        )

        self.pre_count_label = ttk.Label(
            self.pre_center_box,
            text="",
            font=("TkDefaultFont", 8, "italic"),
            width=25,
            anchor="w",
        )

        self.pre_prev_btn.pack(side="left", padx=5)
        jump_frame.pack(side="left", padx=10)
        self.pre_next_btn.pack(side="left", padx=5)
        self.pre_count_label.pack(side="left", padx=15)

    self.pre_pagination_frame.pack(side="bottom", fill="x", pady=5)

    self.pre_page_input_var.set(str(self.current_pre_page + 1))
    self.pre_total_label.config(text=f"de {total_pages}")

    total_videos = (
        len(self.videos_per_cerca) if hasattr(self, "videos_per_cerca") else 0
    )
    self.pre_count_label.config(text=f"({total_videos} vídeos)")

    self.pre_prev_btn.config(
        state="normal" if self.current_pre_page > 0 else "disabled"
    )
    self.pre_next_btn.config(
        state="normal" if self.current_pre_page < (total_pages - 1) else "disabled"
    )


def pre_jump_to_page(self):
    try:
        val = int(self.pre_page_input_var.get())
        total_videos = (
            len(self.videos_per_cerca) if hasattr(self, "videos_per_cerca") else 0
        )
        items_per_page = 2
        total_pages = (total_videos - 1) // items_per_page + 1

        if val < 1:
            val = 1
        if val > total_pages:
            val = total_pages

        self.current_pre_page = val - 1
        self.update_tab2_list()
        self.v_search_canvas.yview_moveto(0)
    except ValueError:
        self.pre_page_input_var.set(str(self.current_pre_page + 1))


def pre_prev_page(self):
    if self.current_pre_page > 0:
        self.current_pre_page -= 1
        self.update_tab2_list()
        self.v_search_canvas.yview_moveto(0)


def pre_next_page(self):
    self.current_pre_page += 1
    self.update_tab2_list()
    self.v_search_canvas.yview_moveto(0)
