<template>
	<view class="container">
		<view v-if="loading" class="loading">
			<text>加载中...</text>
		</view>
		<view v-else-if="user" class="detail">
			<!-- 头像和基本信息 -->
			<view class="profile-header">
				<image class="avatar" :src="user.avatarURL" mode="aspectFill" @click="previewAvatar"></image>
				<view class="basic-info">
					<view class="name-row">
						<text class="nickname">{{user.nickname}}</text>
						<text class="vip-tag" v-if="user.isvip">VIP</text>
					</view>
					<text class="desc">{{user.age}} · {{user.height}} · {{user.weight}} · {{user.education}}</text>
					<text class="desc">{{user.jobs_title}} · {{user.revenue}}</text>
					<text class="desc">{{user.city_name}}</text>
				</view>
			</view>

			<!-- 标签 -->
			<view class="section">
				<view class="section-title">个人标签</view>
				<view class="tags">
					<text class="tag">{{user.marriage}}</text>
					<text class="tag">{{user.height}}</text>
					<text class="tag">{{user.education}}</text>
					<text class="tag">{{user.revenue}}</text>
				</view>
			</view>

			<!-- 个人介绍 -->
			<view class="section" v-if="user.f_text">
				<view class="section-title">自我介绍</view>
				<text class="intro-text">{{user.f_text}}</text>
			</view>

			<!-- 相册 -->
			<view class="section" v-if="photos.length > 0">
				<view class="section-title">个人相册</view>
				<scroll-view class="photo-scroll" scroll-x>
					<image v-for="(photo, idx) in photos" :key="idx" :src="photo.image" mode="aspectFill" class="photo" @click="previewPhoto(idx)"></image>
				</scroll-view>
			</view>
		</view>
	</view>
</template>

<script setup>
	import { ref, onMounted } from "vue"
	import { apiUsers, apiUserPhotos } from "@/api/apis.js"
	
	const user = ref(null);
	const photos = ref([]);
	const loading = ref(true);
	
	onMounted(() => {
		const pages = getCurrentPages();
		const currentPage = pages[pages.length - 1];
		const userId = currentPage.$page?.options?.id;
		if (userId) {
			getUserDetail(userId);
			getUserPhotos(userId);
		} else {
			loading.value = false;
		}
	});
	
	const getUserDetail = async (userId) => {
		try {
			let res = await apiUsers({user_id: userId});
			if (res.code === 200 && res.data && res.data.length > 0) {
				user.value = res.data[0];
				// 解析 f_text JSON
				try {
					const ft = JSON.parse(user.value.f_text);
					if (Array.isArray(ft)) {
						user.value.f_text = ft.join('、');
					}
				} catch(e) {}
			}
		} catch(e) {
			console.error('获取用户详情失败:', e);
		} finally {
			loading.value = false;
		}
	};
	
	const getUserPhotos = async (userId) => {
		try {
			let res = await apiUserPhotos({user_id: userId});
			if (res.code === 200 && res.data && res.data.length > 0) {
				photos.value = res.data;
			}
		} catch(e) {
			console.error('获取用户相册失败:', e);
		}
	};
	
	const previewAvatar = () => {
		if (user.value?.avatarURL) {
			uni.previewImage({
				urls: [user.value.avatarURL]
			});
		}
	};
	
	const previewPhoto = (idx) => {
		const urls = photos.value.map(p => p.image);
		uni.previewImage({
			current: urls[idx],
			urls: urls
		});
	};
</script>

<style lang="scss" scoped>
	.container {
		background: #f5f5f5;
		min-height: 100vh;
	}
	
	.loading {
		text-align: center;
		padding: 100rpx 0;
		color: #999;
	}
	
	.profile-header {
		display: flex;
		padding: 40rpx;
		background: #fff;
		margin-bottom: 20rpx;
		
		.avatar {
			width: 200rpx;
			height: 250rpx;
			border-radius: 16rpx;
			margin-right: 30rpx;
			flex-shrink: 0;
		}
		
		.basic-info {
			flex: 1;
			display: flex;
			flex-direction: column;
			justify-content: center;
			
			.name-row {
				display: flex;
				align-items: center;
				gap: 12rpx;
				margin-bottom: 12rpx;
				
				.nickname {
					font-size: 36rpx;
					font-weight: bold;
					color: #333;
				}
				
				.vip-tag {
					font-size: 20rpx;
					color: #fff;
					background: linear-gradient(135deg, #f5af19, #f12711);
					padding: 4rpx 12rpx;
					border-radius: 6rpx;
				}
			}
			
			.desc {
				font-size: 26rpx;
				color: #999;
				line-height: 1.8;
			}
		}
	}
	
	.section {
		background: #fff;
		padding: 30rpx;
		margin-bottom: 20rpx;
		
		.section-title {
			font-size: 30rpx;
			font-weight: bold;
			color: #333;
			margin-bottom: 20rpx;
		}
		
		.tags {
			display: flex;
			flex-wrap: wrap;
			gap: 12rpx;
			
			.tag {
				font-size: 24rpx;
				color: #28b389;
				background: #e8f8f0;
				padding: 8rpx 24rpx;
				border-radius: 8rpx;
			}
		}
		
		.intro-text {
			font-size: 26rpx;
			color: #666;
			line-height: 1.8;
		}
		
		.photo-scroll {
			white-space: nowrap;
			
			.photo {
				width: 200rpx;
				height: 200rpx;
				border-radius: 12rpx;
				margin-right: 16rpx;
				display: inline-block;
			}
		}
	}
</style>
