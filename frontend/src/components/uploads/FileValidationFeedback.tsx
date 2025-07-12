import React, { useMemo } from "react";
import { cn } from "@/lib/utils";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import {
  AlertCircle,
  AlertTriangle,
  CheckCircle,
  Info,
  FileText,
  Shield,
  Zap,
  HardDrive,
  FileX,
  FileCheck,
  X,
} from "lucide-react";
import logger from "@/logger";
import type {
  FileValidationResult,
  FileValidationError,
  FileValidationWarning,
} from "@/lib/api/types/upload";

/**
 * Configuration for file validation feedback
 */
export interface FileValidationFeedbackConfig {
  /** Show detailed validation information */
  showDetails?: boolean;
  /** Show file metadata */
  showMetadata?: boolean;
  /** Show validation progress */
  showProgress?: boolean;
  /** Compact display mode */
  compact?: boolean;
  /** Enable dismissible alerts */
  dismissible?: boolean;
  /** Group similar validation issues */
  groupSimilar?: boolean;
  /** Maximum number of errors/warnings to show */
  maxIssues?: number;
  /** Custom CSS classes */
  className?: string;
}

/**
 * Props for the FileValidationFeedback component
 */
export interface FileValidationFeedbackProps
  extends FileValidationFeedbackConfig {
  /** File being validated */
  file?: File;
  /** Validation result */
  validation: FileValidationResult;
  /** Custom title */
  title?: string;
  /** Callback when validation issue is dismissed */
  onDismissIssue?: (index: number, type: "error" | "warning") => void;
  /** Callback when feedback is closed */
  onClose?: () => void;
}

/**
 * Individual validation issue component
 */
interface ValidationIssueProps {
  issue: FileValidationError | FileValidationWarning;
  type: "error" | "warning";
  index: number;
  compact?: boolean;
  dismissible?: boolean;
  onDismiss?: (index: number, type: "error" | "warning") => void;
}

const ValidationIssue: React.FC<ValidationIssueProps> = ({
  issue,
  type,
  index,
  compact = false,
  dismissible = false,
  onDismiss,
}) => {
  const getIcon = () => {
    switch (type) {
      case "error":
        return <AlertCircle className="h-4 w-4" />;
      case "warning":
        return <AlertTriangle className="h-4 w-4" />;
      default:
        return <Info className="h-4 w-4" />;
    }
  };

  const getAlertVariant = () => {
    return type === "error" ? "destructive" : "default";
  };

  const getSeverityBadge = () => {
    if (!issue.severity) return null;
    const severityClasses = {
      error: "bg-destructive/10 text-destructive-foreground",
      warning: "bg-warning/10 text-warning-foreground",
    };
    return (
      <Badge
        variant="outline"
        className={cn("text-xs", severityClasses[issue.severity])}
      >
        {issue.severity}
      </Badge>
    );
  };

  const handleDismiss = () => {
    onDismiss?.(index, type);
    logger.debug("Validation issue dismissed", {
      type,
      code: issue.code,
      index,
    });
  };

  return (
    <Alert
      variant={getAlertVariant()}
      className={cn(compact ? "py-2" : "py-3")}
    >
      <div className="flex items-start justify-between gap-2">
        <div className="flex items-start min-w-0 flex-1 gap-3">
          {getIcon()}
          <div className="min-w-0 flex-1">
            <AlertDescription className="text-sm">
              <div className="flex items-center gap-2 mb-1">
                <span className="font-medium">{issue.message}</span>
                {getSeverityBadge()}
              </div>

              {!compact && issue.field && (
                <p className="text-xs text-gray-600 mt-1">
                  Field: {issue.field}
                </p>
              )}

              {!compact && issue.code && (
                <p className="text-xs text-gray-500 mt-1">Code: {issue.code}</p>
              )}
            </AlertDescription>
          </div>
        </div>

        {dismissible && (
          <Button
            variant="ghost"
            size="sm"
            onClick={handleDismiss}
            className="h-6 w-6 p-0 flex-shrink-0"
          >
            <X className="h-3 w-3" />
          </Button>
        )}
      </div>
    </Alert>
  );
};

/**
 * File metadata display component
 */
interface FileMetadataProps {
  file: File;
  metadata?: Record<string, any>;
  compact?: boolean;
}

