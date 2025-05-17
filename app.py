from shiny import App, ui, render, reactive
import pandas as pd
from datetime import datetime, timedelta
import os
import json

# Chemins des fichiers CSV
DATA_DIR = "data"
STOCK_FILE = os.path.join(DATA_DIR, "stock.csv")
VENTES_FILE = os.path.join(DATA_DIR, "ventes.csv")

# Création du répertoire de données s'il n'existe pas
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

def save_data(stock_df, ventes_df):
    """
    Sauvegarde les DataFrames de stock et de ventes dans des fichiers CSV.
    """
    # Sauvegarder le stock
    stock_df.to_csv(STOCK_FILE, index=False)
    
    # Sauvegarder les ventes
    ventes_df.to_csv(VENTES_FILE, index=False)

def load_data():
    # Structure par défaut des DataFrames
    stock_structure = {
        "Categorie": [],
        "Sous-categorie": [],
        "Produit": [],
        "Prix unitaire": [],
        "Quantite": [],
        "Date": [],
        "Quantite_initiale": []
    }
    
    ventes_structure = {
        "Categorie": [],
        "Sous-categorie": [],
        "Produit": [],
        "Prix unitaire": [],
        "Quantite vendue": [],
        "Date": [],
        "Total": []
    }
    
    # Charger les données du stock
    if os.path.exists(STOCK_FILE):
        stock_df = pd.read_csv(STOCK_FILE)
        stock_df = stock_df.fillna(0)
        if "Prix unitaire" in stock_df.columns:
            stock_df["Prix unitaire"] = stock_df["Prix unitaire"].astype(float)
        if "Quantite" in stock_df.columns:
            stock_df["Quantite"] = stock_df["Quantite"].astype(float)
        if "Quantite_initiale" in stock_df.columns:
            stock_df["Quantite_initiale"] = stock_df["Quantite_initiale"].astype(float)
    else:
        stock_df = pd.DataFrame(stock_structure)  # Créer un DataFrame vide avec la structure par défaut
    
    # Charger les données des ventes
    if os.path.exists(VENTES_FILE):
        ventes_df = pd.read_csv(VENTES_FILE)
        ventes_df = ventes_df.fillna(0)
        if "Date" in ventes_df.columns:
            # Utiliser format='mixed' pour gérer les dates au format "%d/%m/%Y" ou "%d-%m-%Y"
            ventes_df["Date"] = pd.to_datetime(ventes_df["Date"], format='mixed', dayfirst=True)
    else:
        ventes_df = pd.DataFrame(ventes_structure)  # Créer un DataFrame vide avec la structure par défaut
    
    # Retourner les deux DataFrames
    return stock_df, ventes_df

# Charger les données initiales
initial_stock, initial_ventes = load_data()

# Afficher les données chargées
print("Stock initial :")
print(initial_stock)

print("\nVentes initiales :")
print(initial_ventes)

