import React, { useState, useMemo } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../ui/tabs';
import { 
    Search, 
    Filter, 
    SortAsc, 
    SortDesc, 
    LayoutGrid, 
    List,
    RefreshCw,
    Download,
    BookMarked,
    Quote
} from 'lucide-react';
import { CitationItem } from './CitationItem';
import { CitedByItem } from './CitedByItem';
import { SourceWithCitations } from './SourceWithCitations';
import { useCitations } from '@/hooks/useCitations';
import type { CitationsFilters, Citation, Source } from '@/types/citations';

interface CitationsSectionProps {
    documentId: string;
    className?: string;
}

export const CitationsSection: React.FC<CitationsSectionProps> = ({ 
    documentId, 
    className = '' 
}) => {
    const [searchTerm, setSearchTerm] = useState('');
    const [selectedType, setSelectedType] = useState<Citation['citationType'] | 'all'>('all');
    const [sortBy, setSortBy] = useState<'date' | 'title' | 'year'>('date');
    const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('desc');
    const [viewMode, setViewMode] = useState<'card' | 'compact'>('card');
    const [activeTab, setActiveTab] = useState<'used' | 'citedBy'>('used');

    const filters: CitationsFilters = useMemo(() => ({
        search: searchTerm,
        citationType: selectedType === 'all' ? undefined : selectedType,
        sortBy,
        sortOrder
    }), [searchTerm, selectedType, sortBy, sortOrder]);

    const {
        data,
        isLoading,
        error,
        refetch,
        loadMoreCitationsUsed,
        loadMoreCitedBy,
        hasMoreCitationsUsed,
        hasMoreCitedBy,
        updateFilters
    } = useCitations({
        documentId,
        filters
    });

    // Update filters when local state changes
    React.useEffect(() => {
        if (updateFilters) {
            updateFilters(filters);
        }
    }, [filters, updateFilters]);

    const citationTypes: { value: Citation['citationType'] | 'all'; label: string }[] = [
        { value: 'all', label: 'All Types' },
        { value: 'journal', label: 'Journal Articles' },
        { value: 'book', label: 'Books' },
        { value: 'website', label: 'Websites' },
        { value: 'conference', label: 'Conference Papers' },
        { value: 'thesis', label: 'Thesis' },
        { value: 'other', label: 'Other' }
    ];

    const sortOptions = [
        { value: 'date', label: 'Date Added' },
        { value: 'title', label: 'Title' },
        { value: 'year', label: 'Publication Year' }
    ];

    const handleExportCitations = () => {
        if (!data?.sourcesUsed?.sources) return;
        
        const csvContent = [
            ['Title', 'Authors', 'Year', 'Journal', 'DOI', 'Citation Count'].join(','),
            ...data.sourcesUsed.sources.map(source => [
                `"${source.title}"`,
                `"${source.authors.join('; ')}"`,
                source.year,
                `"${source.journal || ''}"`,
                source.doi || '',
                source.citationInstances.length
            ].join(','))
        ].join('\n');

        const blob = new Blob([csvContent], { type: 'text/csv' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `citations-${documentId}.csv`;
        a.click();
        URL.revokeObjectURL(url);
    };

    if (error) {
        return (
            <Card className={className}>
                <CardHeader>
                    <CardTitle className="text-destructive">Error Loading Citations</CardTitle>
                    <CardDescription>{error}</CardDescription>
                </CardHeader>
                <CardContent>
                    <Button onClick={refetch} variant="outline">
                        <RefreshCw className="h-4 w-4 mr-2" />
                        Retry
                    </Button>
                </CardContent>
            </Card>
        );
    }

    return (
        <Card className={className}>
            <CardHeader>
                <div className="flex items-center justify-between">
                    <div>
                        <CardTitle className="flex items-center gap-2">
                            <BookMarked className="h-5 w-5" />
                            Citations & References
                        </CardTitle>
                        <CardDescription>
                            Sources used in this document and documents that cite this work
                        </CardDescription>
                    </div>
                    <div className="flex items-center gap-2">
                        <Button
                            variant="outline"
                            size="sm"
                            onClick={handleExportCitations}
                            disabled={!data?.sourcesUsed?.sources?.length}
                        >
                            <Download className="h-4 w-4 mr-2" />
                            Export
                        </Button>
                        <Button
                            variant="outline"
                            size="sm"
                            onClick={refetch}
                            disabled={isLoading}
                        >
                            <RefreshCw className={`h-4 w-4 mr-2 ${isLoading ? 'animate-spin' : ''}`} />
                            Refresh
                        </Button>
                    </div>
                </div>
            </CardHeader>

            <CardContent>
                {/* Filters and Controls */}
                <div className="space-y-4 mb-6">
                    {/* Search and Type Filter */}
                    <div className="flex flex-col sm:flex-row gap-4">
                        <div className="relative flex-1">
                            <Search className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
                            <Input
                                placeholder="Search citations..."
                                value={searchTerm}
                                onChange={(e) => setSearchTerm(e.target.value)}
                                className="pl-10"
                            />
                        </div>
                        <select
                            value={selectedType}
                            onChange={(e) => setSelectedType(e.target.value as Citation['citationType'] | 'all')}
                            className="px-3 py-2 border rounded-md bg-background min-w-[150px]"
                        >
                            {citationTypes.map(type => (
                                <option key={type.value} value={type.value}>
                                    {type.label}
                                </option>
                            ))}
                        </select>
                    </div>

                    {/* Sort and View Controls */}
                    <div className="flex items-center justify-between">
                        <div className="flex items-center gap-2">
                            <Filter className="h-4 w-4 text-muted-foreground" />
                            <select
                                value={sortBy}
                                onChange={(e) => setSortBy(e.target.value as 'date' | 'title' | 'year')}
                                className="px-3 py-1 border rounded-md bg-background text-sm"
                            >
                                {sortOptions.map(option => (
                                    <option key={option.value} value={option.value}>
                                        {option.label}
                                    </option>
                                ))}
                            </select>
                            <Button
                                variant="outline"
                                size="sm"
                                onClick={() => setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc')}
                            >
                                {sortOrder === 'asc' ? (
                                    <SortAsc className="h-4 w-4" />
                                ) : (
                                    <SortDesc className="h-4 w-4" />
                                )}
                            </Button>
                        </div>

                        <div className="flex items-center gap-2">
                            <Button
                                variant={viewMode === 'card' ? 'default' : 'outline'}
                                size="sm"
                                onClick={() => setViewMode('card')}
                            >
                                <LayoutGrid className="h-4 w-4" />
                            </Button>
                            <Button
                                variant={viewMode === 'compact' ? 'default' : 'outline'}
                                size="sm"
                                onClick={() => setViewMode('compact')}
                            >
                                <List className="h-4 w-4" />
                            </Button>
                        </div>
                    </div>
                </div>

                {/* Tabs for Citations Used vs Cited By */}
                <Tabs value={activeTab} onValueChange={(value: string) => setActiveTab(value as 'used' | 'citedBy')}>
                    <TabsList className="grid w-full grid-cols-2">
                        <TabsTrigger value="used" className="flex items-center gap-2">
                            <Quote className="h-4 w-4" />
                            Sources Used
                            {data && (
                                <div className="ml-2 flex gap-1">
                                    <Badge variant="secondary">
                                        {data.sourcesUsed?.totalSources || 0} sources
                                    </Badge>
                                    <Badge variant="outline">
                                        {data.sourcesUsed?.totalCitations || 0} citations
                                    </Badge>
                                </div>
                            )}
                        </TabsTrigger>
                        <TabsTrigger value="citedBy" className="flex items-center gap-2">
                            <BookMarked className="h-4 w-4" />
                            Cited By
                            {data && (
                                <Badge variant="secondary" className="ml-2">
                                    {data.citedBy.total}
                                </Badge>
                            )}
                        </TabsTrigger>
                    </TabsList>

                    <TabsContent value="used" className="mt-6">
                        {isLoading && !data ? (
                            <div className="space-y-4">
                                {Array.from({ length: 3 }).map((_, i) => (
                                    <div key={i} className="animate-pulse">
                                        <div className="h-32 bg-muted rounded-lg"></div>
                                    </div>
                                ))}
                            </div>
                        ) : data?.sourcesUsed.sources.length ? (
                            <div className="space-y-4">
                                {data.sourcesUsed.sources.map((source) => (
                                    <SourceWithCitations
                                        key={source.id}
                                        source={source}
                                        showContext={true}
                                        compact={viewMode === 'compact'}
                                    />
                                ))}
                                
                                {hasMoreCitationsUsed && (
                                    <div className="flex justify-center pt-4">
                                        <Button
                                            variant="outline"
                                            onClick={loadMoreCitationsUsed}
                                            disabled={isLoading}
                                        >
                                            {isLoading ? 'Loading...' : 'Load More Citations'}
                                        </Button>
                                    </div>
                                )}
                            </div>
                        ) : (
                            <div className="text-center py-8 text-muted-foreground">
                                <Quote className="h-12 w-12 mx-auto mb-4 opacity-50" />
                                <p>No citations found{searchTerm ? ' for your search' : ''}.</p>
                            </div>
                        )}
                    </TabsContent>

                    <TabsContent value="citedBy" className="mt-6">
                        {isLoading && !data ? (
                            <div className="space-y-4">
                                {Array.from({ length: 3 }).map((_, i) => (
                                    <div key={i} className="animate-pulse">
                                        <div className="h-32 bg-muted rounded-lg"></div>
                                    </div>
                                ))}
                            </div>
                        ) : data?.citedBy.items?.length ? (
                            <div className="space-y-4">
                                {data.citedBy.items.map((citation) => (
                                    <CitationItem
                                        key={citation.id}
                                        citation={citation}
                                        showContext={true}
                                        compact={viewMode === 'compact'}
                                    />
                                ))}
                                
                                {hasMoreCitedBy && (
                                    <div className="flex justify-center pt-4">
                                        <Button
                                            variant="outline"
                                            onClick={loadMoreCitedBy}
                                            disabled={isLoading}
                                        >
                                            {isLoading ? 'Loading...' : 'Load More Documents'}
                                        </Button>
                                    </div>
                                )}
                            </div>
                        ) : (
                            <div className="text-center py-8 text-muted-foreground">
                                <BookMarked className="h-12 w-12 mx-auto mb-4 opacity-50" />
                                <p>No citing documents found{searchTerm ? ' for your search' : ''}.</p>
                            </div>
                        )}
                    </TabsContent>
                </Tabs>
            </CardContent>
        </Card>
    );
};
