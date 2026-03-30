"""
Build per-machine cost data from Salesforce queries (ProductConsumed), then
output updated JS COST_DATA block for mps-machine.html.

Family split:
  Toner   = Ricoh Copier Toners and Developers  -> tonerNZD  (include in GM)
  Parts   = Ricoh Copier Parts + IT Products     -> partsNZD  (include in GM)
  Equip   = Ricoh Copier Equipment               -> equipNZD  (flag only, exclude from GM)
  Paper   = Digital Paper                        -> paperNZD  (flag only, exclude from GM)
  Skip    = Service Department, Ricoh Software Solutions (service callout / travel fees)
"""
import json
from collections import defaultdict

# ── FX rates ────────────────────────────────────────────────────────────────
FX = {"NZD": 1.0, "SBD": 0.180, "WST": 0.540, "VUV": 0.012, "TOP": 0.640}

def to_nzd(amount, cur):
    return round(amount * FX.get(cur, 1.0), 4)

# ── Serial -> AssetId + LastVisit ────────────────────────────────────────────
asset_info = {
    # Batch 1 (NZ + SI)
    "3089R720383": {"id": "02iMp00000DjMuXIAV", "lastVisit": None},
    "3090R720052": {"id": "02i7F00000Flle3QAB", "lastVisit": "2026-03-12"},
    "3098RC20297": {"id": "02i7F000009Uj7NQAS", "lastVisit": "2026-03-16"},
    "3099R220018": {"id": "02i7F000009UiZyQAK", "lastVisit": "2026-03-19"},
    "3099R220050": {"id": "02i7F000009UhWoQAK", "lastVisit": "2026-03-19"},
    "3203XB57567": {"id": "02iMp000006BfUDIA0", "lastVisit": "2025-09-16"},
    "3352P950284": {"id": "02i7F000000WV5HQAW", "lastVisit": "2026-03-19"},
    "3352P950286": {"id": "02i7F000000WWPTQA4", "lastVisit": "2025-10-09"},
    "3359P201194": {"id": "02i7F00000FlkqTQAR", "lastVisit": "2025-11-25"},
    "3359PA03408": {"id": "02i7F00000FlkqOQAR", "lastVisit": "2026-03-19"},
    "4412RC20160": {"id": "02iGA00000hKXogYAG", "lastVisit": "2026-01-08"},
    "4412RC20161": {"id": "02iGA00000hKXrLYAW", "lastVisit": "2026-02-25"},
    "4451R420031": {"id": "02i7F000000WSvBQAW", "lastVisit": "2025-10-09"},
    "5852ZC31949": {"id": "02i7F000000WX5IQAW", "lastVisit": "2026-03-19"},
    "C378P300509": {"id": "02i7F000009NtyAQAS", "lastVisit": "2026-03-17"},
    "C378P300510": {"id": "02i7F000009NtyBQAS", "lastVisit": "2026-03-24"},
    "C386PC00385": {"id": "02i7F000009NtySQAS", "lastVisit": "2026-03-05"},
    "C387P900198": {"id": "02i7F000009NtycQAC", "lastVisit": "2026-03-06"},
    "C388P800038": {"id": "02i7F000000FLjxQAG", "lastVisit": "2026-03-13"},
    "C388P800047": {"id": "02i7F000000FWGAQA4", "lastVisit": "2026-02-15"},
    "C388PA00312": {"id": "02i7F000000FLk2QAG", "lastVisit": "2026-02-15"},
    "C388PA00314": {"id": "02i7F000000FQ9CQAW", "lastVisit": "2025-12-12"},
    "C388PA00336": {"id": "02i7F000000FQJTQA4", "lastVisit": "2026-03-04"},
    "C388PA00340": {"id": "02i7F000000FQJdQAO", "lastVisit": "2026-03-12"},
    "C388PC00109": {"id": "02i7F000000FWFlQAO", "lastVisit": "2025-12-03"},
    "C388PC00164": {"id": "02i7F000000FLjnQAG", "lastVisit": "2026-02-16"},
    "C409P900081": {"id": "02i7F00000Flk1HQAR", "lastVisit": "2026-01-30"},
    "C508PA03593": {"id": "02i7F000000FLjdQAG", "lastVisit": "2025-04-11"},
    "G696M550109": {"id": "02iMp00000Cq0mbIAB", "lastVisit": "2026-03-26"},
    "G988X370881": {"id": "02i7F000009Nu9BQAS", "lastVisit": "2026-02-09"},
    "G988X370919": {"id": "02i7F000000x4kTQAQ", "lastVisit": "2026-01-20"},
    "G988X790785": {"id": "02i7F000000x56aQAA", "lastVisit": "2026-02-24"},
    "G988X790786": {"id": "02i7F000000FZdKQAW", "lastVisit": "2025-04-21"},
    "G988X790843": {"id": "02i7F000000xJhtQAE", "lastVisit": "2026-03-10"},
    "G988X791117": {"id": "02i7F000000FZdUQAW", "lastVisit": "2026-03-24"},
    "G988X791119": {"id": "02i7F000000FZdjQAG", "lastVisit": "2026-02-23"},
    "G989X110755": {"id": "02i7F000009VLgnQAG", "lastVisit": "2026-03-20"},
    "G989X315631": {"id": "02i7F00000FlkS4QAJ", "lastVisit": "2026-03-11"},
    "G989X315648": {"id": "02i7F000009VCZhQAO", "lastVisit": "2025-05-13"},
    "G989X315651": {"id": "02i7F00000FlkjGQAR", "lastVisit": "2025-05-05"},
    "G996X802544": {"id": "02i7F000009OzemQAC", "lastVisit": "2025-09-07"},
    "Y028X945302": {"id": "02i7F000000FQ9HQAW", "lastVisit": "2026-03-17"},
    "Y028X945305": {"id": "02i7F000000FWFqQAO", "lastVisit": "2026-02-11"},
    "Y849P400668": {"id": "02i7F000000GrSlQAK", "lastVisit": "2023-08-21"},
    # Batch 2 (SI continued + Tonga)
    "3081R920656": {"id": "02i7F00000L21f6QAB", "lastVisit": "2026-03-24"},
    "3090R720163": {"id": "02i7F00000FllfkQAB", "lastVisit": "2026-03-23"},
    "3098RC20204": {"id": "02i7F000009Uy6YQAS", "lastVisit": "2026-02-15"},
    "3101R720218": {"id": "02i7F00000MKN8TQAX", "lastVisit": "2025-11-25"},
    "3102RA90148": {"id": "02i7F000000WVjlQAG", "lastVisit": "2025-11-18"},
    "3102RC20495": {"id": "02i7F000000WX10QAG", "lastVisit": "2026-02-19"},
    "3102RC20511": {"id": "02i7F000000WY7EQAW", "lastVisit": "2025-12-01"},
    "3110RB20313": {"id": "02i7F00000JEMrBQAX", "lastVisit": "2026-02-27"},
    "3111R120114": {"id": "02i7F00000JCdZRQA1", "lastVisit": "2026-03-19"},
    "3111R120123": {"id": "02i7F00000JOlHVQA1", "lastVisit": "2026-03-15"},
    "3121M220258": {"id": "02i7F00000Hxn8nQAB", "lastVisit": "2026-03-24"},
    "3128MC20092": {"id": "02i7F000009UhwmQAC", "lastVisit": "2026-03-25"},
    "3129MC20133": {"id": "02i7F00000Flk3RQAR", "lastVisit": "2026-03-24"},
    "3200X631880": {"id": "02i7F00000HxqBEQAZ", "lastVisit": "2026-03-24"},
    "3350P702454": {"id": "02i7F00000Fljc6QAB", "lastVisit": "2026-03-25"},
    "3920PC02053": {"id": "02i7F00000FlnZ9QAJ", "lastVisit": "2026-03-12"},
    "3922P851100": {"id": "02iGA00000esu9DYAQ", "lastVisit": "2026-03-10"},
    "3929PB01403": {"id": "02i7F000009VKQMQA4", "lastVisit": "2026-02-09"},
    "4442R520109": {"id": "02i7F000000WSDVQA4", "lastVisit": "2026-02-12"},
    "4451R320002": {"id": "02i7F000000WTwfQAG", "lastVisit": "2026-03-25"},
    "4451R320009": {"id": "02i7F000000WSDUQA4", "lastVisit": "2026-02-12"},
    "9133R710078": {"id": "02iGA000000WZ4sYAG", "lastVisit": "2026-03-12"},
    "9133R710127": {"id": "02iGA00000e5203YAA", "lastVisit": "2026-02-15"},
    "9153RC30478": {"id": "02iMp000005oS4fIAE", "lastVisit": "2025-11-26"},
    "9174R120239": {"id": "02iGA00000ZMdlZYAT", "lastVisit": "2026-03-13"},
    "9175R220104": {"id": "02iMp00000DiqJZIAZ", "lastVisit": "2026-03-06"},
    "9193R330008": {"id": "02i7F000000WVwOQAW", "lastVisit": "2025-08-06"},
    "9193R630092": {"id": "02iGA000000XiliYAC", "lastVisit": "2026-02-18"},
    "9194R830192": {"id": "02iMp00000889HdIAI", "lastVisit": "2025-11-17"},
    "C370P100183": {"id": "02i7F00000FlhzOQAR", "lastVisit": "2026-03-12"},
    "C388P800005": {"id": "02i7F000009UkgNQAS", "lastVisit": "2026-02-24"},
    "C409PA00069": {"id": "02i7F000000Grk7QAC", "lastVisit": "2026-01-28"},
    "C509P702882": {"id": "02i7F000009V2bhQAC", "lastVisit": "2026-03-24"},
    "C509P906086": {"id": "02i7F000009VBuYQAW", "lastVisit": "2024-12-16"},
    "C509P906161": {"id": "02i7F000009VBuiQAG", "lastVisit": "2026-03-05"},
    "C738M830460": {"id": "02i7F000009NtzoQAC", "lastVisit": "2026-03-04"},
    "E154M450453": {"id": "02iGA00000hKIJTYA4", "lastVisit": "2025-11-18"},
    "E154MA50136": {"id": "02iMp00000AJjjdIAD", "lastVisit": "2026-03-27"},
    "E155M650028": {"id": "02iMp00000AvAwAIAV", "lastVisit": "2025-10-08"},
    "E165M550019": {"id": "02iMp000005oQ65IAE", "lastVisit": "2026-02-24"},
    "E175MA50358": {"id": "02iGA00000hKw2BYAS", "lastVisit": "2026-03-09"},
    "E185M350137": {"id": "02iMp000005oRVBIA2", "lastVisit": "2025-04-22"},
    "E185M950261": {"id": "02i7F000000WWnAQAW", "lastVisit": "2026-02-26"},
    "E185MA50180": {"id": "02iGA00000hKrraYAC", "lastVisit": "2026-02-23"},
    "E185MB50005": {"id": "02i7F000000WVm9QAG", "lastVisit": "2025-09-09"},
    "E205R870721": {"id": "02iMp000005oPGTIA2", "lastVisit": "2026-03-24"},
    "E214R880353": {"id": "02iMp000005oPUzIAM", "lastVisit": "2026-03-27"},
    "E215R380194": {"id": "02iMp000005oPhtIAE", "lastVisit": "2025-09-03"},
    "E215R880234": {"id": "02iMp000005oPpxIAE", "lastVisit": "2026-03-10"},
    "G988X993746": {"id": "02i7F000009Unz0QAC", "lastVisit": "2026-03-17"},
    "S9159501265": {"id": "02i7F000009NuB0QAK", "lastVisit": "2026-02-18"},
}

