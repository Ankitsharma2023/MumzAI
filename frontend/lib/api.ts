// Talks to the Python backend. The URL comes from .env.local.
export const API_URL =
  process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export interface Product {
  id: string;
  name_en: string;
  name_ar: string;
  brand: string;
  category: string;
  subcategory: string;
  price_aed: number;
  sale_price_aed: number;
  tabby_installment_aed: number;
  rating: number;
  rating_count: number;
  recommended_age: string;
  weight_range_kg: string;
  isofix: boolean;
  in_stock: boolean;
  image_url: string;
  description_en: string;
  description_ar: string;
  reviews?: { author: string; stars: number; text: string }[];
}

export interface ChatResponse {
  answer: string;
  confidence: "high" | "medium" | "low";
  safety_notes: string;
  products: Product[];
  retrieved_ids: string[];
  latency_ms: number;
  lang: "en" | "ar";
  clarifying_questions?: { question: string; options: string[] }[];
}

export interface Turn {
  role: "user" | "assistant";
  content: string;
}

export async function sendChat(
  message: string,
  lang: "en" | "ar",
  history: Turn[] = [],
  contextIds: string[] = []
): Promise<ChatResponse> {
  const res = await fetch(`${API_URL}/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message, lang, history, context_ids: contextIds }),
  });
  if (!res.ok) throw new Error(`API error ${res.status}`);
  return res.json();
}
