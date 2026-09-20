"""Aurora's native visual components; no external assets or web views."""
import math
from PySide6.QtCore import Qt, QTimer, QRectF, QPointF, QPropertyAnimation, QEasingCurve
from PySide6.QtGui import QColor, QPainter, QPen, QLinearGradient, QRadialGradient, QPainterPath, QIcon, QPixmap
from PySide6.QtWidgets import QWidget, QStackedWidget, QGraphicsOpacityEffect, QPushButton, QVBoxLayout, QHBoxLayout, QLabel, QScrollArea, QFrame, QApplication, QComboBox

STYLE = '''
QWidget { color: #eee9f8; font-family: 'Segoe UI'; font-size: 14px; }
QMainWindow, QDialog { background: #100e19; }
QWidget#sidebar { background: rgba(10, 10, 19, 218); border-right: 1px solid #30253d; }
QWidget#page { background: rgba(8, 9, 16, 108); }
QLabel { background: transparent; border: none; }
QLabel#brand { color: #fff0e4; font-size: 30px; font-weight: 700; letter-spacing: -1px; }
QLabel#title { font-size: 26px; font-weight: 650; letter-spacing: -0.5px; }
QLabel#muted { color: #aea2bf; font-size: 12px; }
QLabel#eyebrow { color: #e4a183; font-size: 10px; font-weight: 700; letter-spacing: 1.8px; }
QLabel#badge { background: #33232b; color: #ffd9c1; border: 1px solid #68404a; border-radius: 12px; padding: 6px 12px; font-size: 11px; }
QLabel#avatar { background: #55357a; color: #f5eaff; border: 1px solid #9862c5; border-radius: 19px; font-weight: 700; font-size: 16px; }
QLabel#sectionTitle { color: #eee5fa; font-weight: 650; font-size: 16px; }
QLabel#heroTitle { color: #faf4ff; font-size: 36px; font-weight: 650; letter-spacing: -1px; }
QLabel#heroText { color: #c8b9dc; font-size: 14px; }
QLabel#status { color: #b7a3cf; font-size: 11px; padding: 1px 2px; }
QFrame#card, QWidget#card { background: rgba(25, 20, 36, 224); border: 1px solid #34283f; border-radius: 17px; }
QFrame#composerCard { background: rgba(30, 23, 42, 234); border: 1px solid #544064; border-radius: 19px; }
QPushButton { background: #281e37; border: 1px solid #453154; border-radius: 10px; padding: 10px 14px; text-align: left; }
QPushButton:hover { background: #372646; border-color: #a876d5; }
QPushButton:pressed { background: #49305c; }
QPushButton:focus { border: 1px solid #cca2ff; }
QPushButton:disabled { color: #8b7b9b; background: #201929; border-color: #34283f; }
QPushButton#primary { background: qlineargradient(x1:0,y1:0,x2:1,y2:1,stop:0 #e17b57,stop:1 #96333c); color: #fffaf5; border: 1px solid #f0ad83; font-weight: 650; border-radius: 11px; padding: 11px 20px; }
QPushButton#primary:hover { background: qlineargradient(x1:0,y1:0,x2:1,y2:1,stop:0 #ef956c,stop:1 #b54348); }
QPushButton#primary:disabled { background: #523037; color: #c7a5a0; border-color: #70434a; }
QPushButton#nav { background: transparent; color: #ad9dbe; border: 1px solid transparent; border-radius: 11px; padding: 13px 14px; }
QPushButton#nav:hover { background: #21192e; color: #e7d7fa; }
QPushButton#nav:checked { background: qlineargradient(x1:0,y1:0,x2:1,y2:0,stop:0 #542936,stop:1 #281c28); color: #fff1e7; border: 1px solid #77424b; font-weight: 600; }
QPushButton#quiet { background: transparent; color: #b6a3ca; border: 1px solid transparent; padding: 7px 8px; font-size: 12px; }
QPushButton#quiet:hover { background: #2a1e39; color: #ead4ff; }
QPushButton#segment { background: transparent; border: none; color: #a897bb; padding: 9px 17px; }
QPushButton#segment:checked { background: #59313b; color: #fff0e6; border-radius: 9px; }
QLineEdit, QTextEdit, QTextBrowser, QComboBox, QListWidget, QDateTimeEdit { background: #15111f; border: 1px solid #3d2e4c; border-radius: 10px; padding: 10px 12px; selection-background-color: #764cab; color: #e9dff4; }
QLineEdit:focus, QTextEdit:focus, QComboBox:focus, QDateTimeEdit:focus { border-color: #b886f0; background: #1a1425; }
QComboBox { min-height: 23px; }
QComboBox::drop-down { border: none; width: 26px; }
QComboBox::down-arrow { image: none; }
QComboBox QAbstractItemView { background: #251a35; selection-background-color: #694198; color: #f2e7ff; padding: 5px; }
QTextEdit#composer { background: transparent; border: none; padding: 5px; font-size: 15px; }
QTextBrowser#chat { background: transparent; border: none; padding: 0px; }
QListWidget { background: #171220; padding: 8px; border: none; }
QListWidget::item { padding: 15px 10px; margin: 3px; border-radius: 9px; border: 1px solid #352743; background: #21182e; }
QListWidget::item:selected { background: #39244d; border-color: #9466b9; }
QListWidget::indicator { width: 18px; height: 18px; border: 1px solid #85659e; border-radius: 6px; background: #191021; }
QListWidget::indicator:checked { background: #a978e5; border-color: #d0aff7; }
QCheckBox { color: #bfb0d0; spacing: 8px; font-size: 12px; }
QCheckBox::indicator { width: 16px; height: 16px; border: 1px solid #795892; border-radius: 5px; background: #191221; }
QCheckBox::indicator:checked { background: #ad79ea; border-color: #d0aff7; }
QScrollArea { background: transparent; border: none; }
QScrollBar:vertical { background: transparent; width: 7px; margin: 3px 0; }
QScrollBar::handle:vertical { background: #503965; min-height: 30px; border-radius: 3px; }
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0px; }
QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical { background: transparent; }
QToolTip { background: #352344; color: #f3e6ff; border: 1px solid #765490; padding: 6px; }
'''

