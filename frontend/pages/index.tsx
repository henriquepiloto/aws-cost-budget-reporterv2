import React from 'react';
import AdminPanel from './components/AdminPanel';
import CloudinhoChat from './components/CloudinhoChat';

export default function Home() {
  return (
    <div className="min-h-screen bg-gray-50">
      <AdminPanel />
      <CloudinhoChat />
    </div>
  );
}
