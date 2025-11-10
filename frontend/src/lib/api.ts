const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "";

async function handleResponse<TResponse>(res: Response): Promise<TResponse> {
  if (!res.ok) {
    const message = `API Error ${res.status}`;
    throw new Error(message);
  }

  if (res.status === 204) {
    return {} as TResponse;
  }

  return (await res.json()) as TResponse;
}

export async function apiPost<TResponse>(path: string, data: unknown): Promise<TResponse> {
  const res = await fetch(`${API_URL}${path}`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(data),
    credentials: "include",
  });

  return handleResponse<TResponse>(res);
}

export async function apiGet<TResponse>(path: string): Promise<TResponse> {
  const res = await fetch(`${API_URL}${path}`, {
    method: "GET",
    credentials: "include",
  });

  return handleResponse<TResponse>(res);
}

function buildAuthHeaders(token: string | null | undefined, extra?: HeadersInit): HeadersInit {
  const headers: Record<string, string> = {};
  if (token) {
    headers.Authorization = `Bearer ${token}`;
  }
  return {
    ...extra,
    ...headers,
  };
}

export async function apiGetAuthorized<TResponse>(path: string, token: string): Promise<TResponse> {
  const res = await fetch(`${API_URL}${path}`, {
    method: "GET",
    headers: buildAuthHeaders(token),
    credentials: "include",
  });

  return handleResponse<TResponse>(res);
}

export async function apiPostAuthorized<TResponse>(
  path: string,
  data: unknown,
  token: string,
  extraHeaders: HeadersInit = {}
): Promise<TResponse> {
  const res = await fetch(`${API_URL}${path}`, {
    method: "POST",
    headers: buildAuthHeaders(token, {
      "Content-Type": "application/json",
      ...extraHeaders,
    }),
    body: JSON.stringify(data),
    credentials: "include",
  });

  return handleResponse<TResponse>(res);
}

export async function apiPostFormAuthorized<TResponse>(
  path: string,
  formData: FormData,
  token: string,
  extraHeaders: HeadersInit = {}
): Promise<TResponse> {
  const res = await fetch(`${API_URL}${path}`, {
    method: "POST",
    headers: buildAuthHeaders(token, extraHeaders),
    body: formData,
    credentials: "include",
  });

  return handleResponse<TResponse>(res);
}

export interface StreamResult<TParsed = unknown> {
  fullText: string;
  parsed?: TParsed;
}

interface StreamOptions {
  signal?: AbortSignal;
  onChunk?: (chunk: string) => void;
  extraHeaders?: HeadersInit;
}

export async function apiPostStreamAuthorized<TParsed = unknown>(
  path: string,
  data: unknown,
  token: string,
  options: StreamOptions = {}
): Promise<StreamResult<TParsed>> {
  const res = await fetch(`${API_URL}${path}`, {
    method: "POST",
    headers: buildAuthHeaders(token, {
      "Content-Type": "application/json",
      ...options.extraHeaders,
    }),
    body: JSON.stringify(data),
    credentials: "include",
    signal: options.signal,
  });

  if (!res.ok) {
    const message = `API Error ${res.status}`;
    throw new Error(message);
  }

  const contentType = res.headers.get("content-type") ?? "";

  if (contentType.includes("application/json") && !contentType.includes("stream")) {
    const parsed = (await res.json()) as TParsed;
    let text = "";
    if (parsed && typeof parsed === "object" && "reply" in (parsed as Record<string, unknown>)) {
      const maybeReply = (parsed as Record<string, unknown>).reply;
      text = typeof maybeReply === "string" ? maybeReply : JSON.stringify(parsed);
    } else if (typeof parsed === "string") {
      text = parsed;
    } else {
      text = JSON.stringify(parsed);
    }
    if (text) {
      options.onChunk?.(text);
    }
    return { fullText: text, parsed };
  }

  if (!res.body) {
    const text = await res.text();
    if (text) {
      options.onChunk?.(text);
    }
    return { fullText: text };
  }

  const reader = res.body.getReader();
  const decoder = new TextDecoder();

  if (!contentType.includes("event-stream")) {
    let fullText = "";
    while (true) {
      const { value, done } = await reader.read();
      if (done) {
        break;
      }
      const chunk = decoder.decode(value, { stream: true });
      if (chunk) {
        fullText += chunk;
        options.onChunk?.(chunk);
      }
    }
    const flush = decoder.decode();
    if (flush) {
      fullText += flush;
      options.onChunk?.(flush);
    }
    return { fullText };
  }

  let buffer = "";
  let fullText = "";

  const processLine = (line: string) => {
    const trimmed = line.trim();
    if (!trimmed) {
      return;
    }
    if (trimmed.startsWith("data:")) {
      const payload = trimmed.slice(5).trim();
      if (!payload || payload === "[DONE]") {
        return;
      }
      let textSegment = payload;
      try {
        const parsed = JSON.parse(payload) as Record<string, unknown>;
        const delta = parsed.delta ?? parsed.reply ?? parsed.content;
        if (typeof delta === "string") {
          textSegment = delta;
        } else {
          textSegment = JSON.stringify(parsed);
        }
      } catch {
        textSegment = payload;
      }
      if (textSegment) {
        fullText += textSegment;
        options.onChunk?.(textSegment);
      }
      return;
    }

    fullText += trimmed;
    options.onChunk?.(trimmed);
  };

  while (true) {
    const { value, done } = await reader.read();
    if (done) {
      break;
    }
    buffer += decoder.decode(value, { stream: true });
    let newlineIndex = buffer.indexOf("\n");
    while (newlineIndex !== -1) {
      const line = buffer.slice(0, newlineIndex);
      buffer = buffer.slice(newlineIndex + 1);
      processLine(line);
      newlineIndex = buffer.indexOf("\n");
    }
  }

  const remainder = buffer + decoder.decode();
  if (remainder.trim()) {
    processLine(remainder);
  }

  return { fullText };
}
