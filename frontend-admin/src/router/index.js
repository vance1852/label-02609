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
        path: "my-leave",
        name: "MyLeave",
        component: () => import("@/views/MyLeave.vue"),
      },
      {
        path: "leave-approval",
        name: "LeaveApproval",
        component: () => import("@/views/LeaveApproval.vue"),
      },
    ],
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

router.beforeEach((to, from, next) => {
  const userStore = useUserStore();

  if (to.meta.requiresAuth !== false && !userStore.token) {
    next("/login");
  } else {
    next();
  }
});

export default router;
