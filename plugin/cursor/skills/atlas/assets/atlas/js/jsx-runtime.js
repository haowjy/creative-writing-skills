/*
 * @xyflow/react's UMD build expects a `jsxRuntime` global, which React's UMD build doesn't
 * provide. This maps jsx and jsxs onto the one React already loaded, so the page keeps a
 * single copy of React. A key passed separately rides in props, as createElement takes it.
 */
(() => {
  const { createElement, Fragment } = globalThis.React;
  const jsx = (type, props, key) =>
    createElement(type, key === undefined ? props : { ...props, key });
  globalThis.jsxRuntime = { jsx, jsxs: jsx, Fragment };
})();
