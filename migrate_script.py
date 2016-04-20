#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import glob, json, sys, os, hashlib, uuid
from collections import OrderedDict, Counter

path = "your_installation_path_here"

def print_channels ( channels ):
    print("\nListe des chaines trouvées : \n")
    print("N° \t" + "Nom de la chaine".ljust(32) + "UUID")
    print("".ljust(72,"-"))
    for i in sorted(channels):
        print(channels[i]["lcn"], "\t" + channels[i]["svcname"].ljust(32) + channels[i]["uuid"])

def print_merge_channels ( merge_channels ):
    #A la fin du traitement, on affiche les correspondances effectuées
    print("\nCorrespondance des chaines trouvées dans les logs DVR : \n")
    print("Nom de la chaine".ljust(32) + "N°".rjust(4))
    print("".ljust(36,"-"))
    for j in merge_channels :
        print(j.ljust(32)+ str(merge_channels[j]).rjust(4))

def print_users( users ):
    #A la fin du traitement, on affiche les correspondances effectuées
    print("\nListe des utilisateurs trouvés : \n")
    print("N°".ljust(4) + "Nom utilisateurs".ljust(28) + "dvr_config".ljust(32))
    print("".ljust(64,"-"))
    for i in users:
        print(str(i).ljust(4) + users[i]["username"].ljust(28) + users[i]["config_name"].ljust(32))

def load_channels ( path ):
    channels = {}
    for path_service in glob.glob( path + '/var/input/dvb/networks/*/muxes/*/services/*' ):
        fd = open(path_service).read()
        jd = json.loads(fd)
        #print path_service
        if 'svcname' in jd:
            channels[ jd["lcn"] ] = {
                "lcn" : jd["lcn"],
                "svcname" : jd["svcname"],
                "uuid" : os.path.basename(path_service)
                }
    for path_channel in glob.glob( path + '/var/channel/config/*' ):
        fd = open(path_channel).read()
        jd = json.loads(fd)
        if 'name' in jd:
            for n_channel in channels:
                if(channels[n_channel]["uuid"] == jd["services"][0]):
                    print("Ajout merge :" + channels[n_channel]["svcname"] + " -> " + jd["name"])
                    channels[n_channel]["svcname"] = jd["name"]
                    break;

    return channels

def load_users( path ):
    users = {}
    for path_service in glob.glob( path + '/var/accesscontrol/*' ):
        fd = open(path_service).read()
        jd = json.loads(fd)
        if 'username' in jd:
            if jd["enabled"]:
                users[ jd["index"] ] = {
                    "username" : jd["username"],
                    "config_name" : jd["dvr_config"]
                }
    return users

def load_logs( path ):
    print("\nListe des logs trouvés : \n")
    nb_logs_v3 = 0
    nb_logs_v4 = 0
    logs = {}
    for path_service in glob.glob( path + '/var/dvr/log/*' ):
        fd = open(path_service).read()
        jd = json.loads(fd)
        if 'channelname' not in jd:
            i = 3
            nb_logs_v3 += 1
        else:
            i = 4
            nb_logs_v4 += 1
        logs[ os.path.basename(path_service) ] = {
            "pathname" : path_service,
            "version"  : i
        }
    # for i in logs:
    #     print(i.ljust(4) + logs[i]["pathname"].ljust(40), logs[i]["version"])
    print("Nombre de logs v3 traités : ", nb_logs_v3)
    print("Nombre de logs v4 traités : ", nb_logs_v4)
    print("Nombre total de logs traités : ", nb_logs_v3 + nb_logs_v4)
    return logs


def fetch_channels ( path, channels ):
    merge_channels = {}
    nb_logs_v3 = 0
    nb_logs_v4 = 0
    nb_logs_total = 0
    for i in channels :
        merge_channels[channels[i]["svcname"]] = i
        # print(channels[i]["svcname"].ljust(32), i)
    for dvr_log in glob.glob( path + '/var/dvr/log/*'):
        fd = open(dvr_log).read()
        jd = json.loads(fd)
        # détection des logs v3 ou v4
        # si pas d'attribut "channelname", alors ce sont des logs v3
        if 'channelname' not in jd:
            # print("Logs v3 identifiés")
            if jd['channel'] not in merge_channels:
                found = False
                for i in merge_channels:
                    if(i.lower() == jd['channel'].lower()):
                        merge_channels[jd['channel']] = merge_channels[i]
                        print("Ajout de la correspondance : " + jd['channel'] + " -> " + i)
                        found = True
                        break
                if(not found):
                    print("Aucune correspondance trouvée pour la chaine : " + jd['channel'])
                    while( not found ):
                        i = int(input("Merci de rentrer le numéro de la chaine correspondant à " + jd['channel'] + " : "))
                        if i not in channels:
                            print(i, type(i))
                            print("Saisie incorrecte, merci de rentrer une valeur correcte")
                        else:
                            merge_channels[jd['channel']] = i
                            print("Ajout de la correspondance : " + jd['channel'] + " -> " + channels[i]["svcname"])
                            found = True
            nb_logs_v3 += 1
            nb_logs_total += 1
        #sinon, ce sont des logs v4
        elif 'channelname' in jd:
            # print("Logs v4 identifiés")
            if jd['channelname'] not in merge_channels:
                found = False
                for i in merge_channels:
                    if(i.lower() == jd['channelname'].lower()):
                        merge_channels[jd['channelname']] = merge_channels[i]
                        print("Ajout de la correspondance : " + jd['channelname'] + " -> " + i)
                        found = True
                        break
                if(not found):
                    print("Aucune correspondance trouvée pour la chaine : " + jd['channelname'])
                    while( not found ):
                        i = int(input("Merci de rentrer le numéro de la chaine correspondant à " + jd['channelname'] + " : "))
                        if i not in channels:
                            print(i, type(i))
                            print("Saisie incorrecte, merci de rentrer une valeur correcte")
                        else:
                            merge_channels[jd['channelname']] = i
                            print("Ajout de la correspondance : " + jd['channelname'] + " -> " + channels[i]["svcname"])
                            found = True
            nb_logs_v4 += 1
            nb_logs_total += 1
        else:
            print("[!] error : impossible de lire la chaine pour:", os.path.basename(log_service))
    print("Fin de la procédure d'identification des chaines :")
    print("Nombre de logs v3 traités : ", nb_logs_v3)
    print("Nombre de logs v4 traités : ", nb_logs_v4)
    print("Nombre total de logs traités : ", nb_logs_total)
    return merge_channels

