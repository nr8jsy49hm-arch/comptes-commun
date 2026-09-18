import { useEffect, useState } from "react";
import {
  BarChart,
  Bar,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";
import { getAnneesDisponibles, getHistoriqueAnnee, getEvolutionEpargne } from "../api";

function TooltipPersonnalise({ active, payload, label, suffixe = "€" }) {
  if (!active || !payload || !payload.length) return null;
  return (
    <div className="graphique-tooltip">
      <strong>{label}</strong>
      <div>{payload[0].value.toFixed(2)} {suffixe}</div>
    </div>
  );
}

export default function Graphiques() {
  const [annees, setAnnees] = useState([]);
  const [anneeSelectionnee, setAnneeSelectionnee] = useState(null);
  const [donneesDepenses, setDonneesDepenses] = useState([]);
  const [donneesEpargne, setDonneesEpargne] = useState([]);

  useEffect(() => {
    getAnneesDisponibles().then((res) => {
      setAnnees(res.data);
      if (res.data.length > 0) setAnneeSelectionnee(res.data[0]);
    });
  }, []);

  useEffect(() => {
    if (anneeSelectionnee == null) return;
    getHistoriqueAnnee(anneeSelectionnee).then((res) => {
      setDonneesDepenses(res.data.map((m) => ({ nom: m.nom_mois.slice(0, 3), montant: m.total_depense })));
    });

    let cumul = 0;
    getEvolutionEpargne(anneeSelectionnee).then((res) => {
      setDonneesEpargne(
        res.data.map((m) => {
          cumul += m.total_verse;
          return { nom: m.nom_mois.slice(0, 3), cumul: Math.round(cumul * 100) / 100 };
        })
      );
    });
  }, [anneeSelectionnee]);

  if (annees.length === 0) return null;

  return (
    <div className="dashboard graphiques">
      <div className="historique-header">
        <h3>Graphiques</h3>
        <select
          value={anneeSelectionnee ?? ""}
          onChange={(e) => setAnneeSelectionnee(Number(e.target.value))}
        >
          {annees.map((a) => (
            <option key={a} value={a}>
              {a}
            </option>
          ))}
        </select>
      </div>

      <h4>Dépenses communes par mois</h4>
      <div className="graphique-conteneur">
        <ResponsiveContainer width="100%" height={220}>
          <BarChart data={donneesDepenses} margin={{ top: 8, right: 8, left: 0, bottom: 0 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="var(--color-line)" vertical={false} />
            <XAxis dataKey="nom" tick={{ fill: "var(--color-ink-soft)", fontSize: 12 }} axisLine={{ stroke: "var(--color-line)" }} tickLine={false} />
            <YAxis tick={{ fill: "var(--color-ink-soft)", fontSize: 12 }} axisLine={false} tickLine={false} width={40} />
            <Tooltip content={<TooltipPersonnalise />} cursor={{ fill: "var(--color-parchment)" }} />
            <Bar dataKey="montant" fill="var(--color-brass)" radius={[4, 4, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>

      <h4>Épargne cumulée (tous objectifs)</h4>
      <div className="graphique-conteneur">
        <ResponsiveContainer width="100%" height={220}>
          <LineChart data={donneesEpargne} margin={{ top: 8, right: 8, left: 0, bottom: 0 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="var(--color-line)" vertical={false} />
            <XAxis dataKey="nom" tick={{ fill: "var(--color-ink-soft)", fontSize: 12 }} axisLine={{ stroke: "var(--color-line)" }} tickLine={false} />
            <YAxis tick={{ fill: "var(--color-ink-soft)", fontSize: 12 }} axisLine={false} tickLine={false} width={40} />
            <Tooltip content={<TooltipPersonnalise />} cursor={{ stroke: "var(--color-line)" }} />
            <Line type="monotone" dataKey="cumul" stroke="var(--color-pine)" strokeWidth={2.5} dot={{ r: 3, fill: "var(--color-pine)" }} />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
