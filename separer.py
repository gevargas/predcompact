import pandas as pd
import numpy as np

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
    nom_colonne = (ingredient.replace(' ', '_').replace('-', '_').replace('(', '')
                   .replace(')', '').replace('/', '_').replace('.', '_')
                   .replace(',', '').replace("'", '').replace('"', '')
                   .replace('[', '').replace(']', '').replace(':', '_'))
    
    if 'aqua' in nom_colonne:
        return 'aqua'
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
