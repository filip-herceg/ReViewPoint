import { useState, useEffect } from 'react';
import type { CitationsData, Source, CitationInstance, Citation } from '@/types/citations';

interface UseCitationsProps {
  documentId: string;
  filters?: any; // For backward compatibility
}

interface UseCitationsReturn {
  data: CitationsData | null;
  isLoading: boolean;
  error: string | null;
  refetch: () => void;
  loadMoreCitationsUsed: () => void;
  hasMoreCitationsUsed: boolean;
  loadMoreCitedBy?: () => void; // For backward compatibility
  hasMoreCitedBy?: boolean; // For backward compatibility
  updateFilters?: (filters: any) => void; // For backward compatibility
}

// Generate realistic citation data based on paper type
const generateRealisticCitations = (documentId: string): CitationsData => {
  // Simple paper type detection from documentId
  const paperType = detectPaperType(documentId);
  const citationTemplates = getCitationTemplates(paperType);
  
  // Generate realistic numbers: academic papers typically have 15-35 unique sources
  const uniqueSourceCount = Math.floor(Math.random() * 21) + 15; // 15-35 sources
  
  const sources: Source[] = [];
  let totalCitationInstances = 0;
  
  // Create each unique source and determine how many times it's cited
  for (let i = 0; i < uniqueSourceCount; i++) {
    const template = citationTemplates[Math.floor(Math.random() * citationTemplates.length)];
    
    // Realistic citation frequency distribution
    let citationCount;
    const rand = Math.random();
    if (rand < 0.5) citationCount = 1;        // 50% cited once
    else if (rand < 0.8) citationCount = 2;   // 30% cited twice  
    else if (rand < 0.95) citationCount = 3;  // 15% cited 3 times
    else citationCount = Math.floor(Math.random() * 3) + 4; // 5% cited 4-6 times
    
    // Generate citation instances for this source
    const citationInstances: CitationInstance[] = [];
    for (let j = 0; j < citationCount; j++) {
      citationInstances.push({
        id: `citation-${i + 1}-${j + 1}`,
        sourceId: `source-${i + 1}`,
        page: Math.floor(Math.random() * 50) + 1,
        paragraph: Math.floor(Math.random() * 8) + 1,
        line: Math.floor(Math.random() * 15) + 1,
        context: generateCitationContext(template.title, j),
        severity: ['info', 'warning', 'error'][Math.floor(Math.random() * 3)] as any,
        citationStyle: ['APA', 'MLA', 'IEEE', 'Chicago'][Math.floor(Math.random() * 4)] as any
      });
    }
    
    totalCitationInstances += citationCount;
    
    const source: Source = {
      id: `source-${i + 1}`,
      title: template.title,
      authors: template.authors,
      year: 2018 + Math.floor(Math.random() * 7), // 2018-2024
      journal: template.journal,
      source: template.journal,
      doi: `10.1000/${Math.random().toString(36).substr(2, 9)}`,
      pages: `${Math.floor(Math.random() * 20) + 1}-${Math.floor(Math.random() * 20) + 25}`,
      volume: `${Math.floor(Math.random() * 50) + 1}`,
      issue: `${Math.floor(Math.random() * 12) + 1}`,
      type: template.type,
      abstract: `This ${template.type} presents comprehensive research on ${template.title.toLowerCase()}...`,
      tags: [paperType, template.type, 'research'],
      citationInstances
    };
    
    sources.push(source);
  }

  // Debug logging to verify our realistic numbers
  console.log(`📊 Citation Analysis for ${paperType} paper:
    • Unique Sources: ${uniqueSourceCount}
    • Total Citation Instances: ${totalCitationInstances}
    • Ratio: ${(totalCitationInstances / uniqueSourceCount).toFixed(2)} citations per source
    • Citation Distribution:
      ${sources.map((s: Source) => `- "${s.title}" cited ${s.citationInstances.length} times`).join('\n      ')}`);

  // Create backward compatibility items
  const backwardCompatibilityCitations: Citation[] = sources.map(source => ({
    id: source.id,
    title: source.title,
    authors: source.authors,
    year: source.year,
    journal: source.journal,
    source: source.source,
    doi: source.doi,
    pages: source.pages,
    volume: source.volume,
    issue: source.issue,
    citationStyle: source.citationInstances[0]?.citationStyle || 'APA',
    severity: source.citationInstances[0]?.severity || 'info',
    type: source.type,
    citationType: source.type,
    citationInstances: source.citationInstances.length,
    abstract: source.abstract,
    tags: source.tags,
    page: source.citationInstances[0]?.page,
    paragraph: source.citationInstances[0]?.paragraph,
    line: source.citationInstances[0]?.line
  }));

  return {
    sourcesUsed: {
      sources,
      totalSources: uniqueSourceCount,
      totalCitations: totalCitationInstances,
      // Backward compatibility
      items: backwardCompatibilityCitations,
      citations: backwardCompatibilityCitations,
      documentCitations: backwardCompatibilityCitations.map(c => ({ id: c.id, citationId: c.id, documentId })),
      total: totalCitationInstances
    },
    citedBy: (() => {
      const citedByItems = generateCitedBy();
      return {
        items: citedByItems,
        documents: [],
        total: citedByItems.length
      };
    })()
  };
};

