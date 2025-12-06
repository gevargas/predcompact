import pandas as pd
from IPython.display import HTML

def creer_tableau_dynamique(data_avec_ingredients):
    """
    Crée un tableau croisé dynamique montrant le nombre de produits par marque,
    regroupés par groupe/société cosmétique avec des sous-totaux.
    
    Parameters:
    -----------
    data_avec_ingredients : pd.DataFrame
        DataFrame contenant les colonnes 'Groupe(s) / Société(s) cosmétique(s)' et 'Marque'
    
    Returns:
    --------
    pd.DataFrame : Tableau final avec sous-totaux et total général
    """

    groupe_cosmetique = 'Groupe(s) / Société(s) cosmétique(s)'
    nb_produit = 'Nombre de produits'
    # Créer le tableau : Nombre de produits par Marque regroupés par Groupe/Société
    comptage = data_avec_ingredients.groupby([groupe_cosmetique, 'Marque']).size().reset_index(name=nb_produit)
    
    # Calculer les sous-totaux par Groupe/Société
    subtotaux = data_avec_ingredients.groupby(groupe_cosmetique).size().to_dict()
    
    # Créer la liste finale avec insertion des sous-totaux
    lignes_finales = []
    for groupe in data_avec_ingredients[groupe_cosmetique].unique():
        if pd.notna(groupe):
            # Ajouter toutes les marques de ce groupe
            marques_groupe = comptage[comptage[groupe_cosmetique] == groupe]
            for _, row in marques_groupe.iterrows():
                lignes_finales.append({
                    groupe_cosmetique : row[groupe_cosmetique],
                    'Marque': row['Marque'],
                    nb_produit : row[nb_produit]
                })
            
            # Ajouter le sous-total du groupe
            lignes_finales.append({
                groupe_cosmetique: groupe,
                'Marque': 'SOUS-TOTAL',
                nb_produit : subtotaux[groupe]
            })
    
    # Ajouter le total général
    lignes_finales.append({
        groupe_cosmetique: 'TOTAL',
        'Marque': '',
        nb_produit : len(data_avec_ingredients)
    })
    
    # Créer le DataFrame final
    tableau_final = pd.DataFrame(lignes_finales)
    tableau_final = tableau_final.set_index([groupe_cosmetique, 'Marque'])
    
    return tableau_final


def afficher_tableau_dynamique(data_avec_ingredients):
    """
    Crée et affiche le tableau croisé dynamique en format HTML.
    
    Parameters:
    -----------
    data_avec_ingredients : pd.DataFrame
        DataFrame contenant les colonnes 'Groupe(s) / Société(s) cosmétique(s)' et 'Marque'
    
    Returns:
    --------
    IPython.display.HTML : Affichage HTML du tableau
    """
    tableau_final = creer_tableau_dynamique(data_avec_ingredients)
    
    print("Tableau croisé dynamique - Nombre de produits par Marque et Groupe/Société:")
    print("(avec sous-totaux par groupe)")
    print("="*80)
    
    html = tableau_final.to_html(max_rows=None)
    return HTML(html)