# Interface utilisateur
app_ui = ui.page_fluid(
    ui.tags.head(
        ui.tags.style("""
            body {
                font-family: 'Arial', sans-serif;
                background-color: #f4f4f4;
                color: #333;
            }
            .navbar {
                background-color: #4CAF50;
                color: white;
                padding: 10px;
                border-radius: 5px;
                margin-bottom: 20px;
            }
            .navbar h1 {
                margin: 0;
                font-size: 24px;
            }
            .card {
                background-color: white;
                border-radius: 5px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                padding: 20px;
                margin-bottom: 20px;
            }
            .card h2 {
                margin-top: 0;
                font-size: 20px;
                color: #4CAF50;
            }
            .form-group {
                margin-bottom: 15px;
            }
            .form-group label {
                display: block;
                margin-bottom: 5px;
                font-weight: bold;
            }
            .form-group input, .form-group select {
                width: 100%;
                padding: 8px;
                border: 1px solid #ddd;
                border-radius: 4px;
            }
            .btn-primary {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 4px;
                cursor: pointer;
            }
            .btn-primary:hover {
                background-color: #45a049;
            }
            .btn-danger {
                background-color: #f44336;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 4px;
                cursor: pointer;
            }
            .btn-danger:hover {
                background-color: #d32f2f;
            }
            .btn-secondary {
                background-color: #9e9e9e;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 4px;
                cursor: pointer;
            }
            .btn-secondary:hover {
                background-color: #757575;
            }
            .m-1 {
                margin: 0.25rem;
            }
            .table {
                width: 100%;
                border-collapse: collapse;
                margin-bottom: 20px;
            }
            .table th, .table td {
                padding: 10px;
                border: 1px solid #ddd;
                text-align: left;
            }
            .table th {
                background-color: #4CAF50;
                color: white;
            }
            .table tr:nth-child(even) {
                background-color: #f9f9f9;
            }
            .table tr:hover {
                background-color: #f1f1f1;
            }
            .alert {
                padding: 10px;
                border-radius: 4px;
                margin-bottom: 20px;
            }
            .alert-success {
                background-color: #d4edda;
                color: #155724;
                border: 1px solid #c3e6cb;
            }
            .alert-error {
                background-color: #f8d7da;
                color: #721c24;
                border: 1px solid #f5c6cb;
            }

            /* Styles pour l'icône de suppression (🗑) */
            .delete-icon {
                color: #ff4444;
                font-size: 24px;
                cursor: pointer;
                transition: color 0.3s ease;
            }

            .delete-icon:hover {
                color: #cc0000;
            }

            /* Styles pour l'icône de modification (✏) */
            .edit-icon {
                color: #33b5e5;
                font-size: 24px;
                cursor: pointer;
                transition: color 0.3s ease;
            }

            .edit-icon:hover {
                color: #0099cc;
            }

            /* Boîte de dialogue de suppression */
            #modal-confirmation {
                display: none;
                position: fixed;
                top: 50%;
                left: 50%;
                transform: translate(-50%, -50%);
                background-color: white;
                padding: 20px;
                border-radius: 5px;
                box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
                z-index: 1000;
            }

            #overlay {
                display: none;
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background-color: rgba(0, 0, 0, 0.5);
                z-index: 999;
            }
        """)
    ),
    ui.tags.script("""
    $(document).ready(function() {
        var indexToDelete = null;

        $(document).on('click', '.delete-icon', function() {
            indexToDelete = $(this).data('index');
            $("#modal-confirmation").show();
            $("#overlay").show();
        });

        $("#annuler_suppression").on("click", function() {
            $("#modal-confirmation").hide();
            $("#overlay").hide();
            indexToDelete = null;
        });

        $("#confirmer_suppression").on("click", function() {
            if (indexToDelete !== null) {
                Shiny.setInputValue('delete', indexToDelete, {priority: 'event'});
                $("#modal-confirmation").hide();
                $("#overlay").hide();
                indexToDelete = null;
            }
        });
    });
    """),
    ui.div(
        {"class": "navbar"},
        ui.h1("Gestion de Stock et Ventes")
    ),
    ui.navset_tab(
        ui.nav_panel("Stock",
            ui.div(
                {"class": "card"},
                ui.h2("Gestion du Stock"),
                ui.row(
                    ui.column(4, 
                        ui.div(
                            {"class": "form-group"},
                            ui.input_selectize(
                                "categorie",
                                "Catégorie",
                                choices=[],
                                options={
                                    "create": True,
                                    "placeholder": "Commencez à taper une catégorie...",
                                    "searchField": ["label"],
                                    "sortField": "label",
                                    "openOnFocus": True,
                                    "dropdownParent": "body"
                                }
                            )
                        ),
                        ui.div(
                            {"class": "form-group"},
                            ui.input_selectize(
                                "sous_categorie",
                                "Sous-catégorie",
                                choices=[],
                                options={
                                    "create": True,
                                    "placeholder": "Commencez à taper une sous-catégorie...",
                                    "searchField": ["label"],
                                    "sortField": "label",
                                    "openOnFocus": True,
                                    "dropdownParent": "body"
                                }
                            )
                        ),
                        ui.div(
                            {"class": "form-group"},
                            ui.input_selectize(
                                "produit",
                                "Produit",
                                choices=[],
                                options={
                                    "create": True,
                                    "placeholder": "Commencez à taper un produit...",
                                    "searchField": ["label"],
                                    "sortField": "label",
                                    "openOnFocus": True,
                                    "dropdownParent": "body"
                                }
                            )
                        ),
                        ui.div(
                            {"class": "form-group"},
                            ui.input_numeric("prix_unitaire", "Prix unitaire", value=0, min=0, step=0.01)
                        ),
                        ui.div(
                            {"class": "form-group"},
                            ui.input_numeric("quantite", "Quantité", value=0, min=0, step=1)
                        ),
                        ui.input_action_button("ajouter", "Ajouter", class_="btn-primary"),
                        ui.output_text("message_confirmation")
                    ),
                    ui.column(8, 
                        ui.output_ui("tableau_stock")
                    )
                )
            )
        ),
        ui.nav_panel("Ventes",
            ui.div(
                {"class": "card"},
                ui.h2("Gestion des Ventes"),
                ui.row(
                    ui.column(4,
                        ui.div(
                            {"class": "form-group"},
                            ui.input_select("categorie_vente", "Catégorie", choices=["Tous"])
                        ),
                        ui.div(
                            {"class": "form-group"},
                            ui.input_select("sous_categorie_vente", "Sous-catégorie", choices=["Tous"])
                        ),
                        ui.div(
                            {"class": "form-group"},
                            ui.input_select("produit_vente", "Produit", choices=["Tous"])
                        ),
                        ui.div(
                            {"class": "form-group"},
                            ui.input_numeric("prix_unitaire_vente", "Prix unitaire", value=0, min=0, step=0.01)
                        ),
                        ui.div(
                            {"class": "form-group"},
                            ui.input_numeric("quantite_vendue", "Quantité", value=0, min=0, step=1)
                        ),
                        ui.input_action_button("vendre", "Vendre", class_="btn-primary"),
                        ui.output_text("message_vente_text")
                    ),
                    ui.column(8,
                        ui.output_ui("tableau_vente")
                    )
                )
            )
        ),
        ui.nav_panel("Tableau de Bord",
            ui.div(
                {"class": "card"},
                ui.h2("Tableau de Bord"),
                ui.row(
                    ui.column(2, ui.input_select("categorie_analyse", "Catégorie", choices=["Tous"])),
                    ui.column(2, ui.input_select("sous_categorie_analyse", "Sous-catégorie", choices=["Tous"])),
                    ui.column(2, ui.input_select("produit_analyse", "Produit", choices=["Tous"])),
                    ui.column(2, ui.input_date("date_debut", "Date de début", value=None)),
                    ui.column(2, ui.input_date("date_fin", "Date de fin", value=None)),
                    ui.column(2, ui.input_action_button("filtrer", "Filtrer", class_="btn-primary")),
                ),
                ui.row(
                    ui.column(12,
                        ui.div(
                            {"class": "btn-group mt-2"},
                            ui.input_action_button("aujourd_hui", "Aujourd'hui", class_="btn-secondary"),
                            ui.input_action_button("cette_semaine", "Cette semaine", class_="btn-secondary"),
                            ui.input_action_button("ce_mois", "Ce mois", class_="btn-secondary"),
                            ui.input_action_button("ce_trimestre", "Ce trimestre", class_="btn-secondary"),
                            ui.input_action_button("cette_annee", "Cette année", class_="btn-secondary"),
                            ui.input_action_button("tout", "Tout", class_="btn-secondary"),
                        )
                    )
                ),
                ui.row(
                    ui.column(12,
                        ui.div(
                            {"class": "alert alert-success"},
                            ui.h4("Alertes Stock Critique (≤ 20% restant)"),
                            ui.output_ui("alerte_stock_critique")
                        ),
                        ui.div(
                            {"class": "alert alert-error"},
                            ui.h4("Stock Faible (21-40% restant)"),
                            ui.output_ui("alerte_stock_faible")
                        )
                    )
                ),
                ui.row(
                    ui.column(12,
                        ui.h4("Statistiques de Vente"),
                        ui.output_ui("statistiques_vente")
                    )
                ),
                ui.row(
                    ui.column(12,
                        ui.h4("Tous les Produits avec Pourcentage de Stock Restant"),
                        ui.output_ui("tableau_stock_pourcentage")
                    )
                ),
                ui.row(
                    ui.column(12,
                        ui.input_action_button("afficher_tout", "Afficher toutes les données", class_="btn-primary")
                    )
                )
            )
        )
    ),
    # Boîte de dialogue de confirmation pour la suppression
    ui.div(
        ui.tags.div(
            ui.h4("Voulez-vous vraiment supprimer ce produit?"),
            ui.input_action_button("confirmer_suppression", "Oui, supprimer", class_="btn-danger m-1"),
            ui.input_action_button("annuler_suppression", "Annuler", class_="btn-secondary m-1"),
            id="modal-confirmation",
            class_="p-3 border rounded bg-light"
        ),
        ui.tags.div(
            id="overlay"
        )
    )
)
# Serveur
def server(input, output, session):
    # Variables réactives pour stocker les messages
    message_stock = reactive.Value("")
    message_vente = reactive.Value("")

    stock_data = reactive.Value(initial_stock.copy())
    vente_data = reactive.Value(initial_ventes.copy())

