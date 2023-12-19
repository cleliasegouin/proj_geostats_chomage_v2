library(sf)
library(dplyr)

# Import des données 
temps_flux = readRDS('data/flux_dom_trav/listtimes.Rds')
flux = read.csv('data/flux_dom_trav/base-flux-mobilite-domicile-lieu-travail-2019.csv',sep=';')
df_pop_active = read.csv("./data/emploi/pop_active.csv",sep=";")
df_pop_chom = select(df_pop_active, CODGEO, P20_CHOM1564, taux_CHOM1564_POP1564,POPULATION,P20_POP1564)
df_pop_chom$CODGEO = as.character(df_pop_chom$CODGEO)

# Tableau des flux pour les temps de trajets en TC 
temps_TC = temps_flux$TC
temps_TC = temps_TC %>%  rename(CODGEO=ORI,DCLT=DES)
TC_flux_duration = left_join(x=flux,y=temps_TC,by=c('CODGEO','DCLT'))
TC_flux_duration_idf = TC_flux_duration[complete.cases(TC_flux_duration$VAL),]

# Ajout des données taux de chômage, pop active de la commune de départ
TC_flux_duration_idf_chom = left_join(TC_flux_duration_idf, df_pop_chom, by = c('CODGEO'))

# Tableau des flux pour les temps de trajets en voiture
temps_vpm = temps_flux$VPM
temps_vps = temps_flux$VPS
temps_vp = left_join(x=temps_vpm,y=temps_vps,by=c('ORI','DES'))
temps_vp$MEAN_DURATION = (temps_vp$VAL.x+temps_vp$VAL.y)/2
temps_vp = select(temps_vp,ORI,DES,MEAN_DURATION)
temps_vp = temps_vp %>%  rename(CODGEO=ORI,DCLT=DES)
VP_flux_duration = left_join(x=flux,y=temps_vp,by=c('CODGEO','DCLT'))
VP_flux_duration_idf = VP_flux_duration[complete.cases(VP_flux_duration$MEAN_DURATION),]

# Ajout des données de chômage de la commune de départ 
VP_flux_duration_idf_chom = left_join(VP_flux_duration_idf, df_pop_chom, by = c('CODGEO'))

# PLOT 
# plot(TC_flux_duration_idf_chom$NBFLUX_C19_ACTOCC15P,TC_flux_duration_idf_chom$taux_CHOM1564_POP1564)


### Inégalités d'accès aux TC - courbe de lorenz et coefficient de Gini 
#install.packages('ineq')
library(ineq)
lorenz = Lc(x=TC_flux_duration_idf_chom$VAL,n=TC_flux_duration_idf_chom$NBFLUX_C19_ACTOCC15P,plot=TRUE)
Gini(TC_flux_duration_idf_chom$VAL, corr = FALSE, na.rm = TRUE)

data_revenus = read.csv('data/emploi/cc_filosofi_2020_COM.csv',sep=';')
data_revenus = select(data_revenus, CODGEO, MED20)
VP_flux_duration_idf_chom_revenu = left_join(VP_flux_duration_idf_chom,data_revenus,by=c('CODGEO'))
VP_flux_duration_idf_chom_revenu$MED20 = as.numeric(VP_flux_duration_idf_chom_revenu$MED20,rm.na=T)
VP_flux_duration_idf_chom_revenu = na.omit(VP_flux_duration_idf_chom_revenu,subset=c('MED20'))

## Revenu/chômage 
library("ggpubr")
ggscatter(VP_flux_duration_idf_chom_revenu, x = "MED20", y = "taux_CHOM1564_POP1564", 
          add = "reg.line", conf.int = TRUE, 
          cor.coef = TRUE, cor.method = "pearson",
          xlab = "Revenu médian", ylab = "taux de chomage par commune de départ")

## Corrélation chômage/arrêt/fréquence de passage
frequences = read.csv('data/transports_idf/frequence_par_commune.csv')
arret = read.csv('data/transports_idf/stops_par_commune.csv')

comm_pop_freq = left_join(df_pop_active,frequences,by=c('CODGEO'))
comm_pop_freq_arr = left_join(comm_pop_freq,arret,by=c('CODGEO'))

comm_pop_freq_arr$freq_par_hab = 
  comm_pop_freq_arr$arrival_time_num/
  comm_pop_freq_arr$P20_POP1564

ggscatter(comm_pop_freq_arr, x = "arrival_time_num", y = "taux_CHOM1564_POP1564", 
          add = "reg.line", conf.int = TRUE, 
          cor.coef = TRUE, cor.method = "pearson",
          xlab = "Nombre de passages par jour", ylab = "taux de chomage par commune de départ")


VP_flux_duration_idf_chom_revenu_freq = left_join(VP_flux_duration_idf_chom_revenu,frequences,by=c('CODGEO'))
ggscatter(VP_flux_duration_idf_chom_revenu_freq, x = "arrival_time_num", y = "taux_CHOM1564_POP1564", 
         add = "reg.line", conf.int = TRUE, 
         cor.coef = TRUE, cor.method = "pearson",
         xlab = "Arrêts par commune", ylab = "taux de chomage par commune de départ")

  # normalisation par le nombre de communes 
VP_flux_duration_idf_chom_revenu_freq$freq_par_hab = 
VP_flux_duration_idf_chom_revenu_freq$arrival_time_num/
VP_flux_duration_idf_chom_revenu_freq$P20_POP1564


VP_flux_duration_idf_chom_revenu_freq_arr = left_join(VP_flux_duration_idf_chom_revenu_freq,arret,by=c('CODGEO'))
VP_flux_duration_idf_chom_revenu_freq_arr = filter(VP_flux_duration_idf_chom_revenu_freq_arr,CODGEO!='77291'&CODGEO!=95527&CODGEO!=91538)

ggscatter(VP_flux_duration_idf_chom_revenu_freq_arr, x = "freq_par_hab", y = "taux_CHOM1564_POP1564", 
          add = "reg.line", conf.int = TRUE, 
          cor.coef = TRUE, cor.method = "pearson",
          xlab = "Fréquence de passage par habitant", ylab = "taux de chomage par commune de départ")

ggscatter(VP_flux_duration_idf_chom_revenu_freq_arr, x = "stop_id", y = "taux_CHOM1564_POP1564", 
          add = "reg.line", conf.int = TRUE, 
          cor.coef = TRUE, cor.method = "pearson",
          xlab = "Nombre d'arrêts par commune", ylab = "taux de chomage par commune de départ")

ggscatter(VP_flux_duration_idf_chom_revenu_freq_arr, x = "stop_id", y = "MED20", 
          add = "reg.line", conf.int = TRUE, 
          cor.coef = TRUE, cor.method = "pearson",
          xlab = "Nombre d'arrêts par commune", ylab = "Niveau de vie médian")

ggscatter(VP_flux_duration_idf_chom_revenu_freq_arr, x = "freq_par_hab", y = "MED20", 
          add = "reg.line", conf.int = TRUE, 
          cor.coef = TRUE, cor.method = "pearson",
          xlab = "Nombre de passage par jour par habitant", ylab = "Niveau de vie médian")
