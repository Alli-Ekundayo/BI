import { useQueryStore } from "../store/queryStore";
import { useDatasourceStore } from "../store/datasourceStore";
import { useSessionStore } from "../store/sessionStore";
import { submitQuery } from "../api/query";
import type { QueryRequest } from "../types";

export function useQuery() {
  const { activeDatasource } = useDatasourceStore();
  const { sessionId, pushMessage } = useSessionStore();
  const { setLoading, setError, addResult } = useQueryStore();

  async function runQuery(message: string): Promise<void> {
    if (!activeDatasource) {
      setError("Connect a datasource first.");
      return;
    }

    const payload: QueryRequest = {
      message,
      datasource: activeDatasource,
      session_id: sessionId,
    };

    setLoading(true);
    pushMessage({ role: "user", content: message, timestamp: new Date().toISOString() });

    try {
      const result = await submitQuery(payload);
      addResult(result);
      pushMessage({
        role: "assistant",
        content: result.answer,
        timestamp: new Date().toISOString(),
      });
    } catch (error: unknown) {
      const messageText =
        error instanceof Error ? error.message : "Query failed unexpectedly.";
      setError(messageText);
    }
  }

  return { runQuery };
}
