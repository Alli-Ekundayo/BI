import { apiClient } from "./client";
import type { DatasourceConfig, SchemaResponse, SessionData } from "../types";

export async function fetchSchema(
  datasource: DatasourceConfig
): Promise<SchemaResponse> {
  const { data } = await apiClient.get<SchemaResponse>("/schema", {
    params: {
      datasource_type: datasource.type,
      datasource_id: datasource.datasource_id,
    },
  });
  return data;
}

export async function createSession(
  datasource: DatasourceConfig
): Promise<SessionData> {
  const { data } = await apiClient.post<SessionData>("/session", datasource);
  return data;
}

export async function fetchSession(sessionId: string): Promise<SessionData> {
  const { data } = await apiClient.get<SessionData>(`/session/${sessionId}`);
  return data;
}
