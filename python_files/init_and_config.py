import os
import json
from datetime import datetime
import tkinter as tk
from tkinter import ttk
from config_utils import EAF_ORIGINAL_PATH, EAF_TEMP_PATH, SUB_FILES_PATH, CONFIG_PATH, ICON_PATH
from process_CSV import get_metadata
from config_utils import get_resource_path
from helpers import (
    clear_temporary_elan,
    standardize_elan,
    standardize_names,
    generate_subtitles,
)

try:
    import mpv
except OSError:
    mpv = None

TIERS = [
    "Glossa mà activa S1",
    "Glossa mà passiva S1",
    "Glossa mà activa S2",
    "Glossa mà passiva S2",
]


def init_func(self, root):
    self.root = root
    self.root.title("Navegador per al Corpus de la LSC")
    self.root.geometry("1400x900")
    try:
        self.root.state("zoomed")
    except:
        pass

    self.is_fullscreen = False
    self.root.bind("<Escape>", self.exit_fullscreen)

    try:
        internal_base = get_resource_path()
        png_name = "logo.png"
        internal_png_path = os.path.join(internal_base, png_name)
        
        img = tk.PhotoImage(file=internal_png_path)
        root.iconphoto(True, img)
    except Exception as e:
        print(f"Icon failed to load: {e}")

    clear_temporary_elan(EAF_TEMP_PATH)
    self.metadata = get_metadata("metadades_videos.csv")
    standardize_elan(EAF_ORIGINAL_PATH, EAF_TEMP_PATH)
    standardize_names(self.metadata)
    generate_subtitles(EAF_TEMP_PATH, SUB_FILES_PATH, TIERS, False)

    self.dark_mode_var = tk.BooleanVar(value=False)
    self.subs_enabled_var = tk.BooleanVar(value=True)
    self.margin_v_var = tk.IntVar(value=55)
    self.margin_edge_var = tk.IntVar(value=80)
    self.font_size_var = tk.IntVar(value=44)

    self.load_config()

    self.selected_video_id = None
    self.filtered_indices = []
    self.search_var = tk.StringVar()
    self.counter_var = tk.StringVar()
    self.is_seeking = False

    self.videos_per_cerca = set()
    self.video_widgets = {}

    self.show_pos_var = tk.BooleanVar(value=False)
    self.show_time_var = tk.BooleanVar(value=False)
    self.raw_search_query = tk.StringVar()
    self.search_mode_regex = tk.BooleanVar(value=False)
    self.advanced_search_mode = tk.BooleanVar(value=False)

    self.is_searching = False
    self.search_results = []
    self.current_page = 0
    self.results_per_page = 5
    self.page_input_var = tk.StringVar(value="1")

    self.search_s1_var = tk.BooleanVar(value=True)
    self.search_s2_var = tk.BooleanVar(value=True)
    self.search_act_var = tk.BooleanVar(value=True)
    self.search_pas_var = tk.BooleanVar(value=True)

    self.subs_filter_dict = {"Només amb arxiu .eaf": tk.BooleanVar(value=False)}
    self.age_filters = {
        age: tk.BooleanVar(value=False)
        for age in ["18-30 anys", "31-50 anys", "51-80 anys"]
    }
    loc_names = [
        "1 - TERRASSA: Associació de Persones Sordes de Terrassa",
        "2 - LLEIDA: Llar del Sord de Lleida",
        "3 - BLANES: Associació de Persones Sordes de Blanes i La Selva",
        "4 - PALAFRUGELL: Centre de Persones Sordes del Baix Empordà",
        "5 - BARCELONA: Casal de Sords de Barcelona",
        "6 - BARCELONA: Centro Recreativo Cultural de Sordos (CERECUSOR)",
        "7 - VIC: Agrupació de Sords de Vic i Comarca",
        "8 - BARCELONA: Federació de Persones Sordes de Catalunya (FESOCA)",
        "9 - CAMBRILS: Associació de Persones Sordes de Cambrils",
        "10 - BADALONA: Llar de persones sordes de Badalona",
        "11 - MANRESA: Casa social del sord de Manresa i Comarques",
        "12 - MATARÓ: Centre de Persones Sordes del Maresme a Mataró",
    ]
    self.loc_filters = {name: tk.BooleanVar(value=False) for name in loc_names}

    act_names = [
        "1 - Presentació",
        "2 - Narració (granota)",
        "3 - Narració (Silvestre)",
        "4 - Anècdota sordesa",
        "5 - Desc. i expl. (aliments)",
        "6 - Desc. i expl. (cos i colors)",
        "7 - Descripció escena",
        "8 - Explicació vídeo",
        "9 - Debat futur associacions",
    ]
    self.act_filters = {name: tk.BooleanVar(value=False) for name in act_names}
    self.gen_filters = {
        gen: tk.BooleanVar(value=False)
        for gen in ["Narració", "Explicació", "Descripció", "Argumentació"]
    }

    date_list = [
        "30/8/2013",
        "20/9/2016",
        "31/8/2013",
        "1/11/2015",
        "20/11/2024",
        "8/11/2016",
        "3/10/2013",
        "19/2/2023",
        "28/11/2021",
        "23/9/2016",
        "29/10/2016",
        "21/10/2019",
        "25/10/2018",
        "26/6/2015",
        "9/10/2022",
        "20/12/2015",
        "14/11/2021",
        "15/11/2014",
        "14/11/2024",
    ]
    sorted_dates = sorted(
        list(set(date_list)), key=lambda d: datetime.strptime(d, "%d/%m/%Y")
    )
    self.date_filters = {d: tk.BooleanVar(value=False) for d in sorted_dates}

    self.notebook = ttk.Notebook(self.root)
    self.notebook.pack(expand=True, fill="both")
    self.tab1 = ttk.Frame(self.notebook)
    self.tab2 = ttk.Frame(self.notebook)
    self.tab3 = ttk.Frame(self.notebook)
    self.notebook.add(self.tab1, text="Explorador de vídeos")
    self.notebook.add(self.tab2, text="Cercador de contingut")
    self.notebook.add(self.tab3, text="Configuració")

    self.setup_tab1()
    self.setup_tab2()
    self.setup_tab3()

    self.init_mpv()

    if self.dark_mode_var.get():
        self.toggle_dark_mode(save=False)

    self.refresh_list()
    self.poll_progress()
    self.root.protocol("WM_DELETE_WINDOW", self.on_closing)


