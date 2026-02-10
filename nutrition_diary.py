# nutrition_diary.py
import streamlit as st
import pandas as pd
from datetime import datetime, date, timedelta
import os
from config import NUTRITION_FILE, ASSETS_DIR
from database import load_json, save_json, empty_df
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
import io

def load_nutrition_data() -> pd.DataFrame:
    """Lädt die Ernährungsdaten aus der CSV-Datei."""
    if os.path.exists(NUTRITION_FILE):
        df = pd.read_csv(NUTRITION_FILE)
        if not df.empty:
            # --- KORREKTUR HIER ---
            # Die .dt.date Konvertierung wurde entfernt, um das Datum im Pandas-Format zu belassen.
            df["date"] = pd.to_datetime(df["date"])
        return df
    return empty_df_nutrition()

def empty_df_nutrition() -> pd.DataFrame:
    """Erstellt einen leeren DataFrame für Ernährungsdaten."""
    return pd.DataFrame(columns=["date", "phase", "fruehstueck", "mittag", "abend", "snacks", "supplements", "notizen"])

def save_nutrition_data(df: pd.DataFrame) -> None:
    """Speichert den DataFrame in der CSV-Datei."""
    d = df.copy()
    if not d.empty:
        d["date"] = pd.to_datetime(d["date"]).dt.strftime("%Y-%m-%d")
    d.to_csv(NUTRITION_FILE, index=False)

def render_nutrition_form():
    """Rendert das Ernährungstagebuch-Formular."""
    with st.form(key="nutrition_form_key"):
        st.header("📓 Eintrag hinzufügen")
        
        col1, col2 = st.columns(2)
        date_val = col1.date_input("Datum", value=date.today(), key="nutrition_date_input")
        phase = col2.selectbox("Phase", ["Omnivor", "Vegan"], key="nutrition_phase_selectbox")
        
        st.subheader("Mahlzeiten")
        
        fruehstueck = st.text_area("Frühstück", key="fruehstueck_input", height=100)
        mittag = st.text_area("Mittag", key="mittag_input", height=100)
        abend = st.text_area("Abend", key="abend_input", height=100)
        snacks = st.text_area("Snacks", key="snacks_input", height=100)
        supplements = st.text_area("Supplements", key="supplements_input", height=100)
        notizen = st.text_area("Notizen / Bemerkungen", key="notizen_input", height=100)
        
        submitted = st.form_submit_button("Eintrag speichern")
        
        if submitted:
            # Daten laden
            df = load_nutrition_data()
            
            # Prüfen, ob für dieses Datum bereits ein Eintrag existiert
            existing_entry = df[df["date"] == pd.to_datetime(date_val)]
            
            if not existing_entry.empty:
                # Bestehenden Eintrag aktualisieren
                df.loc[df["date"] == pd.to_datetime(date_val), ["phase", "fruehstueck", "mittag", "abend", "snacks", "supplements", "notizen"]] = [
                    phase, fruehstueck, mittag, abend, snacks, supplements, notizen
                ]
                st.success("Eintrag wurde aktualisiert!")
            else:
                # Neuen Eintrag hinzufügen
                new_row = pd.DataFrame([{
                    "date": pd.to_datetime(date_val),
                    "phase": phase,
                    "fruehstueck": fruehstueck,
                    "mittag": mittag,
                    "abend": abend,
                    "snacks": snacks,
                    "supplements": supplements,
                    "notizen": notizen
                }])
                df = pd.concat([df, new_row], ignore_index=True)
                st.success("Eintrag wurde gespeichert!")
            
            # Daten speichern
            save_nutrition_data(df)
            st.rerun()

