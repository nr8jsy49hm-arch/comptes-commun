import { useState } from "react";
import Dashboard from "./components/Dashboard";
import DepenseForm from "./components/DepenseForm";

export default function App() {
  const [refreshKey, setRefreshKey] = useState(0);

  return (
    <div className="app">
      <h1>Comptes Communs</h1>
      <Dashboard key={refreshKey} />
      <DepenseForm onDepenseCreee={() => setRefreshKey((k) => k + 1)} />
    </div>
  );
}
