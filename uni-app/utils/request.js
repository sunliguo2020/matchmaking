const BASE_URL = "https://tea.qingnian8.com/api/bizhi"

//使用Promise()方法封装了uni-app的uni.request方法
export function request(config = {}) {
	//resolve 成功  reject 失败
	return new Promise((resolve, reject) => {
		//解构参数
		let {
			url,
			method = "GET",
			header = {},
			data = {} //转换为string类型
		} = config;
		
		//url不是http开头，则
		if(!url.startsWith("https://") && !url.startsWith("http://")){
			url = BASE_URL + url;
		}
		
		uni.request({
			url,
			data,
			method,
			header,
			//请求成功后的回调函数
			success: res => {
				console.log('请求成功返回的res',res)
				if (res.code == 2000) {
					resolve(res.data);
				} else if (res.code === 400) {
					uni.showModal({
						title: "错误提示",
						content: res.msg,
						showCancel: false
					})
					reject(res.data.data)
				} else {
					uni.showModal({
						title: res.data.errMsg,
						icon: "none",
					});
					rejct(res.data.data);
				}
			},
			//请求失败后的回调函数
			fail: err => {
				console.log('请求失败返回',err)
				uni.showToast({
					title:'请求失败',
					showCancel:false,
					icon:"error",
				})
				reject(err);
			},
			//接口调用结束的回调函数
			complete:()=>{
				console.log(url,"请求结束");
			}
		})
	})
}