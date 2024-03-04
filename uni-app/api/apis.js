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
		url: "http://127.0.0.1:8000/api/anli/",
		method: 'GET',
		data
	});
};
