import { defineStore } from "pinia";
import { ref, computed } from "vue";
import api from "@/api";

export const useUserStore = defineStore("user", () => {
  const token = ref(localStorage.getItem("token") || "");
  const userInfo = ref(null);

  const isLoggedIn = computed(() => !!token.value);
  const isAdmin = computed(() => userInfo.value?.role === "admin");

  async function login(username, password) {
    const res = await api.auth.login({ username, password });
    token.value = res.data.access_token;
    userInfo.value = res.data.user;
    localStorage.setItem("token", token.value);
    return res;
  }

  async function logout() {
    try {
      await api.auth.logout();
    } catch (e) {
      // ignore
    }
    token.value = "";
    userInfo.value = null;
    localStorage.removeItem("token");
  }

  async function fetchUserInfo() {
    if (!token.value) return;
    try {
      const res = await api.auth.getMe();
      userInfo.value = res.data;
    } catch (e) {
      logout();
    }
  }

  return {
    token,
    userInfo,
    isLoggedIn,
    isAdmin,
    login,
    logout,
    fetchUserInfo,
  };
});
