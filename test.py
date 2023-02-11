import sys
import dns.resolver
from dns.rcode import Rcode


# def resolveDNS():
#     domain = "google.com"
#     resolver = dns.resolver.Resolver();
#     answer = resolver.resolve(domain , "A")
#     return answer
#
#
# resultDNS = resolveDNS()
# answer = ''
#
# for item in resultDNS:
#     resultant_str = ','.join([str(item), answer])
#     print(resultant_str)
# exit(0)


def main():
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

    # domain = "www.cnn.com"
    domain = 'cnn-tls.map.fastly.net'
    splits = domain.split('.')
    spl = []
    for i in range(len(splits)):
        spl.append('.'.join(splits[len(splits)-i-1:]))
    spl_index = 0
    cspl = spl[spl_index]

    servers = rootNSs
    server = rootNSs[5]
    server_index = 0
    result = ""

    test_cspl = 'cnn-tls.map.fastly.net'
    test_server = '185.31.17.78'
    while True:
        log("[spl]", cspl)
        query = dns.message.make_query(cspl, dns.rdatatype.NS)
        response = dns.query.tcp(query, server)

        answer = response.answer
        additional = response.additional
        log("answer", answer)
        log("additional", additional)

        if len(answer) > 0:
            if cspl != domain:
                spl_index += 1
                cspl = spl[spl_index]
                server = answer[0][0].address
                continue
            if answer[0].rdtype == dns.rdatatype.A:
                result = answer
                break
            if answer[0].rdtype == dns.rdatatype.CNAME:
                cspl = str(answer[0][0].target)
                continue

        elif len(additional) > 0:
            for rrset in additional:
                log("rrset", rrset)
                if rrset[0].rdtype == dns.rdatatype.A:
                    server = rrset[0].address
                    spl_index += 1
                    cspl = spl[spl_index]
                    break
        else:
            server_index += 1
            server = rootNSs[server_index]


    print_result(result)


def print_result(result):
    print("------------result------------")
    print("result : ", result)
    print("------------------------------")


def log(name, log):
    print(f"-------{name}-------")
    print(log)
    print(f"--------------------")

main()

