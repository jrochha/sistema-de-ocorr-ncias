import requests
import base64
import os
import sqlite3

from flask import Flask, render_template, request, send_file, redirect, url_for, flash
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from datetime import datetime
from zoneinfo import ZoneInfo

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "chave-dev-trocar")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PDF_DIR = os.path.join(BASE_DIR, "static", "pdfs")
os.makedirs(PDF_DIR, exist_ok=True)
DB_PATH = os.path.join(BASE_DIR, "ocorrencias.db")
LOGO_PATH = os.path.join(BASE_DIR, "static", "logo.png")

PROFESSORES = sorted([
    "Prof. Ana Maria de Lima", "Prof. Alliny Rodrigues Peixe", "Prof. Bibiana Maria Bispo", "Danielly Furlaneto Firmino - Assist. Adm.",
    "Prof. Evanilda de Souza Trindade", "Prof. Fabiola de Oliveira Herbella", "Prof. Felipe Paulo de Souza",
    "Prof. Iwlly Rafaela Mendes", "Izaira Moreira Veiga - Pedagoga", "Prof. Jaqueline Bonifácio Michelato",
    "Janaína Letícia Panaggio - Secretária", "Juliana Aparecida Gonçalves - Pedagoga", "Prof. Juliana Ferri",
    "Prof. Katy Tondelli", "Prof. Kelen Cristina Leão", "Prof. Lorena Cristina de Oliveira Fernandes",
    "Lucas da Costa Ferreira - Assist. Adm.", "Prof. Luzia Nogueira", "Prof. Marcel Dancini Rodrigues",
    "Prof. Marco Aurélio Sant Ana", "Prof. Miriam Aparecida de Souza Dias", "Prof. Patrícia Janoni",
    "Romilson Lopes Leite - Inspetor", "Thiago José da Rocha - Diretor"
])

DISCIPLINAS = [
    "ARTE", "CIENCIAS", "ED DIG COMP PROG E ROBOTICA", "EDUCACAO FISICA",
    "ENSINO RELIGIOSO", "GEOGRAFIA", "HISTORIA", "LINGUA INGLESA",
    "LINGUA PORTUGUESA", "MATEMATICA", "EDUCACAO FINANCEIRA I", "ELETIVA I",
    "ESTUDO ORIENTADO I", "LEITURA REC APREND LINGUA PORT", "EMPREENDEDORISMO I",
    "LITER ART E MOVIMENTO I", "PENS LOG E CIDAD DIGITAL I", "PRATICAS EXPERIMENTAIS I",
    "PROJETO DE VIDA I", "REC APREND MATEMATICA", "REDACAO E LEITURA I", "OUTROS SETORES DA ESCOLA"
]

