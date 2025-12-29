import { create } from 'zustand'
import { Account } from '@/types/account'
import { Pool } from '@/types/pool'

interface AccountState {
  selectedAccount: Account | null
  selectedRegion: string | null
  selectedPool: Pool | null
  setAccount: (account: Account) => void
  setRegion: (region: string) => void
  setPool: (pool: Pool) => void
  clearSelection: () => void
}

export const useAccountStore = create<AccountState>((set) => ({
  selectedAccount: null,
  selectedRegion: null,
  selectedPool: null,
  setAccount: (account) => set({ selectedAccount: account, selectedRegion: null, selectedPool: null }),
  setRegion: (region) => set({ selectedRegion: region, selectedPool: null }),
  setPool: (pool) => set({ selectedPool: pool }),
  clearSelection: () => set({ selectedAccount: null, selectedRegion: null, selectedPool: null }),
}))

