// HomeScreen.js
// ---------------
// Landing screen after login. Entry point to Scan and History,
// and shows the logged-in user's name.

import React, { useEffect, useState } from "react";
import { View, Text, TouchableOpacity, StyleSheet, Image } from "react-native";
import { getCurrentUser, logoutUser } from "../services/api";

export default function HomeScreen({ navigation }) {
  const [user, setUser] = useState(null);

  useEffect(() => {
    (async () => setUser(await getCurrentUser()))();
  }, []);

  const handleLogout = async () => {
    await logoutUser();
    navigation.reset({ index: 0, routes: [{ name: "Login" }] });
  };

  return (
    <View style={styles.container}>
      <Text style={styles.greeting}>
        Hi{user ? `, ${user.full_name}` : ""} 👋
      </Text>
      <Text style={styles.subtitle}>
        Scan a tomato leaf to check for Early Blight, Late Blight, Leaf Mold, or a Healthy plant.
      </Text>

      <TouchableOpacity style={styles.primaryCard} onPress={() => navigation.navigate("Scan")}>
        <Text style={styles.primaryCardText}>📷  Scan New Leaf</Text>
      </TouchableOpacity>

      <TouchableOpacity style={styles.secondaryCard} onPress={() => navigation.navigate("History")}>
        <Text style={styles.secondaryCardText}>🕘  View Scan History</Text>
      </TouchableOpacity>

      <TouchableOpacity style={styles.logoutButton} onPress={handleLogout}>
        <Text style={styles.logoutText}>Log Out</Text>
      </TouchableOpacity>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, padding: 24, backgroundColor: "#F5F9F5", justifyContent: "center" },
  greeting: { fontSize: 26, fontWeight: "bold", color: "#2E7D32", marginBottom: 8 },
  subtitle: { fontSize: 14, color: "#555", marginBottom: 32, lineHeight: 20 },
  primaryCard: {
    backgroundColor: "#2E7D32",
    borderRadius: 12,
    padding: 20,
    alignItems: "center",
    marginBottom: 16,
  },
  primaryCardText: { color: "#fff", fontSize: 18, fontWeight: "600" },
  secondaryCard: {
    backgroundColor: "#fff",
    borderWidth: 1,
    borderColor: "#2E7D32",
    borderRadius: 12,
    padding: 18,
    alignItems: "center",
    marginBottom: 40,
  },
  secondaryCardText: { color: "#2E7D32", fontSize: 16, fontWeight: "600" },
  logoutButton: { alignItems: "center" },
  logoutText: { color: "#999", fontSize: 14 },
});
