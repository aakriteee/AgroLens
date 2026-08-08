// ScanScreen.js
// ---------------
// Lets the farmer either take a new photo with the camera or pick an
// existing photo from the gallery ("scan" and "upload" both live here),
// previews it, then sends it to the backend for VGG16+SVM prediction.

import React, { useState } from "react";
import {
  View,
  Text,
  Image,
  TouchableOpacity,
  StyleSheet,
  ActivityIndicator,
  Alert,
  ScrollView,
} from "react-native";
import * as ImagePicker from "expo-image-picker";
import { scanLeafImage } from "../services/api";

export default function ScanScreen({ navigation }) {
  const [selectedImage, setSelectedImage] = useState(null); // expo-image-picker asset
  const [submitting, setSubmitting] = useState(false);

  const takePhoto = async () => {
    const permission = await ImagePicker.requestCameraPermissionsAsync();
    if (!permission.granted) {
      Alert.alert("Camera permission needed", "Please allow camera access to scan a leaf.");
      return;
    }
    const result = await ImagePicker.launchCameraAsync({
      quality: 0.8,
      allowsEditing: true,
      aspect: [1, 1],
    });
    if (!result.canceled) {
      setSelectedImage(result.assets[0]);
    }
  };

  const pickFromGallery = async () => {
    const permission = await ImagePicker.requestMediaLibraryPermissionsAsync();
    if (!permission.granted) {
      Alert.alert("Gallery permission needed", "Please allow photo library access to upload a leaf image.");
      return;
    }
    const result = await ImagePicker.launchImageLibraryAsync({
      mediaTypes: ImagePicker.MediaTypeOptions.Images,
      quality: 0.8,
      allowsEditing: true,
      aspect: [1, 1],
    });
    if (!result.canceled) {
      setSelectedImage(result.assets[0]);
    }
  };

  const submitForDiagnosis = async () => {
    if (!selectedImage) {
      Alert.alert("No image selected", "Please take or upload a leaf photo first.");
      return;
    }
    setSubmitting(true);
    try {
      const result = await scanLeafImage(selectedImage);
      navigation.navigate("Result", { result, imageUri: selectedImage.uri });
    } catch (err) {
      const message =
        err?.response?.data?.error || "Could not analyze the image. Please try again.";
      Alert.alert("Scan failed", message);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <ScrollView contentContainerStyle={styles.container}>
      <Text style={styles.title}>Scan a Tomato Leaf</Text>
      <Text style={styles.hint}>
        For best results: use good lighting, place a single leaf against a plain background,
        and fill most of the frame with the leaf.
      </Text>

      <View style={styles.previewBox}>
        {selectedImage ? (
          <Image source={{ uri: selectedImage.uri }} style={styles.previewImage} />
        ) : (
          <Text style={styles.previewPlaceholder}>No image selected yet</Text>
        )}
      </View>

      <View style={styles.row}>
        <TouchableOpacity style={styles.actionButton} onPress={takePhoto}>
          <Text style={styles.actionButtonText}>📷 Camera</Text>
        </TouchableOpacity>
        <TouchableOpacity style={styles.actionButton} onPress={pickFromGallery}>
          <Text style={styles.actionButtonText}>🖼️ Upload</Text>
        </TouchableOpacity>
      </View>

      <TouchableOpacity
        style={[styles.submitButton, !selectedImage && styles.submitButtonDisabled]}
        onPress={submitForDiagnosis}
        disabled={!selectedImage || submitting}
      >
        {submitting ? (
          <ActivityIndicator color="#fff" />
        ) : (
          <Text style={styles.submitButtonText}>Analyze Leaf</Text>
        )}
      </TouchableOpacity>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { flexGrow: 1, padding: 24, backgroundColor: "#F5F9F5" },
  title: { fontSize: 22, fontWeight: "bold", color: "#2E7D32", marginBottom: 6 },
  hint: { fontSize: 13, color: "#666", marginBottom: 20, lineHeight: 18 },
  previewBox: {
    height: 280,
    backgroundColor: "#fff",
    borderRadius: 12,
    borderWidth: 1,
    borderColor: "#ddd",
    justifyContent: "center",
    alignItems: "center",
    marginBottom: 20,
    overflow: "hidden",
  },
  previewImage: { width: "100%", height: "100%", resizeMode: "cover" },
  previewPlaceholder: { color: "#999" },
  row: { flexDirection: "row", justifyContent: "space-between", marginBottom: 20 },
  actionButton: {
    flex: 1,
    backgroundColor: "#fff",
    borderWidth: 1,
    borderColor: "#2E7D32",
    borderRadius: 10,
    padding: 14,
    alignItems: "center",
    marginHorizontal: 4,
  },
  actionButtonText: { color: "#2E7D32", fontWeight: "600" },
  submitButton: {
    backgroundColor: "#2E7D32",
    borderRadius: 10,
    padding: 16,
    alignItems: "center",
  },
  submitButtonDisabled: { backgroundColor: "#a5c9a7" },
  submitButtonText: { color: "#fff", fontSize: 16, fontWeight: "600" },
});
