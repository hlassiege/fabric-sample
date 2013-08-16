fabric-sample
=============

Ce repository contient un ensemble de scripts Fabric destiné à illustrer le billet http://www.eventuallycoding.com/index.php/fabric-moi-un-cluster/

Ils devraient être fonctionnels sauf bourde de dernière minute et devraient permettre d'installer un cluster ES, MongoDB et Cassandra sur des machines Debian.

Pour cela :

* Editer le fichier fabfile.py et remplacer 'db': ['root@192.168.0.1', 'root@192.168.0.2', 'root@192.168.0.3'] par la liste de vos machines
* Lancer les prérequis systèmes : 
    fab init_envs
* Lancer l'install elasticsearch
    fab elasticsearch.install
* Lancer l'install MongoDB
    fab mongodb.install
* Lancer l'install Cassandra
    fab cassandra.install



