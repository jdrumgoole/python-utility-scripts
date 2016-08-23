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

from __future__ import print_function

import sys
import os
import urllib2
import tarfile

from argparse import ArgumentParser
from argparse import RawDescriptionHelpFormatter
import shutil

__version__ = "0.2"

DEBUG = 1
TESTRUN = 0
PROFILE = 0

DIRS = { 'lib'  : '/var/lib/mongodb-mms-automation', 
         'log'  : "/var/log/mongodb-mms-automation",
         'data' : '/data/cloudmanager' } 

class CLIError(Exception):
    '''Generic exception to raise and log different fatal errors.'''
    def __init__(self, msg):
        super(CLIError).__init__(type(self))
        self.msg = "E: %s" % msg
    def __str__(self):
        return self.msg
    def __unicode__(self):
        return self.msg

def make_dir( path, verbose=False ):
    if os.path.isdir( path ) :
        if verbose:
            print( "%s already exists no need to make" % path )
    else:
        if verbose:
            print( "Making directories : '%s'"  % path, end="" )
        os.makedirs( path )
        if verbose:
            print( "done")
        
def make_dirs( dirs, verbose=False ) :
    
    for ( k,v ) in dirs.iteritems() :
        make_dir( v, verbose )
    
def updateValue( line, key, value  ):
    
    retVal = None
    
    ( lhs, _ ) = line.split( "=" )
    
    if ( key == lhs ) :
        retVal = key + "=" + value
        
    return retVal
        
def updateValues( line, values ):
    
    for k,v  in values:
        updated = updateValue( line, k, v )
        if updated :
            return updated
        
    return None

def addMMSKeys( configFilePath, verbose=False):
    
    mmsValues = { "mmsGroupId" : "5329cef9a6e96c3c188aee89",
                  "mmsApiKey"  : "6db8eabd203684e09027edd62643394f" }

    
    api_key_present = False
    group_ID_present = False
    
    configData = []
    processed = {}
    
    if verbose:
        print( "Adding MMS keys to '%s'" % configFilePath )
        
    with open( configFilePath, "r") as config_file :
        for line in config_file.readlines() :
            if "=" in line :
                ( lhs, rhs ) = line.split( "=")
                if lhs in mmsValues.keys() :
                    rhs = mmsValues[ lhs ]
                    processed[ lhs ] = rhs
                line = lhs + "=" + rhs + "\n"
            configData.append( line )
            
        for k, v in mmsValues.iteritems() :
            if not k in processed :
                configData.append( k + "=" + v )

    os.rename( configFilePath, configFilePath + ".orig" )
    shutil.copyfile( configFilePath + ".orig", configFilePath )
    
    with open( configFilePath, "w" ) as config_file :
        for line in configData :
            config_file.write( line )
            
    if verbose:
        print( "Keys added")
    
def extract( tarPath, agentPath=".", verbose=False ):
    
    if agentPath is "." :
        agentPath = os.getcwd()
        
    if verbose :
        print( "Extracting files from : '%s' to '%s'" % ( tarPath, agentPath ))
        
    with tarfile.open( tarPath ) as tar_file :
        root = os.path.dirname( tar_file.getmembers()[0].name )
        for f in tar_file :
            print( "Extracting: '%s'" % f.name, end="")
            tar_file.extract( f  )
            print( " done")
        
    if verbose:
        print( "Extraction complete" )
        
    return root
        
        
def download( remote, localPath=None, verbose=None  ):
    # https://cloud.mongodb.com/download/agent/automation/mongodb-mms-automation-agent-2.8.1.1725-1.osx_x86_64.tar.gz

    if localPath is None :
        ( _, localPath ) = os.path.split( remote )
        
    if os.path.exists( localPath ) :
        print( "Using cached local copy ('%s')" % localPath )
        return localPath 
    
    # Open the url
    if verbose:
        print( "Downloading: %s -> %s ..." % ( remote, localPath ))
        
    try:
        f = urllib2.urlopen( remote )

        # Open our local file for writing
        with open( localPath, "wb") as local_file:
            local_file.write(f.read())
            
        if verbose:
            print( "Download complete")

    #handle errors
    except urllib2.HTTPError, e :
        print( "HTTPError opening: '%s' (%s)" % ( remote, e.code ))
        sys.exit( 1 )
    except urllib2.URLError, e :
        print( "URLError opening: '%s' (%s)" % ( remote, e.reason ))
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
    dirs = [ ]
    try:
        # Setup argument parser
        
        euid = os.geteuid()
        egid = os.getegid()
        parser = ArgumentParser(description=program_license, formatter_class=RawDescriptionHelpFormatter)
        parser.add_argument("-v", "--verbose", dest="verbose", default='v', action="count", help="set verbosity level [default: %(default)s]")
        parser.add_argument('-V', '--version', action='version', version=program_version_message)
        parser.add_argument('--download', default=defaultAgentURL, help="Remote URL for agent  location [ default: %(default)s]")
        parser.add_argument('--localpath', default=".", help="default local path for download [ default : '%(default)s']")
        parser.add_argument('--agentpath', default=".", help="default path to extract agent files to [ default : '%(default)s']")
        parser.add_argument('--configfile', default='local.config', help="default name for config file [ default : '%(default)s']")
        parser.add_argument('--agentuid', default=euid, help="default UID for agent [ default : '%(default)s']") 
        parser.add_argument('--agentgid', default=egid, help="default GID for agent [ default : '%(default)s']")  
        #parser.add_argument(dest="paths", help="paths to folder(s) with source file(s) [default: %(default)s]", metavar="path", nargs='+')

        # Process arguments
        args = parser.parse_args()

        verbose = args.verbose

        if verbose > 0:
            print("Verbose mode on")
            
        if args.download :
            localPath = download( args.download, verbose=args.verbose )
            
        if args.agentpath :
            config_path = extract( localPath, args.agentpath, verbose=args.verbose )
            
        config_file = os.path.join( config_path, args.configfile )
        addMMSKeys( config_file, verbose )
        
        make_dirs( DIRS, verbose )

        for ( k,v ) in DIRS.iteritems() :
            os.chown( v, args.agentuid, args.agentgid )

        print( "Configuration complete")
        print( "Now run:")
        agentBinary = os.path.join( config_path, "mongodb-mms-automation-agent")
        args = "--config=" + config_file
        logfile = os.path.join( DIRS[ 'log'], "automation-agent.log" )
        print( "nohup " + agentBinary + " " + args + " >> " + logfile + " 2>&1 &")
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