import dns.message
import dns.query


def recursive_resolve(domain_name, ns):
    query = dns.message.make_query(domain_name, dns.rdatatype.A)
    response = dns.query.udp(query, ns)

    if response.answer:
        # Return the first A record found in the answer section
        for rr in response.answer:
            if rr.rdtype == dns.rdatatype.A:
                return str(rr.address)
    else:
        # If no answer is found, check the authority section
        for rr in response.additional:
            if rr.rdtype == dns.rdatatype.NS:
                # Get the nameserver name
                ns_name = str(rr[0].target)
                # Recursively resolve the nameserver name to an IP address
                ns_ip = recursive_resolve(ns_name, ns)
                # Query the nameserver for the domain name
                return recursive_resolve(domain_name, ns_ip)


# Start the resolution process with the root name servers
root_ns = ['198.41.0.4', '192.228.79.201', '192.33.4.12', '199.7.91.13', '192.203.230.10']
domain_name = "example.com"
ip_address = recursive_resolve(domain_name, root_ns[0])

if ip_address:
    print(f"{domain_name} resolved to {ip_address}")
else:
    print(f"Failed to resolve {domain_name}")