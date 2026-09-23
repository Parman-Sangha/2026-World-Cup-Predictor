import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { motion } from 'framer-motion';
import clsx from 'clsx';
import { twMerge } from 'tailwind-merge';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

function cn(...inputs) {
  return twMerge(clsx(inputs));
}

export default function App() {
  const [view, setView] = useState('predict'); // 'predict' or 'simulate'

  return (
    <div className="min-h-screen bg-slate-900 text-slate-100 font-sans selection:bg-cyan-500 selection:text-white">
      <div className="max-w-5xl mx-auto px-4 py-12">
        <header className="text-center mb-12">
          <h1 className="text-5xl font-extrabold bg-gradient-to-r from-cyan-400 to-blue-600 bg-clip-text text-transparent mb-4">
            2026 World Cup Predictor
          </h1>
          <p className="text-slate-400 text-lg">
            Elo-based match predictions and tournament simulations, trained on 49,000 international matches.
          </p>
        </header>

        <nav className="flex justify-center gap-4 mb-12">
          <button
            onClick={() => setView('predict')}
            className={cn(
              "px-6 py-2 rounded-full font-semibold transition-all duration-300",
              view === 'predict'
                ? "bg-cyan-500 text-white shadow-lg shadow-cyan-500/25"
                : "bg-slate-800 text-slate-400 hover:bg-slate-700"
            )}
          >
            Match Predictor
          </button>
          <button
            onClick={() => setView('simulate')}
            className={cn(
              "px-6 py-2 rounded-full font-semibold transition-all duration-300",
              view === 'simulate'
                ? "bg-purple-500 text-white shadow-lg shadow-purple-500/25"
                : "bg-slate-800 text-slate-400 hover:bg-slate-700"
            )}
          >
            Tournament Sim
          </button>
        </nav>

        <main>
          {view === 'predict' ? <MatchPredictor /> : <TournamentSim />}
        </main>
      </div>
    </div>
  );
}

function MatchPredictor() {
  const [teams, setTeams] = useState([]);
  const [teamA, setTeamA] = useState('');
  const [teamB, setTeamB] = useState('');
  const [host, setHost] = useState('');
  const [prediction, setPrediction] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    axios.get(`${API_URL}/teams`)
      .then(res => setTeams(res.data))
      .catch(err => console.error(err));
  }, []);

  const handlePredict = async () => {
    if (!teamA || !teamB) return;
    setLoading(true);
    try {
      const res = await axios.post(`${API_URL}/predict`, {
        team_a: teamA,
        team_b: teamB,
        host: host || null
      });
      setPrediction(res.data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-slate-800/50 backdrop-blur-xl p-8 rounded-2xl border border-slate-700 shadow-xl">
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <div className="space-y-2">
          <label className="block text-sm font-medium text-slate-400">Team A</label>
          <select
            className="w-full bg-slate-900 border border-slate-700 rounded-lg px-4 py-3 focus:ring-2 focus:ring-cyan-500 outline-none transition-all"
            value={teamA}
            onChange={(e) => setTeamA(e.target.value)}
          >
            <option value="">Select Team</option>
            {teams.map(t => <option key={t} value={t}>{t}</option>)}
          </select>
        </div>

        <div className="space-y-2">
          <label className="block text-sm font-medium text-slate-400">Host (Optional)</label>
          <select
            className="w-full bg-slate-900 border border-slate-700 rounded-lg px-4 py-3 focus:ring-2 focus:ring-cyan-500 outline-none transition-all"
            value={host}
            onChange={(e) => setHost(e.target.value)}
          >
            <option value="">Neutral Ground</option>
            {teams.map(t => <option key={t} value={t}>{t}</option>)}
          </select>
        </div>

        <div className="space-y-2">
          <label className="block text-sm font-medium text-slate-400">Team B</label>
          <select
            className="w-full bg-slate-900 border border-slate-700 rounded-lg px-4 py-3 focus:ring-2 focus:ring-cyan-500 outline-none transition-all"
            value={teamB}
            onChange={(e) => setTeamB(e.target.value)}
          >
            <option value="">Select Team</option>
            {teams.map(t => <option key={t} value={t}>{t}</option>)}
          </select>
        </div>
      </div>

      <div className="text-center mb-8">
        <button
          onClick={handlePredict}
          disabled={loading || !teamA || !teamB}
          className="bg-gradient-to-r from-cyan-500 to-blue-600 text-white font-bold py-3 px-8 rounded-lg shadow-lg shadow-cyan-500/25 hover:scale-105 active:scale-95 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {loading ? 'Analyzing...' : 'Predict Outcome'}
        </button>
      </div>

      {prediction && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="bg-slate-900 rounded-xl p-6 border border-slate-700"
        >
          <div className="flex justify-between items-center mb-6">
            <div className="text-center w-1/3">
              <h3 className="text-xl font-bold text-white mb-1">{prediction.team_a}</h3>
              <div className="text-3xl font-black text-cyan-400">{(prediction.team_a_win * 100).toFixed(1)}%</div>
              <div className="text-xs text-slate-500 mt-1">Win Probability</div>
            </div>
            <div className="text-center w-1/3 border-x border-slate-800">
              <div className="text-2xl font-bold text-slate-400">{(prediction.draw * 100).toFixed(1)}%</div>
              <div className="text-xs text-slate-500 mt-1">Draw</div>
            </div>
            <div className="text-center w-1/3">
              <h3 className="text-xl font-bold text-white mb-1">{prediction.team_b}</h3>
              <div className="text-3xl font-black text-blue-400">{(prediction.team_b_win * 100).toFixed(1)}%</div>
              <div className="text-xs text-slate-500 mt-1">Win Probability</div>
            </div>
          </div>

          <div className="h-4 bg-slate-800 rounded-full overflow-hidden flex">
            <div style={{ width: `${prediction.team_a_win * 100}%` }} className="bg-cyan-500 h-full" />
            <div style={{ width: `${prediction.draw * 100}%` }} className="bg-slate-600 h-full" />
            <div style={{ width: `${prediction.team_b_win * 100}%` }} className="bg-blue-500 h-full" />
          </div>
        </motion.div>
      )}
    </div>
  );
}

