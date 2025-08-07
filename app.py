import streamlit as st
from PIL import Image, ImageDraw, ImageFont
from openpyxl import load_workbook
import pandas as pd
import os
import tempfile
import zipfile
from io import BytesIO

def gerar_cartazes(planilha_path, imagem_base_path, pasta_saida):
    """Função que encapsula o código original de geração de cartazes"""
    
    os.makedirs(pasta_saida, exist_ok=True)
    wb = load_workbook(planilha_path)
    ws = wb.active

    # Fontes (mantendo as configurações originais)
    try:
        fonte_pequena = ImageFont.truetype("arial.ttf", 14)
        fonte_media = ImageFont.truetype("arial.ttf", 35)
        fonte_media_b = ImageFont.truetype("arialbd.ttf", 28)
        fonte_vista = ImageFont.truetype("arialbd.ttf", 26)
        fonte_parcela = ImageFont.truetype("arialbd.ttf", 38)
        fonte_p = ImageFont.truetype("arialbd.ttf", 20)
        fonte_a = ImageFont.truetype("arialbd.ttf", 40)
        fonte_valor = ImageFont.truetype("arialbd.ttf", 85)
        fonte_valor_de = ImageFont.truetype("arialbd.ttf", 70)
    except OSError:
        # Fallback para fontes padrão se Arial não estiver disponível
        fonte_pequena = ImageFont.load_default()
        fonte_media = ImageFont.load_default()
        fonte_media_b = ImageFont.load_default()
        fonte_vista = ImageFont.load_default()
        fonte_parcela = ImageFont.load_default()
        fonte_p = ImageFont.load_default()
        fonte_a = ImageFont.load_default()
        fonte_valor = ImageFont.load_default()
        fonte_valor_de = ImageFont.load_default()

    cartazes_gerados = []
    
    for i, row in enumerate(ws.iter_rows(min_row=2, values_only=True), start=1):
        codigo, descricao, preco_de, preco_por, parcela, filial, Defeito, Tratativa, Armazem = row

        img = Image.open(imagem_base_path).convert("RGB")
        draw = ImageDraw.Draw(img)

        # Código original mantido exatamente igual
        draw.text((85, 350), "DE :", font=fonte_media_b, fill="black")
        
        preco_de_txt = f"{preco_de:,.2f}".replace('.', ',')
        draw.text((150, 320), preco_de_txt, font=fonte_valor_de, fill="black")
        draw.line([(150, 390), (400, 320)], fill="red", width=5)
        draw.line([(146, 326), (371, 400)], fill="red", width=5)

        draw.text((47, 430), "POR :", font=fonte_media_b, fill="black")
        
        preco_por_txt = f"{preco_por:,.2f}".replace('.', ',')
        draw.text((141, 415), preco_por_txt, font=fonte_valor, fill="red")

        draw.text((425, 500), "À VISTA", font=fonte_vista, fill="black")
        draw.text((44 , 542), "OU 10X\nNO CARTÃO :", font=fonte_p, fill="black")
        
        parcela_txt = f"{parcela:,.2f}".replace('.', ',')
        draw.text((180 , 550), parcela_txt, font=fonte_parcela, fill="red")

        draw.text((24, 679), f"FILIAL-{filial}", font=fonte_pequena, fill="black")
        draw.text((24, 706), str(codigo), font=fonte_pequena, fill="black")
        draw.text((140, 706), str(descricao)[:55], font=fonte_pequena, fill="black")
        draw.text((27, 730), str(Defeito), font=fonte_pequena, fill="black")
        draw.text((134, 250), str(Tratativa), font=fonte_a, fill="black")
        draw.text((380, 679), str(Armazem), font=fonte_pequena, fill="black")

        nome_arquivo = f"{pasta_saida}/cartaz_{str(codigo)}.png"
        img.save(nome_arquivo)
        cartazes_gerados.append(nome_arquivo)
        
    return cartazes_gerados

def gerar_pdf(pasta_saida):
    """Função que encapsula o código original de geração do PDF"""
    
    arquivos_png = sorted([f for f in os.listdir(pasta_saida) if f.endswith('.png')])
    imagens = []

    for arquivo in arquivos_png:
        caminho_imagem = os.path.join(pasta_saida, arquivo)
        img = Image.open(caminho_imagem).convert('RGB')
        imagens.append(img)

    if imagens:
        caminho_pdf = os.path.join(pasta_saida, 'cartazes_unificados.pdf')
        imagens[0].save(caminho_pdf, save_all=True, append_images=imagens[1:])
        return caminho_pdf
    else:
        return None

