import _thread, time, dns.resolver, sys
from threading import Thread
# import asyncio
from matplotlib import font_manager
import matplotlib.pyplot as plt
ansList = set()


def update(dorm):
    my_resolver = dns.resolver.Resolver()
    my_resolver.nameservers = ['8.8.8.8']
    try:
        answer = my_resolver.resolve(dorm)
    except Exception as e:
        print(str(e))
        return -1
    for i in answer:
        ansList.add(str(i))
    # print(ansList)

down_set = set()
temp_wrong = set()
right_set = set()
# 为线程定义一个函数
def dns_request(server,dorm):
    my_resolver = dns.resolver.Resolver()
    my_resolver.nameservers = [server]
    try:
        answer = my_resolver.resolve(dorm)
    except:
        down_set.add(server)
    else:
        resList = []
        for i in answer:
            resList.append(str(i))
        if not (set(resList).issubset(set(ansList)) or set(ansList).issubset(set(resList))):
            # print(resList)
            temp_wrong.add(server)
        else:
            right_set.add(server)


def classify(dorm):
    f = open("./credible_20210113.txt")
    # temp_wrong = set()
    print(temp_wrong)
    for i in range(5):
        update(dorm)
        time.sleep(1)
    i = 0
    threads = []
    for line in f:
        i += 1
        if i>1000:
            update(dorm)
            i = 0
        time.sleep(0.005)
        try:
            t = Thread(target=dns_request,args=(line.strip(),dorm))
            t.start()
            threads.append(t)
            # _thread.start_new_thread(dns_request, (line.strip(),dorm,temp_wrong))
        except:
            print("启动线程失败")
    f.close()
    for i in threads:
        i.join()
    return temp_wrong
dorm_list = ['google.com', 'amazon.cn', 'sina.com.cn','youtube.com']

def main():
    all_wrong = classify('baidu.com')
    part_wrong = set()
    for item in dorm_list:
        temp_wrong = classify(item)
        all_wrong = all_wrong & temp_wrong
        part_wrong = part_wrong | (temp_wrong-all_wrong)
        print(item, len(temp_wrong-all_wrong),len(part_wrong))
        temp_wrong = set()
    plt.rcParams['font.sans-serif'] = ['SimHei']
    sum = 9863
    all = len(all_wrong)
    part = len(part_wrong)
    down = len(down_set)
    right = len(right_set)
    labels = ['故障服务器', '响应错误结果的服务器', '选择性响应错误结果的服务器']
    nums = [down,all,part]
    print(nums)
    # plt.pie(nums,labels=labels, autopct='%3.2f%%')
    # # plt.legend(loc='lower left')
    # plt.title('DNS服务器状况统计')
    # plt.show()
    plt.bar(range(len(nums)),nums,tick_label=labels)
    plt.title('DNS服务器状况统计')
    plt.show()
main()