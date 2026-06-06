# Allia Consulting — Design System

> **Projet** : Allia Consulting, nativement IA à l'échelle
> **Version** : 1.0 — Extraction du design system depuis les contenus éditoriaux v5.0
> **Macro-narrative** : *Cabinet de conseil nativement IA agentique*

Ce document définit les fondations visuelles et les composants de l'identité numérique d'Allia Consulting. Il sert de référence unique pour toute production web, design ou frontend du cabinet. Les tokens sont extraits directement de la maquette de référence afin de garantir leur exactitude.

---

## 1. Principes de design

L'identité d'Allia repose sur cinq partis pris visuels, cohérents avec son positionnement de cabinet de stratégie premium.

1. **Sobriété institutionnelle** — Le bleu profond porte l'autorité, l'ambre ponctue sans jamais saturer. La couleur d'accent reste rare pour conserver son poids.
2. **Densité maîtrisée** — Beaucoup d'information, peu de bruit. Les fonds neutres (ivoire, blanc cassé) laissent respirer le contenu dense.
3. **Hiérarchie typographique forte** — Trois familles avec des rôles stricts : Inter pour la structure et l'autorité, DM Sans pour la lecture, JetBrains Mono pour le registre technique.
4. **Bordures fines, pas d'ombres lourdes** — Les contours à 0,5px et les coins arrondis discrets remplacent les ombres portées. L'effet est net, structuré, premium.
5. **L'accent comme signal, pas comme décor** — L'ambre marque ce qui compte : règles de séparation, chiffres clés, signaux GEO, bordures de mise en valeur.

---

## 2. Couleurs

### Palette principale

| Token | Hex | Usage |
|---|---|---|
| `--color-primary` | `#0C447C` | Bleu Allia. Fonds hero, titres, CTA, identité de marque |
| `--color-accent` | `#EF9F27` | Ambre. Règles de séparation, chiffres clés, signaux, bordures de mise en valeur |
| `--color-ink` | `#2C2C2A` | Texte principal, fonds sombres (headers de section) |
| `--color-paper` | `#FAFAF9` | Fond de page (blanc cassé) |

### Bleus secondaires

| Token | Hex | Usage |
|---|---|---|
| `--color-blue-mid` | `#185FA5` | Bleu intermédiaire — accents textuels, bordures de blocs |
| `--color-blue-bright` | `#378ADD` | Bordures gauches de blocs de copy mis en avant |
| `--color-blue-light-border` | `#85B7EB` | Contours de pills clavier / mots-clés |
| `--color-blue-wash` | `#E6F1FB` | Fonds de blocs informatifs, tags, pills primaires |

### Neutres

| Token | Hex | Usage |
|---|---|---|
| `--color-stone-border` | `#D3D1C7` | Bordures de cartes et conteneurs (0,5px) |
| `--color-stone-muted` | `#888780` | Texte secondaire, labels, métadonnées |
| `--color-stone-text` | `#5F5E5A` | Texte de corps atténué, descriptions |
| `--color-ivory` | `#F1EFE8` | Fond ivoire — cartes, sections alternées |

### Ambre — déclinaisons

| Token | Hex | Usage |
|---|---|---|
| `--color-amber` | `#EF9F27` | Accent principal |
| `--color-amber-wash` | `#FAEEDA` | Fond des encarts stratégie, pills secondaires |
| `--color-amber-deep` | `#854F0B` | Texte sur fond ambre clair |
| `--color-amber-darkest` | `#633806` | Texte sur pill ambre plein |
| `--color-amber-pale` | `#FFD58C` | Mots-clés surlignés sur fond sombre |
| `--color-blue-tint` | `#FFFCF7` | Dégradé subtil des colonnes de comparaison « Allia » |

### Bloc de variables CSS prêt à l'emploi

