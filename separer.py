import pandas as pd
import numpy as np
import difflib
import re

# Dictionnaire de correspondances pour normaliser les ingrédients
MAPPING_CORR = {
    'water': 'aqua',
    'eau': 'aqua',
    'glycerine': 'glycerin',
    'fragrance': 'parfum',
    'titanium dioxide': 'ci_77891',
    'mica': 'ci_77019',
    'iron oxides': 'ci_77491',  # Souvent regroupe 77491, 77492, 77499
    'tocopheryl acetate': 'tocopherol', # Vitamine E
}

def _nettoyer_ingredients_str(ingredients_str, separateur):
    """Nettoie et extrait les ingrédients d'une chaîne."""
    if ':' in ingredients_str:
        ingredients_str = ingredients_str.split(':', 1)[1]
    
    ingredients_liste = [ing.strip().lower() for ing in ingredients_str.split(separateur)]
    return [ing for ing in ingredients_liste if ing.strip()]

def _extraire_tous_ingredients(df, colonne_ingredient, separateur):
    """Extrait tous les ingrédients uniques de la colonne."""
    tous_ingredients = set()
    
    for ingredients_str in df[colonne_ingredient].dropna():
        if isinstance(ingredients_str, str):
            ingredients_liste = _nettoyer_ingredients_str(ingredients_str, separateur)
            tous_ingredients.update(ingredients_liste)
    
    return {ing for ing in tous_ingredients if ing.strip()}

def _filtrer_ingredients_indesirables(tous_ingredients):
    """Filtre les ingrédients indésirables."""
    ingredients_a_exclure = {
        ing for ing in tous_ingredients
        if ing.isdigit() or 'may contain' in ing or ing.startswith('+/-')
    }
    return sorted(tous_ingredients - ingredients_a_exclure)

def _normaliser_nom_colonne(ingredient):
    """Normalise un nom d'ingrédient en nom de colonne."""
    # 0. Pré-nettoyage
    ingredient_clean = ingredient.lower().strip()

    # 1. Vérification dans le mapping manuel
    for cle, valeur in MAPPING_CORR.items():
        # On remplace si le mot clé est présent (ex: "mineral oil" -> "paraffinum_liquidum" si mappé)
        # Attention aux faux positifs, ici on fait simple
        if cle == ingredient_clean or f"/{cle}" in ingredient_clean or f"{cle}/" in ingredient_clean:
            return valeur

    # 2. Nettoyage caractères spéciaux
    nom_colonne = (ingredient_clean.replace('*', '').replace(' ', '_').replace('-', '_').replace('(', '')
                   .replace(')', '').replace('/', '_').replace('.', '_')
                   .replace(',', '').replace("'", '').replace('"', '')
                   .replace('[', '').replace(']', '').replace(':', '_'))
    
    # 3. Règles hardcodées classiques
    if 'aqua' in nom_colonne:
        return 'aqua'
    if 'parfum' in nom_colonne:
        return 'parfum'
    
    # 4. Gestion des codes CI (Color Index)
    # On ne garde que le code (ex: ci_77510_ferric... -> ci_77510)
    match_ci = re.match(r'^(ci_\d+)', nom_colonne)
    if match_ci:
        return match_ci.group(1)
        
    return nom_colonne

def _creer_colonnes_mapping(tous_ingredients):
    """Crée le mapping des ingrédients vers les noms de colonnes."""
    colonnes_mapping = {}
    
    for ingredient in tous_ingredients:
        nom_colonne = _normaliser_nom_colonne(ingredient)
        
        if nom_colonne in colonnes_mapping:
            colonnes_mapping[nom_colonne].append(ingredient)
        else:
            colonnes_mapping[nom_colonne] = [ingredient]
    
    return colonnes_mapping

def _remplir_colonnes_binaires(df_result, df, colonne_ingredient, colonnes_mapping, separateur):
    """Remplit les colonnes binaires avec les valeurs d'ingrédients."""
    for nom_colonne, ingredients_associes in colonnes_mapping.items():
        df_result[nom_colonne] = np.nan
        
        for idx, ingredients_str in df[colonne_ingredient].items():
            if pd.notna(ingredients_str) and isinstance(ingredients_str, str):
                ingredients_liste = _nettoyer_ingredients_str(ingredients_str, separateur)
                
                if any(ing in ingredients_liste for ing in ingredients_associes):
                    df_result.loc[idx, nom_colonne] = 1

# Fonction pour séparer les ingrédients en colonnes binaires
def separer_ingredients_binaire(df, colonne_ingredient, separateur=','):
    """
    Sépare une colonne d'ingrédients en colonnes binaires.
    
    Parameters:
    df: DataFrame pandas
    colonne_ingredient: nom de la colonne contenant les ingrédients
    separateur: caractère de séparation (défaut: virgule)
    
    Returns:
    DataFrame avec nouvelles colonnes binaires pour chaque ingrédient
    """
    
    colonnes_a_garder = ['Nom', 'Marque', 'Groupe(s) / Société(s) cosmétique(s)',]
    df_result = df[colonnes_a_garder].copy()
    
    tous_ingredients = _extraire_tous_ingredients(df, colonne_ingredient, separateur)
    tous_ingredients = _filtrer_ingredients_indesirables(tous_ingredients)
    
    print(f"Nombre d'ingrédients uniques trouvés (avant fusion): {len(tous_ingredients)}")
    
    colonnes_mapping = _creer_colonnes_mapping(tous_ingredients)
    
    print(f"Nombre de colonnes créées (après fusion des doublons): {len(colonnes_mapping)}")
    
    _remplir_colonnes_binaires(df_result, df, colonne_ingredient, colonnes_mapping, separateur)
    
    return df_result, tous_ingredients

def suggerer_fusions(tous_ingredients, seuil=0.85):
    """
    Suggère des fusions d'ingrédients basées sur la similarité textuelle.
    Affiche les groupes d'ingrédients qui se ressemblent beaucoup.
    """
    sorted_ingredients = sorted(list(tous_ingredients))
    ignorer = set()
    
    print("\n" + "="*60)
    print("ANALYSE DES SIMILARITÉS (DOUBLONS POTENTIELS)")
    print("="*60)
    
    compteur = 0
    for i, ing1 in enumerate(sorted_ingredients):
        if ing1 in ignorer: continue
            
        # Trouver les proches correspondances dans le reste de la liste
        matches = difflib.get_close_matches(ing1, sorted_ingredients[i+1:], n=10, cutoff=seuil)
        
        if matches:
            groupe = [ing1] + matches
            print(f"Groupe {compteur+1}: {groupe}")
            compteur += 1
            # On marque comme traités pour éviter de les réafficher
            for m in matches:
                ignorer.add(m)
                
    if compteur == 0:
        print("Aucun groupe évident trouvé avec ce seuil.")
    print("="*60 + "\n")
