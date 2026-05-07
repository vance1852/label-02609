import { createRouter, createWebHistory } from "vue-router";
import { useUserStore } from "@/stores/user";

const routes = [
  {
    path: "/login",
    name: "Login",
    component: () => import("@/views/Login.vue"),
    meta: { requiresAuth: false },
  },
  {
    path: "/attendance",
    name: "AttendanceCheck",
    component: () => import("@/views/AttendanceCheck.vue"),
    meta: { requiresAuth: false },
  },
  {
    path: "/",
    component: () => import("@/layouts/MainLayout.vue"),
    meta: { requiresAuth: true },
    children: [
      {
        path: "",
        redirect: "/dashboard",
      },
      {
        path: "dashboard",
        name: "Dashboard",
        component: () => import("@/views/Dashboard.vue"),
      },
      {
        path: "users",
        name: "Users",
        component: () => import("@/views/Users.vue"),
      },
      {
        path: "departments",
        name: "Departments",
        component: () => import("@/views/Departments.vue"),
      },
      {
        path: "records",
        name: "Records",
        component: () => import("@/views/Records.vue"),
      },
      {
        path: "my-leaves",
        name: "MyLeaves",
        component: () => import("@/views/MyLeaves.vue"),
      },
      {
        path: "leave-approval",
        name: "LeaveApproval",
        component: () => import("@/views/LeaveApproval.vue"),
        meta: { requiresAdmin: true },
      },
    ],
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

router.beforeEach(async (to, from, next) => {
  const userStore = useUserStore();

  if (to.meta.requiresAuth !== false && !userStore.token) {
    next("/login");
    return;
  }

  if (to.meta.requiresAdmin) {
    if (!userStore.userInfo) {
      await userStore.fetchUserInfo();
    }
    if (!userStore.isAdmin) {
      next("/dashboard");
      return;
    }
  }

  next();
});

export default router;