def render_nutrition_analysis_section(df: pd.DataFrame):
    """Rendert den Analyse-Bereich für das Ernährungstagebuch mit Filtern."""
    st.subheader("📈 Analyse & Auswertung")
    
    if df.empty:
        st.info("Keine Ernährungsdaten vorhanden.")
        return

    # Zeitraum-Auswahl mit Quick-Filters
    c1, c2, c3, c4, c5 = st.columns(5)
    default_start = (date.today() - timedelta(days=30))
    start_date = c1.date_input("Von", value=df["date"].min().date() if not df.empty else default_start, key="nutrition_start_date_input")
    end_date = c2.date_input("Bis", value=df["date"].max().date() if not df.empty else date.today(), key="nutrition_end_date_input")
    
    if c3.button("7T", key="nutrition_filter_7_days"): 
        start_date = date.today() - timedelta(days=7)
        st.rerun()
    if c4.button("14T", key="nutrition_filter_14_days"): 
        start_date = date.today() - timedelta(days=14)
        st.rerun()
    if c5.button("30T", key="nutrition_filter_30_days"): 
        start_date = date.today() - timedelta(days=30)
        st.rerun()
    
    # 60-Tage-Button mit Phasenvergleich
    c6, c7 = st.columns(2)
    is_60_days = c6.button("60T", key="nutrition_filter_60_days")
    phase_comparison = c7.checkbox("Phasenvergleich", value=is_60_days, key="nutrition_phase_comparison_toggle")
    
    if is_60_days:
        start_date = date.today() - timedelta(days=60)
        phase_comparison = True
        st.rerun()
    
    # Daten filtern
    sel_df = df[(df["date"] >= pd.to_datetime(start_date)) & (df["date"] <= pd.to_datetime(end_date))].copy()

    # Phasenvergleich-Modus
    if phase_comparison:
        st.markdown("---")
        st.header("🔄 Phasenvergleich: Omnivor vs. Vegan")
        
        # Filter-Chips
        show_omnivor = st.checkbox("Omnivor anzeigen", value=True, key="nutrition_show_omnivor")
        show_vegan = st.checkbox("Vegan anzeigen", value=True, key="nutrition_show_vegan")
        
        if not show_omnivor:
            sel_df = sel_df[sel_df['phase'] != 'Omnivor']
        if not show_vegan:
            sel_df = sel_df[sel_df['phase'] != 'Vegan']
        
        st.markdown("---")

    # Gefilterte Tabelle anzeigen
    st.header("📋 Gefilterte Ernährungseinträge")
    
    if sel_df.empty:
        st.info("Keine Daten im ausgewählten Zeitraum vorhanden.")
    else:
        # Nach Datum sortieren
        sel_df = sel_df.sort_values("date", ascending=False)
        
        # Daten für die Anzeige formatieren
        display_df = sel_df.copy()
        display_df["Datum"] = display_df["date"].dt.strftime("%d.%m.%Y")
        display_df["Phase"] = display_df["phase"]
        
        # Tabelle mit ausgewählten Spalten anzeigen
        st.dataframe(
            display_df[["Datum", "Phase", "fruehstueck", "mittag", "abend", "snacks", "supplements", "notizen"]],
            use_container_width=True,
            hide_index=True
        )

    # --- WICHTIG: Gefilterte Daten und Metadaten im Session State speichern ---
    st.session_state['filtered_nutrition_df'] = sel_df
    
    # Titel und Suffix für den Dateinamen basierend auf dem Filter erstellen
    if phase_comparison:
        pdf_title = f"Ernährungstagebuch - Phasenvergleich ({start_date.strftime('%d.%m.%Y')} - {end_date.strftime('%d.%m.%Y')})"
        pdf_suffix = f"phasenvergleich_{datetime.now().strftime('%Y%m%d')}"
    else:
        pdf_title = f"Ernährungstagebuch ({start_date.strftime('%d.%m.%Y')} - {end_date.strftime('%d.%m.%Y')})"
        pdf_suffix = f"{start_date.strftime('%Y%m%d')}_bis_{end_date.strftime('%Y%m%d')}"
    
    st.session_state['nutrition_pdf_title'] = pdf_title
    st.session_state['nutrition_pdf_suffix'] = pdf_suffix


def create_nutrition_pdf(df_to_export: pd.DataFrame, title: str):
    """Erstellt ein PDF mit den übergebenen Ernährungsdaten."""
    if df_to_export.empty:
        st.error("Keine Daten zum Exportieren vorhanden.")
        return None
    
    # PDF erstellen
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=2*cm, leftMargin=2*cm, topMargin=2*cm, bottomMargin=2*cm)
    
    # Styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(name='CustomTitle', parent=styles['Heading1'], fontSize=24, spaceAfter=30, alignment=TA_CENTER, textColor=colors.HexColor("#003366"), fontName='Helvetica-Bold')
    heading_style = ParagraphStyle(name='CustomHeading', parent=styles['Heading2'], fontSize=18, spaceAfter=12, textColor=colors.HexColor("#003366"), fontName='Helvetica-Bold')
    normal_style = ParagraphStyle(name='CustomNormal', parent=styles['Normal'], fontSize=12, spaceAfter=6, leading=14)
    
    story = []
    
    # Titel
    story.append(Paragraph(title, title_style))
    story.append(Spacer(1, 0.5*cm))
    story.append(Paragraph(f"Erstellt am: {datetime.now().strftime('%d.%m.%Y')}", normal_style))
    story.append(PageBreak())
    
    # Einträge
    for index, row in df_to_export.iterrows():
        # Datum und Phase
        story.append(Paragraph(f"<b>Datum:</b> {row['date'].strftime('%d.%m.%Y')} | <b>Phase:</b> {row['phase']}", heading_style))
        story.append(Spacer(1, 0.3*cm))
        
        # Tabelle mit Mahlzeiten
        data = [
            ["Mahlzeit", "Eintrag"],
            ["Frühstück", row['fruehstueck']],
            ["Mittag", row['mittag']],
            ["Abend", row['abend']],
            ["Snacks", row['snacks']],
            ["Supplements", row['supplements']],
            ["Notizen", row['notizen']]
        ]
        
        table = Table(data, colWidths=[4*cm, 12*cm])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#003366")),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor("#f2f2f2")),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(table)
        story.append(Spacer(1, 1*cm))
    
    doc.build(story)
    buffer.seek(0)
    return buffer