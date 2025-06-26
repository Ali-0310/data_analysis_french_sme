import pandas as pd

df_ventes = pd.read_csv("Donnes_ventes.csv")
df_produits = pd.read_csv("Donnees_produits.csv")
df_magasins = pd.read_csv("Donnes_magasins.csv")

print(df_ventes.head())
print(df_produits.head())
print(df_magasins.head())