def line_icon(kind, color='#cdb2ed', size=24):
    pix = QPixmap(size, size); pix.fill(Qt.GlobalColor.transparent)
    p = QPainter(pix); p.setRenderHint(QPainter.RenderHint.Antialiasing); p.scale(size/24, size/24)
    p.setPen(QPen(QColor(color), 1.55, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin))
    p.setBrush(Qt.BrushStyle.NoBrush)
    if kind == 'chat':
        path = QPainterPath(); path.moveTo(6,4); path.lineTo(18,4); path.quadTo(21,4,21,7); path.lineTo(21,14); path.quadTo(21,17,18,17); path.lineTo(10,17); path.lineTo(4,21); path.lineTo(4,17); path.quadTo(2,16,2,14); path.lineTo(2,7); path.quadTo(2,4,6,4); p.drawPath(path)
        p.drawLine(7,9,16,9); p.drawLine(7,12,13,12)
    elif kind == 'list':
        p.drawRoundedRect(QRectF(5,4,15,17),3,3); p.drawLine(9,2,16,2)
        for y in (9,14): p.drawLine(9,y,10,y+1); p.drawLine(10,y+1,12,y-2); p.drawLine(15,y,17,y)
    elif kind == 'settings':
        for y,x in ((6,9),(12,16),(18,7)):
            p.drawLine(3,y,21,y); p.setBrush(QColor('#21162e')); p.drawEllipse(QPointF(x,y),2.4,2.4)
    elif kind == 'bag':
        p.drawRoundedRect(QRectF(4,7,16,14),3,3); p.drawArc(QRectF(8,2,8,11),0,180*16)
    elif kind == 'sun':
        p.drawEllipse(QPointF(12,12),4,4)
        for i in range(8):
            a=i*math.pi/4; p.drawLine(QPointF(12+7*math.cos(a),12+7*math.sin(a)),QPointF(12+10*math.cos(a),12+10*math.sin(a)))
    elif kind == 'spark':
        path=QPainterPath(); path.moveTo(12,2); path.quadTo(13,11,22,12); path.quadTo(13,13,12,22); path.quadTo(11,13,2,12); path.quadTo(11,11,12,2); p.drawPath(path)
    elif kind == 'arrow':
        p.drawLine(5,19,19,5); p.drawLine(7,5,19,5); p.drawLine(19,5,19,17)
    p.end(); return QIcon(pix)

