import streamlit as st
from PIL import Image, ImageDraw, ImageColor
from fpdf import FPDF
from streamlit_image_coordinates import streamlit_image_coordinates
import json
from pathlib import Path
import time

# ======================================
# CONFIGURAÇÕES INICIAIS
# ======================================
st.set_page_config(layout="wide")
st.title("🚽 Relatório de Acessibilidade (NBR 9050)")

# ======================================
# DADOS DOS AMBIENTES (EDITÁVEL)
# ======================================
AMBIENTES = {
    "Banheiro": {
        "path": "pasta_imagens/banheiro.jpg",
        "areas": {
            "Altura Descarga": {"xmin": 450, "xmax": 486, "ymin": 123, "ymax": 340, "texto": "Altura da Descarga em desacordo com a 9050. Deverá ser de no máximo 1m.", "color": "blue"},
            "Alutra Bacia": {"xmin": 297, "xmax": 411, "ymin": 206, "ymax": 246, "texto": "Altura da Bacia sem o assento em desacordo com a 9050. Deverá ser entre 43 a 45cm.", "color": "blue"},
            "Altura Assento": {"xmin": 263, "xmax": 418, "ymin": 263, "ymax": 306, "texto": "Altura da Bacia com o assento em desacordo com a 9050. Deverá ser no máximo 46cm.", "color": "blue"},
            "Barra Horizontal": {"xmin": 312, "xmax": 444, "ymin": 468, "ymax": 496, "texto": "Barra horizontal em desacordo com a 9050. Deverá ter no mínimo 80cm.", "color": "blue"},
            "Distância da barra - 40cm": {"xmin": 387, "xmax": 443, "ymin": 524, "ymax": 558, "texto": "A distância, na paralela, entre barra e o eixo da bacia deve ser de 0,40m.", "color": "blue"},
            "Altura da Barra - 75cm": {"xmin": 721, "xmax": 746, "ymin": 557, "ymax": 583, "texto": "A distância, na altura, entre barra e o piso deve ser de 75cm.", "color": "blue"},
            "Distância entre vaso e barra - 50cm": {"xmin": 658, "xmax": 692, "ymin": 579, "ymax": 599, "texto": "A distância entre a bacia sanitária e a barra deve ser de 50cm.", "color": "blue"},
            "Distância entre vaso e barra - 30cm": {"xmin": 646, "xmax": 680, "ymin": 537, "ymax": 563, "texto": "A distância entre a bacia sanitária e a barra deve ser de 30cm.", "color": "blue"},
            "Distância entre a parede e o lado externo da barra - 11cm": {"xmin": 529, "xmax": 572, "ymin": 460, "ymax": 494, "texto": "A distância máximo é de 11cm", "color": "blue"},            
            "Comprimento da barra horizontal": {"xmin": 611, "xmax": 672, "ymin": 461, "ymax": 485, "texto": "O comprimento mínimo da barra horizontal é de 80cm", "color": "blue"},            
            "Comprimento da barra vertical": {"xmin": 723, "xmax": 741, "ymin": 410, "ymax": 476, "texto": "O comprimento mínimo da barra vertical é de 70cm", "color": "blue"},            
            "Distância entre barras": {"xmin": 750, "xmax": 768, "ymin": 455, "ymax": 497, "texto": "A distância entre a barra horizotanl e vertical deverá ser de 10cm", "color": "blue"},
        }
    },
    "Em Construção": {
        "path": "pasta_imagens/cozinha.jpg",
        "areas": {
            "Construção1": {"xmin": 200, "xmax": 400, "ymin": 100, "ymax": 300, "texto": "Por que você clicou aqui? Estamos em construção", "color": "blue"},
            "Construção2": {"xmin": 500, "xmax": 700, "ymin": 150, "ymax": 350, "texto": "Ainda continua clicando??? É teimoso, em??", "color": "blue"},
        }
    }
}

# ======================================
# SISTEMA DE AUTOSALVAMENTO (NOVO)
# ======================================
SAVE_FILE = "dados_relatorio.json"

