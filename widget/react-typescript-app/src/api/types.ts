export interface StartSessionRequest {
  source_page: string;
}

export interface StartSessionResponse {
  session_id: string;
  status: string;
  started_at: string;
}

export interface SendMessageRequest {
  session_id: string;
  message: string;
}

export interface SendMessageResponse {
  session_id: string;
  answer: string;
  sources_used: number;
  grounded: boolean;
  lead_capture_required: boolean;
  missing_lead_fields: string[];
  field_validation_error: string | null;
  lead_submitted: boolean;
  notification_sent: boolean;
}

export interface LeadCaptureRequest {
  session_id: string;
  name?: string;
  email?: string;
  phone?: string;
}

export interface LeadCaptureResponse {
  success: boolean;
  status: string;
  errors: Record<string, string>;
}