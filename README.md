# _Fermi_-LAT Pass 8 Weekly File Downloader

There is a single Python script (fermilat_weeklydwnldr.py) included in this
repository. This file provides the ability to download the weekly files from:

https://heasarc.gsfc.nasa.gov/FTP/fermi/data/lat/weekly/photon/

### Requirements
The code has been tested with the latest Python v3.6.3, which is thus the
recommended version

- **Python 3** - *Uses the following builtin libraries:*
  - **argparse** - *command line options*
  - **datetime** - *parses last modified time information*
  - **os** - *file operations*
  - **shutil** - *file operations*
  - **ftplib** - *Download files via FTP*

### Features
- The download directory can be changed through the `--urldir` command line 
parameter.
- Subsequent executions of this script will not re-download existing files
- If the local version of a file has a different size than the server version,
the file is re-downloaded (useful for the most recent data file). This feature
can be turned off using the `--ignoresize` command line option.
- Files are initially pre-pended with `tmp_<server_filename>` while downloading 
and this temporary file is deleted if something goes wrong (such as the user 
killing the script mid-download).
- Files are initially downloaded into a temporary directory on the system
specified by the users `$TEMPDIR` environment variable, or `/tmp/` if `$TEMPDIR`
is undefined. This ensures the files are cleanedup by the system if for some 
reason the download is canceled and the temporary file cannot be safely deleted. 
If neither of these locations exist, the file is downloaded into the specified 
download directory.
- By default a dry-run is conducted, printing a list of files to be downloaded
and the total size that would be transferred. Passing the command line option
`--D` will initiate the actual download of the files.

### Usage
```
usage: fermilat_weeklydwnldr.py [-h] [--urldir URLDIR] [--dwndir DWNDIR]
                                [--ignoresize] [--D]

optional arguments:
  -h, --help       show this help message and exit
  --urldir URLDIR  URL directory containing files to download
                   (default: `/FTP/fermi/data/lat/weekly/photon/`)
  --dwndir DWNDIR  Local directory to download files to
                   (default: `$PWD`, i.e. current directory)
  --ignoresize     Ignore file size differences when deciding to re-download
                   file, if server size is different than local file size
  --D              If not supplied, a list of files to be downloaded is
                   printed rather than actually downloading them
```

# Examples

### View files to be downloaded

The most generic execution would be to run the script in the current directory
```
$ python fermilat_weeklydwnldr.py
Files that would be downloaded:
   lat_photon_weekly_w009_p302_v001.fits (17.5 M)
   lat_photon_weekly_w010_p302_v001.fits (59.6 M)
   ...
Total transfer size: 105.54 G
```
This displays the list of files that would be downloaded along with their size
in megabytes. The last line displays a combined total for all files that would
be downloaded. At the time the above was executed, that would be about 105.54 
gigabytes. Note that this total will be smaller if the directory you are
downloading files to already contains some of these files.

### Download files
To actually execute the download you need to pass the `--D` option, like so:
```
$ python fermilat_weeklydwnldr.py --D
Downloading files:
   lat_photon_weekly_w009_p302_v001.fits (17.5 M)
   lat_photon_weekly_w010_p302_v001.fits (59.6 M)
   ...
Total transfer size: 105.54 G
```

Other options also exist to change where files will be downloaded from 
(`--urldir`) and where the files will be downloaded to (`--dwndir`).
