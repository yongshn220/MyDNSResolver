import dns.message
import dns.query

domain = "www.naver.com"
dname = dns.name.from_text(domain)
for i in range(len(dname)):
    spl = dname.split(i+1)
    print(spl)
    print(spl[1])
    print(type(spl[1]))