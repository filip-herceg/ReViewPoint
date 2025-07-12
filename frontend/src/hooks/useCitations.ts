import { useState, useEffect, useCallback, useMemo } from 'react';
import type { 
    CitationsData, 
    CitationsFilters, 
    CitationsHookOptions, 
    CitationsHookReturn,
    Citation,
    DocumentCitation,
    CitedByDocument
} from '@/types/citations';

// Mock data generator for development
const generateMockCitations = (count: number): Citation[] => {
    const mockCitations: Citation[] = [];
    const citationTypes: Citation['citationType'][] = ['journal', 'book', 'website', 'report', 'conference', 'other'];
    const sources = [
        'Nature', 'Science', 'Cell', 'The Lancet', 'NEJM', 'PNAS',
        'Academic Press', 'Cambridge University Press', 'Springer',
        'arXiv.org', 'ResearchGate', 'Google Scholar', 'PubMed'
    ];
    const authors = [
        'Smith, J.', 'Johnson, M.', 'Williams, R.', 'Brown, K.', 'Davis, L.',
        'Miller, S.', 'Wilson, D.', 'Moore, T.', 'Taylor, A.', 'Anderson, C.'
    ];

    for (let i = 0; i < count; i++) {
        mockCitations.push({
            id: `citation-${i + 1}`,
            title: `Research Paper Title ${i + 1}: Advanced Studies in Applied Science`,
            authors: [
                authors[Math.floor(Math.random() * authors.length)],
                authors[Math.floor(Math.random() * authors.length)]
            ],
            year: 2015 + Math.floor(Math.random() * 9),
            source: sources[Math.floor(Math.random() * sources.length)],
            doi: Math.random() > 0.3 ? `10.1000/journal.${1000 + i}` : undefined,
            url: Math.random() > 0.5 ? `https://example.com/paper/${i + 1}` : undefined,
            pages: Math.random() > 0.4 ? `${Math.floor(Math.random() * 50) + 1}-${Math.floor(Math.random() * 50) + 51}` : undefined,
            volume: Math.random() > 0.3 ? `${Math.floor(Math.random() * 20) + 1}` : undefined,
            citationType: citationTypes[Math.floor(Math.random() * citationTypes.length)],
            abstract: Math.random() > 0.6 ? `This is a mock abstract for citation ${i + 1}. It describes the research methodology and findings in detail.` : undefined,
            tags: Math.random() > 0.5 ? [`tag${i % 5 + 1}`, `category${i % 3 + 1}`] : undefined,
            addedDate: new Date(Date.now() - Math.random() * 365 * 24 * 60 * 60 * 1000).toISOString(),
            addedBy: 'Current User'
        });
    }

    return mockCitations;
};

const generateMockDocumentCitations = (citationIds: string[]): DocumentCitation[] => {
    return citationIds.map((citationId, index) => ({
        id: `doc-citation-${index + 1}`,
        documentId: 'current-document',
        citationId,
        pageNumber: Math.random() > 0.3 ? Math.floor(Math.random() * 100) + 1 : undefined,
        context: Math.random() > 0.4 ? `This is the context where citation ${index + 1} appears in the document.` : undefined,
        citationFormat: ['APA', 'MLA', 'Chicago', 'Harvard', 'IEEE', 'Vancouver'][Math.floor(Math.random() * 6)] as any,
        addedDate: new Date(Date.now() - Math.random() * 30 * 24 * 60 * 60 * 1000).toISOString(),
        addedBy: 'Current User'
    }));
};

