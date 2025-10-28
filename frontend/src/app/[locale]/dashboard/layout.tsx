import type { ReactNode } from "react";
import LayoutShell from "@/components/layout/Layout";

export default function DashboardLayout({ children }: { children: ReactNode }) {
  return <LayoutShell>{children}</LayoutShell>;
}