```css
:root {
  /* Principales */
  --color-primary: #0C447C;
  --color-accent: #EF9F27;
  --color-ink: #2C2C2A;
  --color-paper: #FAFAF9;

  /* Bleus */
  --color-blue-mid: #185FA5;
  --color-blue-bright: #378ADD;
  --color-blue-light-border: #85B7EB;
  --color-blue-wash: #E6F1FB;

  /* Neutres */
  --color-stone-border: #D3D1C7;
  --color-stone-muted: #888780;
  --color-stone-text: #5F5E5A;
  --color-ivory: #F1EFE8;

  /* Ambre */
  --color-amber: #EF9F27;
  --color-amber-wash: #FAEEDA;
  --color-amber-deep: #854F0B;
  --color-amber-darkest: #633806;
  --color-amber-pale: #FFD58C;
  --color-blue-tint: #FFFCF7;
}
```

---

## 3. Typographie

### Familles et rôles

| Famille | Rôle | Graisses | Import |
|---|---|---|---|
| **Inter** | Structure, autorité, titres, labels, CTA | 400, 500, 700, 900 | `'Inter', sans-serif` |
| **DM Sans** | Corps de texte, lecture longue | 400 | `'DM Sans', sans-serif` |
| **JetBrains Mono** | Registre technique, codes, métadonnées, rôles | 400 | `'JetBrains Mono', monospace` |

**Import Google Fonts :**

```html
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;700;900&family=DM+Sans:wght@400&family=JetBrains+Mono:wght@400&display=swap" rel="stylesheet">
```

### Échelle typographique

| Token | Taille | Famille / graisse typique | Usage |
|---|---|---|---|
| `--text-display` | 28px | Inter 900 | Titre de document, H1 hero principal |
| `--text-h2-sep` | 22px | Inter 900 | Séparateurs de grandes sections |
| `--text-title` | 18px | Inter 700 | Titres de cas clients, questions de définition |
| `--text-num` | 20px | Inter 900 | Chiffres clés inline, numéros de principes |
| `--text-lead` | 15px | Inter 700 / DM Sans 400 | Copy mise en avant, body large |
| `--text-body` | 14px | DM Sans 400 | Corps de texte standard |
| `--text-body-sm` | 13px | DM Sans 400 | Descriptions de cartes, texte dense |
| `--text-meta` | 12px | DM Sans / Mono 400 | Métadonnées, sous-titres |
| `--text-label` | 11px | Inter 700 | Labels, noms de cartes, tags |
| `--text-overline` | 10px | Inter 700 | Sur-titres, labels de section (uppercase) |
| `--text-micro` | 9px | Mono 700 | Étiquettes SEO/GEO |

### Règles d'usage

- **Interlignage corps** : `line-height: 1.7` pour la lecture, `1.3–1.4` pour les titres.
- **Letter-spacing** : titres serrés (`-0.3px` à `-0.5px`), labels espacés (`0.06em` à `0.12em`, en majuscules).
- **Uppercase** : réservé aux labels, overlines et noms de cartes (registre structurel), jamais au corps de texte.

---

## 4. Espacements & géométrie

### Rayons de bordure

| Token | Valeur | Usage |
|---|---|---|
| `--radius-lg` | 12px | Conteneurs majeurs, hero, blocs de page |
| `--radius-md` | 8px | Cartes, encarts, blocs SEO |
| `--radius-sm` | 6px | Items de copy, petits blocs |
| `--radius-xs` | 4px | Encarts stratégie, surlignages |
| `--radius-pill` | 12–14px | Pills, tags arrondis |

### Bordures

- **Contours standards** : `0.5px solid var(--color-stone-border)` — fines, premium.
- **Bordures d'accent** : `2px` à `4px` à gauche, en `--color-accent` ou `--color-blue-bright`, pour signaler la mise en valeur.

### Espacements de référence

| Contexte | Valeur |
|---|---|
| Largeur max de page | 920px |
| Padding de page | 48px 32px 96px |
| Padding conteneur (hero) | 40px 48px |
| Padding section | 24px 28px |
| Gap de grille | 8px – 24px |

---

## 5. Composants

### 5.1 — Hero (fond bleu)

Bloc d'en-tête de page. Fond `--color-primary`, texte blanc, règle ambre fine en séparateur.

