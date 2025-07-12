import React, { useState } from 'react';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { ChevronDown, ChevronUp, MapPin, AlertTriangle, Info, XCircle } from 'lucide-react';
import type { Source, CitationInstance } from '@/types/citations';

interface SourceWithCitationsProps {
  source: Source;
  showContext?: boolean;
  compact?: boolean;
}

const getSeverityIcon = (severity: CitationInstance['severity']) => {
  switch (severity) {
    case 'error': return <XCircle className="h-3 w-3" />;
    case 'warning': return <AlertTriangle className="h-3 w-3" />;
    case 'info': return <Info className="h-3 w-3" />;
    default: return <Info className="h-3 w-3" />;
  }
};

const getSeverityColor = (severity: CitationInstance['severity']) => {
  switch (severity) {
    case 'error': return 'text-red-600 bg-red-50 border-red-200';
    case 'warning': return 'text-yellow-600 bg-yellow-50 border-yellow-200';
    case 'info': return 'text-blue-600 bg-blue-50 border-blue-200';
    default: return 'text-gray-600 bg-gray-50 border-gray-200';
  }
};

export const SourceWithCitations: React.FC<SourceWithCitationsProps> = ({ 
  source, 
  showContext = true, 
  compact = false 
}) => {
  const [expanded, setExpanded] = useState(false);
  
  // Show first 3 citations by default
  const maxVisible = 3;
  const visibleCitations = expanded ? 
    source.citationInstances : 
    source.citationInstances.slice(0, maxVisible);
  
  const hiddenCount = source.citationInstances.length - maxVisible;

  return (
    <div className="border border-gray-200 rounded-lg p-4 space-y-3">
      {/* Source Header */}
      <div className="space-y-2">
        <div className="flex items-start justify-between">
          <h3 className="font-medium text-lg leading-tight">{source.title}</h3>
          <Badge variant="outline" className="ml-2 shrink-0">
            {source.citationInstances.length} citation{source.citationInstances.length !== 1 ? 's' : ''}
          </Badge>
        </div>
        
        <div className="text-sm text-gray-600">
          {source.authors.join(', ')} ({source.year})
          {source.journal && <span className="text-gray-500"> • {source.journal}</span>}
        </div>
        
        {source.doi && (
          <div className="text-xs text-gray-500">
            DOI: {source.doi}
          </div>
        )}
      </div>

      {/* Citation Instances */}
      <div className="space-y-2">
        <div className="text-sm font-medium text-gray-700">
          Citations in document:
        </div>
        
        {visibleCitations.map((citation, index) => (
          <div 
            key={citation.id}
            className={`p-3 rounded border ${getSeverityColor(citation.severity)}`}
          >
            <div className="flex items-start gap-2">
              {getSeverityIcon(citation.severity)}
              <div className="flex-1 space-y-1">
                <div className="flex items-center gap-2 text-xs">
                  <MapPin className="h-3 w-3" />
                  <span>Page {citation.page}, Para {citation.paragraph}, Line {citation.line}</span>
                  <Badge variant="secondary" className="text-xs">
                    {citation.citationStyle}
                  </Badge>
                </div>
                
                {showContext && citation.context && (
                  <div className="text-sm text-gray-700 italic">
                    "{citation.context}..."
                  </div>
                )}
              </div>
            </div>
          </div>
        ))}
        
        {/* Expand/Collapse Button */}
        {source.citationInstances.length > maxVisible && (
          <Button
            variant="ghost"
            size="sm"
            onClick={() => setExpanded(!expanded)}
            className="w-full text-sm text-gray-600 hover:text-gray-800"
          >
            {expanded ? (
              <>
                <ChevronUp className="h-4 w-4 mr-1" />
                Show fewer citations
              </>
            ) : (
              <>
                <ChevronDown className="h-4 w-4 mr-1" />
                Show {hiddenCount} more citation{hiddenCount !== 1 ? 's' : ''}
              </>
            )}
          </Button>
        )}
      </div>
      
      {/* Source Details (if not compact) */}
      {!compact && source.abstract && (
        <div className="pt-2 border-t border-gray-100">
          <div className="text-sm text-gray-600">
            <span className="font-medium">Abstract: </span>
            {source.abstract}
          </div>
        </div>
      )}
      
      {/* Tags */}
      {source.tags && source.tags.length > 0 && (
        <div className="flex flex-wrap gap-1">
          {source.tags.map(tag => (
            <Badge key={tag} variant="outline" className="text-xs">
              {tag}
            </Badge>
          ))}
        </div>
      )}
    </div>
  );
};
