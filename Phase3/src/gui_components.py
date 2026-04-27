"""
GUI für das Studien-Dashboard
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, date

from entities import Student, Studiengang, Semester, Modul, create_sample_data
from business_logic import StudienManager, note_zu_text


class DashboardGUI:
    """Hauptfenster des Studien-Dashboards"""
    
    def __init__(self):
        self.manager = StudienManager()
        self.root = tk.Tk()
        self.root.title("Studien-Dashboard - Marvin Fox")
        self.root.geometry("800x600")
        
        # GUI erstellen
        self.create_widgets()
        if self.manager.laden():
            # vorhandene Datei zuerst laden
            self.fill_student_entries()
        else:
            self.load_sample_data()
        self.update_display()
    
    def create_widgets(self):
        """Erstellt alle GUI-Komponenten"""
        # Notebook für Tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Tab 1: Dashboard
        self.dashboard_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.dashboard_frame, text="Dashboard")
        self.create_dashboard_tab()
        
        # Tab 2: Module
        self.module_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.module_frame, text="Module")
        self.create_module_tab()
        
        # Tab 3: Einstellungen
        self.settings_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.settings_frame, text="Einstellungen")
        self.create_settings_tab()
    
    def create_dashboard_tab(self):
        """Erstellt das Dashboard"""
        # Info-Bereich
        info_frame = ttk.LabelFrame(self.dashboard_frame, text="Studien-Info", padding=10)
        info_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.info_labels = {}
        
        # Student Info
        ttk.Label(info_frame, text="Student:").grid(row=0, column=0, sticky=tk.W)
        self.info_labels['student'] = ttk.Label(info_frame, text="-")
        self.info_labels['student'].grid(row=0, column=1, sticky=tk.W, padx=(10,0))
        
        # Studiengang Info
        ttk.Label(info_frame, text="Studiengang:").grid(row=1, column=0, sticky=tk.W)
        self.info_labels['studiengang'] = ttk.Label(info_frame, text="-")
        self.info_labels['studiengang'].grid(row=1, column=1, sticky=tk.W, padx=(10,0))
        
        # Notendurchschnitt
        ttk.Label(info_frame, text="Durchschnitt:").grid(row=2, column=0, sticky=tk.W)
        self.info_labels['durchschnitt'] = ttk.Label(info_frame, text="-")
        self.info_labels['durchschnitt'].grid(row=2, column=1, sticky=tk.W, padx=(10,0))
        
        # ECTS Info
        ttk.Label(info_frame, text="ECTS:").grid(row=3, column=0, sticky=tk.W)
        self.info_labels['ects'] = ttk.Label(info_frame, text="-")
        self.info_labels['ects'].grid(row=3, column=1, sticky=tk.W, padx=(10,0))
        
        # Fortschritt
        ttk.Label(info_frame, text="Fortschritt:").grid(row=4, column=0, sticky=tk.W)
        self.info_labels['fortschritt'] = ttk.Label(info_frame, text="-")
        self.info_labels['fortschritt'].grid(row=4, column=1, sticky=tk.W, padx=(10,0))
        
        # Buttons
        button_frame = ttk.Frame(self.dashboard_frame)
        button_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Button(button_frame, text="Aktualisieren", 
                  command=self.update_display).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Speichern", 
                  command=self.save_data).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Laden", 
                  command=self.load_data).pack(side=tk.LEFT, padx=5)
    
    def create_module_tab(self):
        """Erstellt die Modul-Übersicht"""
        # Treeview für Module
        columns = ('Semester', 'Code', 'Name', 'ECTS', 'Note', 'Typ', 'Status')
        self.module_tree = ttk.Treeview(self.module_frame, columns=columns, show='headings')
        
        for col in columns:
            self.module_tree.heading(col, text=col)
            self.module_tree.column(col, width=100)
        
        self.module_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Button-Frame
        button_frame = ttk.Frame(self.module_frame)
        button_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Button(button_frame, text="Note hinzufügen", 
                  command=self.add_note_dialog).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Aktualisieren", 
                  command=self.update_module_tree).pack(side=tk.LEFT, padx=5)
    
    def create_settings_tab(self):
        """Erstellt die Einstellungen"""
        settings_frame = ttk.LabelFrame(self.settings_frame, text="Student-Daten", padding=10)
        settings_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Entry-Felder für Student-Daten
        ttk.Label(settings_frame, text="Matrikelnummer:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.entry_matrikel = ttk.Entry(settings_frame)
        self.entry_matrikel.grid(row=0, column=1, sticky=tk.EW, padx=(10,0), pady=2)
        
        ttk.Label(settings_frame, text="Vorname:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.entry_vorname = ttk.Entry(settings_frame)
        self.entry_vorname.grid(row=1, column=1, sticky=tk.EW, padx=(10,0), pady=2)
        
        ttk.Label(settings_frame, text="Nachname:").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.entry_nachname = ttk.Entry(settings_frame)
        self.entry_nachname.grid(row=2, column=1, sticky=tk.EW, padx=(10,0), pady=2)
        
        ttk.Label(settings_frame, text="E-Mail:").grid(row=3, column=0, sticky=tk.W, pady=2)
        self.entry_email = ttk.Entry(settings_frame)
        self.entry_email.grid(row=3, column=1, sticky=tk.EW, padx=(10,0), pady=2)
        
        settings_frame.columnconfigure(1, weight=1)
        
        # Speichern Button
        ttk.Button(settings_frame, text="Speichern", 
                  command=self.save_student_data).grid(row=4, column=1, sticky=tk.E, pady=10)
    
    def load_sample_data(self):
        """Lädt Beispieldaten"""
        student, studiengang = create_sample_data()
        self.manager.set_student(student)
        self.manager.set_studiengang(studiengang)
        
        # Felder mit Daten füllen
        self.fill_student_entries()

    def fill_student_entries(self):
        """Schreibt Student-Daten in die Eingabefelder"""
        student = self.manager.student
        if not student:
            return

        self.entry_matrikel.delete(0, tk.END)
        self.entry_matrikel.insert(0, student.matrikelnummer)
        self.entry_vorname.delete(0, tk.END)
        self.entry_vorname.insert(0, student.vorname)
        self.entry_nachname.delete(0, tk.END)
        self.entry_nachname.insert(0, student.nachname)
        self.entry_email.delete(0, tk.END)
        self.entry_email.insert(0, student.email)
    
    def update_display(self):
        """Aktualisiert die Anzeige"""
        if self.manager.student:
            self.info_labels['student'].config(
                text=self.manager.student.get_vollname())
        
        if self.manager.studiengang:
            self.info_labels['studiengang'].config(
                text=f"{self.manager.studiengang.name} ({self.manager.studiengang.abschluss})")
        
        # Statistiken berechnen
        stats = self.manager.get_statistiken()
        
        durchschnitt = stats.get('durchschnitt', 0.0)
        self.info_labels['durchschnitt'].config(
            text=f"{durchschnitt:.2f} ({note_zu_text(durchschnitt)})")
        
        ects_erreicht = stats.get('ects_erreicht', 0)
        ects_gesamt = stats.get('ects_gesamt', 180)
        self.info_labels['ects'].config(
            text=f"{ects_erreicht} / {ects_gesamt}")
        
        fortschritt = stats.get('fortschritt', 0.0)
        self.info_labels['fortschritt'].config(
            text=f"{fortschritt:.1f}%")
        
        # Modul-Tree aktualisieren
        self.update_module_tree()
    
    def update_module_tree(self):
        """Aktualisiert die Modul-Tabelle"""
        # Alte Einträge löschen
        for item in self.module_tree.get_children():
            self.module_tree.delete(item)
        
        if not self.manager.studiengang:
            return
        
        # Module einfügen
        for semester in self.manager.studiengang.semester:
            for modul in semester.module:
                # Note/Typ stehen meistens in der Prüfungsleistung
                pl = modul.pruefungsleistung
                note_val = pl.note if (pl and pl.note is not None) else modul.note
                note_text = f"{note_val:.1f}" if note_val is not None else "-"
                typ_text = (pl.get_typ() if pl else (modul.typ or '-'))
                status = "Bestanden" if modul.ist_bestanden() else "Offen"
                
                self.module_tree.insert('', tk.END, values=(
                    f"Sem {semester.nummer}",
                    modul.modulcode,
                    modul.name,
                    modul.ects_punkte,
                    note_text,
                    typ_text,
                    status
                ))
    
    def add_note_dialog(self):
        """Dialog zum Hinzufügen einer Note"""
        if not self.manager.studiengang:
            messagebox.showwarning("Warnung", "Kein Studiengang geladen!")
            return
        
        # Neues Fenster
        dialog = tk.Toplevel(self.root)
        dialog.title("Note hinzufügen")
        dialog.geometry("400x300")
        dialog.transient(self.root)
        
        # Semester auswählen
        ttk.Label(dialog, text="Semester:").grid(row=0, column=0, sticky=tk.W, padx=10, pady=5)
        semester_var = tk.StringVar()
        semester_combo = ttk.Combobox(dialog, textvariable=semester_var, state="readonly")
        semester_values = [f"Semester {sem.nummer}" for sem in self.manager.studiengang.semester]
        semester_combo['values'] = semester_values
        semester_combo.grid(row=0, column=1, sticky=tk.EW, padx=10, pady=5)
        
        # Modul auswählen
        ttk.Label(dialog, text="Modul:").grid(row=1, column=0, sticky=tk.W, padx=10, pady=5)
        modul_var = tk.StringVar()
        modul_combo = ttk.Combobox(dialog, textvariable=modul_var, state="readonly")
        modul_combo.grid(row=1, column=1, sticky=tk.EW, padx=10, pady=5)
        
        # Note
        ttk.Label(dialog, text="Note (1.0-5.0):").grid(row=2, column=0, sticky=tk.W, padx=10, pady=5)
        note_var = tk.StringVar()
        note_entry = ttk.Entry(dialog, textvariable=note_var)
        note_entry.grid(row=2, column=1, sticky=tk.EW, padx=10, pady=5)
        
        # Typ
        ttk.Label(dialog, text="Typ:").grid(row=3, column=0, sticky=tk.W, padx=10, pady=5)
        typ_var = tk.StringVar(value="Klausur")
        typ_combo = ttk.Combobox(dialog, textvariable=typ_var, state="readonly")
        typ_combo['values'] = ['Klausur', 'Portfolio']
        typ_combo.grid(row=3, column=1, sticky=tk.EW, padx=10, pady=5)
        
        dialog.columnconfigure(1, weight=1)
        
        def update_module_list(*args):
            """Aktualisiert Module basierend auf Semester"""
            selected = semester_var.get()
            if selected:
                sem_nr = int(selected.split()[1])
                semester = self.manager.studiengang.get_semester_by_nummer(sem_nr)
                if semester:
                    module_names = [f"{m.modulcode} - {m.name}" for m in semester.module]
                    modul_combo['values'] = module_names
        
        semester_var.trace('w', update_module_list)
        
        def save_note():
            """Speichert die eingegebene Note"""
            try:
                note = float(note_var.get())
                if not (1.0 <= note <= 5.0):
                    messagebox.showerror("Fehler", "Note muss zwischen 1.0 und 5.0 liegen!")
                    return
                
                selected_semester = semester_var.get()
                selected_modul = modul_var.get()
                
                if not selected_semester or not selected_modul:
                    messagebox.showerror("Fehler", "Bitte alle Felder ausfüllen!")
                    return
                
                sem_nr = int(selected_semester.split()[1])
                modulcode = selected_modul.split(' - ')[0]
                typ = typ_var.get()
                
                success = self.manager.add_modul_note(sem_nr, modulcode, note, date.today(), typ)
                
                if success:
                    messagebox.showinfo("Erfolg", "Note wurde hinzugefügt!")
                    dialog.destroy()
                    self.update_display()
                else:
                    messagebox.showerror("Fehler", "Fehler beim Hinzufügen der Note!")
                
            except ValueError:
                messagebox.showerror("Fehler", "Ungültige Note eingegeben!")
        
        # Buttons
        button_frame = ttk.Frame(dialog)
        button_frame.grid(row=4, column=0, columnspan=2, pady=20)
        
        ttk.Button(button_frame, text="Speichern", command=save_note).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Abbrechen", command=dialog.destroy).pack(side=tk.LEFT, padx=5)
    
    def save_student_data(self):
        """Speichert die Student-Einstellungen"""
        try:
            student = Student(
                self.entry_matrikel.get(),
                self.entry_vorname.get(),
                self.entry_nachname.get(),
                self.entry_email.get()
            )
            self.manager.set_student(student)
            self.update_display()
            messagebox.showinfo("Erfolg", "Studentendaten gespeichert!")
        except Exception as e:
            messagebox.showerror("Fehler", f"Fehler beim Speichern: {e}")
    
    def save_data(self):
        """Speichert alle Daten"""
        if self.manager.speichern():
            messagebox.showinfo("Erfolg", "Daten gespeichert!")
        else:
            messagebox.showerror("Fehler", "Fehler beim Speichern!")
    
    def load_data(self):
        """Lädt Daten"""
        if self.manager.laden():
            # geladene Daten in die Felder schreiben
            self.fill_student_entries()
            self.update_display()
            messagebox.showinfo("Erfolg", "Daten geladen!")
        else:
            messagebox.showwarning("Warnung", "Keine gespeicherten Daten gefunden!")
    
    def run(self):
        """Startet die GUI"""
        self.root.mainloop()


if __name__ == "__main__":
    app = DashboardGUI()
    app.run()
