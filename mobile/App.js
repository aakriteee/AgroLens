// App.js
// -------
// Entry point. Sets up navigation between screens and decides whether
// to show the auth flow (Login/Signup) or the main app (Home/Scan/etc)
// based on whether a JWT token is already stored on the device.

import React, { useEffect, useState } from "react";
import { NavigationContainer } from "@react-navigation/native";
import { createNativeStackNavigator } from "@react-navigation/native-stack";
import { View, ActivityIndicator } from "react-native";

import { isLoggedIn } from "./services/api";

import LoginScreen from "./screens/LoginScreen";
import SignupScreen from "./screens/SignupScreen";
import HomeScreen from "./screens/HomeScreen";
import ScanScreen from "./screens/ScanScreen";
import ResultScreen from "./screens/ResultScreen";
import HistoryScreen from "./screens/HistoryScreen";

const Stack = createNativeStackNavigator();

export default function App() {
  const [checkingAuth, setCheckingAuth] = useState(true);
  const [loggedIn, setLoggedIn] = useState(false);

  useEffect(() => {
    (async () => {
      const result = await isLoggedIn();
      setLoggedIn(result);
      setCheckingAuth(false);
    })();
  }, []);

  if (checkingAuth) {
    return (
      <View style={{ flex: 1, justifyContent: "center", alignItems: "center" }}>
        <ActivityIndicator size="large" color="#2E7D32" />
      </View>
    );
  }

  return (
    <NavigationContainer>
      <Stack.Navigator
        initialRouteName={loggedIn ? "Home" : "Login"}
        screenOptions={{
          headerStyle: { backgroundColor: "#2E7D32" },
          headerTintColor: "#fff",
          headerTitleStyle: { fontWeight: "bold" },
        }}
      >
        <Stack.Screen name="Login" component={LoginScreen} options={{ title: "AgroLens Login" }} />
        <Stack.Screen name="Signup" component={SignupScreen} options={{ title: "Create Account" }} />
        <Stack.Screen name="Home" component={HomeScreen} options={{ title: "AgroLens" }} />
        <Stack.Screen name="Scan" component={ScanScreen} options={{ title: "Scan Leaf" }} />
        <Stack.Screen name="Result" component={ResultScreen} options={{ title: "Diagnosis" }} />
        <Stack.Screen name="History" component={HistoryScreen} options={{ title: "Scan History" }} />
      </Stack.Navigator>
    </NavigationContainer>
  );
}
