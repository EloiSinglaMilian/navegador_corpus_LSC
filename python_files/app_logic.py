from config_utils import EAF_TEMP_PATH
from helpers import clear_temporary_elan
from init_and_config import init_func, load_config, save_config, init_mpv
from tab_1 import (
    setup_tab1,
    on_mousewheel,
    on_search_mousewheel,
    select_all_visible,
    deselect_all_visible,
    add_filter_stack,
    add_filter_grid_stack,
    treeview_sort_column,
)
from tab_2 import (
    setup_tab2,
    switch_search_mode,
    draw_raw_search_ui,
    draw_token_search_ui,
    display_page,
    jump_to_page,
    prev_page,
    next_page,
    create_match_card,
    clear_search,
    force_redraw_strips,
    create_video_strip,
    on_subs_slider_release,
    on_treeview_click,
    update_treeview_row,
    draw_pre_search_pagination,
    pre_next_page,
    pre_prev_page,
    pre_jump_to_page,
)
from tab_3 import setup_tab3, check_orphaned_eafs, toggle_dark_mode
from search_engine import execute_search, render_glosses_to_strip, format_ms_to_standard
from video_controls import (
    toggle_subtitles_visibility,
    toggle_pause,
    toggle_fullscreen,
    exit_fullscreen,
    format_time,
    poll_progress,
    on_slider_drag,
    on_slider_release,
    stop_video,
    cycle_speed,
    load_video_to_player,
    update_sub_delay,
)
from app_actions import (
    on_video_select,
    update_thumbnail,
    refresh_list,
    open_url,
    reset_filters,
    go_to_video,
    update_tab2_list,
)


class CorpusApp:
    def __init__(self, root):
        init_func(self, root)

    def load_config(self):
        return load_config(self)

    def save_config(self):
        return save_config(self)

    def init_mpv(self):
        return init_mpv(self)

    def setup_tab1(self):
        return setup_tab1(self)

    def _on_mousewheel(self, event):
        return on_mousewheel(self, event)

    def _on_search_mousewheel(self, event):
        return on_search_mousewheel(self, event)

    def select_all_visible(self):
        return select_all_visible(self)

    def deselect_all_visible(self):
        return deselect_all_visible(self)

    def setup_tab2(self):
        return setup_tab2(self)

    def switch_search_mode(self, is_advanced):
        return switch_search_mode(self, is_advanced)

    def draw_raw_search_ui(self):
        return draw_raw_search_ui(self)

    def draw_token_search_ui(self):
        return draw_token_search_ui(self)

    def execute_search(self):
        return execute_search(self)

    def display_page(self):
        return display_page(self)

    def jump_to_page(self):
        return jump_to_page(self)

    def prev_page(self):
        return prev_page(self)

    def next_page(self):
        return next_page(self)

    def draw_pre_search_pagination(self, total_pages):
        return draw_pre_search_pagination(self, total_pages)

    def pre_prev_page(self):
        return pre_prev_page(self)

    def pre_next_page(self):
        return pre_next_page(self)

    def pre_jump_to_page(self):
        return pre_jump_to_page(self)

    def create_match_card(self, match_data):
        return create_match_card(self, match_data)

    def go_to_video(self, video_name, timestamp_ms):
        return go_to_video(self, video_name, timestamp_ms)

    def clear_search(self):
        return clear_search(self)

    def force_redraw_strips(self):
        return force_redraw_strips(self)

    def update_tab2_list(self):
        return update_tab2_list(self)

    def create_video_strip(self, video_name):
        return create_video_strip(self, video_name)

    def format_ms_to_standard(self, ms):
        return format_ms_to_standard(self, ms)

    def render_glosses_to_strip(self, canvas, data):
        return render_glosses_to_strip(self, canvas, data)

    def on_subs_slider_release(self, event):
        return on_subs_slider_release(self, event)

    def on_treeview_click(self, event):
        return on_treeview_click(self, event)

    def update_treeview_row(self, item_id, nom):
        return update_treeview_row(self, item_id, nom)

    def setup_tab3(self):
        return setup_tab3(self)

    def check_orphaned_eafs(self):
        check_orphaned_eafs(self)

    def toggle_dark_mode(self, save=True):
        return toggle_dark_mode(self, save)

    def toggle_subtitles_visibility(self):
        return toggle_subtitles_visibility(self)

    def update_sub_delay(self, *args):
        return update_sub_delay(self, *args)

    def toggle_fullscreen(self, event=None):
        return toggle_fullscreen(self, event)

    def exit_fullscreen(self, event=None):
        return exit_fullscreen(self, event)

    def format_time(self, seconds):
        return format_time(self, seconds)

    def poll_progress(self):
        return poll_progress(self)

    def on_slider_drag(self, val):
        return on_slider_drag(self, val)

    def on_slider_release(self, event):
        return on_slider_release(self, event)

    def toggle_pause(self):
        return toggle_pause(self)

    def stop_video(self):
        return stop_video(self)

    def cycle_speed(self):
        return cycle_speed(self)

    def load_video_to_player(self, start_time=0):
        return load_video_to_player(self, start_time)

    def on_video_select(self, event):
        return on_video_select(self, event)

    def update_thumbnail(self, url):
        return update_thumbnail(self, url)

    def open_url(self):
        return open_url(self)

    def add_filter_stack(self, p, t, d, c):
        return add_filter_stack(self, p, t, d, c)

    def add_filter_grid_stack(self, p, t, d, c, cl):
        return add_filter_grid_stack(self, p, t, d, c, cl)

    def reset_filters(self):
        return reset_filters(self)

    def treeview_sort_column(self, col, reverse):
        return treeview_sort_column(self, col, reverse)

    def refresh_list(self):
        return refresh_list(self)

    def on_closing(self):
        if hasattr(self, "player"):
            self.player.terminate()
        clear_temporary_elan(EAF_TEMP_PATH)
        self.root.destroy()
