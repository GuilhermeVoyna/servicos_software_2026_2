import os
import gradio as gr 
import requests

ANALISE_URL = os.getenv("ANALISE_URL", "http://analise-service:8081")
SERVER_PORT = int(os.getenv("VISAO_PORT", "7861"))

def analisa_imagem(imagem_path):
    if imagem_path is None:
        return "Nenhuma imagem enviada"

    nome = os.path.basename(imagem_path)
    with open(imagem_path, "rb") as f:
        files = {"file": (nome, f, "image/png")}
        try:
            r = requests.post(
                f"{ANALISE_URL}/analisar", files=files, timeout=600
            )
        except requests.RequestException as e:
            return f"Erro de conexao: {e}"

    if r.status_code != 200:
        return f"Erro no servidor: {r.status_code}"

    dados = r.json()
    return (
        f"Rotulo gerado pela IA: {dados.get('rotulo')}\n"
        f"Confianca: {dados.get('confianca')}\n"
        f"Armazenamento: {dados.get('status_db')}"
    )

demo = gr.Interface(
    fn= analisa_imagem,
    inputs = gr.Image(type="filepath", label = "Envie uma imagem"),
    outputs = gr.Textbox(label="Resultado da IA e do banco"),
)

if __name__ == "__main__":
    demo.launch(server_name = "0.0.0.0", server_port = SERVER_PORT)