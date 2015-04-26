
"""
easySNMP.py
Author - Daniel Shryock

Purpose: Easily configure OS X for SNMP monitoring with just
a few select arguments/keywords.

This script is provided without warranty or guarantee, and is
licensed for use only at the direction of elan Technologies.
It is not for distribution. Any application of this script at
a customer location is allowed however use of this script by
elan Technologies or customers of elan Technologies does not
make elan Technologies responsible for any ongoing maintenance
of this script.

Copyright 2015 Elan Technologies
"""

import optparse
import os
import subprocess
import time

__author__ = 'daniel shryock'
snmpdFile = "/etc/snmp/snmpd.conf"
snmpFile = "/etc/snmp/snmp.conf"
now = time.strftime('%Y%m%d_%H%M')
community_name = ""
app_version = 1.0

# Debug:
# Set to "True" to output the configuration files that are created to
# stdout and to remove numerous copies of the backed up configuration files.
debug = False

snmp_keysToSet = {'defcommunity': ""}
snmpd_keysToSet = {'rocommunity': "", 'sysservices': 76, 'syscontact': "", 'syslocation': ""}


class SNMP(object):

    def __init__(self, com_Name):

        self.com_Name = com_Name


class SNMPD(object):
   
    def __init__(self, com_Name):
        self.com_Name = com_Name


def checkFiles(file):
    # function creates a backup copy of existing SNMP configuration files
    # and creates new, empty ones
    if os.path.exists(file):
        os.rename(str(file), str(file) + '.bkup_' + now)
        open(file, mode='w')
        os.chmod(file, 644)
    else:
        open(file, mode='w')
        os.chmod(file, 644)


def config_SNMPD():
    open_snmpd = open("/etc/snmp/snmpd.conf", "w")
    for item in snmpd_keysToSet:
        if snmpd_keysToSet[item] is not None:
            open_snmpd.write(str(item) + " " + str(snmpd_keysToSet[item]) + "\n")
    open_snmpd.close()


def config_SNMP():
    # writes the tokens for the snmp.conf file
    open_snmp = open("/etc/snmp/snmp.conf", "w")
    for item in snmp_keysToSet:
        if snmp_keysToSet[item] is not None:
            open_snmp.write(str(item) + " " + snmp_keysToSet[item] + "\n")

    open_snmp.close()


def format_config_files():
    # uses 'snmpconf' to format and document the keys that were set by this script
    subprocess.call('snmpconf -R /etc/snmp/snmpd.conf -a -f -I /etc/snmp snmpd.conf', shell=True)
    subprocess.call('snmpconf -R /etc/snmp/snmp.conf -a -f -I /etc/snmp snmp.conf', shell=True)


def debug_cleanup():
    subprocess.call('rm /etc/snmp/snmp*.conf.bkup*', shell=True)


def main():

    # parse the arguments and set the definition list with the passed arguments
    p = optparse.OptionParser(description="Simplifies the configuration of SNMP on an OS X device. Will create, format, and place the configration files in the correct location.  It will also start SNMP with the new configuration",
                              version="1.0", prog="easySNMP", usage="%prog -s string [options]")

    p.add_option('-c', '--community_name', dest='community_name', help="The community string used for authentication")
    p.add_option('-l', '--location', dest='location', help="Where the device is physically located")
    p.add_option('-n', '--name', dest='name', help="Name of contact for this device")
    p.add_option('-r', '--restricted', dest='restrict_to', help="Restrict what can request SNMP data via IP address")

    (options, args) = p.parse_args()

    # check if the configuation files already exist and back them up if they do
    checkFiles(snmpdFile)
    checkFiles(snmpFile)

    if options.community_name:
        if options.restrict_to is not None:
            snmpd_keysToSet['rocommunity'] = options.community_name + " " + str(options.restrict_to)
        else:
            snmpd_keysToSet['rocommunity'] = options.community_name

        snmp_keysToSet['defcommunity'] = options.community_name
    elif options.community_name is None:
        community_name = raw_input('Enter the community string (password):')
        snmpd_keysToSet['rocommunity'] = community_name
        snmp_keysToSet['defcommunity'] = community_name
    else:
        p.print_help()

    if options.location is not "":
        snmpd_keysToSet['syslocation'] = options.location

    if options.name is not "":
        snmpd_keysToSet['syscontact'] = options.name

    # Build the files
    config_SNMPD()
    config_SNMP()

    # format the config files using native 'snmpconfig' utility
    format_config_files()

    # stop and start SNMP with the new config
    proc = subprocess.Popen('launchctl unload /System/Library/LaunchDaemons/org.net-snmp.snmpd.plist', shell=True, bufsize=-1)
    proc = subprocess.Popen('launchctl load -w /System/Library/LaunchDaemons/org.net-snmp.snmpd.plist', shell=True, bufsize=-1)

if debug:
    # subprocess.call('cat ' + str(snmpdFile), shell=True)
    print(snmpd_keysToSet)
    print(snmp_keysToSet)
    debug_cleanup()

if __name__ == '__main__':
    main()
