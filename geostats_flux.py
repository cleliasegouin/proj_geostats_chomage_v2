# -*- coding: utf-8 -*-
"""
Created on Tue Dec 12 15:50:32 2023

@author: josep
"""

import pandas as pd 
import geopandas as gpd 
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import os

## Changer de répertoire de travail 
os.chdir("C:/Users/josep/OneDrive/Documents/ENSG/geodatascience/geostats_chomage")


##Import données communes (et arrondissement de Paris)
arrondissement = gpd.read_file("./data/communes_arrondissements/arrondissements.shp")
cities = gpd.read_file("./data/communes_arrondissements/COMMUNE.shp")

# On garde les communes d'IDF
cities_idf = cities[cities["INSEE_REG"]=="11"]

# Ajout des arrondissement de Paris 
    # On supprime l'entité "Paris"
cities_idf = cities_idf[cities_idf["INSEE_COM"]!= "75056"]

    # Préparation de la concaténation
arrondissement = arrondissement.to_crs(2154)
cities_idf = cities_idf.to_crs(2154)
arrondissement = arrondissement.rename(columns={"c_arinsee": "INSEE_COM"})

cities_w_arrondissement = pd.concat([cities_idf, arrondissement],ignore_index=True)


## Import des données de flux de mobilités : 
    
flux = pd.read_csv("./data/flux_dom_trav/base-flux-mobilite-domicile-lieu-travail-2019.csv",sep=';',
                   dtype = {'CODGEO': str, 'LIBGEO': str, 'DCLT': str,'L_DCLT':str,'NBFLUX_C198ACTOCC15O':np.float64})

flux.reset_index(inplace=True)

# Optionally, you can rename the new index column
flux.rename(columns={'index': 'id'}, inplace=True)

cities_w_arrondissement = cities_w_arrondissement.rename(columns={"INSEE_COM": "CODGEO"})
cities_w_arrondissement = cities_w_arrondissement.dropna(subset="CODGEO")
cities_w_arrondissement["CODGEO"] = cities_w_arrondissement["CODGEO"].astype(str)


##Jointure des flux et communes d'IDF
flux_dep = pd.merge(cities_w_arrondissement,flux, how="inner",on="CODGEO")

cities_w_arrondissement = cities_w_arrondissement.rename(columns={"CODGEO": "DCLT"})
flux_arr = pd.merge(cities_w_arrondissement,flux, how="inner",on="DCLT")
## Calcul des centroïdes des polygones 
flux_dep["centroid"] = flux_dep["geometry"].centroid
flux_arr["centroid"] = flux_arr["geometry"].centroid

flux_dep["lat"] = flux_dep["centroid"].y
flux_dep["lon"] = flux_dep["centroid"].x

flux_arr["lat"] = flux_arr["centroid"].y
flux_arr["lon"] = flux_arr["centroid"].x

## 

df_grouped_flux = pd.DataFrame(flux_arr.groupby('CODGEO')['NBFLUX_C19_ACTOCC15P'].sum().sort_values(ascending=False)).reset_index()

## Questions : 
    #- isolements des communes actives selon un seuil sur les valeurs de flux pour définir bassin d'emploi
    #

## VISU Box plot 
# box_pop = go.Box(y=df_grouped_pop['POPULATION'], name="Population")
box_flux = go.Box(y=df_grouped_flux['NBFLUX_C19_ACTOCC15P'], name="Flux")

fig = go.Figure()
#fig.add_trace(box_pop)
fig.add_trace(box_flux)


fig.write_html("C:/Users/josep/OneDrive/Documents/ENSG/geodatascience/geostats_chomage/box_plot_flux.html")


## VISU Histogramme 


fig = px.histogram(df_grouped_flux, x='NBFLUX_C19_ACTOCC15P', title="Histogramme du Nombre de Flux par Commune")

fig.update_layout(
    xaxis_title="Nombre Total de Flux",
    yaxis_title="Nombre de Communes",
    title="Distribution du Nombre de Flux par Commune"
)

fig.write_html("C:/Users/josep/OneDrive/Documents/ENSG/geodatascience/geostats_chomage/histo_flux.html")
