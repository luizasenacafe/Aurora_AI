import os
import sys
import html
from pathlib import Path
from datetime import datetime

from PySide6.QtCore import Qt, QThread, Signal, QTimer, QDateTime, QSize
from PySide6.QtGui import QColor, QIcon, QPainter, QPixmap, QPen
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QComboBox, QTextEdit, QTextBrowser, QLineEdit, QStackedWidget,
    QFormLayout, QDialog, QDialogButtonBox, QMessageBox, QListWidget, QListWidgetItem,
    QDateTimeEdit, QSystemTrayIcon, QFrame, QScrollArea, QCheckBox, QSizePolicy)
from core import Store, DEFAULT_PERSONA, normalize_url, request_api
from visuals import AmbientHero, SuggestionCard, FadeStack, line_icon, ConversationView, AuroraCombo, GalaxyBackdrop

from visuals import STYLE

def icon():
    pix = QPixmap(256, 256)
    pix.fill(Qt.GlobalColor.transparent)
    p = QPainter(pix)
    p.setRenderHint(QPainter.RenderHint.Antialiasing)
    p.setBrush(QColor('#9d3f43')); p.setPen(Qt.PenStyle.NoPen)
    p.drawRoundedRect(8, 8, 240, 240, 62, 62)
    p.setPen(QPen(QColor('#fff0df'), 17, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin))
    p.drawRoundedRect(64, 58, 72, 140, 32, 32); p.drawArc(82, 58, 92, 72, -90*16, 180*16); p.drawArc(82, 126, 92, 72, -90*16, 180*16)
    p.setPen(QPen(QColor('#ffb78f'), 7, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
    p.drawLine(187, 45, 187, 79); p.drawLine(171, 62, 203, 62)
    p.end()
    return QIcon(pix)

def label(text, kind=None):
    w = QLabel(text)
    w.setTextFormat(Qt.TextFormat.PlainText)
    w.setWordWrap(kind != 'eyebrow')
    if kind: w.setObjectName(kind)
    return w

def button(text, callback, primary=False):
    w = QPushButton(text)
    w.setCursor(Qt.CursorShape.PointingHandCursor)
    if primary: w.setObjectName('primary')
    w.clicked.connect(callback)
    return w

class Worker(QThread):
    result = Signal(object)
    failure = Signal(str)
    def __init__(self, fn):
        super().__init__(); self.fn = fn
    def run(self):
        try: self.result.emit(self.fn())
        except Exception as exc: self.failure.emit(str(exc))

class ProfileDialog(QDialog):
    def __init__(self, parent, profile=None, first=False):
        super().__init__(parent)
        self.setWindowTitle('Seu espaço de IA • Betelgeuse A.I.')
        self.setMinimumWidth(600); self.resize(660, 710)
        lay = QVBoxLayout(self); lay.setContentsMargins(24,24,24,24); lay.setSpacing(12)
        hero = AmbientHero('Seu espaço de IA\ncomeça aqui.' if first else 'Cada conversa,\num universo.', 'Crie um perfil para personalizar suas conversas com o modelo local.', compact=True)
        hero.heading.setStyleSheet('font-size:27px; font-weight:650; color:#fbf4ff;')
        hero.setFixedHeight(190); hero.set_motion(parent.store.get('motion', '1') == '1'); lay.addWidget(hero)
        lay.addWidget(label('01  /  VAMOS NOS CONHECER' if first else 'PERFIL  /  SEU JEITO DE CONVERSAR', 'eyebrow'))
        lay.addWidget(label('Comece com um nome e algumas preferências. Você pode criar vários espaços de conversa.', 'muted'))
        self.name = QLineEdit(profile['name'] if profile else '')
        self.name.setPlaceholderText('Como podemos chamar você?'); self.name.setMaxLength(80)
        self.details = QTextEdit(); self.details.setFixedHeight(85)
        self.details.setPlaceholderText('Contexto, interesses e instruções úteis para este espaço…')
        self.persona = QTextEdit(); self.persona.setFixedHeight(75)
        self.persona.setPlaceholderText('Ex.: seja objetiva, use exemplos simples e me ajude a organizar o dia.')
        if profile:
            self.details.setPlainText(profile['details']); self.persona.setPlainText(profile['persona'])
        for title, w in [('Nome', self.name), ('Sobre esta pessoa', self.details), ('Como a IA deve conversar', self.persona)]:
            lay.addWidget(label(title)); lay.addWidget(w)
        self.error = label('', 'muted'); lay.addWidget(self.error)
        actions = QHBoxLayout(); actions.addWidget(button('Agora não', self.reject)); actions.addStretch()
        actions.addWidget(button('Criar meu espaço  ↗' if first else 'Salvar meu perfil  ↗', self.validate, True)); lay.addLayout(actions)
    def validate(self):
        if not self.name.text().strip(): self.error.setText('Preencha o nome para continuar.'); return
        if len(self.details.toPlainText()) + len(self.persona.toPlainText()) > 6000:
            self.error.setText('Resuma as informações do perfil em até 6.000 caracteres.'); return
        self.accept()

class TutorialDialog(QDialog):
    def __init__(self, parent):
        super().__init__(parent)
        self.setWindowTitle('Primeiros passos • Betelgeuse A.I.')
        self.setMinimumWidth(720); self.resize(760, 620)
        lay = QVBoxLayout(self); lay.setContentsMargins(24,24,24,24); lay.setSpacing(14)
        hero = AmbientHero('IA local.\nPrivacidade real.', 'A Betelgeuse conecta você a modelos que rodam no seu computador ou no seu próprio servidor.', compact=True)
        hero.setFixedHeight(180); hero.set_motion(parent.store.get('motion', '1') == '1'); lay.addWidget(hero)
        lay.addWidget(label('COMO COMEÇAR  /  3 PASSOS', 'eyebrow'))
        lay.addWidget(label('Você controla o modelo, o servidor e os seus dados.', 'muted'))
        steps = [
            ('01', 'Baixe um modelo', 'Abra o LM Studio, escolha um modelo compatível e carregue-o. A Betelgeuse usa o modelo que estiver disponível lá.'),
            ('02', 'Conecte o servidor', 'Em Configurações, use http://localhost:1234/v1 para este PC ou o endereço HTTPS do seu servidor. Teste a conexão e selecione o modelo.'),
            ('03', 'Converse com privacidade', 'Suas mensagens vão apenas para o servidor escolhido. A Betelgeuse não precisa enviar prompts para as grandes plataformas.'),
        ]
        for n, title, body in steps:
            card, cl = parent.card(title, body) if hasattr(parent, 'card') else (QFrame(), QVBoxLayout())
            card.setObjectName('card'); badge = label(n, 'badge'); cl.insertWidget(0, badge); lay.addWidget(card)
        actions=QHBoxLayout(); actions.addStretch(); actions.addWidget(button('Abrir configurações', self.open_settings)); actions.addWidget(button('Entendi, começar  ↗', self.accept, True)); lay.addLayout(actions)
    def open_settings(self):
        self.done(2)

class Composer(QTextEdit):
    submitted = Signal()
    def keyPressEvent(self, event):
        if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter) and not event.modifiers() & Qt.KeyboardModifier.ShiftModifier:
            self.submitted.emit(); return
        super().keyPressEvent(event)

class Aurora(QMainWindow):
    def __init__(self, store):
        super().__init__(); self.store = store; self.jobs = []; self.busy = False; self.token = ''; self.notified = set()
        self.setWindowTitle('Betelgeuse A.I. • IA local e privada'); self.setWindowIcon(icon())
        self.resize(1240, 860); self.setMinimumSize(980, 720)
        root = GalaxyBackdrop(); self.setCentralWidget(root); self.galaxy=root; row = QHBoxLayout(root); row.setContentsMargins(0,0,0,0); row.setSpacing(0)
        side = QWidget(); side.setObjectName('sidebar'); side.setFixedWidth(240)
        nav = QVBoxLayout(side); nav.setContentsMargins(20,30,20,22); nav.setSpacing(10)
        nav.addWidget(label('✦ betelgeuse', 'brand')); nav.addWidget(label('IA LOCAL  /  PRIVACIDADE', 'eyebrow')); nav.addSpacing(28)
        nav.addWidget(label('SEU UNIVERSO', 'eyebrow'))
        self.stack = FadeStack(); self.nav_buttons=[]
        for i, (text, symbol) in enumerate([('Chat local', 'chat'), ('Modelos locais', 'list'), ('Configurações', 'settings')]):
            btn = button('  '+text, lambda checked=False, idx=i: self.stack.setCurrentIndex(idx))
            btn.setObjectName('nav'); btn.setCheckable(True); btn.setIcon(line_icon(symbol)); btn.setIconSize(QSize(20,20)); self.nav_buttons.append(btn); nav.addWidget(btn)
        self.stack.currentChanged.connect(self.update_navigation)
        nav.addSpacing(30); nav.addWidget(label('ESPAÇOS DE CONVERSA', 'eyebrow'))
        profile_card = QFrame(); profile_card.setObjectName('card'); pl = QVBoxLayout(profile_card); pl.setContentsMargins(12,15,12,12); pl.setSpacing(9)
        self.avatar = label('A', 'avatar'); self.avatar.setFixedSize(38,38); self.avatar.setAlignment(Qt.AlignmentFlag.AlignCenter); pl.addWidget(self.avatar)
        self.profiles = AuroraCombo(); self.profiles.setAccessibleName('Perfil da pessoa'); self.profiles.currentIndexChanged.connect(self.profile_changed); pl.addWidget(self.profiles)
        self.edit_btn = button('Personalizar espaço  ↗', self.edit_profile); self.edit_btn.setObjectName('quiet'); pl.addWidget(self.edit_btn); nav.addWidget(profile_card)
        self.add_btn = button('+  Novo espaço', self.add_profile); self.add_btn.setObjectName('quiet'); nav.addWidget(self.add_btn)
        nav.addStretch()
        note = QFrame(); note.setObjectName('card'); nl=QVBoxLayout(note); nl.setContentsMargins(15,17,15,17)
        nl.addWidget(label('RODA NO SEU ESPAÇO', 'eyebrow')); nl.addWidget(label('Seu modelo.\nSeus dados.', 'muted')); nav.addWidget(note); nav.addSpacing(8)
        nav.addWidget(label('BETELGEUSE  /  LOCAL FIRST', 'eyebrow'))
        row.addWidget(side); row.addWidget(self.stack, 1)
        self.make_chat(); self.make_organizer(); self.make_settings(); self.refresh_profiles(); self.apply_motion(); self.update_navigation(0)
        self.tray = QSystemTrayIcon(icon(), self); self.tray.setToolTip('Betelgeuse A.I. • Lembretes'); self.tray.show()
        self.timer = QTimer(self); self.timer.timeout.connect(self.check_reminders); self.timer.start(15000)
        QTimer.singleShot(120, self.first_run)
    def first_run(self):
        # Existing workspaces open directly; the guided tour is for a brand-new install.
        if not self.store.profiles() and self.store.get('tutorial_seen', '0') != '1':
            d = TutorialDialog(self)
            result = d.exec()
            self.store.set('tutorial_seen', '1')
            if result == 2: self.stack.setCurrentIndex(2)
        if not self.store.profiles(): self.add_profile(first=True)

    def page(self, title, subtitle):
        w = QWidget(); w.setObjectName('page'); lay = QVBoxLayout(w); lay.setContentsMargins(30,25,30,22); lay.setSpacing(14)
        header=QHBoxLayout(); header.addWidget(label('BETELGEUSE  /  '+['CHAT LOCAL','MODELOS LOCAIS','CONFIGURAÇÕES'][self.stack.count()], 'eyebrow')); header.addStretch()
        badge=label('✦  Sem nuvem obrigatória', 'badge'); header.addWidget(badge); lay.addLayout(header)
        lay.addWidget(label(title, 'title')); lay.addWidget(label(subtitle, 'muted')); self.stack.addWidget(w)
        return lay
    def update_navigation(self, index):
        for i, btn in enumerate(self.nav_buttons): btn.setChecked(i == index)
    def apply_motion(self):
        enabled = self.store.get('motion', '1') == '1'
        self.stack.set_motion(enabled)
        self.galaxy.set_motion(enabled)
        for hero in self.findChildren(AmbientHero): hero.set_motion(enabled)
    def card(self, title, subtitle=None):
        card=QFrame(); card.setObjectName('card'); layout=QVBoxLayout(card); layout.setContentsMargins(20,18,20,18); layout.setSpacing(12)
        layout.addWidget(label(title, 'sectionTitle'))
        if subtitle: layout.addWidget(label(subtitle, 'muted'))
        return card, layout
    def current(self):
        pid = self.profiles.currentData()
        return next((p for p in self.store.profiles() if p['id'] == pid), None)
    def refresh_profiles(self, pid=None):
        pid = pid or self.profiles.currentData(); self.profiles.blockSignals(True); self.profiles.clear()
        for p in self.store.profiles(): self.profiles.addItem(p['name'], p['id'])
        idx = self.profiles.findData(pid)
        if idx >= 0: self.profiles.setCurrentIndex(idx)
        self.profiles.blockSignals(False); self.profile_changed()
    def add_profile(self, checked=False, first=False):
        d = ProfileDialog(self, first=first)
        if d.exec():
            pid = self.store.save_profile(d.name.text(), d.details.toPlainText(), d.persona.toPlainText())
            self.refresh_profiles(pid)
    def edit_profile(self):
        p = self.current()
        if p is None: return
        d = ProfileDialog(self, p)
        if d.exec():
            self.store.save_profile(d.name.text(), d.details.toPlainText(), d.persona.toPlainText(), p['id']); self.refresh_profiles(p['id'])
    def profile_changed(self):
        p=self.current()
        self.avatar.setText(p['name'][:1].upper() if p else 'A')
        self.render_chat(); self.refresh_items()
    def make_chat(self):
        lay = self.page('Sua inteligência fica no seu espaço.', 'Baixe modelos, conecte ao LM Studio e converse sem entregar seus dados às grandes plataformas.')
        self.chat_area=QStackedWidget(); self.chat_area.setMinimumHeight(205)
        self.hero=AmbientHero('Olá. Bem-vindo\nao seu universo.', 'Sou a Betelgeuse: uma interface para rodar IA localmente, com mais controle e privacidade.')
        self.hero.setMinimumHeight(205)
        self.chat_area.addWidget(self.hero)
        self.chat = ConversationView(); self.chat_area.addWidget(self.chat); lay.addWidget(self.chat_area, 1)
        lead=QHBoxLayout(); lead.addWidget(label('UM PONTO DE PARTIDA', 'eyebrow')); lead.addStretch(); hint=label('Escolha uma ideia ou escreva a sua', 'muted'); hint.setWordWrap(False); lead.addWidget(hint); lay.addLayout(lead)
        chips = QHBoxLayout()
        self.suggestions=[]
        for title, subtitle, symbol, text in [('Escolher um modelo', 'Veja o que está carregado.', 'spark', 'Quais modelos estão disponíveis e qual combina com meu objetivo?'), ('Testar conexão', 'LM Studio ou servidor.', 'sun', 'Explique como confirmar que minha conexão com o servidor local está funcionando.'), ('Entender privacidade', 'Seus dados sob controle.', 'bag', 'Explique o caminho que minha mensagem percorre quando uso uma IA local.')]:
            card=SuggestionCard(title, subtitle, symbol, lambda checked=False, t=text: self.use_suggestion(t)); self.suggestions.append(card); chips.addWidget(card,1)
        lay.addLayout(chips)
        self.status = label('○  Conecte um modelo em Configurações para começar.', 'status'); lay.addWidget(self.status)
        box=QFrame(); box.setObjectName('composerCard'); compose=QVBoxLayout(box); compose.setContentsMargins(14,10,14,10); compose.setSpacing(5)
        self.composer = Composer(); self.composer.setObjectName('composer'); self.composer.setFixedHeight(60)
        self.composer.setPlaceholderText('Pergunte ao seu modelo local…'); self.composer.setAccessibleName('Sua mensagem para Betelgeuse'); self.composer.submitted.connect(self.send); compose.addWidget(self.composer)
        bottom=QHBoxLayout(); hint=label('✦  No seu ritmo. Do seu jeito.', 'muted'); hint.setWordWrap(False); bottom.addWidget(hint); bottom.addStretch()
        self.send_btn = button('Enviar  ↗', self.send, True); bottom.addWidget(self.send_btn); compose.addLayout(bottom); lay.addWidget(box)
        lay.addWidget(label('Enter para enviar  ·  Shift + Enter para nova linha  ·  Confira informações importantes.', 'muted'))
    def use_suggestion(self, text):
        if self.busy: return
        self.composer.setPlainText(text); self.composer.setFocus()
    def render_chat(self):
        p = self.current()
        history = self.store.history(p['id']) if p else []
        if not history:
            name = p['name'].split()[0] if p else ''
            name = name[:20] + '…' if len(name)>20 else name
            self.hero.heading.setText(f'Olá, {name}.\nO que vamos explorar?' if name else 'IA local.\nPrivacidade real.')
            self.hero.heading.setTextFormat(Qt.TextFormat.PlainText); self.chat_area.setCurrentIndex(0)
        else:
            self.chat_area.setCurrentIndex(1)
            self.chat.set_messages(history, p['name'])
        bar = self.chat.verticalScrollBar(); bar.setValue(bar.maximum())
    def launch(self, fn, success, failure, cleanup=None):
        job = Worker(fn); self.jobs.append(job)
        job.result.connect(success); job.failure.connect(failure)
        def finished():
            if cleanup: cleanup()
            self.jobs.remove(job); job.deleteLater()
        job.finished.connect(finished); job.start()
    def set_busy(self, busy):
        self.busy = busy
        for w in [self.send_btn, self.profiles, self.edit_btn, self.add_btn, self.composer]: w.setEnabled(not busy)
        for w in self.suggestions: w.setEnabled(not busy)
        self.send_btn.setText('Pensando…' if busy else 'Enviar  ↗')
    def send(self):
        if self.busy: return
        p = self.current(); text = self.composer.toPlainText().strip()
        if not p: self.add_profile(); return
        if not text: return
        if len(text) > 8000: self.status.setText('Divida sua mensagem em partes de até 8.000 caracteres.'); return
        model = self.store.get('model')
        if not model:
            self.stack.setCurrentIndex(2); self.connection.setText('Teste a conexão, selecione o modelo e salve para começar.'); return
        base, token = self.store.get('server', 'http://localhost:1234/v1'), self.token
        payload = {'model': model, 'messages': self.store.messages_for(p, text), 'temperature': 0.7, 'max_tokens': 1200, 'stream': False}
        self.set_busy(True); self.status.setText('A Betelgeuse está pensando… A primeira resposta pode levar mais tempo.')
        self.store.add_message(p['id'], 'user', text); self.composer.clear(); self.render_chat()
        def work():
            data = request_api(base, token, '/chat/completions', payload)
            content = data['choices'][0]['message'].get('content')
            if not isinstance(content, str) or not content.strip(): raise ValueError('O modelo retornou uma resposta vazia. Tente novamente ou escolha outro modelo.')
            return content
        def done(content):
            self.store.add_message(p['id'], 'assistant', content); self.render_chat(); self.status.setText('Resposta recebida • conversa salva neste computador.')
        def failed(msg):
            # Remove the unanswered turn so retrying does not duplicate the context.
            self.store.db.execute('DELETE FROM messages WHERE id=(SELECT MAX(id) FROM messages WHERE profile=? AND role=?)', (p['id'], 'user')); self.store.db.commit()
            self.render_chat(); self.composer.setPlainText(text); self.status.setText(msg)
        self.launch(work, done, failed, lambda: self.set_busy(False))
    def make_settings(self):
        lay = self.page('Controle o seu universo de IA.', 'Escolha o servidor, o modelo e as instruções que a Betelgeuse usará.')
        scroll=QScrollArea(); scroll.setWidgetResizable(True); content=QWidget(); content.setObjectName('page'); body=QVBoxLayout(content); body.setContentsMargins(0,0,5,0); body.setSpacing(16); scroll.setWidget(content); lay.addWidget(scroll,1)
        connection_card, connection_layout = self.card('01  /  Conexão', 'Use o LM Studio neste PC ou a API privada do seu servidor.'); body.addWidget(connection_card)
        form = QFormLayout(); form.setSpacing(14)
        self.server = QLineEdit(self.store.get('server', 'http://localhost:1234/v1'))
        self.key = QLineEdit(); self.key.setEchoMode(QLineEdit.EchoMode.Password); self.key.setPlaceholderText('Opcional • mantido só enquanto a Betelgeuse está aberta')
        self.models = AuroraCombo(); self.models.setEditable(True)
        if self.store.get('model'): self.models.addItem(self.store.get('model'))
        form.addRow('Endereço do servidor', self.server); form.addRow('Token de acesso', self.key); form.addRow('Modelo', self.models); connection_layout.addLayout(form)
        self.test_btn = button('Testar conexão e buscar modelos  ↗', self.test_connection); connection_layout.addWidget(self.test_btn)
        self.connection = label('Neste PC: localhost. Em outro computador: use o IP do PC que roda o LM Studio.', 'muted'); connection_layout.addWidget(self.connection)
        persona_card, persona_layout = self.card('02  /  Personalidade', 'Defina o comportamento padrão do seu modelo. Cada espaço também pode ter preferências.'); body.addWidget(persona_card)
        self.personality = QTextEdit(); self.personality.setMinimumHeight(100); self.personality.setMaximumHeight(150); self.personality.setPlainText(self.store.get('persona', DEFAULT_PERSONA)); persona_layout.addWidget(self.personality)
        persona_layout.addWidget(label('As mudanças valem para as próximas mensagens. Ajustes por conversa ficam em “Personalizar espaço”.', 'muted'))
        look_card, look_layout=self.card('03  /  Seu ritmo'); body.addWidget(look_card)
        self.reduce_motion=QCheckBox('Reduzir animações e efeitos de movimento'); self.reduce_motion.setChecked(self.store.get('motion','1')=='0'); self.reduce_motion.toggled.connect(self.change_motion); look_layout.addWidget(self.reduce_motion)
        body.addWidget(label('Seus dados ficam neste PC. O perfil ativo e as mensagens recentes são enviados ao servidor escolhido. Os perfis ainda não têm senha individual.', 'muted')); body.addStretch()
        footer=QHBoxLayout(); self.saved_note=label('Personalize. Salve. Mantenha o controle.', 'muted'); footer.addWidget(self.saved_note,1); footer.addWidget(button('Salvar configurações  ↗', self.save_settings, True)); lay.addLayout(footer)
    def change_motion(self, reduced):
        self.store.set('motion', '0' if reduced else '1'); self.apply_motion()
    def test_connection(self):
        try: base = normalize_url(self.server.text())
        except ValueError as exc: self.connection.setText(str(exc)); return
        token = self.key.text().strip(); self.test_btn.setEnabled(False); self.connection.setText('Procurando o servidor…')
        def done(data):
            ids = [m['id'] for m in data.get('data', []) if isinstance(m.get('id'), str)]
            current = self.models.currentText(); self.models.clear(); self.models.addItems(ids)
            if current in ids: self.models.setCurrentText(current)
            self.connection.setText('Conexão feita! Escolha um modelo de conversa e salve.' if ids else 'Servidor encontrado, mas sem modelos. Baixe/carregue um modelo no LM Studio e teste novamente.')
        self.launch(lambda: request_api(base, token, '/models'), done, self.connection.setText, lambda: self.test_btn.setEnabled(True))
    def save_settings(self):
        try: base = normalize_url(self.server.text())
        except ValueError as exc: self.connection.setText(str(exc)); return
        if len(self.personality.toPlainText()) > 6000: self.connection.setText('Resuma a personalidade em até 6.000 caracteres.'); return
        self.store.set('server', base); self.store.set('model', self.models.currentText().strip())
        self.store.set('persona', self.personality.toPlainText().strip() or DEFAULT_PERSONA); self.token = self.key.text().strip()
        self.connection.setText('Configurações salvas. As próximas mensagens usarão essas escolhas.'); self.status.setText('Configurações atualizadas • pronta para conversar quando o servidor estiver disponível.')
        self.saved_note.setText('✓  Tudo salvo. A Betelgeuse está do seu jeito.')
    def make_organizer(self):
        lay = self.page('Modelos locais.', 'Baixe e carregue modelos no LM Studio; a Betelgeuse encontra e usa o que estiver disponível.')
        self.kind = AuroraCombo(); self.kind.addItems(['Notas locais', 'Lembretes']); self.kind.currentIndexChanged.connect(self.refresh_items); self.kind.hide()
        tabs=QHBoxLayout(); self.kind_buttons=[]
        for i,title in enumerate(['Notas locais', 'Lembretes']):
            btn=button(title, lambda checked=False, idx=i: self.kind.setCurrentIndex(idx)); btn.setObjectName('segment'); btn.setCheckable(True); self.kind_buttons.append(btn); tabs.addWidget(btn)
        tabs.addStretch(); self.item_count=label('0 itens', 'badge'); tabs.addWidget(self.item_count); lay.addLayout(tabs)
        list_card=QFrame(); list_card.setObjectName('card'); ll=QVBoxLayout(list_card); ll.setContentsMargins(10,10,10,10)
        self.item_pages=QStackedWidget(); self.items = QListWidget(); self.items.itemChanged.connect(self.toggle_item); self.item_pages.addWidget(self.items)
        empty=QWidget(); el=QVBoxLayout(empty); el.setContentsMargins(30,25,30,25); el.addStretch(); glyph=label('✦'); glyph.setStyleSheet('color:#bd8bea; font-size:44px;'); glyph.setAlignment(Qt.AlignmentFlag.AlignCenter); el.addWidget(glyph)
        self.empty_title=label('O próximo passo começa aqui.', 'sectionTitle'); self.empty_title.setAlignment(Qt.AlignmentFlag.AlignCenter); el.addWidget(self.empty_title)
        self.empty_description=label('Adicione o primeiro item e deixe a lista cuidar dos detalhes.', 'muted'); self.empty_description.setAlignment(Qt.AlignmentFlag.AlignCenter); el.addWidget(self.empty_description); el.addStretch(); self.item_pages.addWidget(empty); ll.addWidget(self.item_pages); lay.addWidget(list_card,1)
        entry, entry_layout=self.card('O que vamos organizar?'); lay.addWidget(entry)
        self.item_title = QLineEdit(); self.item_title.setPlaceholderText('Ex.: uma ideia, um experimento, uma anotação…'); self.item_title.setMaxLength(300); self.item_title.returnPressed.connect(self.add_item); entry_layout.addWidget(self.item_title)
        self.due = QDateTimeEdit(QDateTime.currentDateTime().addSecs(3600)); self.due.setCalendarPopup(True); self.due.setDisplayFormat('dd/MM/yyyy HH:mm'); entry_layout.addWidget(self.due)
        row = QHBoxLayout(); self.remove_btn=button('Remover selecionado', self.remove_item); self.remove_btn.setObjectName('quiet'); row.addWidget(self.remove_btn); row.addStretch(); row.addWidget(button('Adicionar à lista  +', self.add_item, True)); entry_layout.addLayout(row)
        self.reminder_note = label('Marque os itens quando concluir. Para receber lembretes, mantenha a Betelgeuse aberta e o computador acordado.', 'muted'); lay.addWidget(self.reminder_note)
    def refresh_items(self):
        if not hasattr(self, 'items'): return
        self.due.setVisible(self.kind.currentIndex() == 1); self.items.blockSignals(True); self.items.clear(); p = self.current()
        if p:
            for r in self.store.db.execute('SELECT * FROM items WHERE profile=? AND kind=? ORDER BY done,id', (p['id'], self.kind.currentText())):
                suffix = '  •  ' + datetime.fromisoformat(r['due']).strftime('%d/%m %H:%M') if r['due'] else ''
                item = QListWidgetItem(r['title'] + suffix); item.setData(Qt.ItemDataRole.UserRole, r['id'])
                item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable); item.setCheckState(Qt.CheckState.Checked if r['done'] else Qt.CheckState.Unchecked)
                font=item.font(); font.setStrikeOut(bool(r['done'])); item.setFont(font); self.items.addItem(item)
        self.items.blockSignals(False)
        self.item_pages.setCurrentIndex(0 if self.items.count() else 1)
        self.update_item_count()
        self.remove_btn.setEnabled(self.items.count()>0)
        for i, btn in enumerate(self.kind_buttons): btn.setChecked(i==self.kind.currentIndex())
        self.item_title.setPlaceholderText('Ex.: regar as plantas, fazer uma pausa…' if self.kind.currentIndex() else 'Ex.: uma ideia, um experimento, uma anotação…')
        self.empty_title.setText('Um pouco de espaço na memória.' if self.kind.currentIndex() else 'Sua próxima compra começa aqui.')
        self.empty_description.setText('Adicione um lembrete e escolha quando quer ser avisado.' if self.kind.currentIndex() else 'Adicione uma anotação local para não perder o fio do seu experimento.')
    def update_item_count(self):
        total=self.items.count(); done=sum(self.items.item(i).checkState()==Qt.CheckState.Checked for i in range(total))
        self.item_count.setText(f'{done} de {total} concluídos' if total else 'Tudo em seu tempo')
    def add_item(self):
        p = self.current(); title = self.item_title.text().strip()
        if not p: self.add_profile(); return
        if not title: return
        due = self.due.dateTime().toPython().isoformat(timespec='seconds') if self.kind.currentIndex() else None
        if due and datetime.fromisoformat(due) <= datetime.now():
            QMessageBox.information(self, 'Horário do lembrete', 'Escolha um horário no futuro.'); return
        self.store.db.execute('INSERT INTO items(profile,kind,title,due) VALUES (?,?,?,?)', (p['id'], self.kind.currentText(), title, due)); self.store.db.commit(); self.item_title.clear(); self.refresh_items()
    def toggle_item(self, item):
        self.store.db.execute('UPDATE items SET done=? WHERE id=?', (int(item.checkState() == Qt.CheckState.Checked), item.data(Qt.ItemDataRole.UserRole))); self.store.db.commit()
        self.items.blockSignals(True)
        font=item.font(); font.setStrikeOut(item.checkState()==Qt.CheckState.Checked); item.setFont(font)
        self.items.blockSignals(False)
        self.update_item_count()
    def remove_item(self):
        item = self.items.currentItem()
        if item:
            self.store.db.execute('DELETE FROM items WHERE id=?', (item.data(Qt.ItemDataRole.UserRole),)); self.store.db.commit(); self.refresh_items()
    def check_reminders(self):
        rows = self.store.db.execute('SELECT items.*,profiles.name FROM items JOIN profiles ON profiles.id=items.profile WHERE done=0 AND due IS NOT NULL AND due<=?', (datetime.now().isoformat(timespec='seconds'),)).fetchall()
        fresh = [r for r in rows if r['id'] not in self.notified]
        if not fresh: return
        self.notified.update(r['id'] for r in fresh)
        text = '\n'.join(f"{r['name']}: {r['title']}" for r in fresh)
        self.tray.showMessage('Betelgeuse A.I. • Hora de lembrar', text, QSystemTrayIcon.MessageIcon.Information, 10000)
        box = QMessageBox(self); box.setWindowTitle('Betelgeuse A.I. • Seus lembretes'); box.setText(text); box.setInformativeText('Marque como concluído em Organização quando terminar.'); box.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose); box.open()
    def closeEvent(self, event):
        if self.jobs:
            QMessageBox.information(self, 'Conexão em andamento', 'Aguarde a resposta ou o tempo limite da conexão antes de fechar.'); event.ignore(); return
        self.tray.hide(); event.accept()

def main():
    app = QApplication(sys.argv); app.setApplicationName('Betelgeuse A.I.'); app.setStyleSheet(STYLE); app.setWindowIcon(icon())
    folder = Path(os.environ.get('AURORA_DATA_DIR') or Path(os.environ.get('LOCALAPPDATA', str(Path.home()))) / 'AuroraAI')
    window = Aurora(Store(folder / 'aurora.db')); window.show()
    if '--smoke-test' in sys.argv:
        QTimer.singleShot(1500, app.quit)
    sys.exit(app.exec())

if __name__ == '__main__': main()
