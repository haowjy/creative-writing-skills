# Dependencies

## The rules

- **The api's modules are acyclic.** `routes` may import `store`; `store` imports nothing of the api.

## Where the code breaks them

One row per break; none today. Add `import { publish } from "../routes/publish.js"` to
`services/api/src/store/posts.js` and the check fails, naming the new break.

| from | to | rule | example file |
|---|---|---|---|
