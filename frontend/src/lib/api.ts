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
