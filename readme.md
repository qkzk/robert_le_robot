---
  title: Robert le robot
  author: qkzk
  date: 2020/04/04
---

# Robert le robot

## Présentation

**Robert le robot** est un bot en python pour [Mattermost](https://mattermost.org).
Une fois la configuration effectuée (à la main !) il peut répondre à différentes commandes.

Librairies :

* [mattermostdriver](https://github.com/Vaelor/python-mattermost-driver) permet de contrôler le bot et de créer des webhooks
* [pyaml](https://pypi.org/project/PyYAML/) pour lire les fichiers de configuration
* [google classroom](https://developers.google.com/classroom/quickstart/python)
* [sympy](https://www.sympy.org/en/index.html) pour évaluer les commandes latex. Ce parser nécessite aussi [antlr4-python3-runtime](https://pypi.org/project/antlr4-python3-runtime/)

## Créer un bot pour mattermost

L'aide de Mattermost [ici](https://docs.mattermost.com/developer/bot-accounts.html)  et [là](https://docs.mattermost.com/developer/bot-accounts.html#bot-account-creation) explique comment créer un bot.
Il faut d'abord autoriser la création de bots ainsi que celles de webhook,
qui permettent au bot de lire les messages d'un canal.

Robert répond à la fois aux messages privés et aux messages publics sur un canal.



et d'autres trucs marrants (mais faisables)
* python eval bot
  * [+] cool, pratique pour vérifier rapidement
  * [-] dangereux, pénible à programmer (mais existe déjà !)
* classroom api :
  * dernier devoirs
  * résumé de tous les devoirs
  * devoirs en cours
  * créer un lien vers les documents facilement accessible !
  * https://stackoverflow.com/questions/56327781/how-can-i-use-a-google-classroom-api-on-a-website-i-am-making-to-access-specific
  * [+] pratique
  * [-] n'existe sûrement pas

* Assiduité
  * dernières visites, fréquence, nb de visite, nb de posts
  * [+] utile
  * [-] un peu flippant, faut vraiment limiter l'usage

## Token

Votre compte de bot qkzkbot a été créé avec succès. Veuillez utiliser un des jetons d'accès suivants pour connecter le bot. Consultez notre documentation pour en savoir plus.

Jeton :

Veuillez vous assurer d'ajouter ce compte utilisateur de bot aux équipes et canaux avec lesquels vous voulez voir ce bot interagir. Veuillez vous référer à notre documentation pour en savoir plus.
