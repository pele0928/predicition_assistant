import openai
import json
import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente do arquivo .env
load_dotenv()

# Configurar a chave da API
openai.api_key = os.getenv("OPENAI_API_KEY")

# Especificar os caminhos dos arquivos JSON a partir das variáveis de ambiente
caminhos_arquivos_json = [
    os.getenv("JSON_FILE_1")
]

# Função para ler e validar múltiplos arquivos JSON
def ler_arquivos_json(caminhos):
    dados_todos_arquivos = []
    for caminho in caminhos:
        try:
            with open(caminho, 'r', encoding='utf-8') as arquivo:
                dados = json.load(arquivo)
                dados_todos_arquivos.append(dados)
        except json.JSONDecodeError as e:
            print(f"Erro ao decodificar o JSON em {caminho}: {e}")
        except FileNotFoundError:
            print(f"Arquivo não encontrado: {caminho}")
        except Exception as e:
            print(f"Ocorreu um erro ao ler {caminho}: {e}")
    return dados_todos_arquivos

# Função para gerar o prompt específico
def gerar_prompt(transcricao, dados_json):
    prompt = (
        "Você é um engenheiro de dados e está buscando predições nas transcrições de uma ligação.\n\n"
        "Com base na análise do arquivo JSON, texto de transcrição e sua base de conhecimento de IA, identifique se os itens do checklist do Json foram realizados durante o atendimento, respondendo com 1 para FOI REALIZADO e 0 para NÃO REALIZOU.\n\n"
        "Para cada item que for identificado como realizado prediction = (1), forneça a evidência exata do trecho, sem mudar nenhuma palavra, pontuação ou acentuação. O trecho deve ser exatamente igual ao da transcrição e capaz de ser localizado posteriormente no campo \"excerpt\".\n"
        "Certifique-se de que cada item tenha um trecho único, relacionado exclusivamente à etapa especificada, sem reutilizar o mesmo trecho para múltiplos itens.\n"
        "Frases como 'minutinho', 'só momentinho', 'rapidinho', 'vou estar te atendendo', entre outras, devem ser evitadas. Verifique a precisão e clareza na pronúncia da fala do operador em cada transcrição de chamada."
        "\"saudacao\": {\n"
        "    \"hvoiceKey\": \"01 - Abertura | 01 - Recepcionou O Cliente | 03 - Saudação\",\n"
        "    \"prediction\": 0,\n"
        "    \"excerpt\": \"null\"\n"
        "},\n\n"
        "Responda apenas com um JSON no seguinte formato.\n"
        "Não envie nada além de um JSON estruturado.\n"
        "Não coloque 'json' antes da resposta.\n"
        "Exemplo:\n"
        "{\n"
        "    \"saudacao\": {\n"
        "        \"hvoiceKey\": \"01 - Abertura | 01 - Recepcionou O Cliente | 03 - Saudação\",\n"
        "        \"prediction\": 1,\n"
        "        \"excerpt\": \"bom dia\"\n"
        "    },\n"
        "    \"identificacao_operador\": {\n"
        "        \"hvoiceKey\": \"01 - Abertura | 01 - Recepcionou O Cliente | 02 - Apresentação Do Operador\",\n"
        "        \"prediction\": 0,\n"
        "        \"excerpt\": \""
        "    },\n"
        "    \"solicita_cpf_cpnj\": {\n"
        "        \"hvoiceKey\": \"01 - Abertura | 02 - Dados Cadastrais | 04 - Confirmação Cpf\",\n"
        "        \"prediction\": 0,\n"
        "        \"excerpt\": \"\"\n"
        "    },\n"
        "    \"encerramento_padrao\": {\n"
        "        \"hvoiceKey\": \"04 - Finalizações | 08 - Encerramento Adequado\"\n"
        "        \"prediction\": 1,\n"
        "        \"excerpt\": \"agradeço o contato, tenha um bom dia\"\n"
        "    },\n"
        "Checklist do Atendimento:\n"
        "Com base na conversa abaixo, classifique o \"attendance_type\".\n"
        "Caso não encontre um tipo de atendimento adequado entre os citados, retorne null. (Ex: \"attendance_type\": \"null\")\n"
        "Não coloque 'json' antes da resposta.\n"
        "Siga rigorosamente o formato abaixo e não omita nenhuma chave ou valor.\n"
        f"Transcrição da ligação:\n\n{transcricao}\n\n"
    )
    return prompt

