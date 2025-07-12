export interface Citation {
  id: string;
  title: string;
  authors: string[];
  year: number;
  journal?: string;
  source?: string; // Add source property
  doi?: string;
  url?: string;
  page?: number;
  pages?: string; // Add pages property
  volume?: string; // Add volume property
  issue?: string; // Add issue property
  paragraph?: number;
  line?: number;
  citationStyle: "APA" | "MLA" | "IEEE" | "Chicago";
  severity: "info" | "warning" | "error";
  type: "book" | "journal" | "website" | "conference" | "thesis" | "other";
  citationType?:
    | "book"
    | "journal"
    | "website"
    | "conference"
    | "thesis"
    | "other"; // Add citationType for backward compatibility
  citationInstances?: number; // How many times this source is cited
  abstract?: string; // Add abstract property
  tags?: string[]; // Add tags property
}

// Keep these for backward compatibility
export interface DocumentCitation {
  id: string;
  citationId: string;
  documentId: string;
}

export interface CitedByDocument {
  id: string;
  documentTitle: string;
  documentAuthors: string[];
}

export interface CitationsFilters {
  search: string;
  sortBy: "date" | "title" | "year" | "relevance";
  sortOrder: "asc" | "desc";
}

export interface CitationsData {
  citationsUsed: {
    items: Citation[];
    citations?: Citation[]; // For backward compatibility
    documentCitations?: DocumentCitation[]; // For backward compatibility
    total: number;
  };
  citedBy: {
    items: Citation[];
    documents?: CitedByDocument[]; // For backward compatibility
    total: number;
  };
}
