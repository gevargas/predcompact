import pandas as pd
import matplotlib.pyplot as plt

def creer_histogramme_marques(data_avec_ingredients, figsize=(14, 6), color='steelblue'):
    """
    Crée un histogramme représentant le nombre de produits par marque.
    
    Parameters:
    -----------
    data_avec_ingredients : pd.DataFrame
        DataFrame contenant la colonne 'Marque'
    figsize : tuple, optional
        Taille de la figure (largeur, hauteur). Par défaut (14, 6)
    color : str, optional
        Couleur des barres. Par défaut 'steelblue'
    
    Returns:
    --------
    matplotlib.figure.Figure : Figure matplotlib créée
    """

    nb_produit = 'Nombre de produits'
    # Créer un DataFrame avec le nombre de produits par marque (sans sous-totaux)
    produits_par_marque = data_avec_ingredients.groupby('Marque').size().reset_index(name=nb_produit)
    
    # Trier par nombre de produits décroissant
    produits_par_marque = produits_par_marque.sort_values(nb_produit, ascending=False)
    
    # Créer l'histogramme
    fig = plt.figure(figsize=figsize)
    plt.bar(produits_par_marque['Marque'], produits_par_marque[nb_produit], color=color)
    plt.xlabel('Marque', fontsize=12)
    plt.ylabel(nb_produit, fontsize=12)
    plt.title('Nombre de produits par Marque', fontsize=14, fontweight='bold')
    plt.xticks(rotation=45, ha='right')
    plt.grid(axis='y', alpha=0.3)
    plt.tight_layout()
    
    return fig


def afficher_histogramme_marques(data_avec_ingredients, figsize=(14, 6), color='steelblue'):
    """
    Crée et affiche un histogramme représentant le nombre de produits par marque.
    
    Parameters:
    -----------
    data_avec_ingredients : pd.DataFrame
        DataFrame contenant la colonne 'Marque'
    figsize : tuple, optional
        Taille de la figure (largeur, hauteur). Par défaut (14, 6)
    color : str, optional
        Couleur des barres. Par défaut 'steelblue'
    """
    creer_histogramme_marques(data_avec_ingredients, figsize, color)
    plt.show()
    
    # Afficher quelques statistiques
    produits_par_marque = data_avec_ingredients.groupby('Marque').size().sort_values(ascending=False)
    print(f"\nTotal de marques: {len(produits_par_marque)}")
    print(f"Total de produits: {produits_par_marque.sum()}")
