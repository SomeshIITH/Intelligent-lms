type LogLevel = 'INFO' | 'DEBUG' | 'WARN' | 'ERROR';

class FrontendLogger {
  private formatMessage(level: LogLevel, context: string, message: string): string {
    const timestamp = new Date().toISOString();
    return `[${timestamp}] [${level}] [${context}] ${message}`;
  }

  public info(context: string, message: string, data?: any): void {
    console.log(`%c${this.formatMessage('INFO', context, message)}`, 'color: #3b82f6; font-weight: bold;', data ?? '');
  }

  public debug(context: string, message: string, data?: any): void {
    console.log(`%c${this.formatMessage('DEBUG', context, message)}`, 'color: #64748b;', data ?? '');
  }

  public warn(context: string, message: string, data?: any): void {
    console.warn(this.formatMessage('WARN', context, message), data ?? '');
  }

  public error(context: string, message: string, error?: any): void {
    console.error(
      `%c${this.formatMessage('ERROR', context, message)}`,
      'color: #ef4444; font-weight: bold; background: #fee2e2; padding: 2px 4px; border-radius: 4px;',
      error ?? ''
    );
  }
}

export const logger = new FrontendLogger();