import React from 'react';
import { Pressable, Text } from 'react-native';
import { Redirect, Tabs, useRouter } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';
import { useAuth } from '../../src/auth';

export default function TabsLayout() {
  const { user, logout } = useAuth();
  const router = useRouter();
  if (!user) return <Redirect href="/login" />;

  const handleLogout = async () => {
    await logout();
    router.replace('/login');
  };

  return (
    <Tabs
      screenOptions={{
        tabBarActiveTintColor: '#0284c7',
        headerRight: () => (
          <Pressable onPress={handleLogout} style={{ marginRight: 14, flexDirection: 'row', alignItems: 'center', gap: 4 }}>
            <Ionicons name="log-out-outline" size={18} color="#e11d48" />
            <Text style={{ color: '#e11d48', fontWeight: '600', fontSize: 13 }}>Sair</Text>
          </Pressable>
        ),
      }}
    >
      <Tabs.Screen
        name="dashboard"
        options={{
          title: `CardioIA · ${user.name}`,
          tabBarLabel: 'Monitoramento',
          tabBarIcon: ({ color, size }) => <Ionicons name="pulse" size={size} color={color} />,
        }}
      />
      <Tabs.Screen
        name="chat"
        options={{
          title: 'Assistente CardioIA',
          tabBarLabel: 'Assistente IA',
          tabBarIcon: ({ color, size }) => (
            <Ionicons name="chatbubbles-outline" size={size} color={color} />
          ),
        }}
      />
    </Tabs>
  );
}
