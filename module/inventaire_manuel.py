from module.inventaire import Inventaire


def saisir_machine():
    print("\n=== Ajout manuel d'une machine ===\n")

    machine = {
        "id": input("ID : ").strip(),
        "nom": input("Nom : ").strip(),
        "type": input("Type : ").strip(),
        "marque": input("Marque : ").strip(),
        "modele": input("Modèle : ").strip(),
        "numero_de_serie": input("Numéro de série : ").strip(),
        "localisation": input("Localisation : ").strip(),
        "etat": input("État : ").strip()
    }

    return machine


def main():
    inventaire = Inventaire("inventaire.json")

    machine = saisir_machine()

    inventaire.ajouter_machine(machine)

    print("\n✅ Machine ajoutée avec succès !")


if __name__ == "__main__":
    main()