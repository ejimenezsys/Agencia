import smtplib, time, random, sys, datetime, os, csv
from email.mime.text import MIMEText
from email.utils import formataddr, make_msgid

class TeeLogger:
    def __init__(self, filepath):
        self.terminal = sys.stdout
        self.log = open(filepath, 'a', encoding='utf-8')
    def write(self, message):
        self.terminal.write(message)
        self.log.write(message)
        self.log.flush()
    def flush(self):
        self.terminal.flush()
        self.log.flush()

log_file_path = '/Users/ejimenezsys/Desktop/sitiosweb/agencia/campaign_martes_toque1.log'
sys.stdout = TeeLogger(log_file_path)

def load_env(env_path):
    config = {}
    with open(env_path, 'r', encoding='utf-8') as f:
        for line in f:
            if '=' in line and not line.strip().startswith('#'):
                k, v = line.split('=', 1)
                config[k.strip()] = v.strip().strip('"').strip("'")
    return config

env = load_env('/Users/ejimenezsys/Desktop/sitiosweb/agencia/.env')
u = env.get('SMTP_USER')
p = env.get('SMTP_PASSWORD')
h = env.get('SMTP_HOST')
port = int(env.get('SMTP_PORT', 465))
notification_target = "edward@exmaglobal.com"

signature = """Edward Jiménez
Partner Relationship Manager · EXMA Global
edward@exmaglobal.com
exmaglobal.com/miami"""

def get_smtp_connection():
    server = smtplib.SMTP_SSL(h, port, timeout=25)
    server.login(u, p)
    return server

def send_alert(subject, message):
    try:
        server = get_smtp_connection()
        msg = MIMEText(message, 'plain', 'utf-8')
        msg['Subject'] = subject
        msg['From'] = formataddr(('EXMA Outreach System', u))
        msg['To'] = formataddr(('Edward Jimenez', notification_target))
        server.sendmail(u, [notification_target], msg.as_string())
        server.quit()
        print(f"🔔 Alerta enviada a tu móvil ({notification_target}): {subject}", flush=True)
    except Exception as e:
        print(f"⚠️ No se pudo enviar alerta: {e}", flush=True)

def update_databases_on_sent(empresa, email):
    try:
        base_dir = '/Users/ejimenezsys/Desktop/sitiosweb/agencia'
        today = datetime.datetime.now().strftime('%Y-%m-%d')
        target_t2 = (datetime.datetime.now() + datetime.timedelta(days=4)).strftime('%Y-%m-%d')
        multi_csv = os.path.join(base_dir, 'BASE_CONCENTRADA_EXMA_MIAMI_2026_MULTI_CONTACTO.csv')
        if os.path.exists(multi_csv):
            with open(multi_csv, 'r', encoding='utf-8', errors='ignore') as f:
                r = csv.DictReader(f)
                fields = list(r.fieldnames)
                rows = list(r)
            for row in rows:
                if row.get('EMPRESA', '').strip().lower() in empresa.lower() or email.lower() in [row.get('CONTACTO_1_EMAIL', '').lower(), row.get('CONTACTO_2_EMAIL', '').lower()]:
                    row['STATUS_PROSPECCION'] = f'Contactado Toque 1 ({today})'
                    row['FECHA_TOQUE_1'] = today
                    row['FECHA_TOQUE_2_PROGRAMADA'] = target_t2
                    row['CANAL_CONTACTADO'] = email
            with open(multi_csv, 'w', encoding='utf-8', newline='') as f:
                w = csv.DictWriter(f, fieldnames=fields)
                w.writeheader()
                w.writerows(rows)
    except Exception as e:
        print(f'   ⚠️ Error actualizando base para {empresa}: {e}')

prospects = [
    {
        'empresa': 'Microsoft Latin America',
        'destinatario': 'Tito Arciniega',
        'email': 'tito.arciniega@microsoft.com',
        'asunto': '2.500 líderes hispanos en Miami. La era de la IA explicada desde su sede en el sur de Florida.',
        'primera_linea': 'Felicitaciones por liderar con tanta visión la adopción de Microsoft Copilot y tecnologías de IA responsable en todo el tejido empresarial hispanoamericano.',
        'categoria': 'tecnología empresarial, computación en la nube y productividad con IA'
    },
    {
        'empresa': 'Mastercard Latin America & Caribbean',
        'destinatario': 'Paola Duran',
        'email': 'paola.duran@mastercard.com',
        'asunto': '2.500 líderes hispanos en Miami. Priceless experiences para los doers que mueven el país.',
        'primera_linea': 'Admiramos la pasión con la que Mastercard desde Brickell impulsa la aceleración digital de pequeños y medianos comercios y la inclusión financiera en todo el hemisferio.',
        'categoria': 'redes globales de pago y tecnología financiera'
    },
    {
        'empresa': 'Grupo Lala (LALA U.S., Inc.)',
        'destinatario': 'Francisco Camacho',
        'email': 'francisco.camacho@grupolala.com',
        'asunto': '2.500 líderes hispanos en Miami. Una sola marca de lácteos y nutrición activa.',
        'primera_linea': 'Es un gran referente ver cómo desde Dallas han expandido la presencia y preferencia de los yogures bebibles y lácteos Lala en los hogares activos de Estados Unidos.',
        'categoria': 'lácteos, nutrición y bebidas saludables'
    }
]

