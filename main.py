import sys
import dns.resolver
from dns.rcode import Rcode

rootNSs = [
    "198.41.0.4",
    "199.9.14.201",
    "192.33.4.12",
    "99.7.91.13",
    "192.203.230.10",
    "192.5.5.241",
    "192.112.36.4",
    "198.97.190.53",
    "192.36.148.17",
    "192.58.128.30",
    "193.0.14.129",
    "199.7.83.42"]


# if len(sys.argv) != 2:
#     print("Invalid number of arguments :: Please provide 1 argument for domain name.")
#     exit(0)

domain = "www.naver.com"
name = dns.name.from_text(domain)
depth = 2
nextNSs = rootNSs


while True:
    splitName = name.split(depth)
    sub = splitName[1]
    print("sub : ", sub)

    query = dns.message.make_query(sub, dns.rdatatype.NS)
    print("query : ", query)

    for ns in nextNSs:
        response = dns.query.tcp(query, ns)
        print(response)

        if response.rcode() == Rcode.NOERROR:
            break




