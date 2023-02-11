import sys
import dns.resolver
from dns.rcode import Rcode

_root_ns = [
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


_domain = ''
_spl = []
_spl_index = 0
_cspl = ''


def set_domain(dom):
    global _domain, _spl, _spl_index, _cspl
    _domain = dom
    _splits = _domain.split('.')
    spl = []
    for i in range(len(_splits)):
        _spl.append('.'.join(_splits[len(_splits) - i - 1:]))
    _spl_index = 0
    _cspl = _spl[_spl_index]


def main():
    global _domain, _spl, _spl_index, _cspl

    set_domain('cnn-tls.map.fastly.net')
    test_cspl = 'cnn-tls.map.fastly.net'
    test_server = '185.31.17.78'

    root_index = 0
    server = _root_ns[root_index]
    while True:
        log("[spl]", _cspl)
        query = dns.message.make_query(_cspl, dns.rdatatype.NS)
        response = dns.query.tcp(query, server)

        answer = response.answer
        additional = response.additional
        log("answer", answer)
        log("additional", additional)

        if len(answer) > 0:
            log(answer)
            set_domain(_domain)
            root_index += 1
            server = _root_ns[root_index]
            continue

            if _cspl != _domain:
                _spl_index += 1
                cspl = _spl[_spl_index]
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
                    _spl_index += 1
                    _cspl = _spl[_spl_index]
                    break
        else:
            set_domain(_domain)
            root_index += 1
            server = _root_ns[root_index]
            continue


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

