#!/usr/local/python3
from scapy.all import *
import struct,re,random,_thread,threading
import time, geoip2.database


hijack_set = set()
# timestr = time.strftime("%Y%m%d%H%M%S", time.localtime(time.time()))
reader = geoip2.database.Reader('./GeoLite2-Country_20210413/GeoLite2-Country.mmdb')
# 跟我们实现ping程序的想法是一样的，首先构造一个发送一个UDP报文的函数，
# 入参为目的地址，ttl数。
def traceroute_one(dst,ttl_no,dport):
    # 定义发包时间。
    send_time = time.time()
    try:
        # 发送一个包，接收一个包。
        traceroute_one_reply = sr1(IP(dst=dst, ttl=ttl_no) / UDP(dport=dport) / DNS(qd=DNSQR(qname='baidu.com',qtype=1,qclass=1), an = None), timeout=1,
                                   verbose=False)
        # 判断ICMP包是不是超时回答。
        if traceroute_one_reply.getlayer(ICMP).type == 11 and traceroute_one_reply.getlayer(ICMP).code == 0:
            # 提取源地址
            src_ip = traceroute_one_reply.getlayer(IP).src
            # 定义接收时间。
            recv_time = time.time()
            # 计算时间ms数
            mid_time = (recv_time - send_time) * 1000
            # 返回。
            return 1,src_ip,mid_time
        # 这里接接收的是最后一跳。ICMP应该是端口不可达。
        elif traceroute_one_reply.getlayer(ICMP).type == 3 and traceroute_one_reply.getlayer(ICMP).code == 3:
            # 下边处理是一样的。
            src_ip = traceroute_one_reply.getlayer(IP).src
            recv_time = time.time()
            mid_time = (recv_time - send_time) * 1000
            return 2, src_ip, mid_time
    except Exception as e:
        return None


def amend_traceroute(dst,hops):
    #初始化traceroute字典
    trace_dict = first_traceroute(dst,hops)
    # 目的端口从33434开始算起，入参为目的地址，我们想要查找的路由的条数。
    dport = 33434
    hop = 0
    # 进行循环包。
    while hop < hops:
        hop += 1
        # 这里需要改变端口。
        dport += hop
        # 发送一个包，获取返回值。
        traceroute_result = traceroute_one(dst,hop,dport)
        # 如果出现了错误，打印*号。
        if traceroute_result == None:
            pass
        # 这里代表中间路由，我们进行打印信息。
        elif traceroute_result[0] == 1:
            trace_dict[hop] = traceroute_result[1]
            # print("%d %s %4.2fms" % (hop,traceroute_result[1],traceroute_result[2]))
        # 最后一个包，为端口不可达，打印信息后，需要退出循环，因为已经到达目的地址了，虽然可能没有达到我们定义的条数。
        elif traceroute_result[0] == 2:
            trace_dict[hop] = traceroute_result[1]
            # print("%d %s %4.2fms" % (hop, traceroute_result[1], traceroute_result[2]))
            break
        time.sleep(0.05)
    return trace_dict

def first_traceroute(target,hops):
    trace_dict = {}
    res, unans = traceroute(target, maxttl=hops, verbose=False)
    for snd,rcv in res:
        trace_dict[snd.ttl] = str(rcv.src)
    return trace_dict

def search_p(ip):
   try:
      country = reader.country(ip).country.names['zh-CN']
      if country == '香港' or country == '台湾' or country == '澳门':
         country = '中国' + country
   except:
      country = 'Unknown'
   return country

def get_row():
    filename = r'HijackList.xls'
    workbook1 = xlrd.open_workbook(filename, formatting_info=True)
    sheet = workbook1.sheet_by_index(0)
    return sheet.nrows

def trace(address, port):
    trace_dict = amend_traceroute(address, 64)
    # trace_dict.sorted(trace_dict.items(),lambda x:x[0])
    # f1 = open(timestr + '.txt', 'a')
    ttl = 1
    while(ttl<=64):
        ttl += 1
        pkt = IP(dst=address, ttl=ttl)\
              /UDP(sport=12345, dport=port)\
              /DNS(qd=DNSQR(qname='amazon.com',qtype=1,qclass=1), an = None)
        ans = sr1(pkt,timeout=1,verbose=False)
        if ans and ans.summary().find('error')==-1:
            # print(ttl,ans.getlayer(IP).src)
            if ttl in trace_dict:
                if address != trace_dict[ttl]:
                    print("The package was hijacked by %s(1)"%trace_dict[ttl])
                    # str1 = trace_dict[ttl]+' '+search_p(trace_dict[ttl]) + ' ' +search_p(address) + '\n'
                    # f1.write(str1)
                    hijack_set.add(trace_dict[ttl])
                else:
                    print("Safe")
            else:
                p = sr1(IP(dst=address, ttl=ttl) / ICMP(), timeout=1, verbose=False)
                if p:
                    if p.fields['src'] == address:
                        print("Safe")
                    else:
                        print("The package was hijacked by %s(2)" % p.fields['src'])
                        # str1 = trace_dict[ttl] + ' ' + search_p(p.fields['src']) + '\n'
                        # f1.write(str1)
                        hijack_set.add(p.fields['src'])
                else:
                    print("Unknown")
            break
        time.sleep(0.05)
    # f1.close()
    if ttl>64:
        pass
    print(hijack_set)
    pass

if __name__ == "__main__":
    # for i in range(1, 8):
    #     for j in range(1,8):
    #         time.sleep(0.5)
    #         ip = '2.14.{}.{}'.format(str(i),str(j))
    #         try:
    #             t1 = threading.Thread(target=trace, args=(ip,53))
    #             t1.start()
    #         except Exception as e:
    #             print(str(e))
            # trace(ip, 53)
    f = open("./credible_20210113.txt")
    list = f.readlines()[1200:1231]
    i = 0
    for line in list:
        i += 1
        if i >= 500:
            time.sleep(300)
            i = 0
        time.sleep(0.05)
        try:
            t1 = threading.Thread(target=trace, args=(line.strip(), 53))
            t1.start()
        except Exception as e:
            print(str(e))
        # trace(line.strip(), 53)
    # print(len(hijack_set))
    # for item in hijack_set:
    #     print(item)
    f.close()