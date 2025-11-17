"""
RIQUEZA BABILÔNICA - Aplicativo de Finanças Pessoais e Empresariais
Baseado nos princípios atemporais de "O Homem Mais Rico da Babilônia"
Desenvolvido com Kivy/KivyMD para interface moderna e responsiva
"""

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.spinner import Spinner
from kivy.uix.progressbar import ProgressBar
from kivy.graphics import Color, Rectangle, RoundedRectangle
from kivy.metrics import dp
from kivy.animation import Animation
import sqlite3
from datetime import datetime


# ==================== CONFIGURAÇÕES E BANCO DE DADOS ====================
class DatabaseManager:
    """Gerencia todas as operações do banco de dados SQLite"""

    def __init__(self):
        self.conn = sqlite3.connect('riqueza_babilonica.db')
        self.cursor = self.conn.cursor()
        self.create_tables()

    def create_tables(self):
        """Cria as tabelas necessárias"""
        # Tabela de usuário
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS usuario(
                id INTEGER PRIMARY KEY,
                nome TEXT,
                nivel INTEGER DEFAULT 1,
                moedas_virtuais INTEGER DEFAULT 0,
                data_cadastro TEXT
            )
        ''')
        # Tabela de lições (Principia)
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS licoes(
                id INTEGER PRIMARY KEY,
                titulo TEXT,
                conteudo TEXT,
                ordem INTEGER,
                concluida INTEGER DEFAULT 0
            )
        ''')
        # Tabela de transações pessoais
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS transacoes(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tipo TEXT,
                categoria TEXT,
                valor REAL,
                descricao TEXT,
                data TEXT
            )
        ''')
        # Tabela de metas
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS metas(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT,
                valor_alvo REAL,
                valor_atual REAL DEFAULT 0,
                data_inicio TEXT,
                data_alvo TEXT
            )
        ''')
        # Tabela de investimentos
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS investimentos(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tipo_prazo TEXT,
                nome TEXT,
                valor_inicial REAL,
                taxa_anual REAL,
                data_inicio TEXT,
                prazo_meses INTEGER
            )
        ''')
        # Tabela de negócios
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS negocios(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT,
                descricao TEXT,
                investimento_inicial REAL,
                faturamento_projetado REAL,
                data_criacao TEXT
            )
        ''')
        self.conn.commit()
        self.inserir_licoes_iniciais()

    def inserir_licoes_iniciais(self):
        """Insere as 7 Leis de Ouro da Babilônia (apenas 3 no MVP)"""
        licoes = [
            (
                "1ª Lei: Poupe 10% do que Ganha",
                "A primeira lei da riqueza é simples: guarde pelo menos um décimo de tudo que você ganha. "
                "Este dinheiro não é para gastar, mas para construir seu tesouro. "
                "Pague a si mesmo primeiro, antes de pagar contas ou despesas. "
                "Esta é a base da prosperidade duradoura.",
                1
            ),
            (
                "2ª Lei: Controle Seus Gastos",
                "Não confunda despesas necessárias com desejos supérfluos. "
                "Analise cada gasto e questione: 'Isto é realmente necessário?' "
                "Os gastos crescem para consumir toda a renda, a menos que você os controle conscientemente. "
                "Viva com menos do que ganha e terá ouro para multiplicar.",
                2
            ),
            (
                "3ª Lei: Multiplique Seu Ouro",
                "O dinheiro guardado não gera riqueza sozinho. Faça-o trabalhar para você! "
                "Invista com sabedoria em negócios ou empréstimos seguros que gerem retorno. "
                "Cada moeda de ouro que você investe é um escravo trabalhando para trazer mais ouro. "
                "O segredo não é apenas guardar, mas fazer crescer.",
                3
            ),
        ]
        for titulo, conteudo, ordem in licoes:
            self.cursor.execute('''
                INSERT OR IGNORE INTO licoes(titulo, conteudo, ordem)
                VALUES (?, ?, ?)
            ''', (titulo, conteudo, ordem))
        self.conn.commit()

    def adicionar_transacao(self, tipo, categoria, valor, descricao):
        """Adiciona uma transação (receita ou despesa)"""
        self.cursor.execute('''
            INSERT INTO transacoes(tipo, categoria, valor, descricao, data)
            VALUES (?, ?, ?, ?, ?)
        ''', (tipo, categoria, valor, descricao, datetime.now().strftime('%Y-%m-%d')))
        self.conn.commit()

    def obter_saldo(self):
        """Calcula o saldo total (receitas - despesas)"""
        self.cursor.execute("SELECT SUM(valor) FROM transacoes WHERE tipo='receita'")
        receitas = self.cursor.fetchone()[0] or 0
        self.cursor.execute("SELECT SUM(valor) FROM transacoes WHERE tipo='despesa'")
        despesas = self.cursor.fetchone()[0] or 0
        return receitas - despesas

    def obter_transacoes_mes_atual(self):
        """Retorna transações do mês atual"""
        primeiro_dia = datetime.now().replace(day=1).strftime('%Y-%m-%d')
        self.cursor.execute('''
            SELECT tipo, categoria, valor, descricao, data
            FROM transacoes
            WHERE data >= ?
            ORDER BY data DESC
        ''', (primeiro_dia,))
        return self.cursor.fetchall()

    def obter_licoes(self):
        """Retorna todas as lições"""
        self.cursor.execute('SELECT id, titulo, conteudo, concluida FROM licoes ORDER BY ordem')
        return self.cursor.fetchall()

    def marcar_licao_concluida(self, licao_id):
        """Marca uma lição como concluída"""
        self.cursor.execute('UPDATE licoes SET concluida = 1 WHERE id = ?', (licao_id,))
        self.conn.commit()


