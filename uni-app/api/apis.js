import {
	request
} from "@/utils/request.js"
export function apiGetBanner(data ={}) {
	return request({
		url: "/homeBanner",
		method: 'GET',
		data
	});
};

export function apiAnli(data ={}) {
	return request({
		url: "http://127.0.0.1:8000/api/tuodan/anli/",
		method: 'GET',
		data
	});
};

export function apiUsers(data ={}) {
	return request({
		url: "http://127.0.0.1:8000/api/users/list/",
		method: 'GET',
		data
	});
};

export function apiUserPhotos(data ={}) {
	return request({
		url: "http://127.0.0.1:8000/api/users/photos/",
		method: 'GET',
		data
	});
};

export function apiActivity(data ={}) {
	return request({
		url: "http://127.0.0.1:8000/api/tuodan/activity/list/",
		method: 'GET',
		data
	});
};