def main():
    st.set_page_config(
        page_title="Gerador de Cartazes",
        page_icon="🏷️",
        layout="centered"
    )
    
    st.title("🏷️ Gerador de Cartazes de Preço")
    st.markdown("---")
    
    # Upload da planilha
    st.subheader("📊 Upload da Planilha")
    uploaded_file = st.file_uploader(
        "Selecione o arquivo Excel (.xlsx)",
        type=['xlsx'],
        help="Faça upload da planilha com os dados dos produtos"
    )
    
    # Upload da imagem base
    st.subheader("🖼️ Upload da Imagem Base")
    uploaded_image = st.file_uploader(
        "Selecione a imagem base do cartaz (.png)",
        type=['png'],
        help="Faça upload da imagem modelo que será usada como base"
    )
    
    if uploaded_file is not None and uploaded_image is not None:
        
        # Criar diretórios temporários
        with tempfile.TemporaryDirectory() as temp_dir:
            
            # Salvar arquivos temporariamente
            planilha_path = os.path.join(temp_dir, "planilha.xlsx")
            imagem_path = os.path.join(temp_dir, "modelo.png")
            pasta_saida = os.path.join(temp_dir, "cartazes_prontos")
            
            with open(planilha_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            
            with open(imagem_path, "wb") as f:
                f.write(uploaded_image.getbuffer())
            
            # Mostrar preview da planilha
            try:
                wb = load_workbook(planilha_path)
                ws = wb.active
                
                st.subheader("📋 Preview dos Dados")
                
                # Definir os cabeçalhos esperados
                headers = ["código", "descrição", "preço_de", "preço_por", "parcela", "filial", "Defeito", "Tratativa", "Armazém"]
                
                # Criar uma lista com os dados da planilha
                dados = []
                for row in ws.iter_rows(min_row=2, max_row=6, values_only=True):  # Mostrar apenas 5 linhas
                    dados.append(row)
                
                # Mostrar tabela
                if dados:
                    import pandas as pd
                    df_preview = pd.DataFrame(dados, columns=headers)
                    st.dataframe(df_preview)
                    total_rows = ws.max_row - 1  # -1 porque não contamos o cabeçalho
                    st.info(f"Total de produtos na planilha: {total_rows}")
                    
                    # Botão para gerar cartazes
                    if st.button("🚀 Gerar Cartazes", type="primary"):
                        
                        with st.spinner("Gerando cartazes..."):
                            try:
                                # Gerar cartazes
                                cartazes_gerados = gerar_cartazes(planilha_path, imagem_path, pasta_saida)
                                
                                if cartazes_gerados:
                                    st.success(f"✅ {len(cartazes_gerados)} cartazes gerados com sucesso!")
                                    
                                    # Gerar PDF
                                    with st.spinner("Criando PDF..."):
                                        caminho_pdf = gerar_pdf(pasta_saida)
                                    
                                    if caminho_pdf:
                                        st.success("📄 PDF gerado com sucesso!")
                                        
                                        # Mostrar preview do PDF
                                        st.subheader("👀 Visualizar PDF")
                                        
                                        with open(caminho_pdf, "rb") as pdf_file:
                                            pdf_bytes = pdf_file.read()
                                            
                                            # Botão de download
                                            st.download_button(
                                                label="📥 Baixar PDF dos Cartazes",
                                                data=pdf_bytes,
                                                file_name="cartazes_unificados.pdf",
                                                mime="application/pdf",
                                                type="primary"
                                            )
                                            
                                            # Mostrar PDF incorporado
                                            st.markdown("### Preview do PDF:")
                                            st.write("Clique no botão acima para baixar o arquivo PDF completo.")
                                        
                                        # Opção de baixar cartazes individuais em ZIP
                                        st.subheader("📦 Download Individual")
                                        
                                        # Criar ZIP com todos os PNGs
                                        zip_buffer = BytesIO()
                                        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                                            for cartaz in cartazes_gerados:
                                                zip_file.write(cartaz, os.path.basename(cartaz))
                                        
                                        zip_buffer.seek(0)
                                        
                                        st.download_button(
                                            label="📥 Baixar Cartazes Individuais (ZIP)",
                                            data=zip_buffer.getvalue(),
                                            file_name="cartazes_individuais.zip",
                                            mime="application/zip"
                                        )
                                    
                                    else:
                                        st.error("❌ Erro ao gerar PDF")
                                else:
                                    st.error("❌ Nenhum cartaz foi gerado")
                                    
                            except Exception as e:
                                st.error(f"❌ Erro ao processar arquivos: {str(e)}")
                
                else:
                    st.warning("⚠️ Planilha vazia ou sem dados válidos")
                    
            except Exception as e:
                st.error(f"❌ Erro ao ler planilha: {str(e)}")
    
    else:
        st.info("👆 Faça upload da planilha Excel e da imagem base para começar")
        
        # Instruções
        with st.expander("📖 Instruções de Uso"):
            st.markdown("""
            **Como usar este app:**
            
            1. **Upload da Planilha**: Faça upload do arquivo Excel (.xlsx) contendo os dados dos produtos
            2. **Upload da Imagem**: Faça upload da imagem modelo (.png) que será usada como base dos cartazes
            3. **Visualizar**: Confira os dados da planilha na tabela de preview
            4. **Gerar**: Clique em "Gerar Cartazes" para processar os dados
            5. **Baixar**: Faça download do PDF unificado ou dos cartazes individuais em ZIP
            
            **Formato esperado da planilha:**
            - Coluna A: código
            - Coluna B: descrição  
            - Coluna C: preço_de
            - Coluna D: preço_por
            - Coluna E: parcela
            - Coluna F: filial
            - Coluna G: Defeito
            - Coluna H: Tratativa
            - Coluna I: Armazém
            """)

if __name__ == "__main__":
    main()