# ==================== CORES E TEMA ====================
class Cores:
    """Paleta de cores do tema Babilônia"""
    DOURADO = [0.85, 0.65, 0.13, 1]      # Dourado riqueza
    AZUL_ESCURO = [0.05, 0.13, 0.25, 1]  # Azul noite babilônica
    BRANCO = [0.98, 0.98, 0.98, 1]
    CINZA_CLARO = [0.9, 0.9, 0.9, 1]
    VERDE = [0.2, 0.7, 0.3, 1]           # Para receitas
    VERMELHO = [0.9, 0.2, 0.2, 1]        # Para despesas


# ==================== COMPONENTES PERSONALIZADOS ====================
class CartaoElegante(BoxLayout):
    """Cartão com design elegante e sombra"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding = dp(15)
        self.spacing = dp(10)
        self.size_hint_y = None
        self.height = dp(150)
        with self.canvas.before:
            Color(*Cores.BRANCO)
            self.rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(10)])
        self.bind(pos=self.atualizar_rect, size=self.atualizar_rect)

    def atualizar_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size


class BotaoDourado(Button):
    """Botão estilizado com cor dourada"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_normal = ''
        self.background_color = Cores.DOURADO
        self.color = Cores.AZUL_ESCURO
        self.bold = True
        self.font_size = dp(16)
        self.size_hint_y = None
        self.height = dp(50)


# ==================== TELA PRINCIPAL (PRINCIPIA) ====================
class TelaPrincipia(Screen):
    """Aba de ensino financeiro com as Leis de Ouro"""

    def __init__(self, db, **kwargs):
        super().__init__(**kwargs)
        self.db = db
        self.name = 'principia'
        layout = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10))

        # Cabeçalho
        header = BoxLayout(size_hint_y=None, height=dp(80), padding=dp(10))
        with header.canvas.before:
            Color(*Cores.AZUL_ESCURO)
            self.header_rect = Rectangle(pos=header.pos, size=header.size)
        header.bind(pos=self.atualizar_header, size=self.atualizar_header)
        titulo = Label(
            text='🏛 PRINCIPIA\nSabedoria da Babilônia',
            font_size=dp(24), bold=True, color=Cores.DOURADO, halign='center'
        )
        titulo.bind(size=titulo.setter('text_size'))
        header.add_widget(titulo)
        layout.add_widget(header)

        # ScrollView com lições
        scroll = ScrollView()
        licoes_layout = BoxLayout(orientation='vertical', spacing=dp(15), size_hint_y=None, padding=dp(10))
        licoes_layout.bind(minimum_height=licoes_layout.setter('height'))

        licoes = self.db.obter_licoes()
        for licao_id, titulo_licao, conteudo, concluida in licoes:
            cartao = self.criar_cartao_licao(licao_id, titulo_licao, conteudo, concluida)
            licoes_layout.add_widget(cartao)

        scroll.add_widget(licoes_layout)
        layout.add_widget(scroll)
        self.add_widget(layout)

    def atualizar_header(self, instance, value):
        self.header_rect.pos = instance.pos
        self.header_rect.size = instance.size

    def criar_cartao_licao(self, licao_id, titulo, conteudo, concluida):
        cartao = CartaoElegante()
        cartao.height = dp(200)

        titulo_label = Label(
            text=titulo, font_size=dp(18), bold=True, color=Cores.AZUL_ESCURO,
            size_hint_y=None, height=dp(30), halign='left', valign='top'
        )
        titulo_label.bind(size=titulo_label.setter('text_size'))
        cartao.add_widget(titulo_label)

        conteudo_label = Label(
            text=conteudo[:150] + '...',
            font_size=dp(14), color=[0.3, 0.3, 0.3, 1], halign='left', valign='top'
        )
        conteudo_label.bind(size=conteudo_label.setter('text_size'))
        cartao.add_widget(conteudo_label)

        if concluida:
            botao = Button(
                text='✓ Concluída', background_color=Cores.VERDE,
                size_hint_y=None, height=dp(40), disabled=True
            )
        else:
            botao = BotaoDourado(text='Estudar Lição')
            botao.bind(on_press=lambda x: self.marcar_concluida(licao_id, cartao))
        cartao.add_widget(botao)
        return cartao

    def marcar_concluida(self, licao_id, cartao):
        self.db.marcar_licao_concluida(licao_id)
        anim = Animation(background_color=Cores.VERDE, duration=0.3)
        botao = cartao.children[0]
        anim.start(botao)
        botao.text = '✓ Concluída'
        botao.disabled = True