def upgrade_logs( path, merge_channels, channels, users, logs ):
    user_default = False
    print("Début de la mise à jour des logs :")
    print("Merci d'indiquer la configuration utilisateur associée au logs")
    while( not user_default ):
        i = int(input("Merci de rentrer le numéro de l'utilisateur à : "))
        if i not in users:
            print(i, type(i))
            print("Saisie incorrecte, merci de rentrer une valeur correcte")
        else:
            print("Utilisateur " + users[i]['username'] + " sélectionné avec config_name : " + users[i]['config_name'])
            print("Début de la mise à jour des logs")
            user_default = True

    for log_name in logs:
        # structure temporaire de chaque logs
        temp = OrderedDict([
            ("start", 0),
            ("start_extra", 15),
            ("stop", 0),
            ("stop_extra", 15),
            ("channel", ""),
            ("channelname", ""),
            ("title", {}),
            ("subtitle", {}),
            ("description", {}),
            ("pri", 2),
            ("retention", 0),
            ("container", -1),
            ("config_name", ""),
            ("owner", ""),
            ("creator", ""),
            ("errorcode", 0),
            ("errors", 0),
            ("data_errors", 0),
            ("dvb_eid", 0),
            ("noresched", False),
            ("autorec", ""),
            ("timerec", ""),
            ("content_type", 1),
            ("broadcast", 1101),
            ("filename", "test_path")
        ])
        # Paramétrage de l'utilisateur par défaut
        temp["owner"] = users[i]["username"]
        temp["creator"] = users[i]["username"]
        temp["config_name"] = users[i]["config_name"]
        # ouverture des logs
        log_fd = open(logs[log_name]["pathname"]).read()
        log_jd = json.loads(log_fd)

        if(logs[log_name]["version"] == 3):
            # Migrate filename
            if 'filename' in log_jd:
                temp["filename"] = log_jd["filename"]
            else:
                print("[!] error : impossible le pathname pour:", log_name)
                exit(0)
            # Migrate channel
            if 'channel' in log_jd:
                temp["channelname"] = channels[merge_channels[log_jd["channel"]]]["svcname"]
                temp["channel"] = channels[merge_channels[log_jd["channel"]]]["uuid"]
            else:
                print("[i] info : impossible de lire la chaine pour :", log_name)
        else:
            if 'files' in log_jd:
                temp["filename"] = log_jd["files"][0]["filename"]
            elif 'filename' in log_jd:
                temp["filename"] = log_jd["filename"]
            else:
                print("[!] error : impossible le pathname pour:", log_name)
                exit(0)
            # Migrate channel
            if 'channelname' in log_jd:
                temp["channelname"] = channels[merge_channels[log_jd["channelname"]]]["svcname"]
                temp["channel"] = channels[merge_channels[log_jd["channelname"]]]["uuid"]
            else:
                print("[i] info : impossible de lire la chaine pour :", log_name)
        # Migrate timerec
        if 'start' in log_jd:
            temp["start"] = log_jd["start"]
        else:
            print("[i] info : impossible de lire le debut :", log_name)
            exit(0)
        if 'stop' in log_jd:
            temp["stop"] = log_jd["stop"]
        else:
            print("[i] info : impossible de lire la fin :", log_name)
            exit(0)
        # Migrate title
        if 'title' in log_jd:
            for lang in log_jd["title"]:
                temp["title"]["fre"] = log_jd["title"][lang]
        else:
            temp["title"] = {}
            print("Erreur : impossible de lire le titre :", log_name)

        # Migrate subtitle
        if 'subtitle' in log_jd:
            temp["subtitle"] = log_jd["subtitle"]
        else:
            del temp["subtitle"]
            print("[i] info : impossible de lire le sous-titre :", log_name)
        # Migrate description
        if 'description' in log_jd:
            # temp["description"] = log_jd["description"]
            for lang in log_jd["description"]:
                temp["description"]["fre"] = log_jd["description"][lang]
        else:
            temp["description"] = {}
            print("[i] info : impossible de lire la description :", log_name)
        # Migrate content_type
        if 'contenttype' in log_jd:
            temp["content_type"] = log_jd["contenttype"]
        else:
            print("[i] info : impossible de lire le type de l'enregistrement :", log_name)

        # generate hash MD5 namefile
        namefile = uuid.uuid4().hex
        print(log_name, namefile)
        # Open a file for writing
        out_file = open(path + "/var/test/" + namefile ,"w")

        # Save the dictionary into this file
        # (the 'indent=4' is optional, but makes it more readable)
        json.dump(temp, out_file, indent=2, ensure_ascii=False)

        # Close the file descriptor
        out_file.close()


logs = load_logs(path)
channels = load_channels(path)
print_channels(channels)
merge_channels = fetch_channels(path, channels)
print_merge_channels(merge_channels)
users = load_users(path)
print_users(users)
upgrade_logs(path, merge_channels, channels, users, logs)
