import sys
import dns.resolver
import datetime
import time
import math


def send_error(code):
    if code == 1:
        print("Invalid")
        print("Usage: ./main.py [domain]")
        exit(0)
    if code == 2:
        print(f"Error: No corresponding IP to [{domain_input}].")
        exit(0)

def print_result(result):
    if result is None:
        send_error(2)

    print("QUESTION SECTION:")
    print(f"{domain_input} IN A")
    print("")
    print("ANSWER SECTION:")
    for cname in cname_response:
        print(cname)
    print(result)
    print("")
    print(f"Query time: {math.ceil((time.time() - start_time) * 1000)} msec")
    print(f"When: {datetime.datetime.now()}")


def main():
    global domain_input
    domain = None
    if len(sys.argv) == 1:
        domain = input()
    elif len(sys.argv) == 2:
        domain = sys.argv[1]
    else:
        send_error(0)
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
        response = dns.query.tcp(query, ip)
    except Exception:
        return send_error(2)

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
    return None


# result
domain_input = ""
cname_response = []

# init

root_ns = ["198.41.0.4", "199.9.14.201", "192.33.4.12", "199.7.91.13", "192.203.230.10", "192.5.5.241", "192.112.36.4", "198.97.190.53", "192.36.148.17", "192.58.128.30", "193.0.14.129", "199.7.83.42"]
start_time = time.time()
main()