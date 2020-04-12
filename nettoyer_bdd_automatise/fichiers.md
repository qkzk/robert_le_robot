# Nettoyer la bdd de mattermost

La version gratuite (team) de mattermost ne propose aucune option
de respect du rgbd. Tout est conservé...
Effacer un post via l'api ne l'efface pas complètement.

Les commandes en ligne ne font pas ça non plus.

Donc c'est chiant.

Résultat, les données s'accumulent.

## Objectif

Nettoyer régulièrement les fichiers et les posts.

Il y a 3/4 trucs à faire :

1. effacer les posts dans la bdd (impossible d'utiliser l'api)
2. effacer les fileinfo dans la bdd (pareil)
3. effacer les fichiers réellement

Ils sont tous situés dans

~~~bash
<mattermost>/volumes/app/mattermost/data/
~~~

Chaque création de fichier engendre la création d'un dossier du genre :

~~~bash
20200412/teams/noteam/channels/68p83xyq97gqxxxdw8yg1ucoec/users/k77ic47pwinkudkn5pgxpkcznr/zog4sqp5o7fp5xky7t3hhd357c/
~~~

La racine est la date.

Donc facile : on efface tous les dossiers dont la date est trop ancienne.

## Plan retenu

1. script qui efface directement les fileinfo createat < tel timestamp

  **DONE**

2. effacer les dossiers en question avec Python

  **DONE**


---

## Plan 2 -- echec total

2. effacer tous les dossiers dont le nom est inférieur à tel date

Problème : je n'arrive pas à passer le nom du dossier comme paramètre
donc ça devient tres chiant.

**il faut sudo ce truc**

~~~bash
c='20200412/' # utiliser en parametre $1
cd /home/quentin/mattermost/mattermost-docker/volumes/app/mattermost/data/
for d in */ ; do
    # loop trough every directory
    echo "$d"
    if [[ $d < $c ]] # s'il est de nom plus vieux que...
    then
      echo "$d < $c will be deleted" # pour afficher
      rm -rf $d # remplacer par delete
    fi
done
cd -
~~~

## Plan 3 -- pas cool et risqué.

si les infos d'un fichier sont modifiées il ne sera jamais effacé

1. script qui efface directement les fileinfo createat < tel timestamp

    DONE

2. effacer recursivement tous les **fichiers** plus vieux que tel timestamp

    https://tecadmin.net/delete-files-older-x-days/
    ```bash
    $ find /opt/backup -type f -mtime +30 -exec rm -f {} \;
    ```
3. effacer recursivement les dossiers vides


## infos

1. les fichiers sont dans : /home/quentin/mattermost/mattermost-docker/volumes/app/mattermost/data/

2. de là ça donne :

  20200412/teams/noteam/channels/68p83xyq97gqxxxdw8yg1ucoec/users/k77ic47pwinkudkn5pgxpkcznr/zog4sqp5o7fp5xky7t3hhd357c/kb.png
  20200412/teams/noteam/channels/68p83xyq97gqxxxdw8yg1ucoec/users/k77ic47pwinkudkn5pgxpkcznr/zog4sqp5o7fp5xky7t3hhd357c/kb_thumb.jpg
  20200412/teams/noteam/channels/68p83xyq97gqxxxdw8yg1ucoec/users/k77ic47pwinkudkn5pgxpkcznr/zog4sqp5o7fp5xky7t3hhd357c/kb_preview.jpg



             id             |         creatorid          |           postid           |   createat    |   updateat    | deleteat |                                                             path                                                             |                                                           thumbnailpath                                                            |                                                             previewpath                                                              |  name  | extension | size | mimetype  | width | height | haspreviewimage
----------------------------+----------------------------+----------------------------+---------------+---------------+----------+------------------------------------------------------------------------------------------------------------------------------+------------------------------------------------------------------------------------------------------------------------------------+--------------------------------------------------------------------------------------------------------------------------------------+--------+-----------+------+-----------+-------+--------+-----------------
 zog4sqp5o7fp5xky7t3hhd357c | k77ic47pwinkudkn5pgxpkcznr | jkyh7air4iy8zxtimpn4wup3cw | 1586701869458 | 1586701869458 |        0 | 20200412/teams/noteam/channels/68p83xyq97gqxxxdw8yg1ucoec/users/k77ic47pwinkudkn5pgxpkcznr/zog4sqp5o7fp5xky7t3hhd357c/kb.png | 20200412/teams/noteam/channels/68p83xyq97gqxxxdw8yg1ucoec/users/k77ic47pwinkudkn5pgxpkcznr/zog4sqp5o7fp5xky7t3hhd357c/kb_thumb.jpg | 20200412/teams/noteam/channels/68p83xyq97gqxxxdw8yg1ucoec/users/k77ic47pwinkudkn5pgxpkcznr/zog4sqp5o7fp5xky7t3hhd357c/kb_preview.jpg | kb.png | png       |  972 | image/png |    96 |     96 | t


plan pour effacer les fichiers :

récupérer la liste des fichiers

* ~~api : peut-être plus pratique~~ :

  impossible de connaitre les posts qui ont des fichiers
  impossible d'avoir les adresses des fichiers il faudrait les reconstituer (faisable)

* bd : pb de la pagination qui est incontournable donc il faut 'limit autant' et faire en lot

  bien relou

  **plus pratique les dates unix**