class AmbientHero(QWidget):
    """A native, gently moving orbital illustration behind real accessible text."""
    def __init__(self, title, subtitle, compact=False, parent=None):
        super().__init__(parent); self.phase=0.; self.motion=True; self.compact=compact
        self.setMinimumHeight(180 if compact else 250)
        lay=QVBoxLayout(self); lay.setContentsMargins(28,23,28,23); lay.setSpacing(10)
        tag=QLabel('B E T E L G E U S E   /   IA LOCAL • PRIVACIDADE'); tag.setObjectName('eyebrow'); lay.addWidget(tag)
        lay.addStretch()
        self.heading=QLabel(title); self.heading.setObjectName('heroTitle'); self.heading.setWordWrap(True); lay.addWidget(self.heading)
        self.description=QLabel(subtitle); self.description.setObjectName('heroText'); self.description.setWordWrap(True); lay.addWidget(self.description)
        lay.addStretch()
        self.timer=QTimer(self); self.timer.setInterval(40); self.timer.timeout.connect(self.tick)
    def set_motion(self, enabled):
        self.motion=enabled
        if enabled and self.isVisible(): self.timer.start()
        else: self.timer.stop()
        self.update()
    def showEvent(self,event):
        super().showEvent(event)
        if self.motion: self.timer.start()
    def hideEvent(self,event): self.timer.stop(); super().hideEvent(event)
    def tick(self):
        self.phase += .009; self.update()
    def resizeEvent(self,event):
        super().resizeEvent(event)
        width = int(self.width() * (.64 if self.width()>550 else .88))
        self.heading.setMaximumWidth(width); self.description.setMaximumWidth(width)
        size=27 if self.compact else (29 if self.width()<800 else 36)
        self.heading.setStyleSheet(f'font-size:{size}px; font-weight:650; color:#faf4ff; background:transparent;')
    def paintEvent(self,event):
        p=QPainter(self); p.setRenderHint(QPainter.RenderHint.Antialiasing)
        rect=QRectF(self.rect()).adjusted(1,1,-1,-1); clip=QPainterPath(); clip.addRoundedRect(rect,21,21); p.setClipPath(clip)
        bg=QLinearGradient(0,0,self.width(),self.height()); bg.setColorAt(0,QColor('#241827')); bg.setColorAt(.52,QColor('#3a202b')); bg.setColorAt(1,QColor('#11131d')); p.fillRect(rect,bg)
        cx,cy=self.width()*.84,self.height()*.50; radius=min(self.height()*.32,100)
        if self.width()<550: p.setOpacity(.35)
        glow=QRadialGradient(QPointF(cx,cy),radius*2.8); glow.setColorAt(0,QColor(167,100,245,100)); glow.setColorAt(.55,QColor(101,62,176,38)); glow.setColorAt(1,QColor(80,40,130,0)); p.fillRect(rect,glow)
        for i in range(24):
            x=(i*71+21)%max(self.width(),1); y=(i*43+19)%max(self.height(),1)
            alpha=int(35+25*(1+math.sin(self.phase+i))/2); p.setPen(Qt.PenStyle.NoPen); p.setBrush(QColor(220,187,255,alpha)); p.drawEllipse(QPointF(x,y),1,1)
        p.save(); p.translate(cx,cy); p.rotate(-25)
        for scale in (1.35,1.65):
            p.setPen(QPen(QColor(194,144,245,45),1)); p.setBrush(Qt.BrushStyle.NoBrush); p.drawEllipse(QRectF(-radius*scale,-radius*.48*scale,2*radius*scale,radius*.96*scale))
        p.restore()
        sphere=QRadialGradient(QPointF(cx-radius*.3,cy-radius*.4),radius*1.65)
        sphere.setColorAt(0,QColor('#ffd0a0')); sphere.setColorAt(.22,QColor('#e78760')); sphere.setColorAt(.48,QColor('#9e3e4a')); sphere.setColorAt(.75,QColor('#402334')); sphere.setColorAt(1,QColor('#17121f'))
        p.setPen(QPen(QColor(227,191,255,130),1)); p.setBrush(sphere); p.drawEllipse(QPointF(cx,cy),radius,radius)
        p.save(); sphereclip=QPainterPath(); sphereclip.addEllipse(QPointF(cx,cy),radius-1,radius-1); p.setClipPath(sphereclip,Qt.ClipOperation.IntersectClip)
        for j in range(8):
            path=QPainterPath()
            for step in range(45):
                x=cx-radius+2*radius*step/44; y=cy-radius*.8+j*radius*.23+math.sin(step*.09+self.phase+j*.25)*radius*.2
                if step==0: path.moveTo(x,y)
                else: path.lineTo(x,y)
            p.setPen(QPen(QColor(244,217,255,35),1)); p.drawPath(path)
        p.restore()
        angle=self.phase; p.setPen(Qt.PenStyle.NoPen); p.setBrush(QColor('#e9c7ff')); p.drawEllipse(QPointF(cx+math.cos(angle)*radius*1.55,cy+math.sin(angle)*radius*.72),3,3)
        p.setOpacity(1); p.setClipping(False); p.setBrush(Qt.BrushStyle.NoBrush); p.setPen(QPen(QColor('#604078'),1)); p.drawRoundedRect(rect,21,21); p.end()