# ==================== TELA MEU DINHEIRO ====================
class TelaMeuDinheiro(Screen):
    """Aba de controle financeiro pessoal"""

    def __init__(self, db, **kwargs):
        super().__init__(**kwargs)
        self.db = db
        self.name = 'meu_dinheiro'
        layout = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10))

        # Cabeçalho
        header = BoxLayout(size_hint_y=None, height=dp(80), padding=dp(10))
        with header.canvas.before:
            Color(*Cores.AZUL_ESCURO)
            self.header_rect = Rectangle(pos=header.pos, size=header.size)
        header.bind(pos=self.atualizar_header, size=self.atualizar_header)
        titulo = Label(
            text='💰 MEU DINHEIRO\nControle Financeiro',
            font_size=dp(24), bold=True, color=Cores.DOURADO, halign='center'
        )
        titulo.bind(size=titulo.setter('text_size'))
        header.add_widget(titulo)
        layout.add_widget(header)

        # Cartão de saldo
        saldo_cartao = CartaoElegante()
        saldo_cartao.height = dp(120)
        saldo_label = Label(
            text='Saldo Total', font_size=dp(16), color=Cores.AZUL_ESCURO,
            size_hint_y=None, height=dp(30)
        )
        saldo_cartao.add_widget(saldo_label)
        saldo_atual = self.db.obter_saldo()
        self.valor_saldo = Label(
            text=f'R$ {saldo_atual:,.2f}', font_size=dp(32), bold=True,
            color=Cores.VERDE if saldo_atual >= 0 else Cores.VERMELHO
        )
        saldo_cartao.add_widget(self.valor_saldo)
        layout.add_widget(saldo_cartao)

        # Botões de ação
        botoes = GridLayout(cols=2, spacing=dp(10), size_hint_y=None, height=dp(60))
        btn_receita = BotaoDourado(text='+ Receita')
        btn_receita.background_color = Cores.VERDE
        btn_receita.bind(on_press=self.adicionar_receita)
        botoes.add_widget(btn_receita)

        btn_despesa = BotaoDourado(text='- Despesa')
        btn_despesa.background_color = Cores.VERMELHO
        btn_despesa.bind(on_press=self.adicionar_despesa)
        botoes.add_widget(btn_despesa)
        layout.add_widget(botoes)

        # Lista de transações
        trans_label = Label(
            text='Transações Recentes', font_size=dp(18), bold=True,
            color=Cores.AZUL_ESCURO, size_hint_y=None, height=dp(40)
        )
        layout.add_widget(trans_label)

        scroll = ScrollView()
        self.lista_transacoes = BoxLayout(orientation='vertical', spacing=dp(5), size_hint_y=None, padding=dp(5))
        self.lista_transacoes.bind(minimum_height=self.lista_transacoes.setter('height'))
        self.atualizar_transacoes()
        scroll.add_widget(self.lista_transacoes)
        layout.add_widget(scroll)
        self.add_widget(layout)

    def atualizar_header(self, instance, value):
        self.header_rect.pos = instance.pos
        self.header_rect.size = instance.size

    def adicionar_receita(self, instance):
        self.mostrar_formulario('receita')

    def adicionar_despesa(self, instance):
        self.mostrar_formulario('despesa')

    def mostrar_formulario(self, tipo):
        self.lista_transacoes.clear_widgets()
        form = BoxLayout(orientation='vertical', spacing=dp(10), size_hint_y=None, height=dp(300))
        form.padding = dp(10)

        titulo = Label(
            text=f'Nova {tipo.capitalize()}', font_size=dp(20), bold=True,
            color=Cores.AZUL_ESCURO, size_hint_y=None, height=dp(40)
        )
        form.add_widget(titulo)

        valor_input = TextInput(
            hint_text='Valor (R$)', input_filter='float', multiline=False,
            size_hint_y=None, height=dp(45)
        )
        form.add_widget(valor_input)

        categorias = ['Salário', 'Freelance', 'Investimentos'] if tipo == 'receita' else \
                     ['Alimentação', 'Transporte', 'Moradia', 'Lazer', 'Outros']
        categoria_spinner = Spinner(
            text='Selecione Categoria', values=categorias,
            size_hint_y=None, height=dp(45)
        )
        form.add_widget(categoria_spinner)

        desc_input = TextInput(hint_text='Descrição', multiline=True, size_hint_y=None, height=dp(80))
        form.add_widget(desc_input)

        botoes = BoxLayout(spacing=dp(10), size_hint_y=None, height=dp(50))
        btn_salvar = BotaoDourado(text='Salvar')
        btn_salvar.bind(on_press=lambda x: self.salvar_transacao(
            tipo, categoria_spinner.text, valor_input.text, desc_input.text
        ))
        botoes.add_widget(btn_salvar)

        btn_cancelar = Button(text='Cancelar', background_color=[0.5, 0.5, 0.5, 1])
        btn_cancelar.bind(on_press=lambda x: self.atualizar_transacoes())
        botoes.add_widget(btn_cancelar)

        form.add_widget(botoes)
        self.lista_transacoes.add_widget(form)

    def salvar_transacao(self, tipo, categoria, valor, descricao):
        try:
            valor_float = float(valor.replace(',', '.'))
            self.db.adicionar_transacao(tipo, categoria, valor_float, descricao)
            saldo_novo = self.db.obter_saldo()
            self.valor_saldo.text = f'R$ {saldo_novo:,.2f}'
            self.valor_saldo.color = Cores.VERDE if saldo_novo >= 0 else Cores.VERMELHO
            self.atualizar_transacoes()
        except ValueError:
            pass  # Tratar erro de valor inválido

    def atualizar_transacoes(self):
        self.lista_transacoes.clear_widgets()
        transacoes = self.db.obter_transacoes_mes_atual()
        if not transacoes:
            msg = Label(
                text='Nenhuma transação este mês.\nComece adicionando uma receita ou despesa!',
                color=Cores.AZUL_ESCURO, halign='center'
            )
            msg.bind(size=msg.setter('text_size'))
            self.lista_transacoes.add_widget(msg)
            return

        for tipo, categoria, valor, descricao, data in transacoes:
            item = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(60), padding=dp(5))
            cor = Cores.VERDE if tipo == 'receita' else Cores.VERMELHO
            with item.canvas.before:
                Color(*cor, 0.2)
                rect = RoundedRectangle(pos=item.pos, size=item.size, radius=[dp(5)])
                item.bind(pos=lambda inst, r=rect: setattr(r, 'pos', inst.pos),
                          size=lambda inst, r=rect: setattr(r, 'size', inst.size))

            info = BoxLayout(orientation='vertical')
            info.add_widget(Label(
                text=f'{categoria} - {descricao[:20]}',
                color=Cores.AZUL_ESCURO, bold=True, halign='left', size_hint_y=0.6
            ))
            info.add_widget(Label(
                text=data, color=[0.5, 0.5, 0.5, 1], font_size=dp(12), halign='left', size_hint_y=0.4
            ))
            for label in info.children:
                label.bind(size=label.setter('text_size'))
            item.add_widget(info)

            valor_label = Label(
                text=f'R$ {valor:,.2f}',
                color=Cores.VERDE if tipo == 'receita' else Cores.VERMELHO,
                bold=True, size_hint_x=0.3
            )
            item.add_widget(valor_label)
            self.lista_transacoes.add_widget(item)


