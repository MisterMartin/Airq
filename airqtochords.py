#! /usr/local/bin/python3
"""
Read ccs811 sensors (ina219, ccs811 and ccs811), and send to CHORDS.
"""

# pylint: disable=C0103

import time
import sys
import json

import iwconfig
import pychords.tochords as tochords

SHUNT_OHMS = 0.1
MAX_EXPECTED_AMPS = 0.2

# Create the ccs811 device
ccs811 = ccs811.ccs811()

# A test config to be used in the absence of a configuration file
test_config = """
{
    "chords": {
        "skey":    "secret_key",
        "host":    "chords_host.com",
        "enabled": true,
        "inst_id": "1",
        "test":    true,
        "sleep_secs": 5
    }
}
"""

def make_chords_vars(old_hash, replace_keys):
    """
    Rename the keys in a hash. If an old key does not
    exist in the new_keys, remove it.
    """
    new_hash = {}
    for old_key, old_val in old_hash.items():
        if old_key in replace_keys:
            new_hash[replace_keys[old_key]] = old_val

    # The chords library wants the vars in a separate dict
    new_hash = {"vars": new_hash}
    return new_hash


def timestamp():
    """
    Return an ISO formated current timestamp
    """
    t = time.gmtime()
    ts = "{:04}-{:02}-{:02}T{:02}:{:02}:{:02}Z".format(t[0], t[1], t[2], t[3], t[4], t[5])
    return ts

def get_iw():
    """
    Return iwconfig values that we want to send on to CHORDS.
    Possible returned hash values are "sig_dbm".
    """
    iw = iwconfig.iwconfig()
    iwvars = {}
    if "sig_dbm" in iw.keys():
        iwvars["sig_dbm"] = iw["sig_dbm"]
    return iwvars

def get_ccs811():
    """
    Get a ccs811 reading. Translate hash names into
    CHORDS shortnames.
    """
    ccs811 = ccs811.reading()
    ccs811['ccs811_pres_mb'] = ccs811.pop('pres_mb')
    ccs811['ccs811_pres_mb'] = ccs811.pop('pres_mb')
    ccs811['ccs811_pres_mb'] = ccs811.pop('pres_mb')
    ccs811['ccs811_temp_c'] = ccs811.pop('temp_C')
    ccs811['ccs811_rh'] = ccs811.pop('rh')
    return ccs811

if __name__ == '__main__':


    new_keys = {
        'time': 'at',
        'voc': 'voc',
        'eco2': 'eco2',
        'pressure': 'airq_p',
        'temperature': 'airq_t',
        'humidity': 'airq_rh'
    }

    print("Starting", sys.argv)

    if len(sys.argv) > 2:
        print("Usage:", sys.argv[0], "[config_file]")
        sys.exit(1)

    if len(sys.argv) == 1:
        config = json.loads(test_config)
    else:
        config = json.loads(open(sys.argv[1]).read())

    # Extract some useful config values
    host = config["chords"]["host"]
    chords_options = {
        "inst_id": config["chords"]["inst_id"],
        "test": config["chords"]["test"],
        "skey": config["chords"]["skey"]
    }
    if "sleep_secs" in config["chords"]:
        sleep_secs = config["chords"]["sleep_secs"]
    else:
        sleep_secs = 5

    # Start the CHORDS sender thread
    tochords.startSender()

    while True:
        # Get the CCS811 reading
        ccs811_data = ccs811.reading()

        # Make a chords variable dict to send to chords
        chords_record = make_chords_vars(ccs811_data, new_keys)

        # Add in other variables

        # Get iwconfig details
        iw_vars = get_iw()
        chords_record["vars"].update(iw_vars)

        # Merge in the chords options
        chords_record.update(chords_options)

        # create the chords uri
        uri = tochords.buildURI(host, chords_record)
        # Send it to chords
        tochords.submitURI(uri, 10*24*60)

        # Flush the outputs
        sys.stdout.flush()
        sys.stderr.flush()

        # Sleep until the next measurement time
        time.sleep(sleep_secs)