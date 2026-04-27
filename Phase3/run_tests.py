"""
Kleine Tests für das Studien-Dashboard.
"""

import os
import sys
import tempfile
import unittest
from datetime import date


sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from business_logic import StudienManager, berechne_notendurchschnitt
from data_access import JSONRepository
from entities import Modul, Student, Studiengang, Semester


class TestEntities(unittest.TestCase):

    def test_modul_note_setzen(self):
        modul = Modul("TEST01", "Testmodul", 5)
        modul.set_note(2.0, date(2025, 1, 20), "Klausur")

        self.assertEqual(modul.note, 2.0)
        self.assertTrue(modul.ist_bestanden())
        self.assertEqual(modul.pruefungsleistung.get_typ(), "Klausur")

    def test_json_felder_laden(self):
        modul = Modul("TEST02", "Portfolio Test", 5)
        modul.from_dict({
            "modulcode": "TEST02",
            "name": "Portfolio Test",
            "ects_punkte": 5,
            "pruefungsleistung": {
                "typ": "Portfolio",
                "note": 1.7,
                "datum": "2025-01-20",
                "bestanden": True,
                "versuch": 1,
                "seitenzahl": 12
            }
        })

        self.assertEqual(modul.note, 1.7)
        self.assertEqual(modul.pruefungsleistung.seitenzahl, 12)


class TestBusinessLogic(unittest.TestCase):

    def test_durchschnitt_funktion(self):
        self.assertEqual(berechne_notendurchschnitt([1.0, 2.0, 3.0]), 2.0)
        self.assertEqual(berechne_notendurchschnitt([]), 0.0)

    def test_manager_durchschnitt(self):
        student = Student("1", "Max", "Muster", "max@example.com")
        studiengang = Studiengang("Test Studiengang", "B.Sc.", 6, 180)
        semester = Semester(1, "Testsemester", date(2025, 4, 1), date(2025, 9, 30), 30)

        modul1 = Modul("A", "Modul A", 5)
        modul2 = Modul("B", "Modul B", 5)
        modul1.set_note(1.0, date(2025, 1, 20), "Klausur")
        modul2.set_note(3.0, date(2025, 1, 20), "Portfolio")

        semester.add_modul(modul1)
        semester.add_modul(modul2)
        studiengang.add_semester(semester)

        manager = StudienManager()
        manager.set_student(student)
        manager.set_studiengang(studiengang)

        self.assertEqual(manager.berechne_durchschnitt(), 2.0)


class TestSpeichernLaden(unittest.TestCase):

    def test_speichern_und_laden(self):
        with tempfile.TemporaryDirectory() as tmp:
            student = Student("IU123", "Lisa", "Test", "lisa@example.com")
            studiengang = Studiengang("Python", "B.Sc.", 6, 180)
            semester = Semester(1, "Semester 1", date(2025, 4, 1), date(2025, 9, 30), 30)
            modul = Modul("PY01", "Python Grundlagen", 5)
            modul.set_note(1.3, date(2025, 1, 20), "Portfolio")
            semester.add_modul(modul)
            studiengang.add_semester(semester)

            dateipfad = os.path.join(tmp, "test_dashboard.json")
            repo = JSONRepository(dateipfad)
            self.assertTrue(repo.save_data(student, studiengang))
            self.assertTrue(repo.file_exists())

            daten = repo.load_data()
            self.assertEqual(daten["student"].vorname, "Lisa")
            self.assertEqual(daten["studiengang"].semester[0].module[0].note, 1.3)


if __name__ == "__main__":
    unittest.main()
