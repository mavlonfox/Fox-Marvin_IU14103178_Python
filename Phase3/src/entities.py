"""
Entity-Klassen für das Studien-Dashboard
"""

from datetime import datetime, date
from abc import ABC, abstractmethod


class Student:
    """Repräsentiert einen Studenten mit seinen Grunddaten"""
    
    def __init__(self, matrikelnummer, vorname, nachname, email):
        self.matrikelnummer = matrikelnummer
        self.vorname = vorname
        self.nachname = nachname
        self.email = email
        self.einschreibedatum = datetime.now()
    
    def get_vollname(self):
        return f"{self.vorname} {self.nachname}"
    
    def to_dict(self):
        return {
            'matrikelnummer': self.matrikelnummer,
            'vorname': self.vorname,
            'nachname': self.nachname,
            'email': self.email,
            'einschreibedatum': self.einschreibedatum.isoformat()
        }
    
    def from_dict(self, data):
        # Daten aus JSON übernehmen
        self.matrikelnummer = data['matrikelnummer']
        self.vorname = data['vorname']
        self.nachname = data['nachname']
        self.email = data['email']
        if 'einschreibedatum' in data:
            self.einschreibedatum = datetime.fromisoformat(data['einschreibedatum'])
    
    def __str__(self):
        return f"Student({self.matrikelnummer}, {self.get_vollname()})"


class Studiengang:
    """Repräsentiert einen Studiengang"""
    
    def __init__(self, name, abschluss, regelstudienzeit, gesamt_ects):
        self.name = name
        self.abschluss = abschluss
        self.regelstudienzeit = regelstudienzeit
        self.gesamt_ects = gesamt_ects
        self.semester = []
    
    def add_semester(self, semester):
        self.semester.append(semester)
    
    def get_semester_by_nummer(self, nummer):
        for semester in self.semester:
            if semester.nummer == nummer:
                return semester
        return None
    
    def to_dict(self):
        return {
            'name': self.name,
            'abschluss': self.abschluss,
            'regelstudienzeit': self.regelstudienzeit,
            'gesamt_ects': self.gesamt_ects,
            'semester': [sem.to_dict() for sem in self.semester]
        }
    
    def from_dict(self, data):
        self.name = data['name']
        self.abschluss = data['abschluss']
        self.regelstudienzeit = data['regelstudienzeit']
        self.gesamt_ects = data['gesamt_ects']
        self.semester = []
        for sem_data in data.get('semester', []):
            semester = Semester.from_dict_new(sem_data)
            self.semester.append(semester)
    
    def __str__(self):
        return f"Studiengang({self.name} {self.abschluss})"


class Semester:
    """Repräsentiert ein Semester"""
    
    def __init__(self, nummer, bezeichnung, startdatum, enddatum, geplante_ects):
        self.nummer = nummer
        self.bezeichnung = bezeichnung
        self.startdatum = startdatum
        self.enddatum = enddatum
        self.geplante_ects = geplante_ects
        self.module = []
    
    def add_modul(self, modul):
        self.module.append(modul)
    
    def get_erreichte_ects(self):
        ects = 0
        for modul in self.module:
            if modul.note and modul.note <= 4.0:  # bestanden
                ects += modul.ects_punkte
        return ects
    
    def to_dict(self):
        return {
            'nummer': self.nummer,
            'bezeichnung': self.bezeichnung,
            'startdatum': self.startdatum.isoformat() if self.startdatum else None,
            'enddatum': self.enddatum.isoformat() if self.enddatum else None,
            'geplante_ects': self.geplante_ects,
            'module': [modul.to_dict() for modul in self.module]
        }
    
    @classmethod
    def from_dict_new(cls, data):
        startdatum = date.fromisoformat(data['startdatum']) if data['startdatum'] else None
        enddatum = date.fromisoformat(data['enddatum']) if data['enddatum'] else None
        semester = cls(data['nummer'], data['bezeichnung'], startdatum,
                       enddatum, data['geplante_ects'])
        semester.from_dict(data)
        return semester

    def from_dict(self, data):
        self.nummer = data['nummer']
        self.bezeichnung = data['bezeichnung']
        self.startdatum = date.fromisoformat(data['startdatum']) if data['startdatum'] else None
        self.enddatum = date.fromisoformat(data['enddatum']) if data['enddatum'] else None
        self.geplante_ects = data['geplante_ects']
        self.module = []
        for modul_data in data.get('module', []):
            modul = Modul("", "", 0)
            modul.from_dict(modul_data)
            self.module.append(modul)
    
    def __str__(self):
        return f"Semester {self.nummer}: {self.bezeichnung}"