```html
<div class="hero">
  <div class="hero-eyebrow">Cabinet de conseil nativement IA agentique</div>
  <h1 class="hero-title">L'IA agentique n'est pas notre offre. C'est notre façon de travailler.</h1>
  <hr class="amber-rule">
  <p class="hero-sub">Allia accompagne les grandes organisations…</p>
</div>
```

```css
.hero { background: var(--color-primary); color: #fff; border-radius: var(--radius-lg); padding: 40px 48px; }
.hero-eyebrow { font-family: 'Inter'; font-size: 13px; color: rgba(255,255,255,0.5); text-transform: uppercase; letter-spacing: 0.06em; }
.hero-title { font-family: 'Inter'; font-weight: 900; font-size: 28px; letter-spacing: -0.5px; }
.hero-sub { font-family: 'DM Sans'; font-size: 14px; color: rgba(255,255,255,0.7); line-height: 1.6; max-width: 660px; }
.amber-rule { width: 40px; height: 2px; background: var(--color-accent); border: none; margin: 12px 0 16px; }
```

### 5.2 — Carte

Bloc de contenu modulaire. Fond ivoire, contour fin, label en majuscules.

```css
.card { background: var(--color-ivory); border: 0.5px solid var(--color-stone-border); border-radius: var(--radius-md); padding: 16px; }
.card-name { font-family: 'Inter'; font-size: 11px; font-weight: 700; color: var(--color-primary); text-transform: uppercase; letter-spacing: 0.04em; margin-bottom: 8px; }
```

### 5.3 — Tag / Pill

| Variante | Fond | Texte | Bordure |
|---|---|---|---|
| Défaut | `--color-blue-wash` | `--color-blue-mid` | `--color-blue-light-border` |
| Primaire | `--color-accent` | `--color-amber-darkest` | `#854F0B` |
| Secondaire | `--color-amber-wash` | `--color-amber-deep` | `--color-accent` |

```css
.pill { font-family: 'JetBrains Mono'; font-size: 11px; padding: 5px 10px; border-radius: 14px; background: var(--color-blue-wash); color: var(--color-blue-mid); border: 0.5px solid var(--color-blue-light-border); }
.pill--primary { background: var(--color-accent); color: var(--color-amber-darkest); border-color: #854F0B; font-weight: 600; }
.pill--secondary { background: var(--color-amber-wash); color: var(--color-amber-deep); border-color: var(--color-accent); }
```

### 5.4 — Encart stratégie

Note méthodologique. Fond ambre clair, bordure gauche ambre, texte en italique.

```css
.strategy-note { font-family: 'DM Sans'; font-size: 12px; color: var(--color-stone-text); font-style: italic; padding: 8px 12px; background: var(--color-amber-wash); border-left: 2px solid var(--color-accent); border-radius: var(--radius-xs); line-height: 1.6; }
```

### 5.5 — Boîte de définition (GEO)

Encart auto-portant pensé pour la citation par les moteurs IA. Bordure gauche ambre épaisse.

```css
.def-box { background: #fff; border: 0.5px solid var(--color-stone-border); border-left: 4px solid var(--color-accent); border-radius: var(--radius-md); padding: 22px 26px; }
.def-q { font-family: 'Inter'; font-size: 18px; font-weight: 700; color: var(--color-primary); line-height: 1.3; letter-spacing: -0.3px; }
.def-a { font-family: 'DM Sans'; font-size: 14px; color: var(--color-ink); line-height: 1.75; }
.def-a strong { color: var(--color-primary); font-weight: 700; }
.def-a em { font-style: italic; color: var(--color-blue-mid); }
```

### 5.6 — Bloc résultat (cas client)

Fond bleu, chiffre clé en ambre. Conclut chaque cas client.

```css
.result { background: var(--color-primary); color: #fff; border-radius: var(--radius-md); padding: 14px 18px; }
.result-label { font-family: 'Inter'; font-size: 10px; font-weight: 500; text-transform: uppercase; letter-spacing: 0.08em; color: rgba(255,255,255,0.6); }
.result-text { font-family: 'Inter'; font-size: 14px; font-weight: 700; line-height: 1.4; }
.result-text .num { color: var(--color-accent); font-size: 20px; font-weight: 900; }
```

