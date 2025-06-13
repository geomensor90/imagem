import streamlit as st
from PIL import Image, ImageDraw, ImageColor
from fpdf import FPDF
from streamlit_image_coordinates import streamlit_image_coordinates

# Configuração
st.set_page_config(layout="wide")
st.title("🔧 Relatório de Inspeção")

# 1. Dicionário de ambientes (IMPORTANTE: ajuste os caminhos das imagens!)
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

# 2. Inicializar relatório único
if "relatorio" not in st.session_state:
    st.session_state.relatorio = []

# 3. Seletor de ambiente
ambiente_selecionado = st.selectbox("Selecione o ambiente:", list(AMBIENTES.keys())) 

# 4. Carregar imagem e desenhar áreas clicáveis
try:
    ambiente = AMBIENTES[ambiente_selecionado]
    image = Image.open(ambiente["path"])
    
    # Criar imagem com retângulos semitransparentes
    image_with_rectangles = image.copy()
    draw = ImageDraw.Draw(image_with_rectangles, "RGBA")
    
    for area, params in ambiente["areas"].items():
        draw.rectangle(
            [(params["xmin"], params["ymin"]), (params["xmax"], params["ymax"])],
            outline=params["color"],
            fill=(*ImageColor.getrgb(params["color"]), 20),  # 50 = opacidade (0-255)
            width=2
        )
    
except FileNotFoundError:
    st.error(f"Erro: Imagem não encontrada em '{ambiente['path']}'")
    st.stop()

# 5. Mostrar imagem e capturar cliques
st.subheader(f"Clique nos itens problemáticos ({ambiente_selecionado})")
coordinates = streamlit_image_coordinates(image_with_rectangles, key=f"coords_{ambiente_selecionado}")
if coordinates:
    x, y = coordinates["x"], coordinates["y"]
    st.write(f"📍 Coordenadas do clique: X={x}, Y={y}")  # Mostra as coordenadas brutas
    
    # Verifica se está dentro de alguma área (opcional)
    for area, params in ambiente["areas"].items():
        if (params["xmin"] <= x <= params["xmax"]) and (params["ymin"] <= y <= params["ymax"]):
            st.write(f"✅ Área identificada: {area} (X={params['xmin']}-{params['xmax']}, Y={params['ymin']}-{params['ymax']})")
if coordinates:
    x, y = coordinates["x"], coordinates["y"]
    for area, params in ambiente["areas"].items():
        if (params["xmin"] <= x <= params["xmax"]) and (params["ymin"] <= y <= params["ymax"]):
            item_texto = f"{ambiente_selecionado} - {area}: {params['texto']}"
            if item_texto not in st.session_state.relatorio:
                st.session_state.relatorio.append(item_texto)
                st.toast(f"✅ Item adicionado: {area}")

# 6. Mostrar relatório atual
st.divider()
st.subheader("📋 Itens no Relatório")

if st.session_state.relatorio:
    for item in st.session_state.relatorio:
        st.write(f"- {item}")
else:
    st.info("Nenhum item adicionado ainda.")

# 7. Botões de ação
col1, col2 = st.columns(2)
with col1:
    if st.button("🧹 Limpar Relatório", type="primary"):
        st.session_state.relatorio = []
        st.rerun()
        
from io import BytesIO
import base64

with col2:


    # Substitua a parte do PDF no seu código por:
    if st.session_state.relatorio:
        # [...] (código anterior igual)
        if st.button("📄 Gerar PDF", type="secondary"):
            if st.session_state.relatorio:
                pdf = FPDF()
                pdf.add_page()
                pdf.set_font("Arial", size=12)
                pdf.cell(200, 10, txt="RELATÓRIO DE INSPEÇÃO", ln=True)
                
                for item in st.session_state.relatorio:
                    pdf.cell(200, 10, txt=item, ln=True)
                
                # Gera o PDF em memória para download
                pdf_bytes = pdf.output(dest="S").encode("latin1")
                st.download_button(
                    label="⬇️ Baixar PDF",
                    data=pdf_bytes,
                    file_name="relatorio_inspecao.pdf",
                    mime="application/pdf",
                )
            else:
                st.warning("Adicione itens antes de gerar o PDF.")