class Modul:
    """Repräsentiert ein Modul"""
    
    def __init__(self, modulcode, name, ects_punkte, beschreibung="", dozent=""):
        self.modulcode = modulcode
        self.name = name
        self.ects_punkte = ects_punkte
        self.beschreibung = beschreibung
        self.dozent = dozent
        # Alte Felder für frühere Daten
        self.note = None
        self.datum = None
        self.versuch = 1
        self.typ = ""  # "Klausur" oder "Portfolio"
        # Prüfungsleistung als eigenes Objekt
        self.pruefungsleistung = None  # Instanz von Pruefungsleistung
    
    def set_note(self, note, datum, typ="Klausur"):
        if not (1.0 <= note <= 5.0):
            print("Fehler: Note muss zwischen 1.0 und 5.0 liegen")
            return
        # Felder setzen
        self.note = note
        self.datum = datum
        self.typ = typ
        # Prüfungsleistung als Objekt anlegen
        if typ == "Portfolio":
            self.pruefungsleistung = Portfolio(note=note, datum=datum, versuch=self.versuch)
        else:
            self.pruefungsleistung = Klausur(note=note, datum=datum, versuch=self.versuch)
    
    def ist_bestanden(self):
        if self.pruefungsleistung is not None:
            return self.pruefungsleistung.ist_bestanden()
        # Fallback für ältere Daten
        return self.note is not None and self.note <= 4.0
    
    def to_dict(self):
        data = {
            'modulcode': self.modulcode,
            'name': self.name,
            'ects_punkte': self.ects_punkte,
            'beschreibung': self.beschreibung,
            'dozent': self.dozent,
            'note': self.note,
            'datum': self.datum.isoformat() if self.datum else None,
            'versuch': self.versuch,
            'typ': self.typ
        }
        if self.pruefungsleistung is not None:
            data['pruefungsleistung'] = self.pruefungsleistung.to_dict()
        return data
    
    def from_dict(self, data):
        self.modulcode = data['modulcode']
        self.name = data['name']
        self.ects_punkte = data['ects_punkte']
        self.beschreibung = data.get('beschreibung', '')
        self.dozent = data.get('dozent', '')
        self.note = data.get('note')
        self.datum = date.fromisoformat(data['datum']) if data.get('datum') else None
        self.versuch = data.get('versuch', 1)
        self.typ = data.get('typ', '')
        self.pruefungsleistung = None
        pl_data = data.get('pruefungsleistung')
        if pl_data and isinstance(pl_data, dict):
            typ = pl_data.get('typ', 'Klausur')
            if typ == 'Portfolio':
                pl = Portfolio(note=pl_data.get('note'),
                               datum=date.fromisoformat(pl_data['datum']) if pl_data.get('datum') else None,
                               versuch=pl_data.get('versuch', 1),
                               seitenzahl=pl_data.get('seitenzahl'))
            else:
                pl = Klausur(note=pl_data.get('note'),
                             datum=date.fromisoformat(pl_data['datum']) if pl_data.get('datum') else None,
                             versuch=pl_data.get('versuch', 1),
                             dauer_minuten=pl_data.get('dauer_minuten'))
            self.pruefungsleistung = pl
            self.note = pl.note
            self.datum = pl.datum
            self.versuch = pl.versuch
            self.typ = pl.get_typ()
    
    def __str__(self):
        status = "bestanden" if self.ist_bestanden() else "offen"
        return f"Modul({self.modulcode}, {self.name}, {status})"


