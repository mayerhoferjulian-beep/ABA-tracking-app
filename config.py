# config.py
import os

# --- Pfade ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
TRAINING_PHOTOS_DIR = os.path.join(BASE_DIR, "assets", "training_photos") # Wird zwar nicht mehr genutzt, aber belassen
BKP_DIR = os.path.join(BASE_DIR, "data/backups")
SPORT_TESTS_DIR = os.path.join(BASE_DIR, "data", "sport_tests")
BLOOD_TESTS_DIR = os.path.join(BASE_DIR, "data", "blood_tests")

# Dateipfade
DATA_FILE = os.path.join(DATA_DIR, "daily_log.csv")
NUTRITION_FILE = os.path.join(DATA_DIR, "nutrition_log.csv")
SETTINGS_FILE = os.path.join(DATA_DIR, "settings.json")
MAPPING_FILE = os.path.join(DATA_DIR, "col_mapping.json")
GOALS_FILE = os.path.join(DATA_DIR, "goals.json")
SPORT_TESTS_FILE = os.path.join(DATA_DIR, "sport_tests.csv")
BLOOD_TESTS_FILE = os.path.join(DATA_DIR, "blood_tests.csv")

# Stellen sicher, dass die Verzeichnisse existieren
for path in [DATA_DIR, ASSETS_DIR, TRAINING_PHOTOS_DIR, BKP_DIR, SPORT_TESTS_DIR, BLOOD_TESTS_DIR]:
    os.makedirs(path, exist_ok=True)

# --- Spaltendefinitionen für Tageswerte ---
COLUMNS = [
    "date", "weekday", "phase",
    "sleep_hours", "sleep_score", "hrv_sleep_avg", "rhr_sleep_avg", "rhr_sleep_min",
    "spo2_sleep_avg", "spo2_sleep_min", "deep_sleep_hours", "deep_sleep_percent", "awakenings",
    # Aktivität (Alltag)
    "total_steps", "total_kcal_burn",
    # ENERGIE & NÄHRSTOFFE (neu hinzugefügt)
    "intake_kcal", "carbs_g", "protein_g", "fat_g", "water_ml",
    # Körper & Kreislauf
    "morning_pulse", "hrv_day_avg", "spo2_day_avg", "bp_sys", "bp_dia",
    "body_weight", "stress_avg", "stress_peak",
    # Wohlbefinden
    "energy", "mood", "motivation", "concentration", "note",
    # Berechnete Metriken
    "energy_balance", "protein_g_per_kg", "recovery_index", "load_score", "wellbeing_score", "stress_balance",
    "last_modified"
]

# --- Spaltendefinitionen für Ernährungstagebuch ---
NUTRITION_COLUMNS = [
    "date", "phase",
    # Mahlzeiten
    "breakfast", "snack_1", "lunch", "snack_2", "dinner", "supplements", "nutrition_note",
    # Energie & Nährstoffe
    "intake_kcal", "carbs_g", "protein_g", "fat_g", "water_ml",
    "last_modified"
]

# --- Spaltendefinitionen für Sporttests ---
SPORT_TESTS_COLUMNS = [
    "test_date", "test_type", "general_notes",
    # Cooper-Test
    "cooper_distance", "cooper_avg_hr", "cooper_max_hr", "cooper_pace", "cooper_kcal",
    "cooper_warmup", "cooper_aerob", "cooper_anaerob", "cooper_intensive", "cooper_photo",
    # 5km-Lauf
    "run5k_time", "run5k_avg_hr", "run5k_max_hr", "run5k_pace", "run5k_kcal",
    "run5k_warmup", "run5k_aerob", "run5k_anaerob", "run5k_intensive", "run5k_photo",
    # Liegestütze
    "pushups_reps", "pushups_avg_hr", "pushups_max_hr", "pushups_photo",
    # Plank
    "plank_time", "plank_avg_hr", "plank_max_hr", "plank_photo",
    # Burpee-Test
    "burpee_reps", "burpee_avg_hr", "burpee_max_hr", "burpee_photo",
    # VO2max-Test
    "vo2max_value", "vo2max_avg_hr", "vo2max_max_hr", "vo2max_duration", "vo2max_speed", "vo2max_photo",
    "last_modified"
]

# --- Spaltendefinitionen für Bluttests ---
BLOOD_TESTS_COLUMNS = [
    "test_date", "test_type", "notes", "pdf_file",
    # Rotes & weißes Blutbild
    "hemoglobin", "erythrocytes", "mcv", "mch", "thrombocytes", "leukocytes",
    "segment", "monocytes", "lymphocytes", "basophils", "eosinophils",
    # Blutchemie
    "alat", "asat", "creatinine", "egfr", "iron", "transferrin_saturation",
    "gamma_gt", "ap", "iron_saturation", "ebk", "ferritin", "transferrin",
    # Blutfette
    "cholesterol", "triglycerides", "ldl_chol",
    # Elektrolyte
    "sodium", "calcium", "potassium",
    # Schilddrüsenhormone
    "tsh_basal",
    # Harnbefund
    "hk",
    "last_modified"
]

# --- Standardwerte ---
DEFAULT_SETTINGS = {"auto_import_enabled": False, "watch_folder": "", "filename_glob": "*.csv", "mapping_saved": False}
DEFAULT_MAPPING = {}
DEFAULT_GOALS = {
    "sleep_hours_goal": 8.0,
    "total_steps_goal": 10000,
    "intake_kcal_goal": 2500,
    "protein_g_per_kg_goal": 1.6,
}

# --- Vordefinierte Trainingstypen (nicht mehr in Benutzung, aber belassen) ---
TRAINING_TYPES = ["Laufen", "Kraftsport", "Radfahren", "Schwimmen", "Yoga", "Rudern", "Andere"]