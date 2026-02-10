# ui_components.py
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import date, timedelta, datetime
from config import *
from database import load_json, save_json, load_goals, save_goals, update_data, load_data, save_data, compute_metrics, load_nutrition_data, save_nutrition_data, update_nutrition_data, delete_nutrition_data, load_sport_tests_data, save_sport_tests_data, update_sport_tests_data, load_blood_tests_data, save_blood_tests_data, update_blood_tests_data
import base64
import io
import os
from scipy import stats

# --- Definierte Farbpalette für Konsistenz ---
COLORS = {
    "hrv": "lightblue",
    "resting_hr": "red",
    "steps": "blue",
    "duration": "green",
    "rpe": "orange",
    "active_kcal": "gray",
    "intake": "red",
    "burn": "blue",
    "mood": "dodgerblue",
    "motivation": "seagreen",
    "energy": "gold",
    "stress": "red",
    "bp_sys": "red",
    "bp_dia": "blue",
    "trend": "rgba(255,255,255,0.4)",
    "omnivor": "#6C757D",  # Grau für Omnivor
    "vegan": "#28A745",     # Grün für Vegan
    "protein": "mediumseagreen",
    "carbs": "orange",
    "fat": "gold",
    "sleep": "mediumpurple",
}

def load_demo_csv_bundle():
    """Lädt die Demo-Daten aus den CSV-Dateien und speichert sie in der Datenbank."""
    try:
        # 1. Tageswerte laden
        daily_demo_path = os.path.join(BASE_DIR, "daily_demo.csv")
        if os.path.exists(daily_demo_path):
            daily_df = pd.read_csv(daily_demo_path)
            # Datumsspalte konvertieren
            daily_df["date"] = pd.to_datetime(daily_df["date"]).dt.date
            # Metriken berechnen
            daily_df = compute_metrics(daily_df)
            # Speichern
            save_data(daily_df)
        
        # 2. Ernährungstagebuch laden
        nutrition_demo_path = os.path.join(BASE_DIR, "nutrition_demo.csv")
        if os.path.exists(nutrition_demo_path):
            nutrition_df = pd.read_csv(nutrition_demo_path)
            # Datumsspalte konvertieren
            nutrition_df["date"] = pd.to_datetime(nutrition_df["date"]).dt.date
            # Speichern
            save_nutrition_data(nutrition_df)
        
        # 3. Bluttests laden
        blood_demo_path = os.path.join(BASE_DIR, "blood_demo.csv")
        if os.path.exists(blood_demo_path):
            blood_df = pd.read_csv(blood_demo_path)
            # Datumsspalte konvertieren
            blood_df["test_date"] = pd.to_datetime(blood_df["test_date"]).dt.date
            # Speichern
            save_blood_tests_data(blood_df)
        
        # 4. Sporttests laden
        sport_demo_path = os.path.join(BASE_DIR, "sport_demo.csv")
        if os.path.exists(sport_demo_path):
            sport_df = pd.read_csv(sport_demo_path)
            # Datumsspalte konvertieren
            sport_df["test_date"] = pd.to_datetime(sport_df["test_date"]).dt.date
            # Speichern
            save_sport_tests_data(sport_df)
        
        return True
    except Exception as e:
        st.error(f"Fehler beim Laden der Demo-Daten: {e}")
        return False

