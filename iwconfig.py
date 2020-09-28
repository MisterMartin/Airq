"""
Access iwconfig command.
"""
import subprocess
import re

def iwconfig(teststring=None):
    """
    Run iwconfig and return the wifi characteristics as a hash.

    iwconfig returns outout in this form:
    wlan0     IEEE 802.11  ESSID:"Kitchen"
          Mode:Managed  Frequency:2.417 GHz  Access Point: 28:C6:8E:76:5B:70
          Bit Rate=5.5 Mb/s   Tx-Power=31 dBm
          Retry short limit:7   RTS thr:off   Fragment thr:off
          Power Management:on
          Link Quality=31/70  Signal level=-79 dBm
          Rx invalid nwid:0  Rx invalid crypt:0  Rx invalid frag:0
          Tx excessive retries:451  Invalid misc:0   Missed beacon:0

    lo        no wireless extensions.

"""

    if teststring:
        lines = teststring
    else:
        lines = ''
        process = subprocess.Popen('/sbin/iwconfig', stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        while True:
            line = process.stdout.read().decode('utf-8')
            if line == '':
                break
            lines = lines + line

    lines = lines.split("\n")

    retval = {}

    # Create one long list of all of the tokens in the output
    tokens = []
    for l in lines:
        ll = l.strip()
        # Break them apart using these separators:
        tokens = tokens + re.split('  *|,|=|:', ll)
    # Remove empty toekns
    tokens.remove('')

    # Find "ESSID" followed by a value
    try:
        i1 = tokens.index("ESSID")
        if len(tokens) > i1:
            retval["ssid"] = tokens[i1+1].strip('"')
    except ValueError:
        # not found
        pass

    # Find "Signal" followed by "level" followed by a value
    try:
        i1 = tokens.index("Signal")
        i2 = tokens.index("level")
        if (i2 == i1+1) and (len(tokens) > i2):
            retval["sig_dbm"] = tokens[i2+1]
    except ValueError:
        # not found
        pass

    return retval

if __name__ == '__main__':

    test = """
    wlan0     IEEE 802.11  ESSID:"Kitchen"  
          Mode:Managed  Frequency:2.417 GHz  Access Point: 28:C6:8E:76:5B:70   
          Bit Rate=5.5 Mb/s   Tx-Power=31 dBm   
          Retry short limit:7   RTS thr:off   Fragment thr:off
          Power Management:on
          Link Quality=31/70  Signal level=-79 dBm  
          Rx invalid nwid:0  Rx invalid crypt:0  Rx invalid frag:0
          Tx excessive retries:451  Invalid misc:0   Missed beacon:0

    lo        no wireless extensions.
    """

    print(iwconfig(test))