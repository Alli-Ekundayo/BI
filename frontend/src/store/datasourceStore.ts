import { create } from "zustand";
import type { DatasourceConfig } from "../types";

interface DatasourceState {
  activeDatasource: DatasourceConfig | null;
  isDatasourceModalOpen: boolean;
  setActiveDatasource: (datasource: DatasourceConfig | null) => void;
  openDatasourceModal: () => void;
  closeDatasourceModal: () => void;
}

export const useDatasourceStore = create<DatasourceState>((set) => ({
  activeDatasource: null,
  isDatasourceModalOpen: false,
  setActiveDatasource: (activeDatasource) => set({ activeDatasource }),
  openDatasourceModal: () => set({ isDatasourceModalOpen: true }),
  closeDatasourceModal: () => set({ isDatasourceModalOpen: false }),
}));
