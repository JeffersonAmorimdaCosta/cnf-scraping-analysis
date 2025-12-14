import requests
from bs4 import BeautifulSoup
import ddddocr
import urllib3

# Silenciar avisos
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

URL = 'http://nfe.sefaz.ba.gov.br/servicos/nfce/Modulos/Geral/NFCEC_consulta_chave_acesso.aspx'
ACESS_KEY = 'YOUR ACCESS KEY HERE'

session = requests.Session()
ocr = ddddocr.DdddOcr(show_ad=False)

# Adicionar Headers para parecer um navegador real (evita bloqueios simples)
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36'
})

print("Acessando página de login...")

# Faz o get da página inicial
response = session.get(URL, verify=False)
soup = BeautifulSoup(response.text, 'html.parser')

# Pega a tag do CAPTCHA e do formulário
img_tag = soup.find('img', id='img_captcha')
form_tag = soup.find('form', id='frm_NFCEC_consulta_chave_acesso')

if form_tag and img_tag:
    # Capturar a URL da imagem do CAPTCHA
    img_url = img_tag['src']
    
    # Ajustando URL relativo para absoluto
    if not img_url.startswith('http'):
        img_url = requests.compat.urljoin(URL, img_url)
    
    print(f"Baixando CAPTCHA de: {img_url}")
    
    # Response da imagem do CAPTCHA
    response_img = session.get(img_url, verify=False)

    # Usar OCR para reconhecer o CAPTCHA
    captcha_text = ocr.classification(response_img.content)

    # Preencher o payload do formulário
    payload = {
        'txt_chave_acesso': ACESS_KEY,
        'txt_cod_antirobo': captcha_text,
        'btn_consulta_completa': 'Consultar'
    }

    # Preencher campos ocultos do formulário (segunraça, memória, etc)
    print("Capturando campos ocultos...")
    for hidden in form_tag.find_all("input", type="hidden"):
        nome = hidden.get('name')
        valor = hidden.get('value')
        if nome:
            payload[nome] = valor
    
    print("Enviando formulário...")

    # Enviar o formulário (POST) com o CAPTCHA resolvido
    final_response = session.post(URL, data=payload, verify=False)

    # Salvar a resposta final em um arquivo HTML
    with open('final_response.html', 'w', encoding='utf-8') as f:
        f.write(final_response.text)

    print("Resposta salva em 'final_response.html'")