# app.py
# ===================================================================
# DATEI: app.py
# ===================================================================
import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, date, timedelta
import os

# Importiere die eigenen Module
from config import *
from database import load_json, save_json, load_data, save_data, compute_metrics, load_goals, update_data, load_nutrition_data, save_nutrition_data, update_nutrition_data, load_sport_tests_data, save_sport_tests_data, update_sport_tests_data, load_blood_tests_data, save_blood_tests_data, update_blood_tests_data
from ui_components import render_settings_expander, render_daily_form, render_nutrition_form, render_analysis_section_v2, render_sport_tests_form, render_blood_tests_form, save_uploaded_file, generate_demo_data

# --- Konfiguration der Seite ---
st.set_page_config(page_title="ABA Selbsttest – Pflanzlich fit? Vegane Ernährung & sportliche Leistungsfähigkeit", layout="wide")

# --- Titel ---
st.title("🌱 ABA Selbsttest – Pflanzlich fit? Vegane Ernährung & sportliche Leistungsfähigkeit")

# --- Daten laden ---
settings = load_json(SETTINGS_FILE, DEFAULT_SETTINGS)
mapping = load_json(MAPPING_FILE, DEFAULT_MAPPING)
goals = load_goals()
df = load_data()
nutrition_df = load_nutrition_data()
sport_tests_df = load_sport_tests_data()
blood_tests_df = load_blood_tests_data()
df = compute_metrics(df).sort_values("date")

# --- UI-Elemente rendern ---
render_settings_expander(settings, mapping)

# --- Tabs für verschiedene Bereiche ---
tab1, tab2, tab3, tab4, tab5 = st.tabs(["📊 Tageswerte", "🍽️ Ernährungstagebuch", "🏃‍♂️ Sporttests", "🩸 Bluttests", "📈 Analyse"])

