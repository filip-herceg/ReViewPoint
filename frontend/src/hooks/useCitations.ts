import { useState, useEffect } from "react";
import type { CitationsData, Citation } from "@/types/citations";

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
  const uniqueSources = Math.floor(Math.random() * 21) + 15; // 15-35 sources

  const citations: Citation[] = [];
  let totalCitationInstances = 0;

  // Create each unique source and determine how many times it's cited
  for (let i = 0; i < uniqueSources; i++) {
    const template =
      citationTemplates[Math.floor(Math.random() * citationTemplates.length)];

    // Realistic citation frequency: most sources cited 1-2 times, some 3-5 times, rarely more
    let timesUsed;
    const rand = Math.random();
    if (rand < 0.5)
      timesUsed = 1; // 50% cited once
    else if (rand < 0.8)
      timesUsed = 2; // 30% cited twice
    else if (rand < 0.95)
      timesUsed = 3; // 15% cited 3 times
    else timesUsed = Math.floor(Math.random() * 3) + 4; // 5% cited 4-6 times

    totalCitationInstances += timesUsed;

    citations.push({
      id: `citation-${i + 1}`,
      title: template.title,
      authors: template.authors,
      year: 2018 + Math.floor(Math.random() * 7), // 2018-2024
      journal: template.journal,
      source: template.journal,
      doi: `10.1000/${Math.random().toString(36).substr(2, 9)}`,
      page: Math.floor(Math.random() * 50) + 1,
      pages: `${Math.floor(Math.random() * 20) + 1}-${Math.floor(Math.random() * 20) + 25}`,
      volume: `${Math.floor(Math.random() * 50) + 1}`,
      issue: `${Math.floor(Math.random() * 12) + 1}`,
      paragraph: Math.floor(Math.random() * 10) + 1,
      line: Math.floor(Math.random() * 20) + 1,
      citationStyle: ["APA", "MLA", "IEEE", "Chicago"][
        Math.floor(Math.random() * 4)
      ] as any,
      severity: ["info", "warning", "error"][
        Math.floor(Math.random() * 3)
      ] as any,
      type: template.type,
      citationType: template.type, // For backward compatibility
      citationInstances: timesUsed, // Store how many times this source is cited
      abstract: `This ${template.type} presents comprehensive research on ${template.title.toLowerCase()}...`,
      tags: [paperType, template.type, "research"],
    });
  }

  // Debug logging to verify our realistic numbers
  console.log(`📊 Citation Analysis for ${paperType} paper:
    • Unique Sources: ${uniqueSources}
    • Total Citation Instances: ${totalCitationInstances}
    • Ratio: ${(totalCitationInstances / uniqueSources).toFixed(2)} citations per source
    • Citation Distribution:
      ${citations.map((c: Citation) => `- "${c.title}" cited ${c.citationInstances} times`).join("\n      ")}`);

  return {
    citationsUsed: {
      items: citations,
      citations: citations, // For backward compatibility
      documentCitations: citations.map((c) => ({
        id: c.id,
        citationId: c.id,
        documentId,
      })), // For backward compatibility
      total: totalCitationInstances, // This is the ACTUAL number of citation instances in the paper
    },
    citedBy: {
      items: generateCitedBy(),
      documents: [], // For backward compatibility
      total: Math.floor(Math.random() * 30) + 15,
    },
  };
};

const detectPaperType = (
  documentId: string,
): "architecture" | "medical" | "business" => {
  const id = documentId.toLowerCase();
  if (
    id.includes("architecture") ||
    id.includes("design") ||
    id.includes("building")
  )
    return "architecture";
  if (
    id.includes("medical") ||
    id.includes("health") ||
    id.includes("clinical")
  )
    return "medical";
  return "business";
};

