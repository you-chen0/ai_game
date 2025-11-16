import axios from 'axios';
import { StoryState, Choice } from '@/types/story';

// 创建axios实例
const api = axios.create({
  baseURL: 'http://localhost:8000',
  headers: {
    'Content-Type': 'application/json',
  },
});

export const uploadImage = async (file: File): Promise<{url: string, file_id: string}> => {
  const formData = new FormData();
  formData.append('file', file);

  const response = await api.post('/api/upload', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });

  return {
    url: response.data.url,
    file_id: response.data.file_id
  };
};

export const startStory = async (
  imageUrl: string,
  genre?: string
): Promise<{state: StoryState, state_id: string}> => {
  const response = await api.post('/api/story/start',
    new URLSearchParams({
      image_url: imageUrl,
      genre: genre || 'adventure'
    }), {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
    }
  );

  return {
    state: response.data.state,
    state_id: response.data.state_id
  };
};

export const continueStory = async (
  choiceId: string,
  stateId: string
): Promise<{state: StoryState, state_id: string}> => {
  const response = await api.post('/api/story/continue',
    new URLSearchParams({
      choice_id: choiceId,
      state_id: stateId
    }), {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
    }
  );

  return {
    state: response.data.state,
    state_id: response.data.state_id
  };
};

export const rollbackStory = async (
  targetStep: number,
  stateId: string
): Promise<{state: StoryState, state_id: string, message: string}> => {
  const response = await api.post('/api/story/rollback',
    new URLSearchParams({
      target_step: targetStep.toString(),
      state_id: stateId
    }), {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
    }
  );

  return {
    state: response.data.state,
    state_id: response.data.state_id,
    message: response.data.message
  };
};

export default api;
