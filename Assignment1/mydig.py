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
        print("Usage: ./mydig.py [domain]")
        exit(0)
    if code == 2:
        print(f"Error: No corresponding IP to [{domain_input}].")


def print_result(answer, result):
    if answer is None:
        send_error(2)
        exit(0)

    print("QUESTION SECTION:")
    print(f"{domain_input.ljust(37)}  {'IN'.ljust(5)} {'A'.ljust(6)}")
    print("")
    if result:
        print("ANSWER SECTION:")
    else:
        print("AUTHORITY SECTION:")
    for cname in cname_response:
        print(str(cname.name).ljust(30), str(cname.ttl).ljust(7), str_rdclass(cname[0].rdclass).ljust(5), str_rdtype(cname[0].rdtype).ljust(5), str(cname[0].target))
    print(str(answer.name).ljust(30), str(answer.ttl).ljust(7), str_rdclass(answer[0].rdclass).ljust(5), str_rdtype(answer[0].rdtype).ljust(5), answer[0].address)
    print("")
    print(f"Query time: {math.ceil((time.time() - start_time) * 1000)} msec")
    print(f"When: {datetime.datetime.now()}")


def main():
    global domain_input
    domain = None
    # Input Handling
    if len(sys.argv) == 1:
        domain = input("Enter domain name: ")
    elif len(sys.argv) == 2:
        domain = sys.argv[1]
    else:
        send_error(1)
    domain_input = domain
    dname = dns.name.from_text(domain)

    answer, result = rec_roots(dname)
    print_result(answer, result)


# search from the root name server
def rec_roots(dname):
    for rip in root_ns:
        answer, result = rec(rip, dname)
        if answer:
            return answer, result
    return None, False


# recursively search following domain with ip.
def rec(ip, dname):
    query = dns.message.make_query(dname, dns.rdatatype.A)
    try:
        response = dns.query.udp(query, ip)
    except Exception:
        return None, False

    if len(response.answer) > 0:
        for ans in response.answer:
            if ans.rdtype == dns.rdatatype.A:
                return ans, True
            if ans.rdtype == dns.rdatatype.CNAME:
                cname_response.append(ans)
                return rec_roots(ans[0].target)  # recursive from root
    if len(response.additional) > 0:
        for rrset in response.additional:
            if rrset.rdtype != dns.rdatatype.A:
                continue
            for rr in rrset:
                answer, result = rec(rr.address, dname)  # recursive
                if answer:
                    return answer, result
                else:
                    return rrset, result
    if len(response.authority) > 0:
        for rrset in response.authority[0]:
            if rrset.rdtype == dns.rdatatype.NS:
                arrset, result = rec_roots(rrset.target)  # recursive root
                answer, result = rec(arrset[0].address, dname)  # recursive
                if answer:
                    return answer, result
                else:
                    return rrset, result
    return None, False


# result
domain_input = ""
cname_response = []

# init
root_ns = ["198.41.0.4", "199.9.14.201", "192.33.4.12", "199.7.91.13", "192.203.230.10", "192.5.5.241", "192.112.36.4", "198.97.190.53", "192.36.148.17", "192.58.128.30", "193.0.14.129", "199.7.83.42"]
start_time = time.time()
main()
