import dns.resolver
import checkdmarc

def check_spf_dmarc(senderAddress):
    domain = checkdmarc.get_base_domain(senderAddress)  # get the base email server domain from the sender address

    # source: https://www.thierolf.org/blog/2021/small-python-script-to-quick-test-dmarc-dkim-and-spf-records/
    try:
        test_dmarc = dns.resolver.resolve('_dmarc.' + domain , 'TXT')
        for dns_data in test_dmarc:
            if 'DMARC1' in str(dns_data):
                break
    except:
        print("[FAIL] DMARC record not found.")
        return False

    try:
        test_spf = dns.resolver.resolve(domain , 'TXT')
        for dns_data in test_spf:
            if 'spf1' in str(dns_data):
                break
    except:
        print ("[FAIL] SPF record not found.")
        return False

    return True