def generate_body(p):
    first_name = p['destinatario'].split()[0]
    return f"""Hola {first_name}:

{p['primera_linea']}

El 4 y 5 de diciembre, EXMA reúne en Downtown Event Center, Fort Lauderdale (área de Miami) a 2.500 dueños de negocio, ejecutivos C-Level y líderes hispanos que toman decisiones diarias de inversión y alianzas.

Trabajamos con exclusividad por categoría. En {p['categoria']}, solo habrá una marca aliada en el escenario principal y en las experiencias del evento.

¿Tiene 15 minutos esta semana o la próxima para conversar brevemente sobre esta oportunidad?

Saludos,

{signature}"""

def run_campaign(dry_run=False):
    total = len(prospects)
    print(f"==================================================")
    print(f"🚀 DESPACHO NUEVOS TOQUE 1 VALIDADOS MARTES ({total} CORREOS)")
    print(f"Modo: {'SIMULACIÓN (DRY RUN)' if dry_run else 'ENVÍO EN VIVO'}")
    print(f"==================================================")

    if not dry_run:
        send_alert(f"🚀 [EXMA Outreach] Arrancó el despacho de {total} nuevos prospectos validados",
                   f"Despachando Toque 1 para cuentas verificadas en EmailAwesome: Microsoft, Mastercard, Grupo Lala.")

    server = None
    if not dry_run:
        server = get_smtp_connection()

    success = 0
    errors = 0

    for idx, p in enumerate(prospects, 1):
        to_email = p['email'].strip()
        nombre_dest = p['destinatario'].strip()
        empresa = p['empresa'].strip()
        subject = p['asunto']
        body = generate_body(p)

        if dry_run:
            print(f"[{idx}/{total}] [SIMULADO] {nombre_dest} ({empresa}) <{to_email}>")
            print(f"    Asunto: {subject}")
            success += 1
            continue

        msg = MIMEText(body, 'plain', 'utf-8')
        msg['Subject'] = subject
        msg['From'] = formataddr(('Edward Jiménez · EXMA Global', u))
        msg['To'] = formataddr((nombre_dest, to_email))
        msg['Reply-To'] = 'edward@exmaglobal.com'
        msg['Message-ID'] = make_msgid(domain='agenciaprosperia.com')

        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        sent_ok = False

        for attempt in range(2):
            try:
                server.sendmail(u, [to_email], msg.as_string())
                print(f"[{idx}/{total}] ✅ {timestamp} [VALIDADO] ENVIADO: {nombre_dest} ({empresa}) <{to_email}>", flush=True)
                success += 1
                sent_ok = True
                update_databases_on_sent(empresa, to_email)
                break
            except Exception as e:
                print(f"⚠️ Reintentando conexión SMTP para {to_email}... ({e})", flush=True)
                try:
                    server = get_smtp_connection()
                    server.sendmail(u, [to_email], msg.as_string())
                    print(f"[{idx}/{total}] ✅ {timestamp} [REINTENTO OK] ENVIADO: {nombre_dest} ({empresa}) <{to_email}>", flush=True)
                    success += 1
                    sent_ok = True
                    update_databases_on_sent(empresa, to_email)
                    break
                except Exception as e2:
                    print(f"[{idx}/{total}] ❌ {timestamp} ERROR con {to_email}: {e2}", flush=True)

        if not sent_ok:
            errors += 1

        if idx < total:
            wait_s = random.randint(60, 90)
            print(f"   ⏳ Pausa humana anti-spam: esperando {wait_s}s antes del siguiente...", flush=True)
            time.sleep(wait_s)

    if server:
        try: server.quit()
        except: pass

    if not dry_run:
        summary_msg = f"Nuevos Toque 1 Martes completados: {success}/{total}. Errores: {errors}"
        send_alert(f"🎉 [EXMA Outreach] Toque 1 Martes COMPLETADO ({success}/{total})", summary_msg)

    print(f"Finalizado: {success}/{total} enviados. Errores: {errors}")

if __name__ == '__main__':
    dry = '--dry-run' in sys.argv
    run_campaign(dry_run=dry)
