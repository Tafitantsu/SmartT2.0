________________________________________
Projet de simulation : Intersection à 2 voies avec feux tricolores
1. Objectif
Simuler le fonctionnement d’une intersection à deux voies (Nord-Sud et Est-Ouest) en utilisant un réseau de Pétri, afin de :
•	Gérer la circulation des véhicules sur deux axes perpendiculaires.
•	Gérer le passage des piétons en sécurité.
•	Prendre en compte l’alternance des feux (Vert, Jaune, Rouge) et la temporisation.
•	Simuler les embouteillages (queues de véhicules) et la demande piétons.
•	Étudier les effets de la synchronisation, de la phase de sécurité et des priorités sur le flux global.
________________________________________
2. Modélisation avec réseau de Pétri
2.1 Composants
•	Places (états du système):
o	Feux voitures: NS_V, NS_Y, NS_R, EW_V, EW_Y, EW_R
o	Feux piétons : P_NS_V, P_NS_Y, P_NS_R, P_EW_V, P_EW_Y, P_EW_R
o	Phase sécurité : PS (Tous rouges)
o	Queues véhicules : Q_NS, Q_EW (jetons multiples)
o	Demande piétons : D_NS, D_EW (jeton = présence d’un piéton souhaitant traverser)
•	Transitions (événements) :
o	TV1, TV2, T_EW, TP_NS, TP_EW, T_PS, T_back
o	Chaque transition peut être associée à une temporisation [t_min, t_max]
o	Certaines transitions sont synchronisées (ex : passage NS rouge → EW vert, piétons correspondants)
•	Jetons:
o	Un jeton = état actif pour feux ou présence de piétons
o	Jetons multiples = nombre de véhicules en file d’attente
________________________________________
1.2	Règles de fonctionnement
1. Règles de gestion de base :
La gestion des feux de carrefour d'une intersection de 2 routes.
En temps normal, le temps de passage des voitures (au vert) dure 10 secondes sur la route prioritaire et 5 sur l'autre route
Le feux jaune dure 2 secondes
Le feux vert piéton fonctionne pendant le feu rouge et le feux rouge piéton pendant les feux vert et jaune
La nuit (une horloge gère le passage jour/nuit. On simulera cette horloge par un interrupteur) les feux jaunes clignotent (2 secondes)
Une des voie est une voie plus importante et donc prioritaire. Deux capteurs 'présence voiture' signalent qu'une voiture attend au feux de la route non prioritaire. S'il n'y a pas de voiture, les feux de la route prioritaire restent au vert (sauf en cas d'appel piéton que l'on simulera avec un interrupteur).
2. Cycle feux voitures et piétons :
o	NS vert, EW rouge → véhicules NS passent, piétons NS arrêtés.
o	NS jaune → prévision d’arrêt.
o	NS rouge + PS → EW vert si Q_EW > 0.
o	Piétons NS traversent si D_NS = 1.
o	EW vert → véhicules EW passent, NS rouge.
o	EW jaune → prévision d’arrêt.
o	EW rouge + PS → NS vert si Q_NS > 0.
o	Piétons EW traversent si D_EW = 1.
o	Cycle recommences.
3.	Gestion des embouteillages :
a.	Les queues Q_NS et Q_EW influencent la priorité du feu vert: plus, de jetons → feu vert prioritaire.
4.	Gestion des piétons :
a.	Si D_NS ou D_EW est présent et que la voie correspondante est rouge, la transition piétons peut tirer immédiatement.


5.	Phase sécurité PS:
a.	Tout rouge pendant une courte durée pour éviter conflit lors du changement de direction.
6.	Temporisation:
a.	Chaque transition associée à [t_min, t_max] pour simuler des durées variables des feux.
________________________________________
3. Objectifs de simulation
•	Visualiser le cycle complet des feux et la synchronisation véhicules/piétons.
•	Étudier l’effet des embouteillages et des demandes piétons sur le temps d’attente moyen.
•	Tester différents scénarios :
o	Période de pointe (queues longues)
o	Passage piétons fréquent ou rare
o	Variation des temporisations des feux
________________________________________
4. Livrables du projet
1.	Schéma réseau de Pétri complet (générer avec python)













2.	Simulation en Python (video)( voir demo):
o	Gestion des jetons
o	Temporisation des transitions
o	Gestion des queues et demandes piétons
o	Affichage en temps réels le changement de couleurs.
3.	Lien du code source :
https://github.com/Tafitantsu/SmartT2.0 
________________________________________

