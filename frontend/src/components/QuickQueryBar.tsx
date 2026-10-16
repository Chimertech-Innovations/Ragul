import React from 'react';

interface QuickQueryBarProps {
  onSelectQuery: (query: string) => void;
}

export const QuickQueryBar: React.FC<QuickQueryBarProps> = ({ onSelectQuery }) => {
  const queries = [
    { label: "🔥 Which cows show estrus / heat signs today?", text: "Which cows have estrus signs today?" },
    { label: "🐮 What mounting behavior was detected on CAM01?", text: "What mounting behavior was detected by CAM01 camera?" },
    { label: "🌾 Check cattle feeding and manger activity", text: "Check cattle feeding and manger activity logs" },
    { label: "📊 Overall Farm Vision & Cattle Summary", text: "Give me an overall farm vision activity summary" },
    { label: "💉 Recommended breeding window for cows in heat", text: "What is the recommended breeding window for cows in heat?" }
  ];

  return (
    <div className="quick-queries">
      <span style={{ fontSize: '0.78rem', color: 'var(--text-muted)', alignSelf: 'center', marginRight: '6px', fontWeight: 600 }}>
        Quick Farm Questions:
      </span>
      {queries.map((q, idx) => (
        <button key={idx} className="chip" onClick={() => onSelectQuery(q.text)}>
          {q.label}
        </button>
      ))}
    </div>
  );
};
