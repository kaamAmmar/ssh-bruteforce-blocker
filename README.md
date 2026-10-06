# ssh-bruteforce-blocker

Petit détecteur de force brute SSH écrit en Python. Il surveille `/var/log/auth.log`, compte les erreurs de mot de passe par adresse IP et bloque l'IP avec `iptables` quand un seuil est atteint (5 par défaut).

Projet pédagogique : construire soi-même un outil équivalent à Fail2ban pour comprendre son fonctionnement.

> **Avertissement légal** : à tester uniquement sur vos propres machines, dans un réseau isolé (laboratoire de machines virtuelles). Ne jamais lancer d'attaque sur un système qui ne vous appartient pas.

## Fonctionnalités

- Lecture du journal en continu (nouvelles lignes uniquement)
- Détection des lignes `Failed password` et extraction de l'IP
- Compteur d'erreurs par IP
- Blocage avec `iptables` au seuil
- Liste blanche (IP jamais bloquées)
- Mode test (affiche sans bloquer)
- Pas de double blocage de la même IP

## Limites (version 1)

- Pas de déblocage automatique (manuel ou au redémarrage)
- Pas de détection des erreurs par clé SSH
- IPv4 uniquement
- Pas d'alerte (prévu en amélioration)
- Les règles iptables sont perdues au redémarrage
- Le compteur n'a pas de fenêtre de temps

## Prérequis

- Ubuntu ou Debian avec `openssh-server`
- Python 3 (aucune bibliothèque externe)
- Droits administrateur (`sudo`)

## Installation

```bash
git clone https://github.com/kaamAmmar/ssh-bruteforce-blocker.git
cd ssh-bruteforce-blocker
```

Modifier la liste blanche dans `ssh_guard.py` (variable `WHITELIST`) pour y mettre **votre propre IP** avant tout test réel.

## Utilisation

```bash
# Mode test : affiche sans bloquer
sudo python3 ssh_guard.py --test

# Mode réel : bloque avec iptables
sudo python3 ssh_guard.py
```

Vérifier les blocages et débloquer :

```bash
sudo iptables -L INPUT -n
sudo iptables -D INPUT -s IP -j DROP
```

## Fonctionnement

```
Journal SSH -> Détection d'erreur -> Compteur par IP -> Seuil atteint ? -> Blocage iptables
```

## Laboratoire de test

- Victime : Ubuntu (openssh-server)
- Attaquante : Kali Linux
- Réseau privé Host-only (VMware), isolé d'Internet pendant les tests

## Tests

| N° | Action | Résultat attendu | Résultat obtenu |
| --- | --- | --- | --- |
| T1 | Ajouter 1 fausse ligne d'erreur (`logger`) | Compteur 1/5 | |
| T2 | Ajouter 5 fausses lignes de la même IP | Message « Trop d'erreurs » | |
| T3 | Connexion réussie | Aucune réaction | |
| T4 | Erreurs depuis une IP en liste blanche | Erreurs ignorées | |
| T5 | Seuil atteint en mode test | Message, aucune règle iptables | |
| T6 | Mode réel, 5 erreurs depuis Kali | Règle DROP visible, SSH impossible | |
| T7 | Suppression manuelle de la règle | Kali peut se reconnecter | |

Captures d'écran : dossier `screenshots/`.

## Améliorations possibles

1. Alerte Telegram lors d'un blocage
2. Déblocage automatique après un délai
3. Fenêtre de temps (5 erreurs en 2 minutes)
4. Sauvegarde des blocages pour survivre au redémarrage
5. Support IPv6 et nftables
6. Envoi des événements vers Wazuh

## Auteur

Ammar Kaam - [GitHub](https://github.com/kaamAmmar) - [LinkedIn](https://linkedin.com/in/ammar-kaam)
