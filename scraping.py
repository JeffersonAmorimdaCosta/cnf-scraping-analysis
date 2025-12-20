import requests
from bs4 import BeautifulSoup
import ddddocr
import urllib3
from utils import get_new_acess_keys

# Silenciar avisos de SSL
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def query_acess_key(url: str, session: requests.Session, access_key: str, ocr: ddddocr.DdddOcr) -> str | None:
    # Faz o get da página inicial
    response = session.get(url, verify=False)
    soup = BeautifulSoup(response.text, 'html.parser')

    # Pega a tag do CAPTCHA e do formulário
    img_tag = soup.find('img', id='img_captcha')
    form_tag = soup.find('form', id='frm_NFCEC_consulta_chave_acesso')

    if form_tag and img_tag:
        # Capturar a URL da imagem do CAPTCHA
        img_url = img_tag['src']
        
        # Ajustando URL relativo para absoluto
        if not img_url.startswith('http'):
            img_url = requests.compat.urljoin(url, img_url)
        
        # print(f"Baixando CAPTCHA de: {img_url}")
        
        # Response da imagem do CAPTCHA
        response_img = session.get(img_url, verify=False)

        # Usar OCR para reconhecer o CAPTCHA
        captcha_text = ocr.classification(response_img.content)

        # Preencher o payload do formulário
        payload = {
            'txt_chave_acesso': access_key,
            'txt_cod_antirobo': captcha_text,
            'btn_consulta_completa': 'Consultar'
        }

        # Preencher campos ocultos do formulário (segunraça, memória, etc)
        # print("Capturando campos ocultos...")
        for hidden in form_tag.find_all("input", type="hidden"):
            nome = hidden.get('name')
            valor = hidden.get('value')
            if nome:
                payload[nome] = valor
        
        # print("Enviando formulário...")

        # Enviar o formulário (POST) com o CAPTCHA resolvido
        final_response = session.post(url, data=payload, verify=False)

        # Salvar a resposta final em um arquivo HTML
        # with open('final_response.html', 'w', encoding='utf-8') as f:
        #     f.write(final_response.text)

        # print("Resposta salva em 'final_response.html'")

        final_soup = BeautifulSoup(final_response.text, 'html.parser')

        # label_cpf = final_soup.find('strong', string=lambda text: text and 'CPF' in text)

        total_value = final_soup.find('span', class_='totalNumb txtMax')


        # if label_cpf:
        #     return label_cpf.next_sibling.strip()

        if total_value:
            return total_value.text.strip()
        
        return None

    
def main(BASE_ACCESS_KEY: str, k: int = 1, n: int = 20) -> None:

    URL = 'http://nfe.sefaz.ba.gov.br/servicos/nfce/Modulos/Geral/NFCEC_consulta_chave_acesso.aspx'

    session = requests.Session()
    ocr = ddddocr.DdddOcr(show_ad=False)

    # Adicionar headers para parecer um navegador real (evita bloqueios simples)
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36'
    })

    # Gerar chaves baseadas no incremento k
    new_keys = get_new_acess_keys(BASE_ACCESS_KEY, k, n)
    total = 0

    for i, ak in enumerate(new_keys):
        result = query_acess_key(url=URL, session=session, access_key=ak, ocr=ocr)

        print('=' * 20, 'CHAVE DE ACESSO', i, '=' * 20)
        if result:
            print(f"Chave de Acesso Válida Encontrada: {ak} - Valor: {result}")
            total += float(result.replace(',', '.'))
        else:
            print(f"Chave de Acesso Inválida: {ak}")
        print()
    
    print('VALOR TOTAL:', 'R$', total)
    
    

if __name__ == "__main__":
    BASE_ACCESS_KEY = 'YOUR ACCESS KEY HERE'  # Substitua pela chave de acesso base
    main(BASE_ACCESS_KEY, n=30)