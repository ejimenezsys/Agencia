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

log_file_path = '/Users/ejimenezsys/Desktop/sitiosweb/agencia/campaign_jueves_15_oct.log'
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
        
        # 1. Base Multi-Contacto
        multi_csv = os.path.join(base_dir, 'BASE_CONCENTRADA_EXMA_MIAMI_2026_MULTI_CONTACTO.csv')
        if os.path.exists(multi_csv):
            with open(multi_csv, 'r', encoding='utf-8', errors='ignore') as f:
                r = csv.DictReader(f)
                fields = list(r.fieldnames)
                rows = list(r)
            updated = False
            for row in rows:
                if row.get('EMPRESA', '').strip().lower() in empresa.lower() or email.lower() in [row.get('CONTACTO_1_EMAIL', '').lower(), row.get('CONTACTO_2_EMAIL', '').lower(), row.get('CONTACTO_3_EMAIL', '').lower()]:
                    row['STATUS_PROSPECCION'] = f'Contactado Toque 1 ({today})'
                    row['FECHA_TOQUE_1'] = today
                    row['FECHA_TOQUE_2_PROGRAMADA'] = target_t2
                    row['CANAL_CONTACTADO'] = email
                    updated = True
            if updated:
                with open(multi_csv, 'w', encoding='utf-8', newline='') as f:
                    w = csv.DictWriter(f, fieldnames=fields)
                    w.writeheader()
                    w.writerows(rows)
                    
        # 2. Base 120
        base120_csv = os.path.join(base_dir, 'EXMA_BASE_120_CONSOLIDADA_100_PORCIENTO.csv')
        if os.path.exists(base120_csv):
            with open(base120_csv, 'r', encoding='utf-8', errors='ignore') as f:
                r = csv.DictReader(f)
                fields = list(r.fieldnames)
                rows = list(r)
            updated120 = False
            for row in rows:
                if row.get('empresa', '').strip().lower() in empresa.lower() or email.lower() in [row.get('c1_email', '').lower(), row.get('c2_email', '').lower(), row.get('c3_email', '').lower()]:
                    row['estado_comercial'] = f'Contactado (Toque 1)'
                    row['fecha_toque_1'] = today
                    row['fecha_toque_2'] = target_t2
                    updated120 = True
            if updated120:
                with open(base120_csv, 'w', encoding='utf-8', newline='') as f:
                    w = csv.DictWriter(f, fieldnames=fields)
                    w.writeheader()
                    w.writerows(rows)
    except Exception as e:
        print(f'   ⚠️ Error actualizando bases para {empresa}: {e}')

