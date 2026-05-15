import os
from helpers import build_ass
from config_utils import EAF_TEMP_PATH, SUB_FILES_PATH, TIERS


def toggle_subtitles_visibility(self):
    self.save_config()
    if hasattr(self, "player"):
        self.player["sub-visibility"] = "yes" if self.subs_enabled_var.get() else "no"


def update_sub_delay(self, *args):
    if not hasattr(self, "player") or not self.player:
        return

    try:
        val = self.sub_delay_var.get().replace(",", ".")
        delay_sec = float(val) if val else 0.0
    except ValueError:
        delay_sec = 0.0

    self.player["sub-delay"] = delay_sec
    self.root.focus_set()


def toggle_fullscreen(self, event=None):
    self.is_fullscreen = not self.is_fullscreen
    if self.is_fullscreen:
        self.root.attributes("-fullscreen", True)
        self.notebook.pack_forget()
        self.player_frame.pack_forget()
        self.player_frame.pack(in_=self.root, fill="both", expand=True)
    else:
        self.root.attributes("-fullscreen", False)
        self.player_frame.pack_forget()
        self.notebook.pack(expand=True, fill="both")
        self.player_frame.pack(
            in_=self.right_col,
            side="bottom",
            fill="both",
            expand=True,
            pady=(10, 0),
        )


def exit_fullscreen(self, event=None):
    if getattr(self, "is_fullscreen", False):
        self.toggle_fullscreen()


def format_time(self, seconds):
    if seconds is None or seconds < 0:
        return "00:00:00"
    m, s = divmod(int(seconds), 60)
    h, m = divmod(m, 60)
    cc = int((seconds % 1) * 100)
    return f"{h:02d}:{m:02d}:{s:02d}.{cc:02d}" if h > 0 else f"{m:02d}:{s:02d}.{cc:02d}"


def poll_progress(self):
    if hasattr(self, "player") and getattr(self.player, "time_pos", None) is not None:
        if not self.is_seeking:
            tp, dr = self.player.time_pos, self.player.duration
            if tp and dr:
                self.progress_var.set((tp / dr) * 100)
                self.time_label.config(
                    text=f"{self.format_time(tp)} / {self.format_time(dr)}"
                )
    self.root.after(250, self.poll_progress)


def on_slider_drag(self, val):
    self.is_seeking = True


def on_slider_release(self, event):
    if hasattr(self, "player") and self.player.duration:
        self.player.time_pos = (self.progress_var.get() / 100) * self.player.duration
    self.is_seeking = False


def toggle_pause(self):
    if hasattr(self, "player"):
        self.player.pause = not self.player.pause


def stop_video(self):
    if hasattr(self, "player"):
        self.player.stop()
    self.video_container.pack_forget()
    self.thumbnail_label.pack(fill="both", expand=True)
    self.progress_var.set(0)
    self.time_label.config(text="00:00.00 / 00:00.00")


def cycle_speed(self):
    if hasattr(self, "player"):
        s = [1.0, 1.25, 1.5, 2.0, 2.5, 3.0, 0.5, 0.75]
        n = s[(s.index(self.player.speed or 1.0) + 1) % len(s)]
        self.player.speed = n
        self.speed_label.config(text=f"{n}x")


def load_video_to_player(self, start_time):
    if not self.selected_video_id:
        return
        
    self.thumbnail_label.pack_forget()
    self.video_container.pack(fill="both", expand=True)
    
    m = self.metadata[self.selected_video_id]
    nom = m["Nom_fitxer"]
    e = os.path.join(EAF_TEMP_PATH, f"{nom}.eaf")
    a = os.path.join(SUB_FILES_PATH, f"{nom}.ass")
    
    if os.path.exists(e):
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
        self.player.start = str(start_time)
        self.player.play(m["YouTube_logotips"])
        self.player["sub-visibility"] = (
            "yes" if self.subs_enabled_var.get() else "no"
        )
        
        if os.path.exists(a):
            self.player.command("sub-add", a, "select")
