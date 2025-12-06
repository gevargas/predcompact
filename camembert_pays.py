import pandas as pd
import matplotlib.pyplot as plt

def creer_camembert_pays(data_ingredient, seuil_pourcentage=2, figsize=(18, 8)):
    """
    Crée deux diagrammes camembert côte à côte :
    - Le premier montre la répartition des pays avec >= seuil_pourcentage%, les autres regroupés dans "Autres"
    - Le second détaille la catégorie "Autres"
    
    Parameters:
    -----------
    data_ingredient : pd.DataFrame
        DataFrame contenant la colonne 'Made in'
    seuil_pourcentage : float, optional
        Seuil en pourcentage pour séparer les pays principaux. Par défaut 2%
    figsize : tuple, optional
        Taille de la figure (largeur, hauteur). Par défaut (18, 8)
    
    Returns:
    --------
    tuple : (fig, pays_principaux, pays_autres, pourcentages)
    """
    # Compter les produits par pays (Made in)
    produits_par_pays = data_ingredient['Made in'].value_counts()
    
    # Calculer les pourcentages
    pourcentages = (produits_par_pays / produits_par_pays.sum() * 100).round(1)
    
    # Séparer les pays >= seuil% et < seuil%
    pays_principaux = produits_par_pays[pourcentages >= seuil_pourcentage]
    pays_autres = produits_par_pays[pourcentages < seuil_pourcentage]
    
    # Créer les données pour le camembert principal avec "Autres"
    if len(pays_autres) > 0:
        camembert_data = pd.concat([
            pays_principaux,
            pd.Series({'Autres': pays_autres.sum()})
        ])
    else:
        camembert_data = pays_principaux
    
    # Créer une figure avec 2 sous-graphiques
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=figsize)
    
    # Camembert principal - sans labels directs
    colors = plt.cm.Set3(range(len(camembert_data)))
    wedges, _, autotexts = ax1.pie(
        camembert_data, 
        labels=None,  # Pas de labels directs
        autopct='%1.1f%%',
        startangle=90,
        colors=colors,
        textprops={'fontsize': 11}
    )
    
    for autotext in autotexts:
        autotext.set_color('black')
        autotext.set_fontweight('bold')
    
    # Ajouter une légende à côté
    ax1.legend(wedges, camembert_data.index, 
              title="Pays",
              loc="center left",
              bbox_to_anchor=(1, 0, 0.5, 1),
              fontsize=10)
    
    ax1.set_title('Répartition des produits par pays (Made in)', fontsize=14, fontweight='bold', pad=20)
    
    # Détail de la catégorie "Autres" si elle existe
    if len(pays_autres) > 0:
        colors_autres = plt.cm.Pastel1(range(len(pays_autres)))
        wedges2, _, autotexts2 = ax2.pie(
            pays_autres,
            labels=None,  # Pas de labels directs
            autopct='%1.1f%%',
            startangle=90,
            colors=colors_autres,
            textprops={'fontsize': 9}
        )
        
        for autotext in autotexts2:
            autotext.set_color('black')
            autotext.set_fontweight('bold')
        
        # Légende pour "Autres"
        ax2.legend(wedges2, pays_autres.index,
                  title="Pays (Autres)",
                  loc="center left",
                  bbox_to_anchor=(1, 0, 0.5, 1),
                  fontsize=9)
        
        ax2.set_title(f'Détail "Autres" ({len(pays_autres)} pays < {seuil_pourcentage}%)', 
                     fontsize=12, fontweight='bold', pad=20)
    else:
        ax2.text(0.5, 0.5, f'Aucun pays < {seuil_pourcentage}%', ha='center', va='center', fontsize=12)
        ax2.axis('off')
    
    plt.tight_layout()
    
    return fig, pays_principaux, pays_autres, pourcentages


def afficher_camembert_pays(data_ingredient, seuil_pourcentage=2, figsize=(18, 8)):
    """
    Crée et affiche les diagrammes camembert avec statistiques détaillées.
    
    Parameters:
    -----------
    data_ingredient : pd.DataFrame
        DataFrame contenant la colonne 'Made in'
    seuil_pourcentage : float, optional
        Seuil en pourcentage pour séparer les pays principaux. Par défaut 2%
    figsize : tuple, optional
        Taille de la figure (largeur, hauteur). Par défaut (18, 8)
    """
    _, pays_principaux, pays_autres, pourcentages = creer_camembert_pays(
        data_ingredient, seuil_pourcentage, figsize
    )
    
    plt.show()
    
    # Afficher les statistiques détaillées
    produits_par_pays = data_ingredient['Made in'].value_counts()
    
    print("\n" + "="*60)
    print(f"PAYS PRINCIPAUX (≥ {seuil_pourcentage}%)")
    print("="*60)
    for pays, count in pays_principaux.items():
        print(f"{pays}: {count} produits ({pourcentages[pays]}%)")
    
    if len(pays_autres) > 0:
        print("\n" + "="*60)
        print(f"AUTRES PAYS (< {seuil_pourcentage}%)")
        print("="*60)
        for pays, count in pays_autres.items():
            print(f"{pays}: {count} produits ({pourcentages[pays]}%)")
        print(f"\nTotal 'Autres': {pays_autres.sum()} produits ({(pays_autres.sum()/produits_par_pays.sum()*100).round(1)}%)")
    
    print(f"\n{'='*60}")
    print(f"TOTAL: {produits_par_pays.sum()} produits")