class GalaxyBackdrop(QWidget):
    """Animated astronomical backdrop drawn natively, with a quiet red-supergiant glow."""
    def __init__(self, parent=None):
        super().__init__(parent); self.phase=0.; self.motion=True
        self.timer=QTimer(self); self.timer.setInterval(55); self.timer.timeout.connect(self.tick)
        self.setAttribute(Qt.WidgetAttribute.WA_OpaquePaintEvent)
    def set_motion(self,enabled):
        self.motion=enabled
        if enabled and self.isVisible(): self.timer.start()
        else: self.timer.stop()
    def showEvent(self,event):
        super().showEvent(event)
        if self.motion: self.timer.start()
    def hideEvent(self,event): self.timer.stop(); super().hideEvent(event)
    def tick(self): self.phase += .004; self.update()
    def paintEvent(self,event):
        p=QPainter(self); p.setRenderHint(QPainter.RenderHint.Antialiasing)
        w,h=self.width(),self.height(); rect=QRectF(0,0,w,h)
        base=QLinearGradient(0,0,w,h); base.setColorAt(0,QColor('#070a12')); base.setColorAt(.42,QColor('#111321')); base.setColorAt(1,QColor('#0d0913')); p.fillRect(rect,base)
        # Large soft nebula fields.
        for cx,cy,rx,ry,col,alpha in ((w*.91,h*.14,w*.62,h*.48,'#b73528',78),(w*.12,h*.86,w*.70,h*.52,'#254d7b',62),(w*.55,h*.55,w*.65,h*.32,'#6f284b',34),(w*.32,h*.07,w*.42,h*.30,'#604a91',28)):
            g=QRadialGradient(QPointF(cx,cy),max(rx,ry)); c=QColor(col); c.setAlpha(alpha); g.setColorAt(0,c); c2=QColor(col); c2.setAlpha(alpha//3); g.setColorAt(.45,c2); c3=QColor(col); c3.setAlpha(0); g.setColorAt(1,c3); p.fillRect(rect,g)
        # Dust lanes and a slow stellar drift.
        p.save(); p.translate(w*.48,h*.52); p.rotate(-18+math.sin(self.phase)*1.5)
        for i in range(10):
            y=(i-5)*h*.065; path=QPainterPath(); path.moveTo(-w*.62,y)
            for x in range(-int(w*.62),int(w*.62),30): path.lineTo(x,y+math.sin(x*.008+i+self.phase)*h*.022)
            p.setPen(QPen(QColor(231,170,152,18 if i%2 else 28),max(1,h*.004))); p.drawPath(path)
        p.restore()
        p.setPen(Qt.PenStyle.NoPen)
        for i in range(130):
            x=(i*97+31)%max(w,1); y=(i*53+17)%max(h,1); twinkle=(math.sin(self.phase*18+i*.8)+1)/2; size=0.5+(i%3)*.35
            p.setBrush(QColor(225,228,245,int(26+80*twinkle))); p.drawEllipse(QPointF(x,y),size,size)
        # Betelgeuse: warm red supergiant, kept on the edge so copy remains readable.
        cx,cy=w*.88,h*.24; r=max(36,min(w,h)*.085); glow=QRadialGradient(QPointF(cx-r*.25,cy-r*.30),r*3.5); glow.setColorAt(0,QColor(255,155,94,145)); glow.setColorAt(.22,QColor(213,74,45,100)); glow.setColorAt(1,QColor(133,36,43,0)); p.fillRect(rect,glow)
        star=QRadialGradient(QPointF(cx-r*.3,cy-r*.35),r*1.4); star.setColorAt(0,QColor('#ffd0a0')); star.setColorAt(.3,QColor('#ef754b')); star.setColorAt(.68,QColor('#b63c3c')); star.setColorAt(1,QColor('#4b162b')); p.setBrush(star); p.drawEllipse(QPointF(cx,cy),r,r)
        for i in range(3): p.setPen(QPen(QColor(255,166,117,60-i*14),1)); p.drawEllipse(QPointF(cx,cy),r*(1.55+i*.38),r*(.8+i*.22))
        p.setOpacity(1); p.end()

class SuggestionCard(QPushButton):
    def __init__(self, title, subtitle, symbol, callback):
        super().__init__(); self.setCursor(Qt.CursorShape.PointingHandCursor); self.setMinimumHeight(102)
        self.setAccessibleName(title+'. '+subtitle); self.clicked.connect(callback)
        lay=QVBoxLayout(self); lay.setContentsMargins(16,12,16,12); lay.setSpacing(5)
        glyph=QLabel(); glyph.setPixmap(line_icon(symbol).pixmap(21,21)); lay.addWidget(glyph)
        name=QLabel(title+'  ↗'); name.setStyleSheet('font-size:13px; font-weight:600; background:transparent;'); lay.addWidget(name)
        desc=QLabel(subtitle); desc.setObjectName('muted'); desc.setWordWrap(True); lay.addWidget(desc)
        for w in (glyph,name,desc): w.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)

