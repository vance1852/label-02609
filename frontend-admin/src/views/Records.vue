<template>
  <div class="records-page">
    <div class="page-header">
      <h2 class="page-title">考勤记录</h2>
    </div>
    
    <div class="card">
      <div class="search-bar">
        <el-date-picker
          v-model="dateRange"
          type="daterange"
          range-separator="至"
          start-placeholder="开始日期"
          end-placeholder="结束日期"
          value-format="YYYY-MM-DD"
          class="date-picker-400"
        />
        <el-select v-model="selectedUser" placeholder="选择员工" clearable style="width: 120px">
          <el-option v-for="u in userOptions" :key="u.id" :label="u.real_name" :value="u.id" />
        </el-select>
        <el-button type="primary" @click="fetchRecords">查询</el-button>
        <el-button @click="resetSearch">重置</el-button>
      </div>
      
      <el-table :data="records" stripe v-loading="loading" border style="width: 100%">
        <el-table-column prop="employee_no" label="工号" min-width="80" align="center" />
        <el-table-column prop="user_name" label="姓名" min-width="80" align="center" />
        <el-table-column prop="department_name" label="部门" min-width="100" align="center">
          <template #default="{ row }">{{ row.department_name || '-' }}</template>
        </el-table-column>
        <el-table-column prop="attendance_date" label="日期" min-width="100" align="center" />
        <el-table-column prop="record_type_text" label="类型" min-width="70" align="center">
          <template #default="{ row }">
            <el-tag :type="row.record_type === 'check_in' ? 'success' : 'warning'" size="small">
              {{ row.record_type_text }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="record_time" label="打卡时间" min-width="100" align="center" />
        <el-table-column label="打卡照片" min-width="80" align="center">
          <template #default="{ row }">
            <el-image
              v-if="row.record_image"
              :src="getImageUrl(row.record_image)"
              :preview-src-list="[getImageUrl(row.record_image)]"
              fit="cover"
              style="width: 40px; height: 40px; border-radius: 4px; cursor: pointer;"
            />
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column prop="status_text" label="状态" min-width="80" align="center">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)" size="small">{{ row.status_text }}</el-tag>
          </template>
        </el-table-column>
      </el-table>
      
      <el-pagination
        v-model:current-page="pagination.page"
        v-model:page-size="pagination.pageSize"
        :total="pagination.total"
        :page-sizes="[10, 20, 50]"
        layout="total, sizes, prev, pager, next"
        @change="fetchRecords"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import api from '@/api'

const loading = ref(false)
const records = ref([])
const userOptions = ref([])
const dateRange = ref([])
const selectedUser = ref(null)
const pagination = reactive({ page: 1, pageSize: 10, total: 0 })

const getStatusType = (status) => {
  const map = { normal: 'success', late: 'warning', early: 'danger' }
  return map[status] || 'info'
}

const getImageUrl = (path) => {
  if (!path) return ''
  const filename = path.split('/').pop().split('\\').pop()
  return `http://localhost:8000/uploads/attendance/${filename}`
}

const fetchRecords = async () => {
  loading.value = true
  try {
    const params = {
      page: pagination.page,
      page_size: pagination.pageSize
    }
    if (dateRange.value?.length === 2) {
      params.start_date = dateRange.value[0]
      params.end_date = dateRange.value[1]
    }
    if (selectedUser.value) {
      params.user_id = selectedUser.value
    }
    
    const res = await api.attendance.list(params)
    records.value = res.data.list
    pagination.total = res.data.total
  } finally {
    loading.value = false
  }
}

const fetchUsers = async () => {
  try {
    const res = await api.users.list({ page: 1, page_size: 1000 })
    userOptions.value = res.data.list
  } catch (e) {}
}

const resetSearch = () => {
  dateRange.value = []
  selectedUser.value = null
  pagination.page = 1
  fetchRecords()
}

onMounted(() => {
  fetchRecords()
  fetchUsers()
})
</script>

<style lang="scss" scoped>
.search-bar {
  :deep(.el-date-editor) {
    width: 400px !important;
    max-width: 400px !important;
  }
}
</style>
