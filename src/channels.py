import glob, json, sys, os, hashlib, uuid, logging, gzip

class channels:

    def __init__( self, path, networks ):
        # Init logger
        self.logger = logging.getLogger('main.tools')
        self.logger.info('creating an instance of tools')
        # Set filepath
        self.tvhpath = path
        self.networks = networks
        self.services = {}
        self.channels = {}

    def load_services( self ):
        for n_uuid, network in self.networks['networks'].items():
            for m_uuid, muxe in network['muxes'].items():
                for s_uuid, service in muxe['config']['services'].items():
                    if 'svcname' in service:
                        self.services[s_uuid] = {
                            'lcn' : service['lcn'],
                            'svcname' : service['svcname']
                        }
                    else:
                        self.logger.debug('no channel for service %s', s_uuid)

    def load_channels( self ):
        for channel_path in glob.glob( self.tvhpath + '/var/channel/config/*' ):
            fd = open(channel_path).read()
            jd = json.loads(fd)
            # channel_uuid
            c_uuid = os.path.basename(channel_path)
            if 'services' in jd:
                s_uuid = jd['services'][0]
                if s_uuid in self.services:
                    lcn = self.services[s_uuid]['lcn']
                    svcname = self.services[s_uuid]['svcname']
                    self.channels[lcn] = {
                        'svcname' : svcname,
                        'uuid' : c_uuid
                    }

    def get_services( self ):
        return self.services

    def get_channels( self ):
        return self.channels

    def print_services ( self ):
        print("\n> List of found services : \n")
        print("LCN \t" + "Service Name".ljust(32) + "UUID".ljust(32))
        print("".ljust(72,"-"))
        for uuid, service in self.services.items():
            print(str(service["lcn"]) + "\t" + service["svcname"].ljust(32) + str(uuid))

    def print_channels ( self ):
        print("\n> List of found channels : \n")
        print("N° \t" + "Channel name".ljust(32) + "UUID")
        print("".ljust(72,"-"))
        for lcn, channel in sorted(self.channels.items()):
            print(str(lcn) + "\t" + channel["svcname"].ljust(32) + channel["uuid"])