# ── ProductConsumed records: (serial, qty, unitPrice, currency, family) ──────
# family: "Toner" | "Parts" | "Equip" | "Paper" | "Skip"
# Source: Case -> WorkOrder -> ProductConsumed, last 90 days, all 4 SF batches
# Queried 2026-03-30

pc_records = [
    # ── Batch 1 (batch 1 assets, 66 SF records) ──
    ("4412RC20160", 1, 2041.16, "SBD", "Toner"),
    ("3359PA03408", 1, 2425.10, "SBD", "Toner"),
    ("C386PC00385", 1, 13777.97, "SBD", "Parts"),
    ("C386PC00385", 1, 2149.83, "SBD", "Parts"),
    ("C386PC00385", 1, 25720.50, "SBD", "Parts"),
    ("3098RC20297", 1, 3708.00, "SBD", "Toner"),
    ("C388PA00336", 1, 3015.34, "SBD", "Toner"),
    ("3352P950284", 75, 50.00, "SBD", "Paper"),  # Kiwi Copy A4 paper reams
    ("3098RC20297", 1, 3708.00, "SBD", "Toner"),
    ("3099R220050", 1, 1772.10, "SBD", "Toner"),
    ("3099R220050", 1, 3708.00, "SBD", "Toner"),
    ("3099R220018", 1, 1772.10, "SBD", "Toner"),
    ("3099R220018", 1, 3708.00, "SBD", "Toner"),
    ("3098RC20297", 1, 3708.00, "SBD", "Toner"),
    ("C388PA00340", 1, 2305.10, "SBD", "Toner"),
    ("C388PA00340", 1, 8772.06, "SBD", "Parts"),  # OPC Drum
    ("C388PA00340", 1, 2250.27, "SBD", "Toner"),  # Developer Black (Toner family in SF)
    ("C388PA00340", 1, 2004.66, "SBD", "Parts"),  # Brush Roller Cleaner
    ("C388PA00340", 1, 1621.97, "SBD", "Parts"),  # Blade Cleaning
    ("C387P900198", 2, 1153.54, "SBD", "Toner"),
    ("C378P300510", 1, 0.00, "SBD", "Parts"),     # Optical Writing Unit ($0 warranty)
    ("3090R720052", 1, 3708.00, "SBD", "Toner"),
    ("3090R720052", 1, 3708.00, "SBD", "Toner"),
    ("3090R720052", 1, 1793.15, "SBD", "Toner"),
    ("3090R720052", 1, 3708.00, "SBD", "Toner"),
    ("C388PA00312", 1, 3015.34, "SBD", "Toner"),
    ("C388P800047", 1, 3015.34, "SBD", "Toner"),
    ("3352P950284", 75, 50.00, "SBD", "Paper"),
    ("3098RC20297", 1, 3708.00, "SBD", "Toner"),
    ("3099R220018", 1, 1772.10, "SBD", "Toner"),
    ("3099R220018", 1, 3708.00, "SBD", "Toner"),
    ("4412RC20161", 2, 830.50, "SBD", "Toner"),
    ("3098RC20297", 1, 3708.00, "SBD", "Toner"),
    ("3099R220050", 1, 3708.00, "SBD", "Toner"),
    ("3099R220050", 1, 3708.00, "SBD", "Toner"),
    ("3098RC20297", 1, 3708.00, "SBD", "Toner"),
    ("3099R220018", 1, 0.00, "SBD", "Parts"),     # Fusing Unit ($0 warranty)
    ("3099R220018", 1, 3708.00, "SBD", "Toner"),
    ("3099R220018", 1, 3708.00, "SBD", "Toner"),
    ("C386PC00385", 1, 3015.34, "SBD", "Toner"),
    ("C387P900198", 1, 21870.50, "SBD", "Parts"), # PCU Cleaning Unit
    ("C387P900198", 1, 13777.97, "SBD", "Parts"), # PCDU
    ("3099R220050", 1, 8071.05, "SBD", "Parts"),  # PCU KCMY
    ("3099R220050", 1, 5216.27, "SBD", "Parts"),  # Dev Unit C
    ("3099R220050", 1, 0.00, "SBD", "Parts"),     # Toner Hopper ($0)
    ("3099R220050", 1, 3708.00, "SBD", "Toner"),
    ("3099R220050", 1, 3708.00, "SBD", "Toner"),
    ("3098RC20297", 1, 1772.10, "SBD", "Toner"),
    ("3090R720052", 1, 1772.10, "SBD", "Toner"),
    ("C388P800038", 1, 13777.97, "SBD", "Parts"), # PCDU
    ("C388P800038", 1, 2149.83, "SBD", "Parts"),  # Transfer Roller
    ("3099R220050", 1, 0.00, "SBD", "Parts"),
    ("3099R220050", 1, 5216.27, "SBD", "Parts"),
    ("3099R220050", 1, 8071.05, "SBD", "Parts"),
    ("3098RC20297", 1, 3708.00, "SBD", "Toner"),
    ("3099R220018", 1, 1772.10, "SBD", "Toner"),
    ("3099R220018", 1, 3708.00, "SBD", "Toner"),
    ("3352P950284", 75, 50.00, "SBD", "Paper"),
    ("3099R220018", 1, 1772.10, "SBD", "Toner"),
    ("5852ZC31949", 1, 4450.00, "SBD", "Equip"),  # Ricoh M 320F machine
    ("3099R220018", 1, 1772.10, "SBD", "Toner"),
    ("3099R220018", 1, 1772.10, "SBD", "Toner"),
    ("3099R220018", 1, 3708.00, "SBD", "Toner"),
    ("3099R220050", 1, 1772.10, "SBD", "Toner"),
    ("5852ZC31949", 1, 4450.00, "SBD", "Equip"),  # Ricoh M 320F machine
    ("C378P300510", 1, 3015.34, "SBD", "Toner"),

    # ── Batch 2 (batch 2a assets, 22 SF records) ──
    ("G988X370881", 1, 938.75, "SBD", "Parts"),   # Hot Fuser Roller
    ("G988X370881", 1, 938.75, "SBD", "Parts"),
    ("G988X370881", 1, 0.00, "SBD", "Parts"),     # Retard Roller ($0)
    ("G988X370881", 1, 0.00, "SBD", "Parts"),     # Pulley Feed ($0)
    ("G988X370881", 1, 0.00, "SBD", "Parts"),     # Pick Up ($0)
    ("C409P900081", 2, 1153.54, "SBD", "Toner"),
    ("Y028X945302", 1, 0.00, "SBD", "Parts"),     # Fusing Unit ($0)
    ("Y028X945302", 1, 3560.75, "SBD", "Parts"),  # PCU
    ("Y028X945302", 1, 4810.10, "SBD", "Toner"),
    ("Y028X945305", 1, 0.00, "SBD", "Parts"),     # Imaging Unit ($0)
    ("C388PC00164", 1, 8772.06, "SBD", "Parts"),  # OPC Drum
    ("C388PC00164", 1, 2004.66, "SBD", "Parts"),  # Brush Roller Cleaner
    ("C388PC00164", 1, 1621.97, "SBD", "Parts"),  # Blade Cleaning
    ("C388PC00164", 1, 2171.71, "SBD", "Parts"),  # Charge Roller
    ("C388PC00164", 1, 2250.27, "SBD", "Toner"),  # Developer Black (Toner family)
    ("G989X315631", 1, 938.75, "SBD", "Parts"),   # Hot Fuser Roller
    ("G989X315631", 1, 406.00, "SBD", "Parts"),   # Drum Cleaning Blade
    ("G988X791119", 1, 4810.10, "SBD", "Toner"),
    ("G988X790785", 1, 4810.10, "SBD", "Toner"),
    ("G989X315631", 1, 4810.10, "SBD", "Toner"),
    ("Y028X945302", 1, 938.75, "SBD", "Parts"),   # Hot Fuser Roller
    ("G988X791117", 1, 4810.10, "SBD", "Toner"),

    # ── Batch 3 (batch 2b assets, 54 SF records) ──
    ("3090R720163", 1, 3708.00, "SBD", "Toner"),
    ("3090R720163", 1, 3708.00, "SBD", "Toner"),
    ("3090R720163", 1, 3708.00, "SBD", "Toner"),
    ("3128MC20092", 1, 2948.98, "SBD", "Toner"),
    ("3102RC20495", 1, 364.02, "TOP", "Toner"),
    ("3121M220258", 1, 2948.98, "SBD", "Toner"),
    ("3090R720163", 1, 1772.10, "SBD", "Toner"),
    ("3090R720163", 1, 3708.00, "SBD", "Toner"),
    ("3111R120114", 1, 159.00, "TOP", "Skip"),    # Service Callout Fee
    ("3128MC20092", 1, 2948.98, "SBD", "Toner"),
    ("3929PB01403", 1, 2442.35, "SBD", "Toner"),
    ("4451R320002", 2, 1153.54, "SBD", "Toner"),
    ("3929PB01403", 1, 4058.45, "SBD", "Toner"),
    ("3929PB01403", 1, 4058.45, "SBD", "Toner"),
    ("3098RC20204", 1, 1772.10, "SBD", "Toner"),
    ("3102RC20495", 1, 20.00, "TOP", "Skip"),     # Service Travel
    ("3102RC20495", 1, 364.02, "TOP", "Toner"),
    ("3102RC20495", 1, 159.00, "TOP", "Skip"),    # Service Callout Fee
    ("4442R520109", 1, 159.00, "TOP", "Skip"),    # Service Callout Fee
    ("4451R320009", 1, 159.00, "TOP", "Skip"),    # Service Callout Fee
    ("3098RC20204", 1, 3708.00, "SBD", "Toner"),
    ("3090R720163", 1, 3708.00, "SBD", "Toner"),
    ("3128MC20092", 1, 2714.00, "SBD", "Toner"),
    ("3128MC20092", 1, 6982.00, "SBD", "Toner"),
    ("3128MC20092", 1, 6982.00, "SBD", "Toner"),
    ("3090R720163", 1, 8989.05, "SBD", "Parts"),  # PCDU K
    ("3090R720163", 3, 4392.53, "SBD", "Parts"),  # PCU KCMY
    ("3129MC20133", 1, 2714.00, "SBD", "Toner"),
    ("3102RC20495", 1, 0.00, "TOP", "Parts"),     # Fusing Unit ($0)
    ("3102RC20495", 1, 20.00, "TOP", "Skip"),     # Service Travel
    ("3102RC20495", 1, 836.73, "TOP", "Toner"),
    ("3121M220258", 1, 6982.00, "SBD", "Toner"),
    ("3110RB20313", 1, 20.00, "TOP", "Skip"),     # Service Travel
    ("3110RB20313", 1, 420.73, "TOP", "Toner"),
    ("3111R120114", 1, 20.00, "TOP", "Skip"),     # Service Travel
    ("3111R120114", 1, 420.73, "TOP", "Toner"),
    ("3111R120114", 1, 781.53, "TOP", "Toner"),
    ("3081R920656", 1, 1772.10, "SBD", "Toner"),
    ("3121M220258", 1, 9820.48, "SBD", "Parts"),  # PCU Black
    ("3090R720163", 1, 1772.10, "SBD", "Toner"),
    ("3128MC20092", 1, 2948.98, "SBD", "Toner"),
    ("3121M220258", 1, 2948.98, "SBD", "Toner"),
    ("3920PC02053", 1, 159.00, "TOP", "Skip"),    # Service Callout Fee
    ("3920PC02053", 1, 159.00, "TOP", "Skip"),    # Service Callout Fee
    ("4451R320002", 1, 3199.98, "SBD", "Parts"),  # Pressure Roller
    ("4451R320002", 1, 817.45, "SBD", "Parts"),   # Thermistor
    ("3111R120114", 1, 1717.04, "TOP", "Parts"),  # PCU CMY
    ("3111R120114", 1, 2394.95, "TOP", "Parts"),  # PCU K
    ("4451R320002", 1, 3015.34, "SBD", "Toner"),
    ("3081R920656", 1, 3708.00, "SBD", "Toner"),
    ("3081R920656", 1, 3708.00, "SBD", "Toner"),
    ("3350P702454", 1, 2425.10, "SBD", "Toner"),
    ("3128MC20092", 1, 2948.98, "SBD", "Toner"),
    ("4451R320002", 1, 10318.80, "SBD", "Parts"), # Sleeve

    # ── Batch 4 (batch 2c assets, 71 SF records) ──
    ("E154MA50136", 1, 2648.75, "SBD", "Toner"),
    ("E214R880353", 1, 6167.08, "SBD", "Parts"),  # Dev Unit C
    ("E214R880353", 2, 6475.19, "SBD", "Parts"),  # PCU KCMY
    ("E185MA50180", 1, 1080.11, "TOP", "Parts"),  # PCU Colour
    ("E185MA50180", 1, 935.22, "TOP", "Parts"),   # Dev Unit K
    ("9175R220104", 1, 93168.65, "SBD", "Equip"), # Ricoh IM C4510 (machine replacement)
    ("9175R220104", 1, 10793.24, "SBD", "Equip"), # PB3320 Paper Feed Unit
    ("9175R220104", 1, 7766.38, "SBD", "Toner"),
    ("9175R220104", 1, 7766.38, "SBD", "Toner"),
    ("9175R220104", 1, 7766.38, "SBD", "Toner"),
    ("9175R220104", 1, 2677.28, "SBD", "Toner"),
    ("9175R220104", 1, 273.88, "SBD", "Parts"),   # Surge adapter (Ricoh Copier Parts)
    ("9175R220104", 1, 103.11, "SBD", "Parts"),   # Power cable (IT Products -> treat as parts)
    ("9193R630092", 1, 2677.28, "SBD", "Toner"),
    ("9193R630092", 1, 7766.38, "SBD", "Toner"),
    ("E175MA50358", 1, 1080.11, "TOP", "Parts"),  # PCU K
    ("E185MA50180", 1, 159.00, "TOP", "Skip"),    # Service Callout Fee
    ("9193R630092", 1, 7766.38, "SBD", "Toner"),
    ("9193R630092", 1, 7766.38, "SBD", "Toner"),
    ("9175R220104", 1, 93168.65, "SBD", "Equip"), # Ricoh IM C4510 (second WO)
    ("9175R220104", 1, 10793.24, "SBD", "Equip"), # PB3320 Paper Feed Unit (second WO)
    ("9175R220104", 1, 7766.38, "SBD", "Toner"),
    ("9175R220104", 1, 7766.38, "SBD", "Toner"),
    ("9175R220104", 1, 7766.38, "SBD", "Toner"),
    ("9175R220104", 1, 2677.28, "SBD", "Toner"),
    ("9175R220104", 1, 273.88, "SBD", "Parts"),   # Surge adapter (second WO)
    ("9175R220104", 1, 103.11, "SBD", "Parts"),   # Power cable (second WO)
    ("9175R220104", 1, 0.00, "SBD", "Skip"),      # PaperCut MF $0 (Software)
    ("E185MA50180", 1, 20.00, "TOP", "Skip"),     # Service Travel
    ("E185MA50180", 1, 413.66, "TOP", "Toner"),
    ("E185M950261", 1, 20.00, "TOP", "Skip"),     # Service Travel
    ("E185M950261", 1, 413.66, "TOP", "Toner"),
    ("C509P906161", 1, 2480.66, "SBD", "Toner"),
    ("C509P906161", 1, 3312.75, "SBD", "Toner"),
    ("9133R710127", 1, 2868.96, "SBD", "Toner"),
    ("E185MA50180", 1, 159.00, "TOP", "Skip"),    # Service Callout Fee
    ("E185MA50180", 1, 159.00, "TOP", "Skip"),
    ("S9159501265", 1, 6083.00, "SBD", "Toner"),
    ("9193R630092", 1, 7419.39, "SBD", "Parts"),  # Dev Unit K
    ("9193R630092", 1, 6789.71, "SBD", "Parts"),  # Transfer Belt
    ("9193R630092", 1, 6449.22, "SBD", "Parts"),  # Cleaning Unit
    ("9193R630092", 1, 2677.28, "SBD", "Toner"),
    ("9193R630092", 1, 7766.38, "SBD", "Toner"),
    ("9193R630092", 1, 7766.38, "SBD", "Toner"),
    ("9193R630092", 1, 7766.38, "SBD", "Toner"),
    ("E175MA50358", 1, 413.66, "TOP", "Toner"),
    ("E175MA50358", 1, 20.00, "TOP", "Skip"),     # Service Travel
    ("E214R880353", 1, 0.00, "SBD", "Toner"),     # Toner $0
    ("E185MA50180", 1, 159.00, "TOP", "Skip"),    # Service Callout Fee
    ("E185MA50180", 1, 159.00, "TOP", "Skip"),
    ("E165M550019", 1, 2648.75, "SBD", "Toner"),
    ("E175MA50358", 1, 159.00, "TOP", "Skip"),    # Service Callout Fee
    ("E185M950261", 1, 1080.11, "TOP", "Parts"),  # PCU Colour
    ("E185M950261", 1, 0.00, "TOP", "Parts"),     # Transfer Belt Cleaning ($0)
    ("C738M830460", 1, 2046.54, "TOP", "Parts"),  # Fusing Unit
    ("C509P906161", 1, 3312.75, "SBD", "Toner"),
    ("E215R880234", 1, 1793.15, "SBD", "Toner"),
    ("E175MA50358", 1, 159.00, "TOP", "Skip"),    # Service Callout Fee
    ("E175MA50358", 1, 20.00, "TOP", "Skip"),     # Service Travel
    ("E175MA50358", 1, 444.72, "TOP", "Toner"),
    ("E175MA50358", 1, 900.51, "TOP", "Toner"),
    ("E175MA50358", 1, 900.51, "TOP", "Toner"),
    ("C370P100183", 1, 3015.34, "SBD", "Toner"),
    ("C370P100183", 1, 13777.97, "SBD", "Parts"), # PCDU
    ("C370P100183", 1, 3199.98, "SBD", "Parts"),  # Pressure Roller
    ("C370P100183", 1, 10016.60, "SBD", "Parts"), # Sleeve
    ("C370P100183", 1, 817.45, "SBD", "Parts"),   # Thermistor
    ("9133R710078", 4, 13112.03, "SBD", "Parts"), # PCU KCMY (x4)
    ("9174R120239", 1, 159.00, "TOP", "Skip"),    # Service Callout Fee
    ("9174R120239", 1, 159.00, "TOP", "Skip"),    # Service Callout Fee
    ("E214R880353", 1, 1793.15, "SBD", "Toner"),
]

