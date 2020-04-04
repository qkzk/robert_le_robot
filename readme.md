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

Il faut d'abord autoriser la création de bots ainsi que [celles de webhook](https://docs.mattermost.com/developer/webhooks-outgoing.html),
qui permettent au bot de lire les messages d'un canal.

**Robert** répond à la fois aux messages privés et aux messages publics sur un canal.


## Superpouvoirs de Robert


* [x] **`!robert help`** (ou **aide**) : affiche ce message d'**aide**,
* [x] **`!robert date`** (ou **`heure`** ou **`aujourd'hui`**) : affiche **l'heure**,
* [x] **`!robert python {nom_d_objet}`** : affiche l'aide d'un objet **python**,
* [x] **`!robert latex {syntaxe latex}`** : tente d'évaluer une commande **latex**. J'arrondis la valeur après 4 décimales.
* [x] **`!robert travail [nombre]`** (**`nombre`** est optionnel) : affiche une brève description des derniers travaux déposés sur classroom.
* [ ] _`!robert assiduite \@personne`_ : affiche des infos sur le compte : dernière connexion etc. _PAS ENCORE DÉVELOPPÉ_.

Il reconnait aussi la syntaxe latex :

\`\`\`_latex_
{syntaxe latex}
\`\`\`
