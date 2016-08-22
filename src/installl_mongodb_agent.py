#!/usr/local/bin/python2.7
# encoding: utf-8
'''
installl_mongodb_agent -- install Cloud Manager Agent

installl_mongodb_agent is a script for automation the agent installation steps.

Manual steps (as of 4-Aug-2016)

curl -OL https://cloud.mongodb.com/download/agent/automation/mongodb-mms-automation-agent-2.8.1.1725-1.osx_x86_64.tar.gz
tar -xvf mongodb-mms-automation-agent-2.8.1.1725-1.osx_x86_64.tar.gz
cd mongodb-mms-automation-agent-2.8.1.1725-1.osx_x86_64
vi local.config
add mmsGroupId=5329cef9a6e96c3c188aee89
add mmsApiKey=6db8eabd203684e09027edd62643394f

Create the directories 

/var/lib/mongodb-mms-automation, 
/var/log/mongodb-mms-automation
/data/cloudmanager 

and ensure that they are owned by same user that you will use to run the agent.

sudo mkdir -p /var/lib/mongodb-mms-automation
sudo mkdir -p /var/log/mongodb-mms-automation
sudo mkdir -p /data/cloudmanager

Change owner (if you are logged in as agent runner)

sudo chown `whoami` /var/lib/mongodb-mms-automation
sudo chown `whoami` /var/log/mongodb-mms-automation
sudo chown `whoami` /data/cloudmanager

Start the agent

nohup ./mongodb-mms-automation-agent --config=local.config >> /var/log/mongodb-mms-automation/automation-agent.log 2>&1 &


@author:     joe@joedrumgoole.com

'''

import sys
import os
import urllib2

from argparse import ArgumentParser
from argparse import RawDescriptionHelpFormatter

__version__ = "0.1"

DEBUG = 1
TESTRUN = 0
PROFILE = 0

class CLIError(Exception):
    '''Generic exception to raise and log different fatal errors.'''
    def __init__(self, msg):
        super(CLIError).__init__(type(self))
        self.msg = "E: %s" % msg
    def __str__(self):
        return self.msg
    def __unicode__(self):
        return self.msg

def download( remote, localPath=None  ):
    # https://cloud.mongodb.com/download/agent/automation/mongodb-mms-automation-agent-2.8.1.1725-1.osx_x86_64.tar.gz

    if localPath is None :
        ( _, localPath ) = os.path.split( remote )
        
    # Open the url
    try:
        f = urllib2.urlopen( remote )

        # Open our local file for writing
        with open( localPath, "wb") as local_file:
            local_file.write(f.read())

    #handle errors
    except urllib2.URLError,e :
        print( "URLError opening: '%s' ($s)" % ( remote, e.reason ))
        sys.exit( 1 )
    except urllib2.HTTPError,e :
        print( "HTTPError opening: '%s' ($s)" % ( remote, e.code ))
        sys.exit( 1 )
        
    return localPath
  
    
    
def main(argv=None): # IGNORE:C0111
    '''Command line options.'''

    if argv is None:
        argv = sys.argv
    else:
        sys.argv.extend(argv)
        
    

    program_name = os.path.basename(sys.argv[0])
    program_version = "v%s" % __version__
    program_version_message = '%%(prog)s %s' % (program_version )
    program_shortdesc = __import__('__main__').__doc__.split("\n")[1]
    program_license = '''%s

  Created by joe@joedrumgoole.com

  Licensed under the Apache License 2.0
  http://www.apache.org/licenses/LICENSE-2.0

  Distributed on an "AS IS" basis without warranties
  or conditions of any kind, either express or implied.

USAGE
''' % (program_shortdesc )


    defaultAgentURL = "https://cloud.mongodb.com/download/agent/automation/mongodb-mms-automation-agent-2.8.1.1725-1.osx_x86_64.tar.gz"
    try:
        # Setup argument parser
        parser = ArgumentParser(description=program_license, formatter_class=RawDescriptionHelpFormatter)
        parser.add_argument("-v", "--verbose", dest="verbose", default='v', action="count", help="set verbosity level [default: %(default)s]")
        parser.add_argument('-V', '--version', action='version', version=program_version_message)
        parser.add_argument('--download', default=defaultAgentURL, help="Remote URL for agent  location [ default: %(default)s ]")
        parser.add_argument('--localpath', default=None, help="default local path for download")
        #parser.add_argument(dest="paths", help="paths to folder(s) with source file(s) [default: %(default)s]", metavar="path", nargs='+')

        # Process arguments
        args = parser.parse_args()

        verbose = args.verbose

        if verbose > 0:
            print("Verbose mode on")
            
        if args.download :
            localPath = download( args.download )
            if args.verbose :
                print( "Downloaded: '%s' to '%s'" % ( args.download, localPath ))

        return 0
    except KeyboardInterrupt:
        ### handle keyboard interrupt ###
        return 0
#     except Exception, e:
#         raise( e )
#         indent = len(program_name) * " "
#         sys.stderr.write(program_name + ": " + repr(e) + "\n")
#         sys.stderr.write(indent + "  for help use --help")
#         return 2

if __name__ == "__main__":

    sys.exit(main())