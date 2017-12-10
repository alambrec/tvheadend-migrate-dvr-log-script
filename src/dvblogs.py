import glob, json, sys, os, hashlib, uuid, logging, gzip

class dvblogs:

    def __init__( self, s_path, d_path, d_rev, channels, mergings, users):
        # Init logger
        self.logger = logging.getLogger('main.dvblogs')
        self.logger.info('creating an instance of dvblogs')
        # Init src TVHeadend root path
        self.s_tvhpath = s_path
        # Init dest TVHeadend root path
        self.d_tvhpath = d_path
        # Init revision of TVHeadend destination to format properly dvb logs
        self.d_tvhrev = d_rev
        # Init dict of new TVHeadend config
        self.channels = channels
        self.mergings = mergings
        self.users = users
        self.default_user = 0
        self.logs = {}

    def load_logs( self ):
        print("\n> Liste des logs trouvés : \n")
        nb_logs_v3 = 0
        nb_logs_v4 = 0
        for log_path in glob.glob( self.s_tvhpath + '/var/dvr/log/*' ):
            fd = open(log_path).read()
            jd = json.loads(fd)
            if 'channelname' not in jd:
                i = 3
                nb_logs_v3 += 1
            else:
                i = 4
                nb_logs_v4 += 1
            self.logs[ os.path.basename(log_path) ] = {
                "pathname" : log_path,
                "version"  : i
            }
        # for i in logs:
        #     print(i.ljust(4) + logs[i]["pathname"].ljust(40), logs[i]["version"])
        print("Nombre de logs v3 traités : ", nb_logs_v3)
        print("Nombre de logs v4 traités : ", nb_logs_v4)
        print("Nombre total de logs traités : ", nb_logs_v3 + nb_logs_v4)

    def ask_default_user( self ):
        confirm_user = False
        print("> Choix de l'utilisateur par défaut pour les logs")
        print("Merci d'indiquer la configuration utilisateur associée au logs")
        while( not confirm_user ):
            i = int(input("Merci de rentrer le numéro de l'utilisateur à : "))
            if i not in self.users:
                print(i, type(i))
                print("Saisie incorrecte, merci de rentrer une valeur correcte")
            else:
                self.default_user = i
                print("Utilisateur " + self.users[self.default_user]['username'] + " sélectionné avec config_name : " + self.users[self.default_user]['config_name'])
                confirm_user = True

    def upgrade_logs( self ):
        print("> Début de la mise à jour des logs :")
        for l_uuid, log in self.logs:
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
            temp["owner"] = self.users[self.default_user]["username"]
            temp["creator"] = self.users[self.default_user]["username"]
            temp["config_name"] = self.users[self.default_user]["config_name"]
            # ouverture des logs
            log_fd = open(log["pathname"]).read()
            log_jd = json.loads(log_fd)

            if(log["version"] == 3):
                # Migrate filename
                if 'filename' in log_jd:
                    temp["filename"] = log_jd["filename"]
                else:
                    self.logger.error("unable to find filename for %s", log['pathname'])
                    continue
                # Migrate channel
                if 'channel' in log_jd:
                    temp["channelname"] = self.channels[self.mergings[log_jd["channel"]]]["svcname"]
                    temp["channel"] = self.channels[self.mergings[log_jd["channel"]]]["uuid"]
                else:
                    self.logger.warning("unable to find channel for %s", log['pathname'])
            else:
                if 'files' in log_jd:
                    temp["filename"] = log_jd["files"][0]["filename"]
                elif 'filename' in log_jd:
                    temp["filename"] = log_jd["filename"]
                else:
                    self.logger.error("unable to find filename or files for %s", log['pathname'])
                    continue
                # Migrate channel
                if 'channelname' in log_jd:
                    temp["channelname"] = channels[merge_channels[log_jd["channelname"]]]["svcname"]
                    temp["channel"] = channels[merge_channels[log_jd["channelname"]]]["uuid"]
                else:
                    self.logger.warning("unable to find channelname for %s", log['pathname'])
            # Migrate timerec
            if 'start' in log_jd:
                temp["start"] = log_jd["start"]
            else:
                self.logger.error("unable to find start for %s", log['pathname'])
                continue
            if 'stop' in log_jd:
                temp["stop"] = log_jd["stop"]
            else:
                self.logger.error("unable to find stop for %s", log['pathname'])
                continue
            # Migrate title
            if 'title' in log_jd:
                for lang in log_jd["title"]:
                    temp["title"]["fre"] = log_jd["title"][lang]
            else:
                temp["title"] = {}
                self.logger.error("unable to find title for %s", log['pathname'])
                continue

            # Migrate subtitle
            if 'subtitle' in log_jd:
                temp["subtitle"] = log_jd["subtitle"]
            else:
                del temp["subtitle"]
                self.logger.debug("unable to find subtitle for %s", log['pathname'])
            # Migrate description
            if 'description' in log_jd:
                # temp["description"] = log_jd["description"]
                for lang in log_jd["description"]:
                    temp["description"]["fre"] = log_jd["description"][lang]
            else:
                temp["description"] = {}
                self.logger.warning("unable to find description for %s", log['pathname'])
            # Migrate content_type
            if 'contenttype' in log_jd:
                temp["content_type"] = log_jd["contenttype"]
            else:
                self.logger.debug("unable to find contenttype for %s", log['pathname'])

            # save migrated log
            self.log(temp)

    def save_log( self, content ):
        filename = uuid.uuid4().hex
        filepath = d_tvhpath + "/var/dvr/log/" + filename
        while os.path.isfile(filepath):
            self.logger.error("file %s already exist !", filepath)
            filepath = d_tvhpath + "/var/dvr/log/" + filename
        # Open a file for writing
        fd = open(filepath, 'w')

        # Save the dictionary into this file
        # (the 'indent=4' is optional, but makes it more readable)
        json.dump(content, fd, indent=2, ensure_ascii=False)

        # Close the file descriptor
        fd.close()
