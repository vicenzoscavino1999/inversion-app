import streamlit as st

PWA_NAME = "Inversion App"
PWA_SHORT_NAME = "Inversiones"
PWA_THEME_COLOR = "#0f172a"
PWA_ICON_URL = "/app/static/icons/icon-192.png"
PWA_MANIFEST_URL = "/app/static/manifest.json"


def bootstrap():
    """Inyecta metadata PWA en el document head del cliente."""
    st.html(
        f"""
        <div id="pwa-bootstrap" style="display:none"></div>
        <script>
        (() => {{
          const ensureHeadTag = (selector, factory, apply) => {{
            let node = document.head.querySelector(selector);
            if (!node) {{
              node = factory();
              document.head.appendChild(node);
            }}
            apply(node);
          }};

          ensureHeadTag(
            'link[data-pwa="manifest"]',
            () => {{
              const link = document.createElement('link');
              link.rel = 'manifest';
              link.dataset.pwa = 'manifest';
              return link;
            }},
            (node) => {{
              node.href = '{PWA_MANIFEST_URL}';
            }},
          );

          ensureHeadTag(
            'link[data-pwa="icon"]',
            () => {{
              const link = document.createElement('link');
              link.rel = 'icon';
              link.dataset.pwa = 'icon';
              return link;
            }},
            (node) => {{
              node.href = '{PWA_ICON_URL}';
              node.sizes = '192x192';
              node.type = 'image/png';
            }},
          );

          ensureHeadTag(
            'link[data-pwa="apple-touch-icon"]',
            () => {{
              const link = document.createElement('link');
              link.rel = 'apple-touch-icon';
              link.dataset.pwa = 'apple-touch-icon';
              return link;
            }},
            (node) => {{
              node.href = '{PWA_ICON_URL}';
            }},
          );

          [
            ['theme-color', '{PWA_THEME_COLOR}'],
            ['mobile-web-app-capable', 'yes'],
            ['apple-mobile-web-app-capable', 'yes'],
            ['apple-mobile-web-app-status-bar-style', 'default'],
            ['apple-mobile-web-app-title', '{PWA_SHORT_NAME}'],
            ['application-name', '{PWA_NAME}'],
          ].forEach(([name, content]) => {{
            ensureHeadTag(
              `meta[name="${{name}}"]`,
              () => {{
                const meta = document.createElement('meta');
                meta.name = name;
                return meta;
              }},
              (node) => {{
                node.content = content;
              }},
            );
          }});
        }})();
        </script>
        """,
        width="content",
        unsafe_allow_javascript=True,
    )
