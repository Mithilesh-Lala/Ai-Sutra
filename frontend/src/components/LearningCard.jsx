import { useState } from 'react';

function LearningCard({ content, onSave, isSaved }) {
  const [showFull, setShowFull] = useState(false);

  return (
    <div className="bg-white rounded-xl shadow-md overflow-hidden">
      {/* Header */}
      <div className="p-6 border-b">
        <div className="flex justify-between items-start mb-2">
          <h2 className="text-2xl font-bold text-gray-900">
            {content.title}
          </h2>
          <button
            onClick={() => onSave(content.id)}
            className={`text-2xl ${
              isSaved ? 'text-yellow-500' : 'text-gray-400 hover:text-yellow-500'
            }`}
          >
            {isSaved ? '★' : '☆'}
          </button>
        </div>
        
        <p className="text-gray-600 text-sm">
          {content.summary}
        </p>
        
        <div className="flex items-center gap-4 mt-3 text-xs text-gray-500">
          <span>{content.source}</span>
          <span>•</span>
          <span>{new Date(content.fetched_at).toLocaleDateString()}</span>
        </div>
      </div>

      {/* Full Content */}
      <div className="p-6">
        <div className="prose max-w-none">
          {content.content.split('\n\n').map((paragraph, index) => {
            // Check if it's a header
            if (paragraph.startsWith('## ')) {
              return (
                <h2 key={index} className="text-xl font-bold text-gray-900 mt-6 mb-3">
                  {paragraph.replace('## ', '')}
                </h2>
              );
            }
            // Check if it's a code block
            if (paragraph.startsWith('```')) {
              const code = paragraph.replace(/```python|```/g, '').trim();
              return (
                <pre key={index} className="bg-gray-100 p-4 rounded-lg overflow-x-auto my-4">
                  <code className="text-sm">{code}</code>
                </pre>
              );
            }
            // Regular paragraph
            return (
              <p key={index} className="text-gray-700 mb-4 leading-relaxed">
                {paragraph}
              </p>
            );
          })}
        </div>
      </div>
    </div>
  );
}

export default LearningCard;