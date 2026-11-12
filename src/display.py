import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

# ---------- THÈME (modifie ici) ----------
C = {
    "fond":      "#1a1024",
    "panneau":   "#251636",
    "bordure":   "#3a2455",
    "entete":    "#6614b8",
    "bouton":    "#32204a",
    "bouton_hv": "#4a2f6b",
    "accent":    "#8b5cf6",
    "accent_hv": "#a37cf8",
    "texte":     "#f3eefb",
    "discret":   "#a99bc2",
    "titre":     "#FFD700",
    "log_bg":    "#120a1a",
    "ok":        "#4ade80",
    "info":      "#7dd3fc",
    "warn":      "#fbbf24",
    "err":       "#f87171",
}
F_TITRE = ("Arial", 20, "bold")
F_SECTION = ("Arial", 11, "bold")
F_BTN = ("Arial", 11, "bold")
F_CARTE = ("Arial", 24, "bold")
F_PETIT = ("Arial", 9)
F_LOG = ("Courier", 11)

# (clé dans la machine, titre de colonne, largeur)
COLONNES = [
    ("nom", "Nom", 140),
    ("type", "Type", 110),
    ("marque", "Marque", 110),
    ("modele", "Modèle", 140),
    ("numero_de_serie", "N° de série", 150),
    ("localisation", "Localisation", 130),
    ("etat", "État", 100),
]


def _val(machine, cle):
    """Lit un champ, que la machine soit un dict ou un objet."""
    if isinstance(machine, dict):
        return machine.get(cle, "")
    return getattr(machine, cle, "")


