import axios from "axios";
import { ElMessage } from "element-plus";
import router from "@/router";

const instance = axios.create({
  baseURL: "/api",
  timeout: 30000,
});

// 请求拦截器
instance.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem("token");
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error),
);

// 响应拦截器
instance.interceptors.response.use(
  (response) => {
    const res = response.data;
    if (res.code !== 200) {
      ElMessage.error(res.message || "请求失败");
      return Promise.reject(new Error(res.message));
    }
    return res;
  },
  (error) => {
    if (error.response) {
      const { status, data } = error.response;
      if (status === 401) {
        localStorage.removeItem("token");
        router.push("/login");
        ElMessage.error("登录已过期，请重新登录");
      } else {
        ElMessage.error(data?.message || "请求失败");
      }
    } else {
      ElMessage.error("网络错误");
    }
    return Promise.reject(error);
  },
);

export default {
  auth: {
    login: (data) => instance.post("/auth/login", data),
    logout: () => instance.post("/auth/logout"),
    getMe: () => instance.get("/auth/me"),
  },
  users: {
    list: (params) => instance.get("/users", { params }),
    create: (data) => instance.post("/users", data),
    update: (id, data) => instance.put(`/users/${id}`, data),
    delete: (id) => instance.delete(`/users/${id}`),
    uploadFace: (id, file) => {
      const formData = new FormData();
      formData.append("file", file);
      return instance.post(`/users/${id}/face`, formData);
    },
  },
  departments: {
    list: (params) => instance.get("/departments", { params }),
    all: () => instance.get("/departments/all"),
    create: (data) => instance.post("/departments", data),
    update: (id, data) => instance.put(`/departments/${id}`, data),
    delete: (id) => instance.delete(`/departments/${id}`),
  },
  attendance: {
    checkIn: (file) => {
      const formData = new FormData();
      formData.append("file", file);
      return instance.post("/attendance/check-in", formData);
    },
    checkOut: (file) => {
      const formData = new FormData();
      formData.append("file", file);
      return instance.post("/attendance/check-out", formData);
    },
    publicCheckIn: (file) => {
      const formData = new FormData();
      formData.append("file", file);
      return instance.post("/attendance/public/check-in", formData);
    },
    publicCheckOut: (file) => {
      const formData = new FormData();
      formData.append("file", file);
      return instance.post("/attendance/public/check-out", formData);
    },
    list: (params) => instance.get("/attendance", { params }),
    statistics: (params) => instance.get("/attendance/statistics", { params }),
  },
  leave: {
    create: (data) => instance.post("/leave", data),
    my: (params) => instance.get("/leave/my", { params }),
    pending: (params) => instance.get("/leave/pending", { params }),
    all: (params) => instance.get("/leave/all", { params }),
    approve: (id, data) => instance.put(`/leave/${id}/approve`, data),
    dates: (params) => instance.get("/leave/dates", { params }),
  },
};
