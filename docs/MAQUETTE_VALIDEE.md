# Maquette validée - RAG local

Cette maquette traduit le sujet du TP et le parcours défini dans le plan local. Elle décrit l'expérience attendue avant l'implémentation de la logique RAG.

La version interactive se trouve dans `docs/maquette.html`.

## Structure permanente

- En-tête : nom `RAG Local`, rappel de confidentialité et statut du service local.
- Barre latérale : import multiple PDF/TXT/MD, bouton d'indexation, choix du mode et bibliothèque documentaire.
- Zone principale : accueil, progression d'indexation ou conversation selon l'état courant.
- Sources : toujours reliées au résultat ou à la réponse correspondante.

## États validés

1. **Accueil vide** : trois étapes sont expliquées et le champ de question est désactivé.
2. **Fichiers sélectionnés** : nom, format, taille et validation sont visibles avant indexation.
3. **Indexation en cours** : extraction, validation, chunking, embeddings et stockage sont présentés dans l'ordre.
4. **Recherche sémantique** : les chunks bruts, fichiers, pages et niveaux de pertinence sont affichés sans appel au LLM.
5. **Assistant RAG** : une réponse fondée sur les documents est suivie des extraits réellement utilisés.
6. **Bibliothèque** : suppression, réindexation et vidage complet restent accessibles avec confirmation.

## Direction visuelle

- Interface calme et lisible, pensée comme un outil de travail documentaire.
- Accent vert pour signaler le fonctionnement local et les actions confirmées.
- Accent bleu pour la recherche et les sources.
- Hiérarchie claire entre question, réponse et preuves documentaires.
- Fonctionnement prévu en thème clair et sombre, avec adaptation aux fenêtres étroites.

## Règles fonctionnelles visibles

- Le bouton d'indexation reste inactif sans fichier valide.
- Le champ de question reste inactif tant que la bibliothèque est vide.
- Le mode actif est toujours explicite.
- Le mode Recherche sémantique n'affiche aucune réponse générée.
- Le mode RAG affiche une réponse honnête lorsque l'information manque.
- Aucun état vide ou en erreur ne laisse l'utilisateur sans prochaine action.
