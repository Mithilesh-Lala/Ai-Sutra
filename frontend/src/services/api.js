import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Users
export const createUser = async (userData) => {
  const response = await api.post('/users/', userData);
  return response.data;
};

export const getUser = async (userId) => {
  const response = await api.get(`/users/${userId}`);
  return response.data;
};

// Onboarding
export const processOnboarding = async (userId, interests) => {
  const response = await api.post('/onboarding/', {
    user_id: userId,
    interests: interests,
  });
  return response.data;
};

export const getUserTopics = async (userId) => {
  const response = await api.get(`/onboarding/${userId}/topics`);
  return response.data;
};

// Feed
export const getUserFeed = async (userId, date = null) => {
  const url = date ? `/feed/${userId}?date=${date}` : `/feed/${userId}`;
  const response = await api.get(url);
  return response.data;
};

// Refresh all topics feed
export const refreshFeed = async (userId) => {
  const response = await api.post(`/feed/refresh/${userId}`);
  return response.data;
};

// NEW: Refresh feed for a SPECIFIC topic only
export const refreshTopicFeed = async (userId, topicId) => {
  const response = await api.post(`/feed/refresh/${userId}/topic/${topicId}`);
  return response.data;
};

// Topics
export const deleteTopic = async (topicId) => {
  const response = await api.delete(`/topics/${topicId}`);
  return response.data;
};

// Update Topics

export const updateTopic = async (topicId, data) => {
  const response = await api.put(`/topics/${topicId}`, data);
  return response.data;
};

// Saved Content
export const saveContent = async (userId, contentId) => {
  const response = await api.post('/saved/', {
    user_id: userId,
    content_id: contentId,
  });
  return response.data;
};

export const getSavedContent = async (userId) => {
  const response = await api.get(`/saved/${userId}`);
  return response.data;
};

export const unsaveContent = async (savedId) => {
  const response = await api.delete(`/saved/${savedId}`);
  return response.data;
};

// Settings
export const getUserSettings = async (userId) => {
  const response = await api.get(`/settings/${userId}`);
  return response.data;
};

export const updateUserSettings = async (userId, settings) => {
  const response = await api.put(`/settings/${userId}`, settings);
  return response.data;
};

export default api;