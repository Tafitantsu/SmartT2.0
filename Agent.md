1. Objectif du modèle

Simuler le trafic urbain avec un réseau de Pétri coloré, où chaque jeton a une couleur représentant le type de véhicule. Le modèle permet :

    Suivre différents types de véhicules.

    Visualiser la circulation et identifier les congestions par catégorie.

2. Définition des places
Place	Description	Jetons initiaux (couleurs)
Attente	Véhicules en attente à une intersection	2 rouges, 2 jaunes, 1 vert
En_circulation	Véhicules en mouvement	0
Traversé	Véhicules ayant traversé	0

    Chaque jeton a une couleur pour indiquer son type.

3. Définition des transitions
Transition	Entrées	Sorties	Conditions
Commencer_circulation	Attente:1	En_circulation:1	Au moins 1 jeton disponible dans la place d’entrée
Terminer_circulation	En_circulation:1	Traversé:1	Au moins 1 jeton disponible dans la place d’entrée

    Les transitions déplacent les jetons en conservant leur couleur.

4. Conditions d’activation

    Une transition est franchissable si au moins un jeton de chaque couleur disponible est présent.

    La simulation teste toutes les transitions à chaque pas.

5. Effet de la transition

    Retirer le jeton de la place d’entrée.

    Ajouter le jeton (avec la même couleur) à la place de sortie.

6. Stratégie de simulation

    Simulation pas à pas.

    À chaque pas :

        Identifier les transitions franchissables pour chaque couleur de jeton.

        Franchir la transition en choisissant quel jeton coloré passer.

        Mettre à jour les places et afficher l’état.

7. Visualisation (optionnelle)

    Chaque place montre le nombre de jetons par couleur.

    Graphique avec couleurs distinctes :

        Rouge → véhicules prioritaires

        Jaune → véhicules standards

        Vert → véhicules ayant terminé

8. Étapes pour coder la simulation en Python

    Adapter la classe PetriNet pour stocker des listes de jetons colorés au lieu d’un simple nombre.

    Méthode fire(transition, couleur) : franchit la transition pour un jeton d’une couleur spécifique.

    Afficher l’état des places avec la répartition des couleurs.

    Boucle de simulation pas à pas en tenant compte des couleurs.

    Optionnel : visualisation du graphe avec NetworkX et couleurs des jetons.

9. Références

    Murata, T. (1989). Petri Nets: Properties, Analysis and Applications.

    Jensen, K. (1997). Coloured Petri Nets: Basic Concepts, Analysis Methods and Practical Use.

    Wooldridge, M. (2009). An Introduction to MultiAgent Systems.

    University of Waterloo. Waterloo Multi-Agent Traffic Dataset.

    Russell, S., & Norvig, P. (2020). Artificial Intelligence: A Modern Approach.
