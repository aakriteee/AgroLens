// ResultScreen.js
// -----------------
// Displays the VGG16+SVM prediction returned by the backend: the
// disease class, confidence %, per-class probability breakdown, and
// a recommended action for the farmer.

import React from "react";
import { View, Text, Image, StyleSheet, ScrollView, TouchableOpacity } from "react-native";

const STATUS_COLORS = {
  Healthy: "#2E7D32",
  Early_Blight: "#F9A825",
  Late_Blight: "#C62828",
  Leaf_Mold: "#EF6C00",
};

function formatLabel(label) {
  return label.replace(/_/g, " ");
}

const CONFIDENCE_THRESHOLD = 50; // below this %, we don't trust the prediction

export default function ResultScreen({ route, navigation }) {
  const { result, imageUri } = route.params;
  const confidencePct = Math.round(result.confidence * 100);
  const isUncertain = confidencePct < CONFIDENCE_THRESHOLD;
  const color = isUncertain ? "#757575" : (STATUS_COLORS[result.prediction] || "#2E7D32");

  const sortedProbs = Object.entries(result.all_class_probabilities || {}).sort(
    (a, b) => b[1] - a[1]
  );

  return (
    <ScrollView contentContainerStyle={styles.container}>
      <Image source={{ uri: imageUri }} style={styles.image} />

      <View style={[styles.badge, { backgroundColor: color }]}>
        <Text style={styles.badgeText}>
          {isUncertain ? "Uncertain Result" : formatLabel(result.prediction)}
        </Text>
      </View>
      <Text style={styles.confidence}>{confidencePct}% confidence</Text>

      {isUncertain ? (
        <View style={[styles.card, styles.warningCard]}>
          <Text style={styles.cardTitle}>⚠️ Low Confidence</Text>
          <Text style={styles.cardBody}>
            This image doesn't clearly match a tomato leaf disease we recognize.
            It may not be a tomato leaf, the photo may be unclear, or it could be
            a healthy/diseased pattern outside what this model was trained on.
            Try a clearer, well-lit photo of a single tomato leaf.
          </Text>
        </View>
      ) : (
        <View style={styles.card}>
          <Text style={styles.cardTitle}>Recommendation</Text>
          <Text style={styles.cardBody}>{result.recommendation}</Text>
        </View>
      )}

      <View style={styles.card}>
        <Text style={styles.cardTitle}>Class Probabilities</Text>
        {sortedProbs.map(([label, prob]) => (
          <View key={label} style={styles.probRow}>
            <Text style={styles.probLabel}>{formatLabel(label)}</Text>
            <View style={styles.probBarTrack}>
              <View style={[styles.probBarFill, { width: `${prob * 100}%` }]} />
            </View>
            <Text style={styles.probValue}>{Math.round(prob * 100)}%</Text>
          </View>
        ))}
      </View>

      <TouchableOpacity style={styles.button} onPress={() => navigation.navigate("Scan")}>
        <Text style={styles.buttonText}>Scan Another Leaf</Text>
      </TouchableOpacity>
      <TouchableOpacity
        style={styles.secondaryButton}
        onPress={() => navigation.navigate("Home")}
      >
        <Text style={styles.secondaryButtonText}>Back to Home</Text>
      </TouchableOpacity>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { flexGrow: 1, padding: 24, backgroundColor: "#F5F9F5", alignItems: "center" },
  image: { width: 220, height: 220, borderRadius: 12, marginBottom: 16 },
  badge: { paddingVertical: 8, paddingHorizontal: 20, borderRadius: 20, marginBottom: 6 },
  badgeText: { color: "#fff", fontSize: 18, fontWeight: "bold" },
  confidence: { color: "#555", marginBottom: 20 },
  card: {
    width: "100%",
    backgroundColor: "#fff",
    borderRadius: 12,
    padding: 16,
    marginBottom: 16,
    borderWidth: 1,
    borderColor: "#eee",
  },
  cardTitle: { fontWeight: "bold", fontSize: 15, marginBottom: 8, color: "#333" },
  warningCard: { backgroundColor: "#FFF3E0", borderColor: "#FFB74D" },
  cardBody: { fontSize: 14, color: "#555", lineHeight: 20 },
  probRow: { flexDirection: "row", alignItems: "center", marginBottom: 10 },
  probLabel: { width: 100, fontSize: 12, color: "#444" },
  probBarTrack: { flex: 1, height: 8, backgroundColor: "#eee", borderRadius: 4, marginHorizontal: 8 },
  probBarFill: { height: 8, backgroundColor: "#2E7D32", borderRadius: 4 },
  probValue: { width: 36, fontSize: 12, color: "#444", textAlign: "right" },
  button: {
    backgroundColor: "#2E7D32",
    borderRadius: 10,
    padding: 14,
    alignItems: "center",
    width: "100%",
    marginTop: 8,
  },
  buttonText: { color: "#fff", fontWeight: "600" },
  secondaryButton: { padding: 12, alignItems: "center", width: "100%" },
  secondaryButtonText: { color: "#2E7D32", fontWeight: "600" },
});
