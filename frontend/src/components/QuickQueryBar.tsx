import React from 'react';

interface QuickQueryBarProps {
  onSelectQuery: (query: string) => void;
}

export const QuickQueryBar: React.FC<QuickQueryBarProps> = ({ onSelectQuery }) => {
  const queries = [
    { label: "🐮 Why did Cow 37's milk decrease?", text: "Why did Cow 37's milk decrease today?" },
    { label: "💉 What should I do now for Cow 37?", text: "What should I do now for Cow 37?" },
    { label: "🔥 Check Cow 14 artificial insemination timing", text: "Check Cow 14 artificial insemination breeding timing" },
    { label: "🌾 Check Cow 37 daily feed intake", text: "Check Cow 37 daily feed intake and nutrition target" },
    { label: "📊 Overall Farm Milk & Health Summary", text: "Give me an overall farm milk and health summary" }
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
