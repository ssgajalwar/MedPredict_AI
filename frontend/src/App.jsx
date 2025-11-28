import React, { useState } from 'react';
import Sidebar from './components/Sidebar';
import Layout from './components/Layout';
import Dashboard from './components/Dashboard';
import Resources from './components/Resources';
import Broadcast from './components/Broadcast';

import Analytics from './components/Analytics';
import Inventory from './components/Inventory';
import Reports from './components/Reports';

function App() {
  const [activeTab, setActiveTab] = useState('dashboard');

  return (
    <div className="flex bg-slate-50 min-h-screen font-sans text-slate-900">
      <Sidebar activeTab={activeTab} setActiveTab={setActiveTab} />
      <Layout>
        {activeTab === 'dashboard' && <Dashboard />}
        {activeTab === 'analytics' && <Analytics />}
        {activeTab === 'resources' && <Resources />}
        {activeTab === 'inventory' && <Inventory />}
        {activeTab === 'reports' && <Reports />}
        {activeTab === 'broadcast' && <Broadcast />}
      </Layout>
    </div>
  );
}

export default App;
