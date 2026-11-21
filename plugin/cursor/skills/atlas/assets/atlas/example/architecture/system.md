# System

The writer posts from a browser; the `api` service validates nothing and saves the post.

```mermaid
flowchart LR
  writer["writer<br/><small>publishes a post</small>"]:::person
  api["api<br/><small>takes the post, stores it</small>"]:::service
  db["database<br/><small>keeps the posts</small>"]:::store
  note1["The store is an in-memory array here; a real service would name its database."]:::note
  writer -->|"1. sends the post"| api
  api -->|"2. saves it"| db
  note1 -.- db
  %% at writer 0 0
  %% at api 330 0
  %% at db 660 0
  %% at note1 660 150
```

## writer

The person using the service.

- Kind: person

## api

The only service. Its routes take a request and its store keeps what they are given.

- Kind: service
- Paths: `services/api`
- Keys: `API_TOKEN` (signs a post's id); `DATABASE_URL` (the store, once it is a database)
- Opens: [api](api.md)

## db

Where the posts live.

- Kind: store
