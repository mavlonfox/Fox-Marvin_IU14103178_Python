"""
Hauptprogramm für das Studien-Dashboard
"""

from gui_components import DashboardGUI


def main():
    """Hauptfunktion - startet das Dashboard"""
    try:
        app = DashboardGUI()
        app.run()
    except Exception as e:
        print(f"Fehler beim Starten der Anwendung: {e}")


if __name__ == "__main__":
    main()
