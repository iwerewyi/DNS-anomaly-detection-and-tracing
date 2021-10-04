<template>
	<div>
		<p style="font-size: 20px;">DNS异常检测系统</p>
		<el-row>
			<el-select v-model="dorm" placeholder="请选择">
		    <el-option
		      v-for="item in dormList"
		      :key="item.index"
		      :value="item.dorm">
		    </el-option>
		  </el-select>
		  <el-button type="primary" plain @click="showList">提交</el-button>
		</el-row>
		<div v-if = "ipList.length">
			<el-table
		      :data="ipList"
		      stripe
		      style="width: 80%;margin: 0 auto;"
		      :cell-style="rowClass"  
		      :header-cell-style="headClass">
		      <el-table-column
		        prop="ip"
		        label="服务器IP"
		        width="180">
		      </el-table-column>
		      <el-table-column
		        prop="as"
		        label="自治系统号（AS号）"
		        width="180">
		      </el-table-column>
		      <el-table-column
		        prop="country"
		        label="地区">
		      </el-table-column>
		    </el-table>
		</div>
		<div v-else>
			<el-alert class="boxes"
			    title="暂无异常DNS服务器"
			    type="warning"
			    center
			    :closable="false">
			</el-alert>
		</div>
	</div>
</template>

<script>
  export default {
    data() {
      return {
        value: '',
        dormList: [],
        dorm: '',
        ipList:[],
        loading: false,
      }
    },
    async created() {
			this.dormList = await this.showDorm();
	},
	methods:{
		showDorm(){
			return new Promise((resolve, reject) => {
					this.$axios.get('/api/viewDorm')
						.then((response) => {
							resolve(response.data);
						}).catch(function(error) {
							reject(error);
						})
				})
		},
		showList(){
			if(this.dorm==''){
				this.$message({
						message: '请选择域名！',
						type: 'error',
						customClass: 'zZindex'
					});
			}
			else{
				this.$axios.post('/api/showList',{
						dorm: this.dorm
					})
					.then((response) => {
						if(response.data[0].iplist!='[]'){
							this.ipList = JSON.parse(response.data[0].iplist)
							console.log(this.ipList.length)
						}else{
							this.ipList = []
						}
						
					}).catch(function(error) {
						console.log(error);
					})
			}
		},
		 headClass () {
            return 'text-align: center;background:rgb(242,242,242);color:rgb(140,138,140)'
        },
            // 表格样式设置
        rowClass () {
            return 'text-align: center;'
        }
	}
  }
</script>
<style type="text/css">
	.boxes {
		border: 10px;
		height: 50px;
		width: 80%;
		margin: 0 auto;
	}
</style>