class FadeStack(QStackedWidget):
    def __init__(self):
        super().__init__(); self.motion=True
        self.fade=QGraphicsOpacityEffect(self); self.setGraphicsEffect(self.fade); self.fade.setOpacity(1)
        self.anim=QPropertyAnimation(self.fade,b'opacity',self); self.anim.setDuration(190); self.anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        self.currentChanged.connect(self.transition)
    def transition(self, index):
        self.anim.stop()
        if self.motion and self.isVisible():
            self.anim.setStartValue(.35); self.anim.setEndValue(1.); self.anim.start()
        else: self.fade.setOpacity(1)
    def set_motion(self,enabled):
        self.motion=enabled
        if not enabled: self.anim.stop(); self.fade.setOpacity(1)

class AuroraCombo(QComboBox):
    def paintEvent(self,event):
        super().paintEvent(event)
        p=QPainter(self); p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.setPen(QPen(QColor('#bba1d6'),1.6,Qt.PenStyle.SolidLine,Qt.PenCapStyle.RoundCap,Qt.PenJoinStyle.RoundJoin))
        x,y=self.width()-17,self.height()/2
        path=QPainterPath(); path.moveTo(x-4,y-2); path.lineTo(x,y+2); path.lineTo(x+4,y-2); p.drawPath(path); p.end()

class ConversationView(QScrollArea):
    def __init__(self):
        super().__init__(); self.setWidgetResizable(True); self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.content=QWidget(); self.content.setStyleSheet('background:transparent;'); self.setWidget(self.content)
        self.messages=QVBoxLayout(self.content); self.messages.setContentsMargins(2,5,9,5); self.messages.setSpacing(15); self.bubbles=[]
    def set_messages(self, history, name):
        while self.messages.count():
            item=self.messages.takeAt(0)
            if item.widget(): item.widget().deleteLater()
        self.bubbles=[]
        for msg in history:
            user=msg['role']=='user'; row=QWidget(); rl=QHBoxLayout(row); rl.setContentsMargins(0,0,0,0)
            bubble=QFrame(); bg='#30203f' if user else '#21192c'; border='#533564' if user else '#3b2c48'
            bubble.setStyleSheet(f'QFrame {{background:{bg}; border:1px solid {border}; border-radius:16px;}} QLabel {{border:none; background:transparent;}}')
            bl=QVBoxLayout(bubble); bl.setContentsMargins(18,11,18,17); bl.setSpacing(8)
            head=QHBoxLayout(); who=QLabel(name if user else '✦  Betelgeuse'); who.setTextFormat(Qt.TextFormat.PlainText); who.setStyleSheet('color:#f0b5a3; font-size:12px; font-weight:600;'); head.addWidget(who); head.addStretch()
            copy=QPushButton('Copiar'); copy.setObjectName('quiet'); copy.setAccessibleName('Copiar mensagem'); copy.setCursor(Qt.CursorShape.PointingHandCursor)
            copy.clicked.connect(lambda checked=False, text=msg['content'], btn=copy: self.copy_text(text,btn)); head.addWidget(copy); bl.addLayout(head)
            text=QLabel(msg['content']); text.setTextFormat(Qt.TextFormat.PlainText); text.setWordWrap(True); text.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse | Qt.TextInteractionFlag.TextSelectableByKeyboard); text.setStyleSheet('color:#eee5f6; font-size:15px; border:none; background:transparent;'); bl.addWidget(text)
            if user: rl.addStretch(1)
            rl.addWidget(bubble,9)
            if not user: rl.addStretch(1)
            self.messages.addWidget(row); self.bubbles.append(bubble)
        self.messages.addStretch(); self.resize_bubbles()
        QTimer.singleShot(0,self.scroll_bottom)
    def copy_text(self,text,btn):
        QApplication.clipboard().setText(text); btn.setText('Copiado ✓')
    def scroll_bottom(self):
        bar=self.verticalScrollBar(); bar.setValue(bar.maximum())
    def resize_bubbles(self):
        for bubble in self.bubbles: bubble.setMaximumWidth(max(200,int(self.viewport().width()*.90)))
    def resizeEvent(self,event):
        super().resizeEvent(event); self.resize_bubbles()
