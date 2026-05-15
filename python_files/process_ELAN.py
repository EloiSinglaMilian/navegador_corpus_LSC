import xml.etree.ElementTree as ET
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple


def ms_to_ass_time(ms: int) -> str:
    if ms < 0:
        ms = 0
    cs = ms // 10
    s, cc = divmod(cs, 100)
    m, ss = divmod(s, 60)
    h, mm = divmod(m, 60)
    return f"{h}:{mm:02d}:{ss:02d}.{cc:02d}"


@dataclass
class Ann:
    start_ms: int
    end_ms: int
    value: str


def parse_xml_loose(path: str) -> ET.Element:
    data = open(path, "rb").read()
    if not data:
        raise ValueError("EAF file is empty (0 bytes).")

    i = data.find(b"<")
    if i == -1:
        head = data[:80]
        raise ValueError(
            f"File does not look like XML (no '<' found). First bytes: {head!r}"
        )
    data = data[i:]

    text = data.decode("utf-8-sig", errors="strict")
    return ET.fromstring(text)


def parse_eaf_annotations(eaf_path: str) -> Tuple[Dict[str, int], Dict[str, List[Ann]]]:
    root = parse_xml_loose(eaf_path)

    timeslots: Dict[str, int] = {}
    for elem in root.iter():
        if elem.tag.endswith("TIME_SLOT"):
            ts_id = elem.attrib.get("TIME_SLOT_ID")
            tv = elem.attrib.get("TIME_VALUE")
            if ts_id and tv is not None:
                timeslots[ts_id] = int(tv)

    ann_by_id: Dict[str, Dict[str, object]] = {}

    for tier in root.iter():
        if not tier.tag.endswith("TIER"):
            continue
        tier_id = tier.attrib.get("TIER_ID")
        if not tier_id:
            continue

        for ann_container in tier:
            if not ann_container.tag.endswith("ANNOTATION"):
                continue

            for child in ann_container:
                if child.tag.endswith("ALIGNABLE_ANNOTATION"):
                    a_id = child.attrib.get("ANNOTATION_ID")
                    ts1 = child.attrib.get("TIME_SLOT_REF1")
                    ts2 = child.attrib.get("TIME_SLOT_REF2")

                    val = ""
                    for gc in child:
                        if gc.tag.endswith("ANNOTATION_VALUE"):
                            val = (gc.text or "").strip()
                            break

                    if a_id and ts1 and ts2:
                        ann_by_id[a_id] = {
                            "tier_id": tier_id,
                            "ann": Ann(
                                timeslots.get(ts1, 0), timeslots.get(ts2, 0), val
                            ),
                            "ref_to": None,
                        }

                elif child.tag.endswith("REF_ANNOTATION"):
                    a_id = child.attrib.get("ANNOTATION_ID")
                    ref = child.attrib.get("ANNOTATION_REF")

                    val = ""
                    for gc in child:
                        if gc.tag.endswith("ANNOTATION_VALUE"):
                            val = (gc.text or "").strip()
                            break

                    if a_id:
                        ann_by_id[a_id] = {
                            "tier_id": tier_id,
                            "ann": Ann(-1, -1, val),
                            "ref_to": ref,
                        }

    def resolve_timing(a_id: str, depth: int = 0) -> Optional[Tuple[int, int]]:
        if depth > 50:
            return None
        rec = ann_by_id.get(a_id)
        if not rec:
            return None
        ann: Ann = rec["ann"]  # type: ignore
        if ann.start_ms >= 0 and ann.end_ms >= 0:
            return ann.start_ms, ann.end_ms
        ref_to = rec.get("ref_to")
        if not ref_to:
            return None
        return resolve_timing(ref_to, depth + 1)

    for a_id, rec in ann_by_id.items():
        ann: Ann = rec["ann"]  # type: ignore
        if ann.start_ms < 0 or ann.end_ms < 0:
            timing = resolve_timing(a_id)
            if timing:
                ann.start_ms, ann.end_ms = timing

    tier_to_anns: Dict[str, List[Ann]] = {}
    for rec in ann_by_id.values():
        tier_id = rec["tier_id"]  # type: ignore
        ann: Ann = rec["ann"]  # type: ignore
        if ann.start_ms >= 0 and ann.end_ms >= 0:
            tier_to_anns.setdefault(tier_id, []).append(ann)

    for k in tier_to_anns:
        tier_to_anns[k].sort(key=lambda a: (a.start_ms, a.end_ms))

    return timeslots, tier_to_anns


def collect_cutpoints(
    tier_to_anns: Dict[str, List[Ann]], tiers: List[str]
) -> List[int]:
    cutpoints = set()
    for t in tiers:
        for a in tier_to_anns.get(t, []):
            cutpoints.add(a.start_ms)
            cutpoints.add(a.end_ms)
    return sorted(cutpoints)


def ann_text_at(tier_anns: List[Ann], t0: int, t1: int) -> str:
    hits: List[str] = []
    for a in tier_anns:
        if a.end_ms <= t0:
            continue
        if a.start_ms >= t1:
            break
        if a.start_ms < t1 and a.end_ms > t0 and a.value:
            hits.append(a.value)

    seen = set()
    out = []
    for h in hits:
        if h not in seen:
            seen.add(h)
            out.append(h)
    return " · ".join(out)


def merge_identical_segments(
    segments: List[Tuple[int, int, str]],
) -> List[Tuple[int, int, str]]:
    if not segments:
        return segments
    merged = [segments[0]]
    for s, e, txt in segments[1:]:
        ps, pe, ptxt = merged[-1]
        if txt == ptxt and s == pe:
            merged[-1] = (ps, e, ptxt)
        else:
            merged.append((s, e, txt))
    return merged


