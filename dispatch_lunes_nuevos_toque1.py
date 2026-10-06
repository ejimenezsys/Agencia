import smtplib, time, random, sys, datetime, os, csv
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

log_file_path = '/Users/ejimenezsys/Desktop/sitiosweb/agencia/campaign_lunes_toque1.log'
sys.stdout = TeeLogger(log_file_path)

from email.mime.text import MIMEText
from email.utils import formataddr, make_msgid

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

# === 15 PROSPECTOS DE ALTO ALCANCE - LUNES 5 DE OCTUBRE ===

# BLOQUE 1: ESTE / EDT (FL, NC, NY) - 7 prospectos
batch_eastern = [
    {
        'empresa': 'Heineken USA (Tecate / Dos Equis)',
        'destinatario': 'Brian Thompson',
        'email': 'brian.thompson@heinekenusa.com',
        'tz': 'EDT',
        'location': 'White Plains, NY / South Florida Markets',
        'asunto': '2.500 líderes hispanos en Miami. Celebrando el coraje de triunfar.',
        'primera_linea': 'Felicitaciones por la frescura y la potencia con la que Heineken USA celebra el carácter bicultural y la audacia del consumidor en Estados Unidos a través de marcas como Tecate y Dos Equis.',
        'categoria': 'cerveza premium y experiencias de celebración'
    },
    {
        'empresa': "Lowe's Companies, Inc.",
        'destinatario': 'Jennifer Wilson',
        'email': 'jennifer.wilson@lowes.com',
        'tz': 'EDT',
        'location': 'Mooresville, NC',
        'asunto': '2.500 líderes hispanos en Miami. Una sola marca aliada de los contratistas.',
        'primera_linea': "Destacamos la visión de Lowe's fortaleciendo de manera decidida sus lazos comerciales con los contratistas independientes (Pros) y los pequeños negocios hispanos.",
        'categoria': 'mejoras del hogar y suministro para contratistas y profesionales'
    },
    {
        'empresa': 'Spanish Broadcasting System (SBS)',
        'destinatario': 'Richard D. Lara',
        'email': 'rlara@sbshq.com',
        'tz': 'EDT',
        'location': 'Miami, FL',
        'asunto': 'SBS nació en Miami para nuestra gente. Su presencia natural en EXMA 2026.',
        'primera_linea': 'Es un honor reconocer el liderazgo indiscutible de SBS en el sur de la Florida y todo el país, dando voz, música y entretenimiento a millones de hispanos a través de Mega 97.9, Z92 y LaMusica.',
        'categoria': 'radio, medios de comunicación y entretenimiento hispano'
    },
    {
        'empresa': 'Florida Blue (GuideWell)',
        'destinatario': 'Pat Geraghty',
        'email': 'pat.geraghty@floridablue.com',
        'tz': 'EDT',
        'location': 'Jacksonville, FL / Miami Centers',
        'asunto': '2.500 líderes hispanos en Miami. Una sola aseguradora de salud líder en Florida.',
        'primera_linea': 'Invaluable la labor de Pat Geraghty y el equipo de Florida Blue asegurando el bienestar integral y la salud de las familias trabajadoras y empresarios del sur de la Florida.',
        'categoria': 'salud, cobertura médica y bienestar corporativo'
    },
    {
        'empresa': 'Microsoft Latin America',
        'destinatario': 'Patricia Miron',
        'email': 'patricia.miron@microsoft.com',
        'tz': 'EDT',
        'location': 'Fort Lauderdale / Miami, FL',
        'asunto': '2.500 líderes hispanos en Miami. La era de la IA explicada desde su sede en el sur de Florida.',
        'primera_linea': 'Felicitaciones por liderar con tanta claridad la adopción de Microsoft Copilot y tecnologías de IA responsable en todo el ecosistema empresarial hispanoamericano.',
        'categoria': 'tecnología empresarial, computación en la nube y productividad con IA'
    },
    {
        'empresa': 'Mastercard Latin America & Caribbean',
        'destinatario': 'Adrian Collard',
        'email': 'adrian.collard@mastercard.com',
        'tz': 'EDT',
        'location': 'Miami (Brickell), FL',
        'asunto': '2.500 líderes hispanos en Miami. Priceless experiences para los doers que mueven el país.',
        'primera_linea': 'Admiramos la pasión con la que Mastercard desde Brickell impulsa la aceleración digital de pequeños y medianos comercios y la inclusión financiera en todo el hemisferio.',
        'categoria': 'redes globales de pago y tecnología financiera'
    },
    {
        'empresa': 'Badia Spices',
        'destinatario': 'Martina Sachs Campos',
        'email': 'martina.campos@badiaspices.com',
        'tz': 'EDT',
        'location': 'Doral / Miami, FL',
        'asunto': 'Badia nació en Miami para servir a nuestra comunidad. Su lugar reservado en el escenario.',
        'primera_linea': 'Es un verdadero orgullo ver cómo desde Doral la familia Badía ha llevado el sabor y la sazón de nuestros países a distribuirse en más de 70 naciones manteniendo intacta su calidez.',
        'categoria': 'especias, condimentos y sazón familiar'
    }
]

