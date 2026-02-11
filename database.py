# database.py
import pandas as pd
import numpy as np
import json
import os
from datetime import datetime, date
from config import *

def load_json(path: str, default: dict) -> dict:
    """Lädt eine JSON-Datei oder erstellt sie mit Standardwerten."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        save_json(path, default)
        return default

def save_json(path: str, obj: dict) -> None:
    """Speichert ein Objekt in einer JSON-Datei."""
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2, ensure_ascii=False)

def empty_df() -> pd.DataFrame:
    """Erstellt einen leeren DataFrame mit den korrekten Spalten."""
    return pd.DataFrame(columns=COLUMNS)

def empty_nutrition_df() -> pd.DataFrame:
    """Erstellt einen leeren DataFrame für das Ernährungstagebuch."""
    return pd.DataFrame(columns=NUTRITION_COLUMNS)

def empty_sport_tests_df() -> pd.DataFrame:
    """Erstellt einen leeren DataFrame für die Sporttests."""
    return pd.DataFrame(columns=SPORT_TESTS_COLUMNS)

def empty_blood_tests_df() -> pd.DataFrame:
    """Erstellt einen leeren DataFrame für die Bluttests."""
    return pd.DataFrame(columns=BLOOD_TESTS_COLUMNS)

def load_data() -> pd.DataFrame:
    """Lädt die Hauptdaten aus der CSV-Datei."""
    if os.path.exists(DATA_FILE):
        df = pd.read_csv(DATA_FILE)
        if not df.empty:
            df["date"] = pd.to_datetime(df["date"]).dt.date
            
            # Neue Felder mit Standardwerten initialisieren, falls nicht vorhanden
            for col in COLUMNS:
                if col not in df.columns:
                    df[col] = None
                        
        return df
    return empty_df()

def load_nutrition_data() -> pd.DataFrame:
    """Lädt die Ernährungsdaten aus der CSV-Datei."""
    if os.path.exists(NUTRITION_FILE):
        df = pd.read_csv(NUTRITION_FILE)
        if not df.empty:
            df["date"] = pd.to_datetime(df["date"]).dt.date
            
            # Neue Felder mit Standardwerten initialisieren, falls nicht vorhanden
            for col in NUTRITION_COLUMNS:
                if col not in df.columns:
                    df[col] = None
                    
        return df
    return empty_nutrition_df()

def load_sport_tests_data() -> pd.DataFrame:
    """Lädt die Sporttest-Daten aus der CSV-Datei."""
    if os.path.exists(SPORT_TESTS_FILE):
        df = pd.read_csv(SPORT_TESTS_FILE)
        if not df.empty:
            df["test_date"] = pd.to_datetime(df["test_date"]).dt.date
            
            # Neue Felder mit Standardwerten initialisieren, falls nicht vorhanden
            for col in SPORT_TESTS_COLUMNS:
                if col not in df.columns:
                    df[col] = None
                    
        return df
    return empty_sport_tests_df()

def load_blood_tests_data() -> pd.DataFrame:
    """Lädt die Bluttest-Daten aus der CSV-Datei."""
    if os.path.exists(BLOOD_TESTS_FILE):
        df = pd.read_csv(BLOOD_TESTS_FILE)
        if not df.empty:
            df["test_date"] = pd.to_datetime(df["test_date"]).dt.date
            
            # Neue Felder mit Standardwerten initialisieren, falls nicht vorhanden
            for col in BLOOD_TESTS_COLUMNS:
                if col not in df.columns:
                    df[col] = None
                    
        return df
    return empty_blood_tests_df()

def save_data(df: pd.DataFrame) -> None:
    """Speichert den DataFrame in der CSV-Datei und erstellt ein Backup."""
    d = df.copy()
    if not d.empty:
        d["date"] = pd.to_datetime(d["date"]).dt.strftime("%Y-%m-%d")
    d.to_csv(DATA_FILE, index=False)
    
    # Backup erstellen
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    d.to_csv(os.path.join(BKP_DIR, f"daily_log_{ts}.csv"), index=False)

def save_nutrition_data(df: pd.DataFrame) -> None:
    """Speichert den Ernährungs-DataFrame in der CSV-Datei und erstellt ein Backup."""
    d = df.copy()
    if not d.empty:
        d["date"] = pd.to_datetime(d["date"]).dt.strftime("%Y-%m-%d")
    d.to_csv(NUTRITION_FILE, index=False)
    
    # Backup erstellen
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    d.to_csv(os.path.join(BKP_DIR, f"nutrition_log_{ts}.csv"), index=False)

def save_sport_tests_data(df: pd.DataFrame) -> None:
    """Speichert den Sporttests-DataFrame in der CSV-Datei und erstellt ein Backup."""
    d = df.copy()
    if not d.empty:
        d["test_date"] = pd.to_datetime(d["test_date"]).dt.strftime("%Y-%m-%d")
    d.to_csv(SPORT_TESTS_FILE, index=False)
    
    # Backup erstellen
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    d.to_csv(os.path.join(BKP_DIR, f"sport_tests_{ts}.csv"), index=False)

def save_blood_tests_data(df: pd.DataFrame) -> None:
    """Speichert den Bluttests-DataFrame in der CSV-Datei und erstellt ein Backup."""
    d = df.copy()
    if not d.empty:
        d["test_date"] = pd.to_datetime(d["test_date"]).dt.strftime("%Y-%m-%d")
    d.to_csv(BLOOD_TESTS_FILE, index=False)
    
    # Backup erstellen
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    d.to_csv(os.path.join(BKP_DIR, f"blood_tests_{ts}.csv"), index=False)

def update_data(date_val: date, phase_val: str, updated_data: dict) -> bool:
    """Aktualisiert einen bestehenden Datensatz anhand von Datum und Phase."""
    df = load_data()
    
    # Prüfen, ob der Datensatz existiert
    mask = (df["date"] == date_val) & (df["phase"] == phase_val)
    if not mask.any():
        return False
    
    # Backup vor der Änderung erstellen
    save_data(df)
    
    # Daten aktualisieren
    for key, value in updated_data.items():
        if key in df.columns:
            df.loc[mask, key] = value
    
    # Zeitstempel der letzten Änderung hinzufügen
    df.loc[mask, "last_modified"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Metriken neu berechnen
    df = compute_metrics(df)
    
    # Speichern
    save_data(df)
    return True

def update_nutrition_data(date_val: date, phase_val: str, updated_data: dict) -> bool:
    """Aktualisiert einen bestehenden Ernährungsdatensatz anhand von Datum und Phase.

    - Wenn kein Eintrag existiert, wird ein neuer Datensatz mit allen NUTRITION_COLUMNS angelegt.
    - last_modified wird in beiden Fällen korrekt gesetzt.
    """
    df = load_nutrition_data()

    # Datensatz finden
    mask = (df["date"] == date_val) & (df["phase"] == phase_val)

    if not mask.any():
        # Neuer Eintrag
        new_row_data = {col: None for col in NUTRITION_COLUMNS}
        new_row_data.update({"date": date_val, "phase": phase_val})
        new_row_data.update(updated_data)
        new_row_data["last_modified"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        df = pd.concat([df, pd.DataFrame([new_row_data])], ignore_index=True)
    else:
        # Backup vor der Änderung erstellen
        save_nutrition_data(df)

        # Update bestehenden Eintrag
        for key, value in updated_data.items():
            if key in df.columns:
                df.loc[mask, key] = value

        df.loc[mask, "last_modified"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    save_nutrition_data(df)
    return True

def update_sport_tests_data(test_date_val: date, test_type_val: str, updated_data: dict) -> bool:
    """Aktualisiert einen bestehenden Sporttest-Datensatz anhand von Datum und Testtyp."""
    df = load_sport_tests_data()
    
    # Prüfen, ob der Datensatz existiert
    mask = (df["test_date"] == test_date_val) & (df["test_type"] == test_type_val)
    if not mask.any():
        # Wenn nicht existent, erstelle einen neuen Eintrag
        new_row_data = {col: None for col in SPORT_TESTS_COLUMNS}
        new_row_data.update({"test_date": test_date_val, "test_type": test_type_val, **updated_data})
        df = pd.concat([df, pd.DataFrame([new_row_data])], ignore_index=True)
    else:
        # Backup vor der Änderung erstellen
        save_sport_tests_data(df)
        # Daten aktualisieren
        for key, value in updated_data.items():
            if key in df.columns:
                df.loc[mask, key] = value

    # Zeitstempel der letzten Änderung hinzufügen
    # (Wichtig: nach pd.concat muss der Mask-Filter neu auf dem aktuellen DataFrame berechnet werden.)
    if "last_modified" not in df.columns:
        df["last_modified"] = None
    mask = (df["test_date"] == test_date_val) & (df["test_type"] == test_type_val)
    df.loc[mask, "last_modified"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Speichern
    save_sport_tests_data(df)
    return True

def update_blood_tests_data(test_date_val: date, test_type_val: str, updated_data: dict) -> bool:
    """Aktualisiert einen bestehenden Bluttest-Datensatz anhand von Datum und Testtyp."""
    df = load_blood_tests_data()
    
    # Prüfen, ob der Datensatz existiert
    mask = (df["test_date"] == test_date_val) & (df["test_type"] == test_type_val)
    if not mask.any():
        # Wenn nicht existent, erstelle einen neuen Eintrag
        new_row_data = {col: None for col in BLOOD_TESTS_COLUMNS}
        new_row_data.update({"test_date": test_date_val, "test_type": test_type_val, **updated_data})
        df = pd.concat([df, pd.DataFrame([new_row_data])], ignore_index=True)
    else:
        # Backup vor der Änderung erstellen
        save_blood_tests_data(df)
        # Daten aktualisieren
        for key, value in updated_data.items():
            if key in df.columns:
                df.loc[mask, key] = value

    # Zeitstempel der letzten Änderung hinzufügen
    # (Wichtig: nach pd.concat muss der Mask-Filter neu auf dem aktuellen DataFrame berechnet werden.)
    if "last_modified" not in df.columns:
        df["last_modified"] = None
    mask = (df["test_date"] == test_date_val) & (df["test_type"] == test_type_val)
    df.loc[mask, "last_modified"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Speichern
    save_blood_tests_data(df)
    return True

def delete_data(date_val: date, phase_val: str) -> bool:
    """Löscht einen Datensatz anhand von Datum und Phase."""
    df = load_data()
    
    # Prüfen, ob der Datensatz existiert
    mask = (df["date"] == date_val) & (df["phase"] == phase_val)
    if not mask.any():
        return False
    
    # Backup vor der Löschung erstellen
    save_data(df)
    
    # Datensatz löschen
    df = df[~mask].copy()
    
    # Speichern
    save_data(df)
    return True

def delete_nutrition_data(date_val: date, phase_val: str) -> bool:
    """Löscht einen Ernährungsdatensatz anhand von Datum und Phase."""
    df = load_nutrition_data()
    
    # Prüfen, ob der Datensatz existiert
    mask = (df["date"] == date_val) & (df["phase"] == phase_val)
    if not mask.any():
        return False
    
    # Backup vor der Löschung erstellen
    save_nutrition_data(df)
    
    # Datensatz löschen
    df = df[~mask].copy()
    
    # Speichern
    save_nutrition_data(df)
    return True

def delete_sport_tests_data(test_date_val: date, test_type_val: str) -> bool:
    """Löscht einen Sporttest-Datensatz anhand von Datum und Testtyp."""
    df = load_sport_tests_data()
    
    # Prüfen, ob der Datensatz existiert
    mask = (df["test_date"] == test_date_val) & (df["test_type"] == test_type_val)
    if not mask.any():
        return False
    
    # Backup vor der Löschung erstellen
    save_sport_tests_data(df)
    
    # Datensatz löschen
    df = df[~mask].copy()
    
    # Speichern
    save_sport_tests_data(df)
    return True

def delete_blood_tests_data(test_date_val: date, test_type_val: str) -> bool:
    """Löscht einen Bluttest-Datensatz anhand von Datum und Testtyp."""
    df = load_blood_tests_data()
    
    # Prüfen, ob der Datensatz existiert
    mask = (df["test_date"] == test_date_val) & (df["test_type"] == test_type_val)
    if not mask.any():
        return False
    
    # Backup vor der Löschung erstellen
    save_blood_tests_data(df)
    
    # Datensatz löschen
    df = df[~mask].copy()
    
    # Speichern
    save_blood_tests_data(df)
    return True

def compute_metrics(df: pd.DataFrame) -> pd.DataFrame:
    """Berechnet alle abgeleiteten Metriken."""
    df = df.copy()
    if df.empty:
        return df
    
    # Wochentag robust erzeugen (ohne Locale-Abhängigkeit; Streamlit Cloud kompatibel)
    
    _weekday_idx = pd.to_datetime(df["date"]).dt.weekday  # 0=Mo ... 6=So
    
    _weekday_map = {0: "Montag", 1: "Dienstag", 2: "Mittwoch", 3: "Donnerstag", 4: "Freitag", 5: "Samstag", 6: "Sonntag"}
    
    df["weekday"] = _weekday_idx.map(_weekday_map)

    # Die Nährstoffdaten sind jetzt bereits in df, da sie im Tagesformular eingegeben werden.
    # Ein Merge ist nicht mehr nötig, aber wir behalten ihn zur Sicherheit, falls Daten nur im Ernährungstab eingegeben werden.
    nutrition_df = load_nutrition_data()
    if not nutrition_df.empty:
        # Ergänze fehlende Tage aus dem Ernährungstagebuch in die Hauptdaten,
        # damit Diagramme auch bei reiner Eingabe im Ernährungstab dargestellt werden können.
        required_cols = ["date", "phase", "intake_kcal", "carbs_g", "protein_g", "fat_g", "water_ml"]
        for col in required_cols:
            if col not in nutrition_df.columns:
                nutrition_df[col] = None

        nutrition_subset = nutrition_df[required_cols].copy()

        # Identifiziere (date, phase), die im Haupt-Log noch fehlen
        main_keys = set(zip(df["date"], df["phase"])) if ("date" in df.columns and "phase" in df.columns) else set()
        nutrition_keys = list(zip(nutrition_subset["date"], nutrition_subset["phase"]))
        missing_mask = [k not in main_keys for k in nutrition_keys]
        missing_nutrition = nutrition_subset.loc[missing_mask]

        if not missing_nutrition.empty:
            # Erzeuge leere Zeilen im Schema der Hauptdaten
            new_rows = pd.DataFrame({c: [np.nan] * len(missing_nutrition) for c in df.columns})
            new_rows["date"] = missing_nutrition["date"].values
            new_rows["phase"] = missing_nutrition["phase"].values
            new_rows["intake_kcal"] = missing_nutrition["intake_kcal"].values
            new_rows["carbs_g"] = missing_nutrition["carbs_g"].values
            new_rows["protein_g"] = missing_nutrition["protein_g"].values
            new_rows["fat_g"] = missing_nutrition["fat_g"].values
            new_rows["water_ml"] = missing_nutrition["water_ml"].values
            df = pd.concat([df, new_rows], ignore_index=True).sort_values("date")
        # Merge mit Ernährungsdaten, um fehlende Werte zu ergänzen
        df = df.merge(nutrition_df[["date", "phase", "intake_kcal", "carbs_g", "protein_g", "fat_g", "water_ml"]], 
                     on=["date", "phase"], how="left", suffixes=('', '_from_nutrition'))
        
        # Bevorzuge die Werte aus dem Haupt-Log, falls vorhanden
        for col in ["intake_kcal", "carbs_g", "protein_g", "fat_g", "water_ml"]:
            if f'{col}_from_nutrition' in df.columns:
                df[col] = df[col].fillna(df[f'{col}_from_nutrition'])
                df.drop(columns=[f'{col}_from_nutrition'], inplace=True)

    df["total_kcal_burn"] = df["total_kcal_burn"].fillna(0)
    df["intake_kcal"] = df["intake_kcal"].fillna(0)
    df["energy_balance"] = df["intake_kcal"] - df["total_kcal_burn"]
    df["protein_g_per_kg"] = np.where(df["body_weight"] > 0, df["protein_g"] / df["body_weight"], np.nan)
    df["recovery_index"] = np.where((df["hrv_sleep_avg"] > 0) & (df["rhr_sleep_avg"] > 0),
                                     df["hrv_sleep_avg"] * df["sleep_score"] / df["rhr_sleep_avg"], np.nan)
    
    # Load Score wird nicht mehr berechnet, da es keine Trainingsdaten mehr gibt.
    df["load_score"] = np.nan
    
    df["wellbeing_score"] = pd.to_numeric(df[["energy", "mood", "motivation"]].mean(axis=1), errors="coerce")
    df["stress_balance"] = np.where(df["stress_avg"].notna(), 100 - df["stress_avg"], np.nan)
    return df

def load_goals() -> dict:
    """Lädt die Ziele aus der JSON-Datei."""
    return load_json(GOALS_FILE, DEFAULT_GOALS)

def save_goals(goals: dict) -> None:
    """Speichert die Ziele in der JSON-Datei."""
    save_json(GOALS_FILE, goals)
