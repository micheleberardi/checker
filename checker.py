#!/usr/bin/env python3.4
# -*- coding: utf-8 -*-

"""
check bad words and email account
"""

__author__ = "Michele Berardi"
__copyright__ = "Copyright 2018, "
__license__ = "GPL"
__version__ = "1.0.1"
__maintainer__ = "Michele Berardi"
__email__ = "michele@berardi.com"
__status__ = "Production"

import logging
import requests
from datetime import datetime
from dateutil.relativedelta import relativedelta
import time
import csv
import dns
import dns.resolver
import socket
import smtplib
import re

# SECTION DATE
date2 = datetime.today() + relativedelta(days=-1)
date3 = datetime.today() + relativedelta(hours=-1)
datenow = date2.strftime('%Y-%m-%dT%H:%M:%S')
startdate = date2.strftime('%Y-%m-%dT00:00:00')
enddate = date2.strftime('%Y-%m-%dT23:59:59')
insertdate = date2.strftime('%Y-%m-%d')

# SECTION LOGS
datelog = datetime.now().strftime('%Y-%m-%d')
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(levelname)-8s %(message)s',
                    datefmt='%a, %d %b %Y %H:%M:%S',
                    filename="logs/core-" + datelog + ".log", filemode='a')

start = time.time()
logging.debug("==========================================")
logging.debug(">>>>>>>>>> START TRANSACTION <<<<<<<<<<<<<")


def get_token(endpoint):
    try:
        response = requests.get(endpoint)
        if response.ok:
            result = response.json()
            token1 = result["data"][0]["token"]
            logging.debug("{}{}".format("token1 : ", token1))
            logging.debug("{}{}".format("STATUS TOKEN REQUEST >>> ", response.text))
            logging.debug("{}{}".format("STATUS TOKEN CODE >>> ", response.status_code))
            logging.debug("{}{}".format("STATUS TOKEN RESPONSE >>> ", response.content))
        return token1
    except:
        logging.debug("{}{}".format("STATUS TOKEN REQUEST >>> ", response.text))
        logging.debug("{}{}".format("STATUS TOKEN CODE >>> ", response.status_code))
        logging.debug("{}{}".format("STATUS TOKEN RESPONSE >>> ", response.content))

# SECTION GET ADVERTISING TRACKING REQUEST
def get_advertiser(token):
     logging.debug('GET TOKEN')
     try:
         response = requests.get(endpoint_api)
         if response.ok:
             result = response.json()
             json_result = result["data"]
             logging.debug("{}{}".format("advertiser : ", json_result))
             logging.debug("{}{}".format("STATUS ADVERTISER REQUEST >>> ", response.text))
             logging.debug("{}{}".format("STATUS CALL ADVERTISER CODE >>> ", response.status_code))
             logging.debug("{}{}".format("STATUS ADVERTISER RESPONSE >>> ", response.content))
         return json_result
     except:
         logging.debug("{}{}".format("STATUS ADVERTISER REQUEST >>> ", response.text))
         logging.debug("{}{}".format("STATUS ADVERTISER CODE >>> ", response.status_code))
         logging.debug("{}{}".format("STATUS ADVERTISER RESPONSE >>> ", response.content))

# SECTION SEARCH BAD WORD ON THE FULL JSON

def list_badwords(badwords_list,list_advertisers,token):
    for rows in list_advertisers:
        id = rows["id"]
        username = rows["username"]
        trovato = 'false'
        for k,v in rows.items():
            with open(badwords_list) as csvDataFile:
                csvReader = csv.reader(csvDataFile)
                for keywords in csvReader:
                    if v in keywords:
                        trovato = 'true'
                        logging.debug("{}{}".format("FOUND BAD WORD >>> ", v))
                        break
        check = check_email_account(username)
        if check == 'false':
            trovato = 'true'
            logging.debug("{}{}".format("FOUND BAD EMAIL ACCOUNT >>> ", username))
        if trovato == 'true':
            #print("BLOCCATO")
            logging.debug("{}{}".format("FOUND BAD WORD >>> ", v))
            response = "https://api.michelone.com/3.0/advertiser/tracking-request/" + str(id) + "/?token=" + token + "&company_uid=2321bsh"
            data = {"status_audit": "refused"}
            r = requests.put(response, json=data)
            logging.debug("{}{}".format("STATUS REFUSED REQUEST >>> ", r.text))
            logging.debug("{}{}".format("STATUS REFUSED CODE >>> ", r.status_code))
            logging.debug("{}{}".format("STATUS REFUSED RESPONSE >>> ", r.content))
            logging.debug("{}{}".format("REFUSED >>> ", rows))
            #return ("{}{}".format("REFUSED >>> ", rows))
            #sys.exit(0)

        else:
            #print("APPROVATO")
            response = "https://api.michelone.com/3.0/advertiser/tracking-request/" + str(id) + "/?token=" + token + "&company_uid=2321bsh"
            data = {"status_audit": "approved"}
            r = requests.put(response, json=data)
            logging.debug("{}{}".format("STATUS APPROVED REQUEST >>> ", r.text))
            logging.debug("{}{}".format("STATUS APPROVED CODE >>> ", r.status_code))
            logging.debug("{}{}".format("STATUS APPROVED RESPONSE >>> ", r.content))
            return ("{}{}".format("APPROVED >>> ", rows))
            #sys.exit(0)


def check_email_account(username):
    # CHECK EMAIL
    email_address = username
    logging.debug("checking email " + email_address)
    addressToVerify = email_address
    match = re.match('^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,4})$', addressToVerify)
    if match == None:
        raise ValueError('Bad Syntax')
    domain_name = email_address.split('@')[1]
    try:
        records = dns.resolver.query(domain_name, 'MX')
        mxRecord = records[0].exchange
        mxRecord = str(mxRecord)
    except:
        logging.debug("ERROR >>> time out smtp connection " + email_address + " has been not check")
    # Step 3: ping email server
    # check if the email address exists
    # Get local server hostname
    host = socket.gethostname()
    # SMTP lib setup (use debug level for full output)
    server = smtplib.SMTP()
    server.set_debuglevel(0)
    try:
        # SMTP Conversation
        server.connect(mxRecord)
        server.helo(host)
        server.mail('bucksense.alert@gmail.com')
        code, message = server.rcpt(str(addressToVerify))
        server.quit()
    except:
        logging.debug("ERROR >>> time out smtp connection " + email_address + " has been not check")
    # Assume 250 as Success
    if code == 250:
        logging.debug("email account " + email_address + " for user " + email_address + " is ok")
        logging.debug("user " + email_address + " has been approved")
        time.sleep(1)
        return "true"
    else:
        # BLOCK
        logging.debug(
            "ERROR >>> email account " + email_address + " is not valid for account " + email_address + "\r\n")
        return "false"



if __name__ == "__main__":
    endpoint = "https://api.michelone.com/3.0/login/?username=<USERNAME>&password=<PASSWORD>&company_uid=2321bsh"
    token = get_token(endpoint)
    endpoint_api = "http://api.michelone.com/3.0/advertiser/tracking-request/?token=" + token + "&search=proposed&search_field=status_audit"
    list_advertisers = get_advertiser(token)
    badwords_list = "badwords.csv"
    list_badwords = list_badwords(badwords_list,list_advertisers,token)
    logging.debug("{}{}{}".format("It took : ", time.time() - start, ' seconds.'))
    logging.debug(">>>>>>>>>> FINISH TRANSACTION <<<<<<<<<<<<")
    logging.debug("==========================================")