const STAGE_COLUMNS = [
  ['round_of_16', 'R16'],
  ['quarterfinal', 'QF'],
  ['semifinal', 'SF'],
  ['final', 'Final'],
  ['champion', 'Win'],
];

function TournamentSim() {
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [showAll, setShowAll] = useState(false);

  const runSim = async () => {
    setLoading(true);
    try {
      const res = await axios.get(`${API_URL}/simulate?n_iter=10000`);
      setResults(res.data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-slate-800/50 backdrop-blur-xl p-8 rounded-2xl border border-slate-700 shadow-xl">
      <div className="text-center mb-8">
        <p className="text-slate-400 mb-6">
          Simulate the real 2026 format 10,000 times: the 12 official groups, the top two plus the
          8 best third-placed teams, and the Round of 32 bracket through to the final.
        </p>
        <button
          onClick={runSim}
          disabled={loading}
          className="bg-gradient-to-r from-purple-500 to-pink-600 text-white font-bold py-3 px-8 rounded-lg shadow-lg shadow-purple-500/25 hover:scale-105 active:scale-95 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {loading ? 'Simulating Tournament...' : 'Run Simulation'}
        </button>
      </div>

      {results.length > 0 && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="overflow-x-auto rounded-xl border border-slate-700"
        >
          <table className="w-full text-left border-collapse">
            <thead className="bg-slate-900 text-slate-400 uppercase text-xs font-semibold">
              <tr>
                <th className="p-4">Rank</th>
                <th className="p-4">Team</th>
                {STAGE_COLUMNS.map(([, label]) => (
                  <th key={label} className="p-4 text-right">{label}</th>
                ))}
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-700 bg-slate-800">
              {results.slice(0, showAll ? results.length : 16).map((row, i) => (
                <tr key={row.team} className="hover:bg-slate-700/50 transition-colors">
                  <td className="p-4 text-slate-500 font-mono">#{i + 1}</td>
                  <td className="p-4 font-bold text-white whitespace-nowrap">
                    {row.team}
                    <span className="ml-2 text-xs font-normal text-slate-500">Group {row.group}</span>
                  </td>
                  {STAGE_COLUMNS.map(([key]) => (
                    <td key={key} className="p-4 text-right font-mono text-sm">
                      <span className={cn(
                        key === 'champion' ? "px-2 py-1 rounded font-bold" : "text-slate-300",
                        key === 'champion' && i === 0 ? "bg-yellow-500/20 text-yellow-400" : key === 'champion' && "text-white"
                      )}>
                        {(row[key] * 100).toFixed(1)}%
                      </span>
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
          <button
            onClick={() => setShowAll(!showAll)}
            className="w-full bg-slate-900 p-3 text-center text-xs text-slate-400 hover:text-white transition-colors"
          >
            {showAll ? 'Show top 16' : `Show all ${results.length} teams`}
          </button>
        </motion.div>
      )}
    </div>
  );
}