def ass_header(
    playresx: int = 1920,
    playresy: int = 1080,
    margin_v: int = 55,
    margin_edge: int = 80,
    font_size: int = 44,
) -> str:
    return f"""[Script Info]
ScriptType: v4.00+
PlayResX: {playresx}
PlayResY: {playresy}
WrapStyle: 2
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: BottomCenter,Arial,{font_size},&H00FFFFFF,&H000000FF,&H00000000,&H64000000,0,0,0,0,100,100,0,0,1,2.5,0.8,2,60,60,{margin_v},1
Style: BottomLeft,Arial,{font_size},&H00FFFFFF,&H000000FF,&H00000000,&H64000000,0,0,0,0,100,100,0,0,1,2.5,0.8,2,{margin_edge},980,{margin_v},1
Style: BottomRight,Arial,{font_size},&H00FFFFFF,&H000000FF,&H00000000,&H64000000,0,0,0,0,100,100,0,0,1,2.5,0.8,2,980,{margin_edge},{margin_v},1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""


def ass_dialogue(start_ms: int, end_ms: int, style: str, text: str) -> str:
    text = text.replace("\n", r"\N")
    return f"Dialogue: 0,{ms_to_ass_time(start_ms)},{ms_to_ass_time(end_ms)},{style},,0,0,0,,{text}\n"


def build_ass(
    eaf_path: str,
    out_ass_path: str,
    tiers: List[str],
    layout: str = "stacked",
    margin_v: int = 55,
    margin_edge: int = 80,
    font_size: int = 44,
) -> None:
    _, tier_to_anns = parse_eaf_annotations(eaf_path)

    cutpoints = collect_cutpoints(tier_to_anns, tiers)
    if len(cutpoints) < 2:
        with open(out_ass_path, "w", encoding="utf-8") as f:
            f.write(
                ass_header(
                    margin_v=margin_v, margin_edge=margin_edge, font_size=font_size
                )
            )
        return

    raw_segments: List[Tuple[int, int, str]] = []

    for i in range(len(cutpoints) - 1):
        t0, t1 = cutpoints[i], cutpoints[i + 1]
        if t1 <= t0:
            continue

        if layout == "stacked":
            lines = []
            for t in tiers:
                txt = ann_text_at(tier_to_anns.get(t, []), t0, t1)
                lines.append(txt)
            block = "\n".join(lines).rstrip()
            raw_segments.append((t0, t1, block))

        elif layout == "columns":
            if len(tiers) != 4:
                raise ValueError(
                    "For layout='columns', provide exactly 4 tiers: S1 active, S1 passive, S2 active, S2 passive"
                )

            t_s1a, t_s1p, t_s2a, t_s2p = tiers

            s1a = ann_text_at(tier_to_anns.get(t_s1a, []), t0, t1)
            s1p = ann_text_at(tier_to_anns.get(t_s1p, []), t0, t1)
            s2a = ann_text_at(tier_to_anns.get(t_s2a, []), t0, t1)
            s2p = ann_text_at(tier_to_anns.get(t_s2p, []), t0, t1)

            block = f"__COLUMNS__\n{s1a}\n{s1p}\n__SPLIT__\n{s2a}\n{s2p}"
            raw_segments.append((t0, t1, block))

        else:
            raise ValueError("layout must be 'stacked' or 'columns'")

    segments = merge_identical_segments(raw_segments)

    with open(out_ass_path, "w", encoding="utf-8") as f:
        f.write(
            ass_header(margin_v=margin_v, margin_edge=margin_edge, font_size=font_size)
        )

        for t0, t1, block in segments:
            if not block.strip():
                continue

            if layout == "stacked":
                f.write(ass_dialogue(t0, t1, "BottomCenter", block))

            else:
                if not block.startswith("__COLUMNS__"):
                    continue
                _, rest = block.split("\n", 1)
                left, right = rest.split("__SPLIT__\n", 1)
                left = left.strip("\n")
                right = right.strip("\n")

                if left.strip():
                    f.write(ass_dialogue(t0, t1, "BottomLeft", left))
                if right.strip():
                    f.write(ass_dialogue(t0, t1, "BottomRight", right))


def get_linearized_data(eaf_path):
    tree = ET.parse(eaf_path)
    root = tree.getroot()

    time_order = root.find("TIME_ORDER")
    time_slots = {
        ts.get("TIME_SLOT_ID"): int(ts.get("TIME_VALUE"))
        for ts in time_order.findall("TIME_SLOT")
    }

    linearized_data = []

    target_tiers = [
        "Glossa mà activa S1",
        "Glossa mà passiva S1",
        "Glossa mà activa S2",
        "Glossa mà passiva S2",
    ]

    for tier in root.findall("TIER"):
        tier_id = tier.get("TIER_ID")

        if tier_id in target_tiers:
            speaker = "S1" if "S1" in tier_id else "S2"
            hand = "activa" if "activa" in tier_id else "passiva"

            for annotation in tier.findall(".//ALIGNABLE_ANNOTATION"):
                start_ts = annotation.get("TIME_SLOT_REF1")
                end_ts = annotation.get("TIME_SLOT_REF2")
                gloss_text = annotation.find("ANNOTATION_VALUE").text

                if gloss_text:
                    linearized_data.append(
                        {
                            "gloss": gloss_text.strip(),
                            "start": time_slots.get(start_ts, 0),
                            "end": time_slots.get(end_ts, 0),
                            "speaker": speaker,
                            "hand": hand,
                            "pos": "XXX",
                        }
                    )

    linearized_data.sort(key=lambda x: x["start"])

    return linearized_data