ALUNOS = [
{"id":1,"nome":"AGATHA VITÓRIA NASCIMENTO","turma":"6º","responsavel":"RAQUEL APARECIDA DE CAMPOS"},
{"id":2,"nome":"AGHATA YARA PEREIRA PRUDENTE","turma":"6º","responsavel":"TALITA GABRIELI PEREIRA MARTINS"},
{"id":3,"nome":"ALANA DE OLIVEIRA CHAVES","turma":"6º","responsavel":"LEILA REGINA DE OLIVEIRA CHAVES"},
{"id":4,"nome":"ANA BEATRIZ CAETANO","turma":"6º","responsavel":"LILIAN LUCAS CAETANO"},
{"id":5,"nome":"ANA BEATRIZ DA SILVA COSTA","turma":"6º","responsavel":"NEILA CRISTINA DA SILVA"},
{"id":6,"nome":"ANNA LIVIA RIBEIRO DE LIMA","turma":"6º","responsavel":"ANDREIA MARIA RIBEIRO DE LIMA"},
{"id":7,"nome":"CONRADO LEANDRO BRANDÃO BARRETO","turma":"6º","responsavel":"TAMIRES APARECIDA BRANDÃO"},
{"id":8,"nome":"ELOISA BEATRIZ DE OLIVEIRA CRISTÓVÃO","turma":"6º","responsavel":"ANA KARINE DE OLIVEIRA"},
{"id":9,"nome":"EMANUELA LOURENÇO MUNHOZ","turma":"6º","responsavel":"TAISE LOURENÇO CABRAL"},
{"id":10,"nome":"GUILHERME GONZAGA DE SOUZA MORAIS","turma":"6º","responsavel":"JULIANA DE SOUZA MORAIS"},
{"id":11,"nome":"ISABELLE CRISTINE FERREIRA","turma":"6º","responsavel":"CRISTIANE DE SOUZA FERREIRA"},
{"id":12,"nome":"ISADORA OLIVEIRA PEREIRA","turma":"6º","responsavel":"REGIANE CRISTINA OLIVEIRA"},
{"id":13,"nome":"JOÃO LUCAS FRANCISCO DA SILVA","turma":"6º","responsavel":"LINDALVA FRANCISCO"},
{"id":14,"nome":"JOSÉ EDUARDO CARVALHO DE BRITO","turma":"6º","responsavel":"CÉLIA CARVALHO DE BRITO"},
{"id":15,"nome":"LARA ANDRADE","turma":"6º","responsavel":"ANA CAROLINA BIOLADA ANDRADE"},
{"id":16,"nome":"LORENA CARDOSO SOTERIO","turma":"6º","responsavel":"MOISES SOTERIO"},
{"id":17,"nome":"LUIZ FELIPE COSTA DA SILVA","turma":"6º","responsavel":"CLÁUDIO ROBERTO DA SILVA JÚNIOR"},
{"id":18,"nome":"LUIZ MIGUEL RIBEIRO FRANCISCO","turma":"6º","responsavel":"GEISSI KELLY RIBEIRO DE LIMA"},
{"id":19,"nome":"MARIA CECÍLIA SANCHES","turma":"6º","responsavel":"LUCIANA APARECIDA FERNANDES SANCHES"},
{"id":20,"nome":"MARIA CLARA OLIVEIRA TINTI","turma":"6º","responsavel":"ELAINE CRISTINA DE OLIVEIRA TINTI"},
{"id":21,"nome":"MARIA JULIA DOS SANTOS CARVALHO","turma":"6º","responsavel":"JESSICA OLIVEIRA DOS SANTOS"},
{"id":22,"nome":"MARIA SOPHIA LOURENÇO FORTES","turma":"6º","responsavel":"POLLYANNA LUIZA AMARAL"},
{"id":23,"nome":"MATHEUS APARECIDO MARTINS","turma":"6º","responsavel":"GISLAINE APARECIDO MARTINS"},
{"id":24,"nome":"MIGUEL AUGUSTO DA SILVA GROCHOLSKI","turma":"6º","responsavel":"JUCIANE APARECIDA DA SILVA GROCHOLSKI"},
{"id":25,"nome":"MURILO APARECIDO MARTINS","turma":"6º","responsavel":"GISLAINE APARECIDO MARTINS"},
{"id":26,"nome":"NATHÁLIA OLIVEIRA GODOI","turma":"6º","responsavel":"FERNANDA SANTOS DE OLIVEIRA GODOI"},
{"id":27,"nome":"NICOLE CASTRO BATISTA","turma":"6º","responsavel":"ROZILAINE DA SILVA CASTRO"},
{"id":28,"nome":"RAYSSA VITÓRIA OLIVEIRA DA SILVA","turma":"6º","responsavel":"RENATA OLIVEIRA DA SILVA"},
{"id":29,"nome":"RODRIGO VENÂNCIO DA SILVA JUNIOR","turma":"6º","responsavel":"ADRIANA FERRARI"},
{"id":30,"nome":"THALLES FERNANDO BELCHIOR OLÍMPIO","turma":"6º","responsavel":"LARISSA CRISTINA VITORINO CARVALHO BELCHIOR"},
{"id":31,"nome":"VALLENTINA VESSONI PAULA","turma":"6º","responsavel":"POLLIANE VESSONI"},
{"id":32,"nome":"ABNER DAVI RODRIGUES VIANA DA SILVA","turma":"7º","responsavel":"MEIRIELY VIANA DA SILVA"},
{"id":33,"nome":"AGATHA EMANUELY GABRIEL PIRES","turma":"7º","responsavel":"ELAINE DE FÁTIMA MEIRA GABRIEL"},
{"id":34,"nome":"ANA JULIA SOARES DA SILVA RIBEIRO","turma":"7º","responsavel":"ALEXANDRE SOARES RIBEIRO"},
{"id":35,"nome":"ARTHUR GUILHERME OLIVEIRA DE LIMA","turma":"7º","responsavel":"DELEUZA APARECIDA RODRIGUES"},
{"id":36,"nome":"AYSHA GABRIELLY DOS SANTOS SILVA","turma":"7º","responsavel":"DEISEVANI CRISTINA DOS SANTOS"},
{"id":37,"nome":"BEATRIZ OLIVEIRA DE SOUZA","turma":"7º","responsavel":"VERÔNICA DE OLIVEIRA TOLEDO"},
{"id":38,"nome":"CARLOS HENRIQUE NUNES ROBERTO","turma":"7º","responsavel":"DANIELA NUNES DA SILVA"},
{"id":39,"nome":"CAUÊ VITOR DOS SANTOS ROZA","turma":"7º","responsavel":"ISABELA LUIZA DOS SANTOS SILVA"},
{"id":40,"nome":"GABRIEL DE SOUZA SOARES","turma":"7º","responsavel":"CRISTIANE DA COSTA SOUZA SOARES"},
{"id":41,"nome":"JHON RHEFERSON DOS SANTOS CARVALHO","turma":"7º","responsavel":"JESSICA OLIVEIRA DOS SANTOS"},
{"id":42,"nome":"LETICIA DA SILVA DE CARVALHO","turma":"7º","responsavel":"ROSEMEIRE APARECIDA DA SILVA DE CARVALHO"},
{"id":43,"nome":"LORENA RAFAELLA MENDES DA SILVA","turma":"7º","responsavel":"GABRIELA MARIA MENDES"},
{"id":44,"nome":"MANUELLA ARAÚJO GUIMARÃES","turma":"7º","responsavel":"CINTIA CRISTINA DE ARAÚJO GUIMARÃES"},
{"id":45,"nome":"MARIA ISABELY DE BARROS RIBEIRO","turma":"7º","responsavel":"YASMIN DANIELLE DE BARROS RIBEIRO"},
{"id":46,"nome":"VICTOR HUGO MENDONÇA DE SOUZA","turma":"7º","responsavel":"BEATRIZ CONSTANCIO DE MENDONÇA"},
{"id":47,"nome":"CAIO HENRIQUE BATISTA DUZI","turma":"8º","responsavel":"AMANDA APARECIDA BATISTA"},
{"id":48,"nome":"EDUARDO LOURENÇO MUNHOZ","turma":"8º","responsavel":"TAISE LOURENÇO CABRAL"},
{"id":49,"nome":"ESTHER MARIA DE ASSIS AMANCIO","turma":"8º","responsavel":"ANA CARLA GREGORIO DE ASSIS"},
{"id":50,"nome":"LÉU BRAYAN RAMOS MARQUES","turma":"8º","responsavel":"KÉTI MIRIAM RAMOS DE SIQUEIRA"},
{"id":51,"nome":"LORENA MANUELA INOCENCIO PEREZ BAÇAN","turma":"8º","responsavel":"SILVIA HELENA INOCENCIO"},
{"id":52,"nome":"MARIA HELENA BATISTA FERREIRA","turma":"8º","responsavel":"GRAZIELLA CARLA BATISTA FERREIRA"},
{"id":53,"nome":"MATHEUS FELIPE MARLINI","turma":"8º","responsavel":"DAIANE DE FÁTIMA GONÇALVES"},
{"id":54,"nome":"MAYARA VITORIA DA SILVA FIGAS","turma":"8º","responsavel":"ANDRELISA FARIA DA SILVA FIGAS"},
{"id":55,"nome":"PEDRO HENRIQUE DOMINGOS","turma":"8º","responsavel":"THAYNARA DAIANE MALUZA"},
{"id":56,"nome":"RODRIGO ROQUE CHAGAS","turma":"8º","responsavel":"SANDRA APARECIDA ROQUE CHAGAS"},
{"id":57,"nome":"ALICE ALVES KAVINSKI","turma":"9º","responsavel":"KÁTIA APARECIDA ALVES DO NASCIMENTO"},
{"id":58,"nome":"ANA LAURA GONÇALVES DE LIMA","turma":"9º","responsavel":"LAURIANI RIBEIRO GONCALVES"},
{"id":59,"nome":"ANNA LETÍCIA SANTOS DUARTE SIQUEIRA","turma":"9º","responsavel":"WANÊSSA BARBOSA DOS SANTOS DUARTE"},
{"id":60,"nome":"ANNA LYVIA NUNES LIMA","turma":"9º","responsavel":"ELAINE APARECIDA PEREIRA"},
{"id":61,"nome":"FABRICIO EMANUELL SOARES FRANCISCO","turma":"9º","responsavel":"ELIEUZA SOARES"},
{"id":62,"nome":"GEOVANA STHEFANY GOMES FERREIRA","turma":"9º","responsavel":"JOSIMARA GOMES FERREIRA"},
{"id":63,"nome":"JHONNH HENRY LOÇURDO GONÇALVES PINTO","turma":"9º","responsavel":"PALOMA NAYANE LOÇURDO"},
{"id":64,"nome":"JOÃO ARTHUR MATIAS DA SILVA","turma":"9º","responsavel":"ALINE MOREIRA MATIAS"},
{"id":65,"nome":"JOÃO GUILHERME DA COSTA SILVA","turma":"9º","responsavel":"CLÁUDIO ROBERTO DA SILVA JÚNIOR"},
{"id":66,"nome":"JUAN AUGUSTO PANAGGIO","turma":"9º","responsavel":"KATHIELEN DAYANNE PANAGGIO"},
{"id":67,"nome":"KAUAN AUGUSTO GRACIOLI","turma":"9º","responsavel":"RAQUEL SANTOS SILVA"},
{"id":68,"nome":"KAUAN DE SOUZA DOLNISCKI","turma":"9º","responsavel":"CRISTIANE APARECIDA DE SOUZA"},
{"id":69,"nome":"LAÍSA ISABELE GONÇALVES DE LIMA","turma":"9º","responsavel":"LAURIANI RIBEIRO GONCALVES"},
{"id":70,"nome":"MARIA EDUARDA REIS CHAGAS","turma":"9º","responsavel":"MARIA LARYSSA REIS DAS CHAGAS"},
{"id":71,"nome":"MARIA JULIA DUARTE DAUTA","turma":"9º","responsavel":"FRANCENIRA APARECIDA DUARTE DAUTA"},
{"id":72,"nome":"MARIA VITORIA CAMPOS RODRIGUES DA SILVA","turma":"9º","responsavel":"ANDREIA CAMPOS RODRIGUES"},
{"id":73,"nome":"MIGUEL CARVALHO SANTANA","turma":"9º","responsavel":"EDINALDA DE CARVALHO"},
{"id":74,"nome":"MIGUEL THIAGO DOS SANTOS","turma":"9º","responsavel":"CELSO HORTIS DOS SANTOS"},
{"id":75,"nome":"NATÃ CHAGAS DE BRITO","turma":"9º","responsavel":"ANGELITA INACIA DE BRITO CHAGAS SILVA"},
{"id":76,"nome":"NÍCOLAS HENRIQUE TEODORO DA SILVA","turma":"9º","responsavel":"DEVANIR MARIANO DA SILVA TEODORO"},
{"id":77,"nome":"NIKOLLY CRISTINA DOS SANTOS VIANA","turma":"9º","responsavel":"TATIANE GOMES DOS SANTOS VIANA"},
{"id":78,"nome":"RACHEL VICTORIA DE ASSIS AMÂNCIO","turma":"9º","responsavel":"ANA CARLA GREGORIO DE ASSIS"},
{"id":79,"nome":"RICHARD GABRIEL FAL","turma":"9º","responsavel":"LUCILENE BERGAMASCO DA SILVA FAL"},
{"id":80,"nome":"SOPHIA VITÓRIA PORTO DA SILVA","turma":"9º","responsavel":"DANIELLI FERNANDA PORTO"},
{"id":81,"nome":"JOAO GABRIEL FELICIANO GONCALVES","turma":"9º","responsavel":"FERNANDA FELICIANO"},
]

