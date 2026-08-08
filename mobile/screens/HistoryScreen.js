// HistoryScreen.js
// ------------------
// Lists the user's past scans, newest first, pulled from
// GET /api/history.

import React, { useEffect, useState, useCallback } from "react";
import {
  View,
  Text,
  FlatList,
  Image,
  StyleSheet,
  ActivityIndicator,
  RefreshControl,
} from "react-native";
import { fetchScanHistory } from "../services/api";
import { API_BASE_URL } from "../services/config";

function formatLabel(label) {
  return label.replace(/_/g, " ");
}

export default function HistoryScreen() {
  const [scans, setScans] = useState([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  const loadHistory = useCallback(async () => {
    try {
      const data = await fetchScanHistory();
      setScans(data);
    } catch (err) {
      console.warn("Failed to load history:", err?.message);
    }
  }, []);

  useEffect(() => {
    (async () => {
      await loadHistory();
      setLoading(false);
    })();
  }, [loadHistory]);

  const onRefresh = async () => {
    setRefreshing(true);
    await loadHistory();
    setRefreshing(false);
  };

  if (loading) {
    return (
      <View style={styles.center}>
        <ActivityIndicator size="large" color="#2E7D32" />
      </View>
    );
  }

  if (scans.length === 0) {
    return (
      <View style={styles.center}>
        <Text style={styles.emptyText}>No scans yet. Go scan a leaf!</Text>
      </View>
    );
  }

  return (
    <FlatList
      data={scans}
      keyExtractor={(item) => String(item.id)}
      contentContainerStyle={styles.list}
      refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} />}
      renderItem={({ item }) => (
        <View style={styles.row}>
          <Image source={{ uri: `${API_BASE_URL}${item.image_url}` }} style={styles.thumb} />
          <View style={styles.rowText}>
            <Text style={styles.rowTitle}>{formatLabel(item.predicted_class)}</Text>
            <Text style={styles.rowSubtitle}>
              {Math.round(item.confidence * 100)}% confidence
            </Text>
            <Text style={styles.rowDate}>{item.created_at}</Text>
          </View>
        </View>
      )}
    />
  );
}

const styles = StyleSheet.create({
  center: { flex: 1, justifyContent: "center", alignItems: "center", backgroundColor: "#F5F9F5" },
  emptyText: { color: "#888" },
  list: { padding: 16, backgroundColor: "#F5F9F5" },
  row: {
    flexDirection: "row",
    backgroundColor: "#fff",
    borderRadius: 10,
    padding: 10,
    marginBottom: 12,
    alignItems: "center",
    borderWidth: 1,
    borderColor: "#eee",
  },
  thumb: { width: 56, height: 56, borderRadius: 8, marginRight: 12 },
  rowText: { flex: 1 },
  rowTitle: { fontWeight: "bold", fontSize: 15, color: "#333" },
  rowSubtitle: { fontSize: 12, color: "#666" },
  rowDate: { fontSize: 11, color: "#999", marginTop: 2 },
});
