import { Navigate, Route, Routes } from 'react-router-dom'
import ProtectedRoute from './auth/ProtectedRoute'
import AdminLayout from './layout/AdminLayout'
import Login from './pages/Login'
import MerchantManage from './pages/MerchantManage'
import StaffManage from './pages/StaffManage'
import StoreManage from './pages/StoreManage'
import PackageManage from './pages/PackageManage'
import OrderDashboard from './pages/OrderDashboard'
import ReservationManage from './pages/ReservationManage'
import ChannelBinding from './pages/ChannelBinding'
import DataDashboard from './pages/DataDashboard'

// 路由表：/login 公开；其余页面包在布局 + 权限守卫内。
export default function AppRouter() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route
        element={
          <ProtectedRoute>
            <AdminLayout />
          </ProtectedRoute>
        }
      >
        <Route index element={<Navigate to="/orders" replace />} />
        <Route path="/merchants" element={<MerchantManage />} />
        <Route path="/staff" element={<StaffManage />} />
        <Route path="/stores" element={<StoreManage />} />
        <Route path="/packages" element={<PackageManage />} />
        <Route path="/orders" element={<OrderDashboard />} />
        <Route path="/reservations" element={<ReservationManage />} />
        <Route path="/channels" element={<ChannelBinding />} />
        <Route path="/dashboard" element={<DataDashboard />} />
      </Route>
      <Route path="*" element={<Navigate to="/orders" replace />} />
    </Routes>
  )
}
