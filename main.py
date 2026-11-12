from module.analyse_reseaux import AnalyseReseau
from module.inventaire import Inventaire
from module.stock import Stock
from src.display import ApplicationGUI


class Application:

    def __init__(self):
        self.fichier_inventaire = "inventaire.json"

        self.inventaire = Inventaire(
            self.fichier_inventaire
        )

        self.stock = Stock(
            self.fichier_inventaire
        )

        self.gui = ApplicationGUI(self)

    # ==================================================
    # ANALYSE RESEAU
    # ==================================================

    def scanner_reseau(self):

        scanner = AnalyseReseau(
            "192.168.1.0/24"
        )

        resultats = scanner.analyser_machines()

        ajout = 0

        for machine in resultats:

            existe = False

            for item in self.inventaire.machines:
                if item.get("ip") == machine["ip"]:
                    existe = True
                    break

            if not existe:

                nouvelle_machine = {
                    "id": len(
                        self.inventaire.machines
                    ) + 1,

                    "nom": (
                        machine.get("name")
                        or machine["ip"]
                    ),

                    "type": (
                        machine.get("type")
                        or "Inconnu"
                    ),

                    "marque": "Non détectée",
                    "modele": "Non détecté",

                    "numero_de_serie":
                        machine["mac"],

                    "ip":
                        machine["ip"],

                    "mac":
                        machine["mac"],

                    "localisation":
                        "Réseau local",

                    "etat":
                        "Actif",

                    "observations":
                        "Détecté automatiquement"
                }

                self.inventaire.ajouter_machine(
                    nouvelle_machine
                )

                ajout += 1

        self.gui.ajouter_log(
            f"{ajout} nouvelles machines détectées."
        )

    # ==================================================
    # AJOUT MANUEL
    # ==================================================

    def ajouter_machine(self, machine):

        machine["id"] = (
            len(self.inventaire.machines) + 1
        )

        if "observations" not in machine:
            machine["observations"] = "Ajout manuel"

        self.inventaire.ajouter_machine(machine)

        self.gui.ajouter_log(
            f"Machine '{machine['nom']}' ajoutée."
        )

    # ==================================================
    # AFFICHAGE INVENTAIRE
    # ==================================================

    def afficher_inventaire(self):

        texte = ""

        for machine in self.inventaire.machines:

            texte += (
                f"[{machine['id']}]\n"
                f"Nom : {machine['nom']}\n"
                f"Type : {machine['type']}\n"
                f"Marque : {machine['marque']}\n"
                f"Modèle : {machine['modele']}\n"
                f"État : {machine['etat']}\n"
                f"IP : {machine.get('ip', '-')}\n"
                f"MAC : {machine.get('mac', '-')}\n\n"
            )

        self.gui.ajouter_log(texte)

    # ==================================================
    # ANALYSE MACHINE
    # ==================================================

    def analyser_machine(self, identifiant):

        for machine in self.stock.inventaire.machines:

            if machine["id"] == identifiant:

                rapport = f"""
Analyse machine

Nom : {machine['nom']}
Type : {machine['type']}
Etat : {machine['etat']}
MAC : {machine.get('mac', 'N/A')}
IP : {machine.get('ip', 'N/A')}
"""

                self.gui.ajouter_log(
                    rapport
                )

                return

        self.gui.ajouter_log(
            "Machine introuvable."
        )

    # ==================================================
    # EXECUTION
    # ==================================================

    def run(self):
        self.gui.run()


if __name__ == "__main__":

    app = Application()
    app.run()