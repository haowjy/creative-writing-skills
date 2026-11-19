# api

The api service is two modules: a route that takes the post and a store that keeps it.

```mermaid
flowchart LR
  routes["routes<br/><small>take the request</small>"]:::module
  store["store<br/><small>keeps the posts</small>"]:::module
  routes -->|"1. hands the post to"| store
```

## routes

One route today, `publish`.

- Kind: module
- Paths: `services/api/src/routes`
- Shot: publish/post-form

## store

An in-memory list standing in for a database.

- Kind: module
- Paths: `services/api/src/store`
