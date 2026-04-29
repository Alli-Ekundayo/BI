import { useEffect, useState } from "react";
import { fetchSchema } from "../api/datasource";
import { useDatasourceStore } from "../store/datasourceStore";
import type { SchemaResponse } from "../types";

export function useSchema() {
  const { activeDatasource } = useDatasourceStore();
  const [schema, setSchema] = useState<SchemaResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function loadSchema() {
      if (!activeDatasource) {
        setSchema(null);
        setError(null);
        return;
      }

      setIsLoading(true);
      setError(null);
      try {
        const data = await fetchSchema(activeDatasource);
        setSchema(data);
      } catch (err: unknown) {
        const errorMessage = err instanceof Error ? err.message : "Failed to fetch schema";
        setError(errorMessage);
      } finally {
        setIsLoading(false);
      }
    }

    void loadSchema();
  }, [activeDatasource]);

  return { schema, isLoading, error };
}
