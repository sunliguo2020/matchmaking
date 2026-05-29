<template>
	<view>
		<view v-for="item in anliList" :key="item._id" class="anli-item">
			<view class="header">
				<image class="avatar" :src="item.avatar" mode="aspectFill"></image>
				<text class="nickname">{{item.nickname}}</text>
			</view>
			<view class="content">{{item.content}}</view>
			<view class="images" v-if="item.imgurl && item.imgurl.length > 0">
				<image v-for="(img, idx) in item.imgurl" :key="idx" :src="img" mode="aspectFill" class="anli-image" @click="previewImage(img, item.imgurl)"></image>
			</view>
			<view class="meta">
				<text>❤ {{item.hits}}</text>
				<text>{{item.addtime}}</text>
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
	import { apiAnli } from "@/api/apis.js"
	
	const anliList = ref([]);
	const currentPage = ref(1);
	const total = ref(0);

	const getAnli = async (data = {}) => {
		try {
			let res = await apiAnli(data);
			console.log('API返回:', res);
			if (res.code === 200) {
				anliList.value = res.data || [];
				total.value = res.total_count || 0;
				currentPage.value = res.current_page || 1;
			} else {
				anliList.value = res.data || [];
				total.value = res.total_count || 0;
			}
		} catch(e) {
			console.error('获取案例失败:', e);
		}
	};
	
	const pageChange = ({type, current}) => {
		currentPage.value = current;
		getAnli({page: current});
	};
	
	const previewImage = (current, urls) => {
		uni.previewImage({
			current: current,
			urls: urls
		});
	};
	
	onMounted(() => {
		getAnli();
	});
</script>

<style lang="scss" scoped>
	.anli-item {
		padding: 20rpx;
		margin: 20rpx;
		background: #fff;
		border-radius: 12rpx;
		box-shadow: 0 2rpx 10rpx rgba(0,0,0,0.05);
		
		.header {
			display: flex;
			align-items: center;
			margin-bottom: 16rpx;
			
			.avatar {
				width: 60rpx;
				height: 60rpx;
				border-radius: 50%;
				margin-right: 16rpx;
			}
			
			.nickname {
				font-size: 28rpx;
				font-weight: bold;
				color: #333;
			}
		}
		
		.content {
			font-size: 26rpx;
			color: #666;
			line-height: 1.6;
			margin-bottom: 16rpx;
		}
		
		.images {
			display: flex;
			flex-wrap: wrap;
			gap: 10rpx;
			margin-bottom: 16rpx;
			
			.anli-image {
				width: 200rpx;
				height: 200rpx;
				border-radius: 8rpx;
			}
		}
		
		.meta {
			display: flex;
			justify-content: space-between;
			font-size: 22rpx;
			color: #999;
		}
	}
</style>