# ==================== TELA INVESTIMENTOS ====================
class TelaInvestimentos(Screen):
    """Aba de simulação de investimentos"""

    def __init__(self, db, **kwargs):
        super().__init__(**kwargs)
        self.db = db
        self.name = 'investimentos'
        layout = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10))

        header = BoxLayout(size_hint_y=None, height=dp(80), padding=dp(10))
        with header.canvas.before:
            Color(*Cores.AZUL_ESCURO)
            self.header_rect = Rectangle(pos=header.pos, size=header.size)
        header.bind(pos=self.atualizar_header, size=self.atualizar_header)
        titulo = Label(
            text='📈 INVESTIMENTOS\nSimulador de Crescimento',
            font_size=dp(24), bold=True, color=Cores.DOURADO, halign='center'
        )
        titulo.bind(size=titulo.setter('text_size'))
        header.add_widget(titulo)
        layout.add_widget(header)

        scroll = ScrollView()
        form_layout = BoxLayout(orientation='vertical', spacing=dp(15), size_hint_y=None, padding=dp(10))
        form_layout.bind(minimum_height=form_layout.setter('height'))

        form_layout.add_widget(Label(text='Valor Inicial (R$)', size_hint_y=None, height=dp(30), color=Cores.AZUL_ESCURO))
        self.valor_input = TextInput(hint_text='Ex: 10000', input_filter='float', multiline=False, size_hint_y=None, height=dp(45))
        form_layout.add_widget(self.valor_input)

        form_layout.add_widget(Label(text='Prazo', size_hint_y=None, height=dp(30), color=Cores.AZUL_ESCURO))
        self.prazo_spinner = Spinner(
            text='Selecione',
            values=['Curto Prazo (até 10 meses)', 'Médio Prazo (11-20 meses)', 'Longo Prazo (21-40 meses)'],
            size_hint_y=None, height=dp(45)
        )
        form_layout.add_widget(self.prazo_spinner)

        form_layout.add_widget(Label(text='Taxa Anual Estimada (%)', size_hint_y=None, height=dp(30), color=Cores.AZUL_ESCURO))
        self.taxa_input = TextInput(hint_text='Ex: 12.5', input_filter='float', multiline=False, size_hint_y=None, height=dp(45))
        form_layout.add_widget(self.taxa_input)

        btn_simular = BotaoDourado(text='Simular Crescimento')
        btn_simular.bind(on_press=self.simular)
        form_layout.add_widget(btn_simular)

        self.resultado_label = Label(
            text='', font_size=dp(16), color=Cores.AZUL_ESCURO,
            size_hint_y=None, height=dp(150), halign='center', valign='top'
        )
        self.resultado_label.bind(size=self.resultado_label.setter('text_size'))
        form_layout.add_widget(self.resultado_label)

        scroll.add_widget(form_layout)
        layout.add_widget(scroll)
        self.add_widget(layout)

    def atualizar_header(self, instance, value):
        self.header_rect.pos = instance.pos
        self.header_rect.size = instance.size

    def simular(self, instance):
        try:
            valor = float(self.valor_input.text.replace(',', '.'))
            taxa = float(self.taxa_input.text.replace(',', '.')) / 100

            prazo_texto = self.prazo_spinner.text
            if 'Curto' in prazo_texto:
                meses = 10
            elif 'Médio' in prazo_texto:
                meses = 20
            else:
                meses = 40

            montante = valor * ((1 + taxa) ** (meses / 12))
            rendimento = montante - valor

            self.resultado_label.text = f'''
✨ PROJEÇÃO DE INVESTIMENTO ✨
💰 Valor Investido: R$ {valor:,.2f}
📅 Prazo: {meses} meses
📈 Taxa Anual: {taxa * 100:.2f}%
🎯 Valor Final: R$ {montante:,.2f}
💎 Rendimento: R$ {rendimento:,.2f}
📊 Rentabilidade: {(rendimento / valor * 100):.1f}%
'''
        except ValueError:
            self.resultado_label.text = '⚠ Preencha todos os campos corretamente'


