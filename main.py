import sys
import dns.message
import dns.query
import datetime
import time
import math


def str_rdclass(rdclass):
    if rdclass == dns.rdataclass.IN:
        return "IN"
    return str(rdclass)


def str_rdtype(rdtype):
    if rdtype == dns.rdatatype.CNAME:
        return "CNAME"
    if rdtype == dns.rdatatype.A:
        return "A"
    if rdtype == dns.rdatatype.NS:
        return "NS"
    return str(rdtype)


def send_error(code):
    if code == 1:
        print("Invalid")
        print("Usage: ./main.py [domain]")
        exit(0)
    if code == 2:
        print(f"Error: No corresponding IP to [{domain_input}].")


def print_result(result):
    if result is None:
        send_error(2)
        exit(0)

    print("QUESTION SECTION:")
    print(f"{domain_input.ljust(37)}  {'IN'.ljust(5)} {'A'.ljust(6)}")
    print("")
    print("ANSWER SECTION:")
    for cname in cname_response:
        print(str(cname.name).ljust(30), str(cname.ttl).ljust(7), str_rdclass(cname[0].rdclass).ljust(5), str_rdtype(cname[0].rdtype).ljust(5), str(cname[0].target))
    print(str(result.name).ljust(30), str(result.ttl).ljust(7), str_rdclass(result[0].rdclass).ljust(5), str_rdtype(result[0].rdtype).ljust(5), result[0].address)
    print("")
    print(f"Query time: {math.ceil((time.time() - start_time) * 1000)} msec")
    print(f"When: {datetime.datetime.now()}")


def main():
    global domain_input
    domain = None
    if len(sys.argv) == 1:
        domain = input("Enter domain name: ")
    elif len(sys.argv) == 2:
        domain = sys.argv[1]
    else:
        send_error(1)
    domain_input = domain
    dname = dns.name.from_text(domain)

    result = rec_roots(dname)
    print_result(result)


def rec_roots(dname):
    for rip in root_ns:
        result = rec(rip, dname)
        if result:
            return result
    return None


def rec(ip, dname):
    query = dns.message.make_query(dname, dns.rdatatype.A)
    try:
        response = dns.query.udp(query, ip)
    except Exception:
        return None

    if len(response.answer) > 0:
        for ans in response.answer:
            if ans.rdtype == dns.rdatatype.A:
                return ans
            if ans.rdtype == dns.rdatatype.CNAME:
                cname_response.append(ans)
                return rec_roots(ans[0].target)  # recursive from root
    if len(response.additional) > 0:
        for rrset in response.additional:
            if rrset.rdtype != dns.rdatatype.A:
                continue
            for rr in rrset:
                result = rec(rr.address, dname)  # recursive
                if result:
                    return result
    if len(response.authority) > 0:
        for rrset in response.authority:
            if rrset.rdtype == dns.rdatatype.NS:
                rrset = rec_roots(rrset[0].target)  # recursive root
                result = rec(rrset[0].address, dname)  # recursive
                if result:
                    return result
    return None


# result
domain_input = ""
cname_response = []

# init
root_ns = ["198.41.0.4", "199.9.14.201", "192.33.4.12", "199.7.91.13", "192.203.230.10", "192.5.5.241", "192.112.36.4", "198.97.190.53", "192.36.148.17", "192.58.128.30", "193.0.14.129", "199.7.83.42"]
start_time = time.time()
main()



# My DNS Resolver
# www.google.com * 10 = 95 106 129 157 102 111 121 88 100 147              mean : 115.6  percentile : 100.5   127.0
# www.facebook.com * 10 = 234, 241, 220, 233, 216, 218, 299, 207, 231, 220 mean : 231.9  percentile : 218.50  233.75
# www.apple.com * 10 = 690 597 824 657 698 800 669 689 677 727             mean : 702.8  percentile : 671.00  719.75

# Local DNS Resolver
# www.google.com * 10 = 18 77 33 31 22 32 31 35 48 56          mean : 38.3    percentile : 31.00  44.75
# www.facebook.com * 10 = 35 41 31 23 20 57 26 26 29 35          mean : 32.3  percentile : 26     35
# www.apple.com * 10 = 32 35 32 32 24 82 46 27 48 30          mean : 38.8     percentile : 30.50  43.25

# Google's Public DNS
# www.google.com * 10 = 21 15 29 18 15 17 14 15 14 33          mean : 19.1  percentile : 15.00  20.25
# www.facebook.com * 10 = 17 18 15 16 15 47 27 24 21 10          mean :21   percentile : 15.25  23.25
# www.apple.com * 10 = 25 16 24 21 24 37 14 31 19 34          mean :24.5    percentile : 19.5   29.5
