var express = require('express');
var router = express.Router();
var mysql = require('mysql');

// 连接数据库
//var conn1 = mysql.createconn1ection(models.mysql);
//conn1.conn1ect();
var conn1 = mysql.createConnection({
	 host: 'localhost',
   user: 'iwereA',
   password: 'yiwen170200126',
   database: 'abnormal_ip',
   port: '3306'
});

//显示所有已监测的域名
router.get('/viewDorm', (req, res) => {
    var sql = "select dorm from ips"
    conn1.query(sql,function(err, result) {
        if (err) {
            console.log(err);
        }
        else {
        	return res.json(result)
		}
    })
});
//显示出现问题的服务器IP
router.post('/showList', (req, res) => {
    var sql = "select iplist from ips where dorm = ?"
    var dorm = req.body.dorm
	conn1.query(sql,dorm,function(err, result){
        if (err) {
            console.log(err);
            return res.json({
        		status: 1,
	    		msg:'查询失败'
        	})	        	
		}
        else{
//      	console.log(result)
        	return res.json(result)
        }
    })
    
});

module.exports = router;