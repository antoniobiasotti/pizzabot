import openai
import json
from dotenv import load_dotenv

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
