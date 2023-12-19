# -*- coding: utf-8 -*-
"""
Created on Mon Dec 18 12:07:31 2023

@author: julie
"""

import geopandas as gpd
import pandas as pd

# 1. Import des fichiers
stops = pd.read_csv('C:\\Users\\julie\\Documents\\3A\\STATISTIQUES\\PROJET GEOSTATS\\DONNEES\\Horaires et fréquence sur les lignes TeC IDF\\IDFM-gtfs\\stops.txt')
stop_times = pd.read_csv('C:\\Users\\julie\\Documents\\3A\\STATISTIQUES\\PROJET GEOSTATS\\DONNEES\\Horaires et fréquence sur les lignes TeC IDF\\IDFM-gtfs\\stop_times.txt')
communes = gpd.read_file('C:\\Users\\julie\\Documents\\3A\\STATISTIQUES\\PROJET GEOSTATS\\DONNEES\\cities_with_arr\\cities_arr.shp')

# 2. Conversion des fichiers en GeoDataFrame
communes_spatial = gpd.GeoDataFrame(data = communes, geometry='geometry')

# 3. Affichage
communes.plot()
base = communes.plot(color='white', edgecolor='black')
#stops.plot(ax = base, x = stops.stop_lon, y = stops.stop_lat, color = 'darkblue')

# 4. Agrégation sur les arrêts pour avoir le nombre de passages par arrêt
# 4.1. Création d'une table simplifié depuis stop_times
stop_times.insert(loc = 10, column = 'arrival_time_num', value = 1)
#stop_times_reduit = pd.DataFrame(data = stop_times, columns=['id', 'arrival_time_num'])

# 4.2 Calcul de l'agrégation
frequence_par_arret = stop_times.groupby(by=["stop_id"]).sum()

# 5. Jointure de la table des fréquences sur les arrêts
stops = stops.join(other = frequence_par_arret, on = 'stop_id', how = 'left')

# 6. Jointure spatiale sur les communes
# 6.1 Formatage et reprojection
stops_spatial = gpd.GeoDataFrame(data = stops, geometry = gpd.points_from_xy(x = stops.stop_lon, y = stops.stop_lat),crs = 4326)
stops_spatial = stops_spatial.to_crs(2154)
# 6.2 Jointure spatiale
jointure = gpd.sjoin(left_df= stops_spatial, right_df = communes, how = 'left', predicate = 'within')
# 6.3 Fréquence par commune et arrêts par commune
frequence_par_commune = jointure.groupby(by=["CODGEO"])['arrival_time_num'].sum()
stops_par_commune = jointure.groupby(by=["CODGEO"])['stop_id'].count()

# 7. Export des résultats
frequence_par_commune = pd.DataFrame(data = frequence_par_commune)
stops_par_commune = pd.DataFrame(data = stops_par_commune)
frequence_par_commune.to_csv('C:\\Users\\julie\\Documents\\3A\\STATISTIQUES\\PROJET GEOSTATS\\geostats_chomage\\frequence_par_commune.csv')
stops_par_commune.to_csv('C:\\Users\\julie\\Documents\\3A\\STATISTIQUES\\PROJET GEOSTATS\\geostats_chomage\\stops_par_commune.csv')

