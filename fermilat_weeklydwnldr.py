# ==========================================================================
# Download Fermi-LAT weekly data files via FTP
#
# Copyright (C) 2017 J.V. Cardenzana
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# ==========================================================================

import argparse
from datetime import datetime
import os
import shutil
import ftplib


class fermi_dwnldr:
    """ Downloader for Fermi-LAT weekly files """

    def __init__(self):
        """ Class initializer """
        # URL directory
        self.urlftp("heasarc.gsfc.nasa.gov")
        self.urldir("/FTP/fermi/data/lat/weekly/photon/")
        # Download directory
        self.dwndir(os.environ['PWD'])
        
        # Temporary download directory
        self.__tmpdir = self.__dwndir
        if os.environ.get('TMPDIR') is not None:
            # Store tmp files in system default temporary file storage
            self.__tmpdir = os.environ['TMPDIR']
        elif os.path.isdir('/tmp'):
            # Store tmp files in '/tmp/' temporary file storage
            self.__tmpdir = "/tmp/"

        self.__existing_files = []   # List of files that already exists
        self.__available_files = []  # List of files available for download


    # ====================
    # PUBLIC METHODS
    # ====================

    def available_files(self):
        """ Returns list of files available for download """
        return self.__available_files


    def dwndir(self, dwndir=None):
        """ Get/set the download directory """
        if dwndir is not None:
            self.__dwndir = dwndir

        return self.__dwndir


    def get_available_files(self, force=False):
        """ Looks up what files in self.__urldir are available """

        # Make sure storage object is empty
        if (not force) and (len(self.__available_files) != 0):
            return
    

        try:
            # Store the file names, size and date modified
            self.__available_files = list(self.__ftp.mlsd(self.__urldir, ["size","modify"]))
        except ftplib.error_perm as resp:
            # Catch exception when there are no files
            if str(resp) == "550 No files found":
                print ("No files in {0}".format(self.__urldir))
                return
            else:
                raise

        # Parse through each file name and strip off the path
        rmv_attr = []
        for file_attr in self.__available_files:
            # Get filename
            file_attr = (file_attr[0].split('/')[-1],file_attr[1])
            
            # Remove '.' and '..'
            if (file_attr[0] == '.') or (file_attr[0] == '..'):
                rmv_attr.append(file_attr)
                
        for file_attr in rmv_attr:
            self.__available_files.remove(file_attr)

        # Sort the files
        self.__available_files = sorted(self.__available_files)


    def get_existing_files(self):
        """ Gets a list of existing files """
        self.__existing_files = os.listdir(self.__dwndir)


    def existing_files(self):
        """ Returns the current list of existing files """
        return self.__existing_files


    def run(self, dwnld, ignore_size):
        """ Initiates the actual download of files 
        ARGS:
            dwnld: if 'True' a list of files to be downloaded is printed
        """
        # Get existing and available file lists
        self.get_available_files()
        self.get_existing_files()

        if dwnld:
            print("Downloading files:")
        else:
            print("Files that would be downloaded:")

        # Loop through available files
        size_sum = 0
        for f in self.__available_files:
            # Get the filename
            file_name = f[0]

            # Setup size comparison
            servr_size = int(f[1]['size']) / 1e6
            size_diff = False
            if (not ignore_size) and (file_name in self.__existing_files):
                # Get size from server and existing file
                exist_size = os.stat(self.__dwndir+file_name).st_size / 1e6
                size_diff = (servr_size - exist_size) != 0

            # Make sure the file isn't in the download directory already
            # or that they are different sizes
            if (file_name not in self.__existing_files) or size_diff:

                # Print the file being downloaded along with its size in MB
                self.__printfileinfo(self.__urldir + file_name)

                # Try to actually download the file if requested
                if dwnld:
                    try:
                        self.__downloadfile(f[0])
                    except KeyboardInterrupt:
                        break

                # Increase the size of the transfer
                size_sum += servr_size

            else:
                print("   {0} (exists)".format(file_name))

        # Print total size of files transfered
        if size_sum < 1e3:
            print("Total transfer size: {0:.3f} M\n".format( size_sum ))
        else:
            print("Total transfer size: {0:.2f} G\n".format( size_sum/1e3 ))


    def urldir(self, urldir=None):
        """ Get/set the URL directory """
        if urldir is not None:
            self.__urldir = urldir

        return self.__urldir


    def urlftp(self, urlftp):
        """ Get/set the URL directory """
        self.__ftp = ftplib.FTP(urlftp)
        self.__ftp.login("anonymous","")


    # ====================
    # PRIVATE METHODS
    # ====================

    def __downloadfile(self, file_name):
        """ Download a particular file """
        # Download the file
        file_path = (self.__urldir+file_name)

        # Open the file for writing in binary mode
        tmp_file_name = self.__tmpdir + "/tmp_" + file_name
        f = open(tmp_file_name, 'wb')

        # Do actual download
        try:
            self.__ftp.retrbinary('RETR %s' % file_path, f.write)
            # Clean up time
            f.close()
            shutil.move(tmp_file_name, (self.__dwndir+'/'+file_name))
            #os.rename(tmp_file_name, (self.__dwndir+'/'+file_name))
        except KeyboardInterrupt:
            # The file did not finish downloading, so delete it
            print("\nUser interrupt encountered, deleting temporary file:\n   ",tmp_file_name)
            f.close()
            os.remove(tmp_file_name)
            raise
            

    def __getmodifiedtime(self, file_name):
        """ Parse the modified time string from the server """
        # Convert to time
        time = None

        # Check if the file_name exists already
        for f_atr in self.__available_files:
            if f_atr[0] == file_name:
                time = int(f_atr[1]['modify'])

        # Querry for time from server
        if time is None:
            file_path = self.__urldir + file_name
            try:
                time = int(self.__ftp.sendcmd('MDTM '+file_path).split()[-1] )
            except ftplib.error_perm as resp:
                # Catch exception when there are no files
                if str(resp) == "550 No files found":
                    print ("No such file on server: {0}".format(file_path))
                    return datetime.now()
                else:
                    raise

        # Extract time information into a dedicated datetime object
        year = int(time/1e10)
        mnth = int(time/1e8 % 1e2)
        day  = int(time/1e6 % 1e2)
        hrs  = int(time/1e4 % 1e2)
        mins = int(time/1e2 % 1e2)
        sec  = int(time % 1e2)
        utc_dt = datetime(year, mnth, day, hrs, mins, sec)
        return (utc_dt)

    
    def __getsize_MB(self, file_name):
        """ Get the size of the file on the server """
        file_size = -1

        # Check if the file_name exists already
        for f_atr in self.__available_files:
            if f_atr[0] == file_name:
                file_size = int(f_atr[1]['size'])

        # Size from server
        if file_size < 0:
            self.__ftp.sendcmd("TYPE i")
            file_size = self.__ftp.size(self.__urldir+file_name)
            self.__ftp.sendcmd("TYPE A")

        return file_size/1e6


    def __printfileinfo(self, file_path, mod_time=None):
        """ Print information about the file """
        # Get the time modified file attributes
        file_name = file_path.split('/')[-1]
        file_size = self.__getsize_MB(file_name)

        if mod_time is None:
            # Print without time information
            print ('   {0} ({1:4.1f} M)'.format(file_name, file_size))
        else:
            # Include last modified time
            print ('   {0} ({1} {2}, {3:4.1f} M)'.format(
                file_name, mod_time.date(), mod_time.time(), file_size))        


def getopts_dwnldr():
    """ Get command line options """
    parser = argparse.ArgumentParser()
    parser.add_argument('--urldir', type=str, 
                        default='/FTP/fermi/data/lat/weekly/photon/',
                        help='URL directory containing files to download')
    parser.add_argument('--dwndir', type=str, default='./',
                        help='Local directory to download files to')
    parser.add_argument('--ignoresize', action='store_true',
                        help='Ignore file size differences when deciding to ' +
                             're-download file, if server size is different ' +
                             'than local file size')
    parser.add_argument('--D', action='store_true',
                        help='If not supplied, a list of files to be downloaded '+
                             'is printed rather than actually downloading them')
    return parser.parse_args()


if __name__ == "__main__":
    """ Main method """
    # Get command line options
    args = getopts_dwnldr()

    # Create the downloader
    dwnldr = fermi_dwnldr()
    dwnldr.urldir(args.urldir)
    dwnldr.dwndir(args.dwndir)

    # Run
    dwnldr.run(args.D, args.ignoresize)