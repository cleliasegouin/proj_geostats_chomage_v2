library(plyr)
library(dplyr)
library(readr)
library(ggplot2)
library(ggpubr)
library(sf)
library(mapsf)

# 1. Import des fichiers
# 1.1 Import des données brutes
communes <- st_read('C:\\Users\\julie\\Documents\\3A\\STATISTIQUES\\PROJET GEOSTATS\\DONNEES\\cities_with_arr\\cities_arr.shp')
# 1.2 Import des résultats du traitement des données
frequence_par_commune <- read.csv('C:\\Users\\julie\\Documents\\3A\\STATISTIQUES\\PROJET GEOSTATS\\geostats_chomage\\frequence_par_commune.csv')
stops_par_commune <- read.csv('C:\\Users\\julie\\Documents\\3A\\STATISTIQUES\\PROJET GEOSTATS\\geostats_chomage\\stops_par_commune.csv')

# 2. Jointures sur les communes
# 2.1 Jointure de la fréquence par commune sur les communes
frequence_par_commune$CODGEO <- as.character(frequence_par_commune$CODGEO)
frequence_par_commune_conso = left_join(x = communes,
                        y = frequence_par_commune,
                        by = join_by(CODGEO))
# 2.2 Jointure des stops par commune sur les communes
stops_par_commune$CODGEO <- as.character(stops_par_commune$CODGEO)
stops_par_commune_conso = left_join(x = communes,
                                        y = stops_par_commune,
                                        by = join_by(CODGEO))

# 3. Affichage des cartes
# 3.1 Affichage de la fréquence de passages par habitant par commune
frequence_par_commune_conso$freq_par_hab = 
  frequence_par_commune_conso$arrival_time_num/
  frequence_par_commune_conso$P20_POP156
mf_map(x = frequence_par_commune_conso,
       var = "freq_par_hab",
       type = "choro")
mf_map(x = frequence_par_commune_conso,
       var = "freq_par_hab",
       type = "prop")
# 3.2 Affichage de la proportion de stops par habitant par commune
stops_par_commune_conso$stops_par_hab = 
  stops_par_commune_conso$stop_id /
  stops_par_commune_conso$P20_POP156
mf_map(x = stops_par_commune_conso,
       var = "stops_par_hab",
       type = "choro")
mf_base(communes, col = "white", border = "black")
mf_map(x = stops_par_commune_conso,
       var = "stop_id",
       type = "prop")