# ==================== TELA MEU NEGÓCIO ====================
class TelaMeuNegocio(Screen):
    """Aba de controle financeiro empresarial"""

    def __init__(self, db, **kwargs):
        super().__init__(**kwargs)
        self.db = db
        self.name = 'meu_negocio'
        layout = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10))

        header = BoxLayout(size_hint_y=None, height=dp(80), padding=dp(10))
        with header.canvas.before:
            Color(*Cores.AZUL_ESCURO)
            self.header_rect = Rectangle(pos=header.pos, size=header.size)
        header.bind(pos=self.atualizar_header, size=self.atualizar_header)
        titulo = Label(
            text='🏭 MEU NEGÓCIO\nGestão Empresarial',
            font_size=dp(24), bold=True, color=Cores.DOURADO, halign='center'
        )
        titulo.bind(size=titulo.setter('text_size'))
        header.add_widget(titulo)
        layout.add_widget(header)

        scroll = ScrollView()
        conteudo = BoxLayout(orientation='vertical', spacing=dp(15), size_hint_y=None, padding=dp(10))
        conteudo.bind(minimum_height=conteudo.setter('height'))

        resumo_card = CartaoElegante()
        resumo_card.height = dp(180)
        resumo_card.add_widget(Label(
            text='📊 Dashboard Empresarial', font_size=dp(18), bold=True,
            color=Cores.AZUL_ESCURO, size_hint_y=None, height=dp(35)
        ))
        resumo_card.add_widget(Label(
            text='Faturamento Mensal: R$ 0,00\nDespesas Operacionais: R$ 0,00\nLucro Líquido: R$ 0,00',
            font_size=dp(14), color=Cores.AZUL_ESCURO, halign='left', valign='top'
        ))
        conteudo.add_widget(resumo_card)

        dicas_card = CartaoElegante()
        dicas_card.height = dp(250)
        dicas_card.add_widget(Label(
            text='💡 Sabedoria Empresarial', font_size=dp(18), bold=True,
            color=Cores.DOURADO, size_hint_y=None, height=dp(35)
        ))
        dicas_texto = Label(
            text='''
"O ouro foge do homem que investe sem sabedoria ou que segue os conselhos tolos de trapaceiros e aventureiros."

📋 Checklist do Empreendedor:
• Separe contas pessoais das empresariais
• Mantenha reserva para 3 meses de operação
• Reinvista 30% do lucro no negócio
• Tenha múltiplas fontes de receita
''',
            font_size=dp(13), color=Cores.AZUL_ESCURO, halign='left', valign='top'
        )
        dicas_texto.bind(size=dicas_texto.setter('text_size'))
        dicas_card.add_widget(dicas_texto)
        conteudo.add_widget(dicas_card)

        btn_criar = BotaoDourado(text='+ Cadastrar Novo Negócio')
        btn_criar.bind(on_press=self.criar_negocio)
        conteudo.add_widget(btn_criar)

        scroll.add_widget(conteudo)
        layout.add_widget(scroll)
        self.add_widget(layout)

    def atualizar_header(self, instance, value):
        self.header_rect.pos = instance.pos
        self.header_rect.size = instance.size

    def criar_negocio(self, instance):
        pass  # Implementação futura


