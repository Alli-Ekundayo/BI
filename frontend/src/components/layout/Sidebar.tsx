import { useState } from "react";
import { DatasourceCard } from "../datasource/DatasourceCard";
import { SchemaPanel } from "../schema/SchemaPanel";
import { QueryHistory } from "../query/QueryHistory";

type SidebarTab = "inventory" | "schema" | "logs";

export function Sidebar() {
  const [activeTab, setActiveTab] = useState<SidebarTab>("inventory");

  return (
    <aside className="sidebar">
      <div className="sidebar-nav">
        <p className="kicker">Navigation</p>
        <div className="sidebar-tabs">
          <button 
            className={`sidebar-tab-btn ${activeTab === 'inventory' ? 'active' : ''}`}
            onClick={() => setActiveTab("inventory")}
          >
            Inventory
          </button>
          <button 
            className={`sidebar-tab-btn ${activeTab === 'schema' ? 'active' : ''}`}
            onClick={() => setActiveTab("schema")}
          >
            Schema
          </button>
          <button 
            className={`sidebar-tab-btn ${activeTab === 'logs' ? 'active' : ''}`}
            onClick={() => setActiveTab("logs")}
          >
            Recent Logs
          </button>
        </div>
      </div>

      <div className="sidebar-content animate-in" key={activeTab}>
        {activeTab === "inventory" && (
          <div className="sidebar-section">
            <p className="kicker">Active Datasources</p>
            <DatasourceCard />
          </div>
        )}
        
        {activeTab === "schema" && (
          <div className="sidebar-section">
            <p className="kicker">Knowledge Graph</p>
            <SchemaPanel />
          </div>
        )}

        {activeTab === "logs" && (
          <div className="sidebar-section">
            <p className="kicker">Past Sessions</p>
            <QueryHistory />
          </div>
        )}
      </div>

      <div className="sidebar-footer">
        <p className="subtle-text">BI Bot v1.0.4</p>
      </div>
    </aside>
  );
}