# ── Compute costs per serial by category ─────────────────────────────────────
acc = defaultdict(lambda: {"Toner": defaultdict(float), "Parts": defaultdict(float),
                            "Equip": defaultdict(float), "Paper": defaultdict(float)})
for sn, qty, price, cur, fam in pc_records:
    if fam == "Skip":
        continue
    acc[sn][fam][cur] += qty * price

def sum_nzd(cur_dict):
    return round(sum(to_nzd(amt, cur) for cur, amt in cur_dict.items()), 2)

costs = {}
for sn, cats in acc.items():
    costs[sn] = {
        "tonerNZD": sum_nzd(cats["Toner"]),
        "partsNZD": sum_nzd(cats["Parts"]),
        "equipNZD": sum_nzd(cats["Equip"]),
        "paperNZD": sum_nzd(cats["Paper"]),
    }

# ── Build final output ────────────────────────────────────────────────────────
result = {}
for sn, info in asset_info.items():
    last_visit = info["lastVisit"]
    c = costs.get(sn, {})
    result[sn] = {
        "lastVisit": last_visit,
        "tonerNZD": c.get("tonerNZD", 0),
        "partsNZD": c.get("partsNZD", 0),
        "equipNZD": c.get("equipNZD", 0),
        "paperNZD": c.get("paperNZD", 0),
    }