# ==================== TELA PLANO MESTRE ====================
class TelaPlanoMestre(Screen):
    """Aba do assistente de planejamento de negócios"""

    def __init__(self, db, **kwargs):
        super().__init__(**kwargs)
        self.db = db
        self.name = 'plano_mestre'
        self.pergunta_atual = 0
        self.respostas = {}
        self.perguntas = [
            {'titulo': '🎯 Qual é sua ideia de negócio?',
             'dica': 'Descreva brevemente o que você quer criar ou vender'},
            {'titulo': '👥 Quem é seu cliente ideal?',
             'dica': 'Idade, profissão, necessidades e poder aquisitivo'},
            {'titulo': '💵 Quanto precisa investir inicialmente?',
             'dica': 'Soma de equipamentos, estoque, marketing, etc.'},
            {'titulo': '📊 Qual sua projeção de faturamento mensal?',
             'dica': 'Baseado em pesquisa de mercado e concorrentes'},
            {'titulo': '🚀 Como pretende divulgar seu negócio?',
             'dica': 'Redes sociais, boca a boca, anúncios pagos...'}
        ]

        self.layout_principal = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10))

        header = BoxLayout(size_hint_y=None, height=dp(80), padding=dp(10))
        with header.canvas.before:
            Color(*Cores.AZUL_ESCURO)
            self.header_rect = Rectangle(pos=header.pos, size=header.size)
        header.bind(pos=self.atualizar_header, size=self.atualizar_header)
        titulo = Label(
            text='🧠 PLANO MESTRE\nAssistente de Negócios',
            font_size=dp(24), bold=True, color=Cores.DOURADO, halign='center'
        )
        titulo.bind(size=titulo.setter('text_size'))
        header.add_widget(titulo)
        self.layout_principal.add_widget(header)

        progresso_layout = BoxLayout(orientation='vertical', size_hint_y=None, height=dp(50), padding=[dp(20), 0])
        self.progresso_label = Label(
            text='Pergunta 1 de 5', size_hint_y=None, height=dp(25),
            color=Cores.AZUL_ESCURO, font_size=dp(14)
        )
        progresso_layout.add_widget(self.progresso_label)
        self.barra_progresso = ProgressBar(max=len(self.perguntas), value=1, size_hint_y=None, height=dp(10))
        progresso_layout.add_widget(self.barra_progresso)
        self.layout_principal.add_widget(progresso_layout)

        self.container_pergunta = BoxLayout(orientation='vertical')
        self.mostrar_pergunta()
        self.layout_principal.add_widget(self.container_pergunta)
        self.add_widget(self.layout_principal)

    def atualizar_header(self, instance, value):
        self.header_rect.pos = instance.pos
        self.header_rect.size = instance.size

    def mostrar_pergunta(self):
        self.container_pergunta.clear_widgets()
        if self.pergunta_atual >= len(self.perguntas):
            self.mostrar_resultado()
            return

        pergunta = self.perguntas[self.pergunta_atual]
        scroll = ScrollView()
        conteudo = BoxLayout(orientation='vertical', spacing=dp(20), size_hint_y=None, padding=dp(15))
        conteudo.bind(minimum_height=conteudo.setter('height'))

        card = CartaoElegante()
        card.height = dp(200)
        titulo_pergunta = Label(
            text=pergunta['titulo'], font_size=dp(20), bold=True,
            color=Cores.AZUL_ESCURO, size_hint_y=None, height=dp(60), halign='center', valign='middle'
        )
        titulo_pergunta.bind(size=titulo_pergunta.setter('text_size'))
        card.add_widget(titulo_pergunta)

        dica = Label(
            text=f"💡 {pergunta['dica']}", font_size=dp(14),
            color=[0.4, 0.4, 0.4, 1], size_hint_y=None, height=dp(50), halign='center', valign='middle'
        )
        dica.bind(size=dica.setter('text_size'))
        card.add_widget(dica)
        conteudo.add_widget(card)

        self.input_resposta = TextInput(
            hint_text='Digite sua resposta aqui...',
            multiline=True, size_hint_y=None, height=dp(150), font_size=dp(16)
        )
        conteudo.add_widget(self.input_resposta)

        botoes = BoxLayout(spacing=dp(10), size_hint_y=None, height=dp(60))
        if self.pergunta_atual > 0:
            btn_voltar = Button(
                text='← Voltar', background_color=[0.5, 0.5, 0.5, 1], font_size=dp(16)
            )
            btn_voltar.bind(on_press=self.voltar_pergunta)
            botoes.add_widget(btn_voltar)

        btn_proximo = BotaoDourado(
            text='Próxima →' if self.pergunta_atual < len(self.perguntas) - 1 else 'Gerar Plano ✓'
        )
        btn_proximo.bind(on_press=self.proxima_pergunta)
        botoes.add_widget(btn_proximo)

        conteudo.add_widget(botoes)
        scroll.add_widget(conteudo)
        self.container_pergunta.add_widget(scroll)

    def proxima_pergunta(self, instance):
        resposta = self.input_resposta.text.strip()
        if resposta:
            self.respostas[self.pergunta_atual] = resposta
        self.pergunta_atual += 1
        self.barra_progresso.value = self.pergunta_atual
        self.progresso_label.text = f'Pergunta {self.pergunta_atual + 1} de {len(self.perguntas)}'
        self.mostrar_pergunta()

    def voltar_pergunta(self, instance):
        if self.pergunta_atual > 0:
            self.pergunta_atual -= 1
            self.barra_progresso.value = self.pergunta_atual + 1
            self.progresso_label.text = f'Pergunta {self.pergunta_atual + 1} de {len(self.perguntas)}'
            self.mostrar_pergunta()

    def mostrar_resultado(self):
        self.container_pergunta.clear_widgets()
        scroll = ScrollView()
        resultado = BoxLayout(orientation='vertical', spacing=dp(15), size_hint_y=None, padding=dp(15))
        resultado.bind(minimum_height=resultado.setter('height'))

        titulo_card = CartaoElegante()
        titulo_card.height = dp(120)
        titulo_card.add_widget(Label(
            text='✨ SEU PLANO DE NEGÓCIOS ✨', font_size=dp(22), bold=True,
            color=Cores.DOURADO, size_hint_y=None, height=dp(40)
        ))
        titulo_card.add_widget(Label(
            text='Baseado nos princípios da Babilônia', font_size=dp(14), color=Cores.AZUL_ESCURO, italic=True
        ))
        resultado.add_widget(titulo_card)

        resumo_card = CartaoElegante()
        resumo_card.height = dp(300)
        resumo_card.add_widget(Label(
            text='📋 RESUMO EXECUTIVO', font_size=dp(18), bold=True,
            color=Cores.AZUL_ESCURO, size_hint_y=None, height=dp(35)
        ))
        resumo_texto = f'''🎯 IDEIA DE NEGÓCIO:
{self.respostas.get(0, 'Não informado')}

👥 PÚBLICO-ALVO:
{self.respostas.get(1, 'Não informado')}

💵 INVESTIMENTO INICIAL:
{self.respostas.get(2, 'Não informado')}

📊 FATURAMENTO PROJETADO:
{self.respostas.get(3, 'Não informado')}

🚀 ESTRATÉGIA DE MARKETING:
{self.respostas.get(4, 'Não informado')}
'''
        resumo_label = Label(text=resumo_texto, font_size=dp(13), color=Cores.AZUL_ESCURO, halign='left', valign='top')
        resumo_label.bind(size=resumo_label.setter('text_size'))
        resumo_card.add_widget(resumo_label)
        resultado.add_widget(resumo_card)

        recomendacoes_card = CartaoElegante()
        recomendacoes_card.height = dp(280)
        recomendacoes_card.add_widget(Label(
            text='🏛 SABEDORIA BABILÔNICA', font_size=dp(18), bold=True,
            color=Cores.DOURADO, size_hint_y=None, height=dp(35)
        ))
        recomendacoes_texto = '''
"O ouro chega alegremente e em quantidades crescentes àquele que reserva não menos que um décimo de seus ganhos para criar um patrimônio para seu futuro."

📌 PRÓXIMOS PASSOS:
1. Valide sua ideia com 10 clientes potenciais
2. Crie um protótipo ou versão mínima
3. Calcule seu ponto de equilíbrio
4. Reserve 10% do faturamento como lucro
5. Reinvista 30% no crescimento do negócio

⚠ AVISOS IMPORTANTES:
• Não misture finanças pessoais e empresariais
• Mantenha reserva de emergência (3-6 meses)
• Busque mentoria de quem já tem resultados
'''
        rec_label = Label(text=recomendacoes_texto, font_size=dp(12), color=Cores.AZUL_ESCURO, halign='left', valign='top')
        rec_label.bind(size=rec_label.setter('text_size'))
        recomendacoes_card.add_widget(rec_label)
        resultado.add_widget(recomendacoes_card)

        botoes = BoxLayout(spacing=dp(10), size_hint_y=None, height=dp(60))
        btn_novo = BotaoDourado(text='🔄 Novo Plano')
        btn_novo.bind(on_press=self.reiniciar)
        botoes.add_widget(btn_novo)

        btn_exportar = BotaoDourado(text='📄 Exportar PDF')
        btn_exportar.background_color = Cores.VERDE
        botoes.add_widget(btn_exportar)

        resultado.add_widget(botoes)
        scroll.add_widget(resultado)
        self.container_pergunta.add_widget(scroll)

    def reiniciar(self, instance):
        self.pergunta_atual = 0
        self.respostas = {}
        self.barra_progresso.value = 1
        self.progresso_label.text = 'Pergunta 1 de 5'
        self.mostrar_pergunta()