# BLOQUE 2: CENTRAL / CDT (Texas) - 4 prospectos
batch_central = [
    {
        'empresa': 'Tajín USA',
        'destinatario': 'Luis Alfaro',
        'email': 'lalfaro@tajin.com',
        'tz': 'CDT',
        'location': 'Houston, TX / Zapopan HQ',
        'asunto': '2.500 líderes hispanos en Miami. El sabor único que conquistó a Estados Unidos.',
        'primera_linea': 'Fascinante el fenómeno cultural de penetración que ha logrado Tajín en Norteamérica, convirtiendo la combinación de chile y limón en un clásico querido por todas las generaciones.',
        'categoria': 'condimentos y sazonadores de raíz multicultural'
    },
    {
        'empresa': 'Grupo Lala (LALA U.S., Inc.)',
        'destinatario': 'Leonor Slim',
        'email': 'leonor.slim@lalagroup.com',
        'tz': 'CDT',
        'location': 'Dallas, TX',
        'asunto': '2.500 líderes hispanos en Miami. Una sola marca de lácteos y nutrición activa.',
        'primera_linea': 'Es un gran referente ver cómo desde Dallas han expandido la presencia y preferencia de los yogures bebibles y lácteos Lala en los hogares activos de Estados Unidos.',
        'categoria': 'lácteos, nutrición y bebidas saludables'
    },
    {
        'empresa': 'Ruiz Foods (El Monterey / Tornados)',
        'destinatario': 'Kimberli Carroll',
        'email': 'kcarroll@ruizfoods.com',
        'tz': 'CDT',
        'location': 'Frisco, TX',
        'asunto': '2.500 líderes hispanos en Miami. La marca de alimentos congelados #1 en la nación.',
        'primera_linea': 'Inspiradora la trayectoria de Ruiz Foods al consolidar marcas icónicas como El Monterey en la mesa de millones de familias manteniendo el legado de sus fundadores.',
        'categoria': 'alimentos congelados de herencia y tradición'
    },
    {
        'empresa': 'AT&T Inc',
        'destinatario': 'Kellyn Smith Kenny',
        'email': 'kellyn.kenny@att.com',
        'tz': 'CDT',
        'location': 'Dallas, TX',
        'asunto': '2.500 líderes hispanos en Miami. Una sola red de telecomunicaciones y fibra.',
        'primera_linea': 'Destacamos la cercanía y el compromiso continuo de AT&T impulsando la inclusión digital y la conectividad de alta velocidad en las comunidades hispanas.',
        'categoria': 'telecomunicaciones integradas y conectividad empresarial'
    }
]

