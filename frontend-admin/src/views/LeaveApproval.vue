<template>
  <div class="leave-approval-page">
    <div class="page-header">
      <h2 class="page-title">请假审批</h2>
    </div>

    <div class="card">
      <div class="search-bar">
        <el-select v-model="filterStatus" placeholder="审批状态" clearable style="width: 130px">
          <el-option label="待审批" value="pending" />
          <el-option label="已通过" value="approved" />
          <el-option label="已驳回" value="rejected" />
        </el-select>
        <el-select v-model="filterUser" placeholder="选择员工" clearable style="width: 140px">
          <el-option v-for="u in userOptions" :key="u.id" :label="u.real_name" :value="u.id" />
        </el-select>
        <el-button type="primary" @click="fetchLeaves">查询</el-button>
        <el-button @click="resetFilter">重置</el-button>
      </div>

      <el-table :data="leaves" stripe v-loading="loading" border style="width: 100%">
        <el-table-column prop="employee_no" label="工号" min-width="80" align="center" />
        <el-table-column prop="user_name" label="姓名" min-width="80" align="center" />
        <el-table-column prop="department_name" label="部门" min-width="100" align="center">
          <template #default="{ row }">{{ row.department_name || '-' }}</template>
        </el-table-column>
        <el-table-column prop="leave_type_text" label="请假类型" min-width="80" align="center">
          <template #default="{ row }">
            <el-tag :type="leaveTypeTag(row.leave_type)" size="small">{{ row.leave_type_text }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="起止日期" min-width="180" align="center">
          <template #default="{ row }">{{ row.start_date }} 至 {{ row.end_date }}</template>
        </el-table-column>
        <el-table-column prop="reason" label="请假原因" min-width="160" show-overflow-tooltip />
        <el-table-column prop="status_text" label="审批状态" min-width="90" align="center">
          <template #default="{ row }">
            <el-tag :type="statusTag(row.status)" size="small">{{ row.status_text }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="approver_name" label="审批人" min-width="80" align="center">
          <template #default="{ row }">{{ row.approver_name || '-' }}</template>
        </el-table-column>
        <el-table-column prop="approval_comment" label="审批意见" min-width="130" show-overflow-tooltip>
          <template #default="{ row }">{{ row.approval_comment || '-' }}</template>
        </el-table-column>
        <el-table-column label="操作" min-width="140" align="center" fixed="right">
          <template #default="{ row }">
            <template v-if="row.status === 'pending'">
              <el-button type="success" size="small" @click="handleApprove(row, 'approved')">通过</el-button>
              <el-button type="danger" size="small" @click="handleApprove(row, 'rejected')">驳回</el-button>
            </template>
            <span v-else class="text-muted">已处理</span>
          </template>
        </el-table-column>
      </el-table>

      <el-pagination
        v-model:current-page="pagination.page"
        v-model:page-size="pagination.pageSize"
        :total="pagination.total"
        :page-sizes="[10, 20, 50]"
        layout="total, sizes, prev, pager, next"
        @change="fetchLeaves"
      />
    </div>

    <el-dialog v-model="showApprovalDialog" :title="approvalTitle" width="460px" :close-on-click-modal="false">
      <el-form ref="approvalFormRef" :model="approvalForm" label-width="90px">
        <el-form-item label="员工">
          <span>{{ currentLeave?.user_name }}</span>
        </el-form-item>
        <el-form-item label="请假类型">
          <span>{{ currentLeave?.leave_type_text }}</span>
        </el-form-item>
        <el-form-item label="起止日期">
          <span>{{ currentLeave?.start_date }} 至 {{ currentLeave?.end_date }}</span>
        </el-form-item>
        <el-form-item label="请假原因">
          <span>{{ currentLeave?.reason }}</span>
        </el-form-item>
        <el-form-item label="审批意见">
          <el-input v-model="approvalForm.approval_comment" type="textarea" :rows="3" placeholder="请输入审批意见（可选）" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showApprovalDialog = false">取消</el-button>
        <el-button :type="approvalForm.status === 'approved' ? 'success' : 'danger'" :loading="submitting" @click="submitApproval">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import api from '@/api'

const loading = ref(false)
const submitting = ref(false)
const leaves = ref([])
const userOptions = ref([])
const filterStatus = ref('')
const filterUser = ref(null)
const pagination = reactive({ page: 1, pageSize: 10, total: 0 })

const showApprovalDialog = ref(false)
const currentLeave = ref(null)
const approvalFormRef = ref(null)
const approvalForm = reactive({
  status: '',
  approval_comment: ''
})

const approvalTitle = computed(() => {
  return approvalForm.status === 'approved' ? '通过请假申请' : '驳回请假申请'
})

const leaveTypeTag = (type) => {
  const map = { personal: 'warning', sick: 'danger', annual: 'success' }
  return map[type] || 'info'
}

const statusTag = (status) => {
  const map = { pending: 'warning', approved: 'success', rejected: 'danger' }
  return map[status] || 'info'
}

const fetchLeaves = async () => {
  loading.value = true
  try {
    const params = {
      page: pagination.page,
      page_size: pagination.pageSize
    }
    if (filterStatus.value) {
      params.status = filterStatus.value
    }
    if (filterUser.value) {
      params.user_id = filterUser.value
    }
    const res = await api.leave.all(params)
    leaves.value = res.data.list
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

const resetFilter = () => {
  filterStatus.value = ''
  filterUser.value = null
  pagination.page = 1
  fetchLeaves()
}

const handleApprove = (row, status) => {
  currentLeave.value = row
  approvalForm.status = status
  approvalForm.approval_comment = ''
  showApprovalDialog.value = true
}

const submitApproval = async () => {
  submitting.value = true
  try {
    await api.leave.approve(currentLeave.value.id, {
      status: approvalForm.status,
      approval_comment: approvalForm.approval_comment || null
    })
    const action = approvalForm.status === 'approved' ? '通过' : '驳回'
    ElMessage.success(`请假申请已${action}`)
    showApprovalDialog.value = false
    fetchLeaves()
  } finally {
    submitting.value = false
  }
}

onMounted(() => {
  fetchLeaves()
  fetchUsers()
})
</script>

<style lang="scss" scoped>
.text-muted {
  color: #909399;
  font-size: 13px;
}
</style>
