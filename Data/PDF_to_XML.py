import argparse
import os

import fitz  # PyMuPDF
import re
import pandas as pd
import xml.etree.ElementTree as ET

TEAM_A_IDENTIFIER = 'A'
TEAM_B_IDENTIFIER = 'B'
LEAGUE_IDENTIFIER = 'FEDERAZIONE ITALIANA GIUOCO HANDBALL'

def extract_text_from_pdf(pdf_path):
    """Extracts text from a PDF file."""
    text = ""
    with fitz.open(pdf_path) as doc:
        for page in doc:
            text += page.get_text()
    return text

def extract_player_performance_with_all_discipline(lines):
    """
    Extract player performance and all discipline data from the given lines of text.
    """
    players_data = []
    current_team = ""
    i = 0

    while i < len(lines):
        line = lines[i].strip()
        if line in [TEAM_A_IDENTIFIER, TEAM_B_IDENTIFIER]:  # Team identifiers
            current_team = lines[i + 1].strip()  # Next line is the team name
            i += 2  # Skip to the line after the team name
        elif line.isdigit():  # Player number
            player_number = int(line)
            player_name = lines[i + 1].strip()  # Next line is the player name
            # The next line could be goals or a timestamp for discipline
            try:
                goals = int(lines[i + 2].strip())
                discipline_times = []
                j = i + 3
                # Loop to collect all discipline timestamps
                while j < len(lines) and re.match(r'\d{2}:\d{2}', lines[j].strip()):
                    discipline_times.append(lines[j].strip())
                    j += 1

                players_data.append({
                    "Team": current_team,
                    "Number": player_number,
                    "Name": player_name,
                    "Goals": goals,
                    "Discipline_Times": ', '.join(discipline_times)
                })
                i = j  # Move to the next player
            except ValueError as e:
                if lines[i + 2].strip() not in ['2° tempo', '2° extra']:
                    print(f"Error processing player {player_number}: {e}")
                i += 1
        else:
            i += 1  # Move to the next line if the current line is not useful

    return pd.DataFrame(players_data)[:-1]

def extract_corrected_match_details_improved(lines, team_names):
    """
    Extracts corrected match details from the given lines of text, using improved logic.
    """
    match_details = {
        "League": "",
        "Match_Number": "",
        "Final_Score": "",
        "Location": "",
        "Date": "",
        "Team_A": team_names[0],
        "Team_B": team_names[1],
        "First_Period_Score": "",
        "Seven_m_Throws_Goals": "",
        "Arbitro_1": "",
        "Arbitro_2": ""
    }

    for i, line in enumerate(lines):
        line = line.strip()
        if LEAGUE_IDENTIFIER in line:
            match_details["League"] = lines[i + 1].strip()
        elif 'Numero gara' in line:
            match_details["Match_Number"] = line.split()[-1]
        elif 'Risultato finale' in line:
            match_details["Final_Score"] = lines[i + 1].strip()
        elif 'Località' in line:
            match_details["Location"] = lines[i + 1].strip()
        elif 'Data' in line:
            match_details["Date"] = lines[i + 1].strip()
        elif '1° tempo' in line:
            match_details["First_Period_Score"] = lines[i + 1].strip() + ' - ' + lines[i + 2].strip()
        elif '7m. tiri/reti' in line:
            match_details["Seven_m_Throws_Goals"] = lines[i + 1].strip() + ' - ' + lines[i + 2].strip()
        elif 'Arbitro 1' in line:
            match_details["Arbitro_1"] = lines[i + 1].strip()
        elif 'Arbitro 2' in line:
            match_details["Arbitro_2"] = lines[i + 1].strip()

    return pd.DataFrame([match_details])

def dataframe_to_xml(df, root_element_name, row_element_name):
    """
    Convert a DataFrame to a formatted XML string.
    """
    root = ET.Element(root_element_name)

    for _, row in df.iterrows():
        row_element = ET.SubElement(root, row_element_name)
        for field in df.columns:
            field_element = ET.SubElement(row_element, field)
            field_element.text = str(row[field])

    def indent(elem, level=0):
        i = "\n" + level * "  "
        if len(elem):
            if not elem.text or not elem.text.strip():
                elem.text = i + "  "
            if not elem.tail or not elem.tail.strip():
                elem.tail = i
            for elem in elem:
                indent(elem, level + 1)
            if not elem.tail or not elem.tail.strip():
                elem.tail = i
        else:
            if level and (not elem.tail or not elem.tail.strip()):
                elem.tail = i

    indent(root)
    return ET.tostring(root, encoding='unicode')

def process_pdf_to_xml(pdf_file_path):
    # Extracting text from the PDF
    extracted_text = extract_text_from_pdf(pdf_file_path)
    lines = extracted_text.split('\n')

    # Extracting player performance and discipline data
    player_performance_df = extract_player_performance_with_all_discipline(lines)

    # Splitting and formatting the 'Discipline_Times' column
    discipline_columns = player_performance_df['Discipline_Times'].str.split(',', expand=True)
    discipline_columns.columns = [f'Discipline_{i + 1}' for i in range(discipline_columns.shape[1])]
    full_player_performance_discipline_split_df = player_performance_df.join(discipline_columns)
    full_player_performance_discipline_split_df = full_player_performance_discipline_split_df.drop('Discipline_Times', axis=1)

    # Correcting the player performance DataFrame by removing the last row
    corrected_player_performance_df = full_player_performance_discipline_split_df[:-1]

    # Extracting match details
    team_names = corrected_player_performance_df['Team'].unique()
    corrected_match_details_df = extract_corrected_match_details_improved(lines, team_names)

    # Convert match details DataFrame to XML
    match_details_xml = dataframe_to_xml(corrected_match_details_df, "MatchDetails", "Detail")

    # Convert player performance DataFrame to XML
    player_performance_xml = dataframe_to_xml(corrected_player_performance_df, "PlayerPerformances", "Player")

    # Combine both XML strings into a single XML
    combined_xml = f"<HandballMatch>\n{match_details_xml}\n{player_performance_xml}\n</HandballMatch>"

    return combined_xml

def main():
    parser = argparse.ArgumentParser(description="Process PDF files and generate XML files.")
    parser.add_argument("pdf_directory", help="Path to the directory containing PDF files.")
    parser.add_argument("xml_directory", help="Path to the directory where XML files will be saved.")

    args = parser.parse_args()

    pdf_directory = args.pdf_directory
    xml_directory = args.xml_directory

    extracted_files = [filename for filename in os.listdir(pdf_directory) if filename.endswith(".pdf")]

    for pdf_file in extracted_files:
        pdf_file_path = os.path.join(pdf_directory, pdf_file)
        xml_content = process_pdf_to_xml(pdf_file_path)
        xml_file_name = pdf_file.replace('.pdf', '.xml')
        xml_file_path = os.path.join(xml_directory, xml_file_name)

        with open(xml_file_path, 'w') as file:
            file.write(xml_content)

    xml_file_paths = [os.path.join(xml_directory, filename.replace('.pdf', '.xml')) for filename in extracted_files]
    print(xml_file_paths)  # List of paths to the created XML files

if __name__ == "__main__":
    main()
