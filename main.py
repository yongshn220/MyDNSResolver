import queue
import sys
import dns.resolver


def main(name):
    result = rec_roots(name)
    print(result)


def rec_roots(dname):
    for rip in root_ns:
        result = rec(rip, dname)
        if result:
            return result
    return None


def rec(ip, dname):
    query = dns.message.make_query(dname, dns.rdatatype.A)
    response = dns.query.tcp(query, ip)
    if not response:
        return None

    if len(response.answer) > 0:
        for ans in response.answer:
            if ans.rdtype == dns.rdatatype.A:
                return ans
            if ans.rdtype == dns.rdatatype.CNAME:
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


domain = 'www.cnn.com'
dname = dns.name.from_text(domain)
root_ns = [ "198.41.0.4", "199.9.14.201", "192.33.4.12", "99.7.91.13", "192.203.230.10", "192.5.5.241", "192.112.36.4", "198.97.190.53", "192.36.148.17", "192.58.128.30", "193.0.14.129", "199.7.83.42"]

main(dname)