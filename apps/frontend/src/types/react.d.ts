import * as React from 'react';

declare global {
  namespace React {
    interface FC<P = {}> {
      (props: P & { children?: ReactNode }): ReactElement | null;
    }
    
    interface ReactElement<P = any, T extends string | JSXElementConstructor<any> = string | JSXElementConstructor<any>> {
      type: T;
      props: P;
      key: Key | null;
    }
    
    type ReactNode = ReactChild | ReactFragment | ReactPortal | boolean | null | undefined;
    type ReactChild = ReactElement | ReactText;
    type ReactText = string | number;
    type ReactFragment = {} | ReactNodeArray;
    type ReactNodeArray = Array<ReactNode>;
    type ReactPortal = any;
    type Key = string | number;
    type JSXElementConstructor<P> = ((props: P) => ReactElement | null) | (new (props: P) => Component<P, any>);
    
    interface Component<P = {}, S = {}> {
      props: Readonly<P> & Readonly<{ children?: ReactNode }>;
      state: Readonly<S>;
    }
    
    interface BaseSyntheticEvent<E = object, C = any, T = any> {
      nativeEvent: E;
      currentTarget: C;
      target: T;
      bubbles: boolean;
      cancelable: boolean;
      defaultPrevented: boolean;
      eventPhase: number;
      isTrusted: boolean;
      preventDefault(): void;
      isDefaultPrevented(): boolean;
      stopPropagation(): void;
      isPropagationStopped(): boolean;
      persist(): void;
      timeStamp: number;
      type: string;
    }
    
    interface CSSProperties {
      [key: string]: any;
    }
  }
}