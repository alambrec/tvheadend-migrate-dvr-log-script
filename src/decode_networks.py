import glob, json, sys, os, hashlib, uuid, logging, gzip

#logging.basicConfig(stream=sys.stdout, level=logging.DEBUG, format='%(asctime)s|%(levelname)s|%(funcName)s: %(message)s', datefmt='%H:%M:%S')

PATH = "./samples/muxes_4.2.sample"

class htsmsg_binary:

    def __init__( self, path ):
        # Init logger
        self.logger = logging.getLogger('main.htsmsg_binary')
        self.logger.info('creating an instance of htsmsg_binary')
        # Set constants to identify type of data
        self.HMF_MAP=1
        self.HMF_S64=2
        self.HMF_STR=3
        self.HMF_BIN=4
        self.HMF_LIST=5
        self.HMF_DBL=6
        self.HMF_BOOL=7
        # Set filepath
        self.tvhpath = path

    def BytesToLong( self, rawBytes ):
        if isinstance(rawBytes, bytearray):
            # self.logger.debug("bytearray type identified")
            bytesArray = rawBytes
        elif isinstance(rawBytes, bytes):
            # self.logger.debug("bytes type identified")
            bytesArray = bytearray(rawBytes)
        else:
            self.logger.warning("Incorrect data type")
            return -1
        length = len(bytesArray)
        if(length > 4):
            self.logger.warning("Oversize data, print to hex")
            if(bytes(bytesArray) == b'\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF'):
                return -1
            else:
                return self.BytesToHex(bytesArray)
        else:
            return int.from_bytes(bytesArray, byteorder='big')



    def BytesToHex( self, rawBytes ):
        hexStr = "0x"
        if isinstance(rawBytes, bytearray):
            # self.logger.debug("bytearray type identified")
            bytesArray = rawBytes
        elif isinstance(rawBytes, bytes):
            # self.logger.debug("bytes type identified")
            bytesArray = bytearray(rawBytes)
        else:
            self.logger.warning("Incorrect data type")
            return ""
        length = len(bytesArray)
        if(length > 0):
            i = 0
            while(i < length):
                hexStr = hexStr + "{:02X}".format(bytesArray[i])
                i = i+1
        else:
            hexStr = "null"
        return hexStr

    def BytesToStr( self, rawBytes ):
        return rawBytes.decode('utf-8')


    def htsmsg_binary_des1( self, rawBytes ):
        if isinstance(rawBytes, bytearray):
            logging.debug("> bytearray type identified")
        else:
            self.logger.debug("> input data must be a bytearray")

        returnData = []
        length = len(rawBytes)
        self.logger.debug("> length: %s", length)

        while(length > 5):
            self.logger.debug(">> new data")
            dType = rawBytes[0]
            self.logger.debug(">> %s %s", "dType:".ljust(20), dType)
            dNameLen = rawBytes[1]
            self.logger.debug(">> %s %i", "dNameLen:".ljust(20),  dNameLen)
            dDataLen = int.from_bytes(rawBytes[2:6], byteorder='big')
            self.logger.debug(">> %s %i", "dDataLen:".ljust(20),  dDataLen)


            rawBytes = rawBytes[6:]
            length = length-6

            if(length < dNameLen+dDataLen):
                self.logger.error("length < dNameLen+dDataLen")
                return returnData

            if(dNameLen == 0):
                if(dType == self.HMF_MAP):
                    self.logger.debug(">> %s %s", "dTypeIdentified:".ljust(20),  "HMF_MAP")
                    hmf_map = self.htsmsg_binary_des0(rawBytes[0:dDataLen])
                    returnData.append(hmf_map)
                elif(dType == self.HMF_LIST):
                    self.logger.error(">> %s %s", "dTypeIdentified:".ljust(20),  "HMF_LIST")
                    # if(dDataLen > 0):
                    #     hmf_list = htsmsg_binary_des0(rawBytes[0:dDataLen])
                    # else:
                    #     self.logger.debug(">> %s %s", "hmf_list:".ljust(20),  "null")
                    return returnData
                else:
                    self.logger.error(">> Unable to identity dType")
                    return returnData
            else:
                self.logger.error(">> dDataName is not null")
                return returnData

            rawBytes = rawBytes[dDataLen:]
            length = length-dDataLen

        return returnData

    def htsmsg_binary_des0( self, rawBytes ):
        if isinstance(rawBytes, bytearray):
            self.logger.debug("> bytearray type identified")
        else:
            self.logger.debug("> input data must be a bytearray")

        returnData = {}
        length = len(rawBytes)
        self.logger.debug("> length: %s", length)

        while(length > 5):
            self.logger.debug(">> new data")
            dType = rawBytes[0]
            self.logger.debug(">> %s %s", "dType:".ljust(20), dType)
            dNameLen = rawBytes[1]
            self.logger.debug(">> %s %i", "dNameLen:".ljust(20),  dNameLen)
            dDataLen = int.from_bytes(rawBytes[2:6], byteorder='big')
            self.logger.debug(">> %s %i", "dDataLen:".ljust(20),  dDataLen)


            rawBytes = rawBytes[6:]
            length = length-6

            if(length < dNameLen+dDataLen):
                self.logger.error("length < dNameLen+dDataLen")
                return returnData

            if(dNameLen > 0):
                dataName = self.BytesToStr(rawBytes[0:dNameLen])
                self.logger.debug(">> %s %s", "dDataName:".ljust(20),  dataName)
                rawBytes = rawBytes[dNameLen:]
                length = length-dNameLen

                if(dType == self.HMF_STR):
                    hmf_str = self.BytesToStr(rawBytes[0:dDataLen])
                    self.logger.debug(">> %s %s", "dTypeIdentified:".ljust(20),  "HMF_STR")
                    self.logger.debug(">> %s %s", "hmf_str:".ljust(20),  hmf_str)
                    returnData[dataName] = hmf_str
                elif(dType == self.HMF_BIN):
                    hmf_bin = self.BytesToHex(rawBytes[0:dDataLen])
                    self.logger.debug(">> %s %s", "dTypeIdentified:".ljust(20),  "HMF_BIN")
                    self.logger.debug(">> %s %s", "hmf_bin:".ljust(20),  hmf_bin)
                    returnData[dataName] = hmf_bin
                elif(dType == self.HMF_S64):
                    hmf_s64 = self.BytesToLong(rawBytes[0:dDataLen])
                    self.logger.debug(">> %s %s", "dTypeIdentified:".ljust(20),  "HMF_S64")
                    if isinstance(hmf_s64, int):
                        self.logger.debug(">> %s %i", "hmf_s64:".ljust(20),  hmf_s64)
                    else:
                        self.logger.debug(">> %s %s", "hmf_s64:".ljust(20),  hmf_s64)
                    returnData[dataName] = hmf_s64
                elif(dType == self.HMF_MAP):
                    self.logger.debug(">> %s %s", "dTypeIdentified:".ljust(20),  "HMF_MAP")
                    hmf_map = self.htsmsg_binary_des0(rawBytes[0:dDataLen])
                    returnData[dataName] = hmf_map
                elif(dType == self.HMF_LIST):
                    self.logger.debug(">> %s %s", "dTypeIdentified:".ljust(20),  "HMF_LIST")
                    if(dDataLen > 0):
                        hmf_list = self.htsmsg_binary_des1(rawBytes[0:dDataLen])
                    else:
                        self.logger.debug(">> %s %s", "hmf_list:".ljust(20),  "null")
                        hmf_list = []
                    returnData[dataName] = hmf_list
                elif(dType == self.HMF_BOOL):
                    hmf_bool = rawBytes[0]
                    self.logger.debug(">> %s %s", "dTypeIdentified:".ljust(20),  "HMF_BOOL")
                    self.logger.debug(">> %s %i", "hmf_bool:".ljust(20),  hmf_bool)
                    returnData[dataName] = hmf_bool
                else:
                    self.logger.debug(">> Unable to identity dType")

            else:
                self.logger.debug(">> %s %s", "dDataName:".ljust(20),  "null")

            rawBytes = rawBytes[dDataLen:]
            length = length-dDataLen

        return returnData


    def load_dvb( self ):
        dvb = {}
        dvb["networks"] = self.load_networks(self.tvhpath + '/var/input/dvb/networks')
        return dvb

    def load_networks( self, networkspath ):
        networks = {}
        for network_path in glob.glob( networkspath + '/*' ):
            if os.path.isdir(network_path):
                network_uuid = os.path.basename(network_path)
                fd = open(network_path + '/config').read()
                jd = json.loads(fd)
                networks[network_uuid] = {}
                networks[network_uuid]["config"] = jd
                networks[network_uuid]["muxes"] = self.load_muxes(network_path + '/muxes')
            else:
                self.logger.debug(" %s is not a directory", network_path)
        return networks

    def load_muxes( self, muxespath ):
        muxes = {}
        for muxe_path in glob.glob( muxespath + '/*' ):
            muxe_uuid = os.path.basename(muxe_path)
            if os.path.isfile(muxe_path):
                fd = open(muxe_path, "rb")
                first_two_bytes = fd.read(2)
                self.logger.debug("first_two_bytes:\t %s", self.BytesToHex(first_two_bytes))
                if(first_two_bytes == b'\xFF\xFF'):
                    self.logger.debug("ok")
                    header_control = bytearray(fd.read(6))
                    self.logger.debug("header_control:\t %s", self.BytesToStr(header_control))
                    header_size = int.from_bytes(fd.read(4), byteorder='big')
                    if(header_size <= (10*1024*1024)):
                        self.logger.debug("header_size is ok: %i", header_size)
                        header_data = fd.read()
                        uncompressed_data = gzip.decompress(header_data)
                        muxes[muxe_uuid] = self.htsmsg_binary_des0(bytearray(uncompressed_data))
                    else:
                        self.logger.error("header_size is not oversize: %i", header_size)
                else:
                    self.logger.debug("Incorrect start bytes of files")
            else:
                self.logger.debug(" %s is not a file", muxe_path)
        return muxes


