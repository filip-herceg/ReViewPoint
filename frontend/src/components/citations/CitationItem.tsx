import React from "react";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  ExternalLink,
  Copy,
  Calendar,
  Users,
  BookOpen,
  FileText,
  Globe,
  Presentation,
  Archive,
  Hash,
} from "lucide-react";
import type { Citation, DocumentCitation } from "@/types/citations";

interface CitationItemProps {
  citation: Citation;
  documentCitation?: DocumentCitation;
  showContext?: boolean;
  compact?: boolean;
}

const getCitationTypeIcon = (type: Citation["citationType"]) => {
  switch (type) {
    case "journal":
      return <FileText className="h-4 w-4" />;
    case "book":
      return <BookOpen className="h-4 w-4" />;
    case "website":
      return <Globe className="h-4 w-4" />;
    case "conference":
      return <Presentation className="h-4 w-4" />;
    case "report":
      return <Archive className="h-4 w-4" />;
    default:
      return <FileText className="h-4 w-4" />;
  }
};

const getCitationTypeColor = (type: Citation["citationType"]) => {
  switch (type) {
    case "journal":
      return "bg-primary/10 text-primary";
    case "book":
      return "bg-green-100 text-green-800 dark:bg-green-900/20 dark:text-green-400";
    case "website":
      return "bg-blue-100 text-blue-800 dark:bg-blue-900/20 dark:text-blue-400";
    case "conference":
      return "bg-violet-100 text-violet-800 dark:bg-violet-900/20 dark:text-violet-400";
    case "report":
      return "bg-amber-100 text-amber-800 dark:bg-amber-900/20 dark:text-amber-400";
    default:
      return "bg-muted text-muted-foreground";
  }
};

const formatCitation = (citation: Citation, format: string = "APA"): string => {
  const authorsText =
    citation.authors.length > 0
      ? citation.authors.join(", ")
      : "Unknown Author";
  const year = citation.year ? ` (${citation.year})` : "";
  const title = citation.title ? `"${citation.title}"` : "";
  const source = citation.source ? `, ${citation.source}` : "";
  const volume = citation.volume ? `, ${citation.volume}` : "";
  const pages = citation.pages ? `, pp. ${citation.pages}` : "";

  return `${authorsText}${year}. ${title}${source}${volume}${pages}.`;
};

