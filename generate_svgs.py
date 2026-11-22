import os

flower_svgs = {
    "red_roses.svg": '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 300" width="100%" height="100%">
  <defs>
    <linearGradient id="bg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#FFF5F5"/>
      <stop offset="100%" stop-color="#FFE3E3"/>
    </linearGradient>
    <radialGradient id="roseRed" cx="50%" cy="50%" r="50%">
      <stop offset="0%" stop-color="#FF4D6D"/>
      <stop offset="70%" stop-color="#C9184A"/>
      <stop offset="100%" stop-color="#800F2F"/>
    </radialGradient>
    <radialGradient id="leafGrad" cx="30%" cy="30%" r="70%">
      <stop offset="0%" stop-color="#95D5B2"/>
      <stop offset="100%" stop-color="#2D6A4F"/>
    </radialGradient>
  </defs>
  <rect width="400" height="300" fill="url(#bg)" rx="12"/>
  <!-- Stems and Ribbon -->
  <path d="M170 270 L195 180 M200 270 L200 170 M230 270 L205 180" stroke="#40916C" stroke-width="6" stroke-linecap="round"/>
  <rect x="180" y="220" width="40" height="20" rx="6" fill="#D90429"/>
  <path d="M180 230 C160 250, 160 270, 175 285 M220 230 C240 250, 240 270, 225 285" stroke="#D90429" stroke-width="5" fill="none" stroke-linecap="round"/>
  <!-- Leaves -->
  <path d="M150 180 C120 160, 130 130, 170 150 C160 175, 150 180, 150 180 Z" fill="url(#leafGrad)"/>
  <path d="M250 180 C280 160, 270 130, 230 150 C240 175, 250 180, 250 180 Z" fill="url(#leafGrad)"/>
  <path d="M200 130 C220 90, 250 110, 210 130 Z" fill="url(#leafGrad)"/>
  <!-- Roses -->
  <!-- Left Rose -->
  <circle cx="160" cy="140" r="32" fill="url(#roseRed)"/>
  <path d="M160 120 C150 130, 150 145, 160 155 C170 145, 170 130, 160 120 Z" fill="#FF758F" opacity="0.8"/>
  <circle cx="160" cy="138" r="14" fill="#590D22"/>
  <!-- Right Rose -->
  <circle cx="240" cy="140" r="32" fill="url(#roseRed)"/>
  <path d="M240 120 C230 130, 230 145, 240 155 C250 145, 250 130, 240 120 Z" fill="#FF758F" opacity="0.8"/>
  <circle cx="240" cy="138" r="14" fill="#590D22"/>
  <!-- Center Top Rose -->
  <circle cx="200" cy="100" r="38" fill="url(#roseRed)"/>
  <path d="M200 75 C185 90, 185 110, 200 120 C215 110, 215 90, 200 75 Z" fill="#FF758F" opacity="0.85"/>
  <circle cx="200" cy="98" r="16" fill="#590D22"/>
  <text x="200" y="280" font-family="'Segoe UI', Roboto, sans-serif" font-size="14" font-weight="bold" fill="#A4133C" text-anchor="middle" letter-spacing="1">VELVET RED ROSES</text>
</svg>''',

    "purple_orchids.svg": '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 300" width="100%" height="100%">
  <defs>
    <linearGradient id="pbg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#F3E8FF"/>
      <stop offset="100%" stop-color="#E9D5FF"/>
    </linearGradient>
    <radialGradient id="orchidPetal" cx="50%" cy="50%" r="50%">
      <stop offset="0%" stop-color="#C084FC"/>
      <stop offset="60%" stop-color="#9333EA"/>
      <stop offset="100%" stop-color="#6B21A8"/>
    </radialGradient>
  </defs>
  <rect width="400" height="300" fill="url(#pbg)" rx="12"/>
  <!-- Arching Stem -->
  <path d="M120 280 Q200 220 230 70" stroke="#3F6212" stroke-width="6" fill="none" stroke-linecap="round"/>
  <!-- Left Bloom -->
  <g transform="translate(160, 170)">
    <ellipse cx="-25" cy="-5" rx="24" ry="16" fill="url(#orchidPetal)" transform="rotate(-25)"/>
    <ellipse cx="25" cy="-5" rx="24" ry="16" fill="url(#orchidPetal)" transform="rotate(25)"/>
    <ellipse cx="0" cy="-25" rx="22" ry="18" fill="url(#orchidPetal)"/>
    <ellipse cx="-15" cy="20" rx="20" ry="15" fill="#7E22CE"/>
    <ellipse cx="15" cy="20" rx="20" ry="15" fill="#7E22CE"/>
    <circle cx="0" cy="5" r="8" fill="#FACC15"/>
    <circle cx="0" cy="5" r="3" fill="#E11D48"/>
  </g>
  <!-- Center Main Bloom -->
  <g transform="translate(210, 110)">
    <ellipse cx="-30" cy="-5" rx="28" ry="19" fill="url(#orchidPetal)" transform="rotate(-25)"/>
    <ellipse cx="30" cy="-5" rx="28" ry="19" fill="url(#orchidPetal)" transform="rotate(25)"/>
    <ellipse cx="0" cy="-30" rx="26" ry="20" fill="url(#orchidPetal)"/>
    <ellipse cx="-18" cy="24" rx="24" ry="18" fill="#7E22CE"/>
    <ellipse cx="18" cy="24" rx="24" ry="18" fill="#7E22CE"/>
    <circle cx="0" cy="6" r="10" fill="#FACC15"/>
    <circle cx="0" cy="6" r="4" fill="#E11D48"/>
  </g>
  <!-- Top Bud -->
  <circle cx="230" cy="65" r="9" fill="#84CC16"/>
  <circle cx="238" cy="55" r="6" fill="#A855F7"/>
  <text x="200" y="280" font-family="'Segoe UI', Roboto, sans-serif" font-size="14" font-weight="bold" fill="#6B21A8" text-anchor="middle" letter-spacing="1">ROYAL PURPLE ORCHIDS</text>
</svg>''',

    "yellow_roses.svg": '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 300" width="100%" height="100%">
  <defs>
    <linearGradient id="ybg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#FEFCE8"/>
      <stop offset="100%" stop-color="#FEF08A"/>
    </linearGradient>
    <radialGradient id="roseYellow" cx="50%" cy="50%" r="50%">
      <stop offset="0%" stop-color="#FEF08A"/>
      <stop offset="65%" stop-color="#EAB308"/>
      <stop offset="100%" stop-color="#CA8A04"/>
    </radialGradient>
  </defs>
  <rect width="400" height="300" fill="url(#ybg)" rx="12"/>
  <path d="M180 270 L195 180 M200 270 L200 170 M220 270 L205 180" stroke="#15803D" stroke-width="6" stroke-linecap="round"/>
  <circle cx="160" cy="140" r="30" fill="url(#roseYellow)"/>
  <circle cx="240" cy="140" r="30" fill="url(#roseYellow)"/>
  <circle cx="200" cy="100" r="36" fill="url(#roseYellow)"/>
  <circle cx="200" cy="98" r="14" fill="#A16207"/>
  <circle cx="160" cy="138" r="12" fill="#A16207"/>
  <circle cx="240" cy="138" r="12" fill="#A16207"/>
  <text x="200" y="280" font-family="'Segoe UI', Roboto, sans-serif" font-size="14" font-weight="bold" fill="#854D0E" text-anchor="middle" letter-spacing="1">SUNRISE YELLOW ROSES</text>
</svg>''',

    "pink_carnations.svg": '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 300" width="100%" height="100%">
  <defs>
    <linearGradient id="cbg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#FDF2F8"/>
      <stop offset="100%" stop-color="#FCE7F3"/>
    </linearGradient>
  </defs>
  <rect width="400" height="300" fill="url(#cbg)" rx="12"/>
  <path d="M200 270 L200 150" stroke="#166534" stroke-width="6" stroke-linecap="round"/>
  <path d="M170 270 L190 170 M230 270 L210 170" stroke="#166534" stroke-width="5" stroke-linecap="round"/>
  <!-- Carnation 1 -->
  <g transform="translate(200, 110)">
    <circle cx="0" cy="0" r="42" fill="#F472B6"/>
    <circle cx="-15" cy="-10" r="22" fill="#EC4899"/>
    <circle cx="15" cy="-10" r="22" fill="#EC4899"/>
    <circle cx="0" cy="12" r="24" fill="#DB2777"/>
    <circle cx="0" cy="-5" r="15" fill="#FDF2F8"/>
  </g>
  <!-- Carnation 2 -->
  <g transform="translate(150, 160)">
    <circle cx="0" cy="0" r="32" fill="#F472B6"/>
    <circle cx="-10" cy="-6" r="18" fill="#EC4899"/>
    <circle cx="10" cy="-6" r="18" fill="#EC4899"/>
    <circle cx="0" cy="8" r="18" fill="#DB2777"/>
  </g>
  <!-- Carnation 3 -->
  <g transform="translate(250, 160)">
    <circle cx="0" cy="0" r="32" fill="#F472B6"/>
    <circle cx="-10" cy="-6" r="18" fill="#EC4899"/>
    <circle cx="10" cy="-6" r="18" fill="#EC4899"/>
    <circle cx="0" cy="8" r="18" fill="#DB2777"/>
  </g>
  <text x="200" y="280" font-family="'Segoe UI', Roboto, sans-serif" font-size="14" font-weight="bold" fill="#9D174D" text-anchor="middle" letter-spacing="1">PASTEL PINK CARNATIONS</text>
</svg>''',

    "white_lilies.svg": '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 300" width="100%" height="100%">
  <defs>
    <linearGradient id="lbg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#F8FAFC"/>
      <stop offset="100%" stop-color="#E2E8F0"/>
    </linearGradient>
  </defs>
  <rect width="400" height="300" fill="url(#lbg)" rx="12"/>
  <path d="M200 270 Q180 180 200 120" stroke="#15803D" stroke-width="6" fill="none" stroke-linecap="round"/>
  <!-- Lily Flower -->
  <g transform="translate(200, 110)">
    <!-- 6 Petals -->
    <path d="M0 0 C-20 -50, -40 -70, 0 -90 C40 -70, 20 -50, 0 0 Z" fill="#FFFFFF" stroke="#E2E8F0" stroke-width="2"/>
    <path d="M0 0 C50 -20, 70 -40, 90 0 C70 40, 50 20, 0 0 Z" fill="#FFFFFF" stroke="#E2E8F0" stroke-width="2"/>
    <path d="M0 0 C-50 -20, -70 -40, -90 0 C-70 40, -50 20, 0 0 Z" fill="#FFFFFF" stroke="#E2E8F0" stroke-width="2"/>
    <path d="M0 0 C-20 50, -40 70, 0 90 C40 70, 20 50, 0 0 Z" fill="#F1F5F9" stroke="#E2E8F0" stroke-width="2"/>
    <path d="M0 0 C35 35, 60 55, 60 70 C45 60, 25 35, 0 0 Z" fill="#FFFFFF" stroke="#E2E8F0" stroke-width="2"/>
    <path d="M0 0 C-35 35, -60 55, -60 70 C-45 60, -25 35, 0 0 Z" fill="#FFFFFF" stroke="#E2E8F0" stroke-width="2"/>
    <!-- Center Pistil & Stamens -->
    <circle cx="0" cy="0" r="9" fill="#84CC16"/>
    <circle cx="15" cy="-20" r="4" fill="#B45309"/>
    <circle cx="-15" cy="-20" r="4" fill="#B45309"/>
    <circle cx="25" cy="5" r="4" fill="#B45309"/>
    <circle cx="-25" cy="5" r="4" fill="#B45309"/>
  </g>
  <text x="200" y="280" font-family="'Segoe UI', Roboto, sans-serif" font-size="14" font-weight="bold" fill="#334155" text-anchor="middle" letter-spacing="1">PURE WHITE ASIATIC LILIES</text>
</svg>''',

    "wedding_centerpiece.svg": '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 300" width="100%" height="100%">
  <defs>
    <linearGradient id="wbg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#FFFBEB"/>
      <stop offset="100%" stop-color="#FEF3C7"/>
    </linearGradient>
  </defs>
  <rect width="400" height="300" fill="url(#wbg)" rx="12"/>
  <!-- Vase -->
  <path d="M160 250 L170 180 L230 180 L240 250 Z" fill="#D97706" opacity="0.8"/>
  <ellipse cx="200" cy="180" rx="30" ry="8" fill="#F59E0B"/>
  <ellipse cx="200" cy="250" rx="40" ry="10" fill="#B45309"/>
  <!-- Grand Arrangement -->
  <circle cx="200" cy="130" r="45" fill="#FDA4AF"/>
  <circle cx="155" cy="140" r="35" fill="#F43F5E"/>
  <circle cx="245" cy="140" r="35" fill="#F43F5E"/>
  <circle cx="200" cy="80" r="30" fill="#FDE047"/>
  <circle cx="140" cy="100" r="25" fill="#E2E8F0"/>
  <circle cx="260" cy="100" r="25" fill="#E2E8F0"/>
  <text x="200" y="280" font-family="'Segoe UI', Roboto, sans-serif" font-size="14" font-weight="bold" fill="#78350F" text-anchor="middle" letter-spacing="1">GRAND WEDDING ARRANGEMENT</text>
</svg>''',

    "golden_orchids.svg": '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 300" width="100%" height="100%">
  <defs>
    <linearGradient id="gobg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#FFFBEB"/>
      <stop offset="100%" stop-color="#FEF3C7"/>
    </linearGradient>
  </defs>
  <rect width="400" height="300" fill="url(#gobg)" rx="12"/>
  <path d="M130 270 Q190 200 210 70" stroke="#365314" stroke-width="5" fill="none"/>
  <circle cx="170" cy="170" r="26" fill="#FBBF24"/>
  <circle cx="200" cy="120" r="30" fill="#F59E0B"/>
  <circle cx="215" cy="70" r="18" fill="#D97706"/>
  <circle cx="200" cy="120" r="8" fill="#991B1B"/>
  <text x="200" y="280" font-family="'Segoe UI', Roboto, sans-serif" font-size="14" font-weight="bold" fill="#78350F" text-anchor="middle" letter-spacing="1">LUXURY GOLDEN ORCHIDS</text>
</svg>''',

    "blush_bouquet.svg": '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 300" width="100%" height="100%">
  <defs>
    <linearGradient id="bbg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#FFF1F2"/>
      <stop offset="100%" stop-color="#FFE4E6"/>
    </linearGradient>
  </defs>
  <rect width="400" height="300" fill="url(#bbg)" rx="12"/>
  <path d="M170 270 L195 180 M200 270 L200 170 M230 270 L205 180" stroke="#047857" stroke-width="6"/>
  <circle cx="160" cy="140" r="32" fill="#FB7185"/>
  <circle cx="240" cy="140" r="32" fill="#F43F5E"/>
  <circle cx="200" cy="100" r="38" fill="#FDA4AF"/>
  <text x="200" y="280" font-family="'Segoe UI', Roboto, sans-serif" font-size="14" font-weight="bold" fill="#881337" text-anchor="middle" letter-spacing="1">BLUSH ROMANCE BOUQUET</text>
</svg>''',

    "spring_wildflowers.svg": '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 300" width="100%" height="100%">
  <defs>
    <linearGradient id="sbg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#F0FDF4"/>
      <stop offset="100%" stop-color="#DCFCE7"/>
    </linearGradient>
  </defs>
  <rect width="400" height="300" fill="url(#sbg)" rx="12"/>
  <circle cx="150" cy="120" r="26" fill="#38BDF8"/>
  <circle cx="250" cy="120" r="26" fill="#A855F7"/>
  <circle cx="200" cy="90" r="28" fill="#FACC15"/>
  <circle cx="170" cy="160" r="24" fill="#FB7185"/>
  <circle cx="230" cy="160" r="24" fill="#34D399"/>
  <text x="200" y="280" font-family="'Segoe UI', Roboto, sans-serif" font-size="14" font-weight="bold" fill="#14532D" text-anchor="middle" letter-spacing="1">SPRING WILDFLOWERS</text>
</svg>''',

    "celebration_hamper.svg": '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 300" width="100%" height="100%">
  <defs>
    <linearGradient id="chbg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#FEF2F2"/>
      <stop offset="100%" stop-color="#FEE2E2"/>
    </linearGradient>
  </defs>
  <rect width="400" height="300" fill="url(#chbg)" rx="12"/>
  <!-- Basket -->
  <path d="M140 240 L160 170 L240 170 L260 240 Z" fill="#B45309"/>
  <circle cx="180" cy="140" r="30" fill="#DC2626"/>
  <circle cx="220" cy="140" r="30" fill="#E11D48"/>
  <circle cx="200" cy="100" r="32" fill="#EAB308"/>
  <text x="200" y="280" font-family="'Segoe UI', Roboto, sans-serif" font-size="14" font-weight="bold" fill="#991B1B" text-anchor="middle" letter-spacing="1">CELEBRATION HAMPER</text>
</svg>''',

    "heart_roses.svg": '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 300" width="100%" height="100%">
  <defs>
    <linearGradient id="hrbg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#FFF1F2"/>
      <stop offset="100%" stop-color="#FFE4E6"/>
    </linearGradient>
  </defs>
  <rect width="400" height="300" fill="url(#hrbg)" rx="12"/>
  <!-- Heart Box Shape -->
  <path d="M200 230 C120 170 120 90 170 80 C190 75 200 95 200 95 C200 95 210 75 230 80 C280 90 280 170 200 230 Z" fill="#991B1B" stroke="#E11D48" stroke-width="4"/>
  <!-- Red roses filled in heart -->
  <circle cx="170" cy="120" r="14" fill="#EF4444"/>
  <circle cx="200" cy="125" r="14" fill="#DC2626"/>
  <circle cx="230" cy="120" r="14" fill="#EF4444"/>
  <circle cx="185" cy="155" r="14" fill="#DC2626"/>
  <circle cx="215" cy="155" r="14" fill="#EF4444"/>
  <circle cx="200" cy="185" r="12" fill="#B91C1C"/>
  <text x="200" y="280" font-family="'Segoe UI', Roboto, sans-serif" font-size="14" font-weight="bold" fill="#881337" text-anchor="middle" letter-spacing="1">SCARLET ROSE HEART BOX</text>
</svg>''',

    "white_orchids.svg": '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 300" width="100%" height="100%">
  <defs>
    <linearGradient id="wobg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#F8FAFC"/>
      <stop offset="100%" stop-color="#F1F5F9"/>
    </linearGradient>
  </defs>
  <rect width="400" height="300" fill="url(#wobg)" rx="12"/>
  <!-- Pot -->
  <path d="M165 250 L175 190 L225 190 L235 250 Z" fill="#64748B"/>
  <!-- Orchid Stem -->
  <path d="M190 190 Q210 140 230 70" stroke="#166534" stroke-width="4" fill="none"/>
  <!-- White Blooms -->
  <circle cx="205" cy="150" r="22" fill="#FFFFFF" stroke="#CBD5E1" stroke-width="2"/>
  <circle cx="225" cy="100" r="24" fill="#FFFFFF" stroke="#CBD5E1" stroke-width="2"/>
  <circle cx="225" cy="100" r="6" fill="#FACC15"/>
  <circle cx="205" cy="150" r="6" fill="#FACC15"/>
  <text x="200" y="280" font-family="'Segoe UI', Roboto, sans-serif" font-size="14" font-weight="bold" fill="#334155" text-anchor="middle" letter-spacing="1">PEACEFUL WHITE ORCHIDS</text>
</svg>'''
}

dest_dir = r"C:\Users\DELL\.gemini\antigravity\scratch\flower_shop_system\static\images\flowers"
for filename, svg_code in flower_svgs.items():
    with open(os.path.join(dest_dir, filename), "w", encoding="utf-8") as f:
        f.write(svg_code.strip())

print(f"Generated {len(flower_svgs)} flower SVG assets successfully!")
