import glob, json, sys, os, hashlib, uuid, logging, gzip

class fetch:

    def __init__( self, path, channels ):
        # Init logger
        self.logger = logging.getLogger('main.channels')
        self.logger.info('creating an instance of fetch')
        # Init TVHeadend root path
        self.tvhpath = path
        self.channels = channels
        self.merging = {}

    def fetch( self ):
        nb_logs_v3 = 0
        nb_logs_v4 = 0
        nb_logs_total = 0
        for lcn, channel in self.channels.items():
            self.merging[channel["svcname"]] = int(lcn)
            # print(channels[i]["svcname"].ljust(32), i)
        for dvr_log in glob.glob( self.tvhpath + '/var/dvr/log/*'):
            fd = open(dvr_log).read()
            jd = json.loads(fd)
            # détection des logs v3 ou v4
            # si pas d'attribut "channelname", alors ce sont des logs v3
            if 'channelname' not in jd:
                # print("Logs v3 identifiés")
                if jd['channel'] not in self.merging:
                    found = False
                    for svcname, lcn in self.merging.items():
                        if(svcname.lower() == jd['channel'].lower()):
                            self.merging[jd['channel']] = lcn
                            print("Ajout de la correspondance : " + jd['channel'] + " -> " + svcname)
                            found = True
                            break
                    if(not found):
                        print("Aucune correspondance trouvée pour la chaine : " + jd['channel'])
                        while(not found):
                            i = int(input("Merci de rentrer le numéro de la chaine correspondant à " + jd['channel'] + " : "))
                            if i not in self.channels:
                                print(i, type(i))
                                print("Saisie incorrecte, merci de rentrer une valeur correcte")
                            else:
                                self.merging[jd['channel']] = i
                                print("Ajout de la correspondance : " + jd['channel'] + " -> " + self.channels[i]["svcname"])
                                found = True
                nb_logs_v3 += 1
                nb_logs_total += 1
            #sinon, ce sont des logs v4
            elif 'channelname' in jd:
                # print("Logs v4 identifiés")
                if jd['channelname'] not in self.merging:
                    found = False
                    for svcname, lcn in self.merging.items():
                        if(svcname.lower() == jd['channelname'].lower()):
                            self.merging[jd['channelname']] = lcn
                            print("Ajout de la correspondance : " + jd['channelname'] + " -> " + svcname)
                            found = True
                            break
                    if(not found):
                        print("Aucune correspondance trouvée pour la chaine : " + jd['channelname'])
                        while(not found):
                            i = int(input("Merci de rentrer le numéro de la chaine correspondant à " + jd['channelname'] + " : "))
                            if i not in self.channels:
                                print(i, type(i))
                                print("Saisie incorrecte, merci de rentrer une valeur correcte")
                            else:
                                self.merging[jd['channelname']] = i
                                print("Ajout de la correspondance : " + jd['channelname'] + " -> " + self.channels[i]["svcname"])
                                found = True
                nb_logs_v4 += 1
                nb_logs_total += 1
            else:
                print("[!] error : impossible de lire la chaine pour:", os.path.basename(log_service))
        print("Fin de la procédure d'identification des chaines :")
        print("Nombre de logs v3 traités : ", nb_logs_v3)
        print("Nombre de logs v4 traités : ", nb_logs_v4)
        print("Nombre total de logs traités : ", nb_logs_total)

    def get( self ):
        return self.merging
