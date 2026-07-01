export type ApiEnvelope<T> = {
  success: boolean;
  code: string;
  message: string;
  data: T;
  paywall: null | {
    required: boolean;
    message: string;
    next_action: string;
  };
  risk_notice: string;
};
