import type{
  StartSessionRequest,
  StartSessionResponse,
  SendMessageRequest,
  SendMessageResponse,
  LeadCaptureRequest,
  LeadCaptureResponse,
} from "./types";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

export class ApiError extends Error {
  status: number;
  constructor(message: string, status: number) {
    super(message);
    this.name = "ApiError";
    this.status = status;
  }
}

async function post<TRequest, TResponse>(
  path: string,
  body: TRequest,
  timeoutMs = 20000
): Promise<TResponse> {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), timeoutMs);

  let response: Response;
  try {
    response = await fetch(`${API_BASE_URL}${path}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
      signal: controller.signal,
    });
  } catch (err) {
    if (err instanceof DOMException && err.name === "AbortError") {
      throw new ApiError("Request timed out. Please try again.", 0);
    }
    throw new ApiError("Network error. Please check your connection.", 0);
  } finally {
    clearTimeout(timeoutId);
  }

  if (!response.ok) {
    let detail = response.statusText;
    try {
      const errBody = await response.json();
      detail = errBody.detail ?? detail;
    } catch {
      // response body wasn't JSON — keep statusText
    }
    throw new ApiError(detail, response.status);
  }

  return response.json() as Promise<TResponse>;
}

export function startSession(sourcePage: string): Promise<StartSessionResponse> {
  return post<StartSessionRequest, StartSessionResponse>("/api/v1/sessions", {
    source_page: sourcePage,
  });
}

export function sendMessage(
  sessionId: string,
  message: string
): Promise<SendMessageResponse> {
  return post<SendMessageRequest, SendMessageResponse>("/api/v1/chat/messages", {
    session_id: sessionId,
    message,
  });
}

export function submitLead(data: LeadCaptureRequest): Promise<LeadCaptureResponse> {
  return post<LeadCaptureRequest, LeadCaptureResponse>("/api/v1/lead-capture", data);
}