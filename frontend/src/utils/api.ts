// frontend/src/utils/api.ts

export async function postSummary(text: string, userId: string | null = null) {
  const res = await fetch(`${import.meta.env.VITE_API_URL}/summarize`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ text, user_id: userId }),
  });

  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.detail || "요약 실패");
  }

  return await res.json(); // { summary, saved, summary_id }
}