// Generate contextual citation text
const generateCitationContext = (title: string, instanceIndex: number): string => {
  const contexts = [
    `As demonstrated in ${title.split(':')[0]}`,
    `According to the findings in ${title.split(':')[0]}`,
    `This approach is supported by ${title.split(':')[0]}`,
    `Research from ${title.split(':')[0]} indicates`,
    `The methodology described in ${title.split(':')[0]}`
  ];
  return contexts[instanceIndex % contexts.length] || contexts[0];
};

const detectPaperType = (documentId: string): 'architecture' | 'medical' | 'business' => {
  const id = documentId.toLowerCase();
  if (id.includes('architecture') || id.includes('design') || id.includes('building')) return 'architecture';
  if (id.includes('medical') || id.includes('health') || id.includes('clinical')) return 'medical';
  return 'business';
};

const getCitationTemplates = (paperType: 'architecture' | 'medical' | 'business') => {
  const templates = {
    architecture: [
      { title: "Sustainable Building Design: Environmental Impact and Performance", authors: ["Johnson, M.K.", "Chen, L.Y."], journal: "Architectural Science Review", type: 'journal' as const },
      { title: "Urban Planning in the Digital Age: Smart Cities and IoT Integration", authors: ["Williams, R.A.", "Kumar, S."], journal: "Urban Design International", type: 'journal' as const },
      { title: "Green Architecture: Climate-Responsive Design Strategies", authors: ["Davis, S.L.", "Miller, K.J."], journal: "Building and Environment", type: 'journal' as const },
      { title: "The Pattern Language: Towns, Buildings, Construction (4th Edition)", authors: ["Alexander, C.", "Ishikawa, S.", "Silverstein, M."], journal: "Oxford University Press", type: 'book' as const },
      { title: "Biomimetic Architecture: Learning from Nature's Design Principles", authors: ["Thompson, D.W.", "Garcia, M.R."], journal: "Architectural Design", type: 'journal' as const },
      { title: "Parametric Design in Contemporary Architecture", authors: ["Rodriguez, C.A.", "Nakamura, H."], journal: "International Journal of Architectural Computing", type: 'journal' as const },
      { title: "Historic Preservation and Adaptive Reuse in Modern Cities", authors: ["Bentley, J.P.", "Anderson, K.L."], journal: "Journal of Architectural Conservation", type: 'journal' as const },
      { title: "Material Innovation in Sustainable Construction", authors: ["Zhang, W.H.", "Andersson, L.M."], journal: "Construction and Building Materials", type: 'journal' as const }
    ],
    medical: [
      { title: "Clinical Effectiveness of Telemedicine in Rural Healthcare", authors: ["Smith, J.L.", "Brown, A.M."], journal: "The Lancet Digital Health", type: 'journal' as const },
      { title: "Evidence-Based Medicine: Principles and Practice (6th Edition)", authors: ["Wilson, T.R.", "McCarthy, D.J."], journal: "BMJ Publishing", type: 'book' as const },
      { title: "Artificial Intelligence in Diagnostic Imaging: Current Applications", authors: ["Garcia, M.P.", "Lee, H.K."], journal: "Nature Medicine", type: 'journal' as const },
      { title: "Patient Safety in Healthcare Systems: A Systematic Review", authors: ["Taylor, K.S.", "O'Brien, P.M."], journal: "Patient Safety in Surgery", type: 'journal' as const },
      { title: "Personalized Medicine and Genomics in Clinical Practice", authors: ["Kumar, R.S.", "Singh, A.K."], journal: "Nature Genetics", type: 'journal' as const },
      { title: "Mental Health Treatment Outcomes in Post-Pandemic Era", authors: ["Foster, L.J.", "Chen, X.W."], journal: "The Lancet Psychiatry", type: 'journal' as const },
      { title: "Surgical Innovation and Robotics in Minimally Invasive Procedures", authors: ["Martinez, C.R.", "Tanaka, Y."], journal: "Surgical Endoscopy", type: 'journal' as const },
      { title: "Global Health Policy Analysis: Lessons from COVID-19", authors: ["Ahmed, F.H.", "Clark, R.B."], journal: "Health Policy", type: 'journal' as const }
    ],
    business: [
      { title: "Strategic Management in Digital Transformation Era", authors: ["Anderson, P.K.", "Taylor, R.L."], journal: "Harvard Business Review", type: 'journal' as const },
      { title: "Market Analysis and Consumer Behavior in E-Commerce", authors: ["Thompson, L.M.", "Rodriguez, S.A."], journal: "Journal of Consumer Research", type: 'journal' as const },
      { title: "Corporate Finance and Risk Management (8th Edition)", authors: ["Roberts, K.J.", "White, J.S."], journal: "McGraw-Hill Education", type: 'book' as const },
      { title: "Supply Chain Optimization in Global Markets", authors: ["Liu, Z.H.", "Murphy, E.K."], journal: "Supply Chain Management Review", type: 'journal' as const },
      { title: "Leadership in Organizational Change and Innovation", authors: ["Davis, A.R.", "Patel, V.M."], journal: "Organization Science", type: 'journal' as const },
      { title: "Sustainable Business Practices and ESG Implementation", authors: ["Green, M.K.", "Hoffman, B.L."], journal: "Business Strategy and Environment", type: 'journal' as const },
      { title: "Innovation Management in Technology Firms", authors: ["Chen, L.Q.", "Rodriguez, S.P."], journal: "Research Policy", type: 'journal' as const },
      { title: "Digital Marketing and Customer Experience Management", authors: ["Park, H.J.", "Gonzalez, R.M."], journal: "Journal of Marketing", type: 'journal' as const }
    ]
  };
  
  return templates[paperType] || templates.business;
};

