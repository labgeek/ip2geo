import sys
from optparse import OptionParser
from collections import defaultdict
import re
import os
import csv

'''
Make sure you have the geoip2.database python modules installed
''' 
try:
    import geoip2.database
except ImportError:
    print("[!] Python-GeoIP2 Database python module not found")
    

__author__ = 'JD Durick (labgeek@gmail.com)'
__date__ = 20161228
__version__= 0.01
__description__= "Quick and dirty program to pull IP addresses from any file and feed them into a GeoIP static databases for the results"

'''
Could be used with bulk_extractor or any other forensic tool
'''

'''
Function name: main()
Input:  nothing
Output: exit code
Author:  JD Durick
''' 
def main():
    mainDict = defaultdict(list)
    dataArray = []
    parser = OptionParser()
    parser = OptionParser(usage="usage: %prog -f <inputfilename> -o <outputfilename>", version="%prog 0.1")
    parser.add_option("-f", "--inputfilename", dest="inputfilename", help="input file path", type="string")
    parser.add_option("-o", "--outputfilename", dest="outputfilename", help=" output file path", type="string")
    (options, args) = parser.parse_args()
    ipFile = options.inputfilename
    outfile = options.outputfilename
    
    # Hard-coded locations of the maxmind database(s)
    # Need to have City, Domain, and ISP databases from Maxmind (put in config file using ConfigParser()
    reader = geoip2.database.Reader('GeoIP2-City.mmdb')
    dreader = geoip2.database.Reader('GeoIP2-Domain.mmdb')
    isp_reader = geoip2.database.Reader('GeoIP2-ISP.mmdb')
    private_ip_ranges = ('10.', '172.16.', '172.31.', '192.168')

    # extracts all ip addresses and returns list
    ipaddresses = extractIPs(ipFile)

    # loop it    
    for i in ipaddresses:
        '''
        Using GeoIP API to validate routable vs. non-routable IP Addresses
        '''
        try:
            response = reader.city(i.strip())
            domainres = dreader.domain(i.strip())
            ispres = isp_reader.isp(i.strip())
                
            isp = ispres.isp
            country = response.country.name
            state = response.subdivisions.most_specific.name
            city = response.city.name
            postal = response.postal.code
            lat = response.location.latitude
            lon = response.location.longitude
            tz = response.location.time_zone
            dom = domainres.domain
            dataArray.append([i.strip(), city, country, state, lat, lon, tz, dom, isp])
        except:
            pass
    csvWriter(dataArray, outfile)  

'''
Function name: csvWriter()
Input:  Array of GEOIP values and output file name to be written to
Output: Nothing (file is written to hard disk
Author:  JD Durick
''' 
def csvWriter(data, outputFile):
    print "Writing output..."
    headers = ['IP Address', 'City', 'Country', 'State', 'Latitude', 'Longitude', 'Timezone', 'Domain', 'ISP']
    try:
        with open(outputFile, 'wb') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(headers)
            for d in data:
                writer.writerow(d)
                
            csvfile.flush()
            csvfile.close()
            print "Done Writing to %s\n" % outputFile
            
    except IOError, e:
        print "Error writing to CSV file\n"
        exit(0)
    
'''
Function name: extractIPs()
Input:  File name containing ip addresses
Output: simple array of ip addresses  (string)
'''  
def extractIPs(ipfilename):

    regexString = r"(%s)" % ("\.".join(['(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)']*4))
    patt = re.compile(regexString)
    regexString = open(ipfilename).read()
    i = 0
    results = []
    while True:
        m = patt.search(regexString, i)
        if m:
            results.append(m.group(1))
            i = m.end()+1
        else:
            break
    return results

'''
Function name: readFiles()
Input:  directory name (*nix specific)
Output: simple array of files found in specified directory  (strings)
Note:  unused as of 12/31/2016
''' 
def readFiles(dir):
    '''
    Simple function to read the files out of a certain directory into a
    list and return that list.
    '''
    dirlist = []
    for dirpath, _, filenames in os.walk(dir):
        for f in filenames:
            dirlist.append(os.path.abspath(os.path.join(dirpath, f)))
    return dirlist

if __name__ == '__main__':
    main()
    