# BLOQUE 3: PACÍFICO / PDT (California, Washington) - 4 prospectos
batch_pacific = [
    {
        'empresa': 'Meta Platforms (Facebook / Instagram / WhatsApp)',
        'destinatario': 'Rachael Guana',
        'email': 'rachaelg@meta.com',
        'tz': 'PDT',
        'location': 'Menlo Park, CA / Miami Hub',
        'asunto': '2.500 líderes hispanos en Miami. La plataforma de conexión y PyMEs por excelencia.',
        'primera_linea': 'Reconocemos el impacto transformador de las herramientas comerciales de WhatsApp y Meta en la aceleración y creación de empleo para las comunidades hispanas en todo Estados Unidos.',
        'categoria': 'redes sociales, mensajería y ecosistema publicitario para negocios'
    },
    {
        'empresa': 'Amazon Web Services (AWS)',
        'destinatario': 'Max Tremp',
        'email': 'maxtremp@amazon.com',
        'tz': 'PDT',
        'location': 'Seattle, WA / Miami Regional Hub',
        'asunto': '2.500 líderes hispanos en Miami. Una sola nube líder en innovación e IA.',
        'primera_linea': 'Es notable el respaldo y la tracción que AWS brinda a las startups y empresas nativas digitales para escalar con inteligencia artificial y cómputo en la nube en toda la región.',
        'categoria': 'infraestructura cloud e inteligencia artificial empresarial'
    },
    {
        'empresa': 'Salesforce',
        'destinatario': 'Ariel Kelman',
        'email': 'akelman@salesforce.com',
        'tz': 'PDT',
        'location': 'San Francisco, CA',
        'asunto': '2.500 líderes hispanos en Miami. Una sola plataforma de CRM y agentes de IA.',
        'primera_linea': 'Seguimos con gran admiración el despliegue de Agentforce y la visión pionera de Salesforce en torno a la productividad asistida por agentes autónomos de negocio.',
        'categoria': 'CRM, software corporativo y agentes autónomos'
    },
    {
        'empresa': 'Square (Block Inc)',
        'destinatario': 'Jessica Cook',
        'email': 'jessicacook@squareup.com',
        'tz': 'PDT',
        'location': 'San Francisco, CA',
        'asunto': '2.500 líderes hispanos en Miami. La tecnología de cobro preferida de los comercios.',
        'primera_linea': 'Admiramos la simplicidad y solidez con la que Square empodera a los comerciantes independientes y restaurantes hispanos para operar y nunca perder una venta.',
        'categoria': 'soluciones de cobro en punto de venta y comercio digital'
    }
]


def update_databases_on_sent(empresa, email):
    try:
        base_dir = '/Users/ejimenezsys/Desktop/sitiosweb/agencia'
        today = datetime.datetime.now().strftime('%Y-%m-%d')
        target_t2 = (datetime.datetime.now() + datetime.timedelta(days=4)).strftime('%Y-%m-%d')
        
        # 1. Base concentrada
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
        print(f'   ⚠️ Error actualizando base de datos para {empresa}: {e}')

def generate_toque1_body(p):
    first_name = p['destinatario'].split()[0]
    body = f"""Hola {first_name}:

{p['primera_linea']}

El 4 y 5 de diciembre, EXMA reúne en Downtown Event Center, Fort Lauderdale (área de Miami) a 2.500 dueños de negocio, ejecutivos C-Level y líderes hispanos que toman decisiones diarias de inversión y alianzas.

Trabajamos con exclusividad por categoría. En {p['categoria']}, solo habrá una marca aliada en el escenario principal y en las experiencias del evento.

¿Tiene 15 minutos esta semana o la próxima para conversar brevemente sobre esta oportunidad?

Saludos,

{signature}"""
    return body