# Adicione no início do seu código (após criar SAVE_FILE)
def limpar_relatorio_completo():
    """Limpa relatório, arquivo salvo E cache do Streamlit"""

    
    # 2. Limpa o arquivo JSON
    SAVE_FILE = "dados_relatorio.json"
    if Path(SAVE_FILE).exists():
        Path(SAVE_FILE).unlink()
    
    # 3. Limpa o cache do Streamlit (importante!)
    st.cache_data.clear()  # Limpa todos os caches de dados
    st.cache_resource.clear()  # Limpa caches de recursos
    
    # 4. Feedback e recarga
    st.success("🧹 Limpeza total concluída (dados + cache)!")
    time.sleep(1)
    st.rerun()

def carregar_dados():
    """Carrega os dados salvos localmente"""
    arquivo = Path(SAVE_FILE)
    if arquivo.exists():
        with open(arquivo, 'r') as f:
            return json.load(f)
    return []

def salvar_dados():
    """Salva os dados no arquivo local"""
    with open(SAVE_FILE, 'w') as f:
        json.dump(st.session_state.relatorio, f)

# ======================================
# INICIALIZAÇÃO (COM DADOS SALVOS)
# ======================================
if "relatorio" not in st.session_state:
    st.session_state.relatorio = carregar_dados()

# ======================================
# INTERFACE PRINCIPAL
# ======================================
# Seletor de ambiente
ambiente_selecionado = st.selectbox("Selecione o ambiente:", list(AMBIENTES.keys()))

# Carrega imagem e áreas
try:
    ambiente = AMBIENTES[ambiente_selecionado]
    image = Image.open(ambiente["path"])
    
    # Desenha retângulos semitransparentes
    img_com_areas = image.copy()
    draw = ImageDraw.Draw(img_com_areas, "RGBA")
    
    for area, params in ambiente["areas"].items():
        draw.rectangle(
            [(params["xmin"], params["ymin"]), (params["xmax"], params["ymax"])],
            outline=params["color"],
            fill=(*ImageColor.getrgb(params["color"]), 20),
            width=2
        )
    
    # Mostra imagem interativa
    st.subheader(f"Inspeção: {ambiente_selecionado}")
    coordenadas = streamlit_image_coordinates(img_com_areas, key=f"coords_{ambiente_selecionado}")
    
    # Processa cliques
    if coordenadas:
        x, y = coordenadas["x"], coordenadas["y"]
        #st.write(f"📍 Coordenadas: X={x}, Y={y}")
        
        for area, params in ambiente["areas"].items():
            if (params["xmin"] <= x <= params["xmax"]) and (params["ymin"] <= y <= params["ymax"]):
                novo_item = f"{ambiente_selecionado} - {area}: {params['texto']}"
                if novo_item not in st.session_state.relatorio:
                    st.session_state.relatorio.append(novo_item)
                    salvar_dados()  # Autosalvamento
                    st.toast(f"✅ {area} adicionado")

except FileNotFoundError:
    st.error(f"Erro: Imagem não encontrada em '{ambiente['path']}'")

# ======================================
# RELATÓRIO E AÇÕES
# ======================================
st.divider()
st.subheader("📋 Itens no Relatório")

# Lista de itens com opção de remoção
for i, item in enumerate(st.session_state.relatorio):
    col1, col2 = st.columns([0.9, 0.1])
    with col1:
        st.write(f"- {item}")
    with col2:
        if st.button("🗑️", key=f"del_{i}"):
            st.session_state.relatorio.pop(i)
            salvar_dados()
            st.rerun()

# Botões principais
col1, col2 = st.columns(2)
with col1:
    # No botão de limpar:
    if st.button("🧹 Limpar Tudo", type="primary", key="limpar_tudo"):
        st.session_state.relatorio = []
        limpar_relatorio_completo()
        st.success("Relatório limpo com sucesso!")
        time.sleep(1)  # Pequeno delay para exibir a mensagem
        st.rerun()  # Usamos st.rerun() normal agora

with col2:
    if st.session_state.relatorio:
        # Geração do PDF
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.cell(200, 10, txt="RELATÓRIO DE ACESSIBILIDADE", ln=True)
        
        for item in st.session_state.relatorio:
            pdf.multi_cell(0, 10, txt=item)
        
        pdf_bytes = pdf.output(dest="S").encode("latin1")
        st.download_button(
            label="📄 Gerar PDF",
            data=pdf_bytes,
            file_name="relatorio_acessibilidade.pdf",
            mime="application/pdf",
        )
    else:
        st.warning("Adicione itens antes de gerar o PDF")
