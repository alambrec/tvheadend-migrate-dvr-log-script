import glob, json, sys, os, hashlib, uuid, logging, gzip

class users:

    def __init__( self, path ):
        # Init logger
        self.logger = logging.getLogger('main.users')
        self.logger.info('creating an instance of users')
        # Init TVHeadend root path
        self.tvhpath = path
        self.users = {}

    def load( self ):
        for path_service in glob.glob( self.tvhpath + '/var/accesscontrol/*' ):
            fd = open(path_service).read()
            jd = json.loads(fd)
            if 'username' in jd:
                if jd["enabled"]:
                    self.users[ jd["index"] ] = {
                        "username" : jd["username"],
                        "config_name" : jd["dvr_config"]
                    }

    def get( self ):
        return self.users

    def print_users( self ):
        #A la fin du traitement, on affiche les correspondances effectuées
        print("\nListe des utilisateurs trouvés : \n")
        print("N°" + "\t" + "Nom utilisateurs".ljust(28) + "dvr_config".ljust(32))
        print("".ljust(64,"-"))
        for u_uuid, user in self.users.items():
            print(str(u_uuid) + "\t" + user["username"].ljust(28) + user["config_name"].ljust(32))