def dispatch_batch(batch_name, prospects_list, global_offset=0, total_all=15, dry_run=False, server=None):
    print(f"==================================================")
    print(f"🚀 INICIANDO {batch_name} ({len(prospects_list)} correos)")
    print(f"Hora actual: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"==================================================")

    success = 0
    errors = 0
    logs = []

    for i, p in enumerate(prospects_list):
        global_idx = global_offset + i + 1
        to_email = p['email'].strip()
        nombre_dest = p['destinatario'].strip()
        empresa = p['empresa'].strip()
        tz = p['tz']
        loc = p['location']
        subject = p['asunto']
        body = generate_toque1_body(p)

        if dry_run:
            print(f"[{global_idx}/{total_all}] [SIMULADO] [{tz} - {loc}] {nombre_dest} ({empresa}) <{to_email}>")
            print(f"    Asunto: {subject}")
            print(f"    Cuerpo: {body.splitlines()[0]} | {body.splitlines()[2][:60]}...")
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
                print(f"[{global_idx}/{total_all}] ✅ {timestamp} [{tz} - {loc}] ENVIADO: {nombre_dest} ({empresa}) <{to_email}>", flush=True)
                success += 1
                logs.append(f"✅ {timestamp} [{tz}] {empresa}: {nombre_dest} <{to_email}>")
                sent_ok = True
                break
            except Exception as e:
                print(f"⚠️ Reintentando conexión SMTP para {to_email}... ({e})", flush=True)
                try:
                    server = get_smtp_connection()
                    server.sendmail(u, [to_email], msg.as_string())
                    print(f"[{global_idx}/{total_all}] ✅ {timestamp} [REINTENTO OK] ENVIADO: {nombre_dest} ({empresa}) <{to_email}>", flush=True)
                    success += 1
                    logs.append(f"✅ {timestamp} [{tz}] {empresa}: {nombre_dest} <{to_email}>")
                    sent_ok = True
                    break
                except Exception as e2:
                    print(f"[{global_idx}/{total_all}] ❌ {timestamp} ERROR con {to_email}: {e2}", flush=True)

        if sent_ok:
            update_databases_on_sent(empresa, to_email)
        else:
            errors += 1
            logs.append(f"❌ ERROR con {to_email}")

        if i < len(prospects_list) - 1:
            wait_s = random.randint(60, 90)
            print(f"   ⏳ Pausa humana anti-spam: esperando {wait_s}s antes del siguiente...", flush=True)
            time.sleep(wait_s)

    return success, errors, logs

def run_campaign(dry_run=False):
    total_prospects = len(batch_eastern) + len(batch_central) + len(batch_pacific)
    print(f"==================================================")
    print(f"🚀 DESPACHO NUEVA TANDA LUNES - TOQUE 1 ({total_prospects} CORREOS)")
    print(f"Modo: {'SIMULACIÓN (DRY RUN)' if dry_run else 'ENVÍO EN VIVO'}")
    print(f"==================================================")

    if not dry_run:
        send_alert(f"🚀 [EXMA Outreach] Arrancó el despacho de los {total_prospects} nuevos correos del Lunes",
                   f"Iniciando campaña de prospección Toque 1 para marcas de alto calibre.")

    server = None
    if not dry_run:
        server = get_smtp_connection()

    all_logs = []
    total_success = 0
    total_errors = 0

    # 1. BLOQUE ESTE
    s1, e1, l1 = dispatch_batch("BLOQUE 1: ESTE / EDT (FL, NC, NY)", batch_eastern, 0, total_prospects, dry_run, server)
    total_success += s1
    total_errors += e1
    all_logs.extend(l1)

    if not dry_run:
        print("Enviando alertas...")
    # 2. BLOQUE CENTRAL
    s2, e2, l2 = dispatch_batch("BLOQUE 2: CENTRAL / CDT (Texas)", batch_central, len(batch_eastern), total_prospects, dry_run, server)
    total_success += s2
    total_errors += e2
    all_logs.extend(l2)

    if not dry_run:
        time.sleep(120)

    # 3. BLOQUE PACÍFICO
    offset_pac = len(batch_eastern) + len(batch_central)
    s3, e3, l3 = dispatch_batch("BLOQUE 3: PACÍFICO / PDT (California, Washington)", batch_pacific, offset_pac, total_prospects, dry_run, server)
    total_success += s3
    total_errors += e3
    all_logs.extend(l3)

    if server:
        try: server.quit()
        except: pass

    if not dry_run:
        summary_msg = f"Campaña de Lunes completada: {total_success}/{total_prospects}. Errores: {total_errors}"
        send_alert(f"🎉 [EXMA Outreach] Campaña de Lunes COMPLETADA ({total_success}/{total_prospects})", summary_msg)
    print(f"Finalizado: {total_success}/{total_prospects} enviados. Errores: {total_errors}")

if __name__ == "__main__":
    dry = "--dry-run" in sys.argv
    run_campaign(dry_run=dry)