const generateMockCitedByDocuments = (count: number): CitedByDocument[] => {
    const mockDocuments: CitedByDocument[] = [];
    const documentTypes: CitedByDocument['documentType'][] = ['research', 'review', 'report', 'thesis', 'other'];

    for (let i = 0; i < count; i++) {
        mockDocuments.push({
            id: `citing-doc-${i + 1}`,
            documentId: `document-${i + 1}`,
            documentTitle: `Citing Document ${i + 1}: Analysis and Applications`,
            documentAuthors: [`Author ${i + 1}`, `Co-Author ${i + 1}`],
            citingPageNumber: Math.random() > 0.3 ? Math.floor(Math.random() * 200) + 1 : undefined,
            citingContext: Math.random() > 0.4 ? `Context where this document cites the current document ${i + 1}.` : undefined,
            documentType: documentTypes[Math.floor(Math.random() * documentTypes.length)],
            documentDate: new Date(Date.now() - Math.random() * 1095 * 24 * 60 * 60 * 1000).toISOString(),
            documentUrl: Math.random() > 0.5 ? `https://example.com/citing-doc/${i + 1}` : undefined,
            addedDate: new Date(Date.now() - Math.random() * 60 * 24 * 60 * 60 * 1000).toISOString()
        });
    }

    return mockDocuments;
};

const defaultFilters: CitationsFilters = {
    search: '',
    sortBy: 'date',
    sortOrder: 'desc'
};