# Função para obter a resposta da API OpenAI
def obter_resposta(prompt):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Você é SÊNIOR em Engenharia de Dados."},
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message['content']
    except openai.error.OpenAIError as e:
        print(f"Ocorreu um erro ao chamar a API do OpenAI: {e}")
    except openai.error.RateLimitError as e:
        print(f"Erro de limite de taxa: {e}")
    except openai.error.InvalidRequestError as e:
        print(f"Erro de requisição inválida: {e}")
    except openai.error.AuthenticationError as e:
        print(f"Erro de autenticação: {e}")
    except openai.error.APIConnectionError as e:
        print(f"Erro de conexão com a API: {e}")
    except Exception as e:
        print(f"Ocorreu um erro inesperado: {e}")
    return None

# Função para salvar a resposta em um arquivo TXT
def salvar_resposta_txt(resposta, nome_arquivo):
    try:
        with open(nome_arquivo, 'w', encoding='utf-8') as arquivo:
            arquivo.write(resposta)
        print(f"Resposta salva em {nome_arquivo}")
    except Exception as e:
        print(f"Erro ao salvar a resposta em {nome_arquivo}: {e}")

# Função principal
def main():
    # Carrega os dados dos arquivos JSON
    dados = ler_arquivos_json(caminhos_arquivos_json)
    if not dados:
        print("Não foi possível ler os dados dos arquivos JSON.")
        return

    # Assumindo que a primeira entrada contém as transcrições e a segunda contém os passos de verificação
    # Colocar o texto de transcrição para validar os passos especificados no Prompt e Json de validação
    transcricao = "vivo casa marcos boa tarde boa tarde é da segundo da casa vivo é vivo casa como eu posso te ajuda é eu precisaria fala com o setor de pediu o segundo a compra de telefone eu tenho um seguro e precisaria utiliza esse seguro tá e você precisa pra qual tipo de serviço é desobstrução de um vaso sanitário tá qual que é o número do seu cpf é 2 9 3 3 1 7 meia 5 8 00 tá qual o seu nome completo josé francisco teixeira josé qual o telefone pra contato com você 4 do 3 meia 8 4 do meia meia 4 ou 4 3 meia 8 2 9 5 3 qual que é o ddd 11 tá esses 2 telefones são fixos senhor os 2 telefones são fixos ou é telefones telefones a esse telefone que eu dei é os 2 são 2 fixos tá você utiliza email qual é seu email por favor não não não tenho email não tem tá qual que é o endereço cadastrado da é rua erineu ferreira da silva 1 3 2 qual que é o bairro e a cidade qual é o que bairro e a cidade é são bernardo campo é rua de ramos ok tem algum complemento a casa ou não tá sabe o número do cep é 09621 029 09 6 2 1 020 é vamos lá josé com relação ao atendimento de encanador lembrando que você pode utiliza 4 vezes ao ano o atendimento vivo casa independente de qual seja o atendimento tá sendo gelador eletricista ou chaveiro né né a gente consegue agenda esse atendimento pra amanhã pra amanhã é que horas seria aí você pode defini período manhã entre 8 e meio dia ou a tarde de 13 ás 18 qual você prefere é eu vô dá eu tô na 4ª da tarde é das 13 ás 18 né isso então eu te passa o protocolo tá você pode anota o vai passa o que o protocolo aí o que que é isso né moça protocolo do atendimento né a a protocolo olha a ligação tá tão ruim que a gente não consegue entende tá protocolo qual que é o protocolo protocolo um 01 um 01 final meia 5 3 12 meia 5 3 1 final 12 então espera então seu seu colet um 01 meia 5 3 12 isso correto josé bom agora me me tira uma dúvida olha você não sabe o bairro que eu tomei pra pra consegui fala com vocês qual é telefone que eu tenho que chama quando a gente necessita fala um d d o encanador eletro ciclo qual que é o telefone telefone é esse que você ligou agora deixa eu só confirma aqui que eu já te falo pera que aí também você pode solicita pelo whatsapp tá o atendimento é esse telefone que que liguei é o 0800 025 025 90 25 98 20 isso tá eu tenho anotado isso aí mais isso foi caiu no banco do brasil você olha se não chega sabe o horror que foi viu tá bom então fica marcado pra amanhã dia 10 né dia na 9 amanhã 9 do santos santos a 9 mas amanhã são paulo é feriado é amanhã é feriado né mas a gente continua com fluxo de agendamento tá tá então eu quero vamos lá dia 9 do 7 de 24 a que horas das 13 13 até 18 período tarde tarde 18 tá então quem você sabe quem da onde vem ou quem vem ainda ainda não porque a gente acabo de abri chamado mais você vai recebe por sms no te pra que você não tenha um telefone celular só o fixo né né celular eu tenho se você quiser pode fala o celular que aí você recebe mensagem com o nome do técnico e a previsão de atendimento o telefone celular deixa eu te te passa ele então é 11 sim 9 9 sim 5 8 sim 7 2 1 3 meia 1 3 meia ddd 11 deixa eu só o queira aqui porque a gente envia pra você por sms mensagens com o nome do técnico informações quando ele tiver a caminho tá então eu eu devo recebe é sms amanhã amanhã no dia da visita isso mesmo tá tá no dia da visita só só uma ótima informação desculpa é amanhã no momento da visita tem que ter alguém maior de 18 anos pra recebe o técnico e qualquer eu vô lhe dá você mesmo tá e qualquer atualização nossa central retorna contato via telefone com você tá correto correto esse agora então é bom seu nome é marcos marcos marcos então eu tô aguardando não dá furo não né eu sei é eu usei encanador pra faze acho que uma troca de de torneira alguma coisa assim eu fiquei satisfeito entendeu agora aqui já é um pouquinho mais né acho que tem que querer o vaso não sei como tem que faze aí tá deixa eu explica uma coisa josé o que é importante que você falo a parte do desentupimento que a gente tem é um desentupimento sem maquinário tá então é só um desentupimento considerado simples agora se você precisa de algum maquinário aí você vai ter que faze de forma particular tá tá a deixa eu fala uma coisa esse equipamento que o vaso tem não é vamos dizer nada de joga nada de coisa é pelas pelo de jetos que que foram acumulando acho que subiu né aí geralmente como que é feito a supción como que é feita é isso que eu tô te dizendo no caso ele vai ter um equipamento pra faze o atendimento só que é um equipamento simples não é um maquinário de sucção é isso que eu tô te dizendo entende agora se for precisa de um maquinário de sucção você vai ter que contrata alguma empresa especializada que tenha esse equipamento que a gente não tem aqui com gente é eu eu queria que seja coisa simples alguma coisa que mara mara que seja simples que ele não precisa também né de maquinário é tá então eu tô aguardando amanhã das 13 18 pra chamado de vocês combinado josé basicamente é isso ajudo em algo mais não no momento satisfeito tudo bem uma outra questão que eu queria te passa é o telefone do whatsapp se você preferi anota que aí você pode agenda o atendimento pelo whatsapp ou fala sobre qualquer atendimento pelo whatsapp tá é deixa eu vê deixa eu abri aqui explica um pouquinho você lembra esse telefone do que que é é da central vivo casa também porque você tem 2 opções você pode liga aqui nesse telefone 025 9 8 20 né ou também acionar pelo whatsapp sem precisa liga na central entendeu a certo e o telefone a ser chamado qual que é o telefone do whatsapp é 11 9 34 5 6 34 5 5 6 final 10 7 0 10 7 0 não eu tenho feito chama vocês viu do jeito que a gente tá fazendo mas foi foi difícil de consegui mas já que localizamos tudo se quiser deixa eu aí combinado combinado então josé tá marcos obrigado por nada central vivo casa permanece a disposição viu uma ótima tarde muito obrigado tchau tchau"

    # Gerar o prompt com os dados carregados
    prompt = gerar_prompt(transcricao, dados)

    resposta = obter_resposta(prompt)
    if resposta:
        print(resposta)
        # Salva a resposta em um arquivo TXT
        salvar_resposta_txt(resposta, 'resposta_analise.txt')
    else:
        print("Não foi possível obter uma resposta da API.")

if __name__ == "__main__":
    main()