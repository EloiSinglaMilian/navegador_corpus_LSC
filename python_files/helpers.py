import subprocess
import os
import re
import shutil
from process_ELAN import build_ass


def play_video(idx, metadata, sub_files_path, start="0", end="9999999"):
    d = metadata[idx]
    url = d["YouTube_logotips"]
    name = d["Nom_fitxer"]

    full_subs_path = os.path.join(sub_files_path, f"{name}.ass")
    if os.path.isfile(full_subs_path):
        subs = full_subs_path
    else:
        subs = None

    subprocess.run(
        [
            "mpv.exe",
            url,
            f"--start={start}",
            f"--end={end}",
            f"--sub-file={subs}",
        ]
    )


def clear_temporary_elan(eaf_files_path):
    for file in os.listdir(eaf_files_path):
        file_path = os.path.join(eaf_files_path, file)
        os.remove(file_path)


def get_standard_string(input_string):
    clean_name = os.path.splitext(input_string)[0].upper()
    clean_name = clean_name.replace("CORPUES", "CORPUS")
    clean_name = clean_name.replace("DIALOGO", "")

    tokens = re.findall(r"[A-Z]+|\d+", clean_name)
    official_id = ""

    for t in tokens:
        if t.isdigit():
            digits_1_9 = re.findall(r"[1-9]", t)
            if digits_1_9:
                official_id = f"0000{digits_1_9[-1]}"
                break

    final_suffixes = []
    forbidden_standalone = ["C", "L", "G"]

    for t in tokens:
        if t == "CORPUS" or t.isdigit():
            continue
        if t in ["A", "B"]:
            if official_id:
                official_id += t
            continue
        if t in forbidden_standalone:
            continue
        final_suffixes.append(t)
    
    final_suffixes.sort()
    parts = ["CORPUS"]

    if official_id:
        parts.append(official_id)
    if final_suffixes:
        parts.extend(final_suffixes)

    result = " ".join(parts)

    hardcoding = {
        "CORPUS 00008 BN": "CORPUS 00008 BN CS",
        "CORPUS 00005B BN": "CORPUS 00005B BN CS",
        "CORPUS 00005B DU": "CORPUS 00005B DU KW",
        "CORPUS 00005B FN": "CORPUS 00005B BQ FN",
        "CORPUS 00006 BQ": "CORPUS 00006 BQ FN",
        "CORPUS 00006 CG": "CORPUS 00006 CG QF",
    }

    if result in hardcoding:
        result = hardcoding[result]

    return result


def standardize_elan(original_dir, target_dir):
    for filename in os.listdir(original_dir):
        if filename.lower().endswith(".eaf"):
            new_name = get_standard_string(filename) + ".eaf"
            shutil.copy2(
                os.path.join(original_dir, filename), os.path.join(target_dir, new_name)
            )


def standardize_names(metadata):
    for v in metadata.values():
        v["Nom_fitxer"] = get_standard_string(v["Nom_fitxer"])


def generate_subtitles(eaf_files_path, sub_files_path, tiers, regenerate):
    for file in os.listdir(eaf_files_path):
        name = file.removesuffix(".eaf")
        if name + ".ass" in os.listdir(sub_files_path) and not regenerate:
            continue
        full_eaf_path = os.path.join(eaf_files_path, file)
        full_sub_path = os.path.join(sub_files_path, name + ".ass")
        build_ass(full_eaf_path, full_sub_path, tiers, "columns")


def check_missing(metadata, eaf_files_path):
    names = [v["Nom_fitxer"] + ".eaf" for k, v in metadata.items()]

    no_ELAN_file = [n for n in names if n not in os.listdir(eaf_files_path)]
    no_metadata = [file for file in os.listdir(eaf_files_path) if file not in names]

    return no_ELAN_file, no_metadata