export const CitationItem: React.FC<CitationItemProps> = ({
  citation,
  documentCitation,
  showContext = false,
  compact = false,
}) => {
  const handleCopyFormatted = () => {
    const formatted = formatCitation(
      citation,
      documentCitation?.citationFormat,
    );
    navigator.clipboard.writeText(formatted);
  };

  const handleCopyBibTeX = () => {
    const bibtex = `@article{${citation.id},
  title={${citation.title}},
  author={${citation.authors.join(" and ")}},
  year={${citation.year}},
  journal={${citation.source}},
  ${citation.volume ? `volume={${citation.volume}},` : ""}
  ${citation.pages ? `pages={${citation.pages}},` : ""}
  ${citation.doi ? `doi={${citation.doi}}` : ""}
}`;
    navigator.clipboard.writeText(bibtex);
  };

  if (compact) {
    return (
      <div className="flex items-start justify-between p-3 border rounded-lg hover:bg-muted/50 transition-colors">
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-1">
            <Badge className={getCitationTypeColor(citation.citationType)}>
              {getCitationTypeIcon(citation.citationType)}
              <span className="ml-1 capitalize">{citation.citationType}</span>
            </Badge>
            <span className="text-sm text-muted-foreground">
              {citation.year}
            </span>
          </div>
          <h4 className="font-medium text-sm leading-tight mb-1 truncate">
            {citation.title}
          </h4>
          <p className="text-xs text-muted-foreground truncate">
            {citation.authors.join(", ")} • {citation.source}
          </p>
          {documentCitation?.pageNumber && (
            <p className="text-xs text-muted-foreground mt-1">
              Page {documentCitation.pageNumber}
            </p>
          )}
        </div>
        <div className="flex items-center gap-1 ml-2">
          {citation.url && (
            <Button
              variant="ghost"
              size="sm"
              className="h-6 w-6 p-0"
              onClick={() => window.open(citation.url, "_blank")}
            >
              <ExternalLink className="h-3 w-3" />
            </Button>
          )}
          <Button
            variant="ghost"
            size="sm"
            className="h-6 w-6 p-0"
            onClick={handleCopyFormatted}
            title="Copy formatted citation"
          >
            <Copy className="h-3 w-3" />
          </Button>
        </div>
      </div>
    );
  }

  return (
    <Card className="hover:shadow-md transition-shadow">
      <CardHeader className="pb-3">
        <div className="flex items-start justify-between">
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2 mb-2">
              <Badge className={getCitationTypeColor(citation.citationType)}>
                {getCitationTypeIcon(citation.citationType)}
                <span className="ml-1 capitalize">{citation.citationType}</span>
              </Badge>
              <Badge variant="outline" className="text-xs">
                <Calendar className="h-3 w-3 mr-1" />
                {citation.year}
              </Badge>
              {documentCitation?.citationFormat && (
                <Badge variant="secondary" className="text-xs">
                  {documentCitation.citationFormat}
                </Badge>
              )}
            </div>
            <CardTitle className="text-lg leading-tight mb-2">
              {citation.title}
            </CardTitle>
            <div className="flex items-center gap-4 text-sm text-muted-foreground">
              <div className="flex items-center gap-1">
                <Users className="h-4 w-4" />
                <span>{citation.authors.join(", ")}</span>
              </div>
              <div className="flex items-center gap-1">
                <BookOpen className="h-4 w-4" />
                <span>{citation.source}</span>
              </div>
            </div>
          </div>
          <div className="flex items-center gap-2 ml-4">
            {citation.url && (
              <Button
                variant="outline"
                size="sm"
                onClick={() => window.open(citation.url, "_blank")}
              >
                <ExternalLink className="h-4 w-4 mr-2" />
                View
              </Button>
            )}
            <Button variant="outline" size="sm" onClick={handleCopyFormatted}>
              <Copy className="h-4 w-4 mr-2" />
              Copy
            </Button>
          </div>
        </div>
      </CardHeader>

      <CardContent className="pt-0">
        {/* Citation Details */}
        <div className="space-y-3">
          {(citation.volume || citation.issue || citation.pages) && (
            <div className="flex flex-wrap gap-4 text-sm text-muted-foreground">
              {citation.volume && <span>Volume {citation.volume}</span>}
              {citation.issue && <span>Issue {citation.issue}</span>}
              {citation.pages && <span>Pages {citation.pages}</span>}
            </div>
          )}

          {citation.doi && (
            <div className="flex items-center gap-2 text-sm">
              <Hash className="h-4 w-4 text-muted-foreground" />
              <span className="font-mono text-xs bg-muted px-2 py-1 rounded">
                DOI: {citation.doi}
              </span>
            </div>
          )}

          {citation.abstract && (
            <div>
              <h5 className="font-medium text-sm mb-1">Abstract</h5>
              <p className="text-sm text-muted-foreground leading-relaxed">
                {citation.abstract}
              </p>
            </div>
          )}

          {documentCitation && showContext && (
            <div className="border-t pt-3">
              <h5 className="font-medium text-sm mb-2">Citation Context</h5>
              {documentCitation.pageNumber && (
                <p className="text-xs text-muted-foreground mb-1">
                  Page {documentCitation.pageNumber}
                </p>
              )}
              {documentCitation.context && (
                <p className="text-sm bg-muted/50 p-3 rounded-md italic">
                  "{documentCitation.context}"
                </p>
              )}
            </div>
          )}

          {citation.tags && citation.tags.length > 0 && (
            <div className="flex flex-wrap gap-1">
              {citation.tags.map((tag) => (
                <Badge key={tag} variant="secondary" className="text-xs">
                  {tag}
                </Badge>
              ))}
            </div>
          )}

          {/* Action Buttons */}
          <div className="flex gap-2 pt-2">
            <Button
              variant="ghost"
              size="sm"
              onClick={handleCopyBibTeX}
              className="text-xs"
            >
              Copy BibTeX
            </Button>
            {citation.doi && (
              <Button
                variant="ghost"
                size="sm"
                onClick={() =>
                  window.open(`https://doi.org/${citation.doi}`, "_blank")
                }
                className="text-xs"
              >
                View DOI
              </Button>
            )}
          </div>
        </div>
      </CardContent>
    </Card>
  );
};