TIPOS_OCORRENCIA = [
    "Conversas paralelas e dispersão frequente durante as aulas",
    "Dificuldade em manter atenção e concentração nas atividades propostas",
    "Agitação motora e dificuldade em permanecer no lugar nos momentos adequados",
    "Dificuldade em respeitar regras, combinados e orientações da rotina escolar",
    "Dificuldade de socialização e de convivência com colegas e professores",
    "Uso de linguagem inadequada em interações no ambiente escolar",
    "Postura desafiadora diante de intervenções e encaminhamentos pedagógicos",
    "Resistência ao cumprimento de orientações e solicitações da equipe escolar",
    "Interrupções constantes que comprometem o andamento da aula",
    "Uso inadequado de celular e outros dispositivos eletrônicos durante as aulas",
    "Baixo engajamento e não realização das atividades propostas",
    "Recusa em participar das atividades pedagógicas individuais ou coletivas",
    "Dificuldade em trabalhar de forma colaborativa em grupo",
    "Provocações, conflitos interpessoais e atitudes que prejudicam a convivência escolar",
    "Demonstrações de agressividade verbal em interações com colegas ou profissionais da escola",
    "Demonstrações de agressividade física, empurrões ou atitudes intimidatórias",
    "Baixa tolerância à frustração diante de limites, correções ou dificuldades",
    "Dificuldade de autocontrole emocional e comportamental em situações de conflito",
    "Isolamento social ou baixa participação nas interações da turma",
    "Falta de compromisso com os combinados e responsabilidades escolares",
    "Falta de respeito com colegas, professores e demais profissionais da escola",
    "Entradas frequentes fora do horário estabelecido para as aulas",
    "Saída da sala sem autorização durante os períodos de aula",
    "Tumulto e comportamentos que comprometem a organização do ambiente escolar",
    "Desorganização intencional do espaço e/ou uso inadequado dos materiais escolares",
    "Danos ou mau uso de materiais e patrimônios da escola",
    "Dificuldade em seguir normas de convivência e limites institucionais",
    "Baixa autonomia na realização das atividades escolares",
    "Dependência excessiva de mediação para iniciar ou concluir atividades",
    "Postura passiva diante das propostas pedagógicas e situações de aprendizagem",
    "Insegurança para participar, expor opiniões ou tirar dúvidas em sala de aula",
    "Dificuldade em organizar materiais, tarefas e rotina de estudos",
]

