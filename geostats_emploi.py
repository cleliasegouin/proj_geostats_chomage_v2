# -*- coding: utf-8 -*-
"""
Created on Sun Dec 17 11:32:09 2023

@author: josep
"""

import pandas as pd 
import geopandas as gpd 
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import os

## Changer de répertoire de travail 
# os.chdir("C:/Users/steph/OneDrive/Bureau/ENSG/ING3/DESIGEO/Analyse spatiale/Projet/geostats_chomage")

##Import données commune 
## référence et source des données : https://www.insee.fr/fr/statistiques/7632867?sommaire=7632977#dictionnaire

arrondissement = gpd.read_file("data/communes_arrondissements/arrondissements.shp")
cities = gpd.read_file("data/communes_arrondissements/COMMUNE.shp")

# On garde les communes d'IDF
cities_idf = cities[cities["INSEE_REG"]=="11"]

# On supprime l'entité "Paris"
cities_idf = cities_idf[cities_idf["INSEE_COM"]!= "75056"]

# Préparation de la concaténation
arrondissement = arrondissement.to_crs(2154)
cities_idf = cities_idf.to_crs(2154)
arrondissement = arrondissement.rename(columns={"c_arinsee": "INSEE_COM"})

cities_w_arrondissement = pd.concat([cities_idf, arrondissement],ignore_index=True)

## Import données filosofi 

filosofi = pd.read_csv("data/emploi/base-cc-emploi-pop-active-2020_v2.CSV", sep=";",dtype =str)

cities_w_arrondissement = cities_w_arrondissement.rename(columns={"INSEE_COM": "CODGEO"})
cities_w_arrondissement = cities_w_arrondissement.dropna(subset="CODGEO")

## peut etre filtrer le df avant jointure car 354 colonnes 
fil_com_idf = pd.merge(cities_w_arrondissement,filosofi, how="left",on="CODGEO")


## Taux population active par commune 
# P20_ACT1564  : Nombre de personnes actives de 15 à 64 ans en 2020
# P20_ACT15P : Nombre de personnes actives de 15 ans ou plus en 2020
# P20_ACTOCC / P20_ACTOCC1564 : Nombre de personnes actives occupées [de 15 à 64 ans] en 2020
# P20_CHOM1564 : Nombre de chômeurs de 15 à 64 ans en 2020
# P20_POP1564 : Nombre de personnes de 15 à 64 ans en 2020
# données disponible pour les années 2020, 2014, 2009 pour étude évolution si autre données 

df_pop_active = fil_com_idf[["ID","CODGEO","POPULATION","P20_ACTOCC1564","P20_ACT1564", "P20_ACT15P","P20_ACTOCC","P20_CHOM1564","P20_POP1564","geometry"]]
df_pop_active = df_pop_active.astype({"P20_ACT1564": float, "P20_ACT15P": float, "P20_ACTOCC1564": float,"P20_ACTOCC": float, "P20_CHOM1564": float, "P20_POP1564": float})

df_pop_active["taux_ACT15P_POPULATION"]= df_pop_active["P20_ACT15P"]/df_pop_active["POPULATION"]*100 
df_pop_active["taux_ACT1564_POP1564"]= df_pop_active["P20_ACT1564"]/df_pop_active["P20_POP1564"]*100 

df_pop_active["taux_ACTOCC_POP1564"]= df_pop_active["P20_ACTOCC"]/df_pop_active["P20_POP1564"]*100 
df_pop_active["taux_ACTOCC_POPULATION"]= df_pop_active["P20_ACTOCC"]/df_pop_active["POPULATION"]*100 

df_pop_active["taux_CHOM1564_POP1564"]= df_pop_active["P20_CHOM1564"]/df_pop_active["P20_POP1564"]*100 
df_pop_active["taux_CHOM1564_POPULATION"]= df_pop_active["P20_CHOM1564"]/df_pop_active["P20_POP1564"]*100 

## 5536762 // 5794216

df_pop_active.to_csv("./data/emploi/pop_active.csv",sep=";")
##Taux pauvreté des ménages : 
# MED20 : Médiane du niveau de vie (€) 
# PIMP20 : Part des ménages fiscaux imposés (%) 
# TP6020 : Taux de pauvreté-Ensemble (%) 
# TP60AGE120 : Taux de pauvreté des ménages dont le référent fiscal a moins de 30 ans (%) 
# TP60AGE220 : Taux de pauvreté des ménages dont le référent fiscal a de 30 à 39 ans (%) 
# TP60AGE320 : Taux de pauvreté des ménages dont le référent fiscal a de 40 à 49 ans (%) 
# TP60AGE420 : Taux de pauvreté des ménages dont le référent fiscal a de 50 à 59 ans (%) 
# TP60AGE520 : Taux de pauvreté des ménages dont le référent fiscal a de 60 à 74 ans (%) 

filosofi_nvx_vie = pd.read_csv("./data/emploi/cc_filosofi_2020_COM.csv", sep=";", dtype=str)
