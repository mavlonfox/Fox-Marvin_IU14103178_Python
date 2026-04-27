"""
Data Access für das Studien-Dashboard
"""

import json
import os
from datetime import datetime
from abc import ABC, abstractmethod
from entities import Student, Studiengang


class DataRepository(ABC):
    """Abstrakte Schnittstelle für Datenspeicherung."""

    @abstractmethod
    def save_data(self, student, studiengang):
        pass

    @abstractmethod
    def load_data(self):
        pass

    @abstractmethod
    def file_exists(self):
        pass

    @abstractmethod
    def delete_data(self):
        pass


class JSONRepository(DataRepository):
    """Einfache JSON-Datenspeicherung"""
    
    def __init__(self, filename="studien_dashboard.json"):
        self.filename = filename
        if os.path.isabs(filename):
            self.filepath = filename
            self.data_folder = os.path.dirname(filename)
        else:
            basis_ordner = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            self.data_folder = os.path.join(basis_ordner, "data")
            self.filepath = os.path.join(self.data_folder, self.filename)

        if not os.path.exists(self.data_folder):
            os.makedirs(self.data_folder)
    
    def save_data(self, student, studiengang):
        """Speichert Student und Studiengang als JSON"""
        try:
            data = {
                'student': student.to_dict(),
                'studiengang': studiengang.to_dict(),
                'last_saved': datetime.now().isoformat(),
                'version': '1.0'
            }
            
            with open(self.filepath, 'w', encoding='utf-8') as file:
                json.dump(data, file, indent=2, ensure_ascii=False)
            
            return True
            
        except Exception as e:
            print(f"Fehler beim Speichern: {e}")
            return False
    
    def load_data(self):
        """Lädt Daten aus JSON-Datei"""
        if not os.path.exists(self.filepath):
            print("Keine gespeicherten Daten gefunden")
            return None
        
        try:
            with open(self.filepath, 'r', encoding='utf-8') as file:
                data = json.load(file)
            
            # Student erstellen
            student_data = data.get('student')
            if student_data:
                student = Student("", "", "", "")
                student.from_dict(student_data)
            else:
                student = None
            
            # Studiengang erstellen
            studiengang_data = data.get('studiengang')
            if studiengang_data:
                studiengang = Studiengang("", "", 0, 0)
                studiengang.from_dict(studiengang_data)
            else:
                studiengang = None
            
            return {
                'student': student,
                'studiengang': studiengang
            }
            
        except Exception as e:
            print(f"Fehler beim Laden: {e}")
            return None
    
    def file_exists(self):
        """Prüft ob Datei existiert"""
        return os.path.exists(self.filepath)
    
    def delete_data(self):
        """Löscht die Datendatei"""
        try:
            if os.path.exists(self.filepath):
                os.remove(self.filepath)
                return True
            return False
        except Exception as e:
            print(f"Fehler beim Löschen: {e}")
            return False