const getCitationTemplates = (
  paperType: "architecture" | "medical" | "business",
) => {
  const templates = {
    architecture: [
      {
        title: "Sustainable Building Design: A Global Perspective",
        authors: ["Johnson, M.K.", "Chen, L.Y."],
        journal: "Architectural Science Review",
        type: "journal" as const,
      },
      {
        title: "Urban Planning in the 21st Century",
        authors: ["Williams, R.A."],
        journal: "Urban Design International",
        type: "book" as const,
      },
      {
        title: "Green Architecture: Environmental Impact Assessment",
        authors: ["Davis, S.L.", "Miller, K.J."],
        journal: "Building and Environment",
        type: "journal" as const,
      },
      {
        title: "Smart Cities Integration Framework",
        authors: ["Kumar, A.", "Patel, N."],
        journal: "Smart Cities Journal",
        type: "journal" as const,
      },
      {
        title: "Climate-Responsive Design Principles",
        authors: ["Hassan, A.", "Okoye, C."],
        journal: "Sustainable Architecture",
        type: "journal" as const,
      },
      {
        title: "Biomimetic Architecture: Learning from Nature",
        authors: ["Thompson, D.W.", "Garcia, M.R."],
        journal: "Architectural Design",
        type: "journal" as const,
      },
      {
        title: "Parametric Design in Contemporary Architecture",
        authors: ["Rodriguez, C.", "Nakamura, H."],
        journal: "International Journal of Architectural Computing",
        type: "journal" as const,
      },
      {
        title: "Material Innovation in Construction",
        authors: ["Zhang, W.", "Andersson, L."],
        journal: "Construction and Building Materials",
        type: "journal" as const,
      },
    ],
    medical: [
      {
        title: "Clinical Trial Methodology: A Comprehensive Guide",
        authors: ["Smith, J.L.", "Brown, A.M."],
        journal: "The Lancet",
        type: "journal" as const,
      },
      {
        title: "Evidence-Based Medicine: Principles and Practice",
        authors: ["Wilson, T.R."],
        journal: "BMJ Evidence-Based Medicine",
        type: "book" as const,
      },
      {
        title: "AI in Diagnostic Imaging: Current Applications",
        authors: ["Garcia, M.P.", "Lee, H.K."],
        journal: "Nature Medicine",
        type: "journal" as const,
      },
      {
        title: "Patient Safety in Healthcare Systems",
        authors: ["Taylor, K.S.", "O'Brien, P."],
        journal: "Patient Safety",
        type: "journal" as const,
      },
      {
        title: "Personalized Medicine and Genomics",
        authors: ["Kumar, R.", "Singh, A."],
        journal: "Nature Genetics",
        type: "journal" as const,
      },
      {
        title: "Mental Health Treatment Outcomes",
        authors: ["Foster, L.J.", "Chen, X."],
        journal: "The Lancet Psychiatry",
        type: "journal" as const,
      },
      {
        title: "Surgical Innovation and Robotics",
        authors: ["Martinez, C.R.", "Tanaka, Y."],
        journal: "Surgical Endoscopy",
        type: "journal" as const,
      },
      {
        title: "Global Health Policy Analysis",
        authors: ["Ahmed, F.", "Clark, R."],
        journal: "Health Policy",
        type: "journal" as const,
      },
    ],
    business: [
      {
        title: "Strategic Management in Digital Transformation",
        authors: ["Anderson, P.K.", "Taylor, R.L."],
        journal: "Harvard Business Review",
        type: "journal" as const,
      },
      {
        title: "Market Analysis and Consumer Behavior",
        authors: ["Thompson, L.M."],
        journal: "Journal of Consumer Research",
        type: "book" as const,
      },
      {
        title: "Corporate Finance and Risk Management",
        authors: ["Roberts, K.J.", "White, J.S."],
        journal: "Journal of Finance",
        type: "journal" as const,
      },
      {
        title: "Digital Transformation Strategies",
        authors: ["Liu, Z.", "Murphy, E."],
        journal: "MIT Sloan Management Review",
        type: "journal" as const,
      },
      {
        title: "Supply Chain Optimization",
        authors: ["Davis, A.", "Patel, V."],
        journal: "Operations Research",
        type: "journal" as const,
      },
      {
        title: "Innovation Management in Technology Firms",
        authors: ["Chen, L.", "Rodriguez, S."],
        journal: "Research Policy",
        type: "journal" as const,
      },
      {
        title: "Sustainable Business Practices",
        authors: ["Green, M.K.", "Hoffman, B."],
        journal: "Business Strategy and Environment",
        type: "journal" as const,
      },
      {
        title: "International Trade Economics",
        authors: ["Wilson, J.P."],
        journal: "International Economics",
        type: "journal" as const,
      },
    ],
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
    citationStyle: "APA" as const,
    severity: "info" as const,
    type: "journal" as const,
  }));
};

export const useCitations = ({
  documentId,
}: UseCitationsProps): UseCitationsReturn => {
  const [data, setData] = useState<CitationsData | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchCitations = async () => {
    try {
      setIsLoading(true);
      setError(null);

      // Simulate API delay
      await new Promise((resolve) => setTimeout(resolve, 500));

      const citationsData = generateRealisticCitations(documentId);
      setData(citationsData);
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Failed to fetch citations",
      );
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
    },
  };
};