def server(input, output, session):
    # Variables réactives pour stocker les messages
    message_stock = reactive.Value("")
    message_vente = reactive.Value("")

    stock_data = reactive.Value(initial_stock.copy())
    vente_data = reactive.Value(initial_ventes.copy())

    # Réinitialiser les champs au démarrage
    @reactive.Effect
    def initialize_interface():
        ui.update_selectize("categorie", selected="")  # Réinitialiser la catégorie
        ui.update_selectize("sous_categorie", selected="")  # Réinitialiser la sous-catégorie
        ui.update_selectize("produit", selected="")  # Réinitialiser le produit
        ui.update_numeric("prix_unitaire", value=0)  # Réinitialiser le prix unitaire à 0
        ui.update_numeric("quantite", value=0)  # Réinitialiser la quantité à 0

    @reactive.Effect
    def update_categorie_choices():
        stock = stock_data()
        if not stock.empty:
            categories = stock["Categorie"].unique().tolist()
            ui.update_selectize("categorie", choices=categories, server=True)

    @reactive.Effect
    def update_sous_categorie_choices():
        stock = stock_data()
        if not stock.empty and input.categorie():
            sous_categories = stock[stock["Categorie"] == input.categorie()]["Sous-categorie"].unique().tolist()
            ui.update_selectize("sous_categorie", choices=sous_categories, server=True)

    @reactive.Effect
    def update_produit_choices():
        stock = stock_data()
        if not stock.empty and input.categorie() and input.sous_categorie():
            produits = stock[
                (stock["Categorie"] == input.categorie()) & 
                (stock["Sous-categorie"] == input.sous_categorie())
            ]["Produit"].unique().tolist()
            ui.update_selectize("produit", choices=produits, server=True)

    # Variable réactive pour suivre l'index du produit en cours de modification
    produit_en_modification = reactive.Value(None)

    # Fonction réactive pour obtenir les catégories
    @reactive.Calc
    def get_categories():
        return ["Tous"] + stock_data()["Categorie"].unique().tolist()
    
    @reactive.Effect
    def update_categorie_analyse():
        stock = stock_data()
        if not stock.empty:
            categories = ["Tous"] + stock["Categorie"].unique().tolist()
            ui.update_select("categorie_analyse", choices=categories)
        
    # Mise à jour des sous-catégories pour l'analyse
    @reactive.Effect
    @reactive.event(input.categorie_analyse)
    def update_sous_categorie_analyse():
        stock = stock_data()
        if not stock.empty and input.categorie_analyse():
            if input.categorie_analyse() == "Tous":
                sous_categories = ["Tous"] + stock["Sous-categorie"].unique().tolist()
            else:
                sous_categories = ["Tous"] + stock[stock["Categorie"] == input.categorie_analyse()]["Sous-categorie"].unique().tolist()
            ui.update_select("sous_categorie_analyse", choices=sous_categories)
    
    # Mise à jour des produits pour l'analyse
    @reactive.Effect
    @reactive.event(input.sous_categorie_analyse)
    def update_produit_analyse():
        stock = stock_data()
        if not stock.empty and input.categorie_analyse() and input.sous_categorie_analyse():
            if input.categorie_analyse() == "Tous" and input.sous_categorie_analyse() == "Tous":
                produits = ["Tous"] + stock["Produit"].unique().tolist()
            elif input.categorie_analyse() == "Tous":
                produits = ["Tous"] + stock[stock["Sous-categorie"] == input.sous_categorie_analyse()]["Produit"].unique().tolist()
            elif input.sous_categorie_analyse() == "Tous":
                produits = ["Tous"] + stock[stock["Categorie"] == input.categorie_analyse()]["Produit"].unique().tolist()
            else:
                produits = ["Tous"] + stock[
                    (stock["Categorie"] == input.categorie_analyse()) &
                    (stock["Sous-categorie"] == input.sous_categorie_analyse())
                ]["Produit"].unique().tolist()
            ui.update_select("produit_analyse", choices=produits)
            
    # Mise à jour des sous-catégories en fonction de la catégorie sélectionnée
    @reactive.Effect
    def update_sous_categories():
        stock = stock_data()
        if input.categorie_analyse():
            sous_categories = stock[stock["Categorie"] == input.categorie_analyse()]["Sous-categorie"].unique().tolist()
            ui.update_select("sous_categorie_analyse", choices=[""] + sous_categories)
        else:
            ui.update_select("sous_categorie_analyse", choices=[])

    # Mise à jour des produits en fonction de la catégorie et de la sous-catégorie sélectionnées
    @reactive.Effect
    def update_produits():
        stock = stock_data()
        if input.categorie_analyse() and input.sous_categorie_analyse():
            produits = stock[
                (stock["Categorie"] == input.categorie_analyse()) &
                (stock["Sous-categorie"] == input.sous_categorie_analyse())
            ]["Produit"].unique().tolist()
            ui.update_select("produit_analyse", choices=[""] + produits)
        else:
            ui.update_select("produit_analyse", choices=[])

    # Ajout de produit au stock
    @reactive.Effect
    @reactive.event(input.ajouter)  # Déclenché lorsque le bouton "ajouter" est cliqué
    def ajouter_produit():
        print("Bouton ajouter cliqué")
        stock = stock_data()
        
        # Remplacer NaN par 0 dans le DataFrame
        stock = stock.fillna(0)
        
        # Validation des champs obligatoires
        if not input.categorie() or not input.produit():
            message_stock.set("Veuillez remplir les champs Catégorie et Produit.")
            return
        
        # Vérifier si le prix et la quantité sont valides
        if input.prix_unitaire() < 0 or input.quantite() < 0:
            message_stock.set("Le prix et la quantité doivent être positifs.")
            return
        
        # Récupérer l'index du produit en cours de modification
        index_modification = produit_en_modification()
        
        if index_modification is not None:
            # Si un produit est en cours de modification, remplacer la quantité
            stock.loc[index_modification] = {
                "Categorie": input.categorie(),
                "Sous-categorie": input.sous_categorie(),
                "Produit": input.produit(),
                "Prix unitaire": input.prix_unitaire(),
                "Quantite": input.quantite(),  # Remplace la quantité existante
                "Date": datetime.now().strftime("%d-%m-%Y"),  # Format "dd-mm-yyyy"
                "Quantite_initiale": input.quantite()  # Mise à jour de la quantité initiale
            }
            message_stock.set(f"Produit {input.produit()} modifié avec succès.")
            # Réinitialiser l'indicateur de modification
            produit_en_modification.set(None)
        else:
            # Vérifier si un produit avec les mêmes valeurs existe déjà
            mask = (
                (stock["Categorie"] == input.categorie()) &
                (stock["Sous-categorie"] == input.sous_categorie()) &
                (stock["Produit"] == input.produit()) &
                (stock["Prix unitaire"] == input.prix_unitaire())
            )
            existing = stock[mask]
            
            if not existing.empty:
                # Si un produit correspondant existe, ajouter la quantité
                index = existing.index[0]
                stock.loc[index, "Quantite"] += input.quantite()
                message_stock.set(f"Quantité du produit {input.produit()} mise à jour. Nouvelle quantité : {stock.loc[index, 'Quantite']}")
            else:
                # Si aucun produit correspondant n'existe, ajouter un nouveau produit
                new_row = pd.DataFrame({
                    "Categorie": [input.categorie()],
                    "Sous-categorie": [input.sous_categorie()],
                    "Produit": [input.produit()],
                    "Prix unitaire": [input.prix_unitaire()],
                    "Quantite": [input.quantite()],
                    "Date": [datetime.now().strftime("%d-%m-%Y")],  # Format "dd-mm-yyyy"
                    "Quantite_initiale": [input.quantite()]
                })
                stock = pd.concat([stock, new_row], ignore_index=True)
                message_stock.set(f"Produit {input.produit()} ajouté au stock.")
        
        # Mettre à jour les données de stock
        stock_data.set(stock)

        # Sauvegarder les données
        save_data(stock, vente_data())
        
        # Réinitialiser tous les champs pour que l'interface reste vierge
        ui.update_selectize("categorie", selected="")  # Réinitialiser la catégorie
        ui.update_selectize("sous_categorie", selected="")  # Réinitialiser la sous-catégorie
        ui.update_selectize("produit", selected="")  # Réinitialiser le produit
        ui.update_numeric("prix_unitaire", value=0)  # Réinitialiser le prix unitaire à 0
        ui.update_numeric("quantite", value=0)  # Réinitialiser la quantité à 0
   
    # Enregistrement d'une vente
    @reactive.Effect
    @reactive.event(input.vendre)
    def enregistrer_vente():
        stock = stock_data()
        ventes = vente_data()
        
        # Vérifier que tous les champs sont remplis
        if not input.categorie_vente() or not input.produit_vente():
            message_vente.set("Veuillez sélectionner une catégorie et un produit.")
            return
        
        # Vérifier la quantité vendue
        if input.quantite_vendue() <= 0:
            message_vente.set("La quantité vendue doit être positive.")
            return
        
        # Trouver le produit dans le stock
        mask_stock = (
            (stock["Categorie"] == input.categorie_vente()) & 
            (stock["Produit"] == input.produit_vente())
        )
        produit_stock = stock[mask_stock]
        
        # Vérifier si le produit existe en stock et en quantité suffisante
        if len(produit_stock) == 0:
            message_vente.set("Produit non trouvé en stock.")
            return
        
        stock_index = produit_stock.index[0]
        quantite_disponible = stock.loc[stock_index, "Quantite"]
        prix_unitaire_stock = stock.loc[stock_index, "Prix unitaire"]
        
        # Utiliser le prix unitaire saisi ou le prix du stock si non spécifié
        prix_unitaire_vente = input.prix_unitaire_vente() if input.prix_unitaire_vente() > 0 else prix_unitaire_stock
        
        if input.quantite_vendue() > quantite_disponible:
            message_vente.set(f"Quantité insuffisante. Stock disponible : {quantite_disponible}")
            return
        
        # Mettre à jour le stock
        stock.loc[stock_index, "Quantite"] -= input.quantite_vendue()
        
        # S'assurer que la colonne Quantite_initiale existe
        if "Quantite_initiale" not in stock.columns:
            stock["Quantite_initiale"] = stock["Quantite"].copy()
        
        # Ajouter la vente
        nouvelle_vente = pd.DataFrame({
            "Categorie": [input.categorie_vente()],
            "Sous-categorie": [input.sous_categorie_vente() or ""],
            "Produit": [input.produit_vente()],
            "Prix unitaire": [float(prix_unitaire_vente)],
            "Quantite vendue": [float(input.quantite_vendue())],
            "Date": [datetime.now().strftime("%d-%m-%Y")],  # Format "dd-mm-yyyy"
            "Total": [float(prix_unitaire_vente * input.quantite_vendue())]
        })
        
        if ventes.empty:
            ventes = nouvelle_vente
        else:
            # Convertir la colonne Date en datetime si ce n'est pas déjà fait
            if not pd.api.types.is_datetime64_any_dtype(ventes["Date"]):
                ventes["Date"] = pd.to_datetime(ventes["Date"], format="%d-%m-%Y")
            
            ventes = pd.concat([ventes, nouvelle_vente], ignore_index=True)
        
        # Convertir la colonne Date en datetime
        ventes["Date"] = pd.to_datetime(ventes["Date"], format="%d-%m-%Y")
        
        # Mettre à jour les données
        stock_data.set(stock)
        vente_data.set(ventes)
        
        # Sauvegarder les données
        save_data(stock, ventes)
        
        # Message de confirmation
        message_vente.set(f"{input.quantite_vendue()} {input.produit_vente()} vendus à {prix_unitaire_vente:.2f} Fbu l'unité.")
        
        # Réinitialiser les champs de vente
        ui.update_select("categorie_vente", selected="")
        ui.update_select("sous_categorie_vente", choices=[])
        ui.update_select("produit_vente", choices=[])
        ui.update_numeric("prix_unitaire_vente", value=0)
        ui.update_numeric("quantite_vendue", value=1)

    # Mise à jour des catégories pour la vente et l'analyse
    @reactive.Effect
    def update_dropdowns():
        stock = stock_data()
        
        if not stock.empty:
            # Mise à jour des catégories avec "Tous" en premier
            categories = ["Tous"] + stock["Categorie"].unique().tolist()
            ui.update_select("categorie_vente", choices=categories, selected="Tous")
            ui.update_select("categorie_analyse", choices=categories, selected="Tous")

    # Mise à jour des sous-catégories pour la vente et l'analyse
    @reactive.Effect
    def update_sous_categorie():
        stock = stock_data()
        
        if not stock.empty:
            # Filtrer les sous-catégories en fonction de la catégorie sélectionnée
            if input.categorie_vente():
                if input.categorie_vente() == "Tous":
                    sous_categories = ["Tous"] + stock["Sous-categorie"].unique().tolist()
                else:
                    sous_categories = ["Tous"] + stock[stock["Categorie"] == input.categorie_vente()]["Sous-categorie"].unique().tolist()
                ui.update_select("sous_categorie_vente", choices=sous_categories, selected="Tous")
            
            if input.categorie_analyse():
                if input.categorie_analyse() == "Tous":
                    sous_categories = ["Tous"] + stock["Sous-categorie"].unique().tolist()
                else:
                    sous_categories = ["Tous"] + stock[stock["Categorie"] == input.categorie_analyse()]["Sous-categorie"].unique().tolist()
                ui.update_select("sous_categorie_analyse", choices=sous_categories, selected="Tous")

    # Mise à jour des produits pour la vente et l'analyse
    @reactive.Effect
    def update_produits():
        stock = stock_data()
        
        if not stock.empty:
            # Filtrer les produits en fonction de la catégorie et sous-catégorie sélectionnées
            if input.categorie_vente():
                if input.categorie_vente() == "Tous":
                    produits = ["Tous"] + stock["Produit"].unique().tolist()
                else:
                    mask = stock["Categorie"] == input.categorie_vente()
                    if input.sous_categorie_vente() and input.sous_categorie_vente() != "Tous":
                        mask &= stock["Sous-categorie"] == input.sous_categorie_vente()
                    produits = ["Tous"] + stock[mask]["Produit"].unique().tolist()
                ui.update_select("produit_vente", choices=produits, selected="Tous")
            
            if input.categorie_analyse():
                if input.categorie_analyse() == "Tous":
                    produits = ["Tous"] + stock["Produit"].unique().tolist()
                else:
                    mask = stock["Categorie"] == input.categorie_analyse()
                    if input.sous_categorie_analyse() and input.sous_categorie_analyse() != "Tous":
                        mask &= stock["Sous-categorie"] == input.sous_categorie_analyse()
                    produits = ["Tous"] + stock[mask]["Produit"].unique().tolist()
                ui.update_select("produit_analyse", choices=produits, selected="Tous")

    # Mise à jour du prix unitaire automatiquement
    @reactive.Effect
    def update_prix_unitaire_vente():
        stock = stock_data()
        if not stock.empty:
            # Mettre à jour le prix unitaire lorsqu'un produit est sélectionné
            if input.categorie_vente() and input.produit_vente():
                mask = (stock["Categorie"] == input.categorie_vente()) & (stock["Produit"] == input.produit_vente())
                if input.sous_categorie_vente():
                    mask &= stock["Sous-categorie"] == input.sous_categorie_vente()
                
                produit = stock[mask]
                if not produit.empty:
                    prix_unitaire = produit.iloc[0]["Prix unitaire"]
                    ui.update_numeric("prix_unitaire_vente", value=prix_unitaire)

    # Affichage des messages de confirmation
    @output
    @render.text
    def message_confirmation():
        return message_stock()

    @output
    @render.text
    def message_vente_text():
        return message_vente()

    # Tableau de stock avec boutons d'action
    @output
    @render.ui
    def tableau_stock():
        stock = stock_data()
        
        if stock.empty:
            return ui.p("Aucun produit en stock pour le moment.")
        
        # Créer le tableau HTML
        table_header = """
        <table class="table">
            <thead>
                <tr>
                    <th>Catégorie</th>
                    <th>Sous-catégorie</th>
                    <th>Produit</th>
                    <th>Prix unitaire</th>
                    <th>Quantité</th>
                    <th>Date</th>
                    <th>Action</th>
                </tr>
            </thead>
            <tbody>
        """
        
        table_rows = []
        for i, row in stock.iterrows():
            table_row = f"""
            <tr>
                <td>{row['Categorie']}</td>
                <td>{row['Sous-categorie']}</td>
                <td>{row['Produit']}</td>
                <td>{row['Prix unitaire']}</td>
                <td>{row['Quantite']}</td>
                <td>{row['Date']}</td>
                <td>
                    <span class="delete-icon" data-index="{i}" onclick="Shiny.setInputValue('delete', {i}, {{priority: 'event'}});">🗑</span>
                    <span class="edit-icon" data-index="{i}" onclick="Shiny.setInputValue('modifier', {i}, {{priority: 'event'}});">✏</span>
                </td>
            </tr>
            """
            table_rows.append(table_row)
        
        table_footer = """
            </tbody>
        </table>
        """
        
        # Combiner le tableau
        table_html = table_header + "".join(table_rows) + table_footer
        
        # Retourner le tableau HTML
        return ui.HTML(table_html)
   
    # Gérer l'action de suppression
    @reactive.Effect
    @reactive.event(input.delete)
    def supprimer_produit():
        index = input.delete()
        stock = stock_data()
        if 0 <= index < len(stock):
            stock = stock.drop(index).reset_index(drop=True)
            stock_data.set(stock)
            message_stock.set(f"Produit à l'index {index} supprimé.")

    # Gérer l'action de modification
    @reactive.Effect
    @reactive.event(input.modifier)
    def modifier_produit():
        index = input.modifier()
        stock = stock_data()
        if 0 <= index < len(stock):
            produit = stock.iloc[index]
            # Stocker l'index pour la mise à jour ultérieure
            produit_en_modification.set(index)
        
            # D'abord, mettre à jour les choix disponibles dans les listes déroulantes
            categories = list(stock["Categorie"].unique())
            ui.update_selectize("categorie", choices=categories, selected=produit["Categorie"])
        
            # Filtrer les sous-catégories correspondant à la catégorie sélectionnée
            sous_categories = list(stock[stock["Categorie"] == produit["Categorie"]]["Sous-categorie"].unique())
            ui.update_selectize("sous_categorie", choices=sous_categories, selected=produit["Sous-categorie"])
        
            # Filtrer les produits correspondant à la catégorie et sous-catégorie sélectionnées
            produits = list(stock[
                (stock["Categorie"] == produit["Categorie"]) & 
                (stock["Sous-categorie"] == produit["Sous-categorie"])
            ]["Produit"].unique())
            ui.update_selectize("produit", choices=produits, selected=produit["Produit"])
        
            # Mettre à jour les champs numériques
            ui.update_numeric("prix_unitaire", value=produit["Prix unitaire"])
            ui.update_numeric("quantite", value=produit["Quantite"])
        
            message_stock.set(f"Modification du produit {produit['Produit']}.")

    
    # Affichage du tableau des ventes avec quantité restante au stock
    @output
    @render.ui
    def tableau_vente():
        stock = stock_data()
        ventes = vente_data()

        # Si le tableau est vide, afficher un message
        if ventes.empty:
            return ui.p("Aucune vente enregistrée pour le moment.")

        # Convertir la colonne Date en datetime si ce n'est pas déjà fait
        if "Date" in ventes.columns:
            ventes["Date"] = pd.to_datetime(ventes["Date"], format="%d-%m-%Y")

        # Fusionner les données de stock et de ventes pour afficher la quantité restante
        ventes_data = ventes.merge(
            stock[["Categorie", "Sous-categorie", "Produit", "Quantite"]],
            on=["Categorie", "Sous-categorie", "Produit"],
            how="left",
            suffixes=("", "_stock")
        )

        # Renommer la colonne de quantité restante
        ventes_data = ventes_data.rename(columns={"Quantite": "Quantite restante"})

        # Remplacer les NaN par 0 pour les produits sans stock
        ventes_data["Quantite restante"] = ventes_data["Quantite restante"].fillna(0)

        # Appliquer les filtres seulement s'ils sont sélectionnés
        filtered_data = ventes_data.copy()

        # Filtrage par catégorie
        if input.categorie_vente() and input.categorie_vente() != "Tous":
            filtered_data = filtered_data[filtered_data["Categorie"] == input.categorie_vente()]

        # Filtrage par sous-catégorie
        if input.sous_categorie_vente() and input.sous_categorie_vente() != "Tous":
            filtered_data = filtered_data[filtered_data["Sous-categorie"] == input.sous_categorie_vente()]

        # Filtrage par produit
        if input.produit_vente() and input.produit_vente() != "Tous":
            filtered_data = filtered_data[filtered_data["Produit"] == input.produit_vente()]

        # Créer le tableau HTML avec une colonne "Action"
        table_html = """
        <div class="table-responsive">
            <table class="table table-striped table-bordered">
                <thead>
                    <tr>
                        <th>Catégorie</th>
                        <th>Sous-catégorie</th>
                        <th>Produit</th>
                        <th>Prix unitaire</th>
                        <th>Quantité vendue</th>
                        <th>Total</th>
                        <th>Quantité restante</th>
                        <th>Date</th>
                        <th>Action</th>
                    </tr>
                </thead>
                <tbody>
        """

        for i, row in filtered_data.iterrows():
            table_html += f"""
            <tr>
                <td>{row['Categorie']}</td>
                <td>{row['Sous-categorie']}</td>
                <td>{row['Produit']}</td>
                <td>{row['Prix unitaire']}</td>
                <td>{row['Quantite vendue']}</td>
                <td>{row['Total']:.2f} Fbu</td>
                <td>{row['Quantite restante']}</td>
                <td>{row['Date'].strftime('%d-%m-%Y')}</td>
                <td>
                    <span class="delete-icon" data-index="{i}" onclick="Shiny.setInputValue('delete_vente', {i}, {{priority: 'event'}});">🗑</span>
                </td>
            </tr>
            """

        table_html += """
                </tbody>
            </table>
        </div>
        """

        return ui.HTML(table_html)
    
    @reactive.Effect
    @reactive.event(input.categorie_vente)
    def update_sous_categorie_vente():
        stock = stock_data()
        if not stock.empty and input.categorie_vente():
            if input.categorie_vente() == "Tous":
                sous_categories = ["Tous"] + stock["Sous-categorie"].unique().tolist()
            else:
                sous_categories = ["Tous"] + stock[stock["Categorie"] == input.categorie_vente()]["Sous-categorie"].unique().tolist()
            ui.update_select("sous_categorie_vente", choices=sous_categories, selected="Tous")

    @reactive.Effect
    @reactive.event(input.sous_categorie_vente)
    def update_produit_vente():
        stock = stock_data()
        if not stock.empty and input.categorie_vente() and input.sous_categorie_vente():
            if input.categorie_vente() == "Tous" and input.sous_categorie_vente() == "Tous":
                produits = ["Tous"] + stock["Produit"].unique().tolist()
            elif input.categorie_vente() == "Tous":
                produits = ["Tous"] + stock[stock["Sous-categorie"] == input.sous_categorie_vente()]["Produit"].unique().tolist()
            elif input.sous_categorie_vente() == "Tous":
                produits = ["Tous"] + stock[stock["Categorie"] == input.categorie_vente()]["Produit"].unique().tolist()
            else:
                produits = ["Tous"] + stock[
                    (stock["Categorie"] == input.categorie_vente()) &
                    (stock["Sous-categorie"] == input.sous_categorie_vente())
                ]["Produit"].unique().tolist()
            ui.update_select("produit_vente", choices=produits, selected="Tous")
    
    @reactive.Effect
    @reactive.event(input.delete_vente)
    def supprimer_vente():
        index = input.delete_vente()
        ventes = vente_data()
        
        if 0 <= index < len(ventes):
            # Récupérer la vente à supprimer
            vente_supprimee = ventes.iloc[index]
            
            # Supprimer la vente du DataFrame
            ventes = ventes.drop(index).reset_index(drop=True)
            
            # Mettre à jour les données de ventes
            vente_data.set(ventes)
            
            # Sauvegarder les données
            save_data(stock_data(), ventes)
            
            # Afficher un message de confirmation
            message_vente.set(f"Vente de {vente_supprimee['Produit']} supprimée avec succès.")

    # Fusionner les données de stock et de ventes pour l'analyse
    @reactive.Calc
    def merged_data():
        stock = stock_data()
        ventes = vente_data()

        # Fusionner les données sur les colonnes communes
        merged = stock.merge(
            ventes.groupby(["Categorie", "Sous-categorie", "Produit", "Date"]).agg({
                "Quantite vendue": "sum",
                "Total": "sum"
            }).reset_index(),
            on=["Categorie", "Sous-categorie", "Produit", "Date"],  # Inclure 'Date' dans la fusion
            how="left"
        )

        # Remplacer les NaN par 0 pour les produits sans ventes
        merged["Quantite vendue"] = merged["Quantite vendue"].fillna(0)
        merged["Total"] = merged["Total"].fillna(0)

        return merged
    
    # Initialisation des choix au démarrage
    @reactive.Calc
    def filtered_data():
        stock = stock_data()
        ventes = vente_data()
        
        # Convertir les dates en pandas.Timestamp pour uniformiser le format
        if not ventes.empty and "Date" in ventes.columns:
            if not pd.api.types.is_datetime64_any_dtype(ventes["Date"]):
                ventes["Date"] = pd.to_datetime(ventes["Date"], format="%d-%m-%Y", errors='coerce')
        
        if not stock.empty and "Date" in stock.columns:
            if not pd.api.types.is_datetime64_any_dtype(stock["Date"]):
                stock["Date"] = pd.to_datetime(stock["Date"], format="%d-%m-%Y", errors='coerce')
        
        # Filtrer par dates si des dates sont sélectionnées
        date_debut = pd.to_datetime(input.date_debut()) if input.date_debut() else None
        date_fin = pd.to_datetime(input.date_fin()) if input.date_fin() else None
        
        # Filtrer les ventes par date
        filtered_ventes = ventes.copy()
        if date_debut is not None:
            filtered_ventes = filtered_ventes[filtered_ventes["Date"] >= date_debut]
        if date_fin is not None:
            filtered_ventes = filtered_ventes[filtered_ventes["Date"] <= date_fin]
        
        # Fusionner les données de stock et de ventes filtrées
        if not filtered_ventes.empty:
            merged = stock.merge(
                filtered_ventes.groupby(["Categorie", "Sous-categorie", "Produit"]).agg({
                    "Quantite vendue": "sum",
                    "Total": "sum"
                }).reset_index(),
                on=["Categorie", "Sous-categorie", "Produit"],
                how="left"
            )
        else:
            # Si pas de ventes après filtrage, créer une structure vide
            merged = stock.copy()
            merged["Quantite vendue"] = 0
            merged["Total"] = 0
        
        # Appliquer les filtres de catégorie, sous-catégorie et produit
        if input.categorie_analyse() and input.categorie_analyse() != "Tous":
            merged = merged[merged["Categorie"] == input.categorie_analyse()]
        if input.sous_categorie_analyse() and input.sous_categorie_analyse() != "Tous":
            merged = merged[merged["Sous-categorie"] == input.sous_categorie_analyse()]
        if input.produit_analyse() and input.produit_analyse() != "Tous":
            merged = merged[merged["Produit"] == input.produit_analyse()]
        
        return merged
        
    @reactive.Effect
    @reactive.event(input.filtrer)
    def appliquer_filtres():
        # Appliquer les filtres ici (cela se fait automatiquement via filtered_data())
        
        # Réinitialiser les filtres après application
        ui.update_select("categorie_analyse", selected="Tous")
        ui.update_select("sous_categorie_analyse", selected="Tous")
        ui.update_select("produit_analyse", selected="Tous")
        ui.update_date("date_debut", value=None)
        ui.update_date("date_fin", value=None)
        
        # Message de confirmation
        print("Filtres appliqués et réinitialisés")

    # Ajouter un nouvel output pour afficher la période sélectionnée
    @output
    @render.ui
    def periode_selectionnee():
        if not input.date_debut() and not input.date_fin():
            return ui.div(
                {"class": "alert alert-info"},
                "Toutes les données sont affichées (aucun filtre appliqué)."
            )
        else:
            debut = "Début" if input.date_debut() is None else input.date_debut()
            fin = "Aujourd'hui" if input.date_fin() is None else input.date_fin()
            return ui.div(
                {"class": "alert alert-info"},
                f"Période analysée : {debut} à {fin}"
            )

    # Affichage des totaux dans la page Analyse
    @output
    @render.text
    def total_stock():
        stock = stock_data()
        # Calcul de la valeur totale du stock actuel
        valeur_stock_actuel = (stock["Prix unitaire"] * stock["Quantite"]).sum()
    
        # Calculer la valeur de tous les produits (stock actuel + vendus)
        ventes = vente_data()
        valeur_produits_vendus = 0
        if not ventes.empty:
            valeur_produits_vendus = ventes["Total"].sum()
    
        valeur_totale = valeur_stock_actuel + valeur_produits_vendus
        return f"Valeur totale des produits (stock + vendus) : {valeur_totale:.2f} Fbu"

    @output
    @render.text
    def total_ventes():
        ventes = vente_data()
        if ventes.empty:
            return "Coût total des produits vendus : 0.00 Fbu"
    
        cout_total_ventes = ventes["Total"].sum()
        return f"Coût total des produits vendus : {cout_total_ventes:.2f} Fbu"

    # Fonction pour calculer les pourcentages de stock restant
    def calculer_pourcentage_stock():
        stock = stock_data()
        
        if stock.empty:
            return pd.DataFrame()
            
        # S'assurer que la colonne Quantite_initiale existe
        if "Quantite_initiale" not in stock.columns:
            stock["Quantite_initiale"] = stock["Quantite"]
            for i, row in stock.iterrows():
                # Chercher si ce produit a été vendu
                ventes = vente_data()
                if not ventes.empty:
                    ventes_produit = ventes[
                        (ventes["Categorie"] == row["Categorie"]) & 
                        (ventes["Produit"] == row["Produit"])
                    ]
                    if not ventes_produit.empty:
                        # Estimer la quantité initiale en ajoutant les ventes
                        stock.loc[i, "Quantite_initiale"] = row["Quantite"] + ventes_produit["Quantite vendue"].sum()
    
        # Calculer le pourcentage restant
        stock["Pourcentage_restant"] = (stock["Quantite"] / stock["Quantite_initiale"] * 100).round(2)
        
        # Remplacer NaN par 0
        stock = stock.fillna(0)
        
        return stock
    
    # Alertes de stock critique (20% ou moins)
    @output
    @render.ui
    def alerte_stock_critique():
        stock = calculer_pourcentage_stock()
        stock_critique = stock[stock["Pourcentage_restant"] <= 20]
        
        if stock_critique.empty:
            return ui.p("Aucun produit n'est actuellement à un niveau critique.")
        
        # Créer le tableau HTML
        table_html = """
        <div class="table-responsive">
            <table class="table table-striped table-bordered">
                <thead>
                    <tr>
                        <th>Catégorie</th>
                        <th>Sous-catégorie</th>
                        <th>Produit</th>
                        <th>Stock initial</th>
                        <th>Stock restant</th>
                        <th>Pourcentage</th>
                        <th>Action</th>
                    </tr>
                </thead>
                <tbody>
        """
        
        for i, row in stock_critique.iterrows():
            table_html += f"""
            <tr class="alert-low-stock">
                <td>{row['Categorie']}</td>
                <td>{row['Sous-categorie']}</td>
                <td>{row['Produit']}</td>
                <td>{row['Quantite_initiale']}</td>
                <td>{row['Quantite']}</td>
                <td><span class="stock-percentage">{row['Pourcentage_restant']}%</span></td>
                <td>
                    <button onclick="Shiny.setInputValue('commander', {i}, {{priority: 'event'}});">Commander</button>
                </td>
            </tr>
            """
        
        table_html += """
                </tbody>
            </table>
        </div>
        """
        
        return ui.HTML(table_html)
    
    # Alertes de stock faible (21-40%)
    @output
    @render.ui
    def alerte_stock_faible():
        stock = calculer_pourcentage_stock()
        stock_faible = stock[(stock["Pourcentage_restant"] > 20) & (stock["Pourcentage_restant"] <= 40)]
        
        if stock_faible.empty:
            return ui.p("Aucun produit n'est actuellement à un niveau de stock faible.")
        
        # Créer le tableau HTML
        table_html = """
        <div class="table-responsive">
            <table class="table table-striped table-bordered">
                <thead>
                    <tr>
                        <th>Catégorie</th>
                        <th>Sous-catégorie</th>
                        <th>Produit</th>
                        <th>Stock initial</th>
                        <th>Stock restant</th>
                        <th>Pourcentage</th>
                    </tr>
                </thead>
                <tbody>
        """
        
        for i, row in stock_faible.iterrows():
            table_html += f"""
            <tr>
                <td>{row['Categorie']}</td>
                <td>{row['Sous-categorie']}</td>
                <td>{row['Produit']}</td>
                <td>{row['Quantite_initiale']}</td>
                <td>{row['Quantite']}</td>
                <td><span class="stock-percentage">{row['Pourcentage_restant']}%</span></td>
            </tr>
            """
        
        table_html += """
                </tbody>
            </table>
        </div>
        """
        
        return ui.HTML(table_html)
    
    # Mise à jour de la fonction qui affiche les statistiques de vente
    @output
    @render.ui
    def statistiques_vente():
        filtered = filtered_data()
        
        if filtered.empty:
            return ui.p("Aucune vente enregistrée pour la période sélectionnée.")
        
        # Vérifier si les colonnes nécessaires existent
        if "Total" not in filtered.columns or "Quantite vendue" not in filtered.columns:
            return ui.p("Les données de vente sont incomplètes pour la période sélectionnée.")
        
        # Calculer les statistiques
        total_ventes = filtered["Total"].sum()
        nbr_produits_vendus = filtered["Quantite vendue"].sum()
        
        # Produit le plus vendu (s'il y a des ventes)
        produit_top_info = "Aucun produit vendu"
        if nbr_produits_vendus > 0:
            produits_vendus = filtered[filtered["Quantite vendue"] > 0]
            if not produits_vendus.empty:
                produit_top = produits_vendus.sort_values("Quantite vendue", ascending=False).iloc[0]
                produit_top_info = f"{produit_top['Produit']} ({produit_top['Quantite vendue']} unités)"
        
        # Ventes par catégorie (avec gestion des dates)
        ventes = vente_data()
        
        # Filtrer les ventes par date
        date_debut = pd.to_datetime(input.date_debut()) if input.date_debut() else None
        date_fin = pd.to_datetime(input.date_fin()) if input.date_fin() else None
        
        if not ventes.empty and "Date" in ventes.columns:
            # Assurez-vous que les dates sont au bon format
            if not pd.api.types.is_datetime64_any_dtype(ventes["Date"]):
                ventes["Date"] = pd.to_datetime(ventes["Date"], format="%d-%m-%Y", errors='coerce')
            
            # Appliquer les filtres de date
            if date_debut is not None:
                ventes = ventes[ventes["Date"] >= date_debut]
            if date_fin is not None:
                ventes = ventes[ventes["Date"] <= date_fin]
        
        # Ventes par catégorie et date
        if not ventes.empty:
            ventes_par_categorie = ventes.groupby(["Categorie", "Date"]).agg({
                "Total": "sum",
                "Quantite vendue": "sum"
            }).reset_index()
            
            # Trier par date
            ventes_par_categorie = ventes_par_categorie.sort_values("Date")
            
            # Créer le contenu du tableau ventes par catégorie
            rows_categorie = ""
            for _, row in ventes_par_categorie.iterrows():
                date_str = row['Date'].strftime('%d-%m-%Y')  # Format "dd-mm-yyyy"
                rows_categorie += f"""
                <tr>
                    <td>{row['Categorie']}</td>
                    <td>{date_str}</td>
                    <td>{row['Quantite vendue']}</td>
                    <td>{row['Total']:.2f} Fbu</td>
                </tr>
                """
        else:
            rows_categorie = "<tr><td colspan='4'>Pas de ventes pour la période sélectionnée</td></tr>"
        
        # Créer le tableau HTML pour les statistiques de vente
        html = f"""
        <div class="row">
            <div class="col-md-4">
                <div class="card">
                    <div class="card-body">
                        <h5 class="card-title">Total des ventes</h5>
                        <p class="card-text">{total_ventes:.2f} Fbu</p>
                    </div>
                </div>
            </div>
            <div class="col-md-4">
                <div class="card">
                    <div class="card-body">
                        <h5 class="card-title">Produits vendus</h5>
                        <p class="card-text">{nbr_produits_vendus} unités</p>
                    </div>
                </div>
            </div>
            <div class="col-md-4">
                <div class="card">
                    <div class="card-body">
                        <h5 class="card-title">Produit le plus vendu</h5>
                        <p class="card-text">{produit_top_info}</p>
                    </div>
                </div>
            </div>
        </div>
        <div class="row mt-4">
            <div class="col-md-12">
                <h5>Ventes par catégorie et date</h5>
                <table class="table table-striped">
                    <thead>
                        <tr>
                            <th>Catégorie</th>
                            <th>Date</th>
                            <th>Quantité</th>
                            <th>Montant</th>
                        </tr>
                    </thead>
                    <tbody>
                        {rows_categorie}
                    </tbody>
                </table>
            </div>
        </div>
        """
        
        return ui.HTML(html)

    # Mise à jour de la fonction pour afficher les produits avec le pourcentage de stock
    @output
    @render.ui
    def tableau_stock_pourcentage():
        filtered = filtered_data()
        
        if filtered.empty:
            return ui.p("Aucun produit trouvé pour la période sélectionnée.")
        
        # Remplacer NaN par 0
        filtered = filtered.fillna(0)
        
        # Calculer le pourcentage de stock restant
        if "Quantite_initiale" in filtered.columns and "Quantite" in filtered.columns:
            filtered["Pourcentage_restant"] = (filtered["Quantite"] / filtered["Quantite_initiale"] * 100).round(2)
        else:
            return ui.p("Données de stock incomplètes.")
        
        # Créer le tableau HTML
        table_html = """
        <div class="table-responsive">
            <table class="table table-striped table-bordered">
                <thead>
                    <tr>
                        <th>Catégorie</th>
                        <th>Sous-catégorie</th>
                        <th>Produit</th>
                        <th>Stock initial</th>
                        <th>Stock restant</th>
                        <th>Pourcentage restant</th>
                        <th>Quantité vendue</th>
                        <th>Total ventes</th>
                    </tr>
                </thead>
                <tbody>
        """
        
        for _, row in filtered.iterrows():
            quantite_vendue = row.get('Quantite vendue', 0)
            total_ventes = row.get('Total', 0)
            table_html += f"""
            <tr>
                <td>{row['Categorie']}</td>
                <td>{row['Sous-categorie']}</td>
                <td>{row['Produit']}</td>
                <td>{row['Quantite_initiale']}</td>
                <td>{row['Quantite']}</td>
                <td><span class="stock-percentage">{row['Pourcentage_restant']}%</span></td>
                <td>{quantite_vendue}</td>
                <td>{total_ventes:.2f} Fbu</td>
            </tr>
            """
        
        table_html += """
                </tbody>
            </table>
        </div>
        """
        
        return ui.HTML(table_html)
    
    @reactive.Effect
    @reactive.event(input.afficher_tout)
    def afficher_tout():
        # Réinitialiser les filtres
        ui.update_select("categorie_analyse", selected="Tous")
        ui.update_select("sous_categorie_analyse", selected="Tous")
        ui.update_select("produit_analyse", selected="Tous")
        ui.update_date("date_debut", value=None)
        ui.update_date("date_fin", value=None)
        
        # Forcer la mise à jour des données
        filtered_data.set(stock_data())

    # Mise à jour des fonctions pour les actions sur les dates
    @reactive.Effect
    @reactive.event(input.aujourd_hui)
    def set_aujourd_hui():
        today = datetime.now().date()
        ui.update_date("date_debut", value=today)
        ui.update_date("date_fin", value=today)

    @reactive.Effect
    @reactive.event(input.cette_semaine)
    def set_cette_semaine():
        today = datetime.now().date()
        start_of_week = today - timedelta(days=today.weekday())
        ui.update_date("date_debut", value=start_of_week)
        ui.update_date("date_fin", value=today)

    @reactive.Effect
    @reactive.event(input.ce_mois)
    def set_ce_mois():
        today = datetime.now().date()
        start_of_month = today.replace(day=1)
        ui.update_date("date_debut", value=start_of_month)
        ui.update_date("date_fin", value=today)

    @reactive.Effect
    @reactive.event(input.ce_trimestre)
    def set_ce_trimestre():
        today = datetime.now().date()
        current_quarter = ((today.month - 1) // 3) + 1
        start_month = (current_quarter - 1) * 3 + 1
        start_of_quarter = today.replace(month=start_month, day=1)
        ui.update_date("date_debut", value=start_of_quarter)
        ui.update_date("date_fin", value=today)

    @reactive.Effect
    @reactive.event(input.cette_annee)
    def set_cette_annee():
        today = datetime.now().date()
        start_of_year = today.replace(month=1, day=1)
        ui.update_date("date_debut", value=start_of_year)
        ui.update_date("date_fin", value=today)

    @reactive.Effect
    @reactive.event(input.tout)
    def set_tout():
        ui.update_date("date_debut", value=None)
        ui.update_date("date_fin", value=None)

# Créer l'application Shiny
app = App(app_ui, server)