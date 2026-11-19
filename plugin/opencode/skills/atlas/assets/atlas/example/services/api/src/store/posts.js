const posts = [];

export function savePost(body) {
  posts.push(body);
  return posts.length;
}