with tab1:
    st.header("Tagesformular")
    submitted, form_data = render_daily_form()

    if submitted:
        data = form_data
        sleep_hours = float(data["sh_h"]) + float(data["sh_m"]) / 60.0
        deep_sleep_hours = float(data["deep_hh"]) + float(data["deep_mm"]) / 60.0
        
        base_df = df[df["date"] != data["d"]]
        
        # Nährstoffdaten aus dem Formular extrahieren (NEUE SCHLÜSSEL)
        nutrition_data_to_save = {
            "intake_kcal": data["intake"],
            "carbs_g": data["carbs"],
            "protein_g": data["protein"],
            "fat_g": data["fat"],
            "water_ml": data["water"],
        }

        # Nährstoffdaten im Ernährungstagebuch synchronisieren/aktualisieren
        update_nutrition_data(data["d"], data["phase"], nutrition_data_to_save)
        
        new_row = pd.DataFrame([{
            "date": data["d"], "weekday": None, "phase": data["phase"],
            "sleep_hours": sleep_hours, "sleep_score": data["ss"], "hrv_sleep_avg": data["hrv_s"],
            "rhr_sleep_avg": data["rhr_s"], "rhr_sleep_min": data["rhr_s_min"], "spo2_sleep_avg": data["spo2_s_avg"], "spo2_sleep_min": data["spo2_s_min"],
            "deep_sleep_hours": deep_sleep_hours, "deep_sleep_percent": data["deep_p"], "awakenings": data["awake_n"],
            # Aktivität (Alltag)
            "total_steps": data["total_steps"], "total_kcal_burn": data["total_kcal_burn"],
            # Energie & Nährstoffe (neu hinzugefügt)
            **nutrition_data_to_save,
            # Körper & Kreislauf
            "morning_pulse": data["morning_pulse"], "hrv_day_avg": data["hrv_day"], "spo2_day_avg": data["spo2_day"], "bp_sys": data["bp_sys"], "bp_dia": data["bp_dia"],
            "body_weight": (data["weight"] if data["weight"] > 0 else pd.NA),
            "stress_avg": data["stress_avg"], "stress_peak": data["stress_peak"],
            # Wohlbefinden
            "energy": data["energy"], "mood": data["mood"], "motivation": data["motivation"], "concentration": data["concentration"], "note": data["note"],
            "last_modified": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }])
        
        merged_df = pd.concat([base_df, new_row], ignore_index=True)
        merged_df = compute_metrics(merged_df)
        save_data(merged_df)
        st.success("Gespeichert & automatisch gesichert ✅")
        st.rerun()

    st.header("Daten (Tageswerte)")

    show_all_cols = st.checkbox("Alle Spalten anzeigen", value=False, key="daily_show_all_cols")

    # Editierbare Tabelle mit Inline-Edit
    if not df.empty:
        # Anzeige-DataFrame mit relevanten Spalten
        if show_all_cols:
            display_cols = [c for c in COLUMNS if c in df.columns and c != "last_modified"]
        else:
            display_cols = ["date", "phase", "sleep_hours", "sleep_score", "hrv_sleep_avg", "rhr_sleep_avg",
                           "total_steps", "total_kcal_burn", "intake_kcal", "carbs_g", "protein_g", "fat_g", "water_ml",
                           "body_weight", "stress_avg", "energy", "mood", "motivation"]
            display_cols = [c for c in display_cols if c in df.columns]
        display_df = df[display_cols].copy()
        
        # Tabelle mit Inline-Edit
        edited_df = st.data_editor(
            display_df,
            column_config={
                "date": st.column_config.DateColumn("Datum", format="DD.MM.YYYY"),
                "phase": st.column_config.SelectboxColumn(
                    "Phase",
                    options=["Omnivor", "Vegan"],
                    required=True,
                )
            },
            hide_index=True,
            use_container_width=True,
            num_rows="dynamic"
        )
        
        # Prüfen auf Änderungen (Updates und Löschungen)
        changes_detected = False
        
        # 1. Prüfen auf gelöschte Zeilen
        if len(edited_df) < len(display_df):
            original_dates = set(display_df["date"].astype(str) + "_" + display_df["phase"].astype(str))
            edited_dates = set(edited_df["date"].astype(str) + "_" + edited_df["phase"].astype(str))
            deleted_entries = original_dates - edited_dates
            
            if deleted_entries:
                keep_mask = ~((df["date"].astype(str) + "_" + df["phase"].astype(str)).isin(deleted_entries))
                df = df[keep_mask].copy()
                changes_detected = True
                st.success(f"{len(deleted_entries)} Eintrag(e) gelöscht!")
        
        # 2. Prüfen auf geänderte oder neue Zeilen
        elif len(edited_df) >= len(display_df):
            for i, row in edited_df.iterrows():
                if i < len(df):
                    original_row = df.iloc[i]
                    display_row = display_df.iloc[i] if i < len(display_df) else None
                    
                    if display_row is not None and not row.equals(display_row):
                        updated_data = {}
                        for col in display_cols:
                            if col in df.columns:
                                updated_data[col] = row[col]
                        
                        date_val = row["date"]
                        phase_val = row["phase"]
                        
                        # Update in der Hauptdatenbank
                        update_data(date_val, phase_val, updated_data)
                        
                        # Synchronisation der Nährstoffdaten mit dem Ernährungstagebuch
                        nutrition_updated_data = {k: v for k, v in updated_data.items() if k in ["intake_kcal", "carbs_g", "protein_g", "fat_g", "water_ml"]}
                        if nutrition_updated_data:
                            update_nutrition_data(date_val, phase_val, nutrition_updated_data)

                        changes_detected = True
                else:
                    st.warning("Neue Zeilen können nur über das Tagesformular hinzugefügt werden.")
        
        if changes_detected:
            st.rerun()
    else:
        st.info("Keine Daten vorhanden. Bitte erfassen Sie zuerst einige Daten.")

