import streamlit as st
import requests
import os

# Configurar a URL da API (substitua pela sua URL do Render)
API_URL = os.getenv("API_URL", "http://localhost:8000")

st.set_page_config(page_title="Detector de Fake News - Brasil", page_icon="📰")

st.title("📰 Detector de Fake News - Notícias Brasileiras")

st.write("""
Verifique se uma notícia é falsa ou verdadeira usando nossa IA treinada 
especificamente para notícias brasileiras.
""")

# Entrada de texto
title = st.text_input("Título da Notícia")
content = st.text_area("Conteúdo da Notícia", height=200)

if st.button("Verificar", type="primary"):
    if title and content:
        with st.spinner("Analisando a notícia..."):
            try:
                response = requests.post(
                    f"{API_URL}/check-news",
                    json={"title": title, "content": content}
                )
                
                if response.status_code == 200:
                    result = response.json()
                    
                    # Exibir resultado
                    if result["verdict"] == "VERDADEIRO":
                        st.success(f"✅ **{result['verdict']}** - {result['message']}")
                    elif result["verdict"] == "INDETERMINADO":
                        st.warning(f"⚠️ **{result['verdict']}** - {result['message']}")
                    else:
                        st.error(f"❌ **{result['verdict']}** - {result['message']}")
                    
                    # Barra de probabilidade
                    st.progress(result["probability"])
                    st.write(f"**Probabilidade de ser falsa:** {result['probability']:.2%}")
                    
                    # Recomendações
                    if result["verdict"] != "VERDADEIRO":
                        st.info("""
                        **Recomendações:**
                        - Consulte fontes confiáveis como G1, UOL, Folha de S.Paulo
                        - Verifique em sites de fact-checking como Aos Fatos, Lupa
                        - Desconfie de notícias com título sensacionalista
                        """)
                else:
                    st.error("Erro ao verificar a notícia. Tente novamente.")
                    
            except Exception as e:
                st.error(f"Erro de conexão: {e}")
    else:
        st.warning("Por favor, insira o título e o conteúdo da notícia.")

# Seção de notícias recentes
st.divider()
if st.button("📋 Carregar Notícias Recentes"):
    with st.spinner("Carregando notícias recentes..."):
        try:
            response = requests.get(f"{API_URL}/recent-news?limit=5")
            if response.status_code == 200:
                news = response.json().get("news", [])
                
                st.subheader("Últimas Notícias Coletadas")
                for item in news:
                    with st.expander(f"{item['title']} - {item['source_name']}"):
                        st.write(f"**Fonte:** {item['source_name']}")
                        st.write(f"**Data:** {item['publish_date']}")
                        if item['source_url'] and item['source_url'].startswith('http'):
                            st.write(f"**Link:** [Acessar notícia]({item['source_url']})")
            else:
                st.error("Erro ao carregar notícias recentes.")
        except Exception as e:
            st.error(f"Erro de conexão: {e}")

# Rodapé
st.divider()
st.markdown("""
**Sobre este projeto**: 
Esta ferramenta usa inteligência artificial para detectar possíveis fake news 
em notícias brasileiras. O sistema é atualizado regularmente com novas notícias 
de fontes confiáveis.

**Aviso importante**: Esta ferramenta é um auxílio à verificação, mas não substitui 
a checagem em fontes confiáveis e agências de fact-checking.
""")