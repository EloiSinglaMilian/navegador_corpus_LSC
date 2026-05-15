import os
import csv


def get_metadata(adress: str) -> dict:
    metadata_list = []
    if not os.path.exists(adress):
        return {}

    with open(adress, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter=";")
        for row in reader:
            clean_row = {
                k: v for k, v in row.items() if k and not k.startswith("Unnamed")
            }
            if not any(clean_row.values()):
                continue

            for col in ["Etiquetes", "adreca_html", "Incrustació_logotips"]:
                if col in clean_row:
                    del clean_row[col]

            for col in ("Activitat", "lloc_de_gravacio", "Id"):
                if col in clean_row and clean_row[col]:
                    try:
                        val_str = clean_row[col].replace(",", ".")
                        val = int(float(val_str))
                        if col == "lloc_de_gravacio" and val >= 9:
                            val -= 1
                        clean_row[col] = str(val)
                    except:
                        pass

            if clean_row.get("YouTube_logotips"):
                metadata_list.append(clean_row)

    seen = set()
    unique_metadata = []
    for row in metadata_list:
        row_tuple = tuple(sorted(row.items()))
        if row_tuple not in seen:
            seen.add(row_tuple)
            unique_metadata.append(row)

    duration_map = {}
    durada_file = "durada.csv"
    if os.path.exists(durada_file):
        with open(durada_file, mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                duration_map[row["YouTube_logotips"]] = row.get("Durada_segons", 0)

    def format_duration(seconds):
        try:
            s = int(float(seconds))
            if s <= 0:
                return "0:00"
            m, s = divmod(s, 60)
            return f"{m}:{s:02d}"
        except:
            return "0:00"

    final_metadata = {}
    id_counts = {}

    for row in unique_metadata:
        yt_url = row.get("YouTube_logotips")
        row["Durada_segons"] = duration_map.get(yt_url, 0)
        row["length"] = format_duration(row["Durada_segons"])

        row["Gènere discursiu"] = tuple(
            x.strip() for x in row.get("Gènere discursiu", "").split(",")
        )

        base_id = str(row.get("Id", "0"))
        id_counts[base_id] = id_counts.get(base_id, 0) + 1
        count = id_counts[base_id]

        key = base_id if count == 1 else f"{base_id}.{count-1}"

        final_metadata[key] = row

    return final_metadata


def select(metadata: dict, parameters: list[tuple[str, tuple[str]]]) -> dict:
    d = dict()
    for k, v in metadata.items():
        for field, values in parameters:
            if field == "Gènere discursiu":
                if not any(value in v["Gènere discursiu"] for value in values):
                    break
            elif not any(value == v.get(field) for value in values):
                break
        else:
            d[k] = v
    return d
