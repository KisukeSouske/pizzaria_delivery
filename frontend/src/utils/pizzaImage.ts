const IMAGEM_PADRAO = '/pizzas/padrao.svg'

// Imagens disponíveis em public/pizzas (copiadas de assets/cardapio do backend).
const DISPONIVEIS = new Set(['calabresa', 'mussarela', 'pepperoni', 'portuguesa'])

function criarSlug(nome: string): string {
  return nome
    .normalize('NFD')
    .replace(/\p{Diacritic}/gu, '')
    .toLowerCase()
    .trim()
    .replace(/\s+/g, '-')
}

/** A API não guarda imagens, então o arquivo é escolhido pelo nome da pizza. */
export function imagemDaPizza(nome: string | null): string {
  if (!nome) return IMAGEM_PADRAO
  const slug = criarSlug(nome)
  return DISPONIVEIS.has(slug) ? `/pizzas/${slug}.jpeg` : IMAGEM_PADRAO
}
