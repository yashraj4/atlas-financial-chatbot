import axios from 'axios';

const API_URL = 'http://localhost:8000/api/v1';

export const sendMessage = async (query) => {
  try {
    const response = await axios.post(`${API_URL}/chat`, { query });
    return response.data;
  } catch (error) {
    console.error("API Error:", error);
    throw error;
  }
};


