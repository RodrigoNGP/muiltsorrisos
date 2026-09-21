# Multisorrisos — Landing Page

Landing page de conversão da clínica odontológica Multisorrisos (Caruaru - PE). Todos os botões levam ao agendamento pelo WhatsApp.

## Rodar localmente

```bash
node server.js
```

Abre em http://localhost:5501.

## Editar

O conteúdo fica em `_src/`. Depois de qualquer alteração, gere o `index.html`:

```bash
python build.py
```

| Arquivo | O que controla |
|---|---|
| `_src/pages/index.html` | Textos e seções da página |
| `_src/partials/` | Cabeçalho, rodapé e formulário de agendamento |
| `_src/google-reviews.json` | Avaliações do Google (nota, total e textos) |
| `_src/pacientes.json` | Galeria "Nossos pacientes" (fotos em `assets/pacientes/`) |
| `_src/icons.py` | Ícones SVG, usados como `{{icon:nome}}` |
| `styles.css` / `script.js` | Estilos e comportamento |

## Rastreamento

O `script.js` envia os eventos `whatsapp_click`, `phone_click` e `generate_lead` para GTM/GA4 (`dataLayer`), Google Ads (`gtag`) e Meta (`fbq`). Cole os códigos de rastreamento no `<head>` de `_src/layout.html`.

## Imagens de pacientes

Use apenas fotos com autorização por escrito do paciente (ou dos responsáveis, no caso de crianças). Os originais em alta resolução ficam em `_src/originais/` e não são versionados.