export const useCitations = (options: CitationsHookOptions): CitationsHookReturn => {
    const { documentId, filters = defaultFilters, pageSize = 20, enabled = true } = options;
    
    const [data, setData] = useState<CitationsData | null>(null);
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [currentFilters, setCurrentFilters] = useState<CitationsFilters>({ ...defaultFilters, ...filters });

    // Mock API call simulation
    const fetchCitations = useCallback(async (
        docId: string, 
        appliedFilters: CitationsFilters,
        citationsPage: number = 1,
        citedByPage: number = 1
    ): Promise<CitationsData> => {
        // Simulate API delay
        await new Promise(resolve => setTimeout(resolve, 500 + Math.random() * 1000));

        // Generate mock data based on documentId
        const citationsCount = Math.floor(Math.random() * 150) + 50; // 50-200 citations
        const citedByCount = Math.floor(Math.random() * 80) + 20; // 20-100 citing documents

        const allCitations = generateMockCitations(citationsCount);
        const allCitedBy = generateMockCitedByDocuments(citedByCount);

        // Apply search filter
        const filteredCitations = appliedFilters.search
            ? allCitations.filter(citation =>
                citation.title.toLowerCase().includes(appliedFilters.search.toLowerCase()) ||
                citation.authors.some(author => author.toLowerCase().includes(appliedFilters.search.toLowerCase())) ||
                citation.source.toLowerCase().includes(appliedFilters.search.toLowerCase())
            )
            : allCitations;

        const filteredCitedBy = appliedFilters.search
            ? allCitedBy.filter(doc =>
                doc.documentTitle.toLowerCase().includes(appliedFilters.search.toLowerCase()) ||
                doc.documentAuthors.some(author => author.toLowerCase().includes(appliedFilters.search.toLowerCase()))
            )
            : allCitedBy;

        // Apply type filter
        const typeFilteredCitations = appliedFilters.citationType
            ? filteredCitations.filter(citation => citation.citationType === appliedFilters.citationType)
            : filteredCitations;

        // Apply year filter
        const yearFilteredCitations = appliedFilters.year
            ? typeFilteredCitations.filter(citation => {
                if (appliedFilters.year!.from && citation.year < appliedFilters.year!.from) return false;
                if (appliedFilters.year!.to && citation.year > appliedFilters.year!.to) return false;
                return true;
            })
            : typeFilteredCitations;

        // Sort citations
        const sortedCitations = [...yearFilteredCitations].sort((a, b) => {
            const order = appliedFilters.sortOrder === 'asc' ? 1 : -1;
            switch (appliedFilters.sortBy) {
                case 'title':
                    return order * a.title.localeCompare(b.title);
                case 'year':
                    return order * (a.year - b.year);
                case 'date':
                    return order * (new Date(a.addedDate).getTime() - new Date(b.addedDate).getTime());
                default:
                    return order * (new Date(a.addedDate).getTime() - new Date(b.addedDate).getTime());
            }
        });

        // Sort cited by documents
        const sortedCitedBy = [...filteredCitedBy].sort((a, b) => {
            const order = appliedFilters.sortOrder === 'asc' ? 1 : -1;
            switch (appliedFilters.sortBy) {
                case 'title':
                    return order * a.documentTitle.localeCompare(b.documentTitle);
                case 'date':
                    return order * (new Date(a.documentDate).getTime() - new Date(b.documentDate).getTime());
                default:
                    return order * (new Date(a.addedDate).getTime() - new Date(b.addedDate).getTime());
            }
        });

        // Paginate results
        const citationsStart = (citationsPage - 1) * pageSize;
        const citationsEnd = citationsStart + pageSize;
        const paginatedCitations = sortedCitations.slice(citationsStart, citationsEnd);

        const citedByStart = (citedByPage - 1) * pageSize;
        const citedByEnd = citedByStart + pageSize;
        const paginatedCitedBy = sortedCitedBy.slice(citedByStart, citedByEnd);

        return {
            documentId: docId,
            citationsUsed: {
                citations: paginatedCitations,
                documentCitations: generateMockDocumentCitations(paginatedCitations.map(c => c.id)),
                total: sortedCitations.length,
                page: citationsPage,
                pageSize
            },
            citedBy: {
                documents: paginatedCitedBy,
                total: sortedCitedBy.length,
                page: citedByPage,
                pageSize
            }
        };
    }, [pageSize]);

    const loadData = useCallback(async () => {
        if (!enabled || !documentId) return;
        
        setIsLoading(true);
        setError(null);
        
        try {
            const result = await fetchCitations(documentId, currentFilters);
            setData(result);
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Failed to load citations');
        } finally {
            setIsLoading(false);
        }
    }, [documentId, currentFilters, enabled, fetchCitations]);

    const loadMoreCitationsUsed = useCallback(async () => {
        if (!data || !enabled) return;
        
        const nextPage = data.citationsUsed.page + 1;
        try {
            const result = await fetchCitations(documentId, currentFilters, nextPage, data.citedBy.page);
            setData(prev => prev ? {
                ...prev,
                citationsUsed: {
                    ...result.citationsUsed,
                    citations: [...prev.citationsUsed.citations, ...result.citationsUsed.citations],
                    documentCitations: [...prev.citationsUsed.documentCitations, ...result.citationsUsed.documentCitations],
                    page: nextPage
                }
            } : result);
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Failed to load more citations');
        }
    }, [data, documentId, currentFilters, enabled, fetchCitations]);

    const loadMoreCitedBy = useCallback(async () => {
        if (!data || !enabled) return;
        
        const nextPage = data.citedBy.page + 1;
        try {
            const result = await fetchCitations(documentId, currentFilters, data.citationsUsed.page, nextPage);
            setData(prev => prev ? {
                ...prev,
                citedBy: {
                    ...result.citedBy,
                    documents: [...prev.citedBy.documents, ...result.citedBy.documents],
                    page: nextPage
                }
            } : result);
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Failed to load more cited by documents');
        }
    }, [data, documentId, currentFilters, enabled, fetchCitations]);

    const updateFilters = useCallback((newFilters: Partial<CitationsFilters>) => {
        setCurrentFilters(prev => ({ ...prev, ...newFilters }));
    }, []);

    const refetch = useCallback(() => {
        loadData();
    }, [loadData]);

    const hasMoreCitationsUsed = useMemo(() => {
        if (!data) return false;
        return data.citationsUsed.citations.length < data.citationsUsed.total;
    }, [data]);

    const hasMoreCitedBy = useMemo(() => {
        if (!data) return false;
        return data.citedBy.documents.length < data.citedBy.total;
    }, [data]);

    useEffect(() => {
        loadData();
    }, [loadData]);

    return {
        data,
        isLoading,
        error,
        refetch,
        loadMoreCitationsUsed,
        loadMoreCitedBy,
        hasMoreCitationsUsed,
        hasMoreCitedBy,
        updateFilters
    };
};
