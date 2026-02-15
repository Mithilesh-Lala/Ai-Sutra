import { BookmarkIcon } from '@heroicons/react/24/outline';
import { BookmarkIcon as BookmarkSolidIcon } from '@heroicons/react/24/solid';

function ContentCard({ content, onSave, isSaved = false }) {
  return (
    <div className="card group min-h-[320px] flex flex-col">
      <div className="flex justify-between items-start mb-3">
        <h3 className="text-lg font-semibold text-gray-900 group-hover:text-primary-600 transition-colors line-clamp-2">
          {content.title}
        </h3>
        <button
          onClick={() => onSave(content.id)}
          className="text-gray-400 hover:text-primary-600 transition-colors flex-shrink-0 ml-2"
        >
          {isSaved ? (
            <BookmarkSolidIcon className="w-6 h-6 text-primary-600" />
          ) : (
            <BookmarkIcon className="w-6 h-6" />
          )}
        </button>
      </div>
      
      <p className="text-gray-600 text-sm mb-4 line-clamp-6 flex-grow">
        {content.summary}
      </p>
      
      <div className="flex items-center justify-between mt-auto pt-3 border-t border-gray-100">
        <span className="text-xs text-gray-500">{content.source}</span>
        
        {content.url && (
          <a 
            href={content.url}
            target="_blank"
            rel="noopener noreferrer"
            className="text-primary-600 hover:text-primary-700 font-medium text-sm"
          >
            Read more →
          </a>
        )}
        
        {!content.url && (
          <span className="text-gray-400 text-sm italic">AI Generated</span>
        )}
      </div>
    </div>
  );
}

export default ContentCard;