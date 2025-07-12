declare module "@/logger" {
  type LogLevel = "error" | "warn" | "info" | "debug" | "trace";

  const logger: {
    error: (...args: any[]) => void;
    warn: (...args: any[]) => void;
    info: (...args: any[]) => void;
    debug: (...args: any[]) => void;
    trace: (...args: any[]) => void;
  };

  export default logger;
}