with tab2:
    st.header("🍽️ Ernährungstagebuch")
    
    nutrition_submitted, nutrition_form_data = render_nutrition_form()
    
    if nutrition_submitted:
        data = nutrition_form_data
        base_nutrition_df = nutrition_df[nutrition_df["date"] != data["date"]]
        
        new_nutrition_row = pd.DataFrame([{
            "date": data["date"], "phase": data["nutrition_form_phase_selectbox"],
            "breakfast": data["nutrition_form_breakfast_input"], "snack_1": data["nutrition_form_snack_1_input"], "lunch": data["nutrition_form_lunch_input"], "snack_2": data["nutrition_form_snack_2_input"], "dinner": data["nutrition_form_dinner_input"],
            "supplements": data["nutrition_form_nutrition_supplements_input"], "nutrition_note": data["nutrition_form_nutrition_note_input"],
            # Nährstoffdaten werden hier wieder aus dem Formular übernommen (NEUE SCHLÜSSEL)
            "intake_kcal": data["nutrition_form_nutrition_intake_input"], "carbs_g": data["nutrition_form_nutrition_carbs_input"],
            "protein_g": data["nutrition_form_nutrition_protein_input"], "fat_g": data["nutrition_form_nutrition_fat_input"], "water_ml": data["nutrition_form_nutrition_water_input"],
            "last_modified": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }])
        
        merged_nutrition_df = pd.concat([base_nutrition_df, new_nutrition_row], ignore_index=True)
        save_nutrition_data(merged_nutrition_df)
        st.success("Ernährung gespeichert! ✅")
        st.rerun()
    
    st.header("Ernährungsdaten")
    
    if not nutrition_df.empty:
        nutrition_display_cols = ["date", "phase", "breakfast", "snack_1", "lunch", "snack_2", "dinner", "supplements", "intake_kcal", "carbs_g", "protein_g", "fat_g", "water_ml", "nutrition_note"]
        nutrition_display_df = nutrition_df[nutrition_display_cols].copy()
        
        nutrition_edited_df = st.data_editor(
            nutrition_display_df,
            column_config={
                "date": st.column_config.DateColumn("Datum", format="DD.MM.YYYY"),
                "phase": st.column_config.SelectboxColumn(
                    "Phase",
                    options=["Omnivor", "Vegan"],
                    required=True,
                )
            },
            hide_index=True,
            use_container_width=True,
            num_rows="dynamic"
        )
        
        # Prüfen auf Änderungen
        if not nutrition_edited_df.equals(nutrition_display_df):
            for i, row in nutrition_edited_df.iterrows():
                if i < len(nutrition_df):
                    original_row = nutrition_df.iloc[i]
                    display_row = nutrition_display_df.iloc[i] if i < len(nutrition_display_df) else None
                    
                    if display_row is not None and not row.equals(display_row):
                        updated_data = {}
                        for col in nutrition_display_cols:
                            if col in nutrition_df.columns:
                                updated_data[col] = row[col]
                        
                        date_val = row["date"]
                        phase_val = row["phase"]
                        update_nutrition_data(date_val, phase_val, updated_data)
            
            st.success("Änderungen gespeichert!")
            st.rerun()
    else:
        st.info("Keine Ernährungsdaten vorhanden.")

with tab3:
    st.header("🏃‍♂️ Sporttests")
    sport_submitted, sport_form_data = render_sport_tests_form()

    if sport_submitted:
        data = sport_form_data
        
        # Prepare data for saving
        sport_data_to_save = {
            "test_date": data["test_date"], "test_type": data["test_type"], "general_notes": data["general_notes"],
            # Cooper-Test
            "cooper_distance": data["cooper_distance"], "cooper_avg_hr": data["cooper_avg_hr"], "cooper_max_hr": data["cooper_max_hr"], "cooper_pace": data["cooper_pace"], "cooper_kcal": data["cooper_kcal"],
            "cooper_warmup": data["cooper_warmup"], "cooper_aerob": data["cooper_aerob"], "cooper_anaerob": data["cooper_anaerob"], "cooper_intensive": data["cooper_intensive"],
            # 5km-Lauf
            "run5k_time": f"{data['run5k_time_min']}:{data['run5k_time_sec']:02d}", "run5k_avg_hr": data["run5k_avg_hr"], "run5k_max_hr": data["run5k_max_hr"], "run5k_pace": data["run5k_pace"], "run5k_kcal": data["run5k_kcal"],
            "run5k_warmup": data["run5k_warmup"], "run5k_aerob": data["run5k_aerob"], "run5k_anaerob": data["run5k_anaerob"], "run5k_intensive": data["run5k_intensive"],
            # Liegestütze
            "pushups_reps": data["pushups_reps"], "pushups_avg_hr": data["pushups_avg_hr"], "pushups_max_hr": data["pushups_max_hr"],
            # Plank
            "plank_time": f"{data['plank_time_min']}:{data['plank_time_sec']:02d}", "plank_avg_hr": data["plank_avg_hr"], "plank_max_hr": data["plank_max_hr"],
            # Burpee-Test
            "burpee_reps": data["burpee_reps"], "burpee_avg_hr": data["burpee_avg_hr"], "burpee_max_hr": data["burpee_max_hr"],
            # VO2max-Test
            "vo2max_value": data["vo2max_value"], "vo2max_avg_hr": data["vo2max_avg_hr"], "vo2max_max_hr": data["vo2max_max_hr"], "vo2max_duration": f"{data['vo2max_duration_min']}:{data['vo2max_duration_sec']:02d}", "vo2max_speed": data["vo2max_speed"],
        }
        
        # Handle file uploads
        photo_keys = ["cooper_photo", "run5k_photo", "pushups_photo", "plank_photo", "burpee_photo", "vo2max_photo"]
        for key in photo_keys:
            uploaded_file = data.get(key)
            if uploaded_file is not None:
                filename = f"{data['test_date']}_{data['test_type']}_{key}.pdf"
                file_path = save_uploaded_file(uploaded_file, SPORT_TESTS_DIR, filename)
                if file_path:
                    sport_data_to_save[key] = file_path

        update_sport_tests_data(data["test_date"], data["test_type"], sport_data_to_save)
        st.success("Sporttest gespeichert! ✅")
        st.rerun()

    st.header("Daten (Sporttests)")
    if not sport_tests_df.empty:
        show_all_cols = st.checkbox("Alle Spalten anzeigen", value=False, key="sport_show_all_cols")
        if show_all_cols:
            display_cols = [c for c in SPORT_TESTS_COLUMNS if c in sport_tests_df.columns and c != "last_modified"]
        else:
            display_cols = [c for c in ["test_date", "test_type", "test_category", "distance_m", "time_sec", "vo2max", "notes"] if c in sport_tests_df.columns]
        display_df = sport_tests_df[display_cols].copy()
        display_df = display_df.fillna("")

        st.dataframe(display_df, use_container_width=True)
    else:
        st.info("Keine Sporttest-Daten vorhanden.")

