"""Local-only desktop control panel. No remote administration endpoint."""
import sys
import json
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'source'))
from PySide6.QtCore import QTimer, Qt
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QListWidget, QListWidgetItem, QInputDialog, QMessageBox, QDialog, QCheckBox
from aurora import label,button,icon
from visuals import STYLE
from storage import Keys,read_config,data_dir
import manage

class Panel(QWidget):
    def __init__(self):
        super().__init__(); self.keys=Keys(); self.setWindowTitle('Betelgeuse A.I. • Central do servidor'); self.setWindowIcon(icon()); self.resize(740,710); self.setStyleSheet('Panel {background:#100e19;}')
        lay=QVBoxLayout(self); lay.setContentsMargins(30,25,30,25); lay.setSpacing(14)
        lay.addWidget(label('AURORA  /  CENTRAL DO SERVIDOR','eyebrow')); lay.addWidget(label('Sua casa conectada.','title'))
        lay.addWidget(label('O modelo roda neste PC. A Betelgeuse de outras pessoas se conecta pela internet.','muted'))
        self.state=label('Verificando…','badge'); lay.addWidget(self.state)
        row=QHBoxLayout(); self.start_btn=button('Ligar API + HTTPS',self.start_server,True); row.addWidget(self.start_btn); row.addWidget(button('Parar servidor',manage.stop)); row.addWidget(button('Atualizar endereço',self.refresh)); lay.addLayout(row)
        lay.addWidget(label('ENDEREÇO PARA CONFIGURAR NA AURORA','eyebrow'))
        self.url=QLineEdit(); self.url.setReadOnly(True); self.url.setPlaceholderText('O endereço aparecerá quando o túnel estiver pronto.'); lay.addWidget(self.url)
        lay.addWidget(button('Copiar endereço',lambda:QApplication.clipboard().setText(self.url.text())))
        lay.addWidget(label('Temporário: pode mudar ao reiniciar. O endereço sozinho não concede acesso; cada pessoa precisa de uma chave.','muted'))
        self.startup=QCheckBox('Ligar automaticamente quando eu entrar no Windows'); self.startup.setChecked(manage.startup_path().exists()); self.startup.toggled.connect(self.change_startup); lay.addWidget(self.startup)
        lay.addWidget(label('PESSOAS COM ACESSO','eyebrow')); self.list=QListWidget(); lay.addWidget(self.list,1)
        row=QHBoxLayout(); row.addWidget(button('+ Criar acesso',self.add_key,True)); row.addWidget(button('Revogar selecionado',self.revoke)); lay.addLayout(row)
        lay.addWidget(label('Enquanto o servidor está ligado, ele solicita ao Windows que mantenha o PC acordado. A tela pode apagar. Não resiste a desligamento, falta de energia ou internet.','muted'))
        lay.addWidget(label('Deixe o servidor do LM Studio ativo em 127.0.0.1:1234. Perfis e históricos continuam em cada cliente. O tráfego HTTPS passa pela Cloudflare.','muted'))
        self.refresh_keys(); self.timer=QTimer(self); self.timer.timeout.connect(self.refresh); self.timer.start(2000); self.refresh()
    def start_server(self):
        manage.start(True); self.state.setText('◌  Iniciando API e túnel HTTPS…'); self.url.setText('Aguardando o endereço seguro…'); QTimer.singleShot(3500,self.refresh)
    def refresh(self):
        state=manage.status(); self.state.setText(('●  ' if state.get('api') else '○  ')+state.get('message','Servidor parado.'))
        self.url.setText(state.get('https_url','')+'/v1' if state.get('https_url') else ('Aguardando o túnel HTTPS…' if state.get('running') else ''))
    def refresh_keys(self):
        self.list.clear()
        for kid,name,created,active in self.keys.list():
            item=QListWidgetItem(name+('  •  ativo' if active else '  •  revogado')); item.setData(Qt.ItemDataRole.UserRole,kid); self.list.addItem(item)
    def add_key(self):
        name,ok=QInputDialog.getText(self,'Novo acesso','Nome da pessoa ou dispositivo:')
        if not ok: return
        try: kid,key=self.keys.issue(name)
        except ValueError as exc: QMessageBox.information(self,'Novo acesso',str(exc)); return
        self.refresh_keys(); dialog=QDialog(self); dialog.setWindowTitle('Acesso criado'); dialog.resize(600,290); lay=QVBoxLayout(dialog)
        lay.addWidget(label('Chave de '+name,'sectionTitle')); lay.addWidget(label('Copie agora e entregue somente à pessoa correspondente. O servidor guarda apenas a verificação da chave; ela não será exibida novamente.','muted'))
        field=QLineEdit(key); field.setReadOnly(True); lay.addWidget(field); lay.addWidget(button('Copiar chave',lambda:QApplication.clipboard().setText(key),True))
        lay.addWidget(label('Na Betelgeuse: Configurações → endereço acima → Token de acesso → buscar modelos → salvar.','muted')); lay.addWidget(button('Concluir',dialog.accept)); dialog.exec()
    def revoke(self):
        item=self.list.currentItem()
        if item: self.keys.revoke(item.data(Qt.ItemDataRole.UserRole)); self.refresh_keys()
    def change_startup(self,enabled):
        try: manage.set_startup(enabled)
        except OSError as exc: QMessageBox.information(self,'Inicialização',str(exc)); self.startup.blockSignals(True); self.startup.setChecked(not enabled); self.startup.blockSignals(False)

if __name__=='__main__':
    app=QApplication(sys.argv); app.setStyleSheet(STYLE); p=Panel(); p.show(); sys.exit(app.exec())
