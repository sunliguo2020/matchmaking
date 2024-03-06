<template>
	<view>
		<view v-for="item in anli.result">
			<text>{{item.nickname}}</text>
			<view class="avatar">
				<image :src="item.avatar"></image>
			</view>
			<text>{{item._id}}</text>
			<view>{{item.content}}</view>
			<view v-for="i in item.imgurl">
				<image :src="i"></image>
			</view>
		</view>
		<uni-pagination :current="anli.current_page" :total="anli.total_count" @change="pageChange"  title="标题文字" />
	</view>
</template>

<script setup>
	import {
		ref
	} from "vue"
	import {
		apiAnli
	} from "@/api/apis.js"
	const anli = ref([]);

	const getAnli = async (data) => {
		let res = await apiAnli(data);
		console.log(res);
		anli.value = res.data;
	};
	getAnli()
	
	const pageChange = ({type,current})=>{
		console.log(type,current)
		getAnli({page:current})
	}
</script>

<style lang="scss" scoped>
	.avatar {
		image {
			width: 50rpx;
			height: 50rpx;
		}

	}
</style>