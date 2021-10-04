import _thread, time, dns.resolver, pymysql, json
from flask import Flask, redirect, url_for, request
import geoip2.database
app = Flask(__name__)

conn = pymysql.connect(host="localhost", user = "iwereA", passwd="yiwen170200126", db="abnormal_ip")
cur = conn.cursor()
ansList = set()
wrong_list = []
reader1 = geoip2.database.Reader('./GeoLite2-ASN_20210413/GeoLite2-ASN.mmdb')
reader2 = geoip2.database.Reader('./GeoLite2-Country_20210413/GeoLite2-Country.mmdb')
@app.route('/success')
def success():
   return 'DNS解析异常服务器保存成功！'
@app.route('/fail')
def fail():
   return 'DNS解析异常服务器保存失败！'

@app.route('/lookup',methods = ['POST', 'GET'])
def lookup():
   if request.method == 'POST':
      dorm = request.form['dnm']
      for i in range(5):
         update(dorm)
         time.sleep(1)
      f = open("./credible_20210113.txt")
      i = 0
      for line in f:
         i += 1
         if i>=1000:
            update(dorm)
            i = 0
         time.sleep(0.005)
         try:
            _thread.start_new_thread(dns_request, (line.strip(),dorm))
         except:
            time.sleep(0.005)
            try:
               _thread.start_new_thread(dns_request, (line.strip(),dorm))
            except:
               print("启动线程失败")
      f.close()
      print(wrong_list)
      ips = json.dumps(wrong_list)
      sql1 = 'select * from ips where dorm = %s'
      sql3 = 'update ips set iplist = %s where dorm=%s'
      cur.execute(sql1, dorm)
      iplist1 = cur.fetchall()
      if iplist1:
         cur.execute(sql3,[ips,dorm])
         conn.commit()
      else:
         sql2 = 'insert ips(dorm,iplist) values(%s,%s)'
         cur.execute(sql2,[dorm,ips])
         conn.commit()
      return redirect(url_for('success'))
   else:
      return redirect(url_for('fail'))

#线程函数
def dns_request(server,dorm):
   my_resolver = dns.resolver.Resolver()
   my_resolver.nameservers = [server]
   try:
      answer = my_resolver.resolve(dorm)
   except:
      temp_dict = search_as(server)
      wrong_list.append(temp_dict)
   else:
      resList = []
      for i in answer:
         resList.append(str(i))
      if not (set(resList).issubset(ansList) or ansList.issubset(set(resList))):
         temp_dict = search_as(server)
         wrong_list.append(temp_dict)

def update(dorm):
   my_resolver = dns.resolver.Resolver()
   # my_resolver.nameservers = ['8.8.8.8']
   try:
      answer = my_resolver.resolve(dorm)
   except Exception as e:
      print(str(e))
   for i in answer:
      ansList.add(str(i))
   print(ansList)

def search_as(ip):
   try:
      asnum = reader1.asn(ip).autonomous_system_number
      country = reader2.country(ip).country.names['zh-CN']
      if country == '香港' or country == '台湾':
         country = '中国' + country
   except:
      asnum = 'None'
      country = 'Unknown'
   temp_dict = {'ip':ip,'as':asnum,'country':country}
   return temp_dict

if __name__ == '__main__':
   app.run(debug = True)
