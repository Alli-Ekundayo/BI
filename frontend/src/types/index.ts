export type DatasourceType = "postgres" | "mysql" | "mongodb";
export type VizType = "table" | "bar" | "line" | "pie";

export interface DatasourceConfig {
  type: DatasourceType;
  datasource_id: string;
}

export interface QueryRequest {
  message: string;
  datasource: DatasourceConfig;
  session_id: string;
}

export interface QueryResponse {
  answer: string;
  query_generated: string;
  results: Record<string, unknown>[];
  viz_type: VizType;
  session_id: string;
  error?: string | null;
}

export interface SchemaField {
  column: string;
  type: string;
  nullable?: boolean;
}

export type SchemaResponse = {
  tables: Record<string, SchemaField[]>;
};

export interface SessionMessage {
  role: "user" | "assistant";
  content: string;
  timestamp?: string;
}

export interface SessionData {
  session_id: string;
  datasource_id: string;
  messages: SessionMessage[];
  created_at?: string;
  updated_at?: string;
  expires_at?: string;
}
