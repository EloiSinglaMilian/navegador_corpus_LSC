import os
import re
from tkinter import messagebox
from config_utils import EAF_TEMP_PATH
from process_ELAN import get_linearized_data


def execute_search(self):
    if not self.videos_per_cerca:
        messagebox.showwarning("Atenció", "Selecciona vídeos a l'explorador primer.")
        return

    query = self.raw_search_query.get().strip()
    if not query:
        self.clear_search()
        return

    self.is_searching = True
    self.search_results = []
    self.current_page = 0

    allowed_speakers = [s for s, v in [("S1", self.search_s1_var), ("S2", self.search_s2_var)] if v.get()]
    allowed_hands = [h for h, v in [("activa", self.search_act_var), ("passiva", self.search_pas_var)] if v.get()]

    try:
        flags = re.IGNORECASE
        pattern = re.compile(
            query if self.search_mode_regex.get() else re.escape(query),
            flags,
        )
    except:
        messagebox.showerror("Error", "RegEx no vàlida")
        return

    for video_name in sorted(list(self.videos_per_cerca)):
        eaf_path = os.path.join(EAF_TEMP_PATH, f"{video_name}.eaf")
        all_tokens = get_linearized_data(eaf_path)

        for speaker in allowed_speakers:
            for hand in allowed_hands:
                tier_tokens = [
                    t for t in all_tokens 
                    if t["speaker"] == speaker and t["hand"] == hand
                ]
                
                tier_tokens.sort(key=lambda x: x["start"])

                if not tier_tokens:
                    continue

                full_text = " ".join([t["gloss"] for t in tier_tokens])
                
                char_to_token = []
                curr = 0
                for i, t in enumerate(tier_tokens):
                    char_to_token.append((curr, curr + len(t["gloss"]), i))
                    curr += len(t["gloss"]) + 1

                for m in pattern.finditer(full_text):
                    match_tokens = [
                        tier_tokens[idx]
                        for ts, te, idx in char_to_token
                        if m.start() < te and m.end() > ts
                    ]
                    
                    if match_tokens:
                        context_size = 85
                        start_idx = max(0, m.start() - context_size)
                        end_idx = min(len(full_text), m.end() + context_size)

                        left_context = full_text[start_idx : m.start()]
                        if start_idx > 0: left_context = "..." + left_context

                        right_context = full_text[m.end() : end_idx]
                        if end_idx < len(full_text): right_context += "..."

                        self.search_results.append({
                            "video": video_name,
                            "start": match_tokens[0]["start"],
                            "text": m.group(),
                            "left_context": left_context,
                            "right_context": right_context,
                            "tier": f"{speaker} {hand}",
                        })

    self.display_page()


def render_glosses_to_strip(self, canvas, data):
    x_offset = 15
    tier_y = {
        ("S1", "activa"): 20,
        ("S1", "passiva"): 45,
        ("S2", "activa"): 70,
        ("S2", "passiva"): 95,
    }
    show_p, show_t = self.show_pos_var.get(), self.show_time_var.get()
    for token in data:
        y = tier_y.get((token["speaker"], token["hand"]), 20)
        base = token["gloss"]
        extra = []
        if show_p:
            extra.append(token["pos"])
        if show_t:
            extra.append(self.format_ms_to_standard(token["start"]))
        disp = f"{base} ({'/'.join(extra)})" if extra else base
        tid = canvas.create_text(
            x_offset, y, text=disp, anchor="nw", font=("Consolas", 9)
        )
        bbox = canvas.bbox(tid)
        if bbox:
            x_offset = bbox[2] + 25
    canvas.config(scrollregion=(0, 0, x_offset + 100, 120))


def format_ms_to_standard(self, ms):
    m = ms // 60000
    s = (ms % 60000) // 1000
    c = (ms % 1000) // 10
    return f"{m:02d}:{s:02d}.{c:02d}"
