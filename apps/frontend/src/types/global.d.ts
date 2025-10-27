// Global type declarations for missing modules

declare module 'react' {
  import * as React from 'react';
  export = React;
  export as namespace React;
}

declare module 'react-dom' {
  import * as ReactDOM from 'react-dom';
  export = ReactDOM;
  export as namespace ReactDOM;
}

declare module 'react-router-dom' {
  export interface RouteProps {
    path?: string;
    element?: React.ReactNode;
    children?: React.ReactNode;
  }
  
  export interface NavigateProps {
    to: string;
    replace?: boolean;
    state?: any;
  }
  
  export interface LinkProps {
    to: string;
    className?: string;
    children?: React.ReactNode;
    state?: any;
  }
  
  export interface LocationState {
    from?: { pathname: string };
    message?: string;
  }
  
  export const BrowserRouter: React.ComponentType<{ children: React.ReactNode }>;
  export const Router: React.ComponentType<{ children: React.ReactNode }>;
  export const Routes: React.ComponentType<{ children: React.ReactNode }>;
  export const Route: React.ComponentType<RouteProps>;
  export const Navigate: React.ComponentType<NavigateProps>;
  export const Link: React.ComponentType<LinkProps>;
  export const useNavigate: () => (to: string, options?: { replace?: boolean; state?: any }) => void;
  export const useLocation: () => { pathname: string; state?: LocationState };
}

declare module 'react-hook-form' {
  export interface UseFormReturn<T = any> {
    register: (name: keyof T, options?: any) => any;
    handleSubmit: (onSubmit: (data: T) => void | Promise<void>) => (e?: React.BaseSyntheticEvent) => Promise<void>;
    formState: {
      errors: Record<keyof T, { message?: string }>;
      isSubmitting: boolean;
      isDirty: boolean;
    };
    reset: (data?: Partial<T>) => void;
  }
  
  export const useForm: <T = any>(options?: { resolver?: any; defaultValues?: Partial<T> }) => UseFormReturn<T>;
}

declare module '@hookform/resolvers/zod' {
  export const zodResolver: (schema: any) => any;
}

declare module 'zod' {
  export interface ZodType<T = any> {
    parse: (data: any) => T;
    safeParse: (data: any) => { success: boolean; data?: T; error?: any };
    refine: (fn: (data: T) => boolean, options: { message: string; path?: string[] }) => ZodType<T>;
    optional: () => ZodOptional<T>;
    nullable: () => ZodNullable<T>;
    or: (other: ZodType<any>) => ZodType<T>;
    default: (value: T) => ZodType<T>;
  }
  
  export interface ZodString extends ZodType<string> {
    min: (length: number, message?: string) => ZodString;
    max: (length: number, message?: string) => ZodString;
    email: (message?: string) => ZodString;
    regex: (pattern: RegExp, message?: string) => ZodString;
    url: (message?: string) => ZodString;
    optional: () => ZodOptional<ZodString>;
    or: (other: ZodType<any>) => ZodType<string>;
  }
  
  export interface ZodNumber extends ZodType<number> {
    int: () => ZodNumber;
    min: (value: number, message?: string) => ZodNumber;
    max: (value: number, message?: string) => ZodNumber;
    optional: () => ZodOptional<ZodNumber>;
    nullable: () => ZodNullable<ZodNumber>;
  }
  
  export interface ZodArray<T> extends ZodType<T[]> {
    optional: () => ZodOptional<ZodArray<T>>;
  }
  
  export interface ZodRecord<T> extends ZodType<Record<string, T>> {
    optional: () => ZodOptional<ZodRecord<T>>;
  }
  
  export interface ZodOptional<T> extends ZodType<T | undefined> {
    or: (other: ZodType<any>) => ZodType<T>;
  }
  
  export interface ZodNullable<T> extends ZodType<T | null> {
    optional: () => ZodOptional<ZodNullable<T>>;
  }
  
  export interface ZodObject<T> extends ZodType<T> {
    refine: (fn: (data: T) => boolean, options: { message: string; path?: string[] }) => ZodObject<T>;
  }
  
  export interface ZodEnum<T extends readonly [string, ...string[]]> extends ZodType<T[number]> {
    default: (value: T[number]) => ZodEnum<T>;
  }
  
  export const z: {
    string: () => ZodString;
    number: () => ZodNumber;
    array: <T>(schema: ZodType<T>) => ZodArray<T>;
    record: <T>(keySchema: ZodType<string>, valueSchema: ZodType<T>) => ZodRecord<T>;
    object: <T>(shape: { [K in keyof T]: ZodType<T[K]> }) => ZodObject<T>;
    enum: <T extends readonly [string, ...string[]]>(values: T) => ZodEnum<T>;
    literal: <T extends string>(value: T) => ZodType<T>;
  };
  
