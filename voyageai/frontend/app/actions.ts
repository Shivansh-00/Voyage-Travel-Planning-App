'use server'

export async function normalizePrompt(prompt: string): Promise<string> {
  return prompt.trim()
}
