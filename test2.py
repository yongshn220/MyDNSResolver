"""
resolve.py: a recursive resolver built using dnspython
"""

import argparse

import dns.message
import dns.name
import dns.query
import dns.rdata
import dns.rdataclass
import dns.rdatatype

FORMATS = (("CNAME", "{alias} is an alias for {name}"),
           ("A", "{name} has address {address}"),
           ("AAAA", "{name} has IPv6 address {address}"),
           ("MX", "{name} mail is handled by {preference} {exchange}"))

# current as of 19 March 2018
ROOT_SERVERS = ("198.41.0.4",
                "199.9.14.201",
                "192.33.4.12",
                "199.7.91.13",
                "192.203.230.10",
                "192.5.5.241",
                "192.112.36.4",
                "198.97.190.53",
                "192.36.148.17",
                "192.58.128.30",
                "193.0.14.129",
                "199.7.83.42",
                "202.12.27.33")

simple_cache = {}
sophis_cache = {}


def collect_results(name: str) -> dict:
    """
    This function parses final answers into the proper data structure that
    print_results requires. The main work is done within the `lookup` function.
    """
    if name in simple_cache:
        return simple_cache[name]
    full_response = {}
    target_name = dns.name.from_text(name)
    # lookup CNAME
    response = lookup(target_name, dns.rdatatype.CNAME)
    cnames = []
    if response:
        answers = response.answer
        for answer in answers:
            target_name = dns.name.from_text(str(answer[0]))
            cnames.append({"name": target_name, "alias": name})
    # lookup A
    response = lookup(target_name, dns.rdatatype.A)
    arecords = []
    for answers in response.answer:
        a_name = answers.name
        for answer in answers:
            if answer.rdtype == 1:  # A record
                arecords.append({"name": a_name, "address": str(answer)})
    # lookup AAAA
    response = lookup(target_name, dns.rdatatype.AAAA)
    aaaarecords = []
    for answers in response.answer:
        aaaa_name = answers.name
        for answer in answers:
            if answer.rdtype == 28:  # AAAA record
                aaaarecords.append({"name": aaaa_name, "address": str(answer)})
    # lookup MX
    response = lookup(target_name, dns.rdatatype.MX)
    mxrecords = []
    for answers in response.answer:
        mx_name = answers.name
        for answer in answers:
            if answer.rdtype == 15:  # MX record
                mxrecords.append({"name": mx_name,
                                  "preference": answer.preference,
                                  "exchange": str(answer.exchange)})

    full_response["CNAME"] = cnames
    full_response["A"] = arecords
    full_response["AAAA"] = aaaarecords
    full_response["MX"] = mxrecords
    simple_cache[name] = full_response
    print(full_response)
    return full_response


def lookup(target_name: dns.name.Name,
           qtype: dns.rdata.Rdata) -> dns.message.Message:
    """
    This function uses a recursive resolver to find the relevant answer to the
    query.
    """
    split = str(target_name).split(".")
    domain = split[len(split)-2]
    if domain not in sophis_cache:
        sophis_cache[domain] = {}
    response = None
    for r_server in ROOT_SERVERS:
        if r_server in sophis_cache[domain]:
            response = sophis_cache[domain][r_server]
        else:
            response = queryServer(target_name, qtype, r_server)
            sophis_cache[domain][r_server] = response
        if response:
            if response.answer:
                return response
            elif response.additional:
                for additional in response.additional:
                    if additional.rdtype != 1:
                        continue
                    for add in additional:
                        new_response = lookupRecursive(target_name,
                                                       qtype, str(add))
                        if new_response:
                            return new_response
    return None


def queryServer(target_name: dns.name.Name,
                qtype: dns.rdata.Rdata, ipAddr: str) -> dns.message.Message:
    """
    Makes a udp query to a given ip address, takes care of exceptions
    """
    outbound_query = dns.message.make_query(target_name, qtype)
    response = None
    try:
        response = dns.query.udp(outbound_query, ipAddr, 3)
    except Exception as e:
        response = None
    return response


def lookupRecursive(target_name: dns.name.Name,
                    qtype: dns.rdata.Rdata,
                    ipAddr: str) -> dns.message.Message:
    """
    Recursive lookup that starts from TLD and goes to the lowest level
    """
    response = queryServer(target_name, qtype, ipAddr)
    if response:
        if response.answer:
            for answer in response.answer:
                if answer.rdtype == 5 and qtype != 5:
                    target_name = dns.name.from_text(str(answer[0]))
                    return lookup(target_name, qtype)
            return response
        elif response.additional:
            for additional in response.additional:
                if additional.rdtype != 1:
                    continue
                for add in additional:
                    ip = str(add)
                    new_response = lookupRecursive(target_name, qtype, ip)
                    if new_response:
                        return new_response
    return response


def print_results(results: dict) -> None:
    """
    take the results of a `lookup` and print them to the screen like the host
    program would.
    """
    for rtype, fmt_str in FORMATS:
        for result in results.get(rtype, []):
            print(fmt_str.format(**result))


def main():
    """
    if run from the command line, take args and call
    printresults(lookup(hostname))
    """
    argument_parser = argparse.ArgumentParser()
    argument_parser.add_argument("name", nargs="+",
                                 help="DNS name(s) to look up")
    argument_parser.add_argument("-v", "--verbose",
                                 help="increase output verbosity",
                                 action="store_true")
    program_args = argument_parser.parse_args()
    for a_domain_name in program_args.name:
        result = collect_results(a_domain_name)
        if (result != -1):
            print_results(result)

if __name__ == "__main__":
    main()