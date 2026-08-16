import React from "react";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { getToken } from "./api/http";
import Login from "./pages/Login";
import AppLayout from "./components/layout/AppLayout";
import Dashboard from "./pages/Dashboard";
import Merchants from "./pages/Merchants";
import MerchantDetail from "./pages/MerchantDetail";
import SeedCards from "./pages/SeedCards";
import SeedCardCreate from "./pages/SeedCardCreate";
import SeedCardDetail from "./pages/SeedCardDetail";
import AIReport from "./pages/AIReport";
import AIComment from "./pages/AIComment";
import AIContent from "./pages/AIContent";

/** 登录态守卫：无 token 跳登录页。 */
function RequireAuth({ children }: { children: React.ReactNode }) {
  const token = getToken();
  if (!token) {
    return <Navigate to="/login" replace />;
  }
  return <>{children}</>;
}

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route
          element={
            <RequireAuth>
              <AppLayout />
            </RequireAuth>
          }
        >
          <Route index element={<Navigate to="/dashboard" replace />} />
          <Route path="dashboard" element={<Dashboard />} />
          <Route path="merchants" element={<Merchants />} />
          <Route path="merchants/:id" element={<MerchantDetail />} />
          <Route path="seed-cards" element={<SeedCards />} />
          <Route path="seed-cards/create" element={<SeedCardCreate />} />
          <Route path="seed-cards/:id" element={<SeedCardDetail />} />
          <Route path="ai/report" element={<AIReport />} />
          <Route path="ai/comment" element={<AIComment />} />
          <Route path="ai/content" element={<AIContent />} />
        </Route>
        <Route path="*" element={<Navigate to="/dashboard" replace />} />
      </Routes>
    </BrowserRouter>
  );
}
