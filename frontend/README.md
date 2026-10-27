# Front-end — Pizzaria Delivery

Interface em React + TypeScript (Vite) para a API deste repositório: cardápio,
carrinho, checkout e acompanhamento dos pedidos.

## Estrutura

```
src/
├── main.tsx            # monta o React, o router e o AuthProvider
├── App.tsx             # rotas e layout geral
├── components/         # peças de tela reutilizáveis (Header, Cart, PizzaCard…)
├── pages/              # uma pasta de tela por rota (Cardápio, Meus pedidos, Login)
├── contexts/           # AuthContext (sessão) e CartContext (carrinho)
├── hooks/              # useAuth, useCart, usePizzas
├── services/           # http.ts + um módulo por área da API
├── types/              # espelho dos schemas Pydantic
├── utils/              # formatação, imagens e localStorage
└── styles/             # tokens.css (cores, raios) e global.css
```

Cada componente fica ao lado do seu `*.module.css`; os CSS Modules isolam o
estilo e as cores saem todas de `styles/tokens.css`.

## Como rodar

Com a API no ar (`uvicorn app.main:app --reload`, na raiz do projeto):

```bash
cd frontend
npm install
npm run dev
```

A interface sobe em http://localhost:5173.

| Script            | O que faz                                  |
| ----------------- | ------------------------------------------ |
| `npm run dev`     | servidor de desenvolvimento com hot reload |
| `npm run build`   | checa os tipos e gera `dist/`              |
| `npm run preview` | serve o `dist/` já construído              |
| `npm run typecheck` | só a checagem de tipos                   |

## Como ele conversa com a API

As chamadas usam o prefixo `/api` e o Vite as repassa para o backend
(`vite.config.ts`). Como tudo sai da mesma origem, a API **não precisa liberar
CORS** em desenvolvimento. O alvo do proxy vem de `VITE_API_URL` — copie
`.env.example` para `.env` se a API não estiver em `http://localhost:8000`.

Para servir o `dist/` em outro domínio que não o da API, aí sim o backend
precisaria do `CORSMiddleware` do FastAPI.

O token JWT fica no `localStorage` e é enviado no header `Authorization` a cada
requisição. Se a API responder 401, a sessão é encerrada automaticamente.

## Pontos em que a tela se adapta à API

- **Imagens**: a API não guarda imagens das pizzas, então o arquivo é escolhido
  pelo nome do sabor (`utils/pizzaImage.ts`). As imagens ficam em
  `public/pizzas/`, copiadas de `assets/cardapio/`. Um sabor sem imagem
  correspondente cai num desenho genérico.
- **Quantidade no carrinho**: a API só sabe somar itens (`POST .../itens`) e
  apagá-los (`DELETE .../itens/{id}`). Para **diminuir** a quantidade, o front
  remove o item e o recria com o valor novo (`contexts/CartContext.tsx`).
- **Nome do usuário**: não há rota de perfil, então o cabeçalho mostra o que o
  formulário de login já sabe.