### 5.7 — Item FAQ

Pour la page contact. À implémenter avec Schema.org `FAQPage`.

```css
.faq-item { background: #fff; border: 0.5px solid var(--color-stone-border); border-radius: var(--radius-md); padding: 18px 22px; }
.faq-q { font-family: 'Inter'; font-size: 15px; font-weight: 700; color: var(--color-primary); line-height: 1.4; }
.faq-q::before { content: 'Q. '; color: var(--color-accent); font-weight: 900; }
.faq-a { font-family: 'DM Sans'; font-size: 13px; color: var(--color-ink); line-height: 1.7; }
.faq-a::before { content: 'R. '; color: var(--color-blue-mid); font-weight: 700; font-family: 'Inter'; }
```

### 5.8 — Grille de comparaison

Deux colonnes opposées. La colonne « Allia » se distingue par bordure ambre et léger dégradé.

```css
.comp-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
.comp-col { background: #fff; border: 0.5px solid var(--color-stone-border); border-radius: var(--radius-md); padding: 18px 20px; }
.comp-col--allia { border-color: var(--color-accent); background: linear-gradient(180deg, #fff 0%, var(--color-blue-tint) 100%); }
```

---

## 6. Grilles & layout

| Token | Valeur | Usage |
|---|---|---|
| `--grid-2` | `repeat(2, 1fr)`, gap 12px | Paires de cartes, layout côte à côte |
| `--grid-3` | `repeat(3, 1fr)`, gap 12px | Aperçus expertises, cas clients, insights |
| `--grid-5` | `repeat(5, 1fr)`, gap 8px | Plan du site (5 pages) |

```css
.grid-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
.grid-3 { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 12px; }
```

**Recommandation responsive** : sous 768px, basculer toutes les grilles en colonne unique (`grid-template-columns: 1fr`).

---

## 7. Voix & ton (rappel éditorial)

Le design ne se sépare jamais du discours. Quatre règles éditoriales engagent aussi les choix visuels :

1. **Macro-narrative possédée** — « Cabinet de conseil nativement IA agentique » apparaît en eyebrow hero, footer et page identité.
2. **Expertises, pas services** — Le registre « territoire intellectuel » prime sur le registre commercial.
3. **Anonymisation totale, contexte maximal** — Cas clients sans nom mais maximalement spécifiés (secteur, taille, géo, chiffres).
4. **Signature collective** — Allia signe institutionnellement. Compensation GEO : densité factuelle, FAQ structurée, Schema.org.

---

## 8. Accessibilité — points de vigilance

- **Contraste** : le bleu `#0C447C` sur blanc et le texte blanc sur bleu respectent WCAG AA. Vérifier les textes atténués (`rgba(255,255,255,0.5)`) qui peuvent passer sous le seuil AA pour le texte de petite taille — réserver aux éléments décoratifs ou non essentiels.
- **Ambre sur blanc** : `#EF9F27` n'atteint pas le ratio AA pour du texte normal sur fond clair. Le réserver aux accents graphiques, chiffres de grande taille et bordures, jamais à du corps de texte lisible.
- **Taille de police minimale** : éviter le 9–10px pour du contenu informatif essentiel ; le cantonner aux étiquettes décoratives.
- **États de focus** : prévoir un anneau de focus visible (`outline: 2px solid var(--color-blue-bright)`) sur tous les éléments interactifs, non défini dans la maquette de référence.

---

## 9. Notes d'implémentation GitHub

- Déposer ce fichier sous `/design-system/README.md` ou `/docs/design-system.md` dans le dépôt de gestion.
- Les variables CSS de la section 2 peuvent être extraites dans un `tokens.css` partagé.
- Toute évolution de palette ou de typo doit faire l'objet d'une montée de version (en-tête de ce document).

*Document généré comme référence de design system pour le projet « Allia Consulting, nativement IA à l'échelle ».*
