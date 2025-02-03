import openai
import json
import gradio as gr
from dotenv import load_dotenv
from langchain.chat_models import ChatOpenAI
from langchain.schema import ChatMessage

load_dotenv()

# Configurar a chave da API da OpenAI
openai.api_key = os.getenv("OPENAI_API_KEY")

# Função para carregar as informações da pizzaria de um arquivo JSON
def carregar_informacoes_pizzaria():
    with open('config_pizzaria.json', 'r', encoding='utf-8') as file:
        return json.load(file)

def carregar_template_contexto():
    with open('context_template.txt', 'r', encoding='utf-8') as file:
        return file.read()

# Função para carregar o contexto com informações dinâmicas
def getContexto():
    info = carregar_informacoes_pizzaria()
    template_contexto = carregar_template_contexto()
    cardapio_str = ', '.join(info['cardapio'].keys())

    contexto = template_contexto.format(
        nome=info['nome'],
        endereco=info['endereco'],
        horario_funcionamento=info['horario_funcionamento'],
        telefone=info['telefone'],
        email=info['email'],  
        site=info['site'],    
        cardapio=cardapio_str,
        promocoes=info['promocoes'],
        forma_pagamento=", ".join(info['forma_pagamento']),
        taxa_entrega=info['taxa_entrega']
    )

    return contexto

def start_chat(openai_api_key):
    if not openai_api_key:
        return [], "Por favor, insira sua chave da API."

    # Inicializa as mensagens com uma mensagem do assistente
    messages = [("assistant", "Fala, beleza? Como posso te ajudar? Pergunte sobre nossa pizzaria!")]
    return messages, ""


# Função para fazer uma pergunta ao ChatGPT com informações dinâmicas
def pergunta_chatgpt(pergunta, contexto):
    messages = [
        {"role": "system", "content": contexto}
    ]
    
    messages.append({"role": "user", "content": pergunta})
    resposta = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages,
        max_tokens=250,
        temperature=0.3,
        #top_p=0.9,        # Amostragem de núcleo
        #n=2,              # Número de respostas desejadas
        #stop=["\n"],      # Parar a resposta ao encontrar uma nova linha
    )
    resposta_content = resposta.choices[0].message['content'].strip()
    print(f"Assistente: {resposta_content}\n")
    messages.append({"role": "assistant", "content": resposta_content})


# Função para gerar a resposta do chatbot com contexto da pizzaria
def chatbot_response(messages, user_input, openai_api_key, model="gpt-3.5-turbo", temperature=0.3, max_tokens=250):
    try:
        if not openai_api_key:
            return messages, "", "Por favor, insira a chave da API."

        # Inicializa o modelo de linguagem com a chave da API da OpenAI e parâmetros personalizados
        llm = ChatOpenAI(
            openai_api_key=openai_api_key,
            model=model,          # Define o modelo
            temperature=temperature,  # Define a temperatura
            max_tokens=max_tokens     # Define o número máximo de tokens
        )

        # Adiciona a mensagem do usuário ao histórico
        messages.append(("user", user_input))

       # Converte as mensagens para o formato esperado e adiciona o contexto
        conversation = [ChatMessage(role="system", content=contexto)] + [ChatMessage(role=msg[0], content=msg[1]) for msg in messages]

        # Gera a resposta
        response = llm(conversation)

        # Adiciona a resposta do assistente ao histórico
        messages.append(("assistant", response.content))

        return messages, "", ""  # Retorna as mensagens atualizadas e limpa o input
    except Exception as e:
        return messages, "", f"Erro: {str(e)}"

def main():
    if not openai.api_key:
        print("Erro: A chave da API OpenAI não está configurada.")
        return
    print("Seja bem-vindo à Pizzaria BOT. Como posso te ajudar?")
    contexto = getContexto()
    while True:
        pergunta = input("Você: ")
        if pergunta.lower() in ['sair', 'exit', 'quit']:
            print("Obrigado! Volte Sempre")
            break
        pergunta_chatgpt(pergunta, contexto)

if __name__ == "__main__":
    main()