const FileMetadata: React.FC<FileMetadataProps> = ({
  file,
  metadata,
  compact = false,
}) => {
  const formatFileSize = (bytes: number): string => {
    if (bytes === 0) return "0 B";
    const k = 1024;
    const sizes = ["B", "KB", "MB", "GB"];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return `${parseFloat((bytes / Math.pow(k, i)).toFixed(2))} ${sizes[i]}`;
  };

  const formatDate = (timestamp: number): string => {
    return new Date(timestamp).toLocaleDateString();
  };

  const basicInfo = [
    { icon: <FileText className="h-4 w-4" />, label: "Name", value: file.name },
    {
      icon: <HardDrive className="h-4 w-4" />,
      label: "Size",
      value: formatFileSize(file.size),
    },
    {
      icon: <Zap className="h-4 w-4" />,
      label: "Type",
      value: file.type || "Unknown",
    },
    {
      icon: <Info className="h-4 w-4" />,
      label: "Modified",
      value: formatDate(file.lastModified),
    },
  ];

  if (compact) {
    return (
      <div className="flex items-center gap-4 text-xs text-muted-foreground">
        <span>{formatFileSize(file.size)}</span>
        <span>{file.type || "Unknown type"}</span>
        <span>{formatDate(file.lastModified)}</span>
      </div>
    );
  }

  return (
    <div className="space-y-3">
      <div className="grid grid-cols-2 gap-3">
        {basicInfo.map((info, index) => (
          <div key={index} className="flex items-center gap-2">
            <div className="text-muted-foreground">{info.icon}</div>
            <div className="min-w-0 flex-1">
              <p className="text-xs text-muted-foreground">{info.label}</p>
              <p className="text-sm text-foreground truncate">{info.value}</p>
            </div>
          </div>
        ))}
      </div>

      {metadata && Object.keys(metadata).length > 0 && (
        <div className="pt-2 border-t">
          <p className="text-xs font-medium text-foreground mb-2">
            Additional Metadata
          </p>
          <div className="space-y-1">
            {Object.entries(metadata).map(([key, value]) => (
              <div key={key} className="flex justify-between text-xs">
                <span className="text-muted-foreground">{key}:</span>
                <span className="text-foreground truncate ml-2">
                  {String(value)}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

/**
 * Validation summary component
 */
interface ValidationSummaryProps {
  validation: FileValidationResult;
  compact?: boolean;
}

const ValidationSummary: React.FC<ValidationSummaryProps> = ({
  validation,
  compact = false,
}) => {
  const { isValid, errors, warnings } = validation;

  const getStatusIcon = () => {
    if (!isValid) return <FileX className="h-5 w-5 text-destructive" />;
    if (warnings.length > 0)
      return <AlertTriangle className="h-5 w-5 text-warning" />;
    return <FileCheck className="h-5 w-5 text-success" />;
  };

  const getStatusText = () => {
    if (!isValid) return "Validation Failed";
    if (warnings.length > 0) return "Validation Passed with Warnings";
    return "Validation Passed";
  };

  const getStatusColor = () => {
    if (!isValid) return "text-destructive-foreground";
    if (warnings.length > 0) return "text-warning-foreground";
    return "text-success-foreground";
  };

  if (compact) {
    return (
      <div className="flex items-center gap-2">
        {getStatusIcon()}
        <span className={cn("text-sm font-medium", getStatusColor())}>
          {getStatusText()}
        </span>
        {errors.length > 0 && (
          <Badge variant="destructive" className="text-xs">
            {errors.length} error{errors.length !== 1 ? "s" : ""}
          </Badge>
        )}
        {warnings.length > 0 && (
          <Badge
            variant="outline"
            className="text-xs bg-warning/10 text-warning-foreground"
          >
            {warnings.length} warning{warnings.length !== 1 ? "s" : ""}
          </Badge>
        )}
      </div>
    );
  }

  return (
    <div className="flex items-center justify-between">
      <div className="flex items-center gap-3">
        {getStatusIcon()}
        <div>
          <h4 className={cn("text-lg font-semibold", getStatusColor())}>
            {getStatusText()}
          </h4>
          <p className="text-sm text-muted-foreground">
            {errors.length} error{errors.length !== 1 ? "s" : ""},{" "}
            {warnings.length} warning{warnings.length !== 1 ? "s" : ""}
          </p>
        </div>
      </div>

      <div className="flex items-center gap-2">
        {!isValid && (
          <Badge variant="destructive">
            <Shield className="h-3 w-3 mr-1" />
            Blocked
          </Badge>
        )}
        {isValid && warnings.length > 0 && (
          <Badge
            variant="outline"
            className="bg-warning/10 text-warning-foreground"
          >
            <AlertTriangle className="h-3 w-3 mr-1" />
            Review Required
          </Badge>
        )}
        {isValid && warnings.length === 0 && (
          <Badge
            variant="default"
            className="bg-success/10 text-success-foreground"
          >
            <CheckCircle className="h-3 w-3 mr-1" />
            Approved
          </Badge>
        )}
      </div>
    </div>
  );
};

/**
 * File Validation Feedback Component
 *
 * Displays comprehensive validation feedback for uploaded files,
 * including errors, warnings, metadata, and validation progress.
 */
export const FileValidationFeedback: React.FC<FileValidationFeedbackProps> = ({
  file,
  validation,
  title,
  showDetails = true,
  showMetadata = true,
  showProgress = false,
  compact = false,
  dismissible = false,
  groupSimilar = true,
  maxIssues = 10,
  className,
  onDismissIssue,
  onClose,
}) => {
  // Group similar issues if enabled
  const groupedIssues = useMemo(() => {
    if (!groupSimilar) {
      return {
        errors: validation.errors,
        warnings: validation.warnings,
      };
    }

    const groupBy = (
      items: (FileValidationError | FileValidationWarning)[],
      keyFn: (item: any) => string,
    ) => {
      const groups = new Map();
      items.forEach((item) => {
        const key = keyFn(item);
        if (!groups.has(key)) {
          groups.set(key, []);
        }
        groups.get(key).push(item);
      });
      return Array.from(groups.values()).map((group) => group[0]); // Take first item from each group
    };

    return {
      errors: groupBy(
        validation.errors,
        (error) => error.code || error.message,
      ),
      warnings: groupBy(
        validation.warnings,
        (warning) => warning.code || warning.message,
      ),
    };
  }, [validation.errors, validation.warnings, groupSimilar]);

  // Limit number of issues displayed
  const displayErrors = groupedIssues.errors.slice(0, maxIssues);
  const displayWarnings = groupedIssues.warnings.slice(0, maxIssues);
  const hiddenErrorsCount = Math.max(
    0,
    groupedIssues.errors.length - maxIssues,
  );
  const hiddenWarningsCount = Math.max(
    0,
    groupedIssues.warnings.length - maxIssues,
  );

  const handleCloseClick = () => {
    onClose?.();
    logger.debug("Validation feedback closed");
  };

  return (
    <div
      className={cn("space-y-4 p-4 border rounded-lg bg-background", className)}
    >
      {/* Header */}
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold text-foreground">
          {title || "File Validation"}
        </h3>

        {onClose && (
          <Button
            variant="ghost"
            size="sm"
            onClick={handleCloseClick}
            className="h-8 w-8 p-0"
          >
            <X className="h-4 w-4" />
          </Button>
        )}
      </div>

      {/* Validation Summary */}
      <ValidationSummary validation={validation} compact={compact} />

      {/* File Metadata */}
      {file && showMetadata && (
        <div className="space-y-2">
          <h4 className="text-sm font-medium text-foreground">
            File Information
          </h4>
          <FileMetadata
            file={file}
            metadata={validation.metadata}
            compact={compact}
          />
        </div>
      )}

      {/* Validation Progress */}
      {showProgress && (
        <div className="space-y-2">
          <div className="flex items-center justify-between text-sm">
            <span className="text-muted-foreground">Validation Progress</span>
            <span className="text-foreground font-medium">
              {validation.isValid ? "100%" : "In Progress..."}
            </span>
          </div>
          <Progress value={validation.isValid ? 100 : 75} className="h-2" />
        </div>
      )}

      {/* Validation Errors */}
      {displayErrors.length > 0 && (
        <div className="space-y-2">
          <h4 className="text-sm font-medium text-destructive-foreground flex items-center gap-2">
            <AlertCircle className="h-4 w-4" />
            Errors ({validation.errors.length})
          </h4>
          <div className="space-y-2">
            {displayErrors.map((error, index) => (
              <ValidationIssue
                key={index}
                issue={error}
                type="error"
                index={index}
                compact={compact}
                dismissible={dismissible}
                onDismiss={onDismissIssue}
              />
            ))}

            {hiddenErrorsCount > 0 && (
              <p className="text-xs text-muted-foreground text-center py-2">
                ... and {hiddenErrorsCount} more error
                {hiddenErrorsCount !== 1 ? "s" : ""}
              </p>
            )}
          </div>
        </div>
      )}

      {/* Validation Warnings */}
      {displayWarnings.length > 0 && (
        <div className="space-y-2">
          <h4 className="text-sm font-medium text-warning-foreground flex items-center gap-2">
            <AlertTriangle className="h-4 w-4" />
            Warnings ({validation.warnings.length})
          </h4>
          <div className="space-y-2">
            {displayWarnings.map((warning, index) => (
              <div className="py-1">
                <ValidationIssue
                  key={index}
                  issue={warning}
                  type="warning"
                  index={index}
                  compact={compact}
                  dismissible={dismissible}
                  onDismiss={onDismissIssue}
                />
              </div>
            ))}

            {hiddenWarningsCount > 0 && (
              <p className="text-xs text-muted-foreground text-center py-2">
                ... and {hiddenWarningsCount} more warning
                {hiddenWarningsCount !== 1 ? "s" : ""}
              </p>
            )}
          </div>
        </div>
      )}

      {/* No Issues Message */}
      {validation.isValid &&
        displayErrors.length === 0 &&
        displayWarnings.length === 0 && (
          <div className="text-center py-6">
            <CheckCircle className="h-12 w-12 text-success mx-auto mb-3" />
            <h4 className="text-lg font-medium text-success-foreground mb-1">
              Validation Passed
            </h4>
            <p className="text-sm text-muted-foreground">
              {file
                ? `${file.name} passed all validation checks`
                : "File passed all validation checks"}
            </p>
          </div>
        )}
    </div>
  );
};

export default FileValidationFeedback;
