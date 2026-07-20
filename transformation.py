#!/usr/bin/env python3

import csv

# Mapping des noms de colonnes (Anglais -> Français)
COLUMN_MAPPING = {
    "Hours_Studied": "Heures_Etudiees",
    "Attendance": "Presence",
    "Parental_Involvement": "Implication_Parentale",
    "Access_to_Resources": "Acces_aux_Ressources",
    "Extracurricular_Activities": "Activites_Extrascolaires",
    "Sleep_Hours": "Heures_Sommeil",
    "Previous_Scores": "Scores_Precedents",
    "Motivation_Level": "Niveau_Motivation",
    "Internet_Access": "Acces_Internet",
    "Tutoring_Sessions": "Sessions_Tutorat",
    "Family_Income": "Revenu_Famille",
    "Teacher_Quality": "Qualite_Enseignant",
    "School_Type": "Type_Ecole",
    "Peer_Influence": "Influence_Entourage",
    "Physical_Activity": "Activite_Physique",
    "Learning_Disabilities": "Troubles_Apprentissage",
    "Parental_Education_Level": "Niveau_Education_Parents",
    "Distance_from_Home": "Distance_Maison",
    "Gender": "Genre",
    "Exam_Score": "Score_Examen"
}

# Mapping des valeurs (Anglais -> Français)
VALUE_MAPPING = {
    # Low/Medium/High
    "Low": "Bas",
    "Medium": "Moyen",
    "High": "Haut",
    # Yes/No
    "Yes": "Oui",
    "No": "Non",
    # School Type
    "Public": "Publique",
    "Private": "Privee",
    # Peer Influence
    "Negative": "Negative",
    "Neutral": "Neutre",
    "Positive": "Positif",
    # Parental Education Level
    "High School": "Lycee",
    "College": "Licence",
    "Postgraduate": "Master",
    # Distance from Home
    "Near": "Proche",
    "Moderate": "Moderee",
    "Far": "Loin",
    # Gender
    "Male": "Homme",
    "Female": "Femme"
}


def has_null_values(row):
    # Vérifie si une ligne contient des valeurs nulles ou vides
    for value in row.values():
        if value is None or value.strip() == '':
            return True
    return False


def row_to_tuple(row):
    return tuple(row.values())


def transform_csv(input_file, output_file):
    seen_rows = set()  # Pour détecter les doublons
    total_rows = 0
    duplicates_removed = 0
    null_rows_removed = 0
    
    with open(input_file, 'r', encoding='utf-8') as infile:
        reader = csv.DictReader(infile)
        
        # Renommer les colonnes
        new_fieldnames = [COLUMN_MAPPING.get(col, col) for col in reader.fieldnames]
        
        with open(output_file, 'w', encoding='utf-8', newline='') as outfile:
            writer = csv.DictWriter(outfile, fieldnames=new_fieldnames)
            writer.writeheader()
            
            for row in reader:
                total_rows += 1
                
                # Vérifier les valeurs nulles/vides
                if has_null_values(row):
                    null_rows_removed += 1
                    continue
                
                new_row = {}
                for old_col, value in row.items():
                    # Renommer la colonne
                    new_col = COLUMN_MAPPING.get(old_col, old_col)
                    # Traduire la valeur si elle existe dans le mapping
                    new_value = VALUE_MAPPING.get(value, value)
                    new_row[new_col] = new_value
                
                # Vérifier les doublons
                row_tuple = row_to_tuple(new_row)
                if row_tuple in seen_rows:
                    duplicates_removed += 1
                    continue
                
                seen_rows.add(row_tuple)
                writer.writerow(new_row)
    
    rows_written = total_rows - duplicates_removed - null_rows_removed
    print(f"Transformation terminée: {output_file}")
    print(f"  - Lignes totales: {total_rows}")
    print(f"  - Doublons supprimés: {duplicates_removed}")
    print(f"  - Lignes avec valeurs nulles supprimées: {null_rows_removed}")
    print(f"  - Lignes écrites: {rows_written}")


if __name__ == "__main__":
    input_csv = "StudentPerformanceFactors.csv"
    output_csv = "StudentPerformanceFactors_propre.csv"
    
    transform_csv(input_csv, output_csv)