class ApplicationGUI:

    def __init__(self, controller):
        self.controller = controller

        self.root = tk.Tk()
        self.root.title("Ferrier Inventory Suite")
        self.root.geometry("1400x900")
        self.root.minsize(1200, 700)
        self.root.configure(bg=C["fond"])

        self._style()
        self._build()
        self._horloge()
        self.rafraichir()

    # ==========================================
    # STYLE
    # ==========================================

    def _style(self):
        s = ttk.Style(self.root)
        s.theme_use("clam")
        s.configure("Treeview", background=C["panneau"],
                    fieldbackground=C["panneau"], foreground=C["texte"],
                    rowheight=30, borderwidth=0, font=("Arial", 10))
        s.configure("Treeview.Heading", background=C["bouton"],
                    foreground=C["discret"], relief="flat",
                    font=("Arial", 10, "bold"))
        s.map("Treeview", background=[("selected", C["accent"])])
        s.map("Treeview.Heading", background=[("active", C["bouton_hv"])])

    def _bouton(self, parent, texte, commande, principal=False):
        """Un seul endroit pour styliser TOUS les boutons."""
        bg = C["accent"] if principal else C["bouton"]
        hv = C["accent_hv"] if principal else C["bouton_hv"]
        b = tk.Button(parent, text=texte, command=commande, anchor="w",
                      font=F_BTN, fg=C["texte"], bg=bg,
                      activebackground=hv, activeforeground=C["texte"],
                      relief="flat", bd=0, padx=12, pady=10, cursor="hand2")
        b.pack(fill="x", padx=15, pady=5)
        b.bind("<Enter>", lambda e: b.config(bg=hv))
        b.bind("<Leave>", lambda e: b.config(bg=bg))
        return b

    def _section(self, parent, texte):
        tk.Label(parent, text=texte, font=("Arial", 9, "bold"),
                 fg=C["discret"], bg=C["panneau"], anchor="w"
                 ).pack(fill="x", padx=15, pady=(18, 4))

    def _panneau(self, parent, titre):
        p = tk.Frame(parent, bg=C["panneau"],
                     highlightbackground=C["bordure"], highlightthickness=1)
        tk.Label(p, text=titre, font=F_SECTION, fg=C["titre"],
                 bg=C["panneau"], anchor="w"
                 ).pack(fill="x", padx=14, pady=(12, 8))
        return p

    def _carte(self, parent, col, titre):
        f = tk.Frame(parent, bg=C["panneau"],
                     highlightbackground=C["bordure"], highlightthickness=1)
        f.grid(row=0, column=col, sticky="ew", padx=(0 if col == 0 else 15, 0))
        tk.Label(f, text=titre, font=("Arial", 9, "bold"), fg=C["discret"],
                 bg=C["panneau"], anchor="w").pack(fill="x", padx=14, pady=(12, 0))
        valeur = tk.Label(f, text="0", font=F_CARTE, fg=C["texte"],
                          bg=C["panneau"], anchor="w")
        valeur.pack(fill="x", padx=14, pady=(0, 12))
        return valeur

    # ==========================================
    # CONSTRUCTION
    # ==========================================

    def _build(self):
        # --- en-tête ---
        header = tk.Frame(self.root, bg=C["entete"])
        header.pack(fill="x")
        tk.Label(header, text="FERRIER INVENTORY SUITE", font=F_TITRE,
                 fg="white", bg=C["entete"], pady=18
                 ).pack(side="left", padx=25)
        self.horloge = tk.Label(header, font=("Arial", 11), fg="#e6d6ff",
                                bg=C["entete"])
        self.horloge.pack(side="right", padx=25)

        # --- barre d'état (en bas) ---
        barre = tk.Frame(self.root, bg=C["log_bg"])
        barre.pack(fill="x", side="bottom")
        self.etat = tk.Label(barre, text="Prêt", font=F_PETIT,
                             fg=C["discret"], bg=C["log_bg"],
                             anchor="w", padx=15, pady=6)
        self.etat.pack(side="left")

        # --- corps ---
        main = tk.Frame(self.root, bg=C["fond"])
        main.pack(fill="both", expand=True, padx=20, pady=20)

        # colonne gauche : outils
        left = tk.Frame(main, bg=C["panneau"], width=280,
                        highlightbackground=C["bordure"], highlightthickness=1)
        left.pack(side="left", fill="y")
        left.pack_propagate(False)

        self._section(left, "ACTIONS")
        self._bouton(left, "Scanner le réseau",
                     self.controller.scanner_reseau, principal=True)
        self._bouton(left, "Ajouter une machine", self.fenetre_ajout_machine)
        self._bouton(left, "Analyser machine #1",
                     lambda: self.controller.analyser_machine(1))
        self._section(left, "DONNÉES")
        self._bouton(left, "Afficher l'inventaire",
                     self.controller.afficher_inventaire)
        self._bouton(left, "Vider le journal", self.vider_journal)

        # colonne droite
        right = tk.Frame(main, bg=C["fond"])
        right.pack(side="left", fill="both", expand=True, padx=(20, 0))

        # compteurs
        cartes = tk.Frame(right, bg=C["fond"])
        cartes.pack(fill="x", pady=(0, 15))
        for i in range(3):
            cartes.columnconfigure(i, weight=1, uniform="cartes")
        self.k_total = self._carte(cartes, 0, "MACHINES")
        self.k_types = self._carte(cartes, 1, "TYPES")
        self.k_lieux = self._carte(cartes, 2, "LOCALISATIONS")

        # inventaire
        p_inv = self._panneau(right, "INVENTAIRE")
        p_inv.pack(fill="both", expand=True, pady=(0, 15))
        self.tableau = ttk.Treeview(
            p_inv, columns=[c[0] for c in COLONNES],
            show="headings", selectmode="browse")
        for cle, titre, largeur in COLONNES:
            self.tableau.heading(cle, text=titre, anchor="w")
            self.tableau.column(cle, width=largeur, anchor="w")
        self.tableau.pack(fill="both", expand=True, padx=14, pady=(0, 14))

        # journal
        p_log = self._panneau(right, "JOURNAL D'ACTIVITÉ")
        p_log.pack(fill="x")
        self.log_text = tk.Text(p_log, height=10, bg=C["log_bg"],
                                fg=C["texte"], insertbackground="white",
                                font=F_LOG, relief="flat", state="disabled",
                                padx=10, pady=8)
        self.log_text.pack(fill="x", padx=14, pady=(0, 14))
        self.log_text.tag_config("heure", foreground="#7c6d95")
        for niveau in ("ok", "info", "warn", "err"):
            self.log_text.tag_config(niveau, foreground=C[niveau])

    def _horloge(self):
        self.horloge.config(text=datetime.now().strftime("%H:%M:%S"))
        self.root.after(1000, self._horloge)

    # ==========================================
    # INVENTAIRE (tableau + compteurs)
    # ==========================================

    def rafraichir(self):
        """Relit controller.inventaire.machines et met tout à jour."""
        try:
            machines = self.controller.inventaire.machines
        except AttributeError:
            return  # le controller n'est pas encore prêt
        if isinstance(machines, dict):
            machines = list(machines.values())
        machines = list(machines)

        self.tableau.delete(*self.tableau.get_children())
        for m in machines:
            self.tableau.insert(
                "", "end", values=[_val(m, c[0]) for c in COLONNES])

        types = {_val(m, "type") for m in machines if _val(m, "type")}
        lieux = {_val(m, "localisation") for m in machines
                 if _val(m, "localisation")}
        self.k_total.config(text=str(len(machines)))
        self.k_types.config(text=str(len(types)))
        self.k_lieux.config(text=str(len(lieux)))

    # ==========================================
    # FENETRE AJOUT MACHINE
    # ==========================================

    def fenetre_ajout_machine(self):
        fenetre = tk.Toplevel(self.root)
        fenetre.title("Ajouter une machine")
        fenetre.geometry("460x470")
        fenetre.configure(bg=C["panneau"])
        fenetre.transient(self.root)
        fenetre.grab_set()

        tk.Label(fenetre, text="NOUVELLE MACHINE", font=F_SECTION,
                 fg=C["titre"], bg=C["panneau"]
                 ).grid(row=0, column=0, columnspan=2, pady=(18, 10))

        labels = [
            ("Nom", "nom"),
            ("Type", "type"),
            ("Marque", "marque"),
            ("Modele", "modele"),
            ("Numero de serie", "numero_de_serie"),
            ("Localisation", "localisation"),
            ("Etat", "etat"),
        ]

        champs = {}
        for i, (texte, cle) in enumerate(labels, start=1):
            tk.Label(fenetre, text=texte, fg=C["texte"], bg=C["panneau"],
                     font=("Arial", 10)
                     ).grid(row=i, column=0, padx=(20, 10), pady=7, sticky="w")
            entry = tk.Entry(fenetre, width=30, bg=C["log_bg"], fg=C["texte"],
                             insertbackground="white", relief="flat",
                             highlightthickness=1,
                             highlightbackground=C["bordure"],
                             highlightcolor=C["accent"])
            entry.grid(row=i, column=1, padx=(0, 20), pady=7, ipady=4)
            champs[cle] = entry

        list(champs.values())[0].focus_set()

        def enregistrer(event=None):
            machine = {cle: w.get().strip() for cle, w in champs.items()}
            if not machine["nom"]:
                messagebox.showwarning(
                    "Champ manquant", "Le nom est obligatoire.",
                    parent=fenetre)
                return
            self.controller.ajouter_machine(machine)
            self.rafraichir()
            fenetre.destroy()

        b = tk.Button(fenetre, text="Enregistrer", command=enregistrer,
                      font=F_BTN, fg=C["texte"], bg=C["accent"],
                      activebackground=C["accent_hv"],
                      activeforeground=C["texte"], relief="flat", bd=0,
                      padx=25, pady=9, cursor="hand2")
        b.grid(row=len(labels) + 1, column=0, columnspan=2, pady=22)
        b.bind("<Enter>", lambda e: b.config(bg=C["accent_hv"]))
        b.bind("<Leave>", lambda e: b.config(bg=C["accent"]))

        fenetre.bind("<Return>", enregistrer)
        fenetre.bind("<Escape>", lambda e: fenetre.destroy())

    # ==========================================
    # LOG
    # ==========================================

    @staticmethod
    def _deviner_niveau(texte):
        t = texte.lower()
        if any(k in t for k in ("erreur", "échec", "echec", "impossible")):
            return "err"
        if any(k in t for k in ("attention", "aucune", "aucun", "introuvable")):
            return "warn"
        if any(k in t for k in ("ajout", "terminé", "termine", "succès", "succes")):
            return "ok"
        return "info"

    def ajouter_log(self, texte, niveau=None):
        """Même appel qu'avant : ajouter_log("texte").
        Option : ajouter_log("texte", "ok") avec ok / info / warn / err."""
        niveau = niveau or self._deviner_niveau(texte)
        heure = datetime.now().strftime("%H:%M:%S")

        self.log_text.config(state="normal")
        self.log_text.insert("end", heure + " ", "heure")
        self.log_text.insert("end", f"{texte}\n", niveau)
        self.log_text.see("end")
        self.log_text.config(state="disabled")

        self.etat.config(text=texte)
        self.rafraichir()

    def vider_journal(self):
        self.log_text.config(state="normal")
        self.log_text.delete("1.0", "end")
        self.log_text.config(state="disabled")
        self.etat.config(text="Journal vidé")

    def run(self):
        self.root.mainloop()