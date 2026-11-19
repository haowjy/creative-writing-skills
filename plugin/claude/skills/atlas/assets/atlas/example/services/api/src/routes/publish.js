import { savePost } from "../store/posts.js";

/** POST /posts: stores the post and answers with its id. */
export function publish(request) {
  return { id: savePost(request.body) };
}