# ==================== NAVEGAÇÃO INFERIOR ====================
class BarraNavegacao(BoxLayout):
    """Barra de navegação inferior com 5 abas"""

    def __init__(self, screen_manager, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'horizontal'
        self.size_hint_y = None
        self.height = dp(70)
        self.spacing = dp(2)
        self.screen_manager = screen_manager

        with self.canvas.before:
            Color(*Cores.AZUL_ESCURO)
            self.rect = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self.atualizar_rect, size=self.atualizar_rect)

        abas = [
            ('🏛\nPrincipia', 'principia'),
            ('💰\nDinheiro', 'meu_dinheiro'),
            ('🏭\nNegócio', 'meu_negocio'),
            ('📈\nInvestir', 'investimentos'),
            ('🧠\nPlano', 'plano_mestre')
        ]
        for texto, tela in abas:
            btn = Button(
                text=texto, background_normal='', background_color=[0, 0, 0, 0],
                color=Cores.DOURADO, font_size=dp(12), bold=True
            )
            btn.bind(on_press=lambda x, t=tela: self.mudar_tela(t))
            self.add_widget(btn)

    def atualizar_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size

    def mudar_tela(self, nome_tela):
        self.screen_manager.current = nome_tela


# ==================== APLICATIVO PRINCIPAL ====================
class RiquezaBabilonicaApp(App):
    """Classe principal do aplicativo"""

    def build(self):
        self.title = '🏛 Riqueza Babilônica'
        self.db = DatabaseManager()

        layout_principal = BoxLayout(orientation='vertical')
        self.sm = ScreenManager()

        self.sm.add_widget(TelaPrincipia(self.db))
        self.sm.add_widget(TelaMeuDinheiro(self.db))
        self.sm.add_widget(TelaMeuNegocio(self.db))
        self.sm.add_widget(TelaInvestimentos(self.db))
        self.sm.add_widget(TelaPlanoMestre(self.db))

        layout_principal.add_widget(self.sm)
        self.nav_bar = BarraNavegacao(self.sm)
        layout_principal.add_widget(self.nav_bar)

        return layout_principal

    def on_stop(self):
        self.db.conn.close()


# ==================== EXECUÇÃO ====================
if __name__ == '__main__':
    RiquezaBabilonicaApp().run()