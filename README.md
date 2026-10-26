# Site Brandaz

Site estático da Brandaz (brandaz.com.br). Roda sem Lovable e sem Hostinger: o Cloudflare Pages gera e publica o site a cada `git push`.

## Como está organizado

- `content/` — todo o conteúdo editável
  - `site.json`: textos das páginas, contatos, endereço, serviços, FAQ, clientes, filmes
  - `projetos.json`: os 37 cases (textos, métricas, galeria)
  - `blog.json`: os posts (corpo em Markdown simples: `##`, listas, `**negrito**`, `[link](/projetos/slug)`)
  - `dimensoes.json`: largura/altura das imagens (evita saltos no carregamento)
- `static/` — imagens, vídeos, fontes Karibu, CSS e JS (copiados como estão)
- `tools/build.py` — gera as páginas em `site/` (só Python padrão, nada para instalar)
- `tools/home_js.py` — movimento da home (partículas, trajeto, capas)

## Editar e publicar

1. Edite o texto no arquivo de `content/` (pelo próprio GitHub, no lápis "Edit").
2. Faça o commit. O Cloudflare Pages gera e publica sozinho em cerca de 1 minuto.

Para ver no computador antes de publicar:

```bash
python tools/build.py
python -m http.server 8000 --directory site
```

Prévia com arquivos `.html` soltos (para compartilhar como link de revisão):

```bash
python tools/build.py --preview ../previa
```

## Capas da home

- `/` — V1: filme horizontal da 90 Graus + cases de design
- `/capa-verticais/` — V2: parede de filmes verticais (fora do Google até a decisão)

Para trocar a capa principal, inverta `home('A')` e `home('B')` em `tools/build.py` (função `home`).

## Cloudflare Pages (configuração única)

1. Cloudflare → Workers & Pages → Create → Pages → Connect to Git → repositório `website-brandaz`.
2. Build command: `python3 tools/build.py` · Build output directory: `site`.
3. Custom domains → `brandaz.com.br` e `www.brandaz.com.br` (o Cloudflare indica os registros DNS).

Os arquivos `_redirects` (URLs antigas → novas) e `_headers` (cache) são gerados pelo build.
