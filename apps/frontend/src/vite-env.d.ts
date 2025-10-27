/// <reference types="vite/client" />
/// <reference path="./types/suppress.d.ts" />

interface ImportMetaEnv {
  readonly VITE_API_URL: string
  readonly PROD: boolean
  readonly DEV: boolean
  readonly MODE: string
  readonly BASE_URL: string
  readonly SSR: boolean
  // more env variables...
}

interface ImportMeta {
  readonly env: ImportMetaEnv
  readonly hot?: {
    accept(): void
    accept(cb: (mod: any) => void): void
    accept(dep: string, cb: (mod: any) => void): void
    accept(deps: string[], cb: (mods: any[]) => void): void
    dispose(cb: () => void): void
    decline(): void
    invalidate(): void
    on(event: string, cb: (...args: any[]) => void): void
  }
  readonly glob: (pattern: string) => Record<string, () => Promise<any>>
}