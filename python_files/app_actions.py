import urllib.request
import io
from PIL import Image, ImageTk
import tkinter as tk
from tkinter import ttk
import webbrowser
from config_utils import SUB_FILES_PATH
from process_CSV import select
import os


def on_video_select(self, event):
    sel = self.video_tree.selection()
    if sel:
        self.selected_video_id = self.filtered_indices[int(sel[0])]
        d = self.metadata[self.selected_video_id]

        for k, en in self.meta_labels.items():
            v = d.get(k, "N/A")
            t = ", ".join(v) if isinstance(v, tuple) else str(v)

            if k == "Activitat" and t != "N/A":
                for full_text in self.act_filters.keys():
                    if full_text.startswith(f"{t} - "):
                        t = full_text
                        break

            elif k == "lloc_de_gravacio" and t != "N/A":
                for full_text in self.loc_filters.keys():
                    if full_text.startswith(f"{t} - "):
                        t = full_text
                        break

            en.config(state="normal")
            en.delete(0, tk.END)
            en.insert(0, t)
            en.config(state="readonly")

        self.stop_video()
        self.update_thumbnail(d.get("YouTube_logotips", ""))


def update_thumbnail(self, url):
    try:
        v_id = (
            url.split("/")[-1]
            if "youtu.be" in url
            else url.split("v=")[-1].split("&")[0]
        )
        with urllib.request.urlopen(
            f"https://img.youtube.com/vi/{v_id}/hqdefault.jpg"
        ) as u:
            im = Image.open(io.BytesIO(u.read()))
            im.thumbnail((450, 350))
            ph = ImageTk.PhotoImage(im)
            self.thumbnail_label.config(image=ph, text="")
            self.thumbnail_label.image = ph
    except:
        self.thumbnail_label.config(image="", text="Error miniatura")


def open_url(self):
    u = self.meta_labels.get("YouTube_logotips").get()
    if u and u != "-":
        webbrowser.open(u)


def reset_filters(self):
    self.search_var.set("")
    for f in [
        self.subs_filter_dict,
        self.age_filters,
        self.loc_filters,
        self.act_filters,
        self.gen_filters,
        self.date_filters,
    ]:
        [v.set(False) for v in f.values()]
    self.refresh_list()


def refresh_list(self):
    p = []
    mapping = [
        ("grup_edat", self.age_filters),
        ("lloc_de_gravacio", self.loc_filters),
        ("Activitat", self.act_filters),
        ("Gènere discursiu", self.gen_filters),
        ("data_enregistrament", self.date_filters),
    ]
    for f, d in mapping:
        s = [
            k.split(" - ")[0] if f in ("Activitat", "lloc_de_gravacio") else k
            for k, v in d.items()
            if v.get()
        ]
        if s:
            p.append((f, tuple(s)))
    c = select(self.metadata, p) if p else self.metadata
    q = self.search_var.get().lower()
    self.filtered_indices = [
        idx for idx, info in c.items() if q in info["Nom_fitxer"].lower()
    ]
    self.filtered_indices.sort(key=lambda x: self.metadata[x]["Nom_fitxer"])
    if self.subs_filter_dict["Només amb arxiu .eaf"].get():
        self.filtered_indices = [
            idx
            for idx in self.filtered_indices
            if os.path.exists(
                os.path.join(SUB_FILES_PATH, f"{self.metadata[idx]['Nom_fitxer']}.ass")
            )
        ]
    self.video_tree.delete(*self.video_tree.get_children())
    for i, idx in enumerate(self.filtered_indices):
        m = self.metadata[idx]
        nom = m["Nom_fitxer"]
        has_eaf = os.path.exists(os.path.join(SUB_FILES_PATH, f"{nom}.ass"))
        e_mk = "✓" if has_eaf else ""
        c_mk = ("☑" if nom in self.videos_per_cerca else "☐") if has_eaf else ""
        self.video_tree.insert(
            "",
            tk.END,
            iid=str(i),
            values=(nom, m.get("length", "0:00"), e_mk, c_mk),
        )
    self.counter_var.set(f"Vídeos: {len(self.filtered_indices)}/{len(self.metadata)}")


def go_to_video(self, video_name, timestamp_ms):
    target_id = next(
        (
            vid_id
            for vid_id, info in self.metadata.items()
            if info["Nom_fitxer"] == video_name
        ),
        None,
    )
    if target_id is not None:
        self.notebook.select(self.tab1)
        for item in self.video_tree.get_children():
            if self.video_tree.item(item, "values")[0] == video_name:
                self.video_tree.selection_set(item)
                self.video_tree.see(item)
                self.selected_video_id = target_id
                break
        self.root.after(
            100, lambda: self.load_video_to_player(start_time=(timestamp_ms / 1000))
        )


def update_tab2_list(self):
    if getattr(self, "is_searching", False):
        return

    if not hasattr(self, "current_pre_page"):
        self.current_pre_page = 0

    for widget in self.v_search_scrollable_frame.winfo_children():
        widget.destroy()

    self.video_widgets = {}

    if not getattr(self, "videos_per_cerca", None):
        msg = ttk.Label(
            self.v_search_scrollable_frame,
            text="Selecciona vídeos a l'explorador per començar",
            font=("TkDefaultFont", 10, "italic"),
            foreground="gray",
            padding=50,
        )
        msg.pack(expand=True)
        self.current_pre_page = 0
        return

    videos_list = sorted(list(self.videos_per_cerca))
    items_per_page = 2
    total_pages = (len(videos_list) - 1) // items_per_page + 1

    if self.current_pre_page >= total_pages:
        self.current_pre_page = max(0, total_pages - 1)

    start_idx = self.current_pre_page * items_per_page
    end_idx = start_idx + items_per_page

    for video_name in videos_list[start_idx:end_idx]:
        self.create_video_strip(video_name)

    self.draw_pre_search_pagination(total_pages)