# ── Print JS const for embedding ─────────────────────────────────────────────
print("const COST_DATA = " + json.dumps(result, indent=2, separators=(',', ': ')) + ";")
print()
print(f"// {len(result)} machines | queried 2026-03-30 | 90-day window")
non_zero_t = sum(1 for v in result.values() if v['tonerNZD'] > 0)
non_zero_p = sum(1 for v in result.values() if v['partsNZD'] > 0)
non_zero_e = sum(1 for v in result.values() if v['equipNZD'] > 0)
print(f"// tonerNZD > 0: {non_zero_t} | partsNZD > 0: {non_zero_p} | equipNZD > 0: {non_zero_e}")

# Spot-check 9175R220104
r = result.get("9175R220104", {})
print(f"\n// Spot-check 9175R220104:")
print(f"//   tonerNZD={r.get('tonerNZD')} partsNZD={r.get('partsNZD')} equipNZD={r.get('equipNZD')}")

# ── Write JSON ────────────────────────────────────────────────────────────────
OUT_PATH = r"C:\Users\ShivNarayan(NZ)\OneDrive - RICOH SOUTH PACIFIC\Desktop\Claude-Cowork\MPS Dashboard\machine_costs.json"
with open(OUT_PATH, 'w') as f:
    json.dump(result, f, indent=2)
print(f"\n// Written to {OUT_PATH}")