def generate_demo_data():
    nutrition_data = []  # Initialisierung für Demo-Ernährungsdaten

    """Erzeugt synthetische Demodaten für alle Bereiche der App."""
    # Parameter für die Demodaten
    seed = 42
    mode = "trend"  # "neutral" oder "trend"
    trend_strength = 0.7  # 0.0 bis 1.0
    
    np.random.seed(seed)
    
    # Startdatum für die Demodaten
    start_date = date.today() - timedelta(days=56)
    
    # 1. Tageswerte (56 Tage)
    daily_data = []
    
    # Basiswerte für die omnivore Phase
    base_body_weight = 75.0
    base_bp_sys = 125
    base_bp_dia = 80
    base_energy = 7.0
    base_mood = 7.0
    base_motivation = 7.0
    base_concentration = 7.0
    
    # Basiswerte für die vegane Phase (mit leichten Veränderungen)
    vegan_body_weight_change = -1.0  # -1.0 kg
    vegan_bp_sys_change = -5  # -5 mmHg
    vegan_bp_dia_change = -3  # -3 mmHg
    
    # Nährstoffbasiswerte
    base_intake_kcal = 2400
    base_carbs_g = 250
    base_protein_g = 120
    base_fat_g = 80
    base_water_ml = 2500

    # --- Tageswerte synthetisch erzeugen (56 Tage) ---
    for day in range(1, 57):
        current_date = start_date + timedelta(days=day - 1)
        is_vegan = day > 28
        phase = "Vegan" if is_vegan else "Omnivor"

        # Basis je Phase
        body_weight = base_body_weight + (vegan_body_weight_change if is_vegan else 0.0) + np.random.normal(0, 0.2)
        bp_sys = base_bp_sys + (vegan_bp_sys_change if is_vegan else 0) + np.random.normal(0, 2)
        bp_dia = base_bp_dia + (vegan_bp_dia_change if is_vegan else 0) + np.random.normal(0, 2)

        # Alltags-/Subjektivwerte
        sleep_hours = np.clip(7.2 + np.random.normal(0, 0.6), 4.5, 9.5)
        sleep_score = int(np.clip(78 + np.random.normal(0, 8), 40, 100))
        total_steps = int(np.clip(8500 + np.random.normal(0, 1800), 1000, 25000))
        total_kcal_burn = int(np.clip(2400 + np.random.normal(0, 250), 1200, 5000))

        intake_kcal = int(np.clip(base_intake_kcal + (50 if is_vegan else 0) + np.random.normal(0, 150), 1200, 5000))
        carbs_g = int(np.clip(base_carbs_g + (20 if is_vegan else 0) + np.random.normal(0, 25), 0, 800))
        protein_g = int(np.clip(base_protein_g + (-10 if is_vegan else 0) + np.random.normal(0, 15), 0, 400))
        fat_g = int(np.clip(base_fat_g + (-5 if is_vegan else 0) + np.random.normal(0, 10), 0, 300))
        water_ml = int(np.clip(base_water_ml + np.random.normal(0, 300), 0, 10000))

        hrv_sleep_avg = float(np.clip(45 + np.random.normal(0, 8), 15, 120))
        rhr_sleep_avg = float(np.clip(55 + np.random.normal(0, 6), 35, 95))
        rhr_sleep_min = float(np.clip(rhr_sleep_avg - abs(np.random.normal(4, 2)), 30, 90))
        spo2_sleep_avg = float(np.clip(96 + np.random.normal(0, 1.0), 85, 100))
        spo2_sleep_min = float(np.clip(spo2_sleep_avg - abs(np.random.normal(1.5, 0.8)), 80, 100))
        deep_sleep_hours = float(np.clip(1.6 + np.random.normal(0, 0.3), 0.2, 3.5))
        deep_sleep_percent = float(np.clip(20 + np.random.normal(0, 4), 5, 45))
        awakenings = int(np.clip(2 + abs(np.random.normal(0, 1)), 0, 12))

        morning_pulse = float(np.clip(58 + np.random.normal(0, 6), 35, 110))
        hrv_day_avg = float(np.clip(hrv_sleep_avg + np.random.normal(0, 4), 10, 140))
        spo2_day_avg = float(np.clip(96 + np.random.normal(0, 1.0), 85, 100))
        stress_avg = float(np.clip(35 + np.random.normal(0, 10), 0, 100))
        stress_peak = float(np.clip(stress_avg + abs(np.random.normal(15, 10)), 0, 100))

        energy = float(np.clip(base_energy + (0.2 if is_vegan else 0) + np.random.normal(0, 0.7), 1, 10))
        mood = float(np.clip(base_mood + np.random.normal(0, 0.7), 1, 10))
        motivation = float(np.clip(base_motivation + np.random.normal(0, 0.8), 1, 10))
        concentration = float(np.clip(base_concentration + np.random.normal(0, 0.7), 1, 10))

        daily_row = {
            "date": current_date,
            "weekday": "",  # wird in compute_metrics gesetzt
            "phase": phase,
            "sleep_hours": round(float(sleep_hours), 1),
            "sleep_score": int(sleep_score),
            "hrv_sleep_avg": round(float(hrv_sleep_avg), 1),
            "rhr_sleep_avg": round(float(rhr_sleep_avg), 1),
            "rhr_sleep_min": round(float(rhr_sleep_min), 1),
            "spo2_sleep_avg": round(float(spo2_sleep_avg), 1),
            "spo2_sleep_min": round(float(spo2_sleep_min), 1),
            "deep_sleep_hours": round(float(deep_sleep_hours), 2),
            "deep_sleep_percent": round(float(deep_sleep_percent), 1),
            "awakenings": int(awakenings),
            "total_steps": int(total_steps),
            "total_kcal_burn": int(total_kcal_burn),
            "intake_kcal": int(intake_kcal),
            "carbs_g": int(carbs_g),
            "protein_g": int(protein_g),
            "fat_g": int(fat_g),
            "water_ml": int(water_ml),
            "morning_pulse": round(float(morning_pulse), 1),
            "hrv_day_avg": round(float(hrv_day_avg), 1),
            "spo2_day_avg": round(float(spo2_day_avg), 1),
            "bp_sys": int(round(float(bp_sys))),
            "bp_dia": int(round(float(bp_dia))),
            "body_weight": round(float(body_weight), 1),
            "stress_avg": round(float(stress_avg), 1),
            "stress_peak": round(float(stress_peak), 1),
            "energy": round(float(energy), 1),
            "mood": round(float(mood), 1),
            "motivation": round(float(motivation), 1),
            "concentration": round(float(concentration), 1),
            "note": "DEMO (synthetisch) – Szenario nach Literatur, kein Messwert",
            "last_modified": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }
        daily_data.append(daily_row)

    # Tageswerte speichern (inkl. berechneter Metriken)
    daily_df = pd.DataFrame(daily_data)
    daily_df = compute_metrics(daily_df)
    save_data(daily_df)

    
    
    # Mahlzeitentexte für omnivore Phase
    omnivor_breakfast = [
        "Haferflocken mit Milch und Beeren",
        "Rührei mit Speck und Toast",
        "Joghurt mit Müsli und Honig",
        "Vollkornbrot mit Butter und Käse",
    ]
    omnivor_lunch = [
        "Hühnerschnitzel mit Kartoffelsalat",
        "Spaghetti Bolognese mit Parmesan",
        "Schnitzel mit Pommes und Salat",
        "Linsensuppe mit Wurst und Brot",
    ]
    omnivor_dinner = [
        "Gebratenes Lachsfilet mit Reis und Gemüse",
        "Schweinebraten mit Knödeln und Sauerkraut",
        "Hähnchen-Curry mit Basmatireis",
        "Rindersteak mit Kartoffeln und Kräuterbutter",
    ]
    
    # Mahlzeitentexte für vegane Phase
    vegan_breakfast = [
        "Haferflocken mit Sojamilch und Beeren",
        "Tofu-Rührei mit Vollkorntoast",
        "Sojajoghurt mit Müsli und Ahornsirup",
        "Vollkornbrot mit Avocado und Tomaten",
    ]
    vegan_lunch = [
        "Linsen-Bolognese mit Vollkornnudeln",
        "Kichererbsen-Curry mit Basmatireis",
        "Gemüse-Eintopf mit Vollkornbrot",
        "Burger mit Sojafrikadelle und Salat",
    ]
    vegan_dinner = [
        "Gebratenes Tofu mit Reis und Gemüse",
        "Veganes Chili mit Mais und Brot",
        "Gemüse-Quinoa-Pfanne mit Avocado",
        "Vegane Lasagne mit Tomatensauce",
    ]
    vegan_supplements = "Vitamin B12, DHA (Algenöl), Vitamin D3"
    
    for day in range(1, 57):
        current_date = start_date + timedelta(days=day-1)

        # Index (damit alle Listeneinträge vorkommen)
        idx = (day - 1)

        # Phase bestimmen + Mahlzeiten + Snacks
        if day <= 28:
            phase = "Omnivor"
            breakfast = omnivor_breakfast[idx % len(omnivor_breakfast)]
            lunch = omnivor_lunch[idx % len(omnivor_lunch)]
            dinner = omnivor_dinner[idx % len(omnivor_dinner)]
            supplements = "Multivitamin, Magnesium"

            omnivor_snack_1 = ["Apfel und Nüsse", "Joghurt", "Banane", "Müsliriegel"]
            omnivor_snack_2 = ["Vollkornbrot mit Käse", "Nüsse", "Topfen mit Beeren", "Butterbrot"]
            snack_1 = omnivor_snack_1[idx % len(omnivor_snack_1)]
            snack_2 = omnivor_snack_2[idx % len(omnivor_snack_2)]
        else:
            phase = "Vegan"
            breakfast = vegan_breakfast[idx % len(vegan_breakfast)]
            lunch = vegan_lunch[idx % len(vegan_lunch)]
            dinner = vegan_dinner[idx % len(vegan_dinner)]
            supplements = vegan_supplements

            vegan_variants = [
                {"snack_1": "Banane und Nüsse", "snack_2": "Vollkornbrot mit Hummus"},
                {"snack_1": "Smoothie aus Banane, Haferdrink und Samen", "snack_2": "Sojajoghurt mit Nüssen"},
            ]
            variant = vegan_variants[(day - 29) % 2]
            snack_1 = variant["snack_1"]
            snack_2 = variant["snack_2"]

        # Nährstoffwerte (aus den Tageswerten übernehmen)
        daily_row = daily_df[daily_df["date"] == current_date].iloc[0]

        nutrition_row = {
            "date": current_date,
            "phase": phase,
            "breakfast": breakfast,
            "snack_1": snack_1,
            "lunch": lunch,
            "snack_2": snack_2,
            "dinner": dinner,
            "supplements": supplements,
            "nutrition_note": "DEMO (synthetisch) – Szenario nach Literatur, kein Messwert",
            "intake_kcal": daily_row["intake_kcal"],
            "carbs_g": daily_row["carbs_g"],
            "protein_g": daily_row["protein_g"],
            "fat_g": daily_row["fat_g"],
            "water_ml": daily_row["water_ml"],
            "last_modified": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        nutrition_data.append(nutrition_row)
    
    # Ernährungsdaten speichern
    nutrition_df = pd.DataFrame(nutrition_data)
    save_nutrition_data(nutrition_df)
    
    # 3. Bluttests (2 Tests)
    blood_test_data = []
    
    # Baseline-Test (Tag 1)
    baseline_date = start_date
    baseline_row = {
        "test_date": baseline_date,
        "test_type": "Baseline (Omnivor)",
        "notes": "DEMO (synthetisch) – Szenario nach Literatur, kein Messwert",
        "pdf_file": "",
        # Rotes & weißes Blutbild
        "hemoglobin": 14.5 + np.random.normal(0, 0.3),
        "erythrocytes": 4.8 + np.random.normal(0, 0.2),
        "mcv": 90 + np.random.normal(0, 3),
        "mch": 30 + np.random.normal(0, 1),
        "thrombocytes": 250 + np.random.normal(0, 20),
        "leukocytes": 6.5 + np.random.normal(0, 0.5),
        "segment": 55 + np.random.normal(0, 3),
        "monocytes": 6 + np.random.normal(0, 1),
        "lymphocytes": 30 + np.random.normal(0, 2),
        "basophils": 1 + np.random.normal(0, 0.2),
        "eosinophils": 3 + np.random.normal(0, 0.5),
        # Blutchemie
        "alat": 25 + np.random.normal(0, 3),
        "asat": 22 + np.random.normal(0, 3),
        "creatinine": 0.9 + np.random.normal(0, 0.1),
        "egfr": 95 + np.random.normal(0, 5),
        "iron": 90 + np.random.normal(0, 10),
        "transferrin_saturation": 30 + np.random.normal(0, 3),
        "gamma_gt": 20 + np.random.normal(0, 3),
        "ap": 65 + np.random.normal(0, 5),
        "iron_saturation": 250 + np.random.normal(0, 20),
        "ebk": 4.2 + np.random.normal(0, 0.2),
        "ferritin": 80 + np.random.normal(0, 10),
        "transferrin": 2.8 + np.random.normal(0, 0.2),
        # Blutfette
        "cholesterol": 210 + np.random.normal(0, 10),
        "triglycerides": 120 + np.random.normal(0, 15),
        "ldl_chol": 130 + np.random.normal(0, 10),
        # Elektrolyte
        "sodium": 140 + np.random.normal(0, 2),
        "calcium": 2.4 + np.random.normal(0, 0.1),
        "potassium": 4.2 + np.random.normal(0, 0.1),
        # Schilddrüsenhormone
        "tsh_basal": 1.8 + np.random.normal(0, 0.2),
        # Harnbefund
        "hk": 0.1 + np.random.normal(0, 0.02),
        "last_modified": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    blood_test_data.append(baseline_row)
    
    # Post-Vegan-Test (Tag 56)
    post_vegan_date = start_date + timedelta(days=55)
    post_vegan_row = {
        "test_date": post_vegan_date,
        "test_type": "Vegan-Test",
        "notes": "DEMO (synthetisch) – Szenario nach Literatur, kein Messwert",
        "pdf_file": "",
        # Rotes & weißes Blutbild (kaum Veränderung)
        "hemoglobin": 14.3 + np.random.normal(0, 0.3),
        "erythrocytes": 4.7 + np.random.normal(0, 0.2),
        "mcv": 90 + np.random.normal(0, 3),
        "mch": 30 + np.random.normal(0, 1),
        "thrombocytes": 245 + np.random.normal(0, 20),
        "leukocytes": 6.3 + np.random.normal(0, 0.5),
        "segment": 54 + np.random.normal(0, 3),
        "monocytes": 6 + np.random.normal(0, 1),
        "lymphocytes": 31 + np.random.normal(0, 2),
        "basophils": 1 + np.random.normal(0, 0.2),
        "eosinophils": 3 + np.random.normal(0, 0.5),
        # Blutchemie
        "alat": 23 + np.random.normal(0, 3),
        "asat": 20 + np.random.normal(0, 3),
        "creatinine": 0.9 + np.random.normal(0, 0.1),
        "egfr": 96 + np.random.normal(0, 5),
        "iron": 85 + np.random.normal(0, 10),
        "transferrin_saturation": 28 + np.random.normal(0, 3),
        "gamma_gt": 18 + np.random.normal(0, 3),
        "ap": 62 + np.random.normal(0, 5),
        "iron_saturation": 240 + np.random.normal(0, 20),
        "ebk": 4.1 + np.random.normal(0, 0.2),
        "ferritin": 75 + np.random.normal(0, 10),
        "transferrin": 2.9 + np.random.normal(0, 0.2),
        # Blutfette (moderate Veränderung)
        "cholesterol": 190 + np.random.normal(0, 10),  # ↓
        "triglycerides": 110 + np.random.normal(0, 15),  # ↓
        "ldl_chol": 115 + np.random.normal(0, 10),  # ↓
        # Elektrolyte
        "sodium": 139 + np.random.normal(0, 2),
        "calcium": 2.4 + np.random.normal(0, 0.1),
        "potassium": 4.1 + np.random.normal(0, 0.1),
        # Schilddrüsenhormone
        "tsh_basal": 1.9 + np.random.normal(0, 0.2),
        # Harnbefund
        "hk": 0.1 + np.random.normal(0, 0.02),
        "last_modified": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    blood_test_data.append(post_vegan_row)
    
    # Bluttest-Daten speichern
    blood_test_df = pd.DataFrame(blood_test_data)
    save_blood_tests_data(blood_test_df)
    
    # 4. Sporttests (4 Tests)
    sport_test_data = []
    
    # Baseline-Tests (Tag 1)
    baseline_date = start_date
    baseline_cooper = {
        "test_date": baseline_date,
        "test_type": "Baseline (Omnivor)",
        "general_notes": "DEMO (synthetisch) – keine Aussage zur Leistungsfähigkeit",
        # Cooper-Test
        "cooper_distance": 2400 + np.random.normal(0, 50),
        "cooper_avg_hr": 165 + np.random.normal(0, 5),
        "cooper_max_hr": 180 + np.random.normal(0, 5),
        "cooper_pace": 5.0 + np.random.normal(0, 0.2),
        "cooper_kcal": 650 + np.random.normal(0, 20),
        "cooper_warmup": 5 + np.random.normal(0, 1),
        "cooper_aerob": 6 + np.random.normal(0, 1),
        "cooper_anaerob": 1 + np.random.normal(0, 0.5),
        "cooper_intensive": 0,
        "cooper_photo": "",
        # 5km-Lauf
        "run5k_time": "25:30",
        "run5k_avg_hr": 170 + np.random.normal(0, 5),
        "run5k_max_hr": 185 + np.random.normal(0, 5),
        "run5k_pace": 5.1 + np.random.normal(0, 0.2),
        "run5k_kcal": 350 + np.random.normal(0, 20),
        "run5k_warmup": 5 + np.random.normal(0, 1),
        "run5k_aerob": 20 + np.random.normal(0, 2),
        "run5k_anaerob": 5 + np.random.normal(0, 1),
        "run5k_intensive": 0,
        "run5k_photo": "",
        # Liegestütze
        "pushups_reps": 35 + np.random.normal(0, 3),
        "pushups_avg_hr": 120 + np.random.normal(0, 5),
        "pushups_max_hr": 140 + np.random.normal(0, 5),
        "pushups_photo": "",
        # Plank
        "plank_time": "2:30",
        "plank_avg_hr": 110 + np.random.normal(0, 5),
        "plank_max_hr": 125 + np.random.normal(0, 5),
        "plank_photo": "",
        # Burpee-Test
        "burpee_reps": 45 + np.random.normal(0, 3),
        "burpee_avg_hr": 150 + np.random.normal(0, 5),
        "burpee_max_hr": 170 + np.random.normal(0, 5),
        "burpee_photo": "",
        # VO2max-Test
        "vo2max_value": 45 + np.random.normal(0, 2),
        "vo2max_avg_hr": 175 + np.random.normal(0, 5),
        "vo2max_max_hr": 190 + np.random.normal(0, 5),
        "vo2max_duration": "12:00",
        "vo2max_speed": "12.0 km/h",
        "vo2max_photo": "",
        "last_modified": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    sport_test_data.append(baseline_cooper)
    
    # Mid-Omnivor-Test (Tag 14)
    mid_omnivor_date = start_date + timedelta(days=13)
    mid_omnivor_row = baseline_cooper.copy()
    mid_omnivor_row["test_date"] = mid_omnivor_date
    mid_omnivor_row["test_type"] = "Mid-Omnivor (2W)"
    mid_omnivor_row["cooper_distance"] = 2450 + np.random.normal(0, 50)
    mid_omnivor_row["run5k_time"] = "25:15"
    mid_omnivor_row["pushups_reps"] = 36 + np.random.normal(0, 3)
    mid_omnivor_row["plank_time"] = "2:35"
    mid_omnivor_row["burpee_reps"] = 46 + np.random.normal(0, 3)
    mid_omnivor_row["vo2max_value"] = 45.5 + np.random.normal(0, 2)
    mid_omnivor_row["last_modified"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    sport_test_data.append(mid_omnivor_row)
    
    # Early-Vegan-Test (Tag 42)
    early_vegan_date = start_date + timedelta(days=41)
    early_vegan_row = baseline_cooper.copy()
    early_vegan_row["test_date"] = early_vegan_date
    early_vegan_row["test_type"] = "Early-Vegan (2W)"
    early_vegan_row["cooper_distance"] = 2420 + np.random.normal(0, 50)
    early_vegan_row["run5k_time"] = "25:40"
    early_vegan_row["pushups_reps"] = 34 + np.random.normal(0, 3)
    early_vegan_row["plank_time"] = "2:25"
    early_vegan_row["burpee_reps"] = 44 + np.random.normal(0, 3)
    early_vegan_row["vo2max_value"] = 44.5 + np.random.normal(0, 2)
    early_vegan_row["last_modified"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    sport_test_data.append(early_vegan_row)
    
    # Post-Vegan-Test (Tag 56)
    post_vegan_date = start_date + timedelta(days=55)
    post_vegan_row = baseline_cooper.copy()
    post_vegan_row["test_date"] = post_vegan_date
    post_vegan_row["test_type"] = "Post-Vegan (4W)"
    post_vegan_row["cooper_distance"] = 2380 + np.random.normal(0, 50)
    post_vegan_row["run5k_time"] = "26:00"
    post_vegan_row["pushups_reps"] = 33 + np.random.normal(0, 3)
    post_vegan_row["plank_time"] = "2:20"
    post_vegan_row["burpee_reps"] = 43 + np.random.normal(0, 3)
    post_vegan_row["vo2max_value"] = 44 + np.random.normal(0, 2)
    post_vegan_row["last_modified"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    sport_test_data.append(post_vegan_row)
    
    # Sporttest-Daten speichern
    sport_test_df = pd.DataFrame(sport_test_data)
    save_sport_tests_data(sport_test_df)
    
    return True

def render_csv_import_section():
    """Rendert den Bereich für den CSV-Import von Tageswerten."""
    st.subheader("📥 CSV-Import für Tageswerte")
    st.markdown("Lade hier eine CSV-Datei hoch, um deine Tageswerte zu importieren. Die Spalten müssen anschließend den richtigen Feldern in der App zugeordnet werden.")
    
    uploaded_file = st.file_uploader(
        "CSV-Datei auswählen",
        type=["csv"],
        help="Die Datei muss eine Tabelle mit deinen Messwerten enthalten."
    )

    if uploaded_file is not None:
        try:
            # Versuche, die CSV mit verschiedenen Trennern zu lesen
            import_df = None
            for delimiter in [',', ';']:
                try:
                    # Versuche zuerst mit Komma als Trennzeichen
                    import_df = pd.read_csv(uploaded_file, delimiter=delimiter, encoding='utf-8')
                    # Wenn erfolgreich, prüfe auf Dezimalzeichen
                    if '.' not in import_df.select_dtypes(include=[np.number]).columns.to_string():
                        # Wenn kein Punkt in numerischen Spalten, versuche mit Komma als Dezimaltrennzeichen
                        try:
                            import_df = pd.read_csv(uploaded_file, delimiter=delimiter, decimal=',', encoding='utf-8')
                        except:
                            pass
                    break
                except:
                    continue
            
            if import_df is None:
                # Versuche mit verschiedenen Kodierungen
                for encoding in ['utf-8', 'latin1', 'iso-8859-1']:
                    try:
                        for delimiter in [',', ';']:
                            try:
                                import_df = pd.read_csv(uploaded_file, delimiter=delimiter, encoding=encoding)
                                # Wenn erfolgreich, prüfe auf Dezimalzeichen
                                if '.' not in import_df.select_dtypes(include=[np.number]).columns.to_string():
                                    # Wenn kein Punkt in numerischen Spalten, versuche mit Komma als Dezimaltrennzeichen
                                    try:
                                        import_df = pd.read_csv(uploaded_file, delimiter=delimiter, decimal=',', encoding=encoding)
                                    except:
                                        pass
                                break
                            except:
                                continue
                        if import_df is not None:
                            break
                    except:
                        continue
            
            if import_df is None:
                st.error("Konnte die Datei nicht lesen. Überprüfe das Format und die Kodierung.")
                return

            st.success("Datei erfolgreich geladen!")
            st.write("Vorschau der importierten Daten (erste 5 Zeilen):")
            st.dataframe(import_df.head())

            # Spaltenzuordnung
            st.markdown("---")
            st.subheader("🗺️ Spaltenzuordnung")
            st.markdown("Ordne jede Spalte aus deiner Datei der entsprechenden Spalte in der App zu.")

            # Alle Spalten aus COLUMNS zur Zuordnung anbieten
            key_columns = COLUMNS
            
            column_mapping = {}
            csv_columns = ["-- Spalte ignorieren --"] + list(import_df.columns)

            for col in key_columns:
                mapped_col = st.selectbox(
                    f"Spalte für '{col}'",
                    options=csv_columns,
                    key=f"map_{col}"
                )
                if mapped_col != "-- Spalte ignorieren --":
                    column_mapping[col] = mapped_col

            # Import-Button
            st.markdown("---")
            overwrite = st.checkbox("Vorhandene Einträge (gleiches Datum & Phase) überschreiben?", value=False, help="Wenn aktiviert, werden bestehende Einträge mit den Daten aus der CSV-Datei aktualisiert.")
            
            if st.button("Import starten", type="primary"):
                if not column_mapping.get("date") or not column_mapping.get("phase"):
                    st.error("Die Zuordnung für 'Datum' und 'Phase' ist zwingend erforderlich!")
                    return

                # DataFrame für den Import vorbereiten
                df_to_import = import_df[list(column_mapping.values())].copy()
                df_to_import = df_to_import.rename(columns={v: k for k, v in column_mapping.items()})

                # Datentypen bereinigen und konvertieren
                try:
                    # Versuche verschiedene Datumsformate
                    date_col = column_mapping["date"]
                    for date_format in ["%Y-%m-%d", "%d.%m.%Y", "%m/%d/%Y"]:
                        try:
                            df_to_import['date'] = pd.to_datetime(df_to_import['date'], format=date_format).dt.date
                            break
                        except:
                            continue
                    
                    # Wenn kein Format passt, versuche es ohne Format
                    if df_to_import['date'].dtype == 'object':
                        df_to_import['date'] = pd.to_datetime(df_to_import['date'], errors='coerce').dt.date
                    
                    # Prüfe auf ungültige Daten
                    if df_to_import['date'].isnull().any():
                        st.warning("Einige Daten konnten nicht konvertiert werden und werden ignoriert.")
                        df_to_import = df_to_import.dropna(subset=['date'])
                    
                except Exception as e:
                    st.error(f"Fehler beim Konvertieren des Datums: {e}")
                    return
                
                # Phase validieren
                df_to_import['phase'] = df_to_import['phase'].astype(str).str.title()
                if not df_to_import['phase'].isin(['Omnivor', 'Vegan']).all():
                    st.warning("Die Spalte 'Phase' enthält Werte, die nicht 'Omnivor' oder 'Vegan' sind. Diese werden ignoriert.")
                    df_to_import = df_to_import[df_to_import['phase'].isin(['Omnivor', 'Vegan'])]

                # Numerische Spalten konvertieren
                numeric_cols = [col for col in COLUMNS if col not in ['date', 'phase', 'weekday', 'note', 'last_modified']]
                for col in numeric_cols:
                    if col in df_to_import.columns:
                        df_to_import[col] = pd.to_numeric(df_to_import[col], errors='coerce')

                # Daten importieren
                existing_df = load_data()
                new_count = 0
                updated_count = 0

                with st.spinner("Daten werden verarbeitet..."):
                    for index, row in df_to_import.iterrows():
                        date_val = row['date']
                        phase_val = row['phase']
                        
                        # Prüfen, ob Eintrag bereits existiert
                        mask = (existing_df['date'] == date_val) & (existing_df['phase'] == phase_val)
                        
                        row_data = row.to_dict()
                        row_data['last_modified'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                        if mask.any():
                            if overwrite:
                                # Update bestehenden Eintrag
                                for key, value in row_data.items():
                                    if key in existing_df.columns:
                                        existing_df.loc[mask, key] = value
                                updated_count += 1
                        else:
                            # Neuen Eintrag hinzufügen
                            new_row_df = pd.DataFrame([row_data])
                            existing_df = pd.concat([existing_df, new_row_df], ignore_index=True)
                            new_count += 1
                
                    # Metriken neu berechnen und speichern
                    try:
                        final_df = compute_metrics(existing_df)
                        save_data(final_df)
                    except Exception as e:
                        st.error(f"Fehler bei der Berechnung der Metriken: {e}")
                        return

                st.success(f"✅ Import abgeschlossen! {new_count} neue Einträge hinzugefügt, {updated_count} Einträge aktualisiert.")
                st.rerun()

        except Exception as e:
            st.error(f"Ein Fehler ist aufgetreten: {e}")
            st.exception(e)

def render_settings_expander(settings: dict, mapping: dict):
    """Rendert den Einstellungs-Bereich."""
    with st.expander("⚙️ Einstellungen – Auto-Import, Daten & Ziele"):
        # NEU: Demo-Daten Button
        st.markdown("### 🧪 Szenario-Demo")
        st.markdown("Szenario-Daten dienen nur UI/Diagramm-Test und sind keine Ergebnisse des Selbstversuchs.")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🧪 Szenario-Demo laden (4W Omnivor → 4W Vegan)", key="load_demo_data_button"):
                with st.spinner("Demodaten werden generiert..."):
                    generate_demo_data()
                    st.success("Demodaten wurden erfolgreich geladen!")
                    st.rerun()
        
        with col2:
            if st.button("🧪 Demo-Daten aus CSV laden", key="load_demo_csv_button"):
                with st.spinner("Demo-Daten aus CSV werden geladen..."):
                    if load_demo_csv_bundle():
                        st.success("Demo-Daten aus CSV wurden erfolgreich geladen!")
                        st.rerun()
        
        st.markdown("---")  # Trennlinie
        
        # NEU: CSV-Import Sektion
        render_csv_import_section()
        st.markdown("---") # Trennlinie
        
        st.subheader("Auto-Import")
        settings["auto_import_enabled"] = st.checkbox("Auto-Import einschalten", value=settings.get("auto_import_enabled", False), key="auto_import_enabled_checkbox")
        settings["watch_folder"] = st.text_input("CSV-Ordner (iCloud/Health/Ring/Yazio)", value=settings.get("watch_folder", ""), key="watch_folder_input")
        settings["filename_glob"] = st.text_input("Dateimuster", value=settings.get("filename_glob", "*.csv"), key="filename_glob_input")

        st.subheader("Datenmanagement")
        c1, c2 = st.columns(2)
        if c1.button("💣 Alle Daten löschen", key="delete_all_data_button"):
            from database import save_data, empty_df, save_nutrition_data, empty_nutrition_df, save_sport_tests_data, empty_sport_tests_df, save_blood_tests_data, empty_blood_tests_df
            save_data(empty_df())
            save_nutrition_data(empty_nutrition_df())
            save_sport_tests_data(empty_sport_tests_df())
            save_blood_tests_data(empty_blood_tests_df())
            st.success("Alle Daten wurden gelöscht.")
            st.rerun()
        if c2.button("🧹 Alle Daten vor HEUTE löschen", key="delete_old_data_button"):
            from database import load_data, save_data, load_nutrition_data, save_nutrition_data, load_sport_tests_data, save_sport_tests_data, load_blood_tests_data, save_blood_tests_data
            df = load_data()
            nf = load_nutrition_data()
            sf = load_sport_tests_data()
            bf = load_blood_tests_data()
            today = date.today()
            if not df.empty:
                df = df[pd.to_datetime(df["date"]).dt.date >= today]
                save_data(df)
            if not nf.empty:
                nf = nf[pd.to_datetime(nf["date"]).dt.date >= today]
                save_nutrition_data(nf)
            if not sf.empty:
                sf = sf[pd.to_datetime(sf["test_date"]).dt.date >= today]
                save_sport_tests_data(sf)
            if not bf.empty:
                bf = bf[pd.to_datetime(bf["test_date"]).dt.date >= today]
                save_blood_tests_data(bf)
            st.success("Ältere Daten wurden entfernt.")
            st.rerun()
        
        if st.button("Einstellungen speichern", key="save_settings_button"):
            from config import SETTINGS_FILE
            save_json(SETTINGS_FILE, settings)
            st.success("Gespeichert")

        st.subheader("Persönliche Ziele")
        goals = load_goals()
        with st.form(key="goals_form_key"):
            col1, col2 = st.columns(2)
            goals["sleep_hours_goal"] = col1.number_input("Ziel: Schlafdauer (h)", value=goals.get("sleep_hours_goal", 8.0), step=0.5, key="sleep_hours_goal_input")
            goals["total_steps_goal"] = col2.number_input("Ziel: Gesamtschritte", value=goals.get("total_steps_goal", 10000), step=500, key="total_steps_goal_input")
            goals["intake_kcal_goal"] = col1.number_input("Ziel: Kalorienaufnahme (kcal)", value=goals.get("intake_kcal_goal", 2500), step=50, key="intake_kcal_goal_input")
            goals["protein_g_per_kg_goal"] = col2.number_input("Ziel: Protein (g/kg Körpergewicht)", value=goals.get("protein_g_per_kg_goal", 1.6), step=0.1, key="protein_g_per_kg_goal_input")
            if st.form_submit_button("Ziele speichern", key="save_goals_button"):
                save_goals(goals)
                st.success("Ziele wurden gespeichert!")

def render_daily_form():
    """Rendert das Tagesformular (ohne Training, mit Energie & Nährstoffen)."""
    with st.form(key="daily_form_key"):
        st.subheader("1️⃣ Schlaf & Regeneration")
        r1, r2, r3 = st.columns([1, 1, 1])
        d = r1.date_input("Datum", value=date.today(), key="daily_date_input")
        phase = r2.selectbox("Phase", ["Omnivor", "Vegan"], key="daily_phase_selectbox")
        sh_h = r3.number_input("Schlafdauer – Stunden", 0, 24, step=1, key="daily_sh_h_input")
        r4, r5, r6 = st.columns([1, 1, 1])
        sh_m = r4.number_input("Schlafdauer – Minuten", 0, 59, step=5, key="daily_sh_m_input")
        ss = r5.number_input("Schlafqualität (0–100)", 0, 100, step=1, key="daily_ss_input")
        hrv_s = r6.number_input("HRV im Schlaf (Ø, ms)", 0, 300, step=1, key="daily_hrv_s_input")
        r7,r8,r9,r10=st.columns(4)
        rhr_s=r7.number_input("Ruhepuls Schlaf (Ø, bpm)",20,120,step=1, key="daily_rhr_s_input")
        rhr_s_min=r8.number_input("Ruhepuls Schlaf (Minimum, bpm)",20,120,step=1, key="daily_rhr_s_min_input")
        spo2_s_avg=r9.number_input("SpO₂ Schlaf Ø (%)",80,100,step=1, key="daily_spo2_s_avg_input")
        spo2_s_min=r10.number_input("SpO₂ Schlaf Min (%)",70,100,step=1, key="daily_spo2_s_min_input")
        r11,r12,r13=st.columns(3)
        deep_hh=r11.number_input("Tiefschlaf – Stunden",0,24,step=1, key="daily_deep_hh_input")
        deep_mm=r12.number_input("Tiefschlaf – Minuten",0,59,step=5, key="daily_deep_mm_input")
        deep_p=r13.number_input("Tiefschlaf (%)",0.0,100.0,step=0.5, key="daily_deep_p_input")
        awake_n=st.number_input("Aufwachhäufigkeit (Anzahl)",0,50,step=1, key="daily_awake_n_input")
        
        st.markdown("---"); 
        st.subheader("2️⃣ Aktivität (Alltag)")
        a1,a2=st.columns(2)
        total_steps=a1.number_input("Gesamtschritte",0,50000,step=100, key="daily_total_steps_input")
        total_kcal_burn=a2.number_input("Gesamtkalorienverbrauch (kcal)",0,5000,step=10, key="daily_total_kcal_burn_input")
        
        st.markdown("---"); 
        st.subheader("3️⃣ Energie & Nährstoffe")
        e1, e2, e3, e4 = st.columns(4)
        intake = e1.number_input("Kalorienaufnahme (kcal)", 0, 20000, step=10, key="daily_nutrition_intake_input")
        carbs = e2.number_input("Kohlenhydrate (g)", 0, 1500, step=5, key="daily_nutrition_carbs_input")
        protein = e3.number_input("Eiweiß (g)", 0, 500, step=1, key="daily_nutrition_protein_input")
        fat = e4.number_input("Fett (g)", 0, 300, step=1, key="daily_nutrition_fat_input")
        water = st.number_input("Wasseraufnahme (ml)", 0, 10000, step=50, key="daily_nutrition_water_input")
        
        st.markdown("---"); 
        st.subheader("4️⃣ Körper & Kreislauf")
        k1,k2,k3,k4=st.columns(4)
        morning_pulse=k1.number_input("Morgenpuls (nach Aufwachen, Ruhe) – bpm",20,120,step=1, key="daily_morning_pulse_input")
        hrv_day=k2.number_input("HRV Tagesdurchschnitt (ms)",0,300,step=1, key="daily_hrv_day_input")
        bp_sys=k3.number_input("Blutdruck sys (mmHg)",70,200,step=1, key="daily_bp_sys_input")
        bp_dia=k4.number_input("Blutdruck dia (mmHg)",40,140,step=1, key="daily_bp_dia_input")
        k5,k6,k7,k8=st.columns(4)
        spo2_day=k5.number_input("SpO₂ Tag Ø (%)",80,100,step=1, key="daily_spo2_day_input")
        weight=k6.number_input("Körpergewicht (kg)",0.0,500.0,step=0.1, format="%.1f", key="daily_weight_input")
        stress_avg=k7.number_input("Stresslevel Ø (0–100)",0,100,step=1, key="daily_stress_avg_body_input")
        stress_peak=k8.number_input("Stress Spitzenwert (0–100)",0,100,step=1, key="daily_stress_peak_body_input")
        
        st.markdown("---"); 
        st.subheader("5️⃣ Wohlbefinden & Notizen")
        w1,w2,w3,w4=st.columns(4)
        energy=w1.number_input("Energielevel (1–10)",1,10,step=1, key="daily_energy_input")
        mood=w2.number_input("Stimmung (1–10)",1,10,step=1, key="daily_mood_input")
        motivation=w3.number_input("Motivation (1–10)",1,10,step=1, key="daily_motivation_input")
        concentration=w4.number_input("Konzentration (1–10)",1,10,step=1, key="daily_concentration_input")
        note=st.text_input("Kommentar / Bemerkung","", key="daily_note_input")
        
        ok = st.form_submit_button("Tag speichern", key="daily_save_day_button")
    
    return ok, locals()

def render_nutrition_form():
    """Rendert das Ernährungstagebuch-Formular (Mahlzeiten & Nährstoffe)."""
    with st.form(key="nutrition_form_key"):
        st.subheader("🍽️ Ernährungstagebuch")
        
        r1, r2 = st.columns(2)
        d = r1.date_input("Datum", value=date.today(), key="nutrition_form_date_input")
        phase = r2.selectbox("Phase", ["Omnivor", "Vegan"], key="nutrition_form_phase_selectbox")
        
        st.markdown("---")
        st.subheader("Mahlzeiten")
        
        # Mahlzeiten
        breakfast = st.text_area("Frühstück", key="nutrition_form_breakfast_input", placeholder="Beschreiben Sie Ihr Frühstück...")
        snack_1 = st.text_area("Zwischenmahlzeit (Vormittag)", key="nutrition_form_snack_1_input", placeholder="Beschreiben Sie Ihre Zwischenmahlzeit...")
        lunch = st.text_area("Mittagessen", key="nutrition_form_lunch_input", placeholder="Beschreiben Sie Ihr Mittagessen...")
        snack_2 = st.text_area("Zwischenmahlzeit (Nachmittag)", key="nutrition_form_snack_2_input", placeholder="Beschreiben Sie Ihre Zwischenmahlzeit...")
        dinner = st.text_area("Abendessen", key="nutrition_form_dinner_input", placeholder="Beschreiben Sie Ihr Abendessen...")
        
        st.markdown("---")
        st.subheader("Energie & Nährstoffe")
        
        e1, e2, e3, e4 = st.columns(4)
        intake = e1.number_input("Kalorienaufnahme (kcal)", 0, 20000, step=10, key="nutrition_form_nutrition_intake_input")
        carbs = e2.number_input("Kohlenhydrate (g)", 0, 1500, step=5, key="nutrition_form_nutrition_carbs_input")
        protein = e3.number_input("Eiweiß (g)", 0, 500, step=1, key="nutrition_form_nutrition_protein_input")
        fat = e4.number_input("Fett (g)", 0, 300, step=1, key="nutrition_form_nutrition_fat_input")
        
        e5, e6 = st.columns(2)
        water = e5.number_input("Wasseraufnahme (ml)", 0, 10000, step=50, key="nutrition_form_nutrition_water_input")
        supplements = e6.text_input("Supplements", key="nutrition_form_nutrition_supplements_input", placeholder="Vitamine, Mineralstoffe, etc.")
        
        st.markdown("---")
        nutrition_note = st.text_area("Bemerkungen", key="nutrition_form_nutrition_note_input", placeholder="Zusätzliche Anmerkungen zur Ernährung...")
        
        ok = st.form_submit_button("Ernährung speichern", key="nutrition_form_save_nutrition_button")
    
    return ok, locals()

def render_sport_tests_form():
    """Rendert das Sporttests-Formular."""
    with st.form(key="sport_tests_form_key"):
        st.subheader("🏃‍♂️ Sporttests")

        # Upload-Felder bewusst entfernt (nicht benötigt)
        cooper_photo = None
        run5k_photo = None
        pushups_photo = None
        plank_photo = None
        burpee_photo = None
        vo2max_photo = None
        
        # Allgemeine Eingaben
        col1, col2 = st.columns(2)
        test_date = col1.date_input("Datum des Sporttests", value=date.today(), key="sport_tests_date_input")
        test_type = col2.selectbox("Testtyp", ["Baseline (Omnivor)", "Vegan-Test"], key="sport_tests_type_selectbox")
        general_notes = st.text_area("Allgemeine Notizen", key="sport_tests_general_notes_input", placeholder="Allgemeine Anmerkungen zum Test...")
        
        # TEST 1 - Cooper-Test
        st.markdown("---")
        st.subheader("🔵 TEST 1 – Cooper-Test (12 Minuten)")
        col1, col2, col3, col4, col5 = st.columns(5)
        cooper_distance = col1.number_input("Distanz (m)", min_value=0, step=10, key="cooper_distance_input")
        cooper_avg_hr = col2.number_input("Durchschnittspuls (bpm)", min_value=0, max_value=250, step=1, key="cooper_avg_hr_input")
        cooper_max_hr = col3.number_input("Maximalpuls (bpm)", min_value=0, max_value=250, step=1, key="cooper_max_hr_input")
        cooper_pace = col4.number_input("Pace (min/km)", min_value=0.0, step=0.1, format="%.1f", key="cooper_pace_input")
        cooper_kcal = col5.number_input("Kalorien (kcal)", min_value=0, step=1, key="cooper_kcal_input")
        
        st.markdown("**Herzfrequenz-Zonen:**")
        col1, col2, col3, col4 = st.columns(4)
        cooper_warmup = col1.number_input("Warm-up (min)", min_value=0, step=1, key="cooper_warmup_input")
        cooper_aerob = col2.number_input("Aerob (min)", min_value=0, step=1, key="cooper_aerob_input")
        cooper_anaerob = col3.number_input("Anaerob (min)", min_value=0, step=1, key="cooper_anaerob_input")
        cooper_intensive = col4.number_input("Intensiv (min)", min_value=0, step=1, key="cooper_intensive_input")
        
        # TEST 2 - 5km-Lauf
        st.markdown("---")
        st.subheader("🔵 TEST 2 – 5-km-Lauf")
        col1, col2, col3, col4, col5 = st.columns(5)
        run5k_time_min = col1.number_input("Zeit (Minuten)", min_value=0, step=1, key="run5k_time_min_input")
        run5k_time_sec = col2.number_input("Zeit (Sekunden)", min_value=0, max_value=59, step=1, key="run5k_time_sec_input")
        run5k_avg_hr = col3.number_input("Durchschnittspuls (bpm)", min_value=0, max_value=250, step=1, key="run5k_avg_hr_input")
        run5k_max_hr = col4.number_input("Maximalpuls (bpm)", min_value=0, max_value=250, step=1, key="run5k_max_hr_input")
        run5k_pace = col5.number_input("Pace (min/km)", min_value=0.0, step=0.1, format="%.1f", key="run5k_pace_input")
        
        col1, col2 = st.columns(2)
        run5k_kcal = col1.number_input("Kalorien (kcal)", min_value=0, step=1, key="run5k_kcal_input")
        
        st.markdown("**Herzfrequenz-Zonen:**")
        col1, col2, col3, col4 = st.columns(4)
        run5k_warmup = col1.number_input("Warm-up (min)", min_value=0, step=1, key="run5k_warmup_input")
        run5k_aerob = col2.number_input("Aerob (min)", min_value=0, step=1, key="run5k_aerob_input")
        run5k_anaerob = col3.number_input("Anaerob (min)", min_value=0, step=1, key="run5k_anaerob_input")
        run5k_intensive = col4.number_input("Intensiv (min)", min_value=0, step=1, key="run5k_intensive_input")
        
        # TEST 3 - Liegestütze
        st.markdown("---")
        st.subheader("🟢 TEST 3 – Liegestütze")
        col1, col2, col3, col4 = st.columns(4)
        pushups_reps = col1.number_input("Wiederholungen", min_value=0, step=1, key="pushups_reps_input")
        pushups_avg_hr = col2.number_input("Durchschnittspuls (bpm)", min_value=0, max_value=250, step=1, key="pushups_avg_hr_input")
        pushups_max_hr = col3.number_input("Maximalpuls (bpm)", min_value=0, max_value=250, step=1, key="pushups_max_hr_input")
        
        # TEST 4 - Plank
        st.markdown("---")
        st.subheader("🟡 TEST 4 – Plank")
        col1, col2, col3, col4 = st.columns(4)
        plank_time_min = col1.number_input("Haltezeit (Minuten)", min_value=0, step=1, key="plank_time_min_input")
        plank_time_sec = col2.number_input("Haltezeit (Sekunden)", min_value=0, max_value=59, step=1, key="plank_time_sec_input")
        plank_avg_hr = col3.number_input("Durchschnittspuls (bpm)", min_value=0, max_value=250, step=1, key="plank_avg_hr_input")
        plank_max_hr = col4.number_input("Maximalpuls (bpm)", min_value=0, max_value=250, step=1, key="plank_max_hr_input")
        
        # TEST 5 - Burpee-Test
        st.markdown("---")
        st.subheader("🔴 TEST 5 – 1-Minuten-Burpee-Test")
        col1, col2, col3, col4 = st.columns(4)
        burpee_reps = col1.number_input("Wiederholungen", min_value=0, step=1, key="burpee_reps_input")
        burpee_avg_hr = col2.number_input("Durchschnittspuls (bpm)", min_value=0, max_value=250, step=1, key="burpee_avg_hr_input")
        burpee_max_hr = col3.number_input("Maximalpuls (bpm)", min_value=0, max_value=250, step=1, key="burpee_max_hr_input")
        
        # TEST 6 - VO2max-Test
        st.markdown("---")
        st.subheader("🟣 TEST 6 – VO₂max-Test (Einzeltest)")
        col1, col2, col3, col4 = st.columns(4)
        vo2max_value = col1.number_input("VO₂max-Wert (ml/kg/min)", min_value=0.0, step=0.1, format="%.1f", key="vo2max_value_input")
        vo2max_avg_hr = col2.number_input("Durchschnittspuls (bpm)", min_value=0, max_value=250, step=1, key="vo2max_avg_hr_input")
        vo2max_max_hr = col3.number_input("Maximalpuls (bpm)", min_value=0, max_value=250, step=1, key="vo2max_max_hr_input")
        vo2max_duration_min = col4.number_input("Testdauer (Minuten)", min_value=0, step=1, key="vo2max_duration_min_input")
        
        col1, col2 = st.columns(2)
        vo2max_duration_sec = col1.number_input("Testdauer (Sekunden)", min_value=0, max_value=59, step=1, key="vo2max_duration_sec_input")
        vo2max_speed = col2.text_input("Geschwindigkeit oder Stufe", key="vo2max_speed_input", placeholder="z.B. 12 km/h oder Stufe 8")
        
        ok = st.form_submit_button("Sporttest speichern", key="sport_tests_save_button")
    
    return ok, locals()

def render_blood_tests_form():
    """Rendert das Bluttests-Formular."""
    with st.form(key="blood_tests_form_key"):
        st.subheader("🩸 Bluttests")
        
        # Allgemeine Eingaben
        col1, col2 = st.columns(2)
        test_date = col1.date_input("Datum des Bluttests", value=date.today(), key="blood_tests_date_input")
        test_type = col2.selectbox("Testtyp", ["Baseline (Omnivor)", "Vegan-Test"], key="blood_tests_type_selectbox")
        notes = st.text_area("Notizen", key="blood_tests_notes_input", placeholder="Allgemeine Anmerkungen zum Test...")
        
        st.markdown("**Labor-PDF/Bild hochladen (optional):**")
        pdf_file = st.file_uploader("Labor-PDF/Bild hochladen", type=["pdf", "jpg", "jpeg", "png"], key="blood_tests_pdf_input")
        
        # Rotes & weißes Blutbild
        st.markdown("---")
        st.subheader("🔴 Rotes & weißes Blutbild")
        col1, col2, col3, col4, col5 = st.columns(5)
        hemoglobin = col1.number_input("Hämoglobin (g/dl)", min_value=0.0, step=0.1, format="%.1f", key="hemoglobin_input")
        erythrocytes = col2.number_input("Erythrozyten (Mio/µl)", min_value=0.0, step=0.01, format="%.2f", key="erythrocytes_input")
        mcv = col3.number_input("MCV (fl)", min_value=0.0, step=0.1, format="%.1f", key="mcv_input")
        mch = col4.number_input("MCH (pg)", min_value=0.0, step=0.1, format="%.1f", key="mch_input")
        thrombocytes = col5.number_input("Thrombozyten (10⁹/l)", min_value=0.0, step=1.0, format="%.0f", key="thrombocytes_input")
        
        col1, col2, col3, col4, col5 = st.columns(5)
        leukocytes = col1.number_input("Leuko (10⁹/l)", min_value=0.0, step=0.01, format="%.2f", key="leukocytes_input")
        segment = col2.number_input("Segment (%)", min_value=0.0, step=0.1, format="%.1f", key="segment_input")
        monocytes = col3.number_input("Monozyten (%)", min_value=0.0, step=0.1, format="%.1f", key="monocytes_input")
        lymphocytes = col4.number_input("Lymphozyten (%)", min_value=0.0, step=0.1, format="%.1f", key="lymphocytes_input")
        basophils = col5.number_input("Basophile (%)", min_value=0.0, step=0.1, format="%.1f", key="basophils_input")
        
        eosinophils = st.number_input("Eosinophile (%)", min_value=0.0, step=0.1, format="%.1f", key="eosinophils_input")
        
        # Blutchemie
        st.markdown("---")
        st.subheader("🟣 Blutchemie")
        col1, col2, col3, col4 = st.columns(4)
        alat = col1.number_input("ALAT (U/l)", min_value=0.0, step=0.1, format="%.1f", key="alat_input")
        asat = col2.number_input("ASAT (U/l)", min_value=0.0, step=0.1, format="%.1f", key="asat_input")
        creatinine = col3.number_input("Kreatinin (mg/dl)", min_value=0.0, step=0.01, format="%.2f", key="creatinine_input")
        egfr = col4.number_input("eGFR (ml/min)", min_value=0.0, step=0.1, format="%.1f", key="egfr_input")
        
        col1, col2, col3, col4 = st.columns(4)
        iron = col1.number_input("Eisen (µg/dl)", min_value=0.0, step=0.1, format="%.1f", key="iron_input")
        transferrin_saturation = col2.number_input("Transferrinsättigung (%)", min_value=0.0, step=0.1, format="%.1f", key="transferrin_saturation_input")
        gamma_gt = col3.number_input("Gamma-GT (U/l)", min_value=0.0, step=0.1, format="%.1f", key="gamma_gt_input")
        ap = col4.number_input("AP (U/l)", min_value=0.0, step=0.1, format="%.1f", key="ap_input")
        
        col1, col2, col3, col4 = st.columns(4)
        iron_saturation = col1.number_input("Eisensättigung (µg/dl)", min_value=0.0, step=0.1, format="%.1f", key="iron_saturation_input")
        ebk = col2.number_input("EBK (µg/dl)", min_value=0.0, step=0.1, format="%.1f", key="ebk_input")
        ferritin = col3.number_input("Ferritin (ng/ml)", min_value=0.0, step=0.1, format="%.1f", key="ferritin_input")
        transferrin = col4.number_input("Transferrin (mg/dl)", min_value=0.0, step=0.1, format="%.1f", key="transferrin_input")
        
        # Blutfette
        st.markdown("---")
        st.subheader("🟡 Blutfette")
        col1, col2, col3 = st.columns(3)
        cholesterol = col1.number_input("Cholesterin (mg/dl)", min_value=0.0, step=0.1, format="%.1f", key="cholesterol_input")
        triglycerides = col2.number_input("Triglyceride (mg/dl)", min_value=0.0, step=0.1, format="%.1f", key="triglycerides_input")
        ldl_chol = col3.number_input("LDL-Chol. (mg/dl)", min_value=0.0, step=0.1, format="%.1f", key="ldl_chol_input")
        
        # Elektrolyte
        st.markdown("---")
        st.subheader("🔵 Elektrolyte")
        col1, col2, col3 = st.columns(3)
        sodium = col1.number_input("Natrium (mmol/l)", min_value=0.0, step=0.1, format="%.1f", key="sodium_input")
        calcium = col2.number_input("Calcium (mmol/l)", min_value=0.0, step=0.01, format="%.2f", key="calcium_input")
        potassium = col3.number_input("Kalium (mmol/l)", min_value=0.0, step=0.01, format="%.2f", key="potassium_input")
        
        # Schilddrüsenhormone
        st.markdown("---")
        st.subheader("🟣 Schilddrüsenhormone")
        tsh_basal = st.number_input("TSH basal (uU/ml)", min_value=0.0, step=0.01, format="%.2f", key="tsh_basal_input")
        
        # Harnbefund
        st.markdown("---")
        st.subheader("⚪ Harnbefund")
        hk = st.number_input("HK (g/l)", min_value=0.0, step=0.1, format="%.1f", key="hk_input")
        
        ok = st.form_submit_button("Bluttest speichern", key="blood_tests_save_button")
    
    return ok, locals()

def save_uploaded_file(uploaded_file, directory, filename):
    """Speichert eine hochgeladene Datei im angegebenen Verzeichnis."""
    if uploaded_file is not None:
        # Stelle sicher, dass das Verzeichnis existiert
        os.makedirs(directory, exist_ok=True)
        
        # Speichere die Datei
        file_path = os.path.join(directory, filename)
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        return file_path
    return None

def check_and_warn_for_empty_series(df, col_name):
    """Prüft, ob eine Serie leer ist und zeigt eine Warnung an."""
    if df[col_name].isnull().all():
        st.warning(f"Für diesen Zeitraum fehlen Werte für '{col_name.replace('_', ' ').title()}'.")
        return True
    return False

def create_dual_axis_chart(df, x_col, y1_col, y2_col, title, y1_title, y2_title, y1_color_key, y2_color_key, y1_range, y2_range, show_diff_line=False, show_zero_ref=False, info_badge_text=None):
    """Erstellt ein wissenschaftlich korrektes Dual-Achsen-Diagramm mit Feinschliff."""
    if check_and_warn_for_empty_series(df, y1_col) or check_and_warn_for_empty_series(df, y2_col):
        return None

    fig = go.Figure()
    
    # Linke Y-Achse (y1)
    fig.add_trace(go.Scatter(
        x=df[x_col], y=df[y1_col], name=y1_title, 
        line=dict(color=COLORS[y1_color_key], width=2), 
        marker=dict(size=5),
        connectgaps=False,
        hovertemplate=f'<b>{y1_title}</b><br>Datum: %{{x|%d.%m.%Y}}<br>Wert: %{{y:.2f}}<extra></extra>'
    ))
    
    # Rechte Y-Achse (y2)
    fig.add_trace(go.Scatter(
        x=df[x_col], y=df[y2_col], name=y2_title, yaxis='y2', 
        line=dict(color=COLORS[y2_color_key], width=2), 
        marker=dict(size=5),
        connectgaps=False,
        hovertemplate=f'<b>{y2_title}</b><br>Datum: %{{x|%d.%m.%Y}}<br>Wert: %{{y:.2f}}<extra></extra>'
    ))

    # Optionale Differenzlinie
    if show_diff_line:
        diff_col_name = f'{y2_col}_diff'
        df[diff_col_name] = df[y2_col] - df[y1_col]
        fig.add_trace(go.Scatter(
            x=df[x_col], y=df[diff_col_name], name='Differenz (y2-y1)', yaxis='y2',
            line=dict(color=COLORS['trend'], width=1.5, dash='dot'),
            marker=dict(size=4),
            connectgaps=False,
            hovertemplate=f'<b>Differenz</b><br>Datum: %{{x|%d.%m.%Y}}<br>Wert: %{{y:.2f}}<extra></extra>'
    ))

    fig.update_layout(
        title_text=title,
        title_x=0.5,
        xaxis_title="Datum",
        yaxis=dict(
            title=dict(text=f"{y1_title} ({y1_range['unit']})", font=dict(color=COLORS[y1_color_key])), 
            tickfont=dict(color=COLORS[y1_color_key]),
            range=y1_range['range'],
            showgrid=True, gridcolor='rgba(255,255,255,0.1)'
        ),
        yaxis2=dict(
            title=dict(text=f"{y2_title} ({y2_range['unit']})", font=dict(color=COLORS[y2_color_key])), 
            tickfont=dict(color=COLORS[y2_color_key]), 
            range=y2_range['range'],
            overlaying="y", 
            side="right",
            showgrid=False
        ),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        template='plotly_dark',
        margin=dict(l=50, r=50, t=50, b=50),
        hovermode='x unified'
    )
    
    if show_zero_ref:
        fig.add_hline(y=0, line_width=1, line_dash="dash", line_color="white", annotation_text="Referenz: 0")

    if info_badge_text:
        st.info(info_badge_text)
        
    return fig

def create_single_axis_chart(df, x_col, y_col, title, y_title, color_key, y_range, goal_value=None):
    """Erstellt ein Einzellinien-Diagramm mit Feinschliff."""
    if check_and_warn_for_empty_series(df, y_col):
        return None

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df[x_col], y=df[y_col], name=y_title, 
        line=dict(color=COLORS[color_key], width=2), 
        marker=dict(size=5),
        connectgaps=False,
        hovertemplate=f'<b>{y_title}</b><br>Datum: %{{x|%d.%m.%Y}}<br>Wert: %{{y:.2f}}<extra></extra>'
    ))

    # Optionale Ziel-Linie
    if goal_value:
        fig.add_hline(y=goal_value, line_dash="dash", line_color="white", annotation_text=f"Ziel: {goal_value} {y_range['unit']}")

    fig.update_layout(
        title_text=title,
        title_x=0.5,
        xaxis_title="Datum",
        yaxis_title=f"{y_title} ({y_range['unit']})",
        yaxis=dict(range=y_range['range'], showgrid=True, gridcolor='rgba(255,255,255,0.1)'),
        template='plotly_dark',
        margin=dict(l=50, r=50, t=50, b=50),
        hovermode='x unified'
    )
    return fig

def create_multi_line_chart(df, x_col, y_cols, names, title, y_title, y_range):
    """Erstellt ein Mehrfachlinien-Diagramm (z.B. für Wohlbefinden)."""
    fig = go.Figure()
    for col, name in zip(y_cols, names):
        if not df[col].dropna().empty:
            fig.add_trace(go.Scatter(
                x=df[x_col], y=df[col], name=name, 
                line=dict(color=COLORS[col], width=2), 
                marker=dict(size=5),
                connectgaps=False,
                hovertemplate=f'<b>{name}</b><br>Datum: %{{x|%d.%m.%Y}}<br>Wert: %{{y}}<extra></extra>'
    ))

    fig.update_layout(
        title_text=title,
        title_x=0.5,
        xaxis_title="Datum",
        yaxis_title=y_title,
        yaxis=dict(range=y_range['range'], showgrid=True, gridcolor='rgba(255,255,255,0.1)'),
        template='plotly_dark',
        margin=dict(l=50, r=50, t=50, b=50),
        hovermode='x unified',
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    return fig

def create_phase_comparison_chart(df, metric, title, unit, chart_type="line"):
    """Erstellt ein Phasenvergleichsdiagramm für eine Metrik."""
    # Daten nach Phase filtern
    omnivor_df = df[df['phase'] == 'Omnivor'].copy()
    vegan_df = df[df['phase'] == 'Vegan'].copy()
    
    fig = go.Figure()
    
    if chart_type == "line":
        # Linienchart
        if not omnivor_df.empty:
            fig.add_trace(go.Scatter(
                x=omnivor_df['date'], y=omnivor_df[metric],
                mode='lines+markers', name='Omnivor',
                line=dict(color=COLORS['omnivor'], width=2),
                marker=dict(size=5),
                connectgaps=False,
                hovertemplate=f'<b>Omnivor</b><br>Datum: %{{x|%d.%m.%Y}}<br>Wert: %{{y:.2f}} {unit}<extra></extra>'
            ))
        
        if not vegan_df.empty:
            fig.add_trace(go.Scatter(
                x=vegan_df['date'], y=vegan_df[metric],
                mode='lines+markers', name='Vegan',
                line=dict(color=COLORS['vegan'], width=2),
                marker=dict(size=5),
                connectgaps=False,
                hovertemplate=f'<b>Vegan</b><br>Datum: %{{x|%d.%m.%Y}}<br>Wert: %{{y:.2f}} {unit}<extra></extra>'
            ))
    
    elif chart_type == "box":
        # Boxplot
        if not omnivor_df.empty and not omnivor_df[metric].isna().all():
            fig.add_trace(go.Box(
                y=omnivor_df[metric], name='Omnivor',
                marker_color=COLORS['omnivor'],
                boxpoints='outliers'
            ))
        
        if not vegan_df.empty and not vegan_df[metric].isna().all():
            fig.add_trace(go.Box(
                y=vegan_df[metric], name='Vegan',
                marker_color=COLORS['vegan'],
                boxpoints='outliers'
            ))
    
    # Y-Achsen-Bereich basierend auf Daten
    all_values = pd.concat([omnivor_df[metric], vegan_df[metric]]).dropna()
    if not all_values.empty:
        y_min = max(0, all_values.min() * 0.9)
        y_max = all_values.max() * 1.1
    else:
        y_min, y_max = 0, 1
    
    fig.update_layout(
        title_text=title,
        title_x=0.5,
        xaxis_title="Datum" if chart_type == "line" else "Phase",
        yaxis_title=f"{title} ({unit})",
        yaxis=dict(range=[y_min, y_max], showgrid=True, gridcolor='rgba(255,255,255,0.1)'),
        template='plotly_dark',
        margin=dict(l=50, r=50, t=50, b=50),
        hovermode='x unified' if chart_type == "line" else 'closest',
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    
    return fig

def create_phase_stats_cards(df, metric):
    """Erstellt Statistik-Karten für den Phasenvergleich."""
    omnivor_df = df[df['phase'] == 'Omnivor'][metric].dropna()
    vegan_df = df[df['phase'] == 'Vegan'][metric].dropna()
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"### Omnivor")
        if not omnivor_df.empty:
            st.metric("Mittelwert", f"{omnivor_df.mean():.2f}")
            st.metric("Standardabweichung", f"{omnivor_df.std():.2f}")
            st.metric("Median", f"{omnivor_df.median():.2f}")
            c1, c2 = st.columns(2)
            c1.metric("Minimum", f"{omnivor_df.min():.2f}")
            c2.metric("Maximum", f"{omnivor_df.max():.2f}")
        else:
            st.info("Keine Daten für Omnivor-Phase")
    
    with col2:
        st.markdown(f"### Vegan")
        if not vegan_df.empty:
            st.metric("Mittelwert", f"{vegan_df.mean():.2f}")
            st.metric("Standardabweichung", f"{vegan_df.std():.2f}")
            st.metric("Median", f"{vegan_df.median():.2f}")
            c1, c2 = st.columns(2)
            c1.metric("Minimum", f"{vegan_df.min():.2f}")
            c2.metric("Maximum", f"{vegan_df.max():.2f}")
        else:
            st.info("Keine Daten für Vegan-Phase")

def perform_statistical_tests(df, metric):
    """Führt statistische Tests zwischen den Phasen durch und gibt die Ergebnisse zurück."""
    omnivor_df = df[df['phase'] == 'Omnivor'][metric].dropna()
    vegan_df = df[df['phase'] == 'Vegan'][metric].dropna()
    
    if omnivor_df.empty or vegan_df.empty:
        return None
    
    # Normalverteilung prüfen (Shapiro-Wilk-Test)
    omnivor_normal = stats.shapiro(omnivor_df)
    vegan_normal = stats.shapiro(vegan_df)
    
    # Je nach Normalverteilung den passenden Test auswählen
    if omnivor_normal.pvalue > 0.05 and vegan_normal.pvalue > 0.05:
        # Beide Stichproben normalverteilt -> t-Test
        test_result = stats.ttest_ind(omnivor_df, vegan_df)
        test_name = "t-Test (unabhängige Stichproben)"
    else:
        # Mindestens eine Stichprobe nicht normalverteilt -> Mann-Whitney-U-Test
        test_result = stats.mannwhitneyu(omnivor_df, vegan_df, alternative='two-sided')
        test_name = "Mann-Whitney-U-Test"
    
    # Effektstärke berechnen (Cohen's d für t-Test, r für Mann-Whitney-U)
    if test_name == "t-Test (unabhängige Stichproben)":
        # Cohen's d
        pooled_std = np.sqrt(((len(omnivor_df) - 1) * omnivor_df.var() + 
                            (len(vegan_df) - 1) * vegan_df.var()) / 
                            (len(omnivor_df) + len(vegan_df) - 2))
        effect_size = (omnivor_df.mean() - vegan_df.mean()) / pooled_std
        effect_name = "Cohen's d"
    else:
        # r für Mann-Whitney-U
        n1, n2 = len(omnivor_df), len(vegan_df)
        z_score = stats.norm.ppf(test_result.pvalue / 2) * np.sign(omnivor_df.mean() - vegan_df.mean())
        effect_size = z_score / np.sqrt(n1 + n2)
        effect_name = "Effektstärke r"
    
    return {
        'test_name': test_name,
        'statistic': test_result.statistic,
        'p_value': test_result.pvalue,
        'effect_size': effect_size,
        'effect_name': effect_name,
        'omnivor_mean': omnivor_df.mean(),
        'vegan_mean': vegan_df.mean(),
        'omnivor_normal': omnivor_normal.pvalue > 0.05,
        'vegan_normal': vegan_normal.pvalue > 0.05
    }

def render_analysis_section_v2(df: pd.DataFrame, goals: dict):
    """Rendert den Analyse-Bereich mit gruppierten, feingeschliffenen Diagrammen."""
    st.subheader("📈 Analyse & Auswertung")
    
    if df.empty:
        st.info("Keine Daten im ausgewählten Zeitraum vorhanden.")
        return

    # Zeitraum-Auswahl mit Quick-Filters
    c1, c2 = st.columns(2)
    default_start = (date.today() - timedelta(days=30))
    start_date = c1.date_input("Von", value=df["date"].min() if not df.empty else default_start, key="start_date_input")
    end_date = c2.date_input("Bis", value=df["date"].max() if not df.empty else date.today(), key="end_date_input")


    # Daten nach Zeitraum filtern
    sel_df = df[(df["date"] >= start_date) & (df["date"] <= end_date)].copy()
    phase_comparison = st.checkbox("Phasenvergleich", value=False, key="phase_comparison_toggle")

    # Phasenvergleich-Modus
    if phase_comparison and (end_date - start_date).days >= 30:
        st.markdown("---")
        st.header("🔄 Phasenvergleich: Omnivor vs. Vegan")
        
        # Filter-Chips
        show_omnivor = st.checkbox("Omnivor anzeigen", value=True, key="show_omnivor")
        show_vegan = st.checkbox("Vegan anzeigen", value=True, key="show_vegan")
        
        # Chart-Typ-Umschalter
        chart_type = st.radio("Darstellung", ["Linien", "Boxplot"], key="chart_type_radio")
        
        # Kernmetriken für Phasenvergleich
        metrics = [
            # Schlaf & Regeneration
            ("sleep_hours", "Schlafdauer", "h"),
            ("sleep_score", "Schlafqualität", "Score"),
            ("hrv_sleep_avg", "HRV (Schlaf Ø)", "ms"),
            ("rhr_sleep_avg", "Ruhepuls (Schlaf Ø)", "bpm"),
            ("spo2_sleep_avg", "SpO₂ (Schlaf Ø)", "%"),
            ("deep_sleep_percent", "Tiefschlaf (%)", "%"),
            ("awakenings", "Aufwachhäufigkeit", "Anz."),

            # Aktivität & Energie
            ("total_steps", "Gesamtschritte", "Anz."),
            ("total_kcal_burn", "Kalorienverbrauch", "kcal"),
            ("intake_kcal", "Kalorienaufnahme", "kcal"),
            ("energy_balance", "Energiebilanz (Aufnahme–Verbrauch)", "kcal"),

            # Makros & Wasser (wie im Analyse-Tab)
            ("protein_g_per_kg", "Protein (g/kg Körpergewicht)", "g/kg"),
            ("protein_g", "Protein gesamt", "g"),
            ("carbs_g", "Kohlenhydrate", "g"),
            ("fat_g", "Fette", "g"),
            ("water_ml", "Wasseraufnahme", "ml"),

            # Körper & Kreislauf
            ("body_weight", "Körpergewicht", "kg"),
            ("bp_sys", "Blutdruck systolisch", "mmHg"),
            ("bp_dia", "Blutdruck diastolisch", "mmHg"),

            # Wohlbefinden (einzeln)
            ("energy", "Energielevel", "Score (1–10)"),
            ("mood", "Stimmung", "Score (1–10)"),
            ("motivation", "Motivation", "Score (1–10)"),
            ("concentration", "Konzentration", "Score (1–10)"),

            # Stress
            ("stress_avg", "Stress-Ø", "Score (0–100)"),
            ("stress_peak", "Stress-Spitzenwert", "Score (0–100)")
        ]

# Metrik-Auswahl
        selected_metric = st.selectbox(
            "Metrik auswählen",
            options=[m[1] for m in metrics],
            format_func=lambda x: x,
            key="metric_select"
        )
        
        # Finde die ausgewählte Metrik
        metric_data = next((m for m in metrics if m[1] == selected_metric), None)
        
        if metric_data:
            metric, title, unit = metric_data
            
            # Filtere Daten basierend auf den Checkboxen
            filtered_df = sel_df.copy()
            # Zusatzmetrik: Energiebilanz (deskriptiv)
            if metric == "energy_balance":
                filtered_df = filtered_df.copy()
                filtered_df["energy_balance"] = filtered_df["intake_kcal"] - filtered_df["total_kcal_burn"]

            if not show_omnivor:
                filtered_df = filtered_df[filtered_df['phase'] != 'Omnivor']
            if not show_vegan:
                filtered_df = filtered_df[filtered_df['phase'] != 'Vegan']
            
            # Erstelle das Diagramm
            chart_type_value = "line" if chart_type == "Linien" else "box"

            # Zusatzmetrik: Energiebilanz (deskriptiv)
            if metric == "energy_balance":
                filtered_df = filtered_df.copy()
                filtered_df["energy_balance"] = filtered_df["intake_kcal"] - filtered_df["total_kcal_burn"]
            fig = create_phase_comparison_chart(filtered_df, metric, title, unit, chart_type_value)
            st.plotly_chart(fig, use_container_width=True)
            
            # Zeige Statistik-Karten
            create_phase_stats_cards(filtered_df, metric)
            
            # NEU: Statistische Tests
            st.markdown("---")
            st.subheader("📊 Statistische Analyse")
            
            test_results = perform_statistical_tests(filtered_df, metric)
            
            if test_results:
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("### Testergebnisse")
                    st.markdown(f"**Test:** {test_results['test_name']}")
                    st.markdown(f"**p-Wert:** {test_results['p_value']:.4f}")
                    
                    # Signifikanz interpretieren
                    if test_results['p_value'] < 0.05:
                        st.success("Statistisch signifikanter Unterschied (p < 0.05)")
                    else:
                        st.info("Kein statistisch signifikanter Unterschied (p ≥ 0.05)")
                
                with col2:
                    st.markdown("### Effektstärke")
                    st.markdown(f"**{test_results['effect_name']}:** {test_results['effect_size']:.3f}")
                    
                    # Effektstärke interpretieren
                    if test_results['effect_name'] == "Cohen's d":
                        if abs(test_results['effect_size']) < 0.2:
                            st.info("Kleiner Effekt")
                        elif abs(test_results['effect_size']) < 0.5:
                            st.info("Mittlerer Effekt")
                        else:
                            st.success("Großer Effekt")
                    else:  # r für Mann-Whitney-U
                        if abs(test_results['effect_size']) < 0.1:
                            st.info("Kleiner Effekt")
                        elif abs(test_results['effect_size']) < 0.3:
                            st.info("Mittlerer Effekt")
                        else:
                            st.success("Großer Effekt")
    
    # Normale Analyse
    else:
        # Schlaf & Regeneration
        st.markdown("---")
        st.header("😴 Schlaf & Regeneration")
        
        col1, col2 = st.columns(2)
        with col1:
            sleep_chart = create_single_axis_chart(
                sel_df, "date", "sleep_hours", "Schlafdauer", "Stunden", "steps", 
                {"range": [4, 10], "unit": "h"}, 
                goals.get("sleep_hours_goal")
            )
            if sleep_chart:
                st.plotly_chart(sleep_chart, use_container_width=True)
        
        with col2:
            sleep_score_chart = create_single_axis_chart(
                sel_df, "date", "sleep_score", "Schlafqualität", "Score", "mood", 
                {"range": [50, 100], "unit": "Score"}
            )
            if sleep_score_chart:
                st.plotly_chart(sleep_score_chart, use_container_width=True)
        
        # HRV & Ruhepuls
        col1, col2 = st.columns(2)
        with col1:
            hrv_chart = create_single_axis_chart(
                sel_df, "date", "hrv_sleep_avg", "HRV im Schlaf", "ms", "hrv", 
                {"range": [20, 80], "unit": "ms"}
            )
            if hrv_chart:
                st.plotly_chart(hrv_chart, use_container_width=True)
        
        with col2:
            rhr_chart = create_single_axis_chart(
                sel_df, "date", "rhr_sleep_avg", "Ruhepuls im Schlaf", "bpm", "resting_hr", 
                {"range": [40, 80], "unit": "bpm"}
            )
            if rhr_chart:
                st.plotly_chart(rhr_chart, use_container_width=True)
        
        # Aktivität
        st.markdown("---")
        st.header("🏃 Aktivität")
        
        col1, col2 = st.columns(2)
        with col1:
            steps_chart = create_single_axis_chart(
                sel_df, "date", "total_steps", "Gesamtschritte", "Anzahl", "steps", 
                {"range": [0, 20000], "unit": "Anz."}, 
                goals.get("total_steps_goal")
            )
            if steps_chart:
                st.plotly_chart(steps_chart, use_container_width=True)
        
        with col2:
            kcal_chart = create_dual_axis_chart(
                sel_df, "date", "intake_kcal", "total_kcal_burn", 
                "Energiebilanz", "Kalorienaufnahme", "Kalorienverbrauch", 
                "intake", "burn", 
                {"range": [1500, 3500], "unit": "kcal"}, 
                {"range": [1500, 3500], "unit": "kcal"},
                show_diff_line=True,
                show_zero_ref=True
            )
            if kcal_chart:
                st.plotly_chart(kcal_chart, use_container_width=True)
        
        

        # Ernährung & Makros (deskriptiv)
        st.markdown("---")
        st.header("🍽️ Ernährung & Makros")

        row1_col1, row1_col2 = st.columns(2)
        with row1_col1:
            protein_kg_chart = create_single_axis_chart(
                sel_df, "date", "protein_g_per_kg", "Protein (g/kg Körpergewicht)", "g/kg", "protein",
                {"range": [0.0, 3.0], "unit": "g/kg"},
                goals.get("protein_g_per_kg_goal")
            )
            if protein_kg_chart:
                st.plotly_chart(protein_kg_chart, use_container_width=True)

        with row1_col2:
            protein_chart = create_single_axis_chart(
                sel_df, "date", "protein_g", "Protein gesamt", "g", "protein",
                {"range": [0, 250], "unit": "g"}
            )
            if protein_chart:
                st.plotly_chart(protein_chart, use_container_width=True)

        row2_col1, row2_col2 = st.columns(2)
        with row2_col1:
            carbs_chart = create_single_axis_chart(
                sel_df, "date", "carbs_g", "Kohlenhydrate", "g", "carbs",
                {"range": [0, 600], "unit": "g"}
            )
            if carbs_chart:
                st.plotly_chart(carbs_chart, use_container_width=True)

        with row2_col2:
            fat_chart = create_single_axis_chart(
                sel_df, "date", "fat_g", "Fette", "g", "fat",
                {"range": [0, 200], "unit": "g"}
            )
            if fat_chart:
                st.plotly_chart(fat_chart, use_container_width=True)
# Körper & Kreislauf
        st.markdown("---")
        st.header("❤️ Körper & Kreislauf")
        
        col1, col2 = st.columns(2)
        with col1:
            weight_chart = create_single_axis_chart(
                sel_df, "date", "body_weight", "Körpergewicht", "kg", "energy", 
                {"range": [60, 90], "unit": "kg"}
            )
            if weight_chart:
                st.plotly_chart(weight_chart, use_container_width=True)
        
        with col2:
            bp_chart = create_dual_axis_chart(
                sel_df, "date", "bp_sys", "bp_dia", 
                "Blutdruck", "Systolisch", "Diastolisch", 
                "bp_sys", "bp_dia", 
                {"range": [100, 160], "unit": "mmHg"}, 
                {"range": [60, 100], "unit": "mmHg"}
            )
            if bp_chart:
                st.plotly_chart(bp_chart, use_container_width=True)
        
        # Wohlbefinden
        st.markdown("---")
        st.header("😊 Wohlbefinden")
        
        wellbeing_chart = create_multi_line_chart(
            sel_df, "date", 
            ["energy", "mood", "motivation"], 
            ["Energie", "Stimmung", "Motivation"], 
            "Wohlbefinden", "Score (1-10)", 
            {"range": [1, 10], "unit": "Score"}
        )
        if wellbeing_chart:
            st.plotly_chart(wellbeing_chart, use_container_width=True)