def load_config(self):
    if os.path.exists(CONFIG_PATH):
        try:
            with open(CONFIG_PATH, "r") as f:
                c = json.load(f)
                self.dark_mode_var.set(c.get("dark_mode", False))
                self.subs_enabled_var.set(c.get("subs_enabled", True))
                self.margin_v_var.set(c.get("margin_v", 55))
                self.margin_edge_var.set(c.get("margin_edge", 80))
                self.font_size_var.set(c.get("font_size", 44))
        except:
            pass


def save_config(self):
    c = {
        "dark_mode": self.dark_mode_var.get(),
        "subs_enabled": self.subs_enabled_var.get(),
        "margin_v": self.margin_v_var.get(),
        "margin_edge": self.margin_edge_var.get(),
        "font_size": self.font_size_var.get(),
    }
    with open(CONFIG_PATH, "w") as f:
        json.dump(c, f, indent=4)


def init_mpv(self):
    if mpv is None:
        print("Error: MPV module not found or failed to load DLL.")
        return
    try:
        self.player = mpv.MPV(
            wid=str(int(self.video_container.winfo_id())),
            ytdl=True,
            input_default_bindings=True,
            input_vo_keyboard=True,
            osc=True,
        )
        self.player["keep-open"] = "yes"
        self.player["sub-visibility"] = "yes" if self.subs_enabled_var.get() else "no"

        @self.player.property_observer("fullscreen")
        def on_fullscreen(name, value):
            if value:
                self.root.after(0, lambda: setattr(self.player, "fullscreen", False))
                if not self.is_fullscreen:
                    self.root.after(0, self.toggle_fullscreen)

    except Exception as e:
        print(f"Error: {e}")
