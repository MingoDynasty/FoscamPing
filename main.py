'''==========================================================================
    Programmer: Mingo                                       Date: 2015-10-14
=========================================================================='''
import sys # Provides access to command line arguments.
import os # Provides access to operating system interfaces.
import subprocess

def main(argv):

    bDebug = True
    total = len(sys.argv)
    if(bDebug):
        print ("The total numbers of args passed to the script: %d " % total)
        for i in range(0,total):
            print("Arg[" + str(i) + "]: " + sys.argv[i])
    for i in range(1,total):
        hostname = sys.argv[i]

        hostname = "192.168.2.341" #example

        if ping(hostname):
            print(hostname, 'is up!')
        else:
            print(hostname, 'is down')

    # Atlernatively, get the list of hosts from a file
    filename = 'list_of_hosts'
    if os.path.isfile(filename):
        with open(filename, 'r') as file:
            for line in file:
                line = line.strip()
                print(line)

    print("Done.")
    return

def ping(hostname):
    """
    Ping a host. Note that this implementation may or may not work on non-Windows operating systems.
    :param hostname: hostname to ping
    :return: true on successful ping, else false.
    """
    print("Pinging hostname: " + hostname)
    cmd = "ping -n 1 " + hostname

    try:
        subprocess.check_output(cmd,stderr=subprocess.STDOUT,shell=True)
        return True # if we make it here, then the command succeeded

    # exception is thrown on non zero exits, so this must mean the command failed
    except subprocess.CalledProcessError as e:
        return False

if __name__ == '__main__':
    main(sys.argv)
# end main