prospects = [
    {
        'empresa': "Sedano's Supermarkets",
        'destinatario': 'Javier Herrán',
        'email': 'jherran@sedanos.com',
        'asunto': '2.500 líderes hispanos en Miami. Una sola marca de supermercados hispanos.',
        'primera_linea': "Admiro el profundo arraigo y liderazgo con el que Sedano's ha acompañado y alimentado a la comunidad del sur de Florida durante más de seis décadas.",
        'categoria': 'supermercados y cadenas de consumo masivo hispano'
    },
    {
        'empresa': 'Goya Foods',
        'destinatario': 'Conrad Colon',
        'email': 'conrad.colon@goya.com',
        'asunto': '2.500 líderes hispanos en Miami. Una sola marca de alimentos hispanos.',
        'primera_linea': 'Admiro el liderazgo continuo de Goya celebrando casi nueve décadas alimentando y representando el orgullo de las familias hispanas en todo Estados Unidos.',
        'categoria': 'alimentos auténticos, sazón y productos hispanos de consumo masivo'
    },
    {
        'empresa': 'El Pollo Loco',
        'destinatario': 'Jill Adams',
        'email': 'jadams@elpolloloco.com',
        'asunto': '2.500 líderes hispanos en Miami. Una sola marca de restaurantes de servicio rápido latino.',
        'primera_linea': 'Es inspirador ver cómo El Pollo Loco ha conectado la auténtica herencia culinaria con la innovación de marca y fidelidad en cada comunidad hispana.',
        'categoria': 'restaurantes de servicio rápido, sabor latino y hospitalidad'
    },
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
        'categoria': 'redes globales de pago, medios digitales y tecnología financiera'
    },
    {
        'empresa': 'Grupo Lala (LALA U.S., Inc.)',
        'destinatario': 'Francisco Camacho',
        'email': 'francisco.camacho@grupolala.com',
        'asunto': '2.500 líderes hispanos en Miami. Una sola marca de lácteos y nutrición activa.',
        'primera_linea': 'Es un gran referente ver cómo han expandido la presencia y preferencia de los lácteos y yogures bebibles Lala en los hogares activos de Estados Unidos.',
        'categoria': 'lácteos, nutrición y bebidas saludables'
    },
    {
        'empresa': "Porto's Bakery",
        'destinatario': 'Raul Porto Jr.',
        'email': 'rporto@portosbakery.com',
        'asunto': '2.500 líderes hispanos en Miami. Una sola marca de tradición pastelera artesanal.',
        'primera_linea': "Es un verdadero orgullo ver cómo Porto's Bakery ha convertido la excelencia pastelera y la tradición familiar en uno de los mayores íconos culinarios de Estados Unidos.",
        'categoria': 'panadería artesanal, repostería y orgullo gastronómico hispano'
    },
    {
        'empresa': "Sergio's Cuban Kitchen",
        'destinatario': 'Carlos Gazitua',
        'email': 'cgazitua@sergios.com',
        'asunto': '2.500 líderes hispanos en Miami. Una sola marca referente de gastronomía cubana.',
        'primera_linea': "Reconocemos la genialidad con la que Sergio's ha innovado en tecnología, menús saludables y experiencia de cliente sin perder una pizca de sabor y tradición cubana en Miami.",
        'categoria': 'gastronomía fusión cubana y franquicias de hospitalidad latina'
    },
    {
        'empresa': 'Pollo Campero (CMI Alimentos)',
        'destinatario': 'Luis Javier Rodas',
        'email': 'lrodas@campero.com',
        'asunto': '2.500 líderes hispanos en Miami. Una sola marca de pollo tierno y crujiente latino.',
        'primera_linea': 'Impresionante el despliegue y crecimiento con el que Pollo Campero está conquistando el mercado estadounidense conservando su inconfundible sabor y conexión cultural.',
        'categoria': 'restaurantes de pollo frito con sabor latino y proyección internacional'
    },
    {
        'empresa': 'Viamericas',
        'destinatario': 'Joseph Argilagos',
        'email': 'jargilagos@viamericas.com',
        'asunto': '2.500 líderes hispanos en Miami. Una sola marca de transferencias financieras transfronterizas.',
        'primera_linea': 'Admiramos el impacto directo que Viamericas genera cada día facilitando remesas seguras y construyendo prosperidad para millones de familias en toda América Latina.',
        'categoria': 'transferencias internacionales de dinero y servicios financieros transfronterizos'
    },
    {
        'empresa': 'PwC US',
        'destinatario': 'Paul Griggs',
        'email': 'paul.griggs@pwc.com',
        'asunto': '2.500 líderes hispanos en Miami. Una sola firma global de consultoría estratégica.',
        'primera_linea': 'Felicitaciones por la visión con la que PwC lidera la transformación corporativa y el empoderamiento del talento y liderazgo diverso en el entorno de negocios de Estados Unidos.',
        'categoria': 'consultoría estratégica, auditoría y transformación empresarial'
    },
    {
        'empresa': 'Accenture',
        'destinatario': 'Julie Sweet',
        'email': 'julie.sweet@accenture.com',
        'asunto': '2.500 líderes hispanos en Miami. Una sola marca global de transformación digital e IA.',
        'primera_linea': 'Es admirable cómo Accenture marca la pauta global en reinvención empresarial a través de IA generativa, nube y desarrollo de ecosistemas inclusivos de alto impacto.',
        'categoria': 'tecnología de vanguardia, inteligencia artificial aplicada y consultoría digital'
    },
    {
        'empresa': 'Carnival Cruise Line',
        'destinatario': 'Arlene Brown',
        'email': 'abrown@carnival.com',
        'asunto': '2.500 líderes hispanos en Miami. Una sola línea de cruceros y hospitalidad vacacional.',
        'primera_linea': 'Admiramos cómo Carnival, desde su sede en Miami, sigue siendo el referente indiscutible de diversión, accesibilidad y celebración para las familias hispanas de todo el país.',
        'categoria': 'cruceros, entretenimiento vacacional y hospitalidad marítima'
    },
    {
        'empresa': 'Royal Caribbean Group',
        'destinatario': 'Jason Liberty',
        'email': 'jliberty@rccl.com',
        'asunto': '2.500 líderes hispanos en Miami. Una sola marca insignia de cruceros globales.',
        'primera_linea': 'Reconocemos el formidable salto en innovación y diseño de experiencias que Royal Caribbean lidera desde el sur de Florida, redefiniendo las vacaciones a nivel mundial.',
        'categoria': 'turismo marítimo de lujo, experiencias vacacionales e innovación marina'
    },
    {
        'empresa': 'American Airlines',
        'destinatario': 'Robert Isom',
        'email': 'robert.isom@aa.com',
        'asunto': '2.500 líderes hispanos en Miami. Una sola aerolínea aliada conectando el continente.',
        'primera_linea': 'Destacamos el rol indispensable de American Airlines como el principal puente aéreo que une a Miami con toda América Latina y el Caribe.',
        'categoria': 'aerolíneas comerciales y conectividad aérea internacional con las Américas'
    },
    {
        'empresa': 'Delta Air Lines',
        'destinatario': 'Rodrigo Bértola',
        'email': 'rodrigo.bertola@delta.com',
        'asunto': '2.500 líderes hispanos en Miami. Una sola aerolínea global conectando la región.',
        'primera_linea': 'Felicitaciones por la consolidación del Joint Venture entre Delta y LATAM, expandiendo la mejor conectividad y experiencia premium entre Estados Unidos y la región.',
        'categoria': 'transporte aéreo global, servicio al cliente y lealtad corporativa'
    },
    {
        'empresa': 'Walmart Inc',
        'destinatario': 'Donna Morris',
        'email': 'donna.morris@walmart.com',
        'asunto': '2.500 líderes hispanos en Miami. Una sola marca referente de retail masivo omnicanal.',
        'primera_linea': 'Admiramos cómo Walmart impulsa la movilidad económica, el bienestar y el desarrollo integral de la fuerza laboral hispana en cada rincón del país.',
        'categoria': 'retail masivo, comercio omnicanal y desarrollo de talento corporativo'
    },
    {
        'empresa': 'The Kraft Heinz Company',
        'destinatario': 'Todd Kaplan',
        'email': 'todd.kaplan@kraftheinz.com',
        'asunto': '2.500 líderes hispanos en Miami. Una sola marca insignia de alimentos y marcas de consumo.',
        'primera_linea': 'Es inspirador ver la energía y frescura con la que Kraft Heinz conecta sus marcas de siempre con los nuevos hábitos y la diversidad cultural de los consumidores en Norteamérica.',
        'categoria': 'alimentos empacados, marcas icónicas de consumo y culinaria del hogar'
    },
    {
        'empresa': 'Colgate-Palmolive',
        'destinatario': 'Ari Mandelbaum',
        'email': 'ari_mandelbaum@colpal.com',
        'asunto': '2.500 líderes hispanos en Miami. Una sola marca líder de cuidado personal y bienestar familiar.',
        'primera_linea': 'Reconocemos el arraigo y la confianza que Colgate-Palmolive inspira día a día en los hogares hispanos mediante innovación centrada en la salud y el bienestar.',
        'categoria': 'cuidado personal, higiene bucal y bienestar del hogar'
    },
    {
        'empresa': 'Target Corporation',
        'destinatario': 'Brian Cornell',
        'email': 'brian.cornell@target.com',
        'asunto': '2.500 líderes hispanos en Miami. Una sola marca de grandes almacenes y experiencia retail.',
        'primera_linea': 'Reconocemos el compromiso ejemplar de Target elevando el talento latino y diseñando experiencias de compra acogedoras que celebran la diversidad de las comunidades.',
        'categoria': 'retail departamental, moda, estilo de vida y experiencia de compra curada'
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
    print(f"🚀 DESPACHO JUEVES 15 DE OCTUBRE ({total} CORREOS 100% VALIDADOS)")
    print(f"Modo: {'SIMULACIÓN (DRY RUN)' if dry_run else 'ENVÍO EN VIVO'}")
    print(f"==================================================")

    if not dry_run:
        send_alert(f"🚀 [EXMA Outreach] Arrancó el despacho de {total} correos validados de hoy Jueves 15-Oct",
                   f"Iniciando envío de 20 prospectos auditados y 100% validados en EmailAwesome (cero rebotes garantizados).")

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
            print(f"   ⏳ Pausa humana anti-spam: esperando {wait_s}s antes del siguiente ({idx+1}/{total})...", flush=True)
            time.sleep(wait_s)

    if server:
        try: server.quit()
        except: pass

    if not dry_run:
        summary_msg = f"Despacho Jueves 15 de Octubre completado: {success}/{total} enviados con éxito. Errores: {errors}."
        send_alert(f"🎉 [EXMA Outreach] Despacho Jueves 15-Oct COMPLETADO ({success}/{total})", summary_msg)

    print(f"Finalizado: {success}/{total} enviados. Errores: {errors}")

if __name__ == '__main__':
    dry = '--dry-run' in sys.argv
    run_campaign(dry_run=dry)
