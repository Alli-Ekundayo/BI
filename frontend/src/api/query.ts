import { apiClient } from "./client";
import type { QueryRequest, QueryResponse } from "../types";

export async function submitQuery(payload: QueryRequest): Promise<QueryResponse> {
  const { data } = await apiClient.post<QueryResponse>("/query", payload);
  return data;
}
