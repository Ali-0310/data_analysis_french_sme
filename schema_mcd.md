# Schéma MCD - Modèle en Étoile pour l'Analyse des Ventes

## Vue d'ensemble du modèle en étoile

```
                    ┌─────────────────┐
                    │   FAIT_VENTES   │
                    │   (Table de     │
                    │    faits)       │
                    └─────────────────┘
                            │
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
        ▼                   ▼                   ▼
┌───────────────┐   ┌───────────────┐   ┌───────────────┐
│   DIM_TEMPS   │   │ DIM_PRODUITS  │   │  DIM_MAGASINS │
│   (Dimension  │   │  (Dimension   │   │  ( Dimension  │
│   temporelle) │   │   produits)   │   │  géographique)│
└───────────────┘   └───────────────┘   └───────────────┘
```

## Détail des entités

### 1. FAIT_VENTES (Table de faits - Centre de l'étoile)

**Clés étrangères :**
- `ID_TEMPS` → DIM_TEMPS
- `ID_PRODUIT` → DIM_PRODUITS  
- `ID_MAGASIN` → DIM_MAGASINS

**Mesures (faits) :**
- `QUANTITE_VENDUE` (INTEGER)
- `MONTANT_VENTE` (DECIMAL) = QUANTITE_VENDUE × PRIX_PRODUIT

### 2. DIM_TEMPS (Dimension temporelle)

**Clé primaire :**
- `ID_TEMPS` (INTEGER, AUTO_INCREMENT)

**Attributs descriptifs :**
- `DATE_COMPLETE` (DATE)
- `JOUR_SEMAINE` (VARCHAR)
- `MOIS` (VARCHAR)
- `ANNEE` (INTEGER)
- `TRIMESTRE` (INTEGER)

### 3. DIM_PRODUITS (Dimension produits)

**Clé primaire :**
- `ID_PRODUIT` (INTEGER, AUTO_INCREMENT)

**Attributs descriptifs :**
- `ID_REFERENCE_PRODUIT` (VARCHAR)
- `NOM_PRODUIT` (VARCHAR)
- `PRIX_UNITAIRE` (DECIMAL)
- `STOCK_DISPONIBLE` (INTEGER)

### 4. DIM_MAGASINS (Dimension géographique)

**Clé primaire :**
- `ID_MAGASIN` (INTEGER)

**Attributs descriptifs :**
- `VILLE` (VARCHAR)
- `NOMBRE_SALARIES` (INTEGER)
- `REGION` (VARCHAR)
- `TAILLE_MAGASIN` (VARCHAR)

## Relations entre entités

```
FAIT_VENTES (1) ──── (N) DIM_TEMPS
     │
     ├─── (1) ──── (N) DIM_PRODUITS
     │
     └─── (1) ──── (N) DIM_MAGASINS
```

## Indicateurs de performance (KPIs) calculables

### Indicateurs de vente
- CA total par période, magasin, produit
- Quantité vendue par période, magasin, produit
- Panier moyen par magasin, période

### Indicateurs géographiques
- Performance par ville/région
- Top des magasins par CA

### Indicateurs temporels
- Saisonnalité des ventes
- Tendances mensuelles/trimestrielles

## Avantages du modèle en étoile

1. **Simplicité** : Structure claire et intuitive
2. **Performance** : Requêtes d'analyse rapides
3. **Flexibilité** : Facile d'ajouter de nouvelles dimensions
4. **Maintenabilité** : Séparation claire entre faits et dimensions
5. **Évolutivité** : Peut s'étendre vers un modèle en flocon si nécessaire 