with tab4:
    st.header("🩸 Bluttests")
    blood_submitted, blood_form_data = render_blood_tests_form()

    if blood_submitted:
        data = blood_form_data
        
        # Prepare data for saving
        blood_data_to_save = {
            "test_date": data["test_date"], "test_type": data["test_type"], "notes": data["notes"],
            # Rotes & weißes Blutbild
            "hemoglobin": data["hemoglobin"], "erythrocytes": data["erythrocytes"], "mcv": data["mcv"], "mch": data["mch"], "thrombocytes": data["thrombocytes"], "leukocytes": data["leukocytes"],
            "segment": data["segment"], "monocytes": data["monocytes"], "lymphocytes": data["lymphocytes"], "basophils": data["basophils"], "eosinophils": data["eosinophils"],
            # Blutchemie
            "alat": data["alat"], "asat": data["asat"], "creatinine": data["creatinine"], "egfr": data["egfr"], "iron": data["iron"], "transferrin_saturation": data["transferrin_saturation"],
            "gamma_gt": data["gamma_gt"], "ap": data["ap"], "iron_saturation": data["iron_saturation"], "ebk": data["ebk"], "ferritin": data["ferritin"], "transferrin": data["transferrin"],
            # Blutfette
            "cholesterol": data["cholesterol"], "triglycerides": data["triglycerides"], "ldl_chol": data["ldl_chol"],
            # Elektrolyte
            "sodium": data["sodium"], "calcium": data["calcium"], "potassium": data["potassium"],
            # Schilddrüsenhormone
            "tsh_basal": data["tsh_basal"],
            # Harnbefund
            "hk": data["hk"]
        }
        
        # Handle file upload
        uploaded_file = data.get("pdf_file")
        if uploaded_file is not None:
            filename = f"{data['test_date']}_{data['test_type']}_lab_report.pdf"
            file_path = save_uploaded_file(uploaded_file, BLOOD_TESTS_DIR, filename)
            if file_path:
                blood_data_to_save["pdf_file"] = file_path

        update_blood_tests_data(data["test_date"], data["test_type"], blood_data_to_save)
        st.success("Bluttest gespeichert! ✅")
        st.rerun()

    st.header("Daten (Bluttests)")
    if not blood_tests_df.empty:
        show_all_cols = st.checkbox("Alle Spalten anzeigen", value=False, key="blood_show_all_cols")
        if show_all_cols:
            display_cols = [c for c in BLOOD_TESTS_COLUMNS if c in blood_tests_df.columns and c != "last_modified"]
        else:
            display_cols = [c for c in ["test_date", "test_type", "hemoglobin", "ferritin", "cholesterol", "tsh_basal", "notes"] if c in blood_tests_df.columns]
        display_df = blood_tests_df[display_cols].copy()
        display_df = display_df.fillna("")

        st.dataframe(display_df, use_container_width=True)
    else:
        st.info("Keine Bluttest-Daten vorhanden.")

with tab5:
    render_analysis_section_v2(df, goals)
