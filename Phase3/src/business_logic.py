"""
Business Logic für das Studien-Dashboard
"""

from entities import Student, Studiengang, Semester, Modul
from data_access import JSONRepository


def ist_note_bestanden(note):
    """Prüft ob eine Note bestanden ist"""
    return note <= 4.0


def note_zu_text(note):
    """Wandelt Note in Text um"""
    if note <= 1.5:
        return "sehr gut"
    elif note <= 2.5:
        return "gut"
    elif note <= 3.5:
        return "befriedigend"
    elif note <= 4.0:
        return "ausreichend"
    else:
        return "nicht bestanden"


def berechne_notendurchschnitt(noten):
    """Berechnet Durchschnitt aus Liste von Noten"""
    # Achtung: leere Liste = 0.0
    if not noten:
        return 0.0
    return sum(noten) / len(noten)


class StudienManager:
    """Verwaltet die Studiendaten"""
    
    def __init__(self):
        self.repository = JSONRepository()
        self.student = None
        self.studiengang = None
    
    def set_student(self, student):
        """Setzt den aktuellen Studenten"""
        self.student = student
    
    def set_studiengang(self, studiengang):
        """Setzt den aktuellen Studiengang"""
        self.studiengang = studiengang
    
    def add_modul_note(self, semester_nr, modulcode, note, datum, typ="Klausur"):
        """Fügt eine Note zu einem Modul hinzu"""
        if not self.studiengang:
            return False
        
        semester = self.studiengang.get_semester_by_nummer(semester_nr)
        if not semester:
            return False
        
        for modul in semester.module:
            if modul.modulcode == modulcode:
                modul.set_note(note, datum, typ)
                return True
        return False
    
    def berechne_durchschnitt(self):
        """Berechnet den Notendurchschnitt"""
        if not self.studiengang:
            return 0.0
        
        noten_liste = []
        for semester in self.studiengang.semester:
            for modul in semester.module:
                # Note steht in der Prüfungsleistung
                if modul.pruefungsleistung and modul.pruefungsleistung.note is not None:
                    noten_liste.append(modul.pruefungsleistung.note)
        
        noten = noten_liste
        return berechne_notendurchschnitt(noten)
    
    def berechne_ects_gesamt(self):
        """Berechnet die erreichten ECTS gesamt"""
        if not self.studiengang:
            return 0
        
        ects = 0
        for semester in self.studiengang.semester:
            ects += semester.get_erreichte_ects()
        return ects
    
    def berechne_fortschritt(self):
        """Berechnet den Studienfortschritt in Prozent"""
        if not self.studiengang:
            return 0.0
        
        erreichte_ects = self.berechne_ects_gesamt()
        gesamt_ects = self.studiengang.gesamt_ects
        
        if gesamt_ects == 0:
            return 0.0
        
        return (erreichte_ects / gesamt_ects) * 100
    
    def get_statistiken(self):
        """Gibt einfache Statistiken zurück"""
        if not self.studiengang:
            return {}
        
        stats = {
            'durchschnitt': self.berechne_durchschnitt(),
            'ects_erreicht': self.berechne_ects_gesamt(),
            'ects_gesamt': self.studiengang.gesamt_ects,
            'fortschritt': self.berechne_fortschritt(),
            'anzahl_module': 0,
            'bestandene_module': 0
        }
        
        for semester in self.studiengang.semester:
            for modul in semester.module:
                stats['anzahl_module'] += 1
                if modul.ist_bestanden():
                    stats['bestandene_module'] += 1
        
        return stats
    
    def speichern(self):
        """Speichert die Daten"""
        if self.student and self.studiengang:
            return self.repository.save_data(self.student, self.studiengang)
        return False
    
    def laden(self):
        """Lädt die Daten"""
        data = self.repository.load_data()
        if data:
            self.student = data.get('student')
            self.studiengang = data.get('studiengang')
            return True
        return False
