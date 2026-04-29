import { ReactNode } from "react";
import { Header } from "./Header";
import { Sidebar } from "./Sidebar";

interface AppShellProps {
  children: ReactNode;
}

export function AppShell({ children }: AppShellProps) {
  return (
    <div className="app-frame">
      <Sidebar />
      <main className="main-content">
        <Header />
        {children}
      </main>
    </div>
  );
}
