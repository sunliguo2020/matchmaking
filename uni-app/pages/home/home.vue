<template>
	<view class="container">
		<view class="search-bar">
			<input class="search-input" v-model="keyword" placeholder="搜索昵称或ID..." @confirm="searchUsers" />
			<button class="search-btn" @click="searchUsers">搜索</button>
		</view>
		
		<view class="filter-bar">
			<picker :range="genderOptions" @change="onGenderChange">
				<text class="filter-tag">{{genderText}}</text>
			</picker>
			<picker :range="cityOptions" @change="onCityChange">
				<text class="filter-tag">{{cityText}}</text>
			</picker>
		</view>

		<view v-if="loading" class="loading">
			<text>加载中...</text>
		</view>
		
		<view v-else-if="memberList.length === 0" class="empty">
			<text>暂无会员信息</text>
		</view>

		<view v-else class="member-list">
			<view v-for="item in memberList" :key="item.id" class="member-card" @click="goToDetail(item.user_id)">
				<image class="avatar" :src="item.avatarURL" mode="aspectFill"></image>
				<view class="info">
					<view class="name-row">
						<text class="nickname">{{item.nickname}}</text>
						<text class="age">{{item.age}}</text>
						<text class="vip-tag" v-if="item.isvip">VIP</text>
					</view>
					<view class="tags">
						<text class="tag">{{item.height}}</text>
						<text class="tag">{{item.weight}}</text>
						<text class="tag">{{item.education}}</text>
						<text class="tag">{{item.marriage}}</text>
					</view>
					<view class="detail-row">
						<text>{{item.jobs_title}}</text>
						<text>{{item.revenue}}</text>
						<text>{{item.city_name}}</text>
					</view>
				</view>
			</view>
		</view>
		
		<uni-pagination 
			v-if="total > 0"
			:current="currentPage" 
			:total="total" 
			@change="pageChange" />
	</view>
</template>

<script setup>
	import { ref, onMounted } from "vue"
	import { apiUsers } from "@/api/apis.js"
	
	const memberList = ref([]);
	const currentPage = ref(1);
	const total = ref(0);
	const loading = ref(false);
	const keyword = ref('');
	
	const genderOptions = ['全部', '男', '女'];
	const genderText = ref('性别');
	const genderValue = ref('');
	
	const cityOptions = ['全部', '潍坊市', '济南市', '青岛市'];
	const cityText = ref('城市');
	const cityValue = ref('');

	const getUsers = async (data = {}) => {
		loading.value = true;
		try {
			let params = {...data};
			if (keyword.value) {
				// 如果输入的是纯数字，按 user_id 搜索；否则按昵称搜索
				if (/^\d+$/.test(keyword.value)) {
					params.user_id = keyword.value;
				} else {
					params.nickname = keyword.value;
				}
			}
			if (genderValue.value) params.gender = genderValue.value;
			if (cityValue.value) params.city = cityValue.value;
			
			let res = await apiUsers(params);
			console.log('会员列表:', res);
			if (res.code === 200) {
				memberList.value = res.data || [];
				total.value = res.total_count || 0;
				currentPage.value = res.current_page || 1;
			} else {
				memberList.value = res.data || [];
				total.value = res.total_count || 0;
			}
		} catch(e) {
			console.error('获取会员列表失败:', e);
		} finally {
			loading.value = false;
		}
	};
	
	const searchUsers = () => {
		currentPage.value = 1;
		getUsers({page: 1});
	};
	
	const onGenderChange = (e) => {
		const idx = e.detail.value;
		genderText.value = genderOptions[idx];
		genderValue.value = idx === 0 ? '' : idx;
		currentPage.value = 1;
		getUsers({page: 1});
	};
	
	const onCityChange = (e) => {
		const idx = e.detail.value;
		cityText.value = cityOptions[idx];
		cityValue.value = idx === 0 ? '' : cityOptions[idx];
		currentPage.value = 1;
		getUsers({page: 1});
	};
	
	const pageChange = ({type, current}) => {
		currentPage.value = current;
		getUsers({page: current});
	};
	
	const goToDetail = (userId) => {
		uni.navigateTo({
			url: `/pages/userDetail/userDetail?id=${userId}`
		});
	};
	
	onMounted(() => {
		getUsers();
	});
</script>

<style lang="scss" scoped>
	.container {
		padding: 20rpx;
		background: #f5f5f5;
		min-height: 100vh;
	}
	
	.search-bar {
		display: flex;
		margin-bottom: 20rpx;
		
		.search-input {
			flex: 1;
			height: 72rpx;
			background: #fff;
			border-radius: 36rpx;
			padding: 0 30rpx;
			font-size: 26rpx;
		}
		
		.search-btn {
			width: 120rpx;
			height: 72rpx;
			line-height: 72rpx;
			margin-left: 16rpx;
			background: #28b389;
			color: #fff;
			border-radius: 36rpx;
			font-size: 26rpx;
			text-align: center;
		}
	}
	
	.filter-bar {
		display: flex;
		gap: 20rpx;
		margin-bottom: 20rpx;
		
		.filter-tag {
			display: inline-block;
			padding: 10rpx 30rpx;
			background: #fff;
			border-radius: 30rpx;
			font-size: 24rpx;
			color: #666;
		}
	}
	
	.loading, .empty {
		text-align: center;
		padding: 100rpx 0;
		color: #999;
		font-size: 28rpx;
	}
	
	.member-list {
		.member-card {
			display: flex;
			padding: 24rpx;
			margin-bottom: 20rpx;
			background: #fff;
			border-radius: 16rpx;
			box-shadow: 0 2rpx 10rpx rgba(0,0,0,0.05);
			
			.avatar {
				width: 160rpx;
				height: 200rpx;
				border-radius: 12rpx;
				margin-right: 20rpx;
				flex-shrink: 0;
			}
			
			.info {
				flex: 1;
				display: flex;
				flex-direction: column;
				justify-content: space-between;
				
				.name-row {
					display: flex;
					align-items: center;
					gap: 12rpx;
					
					.nickname {
						font-size: 32rpx;
						font-weight: bold;
						color: #333;
					}
					
					.age {
						font-size: 28rpx;
						color: #999;
					}
					
					.vip-tag {
						font-size: 20rpx;
						color: #fff;
						background: linear-gradient(135deg, #f5af19, #f12711);
						padding: 4rpx 12rpx;
						border-radius: 6rpx;
					}
				}
				
				.tags {
					display: flex;
					flex-wrap: wrap;
					gap: 8rpx;
					
					.tag {
						font-size: 22rpx;
						color: #28b389;
						background: #e8f8f0;
						padding: 4rpx 16rpx;
						border-radius: 6rpx;
					}
				}
				
				.detail-row {
					font-size: 24rpx;
					color: #999;
					display: flex;
					gap: 20rpx;
				}
			}
		}
	}
</style>
