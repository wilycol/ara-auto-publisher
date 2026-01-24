import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { DashboardLayout } from './layouts/DashboardLayout';
import { Dashboard } from './pages/Dashboard';
import { HumanControl } from './pages/HumanControl';
import { Overrides } from './pages/Overrides';
import { CampaignsList } from './pages/CampaignsList';
import { CampaignDetails } from './pages/CampaignDetails';
import { Guide } from './pages/Guide';
import { Tracking } from './pages/Tracking';
import { Support } from './pages/Support';
import { Connections } from './pages/Connections';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<DashboardLayout />}>
          <Route index element={<Dashboard />} />
          <Route path="control" element={<HumanControl />} />
          <Route path="overrides" element={<Overrides />} />
          <Route path="campaigns" element={<CampaignsList />} />
          <Route path="campaigns/:id" element={<CampaignDetails />} />
          <Route path="guide" element={<Guide />} />
          <Route path="tracking" element={<Tracking />} />
          <Route path="connections" element={<Connections />} />
          <Route path="support" element={<Support />} />
          {/* Future routes */}
          <Route path="settings" element={<div className="p-4">Configuración (Próximamente)</div>} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

export default App;
