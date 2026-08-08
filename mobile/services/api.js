// api.js
// -------
// Every network call the app makes goes through here.
// Keeping this in one file means screens don't need to know about
// URLs, headers, or tokens -- they just call these functions.

import axios from "axios";
import AsyncStorage from "@react-native-async-storage/async-storage";
import { API_BASE_URL } from "./config";

const client = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000, // scanning involves VGG16 inference, give it time
});

// Attach the saved JWT token (if any) to every outgoing request.
client.interceptors.request.use(async (config) => {
  const token = await AsyncStorage.getItem("agrolens_token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// --- Auth ---------------------------------------------------------------

export async function registerUser(fullName, email, password) {
  const res = await client.post("/api/auth/register", {
    full_name: fullName,
    email,
    password,
  });
  await AsyncStorage.setItem("agrolens_token", res.data.token);
  await AsyncStorage.setItem("agrolens_user", JSON.stringify(res.data.user));
  return res.data;
}

export async function loginUser(email, password) {
  const res = await client.post("/api/auth/login", { email, password });
  await AsyncStorage.setItem("agrolens_token", res.data.token);
  await AsyncStorage.setItem("agrolens_user", JSON.stringify(res.data.user));
  return res.data;
}

export async function logoutUser() {
  await AsyncStorage.removeItem("agrolens_token");
  await AsyncStorage.removeItem("agrolens_user");
}

export async function getCurrentUser() {
  const raw = await AsyncStorage.getItem("agrolens_user");
  return raw ? JSON.parse(raw) : null;
}

export async function isLoggedIn() {
  const token = await AsyncStorage.getItem("agrolens_token");
  return !!token;
}

// --- Scan / Upload --------------------------------------------------------

/**
 * Sends a leaf photo to the backend for VGG16+SVM prediction.
 * `imageAsset` is the object returned by expo-image-picker
 * (has .uri, and optionally .fileName / .mimeType).
 */
export async function scanLeafImage(imageAsset) {
  const formData = new FormData();
  const filename = imageAsset.fileName || "leaf.jpg";
  const fileType = imageAsset.mimeType || "image/jpeg";

  formData.append("image", {
    uri: imageAsset.uri,
    name: filename,
    type: fileType,
  });

  const res = await client.post("/api/scan", formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });
  return res.data;
}

// --- History ---------------------------------------------------------------

export async function fetchScanHistory() {
  const res = await client.get("/api/history");
  return res.data.history;
}

export default client;