const generateCitedBy = (): Citation[] => {
  const count = Math.floor(Math.random() * 10) + 5;
  return Array.from({ length: count }, (_, i) => ({
    id: `cited-by-${i + 1}`,
    title: `Research Paper ${i + 1}`,
    authors: [`Author ${i + 1}`],
    year: 2021 + Math.floor(Math.random() * 3),
    citationStyle: 'APA' as const,
    severity: 'info' as const,
    type: 'journal' as const
  }));
};

export const useCitations = ({ documentId }: UseCitationsProps): UseCitationsReturn => {
  const [data, setData] = useState<CitationsData | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchCitations = async () => {
    try {
      setIsLoading(true);
      setError(null);
      
      // Simulate API delay
      await new Promise(resolve => setTimeout(resolve, 500));
      
      const citationsData = generateRealisticCitations(documentId);
      setData(citationsData);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch citations');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchCitations();
  }, [documentId]);

  return {
    data,
    isLoading,
    error,
    refetch: fetchCitations,
    loadMoreCitationsUsed: () => {
      // Implement pagination if needed
    },
    hasMoreCitationsUsed: false,
    loadMoreCitedBy: () => {
      // For backward compatibility
    },
    hasMoreCitedBy: false,
    updateFilters: () => {
      // For backward compatibility
    }
  };
};
