#!/usr/bin/env python3
"""ssh_guard_simple.py - Détecteur de force brute SSH avec blocage iptables.

Usage :
    sudo python3 ssh_guard_simple.py --test   # affiche sans bloquer
    sudo python3 ssh_guard_simple.py          # bloque pour de vrai
"""
import os
import re
import subprocess
import sys
import time

LOG_FILE = "/var/log/auth.log"  
SEUIL = 5                   
WHITELIST = {"127.0.0.1", "192.168.75.1"}  
MODE_TEST = "--test" in sys.argv


MOTIF = re.compile(
    r"Failed password for (?:invalid user )?\S+ from (\d{1,3}(?:\.\d{1,3}){3})"
)

erreurs = {}      
deja_bloquees = set() 


def bloquer(ip):
    """Ajoute une règle iptables qui rejette tout le trafic de cette IP."""
    if MODE_TEST:
        print(f"[TEST] {ip} serait bloquée (aucune règle créée)")
        return
    try:
        subprocess.run(
            ["iptables", "-I", "INPUT", "-s", ip, "-j", "DROP"], check=True
        )
        print(f"[BLOCAGE] {ip} bloquée avec iptables")
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        print(f"[ERREUR] Impossible de bloquer {ip} : {e}")


def traiter(ligne):
    """Analyse une ligne du journal et agit si besoin."""
    resultat = MOTIF.search(ligne)
    if not resultat:
        return 
    ip = resultat.group(1)

    if ip in WHITELIST:
        print(f"[IGNORÉE] {ip} est dans la liste blanche")
        return
    if ip in deja_bloquees:
        return

    erreurs[ip] = erreurs.get(ip, 0) + 1
    print(f"[ERREUR] {ip} : {erreurs[ip]}/{SEUIL}")

    if erreurs[ip] >= SEUIL:
        print(f"[ALERTE] Trop d'erreurs pour {ip}")
        bloquer(ip)
        deja_bloquees.add(ip)


def main():
    if os.geteuid() != 0:
        sys.exit("Lance le programme avec sudo (droits administrateur requis).")

    mode = "TEST (aucun blocage)" if MODE_TEST else "RÉEL (blocage actif)"
    print(f"Surveillance de {LOG_FILE} - seuil {SEUIL} - mode {mode}")

    try:
        with open(LOG_FILE, "r", errors="ignore") as f:
            f.seek(0, os.SEEK_END) 
            while True:
                ligne = f.readline()
                if not ligne:
                    time.sleep(0.5) 
                    continue
                traiter(ligne)
    except FileNotFoundError:
        sys.exit(f"Fichier introuvable : {LOG_FILE}")
    except KeyboardInterrupt:
        print("\nArrêt du programme.")


if __name__ == "__main__":
    main()
