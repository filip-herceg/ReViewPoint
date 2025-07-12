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
  Calendar,
  Users,
  FileText,
  BookOpen,
  ClipboardList,
  GraduationCap,
  Archive,
} from "lucide-react";
import type { CitedByDocument } from "@/types/citations";

interface CitedByItemProps {
  document: CitedByDocument;
  compact?: boolean;
}

const getDocumentTypeIcon = (type: CitedByDocument["documentType"]) => {
  switch (type) {
    case "research":
      return <FileText className="h-4 w-4" />;
    case "review":
      return <BookOpen className="h-4 w-4" />;
    case "report":
      return <ClipboardList className="h-4 w-4" />;
    case "thesis":
      return <GraduationCap className="h-4 w-4" />;
    default:
      return <Archive className="h-4 w-4" />;
  }
};

const getDocumentTypeColor = (type: CitedByDocument["documentType"]) => {
  switch (type) {
    case "research":
      return "bg-primary/10 text-primary";
    case "review":
      return "bg-green-100 text-green-800 dark:bg-green-900/20 dark:text-green-400";
    case "report":
      return "bg-amber-100 text-amber-800 dark:bg-amber-900/20 dark:text-amber-400";
    case "thesis":
      return "bg-violet-100 text-violet-800 dark:bg-violet-900/20 dark:text-violet-400";
    default:
      return "bg-muted text-muted-foreground";
  }
};

const formatDate = (dateString: string) => {
  return new Date(dateString).toLocaleDateString("en-US", {
    year: "numeric",
    month: "short",
    day: "numeric",
  });
};

export const CitedByItem: React.FC<CitedByItemProps> = ({
  document,
  compact = false,
}) => {
  if (compact) {
    return (
      <div className="flex items-start justify-between p-3 border rounded-lg hover:bg-muted/50 transition-colors">
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-1">
            <Badge className={getDocumentTypeColor(document.documentType)}>
              {getDocumentTypeIcon(document.documentType)}
              <span className="ml-1 capitalize">{document.documentType}</span>
            </Badge>
            <span className="text-sm text-muted-foreground">
              {formatDate(document.documentDate)}
            </span>
          </div>
          <h4 className="font-medium text-sm leading-tight mb-1 truncate">
            {document.documentTitle}
          </h4>
          <p className="text-xs text-muted-foreground truncate">
            {document.documentAuthors.join(", ")}
          </p>
          {document.citingPageNumber && (
            <p className="text-xs text-muted-foreground mt-1">
              Cited on page {document.citingPageNumber}
            </p>
          )}
        </div>
        <div className="flex items-center gap-1 ml-2">
          {document.documentUrl && (
            <Button
              variant="ghost"
              size="sm"
              className="h-6 w-6 p-0"
              onClick={() => window.open(document.documentUrl, "_blank")}
            >
              <ExternalLink className="h-3 w-3" />
            </Button>
          )}
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
              <Badge className={getDocumentTypeColor(document.documentType)}>
                {getDocumentTypeIcon(document.documentType)}
                <span className="ml-1 capitalize">{document.documentType}</span>
              </Badge>
              <Badge variant="outline" className="text-xs">
                <Calendar className="h-3 w-3 mr-1" />
                {formatDate(document.documentDate)}
              </Badge>
            </div>
            <CardTitle className="text-lg leading-tight mb-2">
              {document.documentTitle}
            </CardTitle>
            <div className="flex items-center gap-4 text-sm text-muted-foreground">
              <div className="flex items-center gap-1">
                <Users className="h-4 w-4" />
                <span>{document.documentAuthors.join(", ")}</span>
              </div>
            </div>
          </div>
          <div className="flex items-center gap-2 ml-4">
            {document.documentUrl && (
              <Button
                variant="outline"
                size="sm"
                onClick={() => window.open(document.documentUrl, "_blank")}
              >
                <ExternalLink className="h-4 w-4 mr-2" />
                View
              </Button>
            )}
          </div>
        </div>
      </CardHeader>

      <CardContent className="pt-0">
        <div className="space-y-3">
          {/* Citation Context */}
          {(document.citingPageNumber || document.citingContext) && (
            <div className="bg-muted/50 p-3 rounded-lg">
              <h5 className="font-medium text-sm mb-2">
                How this document cites yours
              </h5>
              {document.citingPageNumber && (
                <p className="text-xs text-muted-foreground mb-2">
                  Referenced on page {document.citingPageNumber}
                </p>
              )}
              {document.citingContext && (
                <p className="text-sm italic">"{document.citingContext}"</p>
              )}
            </div>
          )}

          {/* Document Metadata */}
          <div className="text-xs text-muted-foreground">
            <p>Added on {formatDate(document.addedDate)}</p>
          </div>
        </div>
      </CardContent>
    </Card>
  );
};
