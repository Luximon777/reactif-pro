import axios from "axios";

const API = `${process.env.REACT_APP_BACKEND_URL}/api/social`;

export const social = axios.create({ baseURL: API });
social.interceptors.request.use((config) => {
  const jwt = localStorage.getItem("ubuntoo_jwt");
  if (jwt) config.headers.Authorization = `Bearer ${jwt}`;
  return config;
});

export const postsApi = {
  getAll: (postType) => social.get(`/posts`, { params: postType ? { post_type: postType } : {} }),
  create: (data) => social.post(`/posts`, data),
  like: (postId) => social.post(`/posts/${postId}/like`),
  react: (postId, reactionType) => social.post(`/posts/${postId}/react`, { reaction_type: reactionType }),
  getComments: (postId) => social.get(`/posts/${postId}/comments`),
  addComment: (postId, content) => social.post(`/comments`, { post_id: postId, content }),
};

export const usersApi = {
  getAll: () => social.get(`/users`),
  getById: (userId) => social.get(`/users/${userId}`),
  updateProfile: (data) => social.put(`/users/profile`, data),
};

export const messagesApi = {
  getConversations: () => social.get(`/messages/conversations`),
  getMessages: (userId) => social.get(`/messages/${userId}`),
  send: (receiverId, content) => social.post(`/messages`, { receiver_id: receiverId, content }),
  getPresence: () => social.get(`/presence`),
};

export const groupsApi = {
  getAll: (category) => social.get(`/groups`, { params: category ? { category } : {} }),
  getById: (groupId) => social.get(`/groups/${groupId}`),
  create: (data) => social.post(`/groups`, data),
  join: (groupId) => social.post(`/groups/${groupId}/join`),
  getDiscussions: (groupId) => social.get(`/groups/${groupId}/discussions`),
};

export const discussionsApi = {
  getById: (discussionId) => social.get(`/discussions/${discussionId}`),
  create: (data) => social.post(`/discussions`, data),
  getReplies: (discussionId) => social.get(`/discussions/${discussionId}/replies`),
  addReply: (discussionId, content) => social.post(`/discussions/${discussionId}/replies`, { content }),
};

export const badgesApi = { getAll: () => social.get(`/badges`) };
export const statsApi = { get: () => social.get(`/stats`) };
export const reportApi = {
  create: (targetType, targetId, reason) => social.post(`/reports`, { target_type: targetType, target_id: targetId, reason }),
};
export const searchApi = { search: (q) => social.get(`/search`, { params: { q } }) };
