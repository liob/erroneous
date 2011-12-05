#!/usr/bin/env python
# api doc: https://ucbrhn.berkeley.edu/rhn/apidoc/index.jsp

import sys, os
import logging
import random
import ConfigParser
import xmlrpclib

config = ConfigParser.SafeConfigParser({'here': sys.path[0]})
try:
    config.read(os.path.join(sys.path[0], 'erroneous.conf'))
except:
    sys.exit("Could not read erroneous.conf")

url = config.get('main', 'url')
login = config.get('main', 'user')
password = config.get('main', 'pass')
debug = config.get('main', 'debug')

if debug == "true" or debug == "True" or debug == "1":
    debug = True
else:
    debug = False
    
if debug:
    FORMAT = "%(asctime)-15s %(message)s"
    logging.basicConfig(level=logging.DEBUG, format=FORMAT)
else:
    logging.basicConfig(level=logging.INFO)

client = xmlrpclib.Server(url, verbose=0)
key = client.auth.login(login, password)

def checkAndCreateErrata(channel, severity, product):
    """
        channel = channel label
        severity = security || bugfix
        product = string   i.e.: Scientific Linux 6
    """
    packages = client.channel.software.listAllPackages(key, channel)
    for package in packages:
        #errata_name = "%s-%s-errataGen" % (package["name"], package["version"])
        errata_name = "%s-%s.%s_errataGen" % (package["name"], package["version"], package["release"])
        try:
            client.errata.listCves(key, errata_name)
            errata_exists = True
            logging.debug("errata %s found" % errata_name)
        except xmlrpclib.Fault, err:
            if err.faultCode == -208: # no errata with that name found
                errata_exists = False
                logging.debug("errata %s not found" % errata_name)
            else:
                raise
        
        if errata_exists:
            found_package = False
            for item in client.errata.listPackages(key, errata_name):
                if item["id"] == package["id"]:
                    logging.debug("found package %s in errata %s" % (package["name"], errata_name))
                    found_package = True
            if not found_package:
                client.errata.addPackages(key, errata_name, [package["id"],])
                logging.info("appended package %s to errata %s" % (package["name"], errata_name))
            
            found_channel = False
            errata_channels = []
            for item in client.errata.applicableToChannels(key, errata_name):
                errata_channels.append(item["label"])
                if item["label"] == channel:
                    found_channel = True
                    logging.debug("found channel %s in errata %s" % (channel, errata_name))
                    continue
            if not found_channel:
                errata_channels.append(channel)
                logging.info("publishing errata %s to channel %s" % (errata_name, channel))
                client.errata.publish(key, errata_name, errata_channels)
                        
        elif not errata_exists:
            package["changelog"] = client.packages.listChangelog(key, package["id"]).split("*")
            errata_info = {}
            if severity == "security":
                errata_info["synopsis"] = "Security update for %s - ErrataGenerator" % package["name"]
                errata_info["advisory_type"] = "Security Advisory"
            elif severity == "bugfix":
                errata_info["synopsis"] = "Enhancement update for %s" % package["name"]#
                errata_info["advisory_type"] = "Bug Fix Advisory"
            errata_info["advisory_name"] = errata_name
            errata_info["advisory_release"] = random.randint(1, 9999)
            errata_info["product"] = product
            errata_info["topic"] = "no topic"
            errata_info["description"] = package["changelog"][1].strip()
            errata_info["solution"] = "no solution"
            
            logging.info("created errata %s for channel %s" % (errata_name, channel))
            client.errata.create(key, errata_info, [], [], [package["id"],], True, [channel,])
            
        else:
            logging.error("could not process package  id: %i name: %s \nEXITING!" % (package["id"], package["name"]))
            sys.exit(1)
        
        

if __name__ == "__main__":
    for sectionName in config.sections():
        if sectionName != "main":
            try:
                severity = config.get(sectionName, 'severity')
                product = config.get(sectionName, 'product')
                if severity != "security" and severity != "bugfix":
                    raise
            except:
                logging.warning("did not succeed in parsing config of part %s" % sectionName)
                continue
            logging.info("starting part %s:  label: %s  severity: %s" % (sectionName, sectionName, severity) )
            checkAndCreateErrata(sectionName, severity, product)
    client.auth.logout(key)