class htsmsg_json:

    def __init__( self, path ):
        self.tvhpath = path

    def load_dvb( self ):
        dvb = {}
        dvb["networks"] = self.load_networks(self.tvhpath + '/var/input/dvb/networks')
        return dvb

    def load_networks( self, networkspath ):
        networks = {}
        for network_path in glob.glob( networkspath + '/*' ):
            if os.path.isdir(network_path):
                network_uuid = os.path.basename(network_path)
                fd = open(network_path + '/config').read()
                jd = json.loads(fd)
                networks[network_uuid] = {}
                networks[network_uuid]["config"] = jd
                networks[network_uuid]["muxes"] = self.load_muxes(network_path + '/muxes')
            else:
                self.logger.debug(" %s is not a directory", network_path)
        return networks

    def load_muxes( self, muxespath ):
        muxes = {}
        for muxe_path in glob.glob( muxespath + '/*' ):
            if os.path.isdir(muxe_path):
                muxe_uuid = os.path.basename(muxe_path)
                fd = open(muxe_path + '/config').read()
                jd = json.loads(fd)
                muxes[muxe_uuid] = {}
                muxes[muxe_uuid]["config"] = jd
                muxes[muxe_uuid]["config"]["services"] = self.load_services(muxe_path + '/services')
            else:
                self.logger.debug(" %s is not a directory", muxe_path)
        return muxes

    def load_services( self, servicespath ):
        services = {}
        for service_path in glob.glob( servicespath + '/*' ):
            if os.path.isfile(service_path):
                service_uuid = os.path.basename(service_path)
                fd = open(service_path).read()
                jd = json.loads(fd)
                services[ service_uuid ] = jd
            else:
                self.logger.debug(" %s is not a file", network_path)
        return services
