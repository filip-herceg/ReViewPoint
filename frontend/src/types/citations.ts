// Types for citations system
export interface Citation {
    id: string;
    title: string;
    authors: string[];
    year: number;
    source: string; // journal, book, website, etc.
    doi?: string;
    url?: string;
    pages?: string;
    volume?: string;
    issue?: string;
    publisher?: string;
    citationType: 'journal' | 'book' | 'website' | 'report' | 'conference' | 'other';
    abstract?: string;
    tags?: string[];
    addedDate: string;
    addedBy: string;
}

export interface DocumentCitation {
    id: string;
    documentId: string;
    citationId: string;
    pageNumber?: number;
    context?: string; // surrounding text where citation appears
    citationFormat: 'APA' | 'MLA' | 'Chicago' | 'Harvard' | 'IEEE' | 'Vancouver';
    addedDate: string;
    addedBy: string;
}

export interface CitedByDocument {
    id: string;
    documentId: string;
    documentTitle: string;
    documentAuthors: string[];
    citingPageNumber?: number;
    citingContext?: string;
    documentType: 'research' | 'review' | 'report' | 'thesis' | 'other';
    documentDate: string;
    documentUrl?: string;
    addedDate: string;
}

export interface CitationsData {
    documentId: string;
    citationsUsed: {
        citations: Citation[];
        documentCitations: DocumentCitation[];
        total: number;
        page: number;
        pageSize: number;
    };
    citedBy: {
        documents: CitedByDocument[];
        total: number;
        page: number;
        pageSize: number;
    };
}

export interface CitationsFilters {
    search: string;
    citationType?: Citation['citationType'];
    year?: {
        from?: number;
        to?: number;
    };
    tags?: string[];
    sortBy: 'date' | 'title' | 'year' | 'relevance';
    sortOrder: 'asc' | 'desc';
}

export interface CitationsHookOptions {
    documentId: string;
    filters?: CitationsFilters;
    pageSize?: number;
    enabled?: boolean;
}

export interface CitationsHookReturn {
    data: CitationsData | null;
    isLoading: boolean;
    error: string | null;
    refetch: () => void;
    loadMoreCitationsUsed: () => void;
    loadMoreCitedBy: () => void;
    hasMoreCitationsUsed: boolean;
    hasMoreCitedBy: boolean;
    updateFilters: (filters: Partial<CitationsFilters>) => void;
}