ENCAMINHAMENTOS = [
    "Orientação verbal ao estudante", "Conversa individual com o estudante",
    "Mediação pedagógica em sala", "Registro para acompanhamento pedagógico",
    "Encaminhamento à equipe pedagógica", "Encaminhamento à direção",
    "Contato com a família", "Convocação do responsável",
    "Registro em ata", "Monitoramento contínuo"
]

INTENSIDADES = ["Leve", "Moderada", "Grave"]


def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS ocorrencias (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                data_hora TEXT,
                professor TEXT,
                turma TEXT,
                aluno TEXT,
                responsavel TEXT,
                disciplina TEXT,
                tipo TEXT,
                intensidade TEXT,
                encaminhamento TEXT,
                observacoes TEXT,
                texto TEXT,
                pdf TEXT
            )
        """)
init_db()


def encontrar_aluno(nome):
    return next((a for a in ALUNOS if a["nome"] == nome), None)


def gerar_texto(data_hora_br, professor, turma, aluno, responsavel, disciplina, tipo, intensidade, encaminhamento, observacoes):
    texto = (
        f"No dia {data_hora_br}, durante a aula/atividade de {disciplina}, na turma {turma}, "
        f"o(a) estudante {aluno}, cujo responsável registrado é {responsavel}, apresentou ocorrência relacionada a: {tipo}. "
        f"A ocorrência foi classificada como {intensidade.lower()}. "
        f"Como encaminhamento inicial, foi realizado: {encaminhamento}."
    )
    if observacoes.strip():
        texto += f" Observações complementares: {observacoes.strip()}"
    texto += f" Registro realizado pelo(a) professor(a)/servidor(a): {professor}."
    return texto


def gerar_pdf(dados):
    nome_seguro = dados["aluno"].replace(" ", "_").replace("/", "-")
    filename = f"ocorrencia_{nome_seguro}_{datetime.now(ZoneInfo('America/Sao_Paulo')).strftime('%Y%m%d_%H%M%S')}.pdf"
    caminho = os.path.join(PDF_DIR, filename)

    doc = SimpleDocTemplate(
        caminho,
        pagesize=A4,
        rightMargin=2*cm,
        leftMargin=2*cm,
        topMargin=1.5*cm,
        bottomMargin=1.5*cm
    )

    styles = getSampleStyleSheet()
    normal = ParagraphStyle('NormalCustom', parent=styles['Normal'], fontSize=10, leading=14)
    titulo = ParagraphStyle('Titulo', parent=styles['Title'], fontSize=15, textColor=colors.HexColor('#08345f'), alignment=1)
    subtitulo = ParagraphStyle('Subtitulo', parent=styles['Normal'], fontSize=10, alignment=1, textColor=colors.HexColor('#0b5b78'))

    elementos = []

    if os.path.exists(LOGO_PATH):
        img = Image(LOGO_PATH, width=2.6*cm, height=2.6*cm)
        img.hAlign = 'CENTER'
        elementos.append(img)

    elementos.append(Paragraph("Sistema de Registro de Ocorrências Escolares", titulo))
    elementos.append(Paragraph("Escola Estadual Padre Manuel da Nóbrega - E.F. Tempo Integral", subtitulo))
    elementos.append(Spacer(1, 0.4*cm))

    tabela = [
        ["Data e horário", dados["data_hora"]],
        ["Professor(a)/Servidor(a)", dados["professor"]],
        ["Turma", dados["turma"]],
        ["Estudante", dados["aluno"]],
        ["Responsável", dados["responsavel"]],
        ["Componente/Setor", dados["disciplina"]],
        ["Tipo de ocorrência", dados["tipo"]],
        ["Intensidade", dados["intensidade"]],
        ["Encaminhamento", dados["encaminhamento"]],
    ]

    table = Table(tabela, colWidths=[4.2*cm, 11.8*cm])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (0,-1), colors.HexColor('#08345f')),
        ('TEXTCOLOR', (0,0), (0,-1), colors.white),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#d0d7de')),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('FONTNAME', (0,0), (0,-1), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 9),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
    ]))

    elementos.append(table)
    elementos.append(Spacer(1, 0.5*cm))

    elementos.append(Paragraph(
        "Texto da ocorrência",
        ParagraphStyle('Secao', parent=styles['Heading2'], fontSize=12, textColor=colors.HexColor('#08345f'))
    ))
    elementos.append(Paragraph(dados["texto"], normal))

    elementos.append(Spacer(1, 1.0*cm))

    elementos.append(Paragraph("______________________________________________", subtitulo))
    elementos.append(Paragraph(dados["aluno"], subtitulo))
    elementos.append(Paragraph("Assinatura do(a) estudante", subtitulo))

    elementos.append(Spacer(1, 0.7*cm))

    elementos.append(Paragraph("______________________________________________", subtitulo))
    elementos.append(Paragraph(dados["responsavel"], subtitulo))
    elementos.append(Paragraph("Assinatura do(a) responsável", subtitulo))

    elementos.append(Spacer(1, 0.7*cm))

    elementos.append(Paragraph("______________________________________________", subtitulo))
    elementos.append(Paragraph(dados["professor"], subtitulo))
    elementos.append(Paragraph("Servidor(a) que realizou o registro", subtitulo))

    doc.build(elementos)
    return filename, caminho

def salvar_banco(dados, filename):
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            INSERT INTO ocorrencias
            (data_hora, professor, turma, aluno, responsavel, disciplina, tipo, intensidade, encaminhamento, observacoes, texto, pdf)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (dados["data_hora"], dados["professor"], dados["turma"], dados["aluno"], dados["responsavel"], dados["disciplina"], dados["tipo"], dados["intensidade"], dados["encaminhamento"], dados["observacoes"], dados["texto"], filename))


def enviar_email(dados, pdf_path):
    remetente = os.environ.get("EMAIL_REMETENTE")
    destinatarios = [e.strip() for e in os.environ.get("EMAIL_DESTINATARIOS", "").split(",") if e.strip()]
    brevo_api_key = os.environ.get("BREVO_API_KEY")

    if not remetente or not destinatarios or not brevo_api_key:
        return False, "E-mail não configurado nas variáveis de ambiente."

    with open(pdf_path, "rb") as f:
        pdf_base64 = base64.b64encode(f.read()).decode("utf-8")

    payload = {
        "sender": {
            "name": "Sistema de Ocorrências Escolares",
            "email": remetente
        },
        "to": [{"email": email} for email in destinatarios],
        "subject": f"Nova ocorrência escolar - {dados['aluno']} - {dados['turma']}",
        "htmlContent": f"""
        <p>Segue nova ocorrência registrada no sistema.</p>
        <p>{dados['texto']}</p>
        """,
        "attachment": [
            {
                "content": pdf_base64,
                "name": os.path.basename(pdf_path)
            }
        ]
    }

    headers = {
        "accept": "application/json",
        "api-key": brevo_api_key,
        "content-type": "application/json"
    }

    try:
        response = requests.post(
            "https://api.brevo.com/v3/smtp/email",
            json=payload,
            headers=headers,
            timeout=20
        )

        if response.status_code in [200, 201, 202]:
            return True, "E-mail enviado com sucesso."

        return False, f"PDF gerado, mas a API Brevo retornou erro {response.status_code}: {response.text}"

    except Exception as e:
        return False, f"PDF gerado, mas houve erro ao enviar e-mail pela API Brevo: {e}"

@app.route("/", methods=["GET", "POST"])

def index():
    if request.method == "POST":
        professor = request.form.get("professor")
        turma = request.form.get("turma")
        aluno_nome = request.form.get("aluno")
        disciplina = request.form.get("disciplina")
        tipo = request.form.get("tipo")
        intensidade = request.form.get("intensidade")
        encaminhamento = request.form.get("encaminhamento")
        observacoes = request.form.get("observacoes", "")
        aluno = encontrar_aluno(aluno_nome)
        if not aluno:
            flash("Aluno não encontrado. Verifique a turma e o estudante selecionado.", "erro")
            return redirect(url_for("index"))

        data_hora = datetime.now(ZoneInfo("America/Sao_Paulo")).strftime("%d/%m/%Y às %H:%M")
        texto = gerar_texto(data_hora, professor, turma, aluno_nome, aluno["responsavel"], disciplina, tipo, intensidade, encaminhamento, observacoes)
        dados = {
            "data_hora": data_hora, "professor": professor, "turma": turma, "aluno": aluno_nome,
            "responsavel": aluno["responsavel"], "disciplina": disciplina, "tipo": tipo,
            "intensidade": intensidade, "encaminhamento": encaminhamento, "observacoes": observacoes, "texto": texto
        }
        filename, pdf_path = gerar_pdf(dados)
        salvar_banco(dados, filename)
        ok, msg = enviar_email(dados, pdf_path)
        flash("Ocorrência registrada e PDF gerado. " + msg, "sucesso" if ok else "aviso")
        return render_template("resultado.html", dados=dados, pdf_file=filename)

    turmas = sorted(set(a["turma"] for a in ALUNOS))
    return render_template("index.html", professores=PROFESSORES, disciplinas=DISCIPLINAS, alunos=ALUNOS, turmas=turmas,
                           tipos=TIPOS_OCORRENCIA, encaminhamentos=ENCAMINHAMENTOS, intensidades=INTENSIDADES)

@app.route("/pdf/<filename>")
def baixar_pdf(filename):
    return send_file(os.path.join(PDF_DIR, filename), as_attachment=True)

@app.route("/historico")
def historico():
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute("SELECT * FROM ocorrencias ORDER BY id DESC LIMIT 100").fetchall()
    return render_template("historico.html", ocorrencias=rows)

if __name__ == "__main__":
    app.run(debug=True)