class Pruefungsleistung(ABC):
    """Abstrakte Basisklasse für Prüfungsleistungen."""

    def __init__(self, note, datum, versuch=1):
        self.note = note
        self.datum = datum
        self.versuch = versuch

    @abstractmethod
    def get_typ(self):
        pass

    def ist_bestanden(self):
        return self.note is not None and self.note <= 4.0

    def to_dict(self):
        return {
            'typ': self.get_typ(),
            'note': self.note,
            'datum': self.datum.isoformat() if self.datum else None,
            'versuch': self.versuch,
        }


class Klausur(Pruefungsleistung):
    """Klausur als Prüfungsleistung"""

    def __init__(self, note, datum, versuch=1, dauer_minuten=None):
        super().__init__(note, datum, versuch)
        self.dauer_minuten = dauer_minuten

    def get_typ(self):
        return "Klausur"

    def to_dict(self):
        data = super().to_dict()
        data['dauer_minuten'] = self.dauer_minuten
        return data


class Portfolio(Pruefungsleistung):
    """Portfolio als Prüfungsleistung"""

    def __init__(self, note, datum, versuch=1, seitenzahl=None):
        super().__init__(note, datum, versuch)
        self.seitenzahl = seitenzahl

    def get_typ(self):
        return "Portfolio"

    def to_dict(self):
        data = super().to_dict()
        data['seitenzahl'] = self.seitenzahl
        return data


# Hilfsfunktion für Beispieldaten
def create_sample_data():
    # Student erstellen
    student = Student("IU14103178", "Marvin", "Fox", "marvin.fox@iu-study.org")
    
    # Studiengang erstellen
    studiengang = Studiengang("Angewandte Künstliche Intelligenz", "Bachelor of Science", 6, 180)
    
    # Semester erstellen
    semester1 = Semester(1, "Wintersemester 2024", 
                        date(2024, 10, 1), date(2025, 2, 28), 30)
    semester2 = Semester(2, "Sommersemester 2025", 
                        date(2025, 4, 1), date(2025, 7, 31), 30)
    
    # Module für Semester 1
    modul1 = Modul("DLBDSOOFPP01", "Objektorientierte Programmierung", 5, 
                   "Einführung in OOP", "Prof. Dr. Schmidt")
    modul2 = Modul("DLBDSMATHF01", "Mathematik Grundlagen", 5, 
                   "Grundlagen der Mathematik", "Prof. Dr. Müller")
    modul3 = Modul("DLBDSEDE01", "Wissenschaftliches Arbeiten", 5, 
                   "Methoden des wissenschaftlichen Arbeitens", "Prof. Dr. Weber")
    
    # Noten setzen
    modul1.set_note(1.7, date(2024, 12, 15), "Portfolio")
    modul2.set_note(2.0, date(2024, 11, 30), "Klausur")
    modul3.set_note(2.3, date(2025, 1, 20), "Portfolio")
    
    # Module zu Semester hinzufügen
    semester1.add_modul(modul1)
    semester1.add_modul(modul2)
    semester1.add_modul(modul3)
    
    # Module für Semester 2 (ohne Noten)
    modul4 = Modul("DLBDSPROG01", "Programmierung", 5, 
                   "Grundlagen der Programmierung", "Prof. Dr. Klein")
    modul5 = Modul("DLBDSALGO01", "Algorithmen", 5, 
                   "Einführung in Algorithmen", "Prof. Dr. Groß")
    
    semester2.add_modul(modul4)
    semester2.add_modul(modul5)
    
    # Semester zu Studiengang hinzufügen
    studiengang.add_semester(semester1)
    studiengang.add_semester(semester2)
    
    return student, studiengang
