<template>
	<view>
		<view>我们脱单了</view>
		<view v-for="item in anli">
			<view>{{item._id}}</view>
			<view>{{item.content}}</view>
		</view>
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

	const getAnli = async () => {
		let res = await apiAnli({
		});
		console.log(res);
		anli.value = res.data;
	};
	getAnli()
</script>

<style lang="scss" scoped>

</style>