#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import src.inputs as inputsLib
import src.channels as channelsLib
import src.fetch as fetchLib
import src.users as usersLib
import src.dvblogs as dvblogsLib
import logging, json

#logging.basicConfig(filename='default.log', level=logging.DEBUG)

# Get root logger
rootLogger = logging.getLogger()

# create logger with 'main'
logger = logging.getLogger('main')
logger.setLevel(logging.DEBUG)


# create file handler which logs even debug messages
fh = logging.FileHandler('debug.log')
fh.setLevel(logging.DEBUG)

# create console handler with a higher log level
ch = logging.StreamHandler()
ch.setLevel(logging.ERROR)

# create formatter and add it to the handlers
formatter = logging.Formatter('%(asctime)s|%(levelname)s|%(funcName)s: %(message)s')
fh.setFormatter(formatter)
ch.setFormatter(formatter)

# add the handlers to the logger
rootLogger.addHandler(fh)
#logger.addHandler(ch)
rootLogger.addHandler(ch)

# test class
#logger.info('decode_module.htsmsg_binary')
#a = decode.htsmsg_binary("./samples/muxes_4.2.sample")
# logger.info('load_file')
# a.load_file()

print('TVHeadend 4.2')
a = inputsLib.inputs("./samples/tvheadend-4.2", 4.2)
a.load()
inputs = a.get()
print(json.dumps(inputs, indent=4, ensure_ascii=False))

print('TVHeadend 4.0')
b = inputsLib.inputs("./samples/tvheadend-4.0", 4.0)
b.load()
# print(json.dumps(b.get(), indent=4, ensure_ascii=False))

print('inputs')
c = channelsLib.channels("./samples/tvheadend-4.2", inputs["dvb"])
c.load_services()
d_services = c.get_services()
c.print_services()
# print(json.dumps(services, indent=4, ensure_ascii=False))
c.load_channels()
d_channels = c.get_channels()
c.print_channels()

print('fetch')
d = fetchLib.fetch("./samples/tvheadend-4.0", d_channels)
d.fetch()
d_merging = d.get()

print('users')
c_users = usersLib.users("./samples/tvheadend-4.2")
c_users.load()
c_users.print_users()
d_users = c_users.get()
# print(json.dumps(c_users.get(), indent=4, ensure_ascii=False))

print('migration')
c_dvblogs = dvblogsLib.dvblogs("./samples/tvheadend-4.0", "./samples/tvheadend-4.2", 4.2, d_channels, d_merging, d_users)
c_dvblogs.load_logs()
c_dvblogs.ask_default_user()
c_dvblogs.upgrade_logs()