  export namespace z {
    export type infer<T extends ZodType<any>> = T extends ZodType<infer U> ? U : never;
  }
}

declare module '@tanstack/react-query' {
  export interface UseQueryOptions<T = any> {
    queryKey: any[];
    queryFn: () => Promise<T>;
    enabled?: boolean;
    retry?: number | boolean;
    staleTime?: number;
  }
  
  export interface UseQueryResult<T = any> {
    data: T | undefined;
    isLoading: boolean;
    error: any;
  }
  
  export interface QueryClient {
    setQueryData: (key: any[], data: any) => void;
    clear: () => void;
  }
  
  export const useQuery: <T = any>(options: UseQueryOptions<T>) => UseQueryResult<T>;
  export const useQueryClient: () => QueryClient;
  export const QueryClient: new (options?: any) => QueryClient;
  export const QueryClientProvider: React.ComponentType<{ client: QueryClient; children: React.ReactNode }>;
}

declare module 'axios' {
  export interface AxiosRequestConfig {
    baseURL?: string;
    timeout?: number;
    headers?: Record<string, string>;
    _retry?: boolean;
  }
  
  export interface AxiosResponse<T = any> {
    data: T;
    status: number;
    statusText: string;
    headers: any;
    config: AxiosRequestConfig;
  }
  
  export interface AxiosError {
    response?: AxiosResponse;
    config?: AxiosRequestConfig;
    message: string;
  }
  
  export interface AxiosInstance {
    get: <T = any>(url: string, config?: AxiosRequestConfig) => Promise<AxiosResponse<T>>;
    post: <T = any>(url: string, data?: any, config?: AxiosRequestConfig) => Promise<AxiosResponse<T>>;
    put: <T = any>(url: string, data?: any, config?: AxiosRequestConfig) => Promise<AxiosResponse<T>>;
    delete: <T = any>(url: string, config?: AxiosRequestConfig) => Promise<AxiosResponse<T>>;
    request: <T = any>(config: AxiosRequestConfig) => Promise<AxiosResponse<T>>;
    interceptors: {
      request: {
        use: (onFulfilled: (config: AxiosRequestConfig) => AxiosRequestConfig, onRejected?: (error: any) => Promise<any>) => void;
      };
      response: {
        use: (onFulfilled: (response: AxiosResponse) => AxiosResponse, onRejected?: (error: AxiosError) => Promise<any>) => void;
      };
    };
  }
  
  export const axios: {
    create: (config?: AxiosRequestConfig) => AxiosInstance;
    post: <T = any>(url: string, data?: any, config?: AxiosRequestConfig) => Promise<AxiosResponse<T>>;
  };
  
  export default axios;
}

declare module 'js-cookie' {
  export interface CookieAttributes {
    expires?: number | Date;
    path?: string;
    domain?: string;
    secure?: boolean;
    sameSite?: 'strict' | 'lax' | 'none';
  }
  
  export const Cookies: {
    get: (name: string) => string | undefined;
    set: (name: string, value: string, attributes?: CookieAttributes) => void;
    remove: (name: string, attributes?: CookieAttributes) => void;
  };
  
  export default Cookies;
}

declare module 'react-hot-toast' {
  export interface ToastOptions {
    duration?: number;
    style?: React.CSSProperties;
    success?: {
      duration?: number;
      iconTheme?: {
        primary: string;
        secondary: string;
      };
    };
    error?: {
      duration?: number;
      iconTheme?: {
        primary: string;
        secondary: string;
      };
    };
  }
  
  export interface ToasterProps {
    position?: 'top-left' | 'top-center' | 'top-right' | 'bottom-left' | 'bottom-center' | 'bottom-right';
    toastOptions?: ToastOptions;
  }
  
  export const toast: {
    success: (message: string) => void;
    error: (message: string) => void;
  };
  
  export const Toaster: React.ComponentType<ToasterProps>;
  
  export default toast;
}

declare module '@heroicons/react/24/outline' {
  export const EyeIcon: React.ComponentType<{ className?: string }>;
  export const EyeSlashIcon: React.ComponentType<{ className?: string }>;
}

declare module '@headlessui/react' {
  // Add any Headless UI components you're using
}

declare module '@heroicons/react' {
  // Add any Heroicons you're using
}

declare module 'clsx' {
  export default function clsx(...args: any[]): string;
}

declare module 'tailwind-merge' {
  export function twMerge(...args: string[]): string;
}

declare module 'socket.io-client' {
  // Add Socket.IO client types if needed
}

// Global JSX namespace
declare global {
  namespace JSX {
    interface IntrinsicElements {
      [elemName: string]: any;
    }
  }
}