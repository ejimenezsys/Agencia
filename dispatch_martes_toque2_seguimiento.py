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

log_file_path = '/Users/ejimenezsys/Desktop/sitiosweb/agencia/campaign_martes_seguimiento.log'
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

def update_databases_on_followup(empresa, email):
    try:
        base_dir = '/Users/ejimenezsys/Desktop/sitiosweb/agencia'
        today = datetime.datetime.now().strftime('%Y-%m-%d')
        for fname in ['EXMA_BASE_120_CONSOLIDADA_100_PORCIENTO.csv', 'EXMA_BASE_240_CONSOLIDADA_100_PORCIENTO.csv']:
            p_csv = os.path.join(base_dir, fname)
            if not os.path.exists(p_csv): continue
            with open(p_csv, 'r', encoding='utf-8', errors='ignore') as f:
                r = csv.DictReader(f)
                fields = list(r.fieldnames)
                rows = list(r)
            for row in rows:
                if row.get('empresa', '').strip().lower() in empresa.lower() or email.lower() in [row.get('c1_email', '').lower(), row.get('c2_email', '').lower()]:
                    row['estado_comercial'] = 'Contactado (Toque 2)'
                    row['fecha_toque_2'] = today
            with open(p_csv, 'w', encoding='utf-8', newline='') as f:
                w = csv.DictWriter(f, fieldnames=fields)
                w.writeheader()
                w.writerows(rows)
    except Exception as e:
        print(f'   ⚠️ Error actualizando seguimiento en base para {empresa}: {e}')

# 12 PROSPECTOS DEL MIÉRCOLES 100% VALIDADOS EN EMAILAWESOME
prospects = [{'destinatario': 'Ron DeFeo', 'empresa': 'American Airlines', 'email': 'ronald.defeo@aa.com', 'tz': 'CDT', 'location': 'Fort Worth, TX', 'tipo': 'VALID', 'asunto': '2.500 líderes hispanos en Miami. Una sola aerolínea oficial.', 'cuerpo': 'Hola Ron:\n\nMiami es el epicentro indiscutible de las operaciones de American Airlines hacia el mundo hispano y toda la región.\n\nEl 4 y 5 de diciembre, EXMA reúne en Downtown Event Center, Fort Lauderdale (área metropolitana de Miami) a 2.500 tomadores de decisión, ejecutivos y emprendedores hispanos que vuelan constantemente por negocios.\n\nTrabajamos bajo el modelo de exclusividad total por industria. En el sector aerocomercial, solo habrá una aerolínea aliada en el escenario y en los espacios ejecutivos.\n\n¿Tiene 15 minutos esta semana o la próxima para conversar?\n\nSaludos,\n\nEdward Jiménez\nPartner Relationship Manager · EXMA Global\nedward@exmaglobal.com\nexmaglobal.com/miami'}, {'destinatario': 'Mark Weinstein', 'empresa': 'Target Corporation', 'email': 'mark.weinstein@target.com', 'tz': 'CDT', 'location': 'Minneapolis, MN', 'tipo': 'VALID', 'asunto': '2.500 líderes hispanos en Miami. Una sola marca de retail masivo.', 'cuerpo': 'Hola Mark:\n\nEl consumidor hispano en Estados Unidos tiene a Target entre sus opciones predilectas de compra física y digital, impulsando de forma decisiva las categorías clave de la cadena.\n\nEl 4 y 5 de diciembre, EXMA reúne en Downtown Event Center, Fort Lauderdale (área de Miami) a 2.500 líderes, ejecutivos y dueños de negocio hispanos que definen el consumo familiar e institucional.\n\nTrabajamos con exclusividad por categoría. En retail masivo y departamental, solo habrá una marca presente en el escenario y experiencias del evento.\n\n¿Tiene 15 minutos esta semana o la próxima para conversar?\n\nSaludos,\n\nEdward Jiménez\nPartner Relationship Manager · EXMA Global\nedward@exmaglobal.com\nexmaglobal.com/miami'}, {'destinatario': 'Sathish Mohanraju', 'empresa': 'Mission Foods (Gruma)', 'email': 'smohanraju@missionfoods.com', 'tz': 'CDT', 'location': 'Irving, TX', 'tipo': 'VALID', 'asunto': '2.500 líderes hispanos en Miami. Una sola marca de alimentos y tortillas.', 'cuerpo': 'Hola Sathish:\n\nMission Foods representa uno de los mayores casos de éxito de una marca de raíz hispana convertida en líder absoluto del consumo masivo en Estados Unidos.\n\nEl 4 y 5 de diciembre, EXMA reúne en Downtown Event Center, Fort Lauderdale (área metropolitana de Miami) a 2.500 líderes empresariales, compradores y profesionales hispanos.\n\nManejamos exclusividad estricta por categoría. En alimentos de consumo masivo y tortillas, habrá una sola marca aliada con visibilidad estelar ante esta audiencia bicultural.\n\n¿Tiene 15 minutos esta semana o la próxima para explorar esta alianza?\n\nSaludos,\n\nEdward Jiménez\nPartner Relationship Manager · EXMA Global\nedward@exmaglobal.com\nexmaglobal.com/miami'}, {'destinatario': 'Molly Battin', 'empresa': 'The Home Depot', 'email': 'molly_battin@homedepot.com', 'tz': 'EDT', 'location': 'Atlanta, GA', 'tipo': 'VALID', 'asunto': '2.500 líderes hispanos en Miami. Una sola marca de home improvement.', 'cuerpo': 'Hola Molly:\n\nLa comunidad hispana de contratistas, desarrolladores y dueños de negocio representa un motor indispensable en el crecimiento del segmento Pro de The Home Depot en todo el país.\n\nEl 4 y 5 de diciembre, EXMA reúne en Downtown Event Center, Fort Lauderdale (área de Miami) a 2.500 líderes empresariales y tomadores de decisión hispanos del sur de la Florida y todo Estados Unidos.\n\nTrabajamos con exclusividad por categoría. En home improvement y construcción comercial, solo habrá una marca en el escenario y en los espacios VIP.\n\n¿Tiene 15 minutos esta semana o la próxima para conversar?\n\nSaludos,\n\nEdward Jiménez\nPartner Relationship Manager · EXMA Global\nedward@exmaglobal.com\nexmaglobal.com/miami'}, {'destinatario': 'Marcel Marcondes', 'empresa': 'Anheuser-Busch InBev', 'email': 'marcel.marcondes@ab-inbev.com', 'tz': 'EDT', 'location': 'New York, NY', 'tipo': 'VALID', 'asunto': '2.500 líderes hispanos en Miami. Una sola marca de cerveza y bebidas.', 'cuerpo': 'Hola Marcel:\n\nEl consumidor hispano en Estados Unidos no solo lidera el crecimiento de la categoría de bebidas, sino que conecta profundamente con marcas que celebran sus momentos de éxito y comunidad.\n\nEl 4 y 5 de diciembre, EXMA reúne en Downtown Event Center, Fort Lauderdale (área de Miami) a 2.500 ejecutivos, fundadores y líderes hispanos.\n\nTrabajamos con exclusividad por categoría. En cerveza y bebidas, solo habrá una corporación en el escenario principal y en las experiencias VIP de networking del evento.\n\n¿Tiene 15 minutos esta semana o la próxima?\n\nSaludos,\n\nEdward Jiménez\nPartner Relationship Manager · EXMA Global\nedward@exmaglobal.com\nexmaglobal.com/miami'}, {'destinatario': 'Elizabeth Rutledge', 'empresa': 'American Express', 'email': 'elizabeth.rutledge@aexp.com', 'tz': 'EDT', 'location': 'New York, NY', 'tipo': 'VALID', 'asunto': '2.500 líderes hispanos en Miami. Una sola marca de tarjetas y servicios financieros.', 'cuerpo': 'Hola Elizabeth:\n\nLos empresarios y ejecutivos hispanos en Estados Unidos forman uno de los segmentos de más rápido crecimiento en adopción de soluciones de pago empresarial y membresías corporativas.\n\nEl 4 y 5 de diciembre, EXMA reúne en Downtown Event Center, Fort Lauderdale (área de Miami) a 2.500 líderes y dueños de negocio con alto poder de compra y decisión.\n\nTrabajamos con exclusividad por categoría. En tarjetas de crédito y servicios financieros premium, solo habrá una marca aliada en el escenario y en el VIP Lounge.\n\n¿Tiene 15 minutos esta semana o la próxima?\n\nSaludos,\n\nEdward Jiménez\nPartner Relationship Manager · EXMA Global\nedward@exmaglobal.com\nexmaglobal.com/miami'}, {'destinatario': 'Harley Finkelstein', 'empresa': 'Shopify Inc.', 'email': 'harley@shopify.com', 'tz': 'EDT', 'location': 'Ottawa / New York', 'tipo': 'VALID', 'asunto': '2.500 líderes hispanos en Miami. Una sola plataforma de comercio digital.', 'cuerpo': 'Hola Harley:\n\nLa tasa de creación de nuevos negocios por fundadores hispanos en Estados Unidos supera consistentemente al resto de los segmentos demográficos, y el comercio omnicanal es su principal vehículo de crecimiento.\n\nEl 4 y 5 de diciembre, EXMA reúne en Downtown Event Center, Fort Lauderdale (área de Miami) a 2.500 fundadores y ejecutivos hispanos que operan o están escalando marcas de retail digital.\n\nTrabajamos bajo exclusividad de categoría. En plataformas de comercio y e-commerce, habrá una sola marca aliada en el escenario principal.\n\n¿Tiene 15 minutos esta semana o la próxima para conversar?\n\nSaludos,\n\nEdward Jiménez\nPartner Relationship Manager · EXMA Global\nedward@exmaglobal.com\nexmaglobal.com/miami'}, {'destinatario': 'Enrique Perez-Pantera', 'empresa': 'Pollo Tropical (Fiesta Restaurant Group)', 'email': 'eperez@pollotropical.com', 'tz': 'EDT', 'location': 'Miami, FL', 'tipo': 'VALID', 'asunto': '2.500 líderes hispanos en Miami. Una sola marca de sabores de Florida.', 'cuerpo': 'Hola Enrique:\n\nPollo Tropical es una institución cultural y culinaria imprescindible en la vida cotidiana de las familias y profesionales en todo el sur de la Florida.\n\nEl 4 y 5 de diciembre, EXMA celebra su gran cumbre empresarial en Downtown Event Center, Fort Lauderdale (área de Miami), congregando a 2.500 líderes hispanos locales y nacionales.\n\nTrabajamos con exclusividad por categoría. En el segmento QSR regional y sabores caribeños, solo habrá una marca presente con activaciones y visibilidad de marca.\n\n¿Tiene 15 minutos esta semana o la próxima para conversar sobre esta presencia?\n\nSaludos,\n\nEdward Jiménez\nPartner Relationship Manager · EXMA Global\nedward@exmaglobal.com\nexmaglobal.com/miami'}, {'destinatario': 'Kip Bodnar', 'empresa': 'HubSpot, Inc.', 'email': 'kbodnar@hubspot.com', 'tz': 'EDT', 'location': 'Cambridge, MA', 'tipo': 'VALID', 'asunto': '2.500 líderes hispanos en Miami. Una sola plataforma de CRM y marketing.', 'cuerpo': 'Hola Kip:\n\nEl ecosistema empresarial hispano en EE.UU. y Miami está viviendo una acelerada profesionalización en marketing automation, inbound sales y digital customer experience.\n\nEl 4 y 5 de diciembre, EXMA reúne en Downtown Event Center, Fort Lauderdale (área metropolitana de Miami) a 2.500 directores, CEOs y líderes de marketing hispanos.\n\nTrabajamos con exclusividad por categoría. En CRM, automatización de marketing y plataformas de ventas, solo habrá una compañía en el escenario principal.\n\n¿Tiene 15 minutos esta semana o la próxima para conversar?\n\nSaludos,\n\nEdward Jiménez\nPartner Relationship Manager · EXMA Global\nedward@exmaglobal.com\nexmaglobal.com/miami'}, {'destinatario': 'Leslie Vesper', 'empresa': 'Bimbo Bakeries USA', 'email': 'leslie.vesper@grupobimbo.com', 'tz': 'EDT', 'location': 'Horsham, PA', 'tipo': 'VALID', 'asunto': '2.500 líderes hispanos en Miami. Una sola marca de panadería y snacks.', 'cuerpo': 'Hola Leslie:\n\nGrupo Bimbo es el ejemplo definitivo de excelencia empresarial que conecta con el corazón, la nostalgia y la vida diaria de las familias hispanas y el mercado general en Estados Unidos.\n\nEl 4 y 5 de diciembre, EXMA reúne en Downtown Event Center, Fort Lauderdale (área de Miami) a 2.500 líderes empresariales, compradores y ejecutivos hispanos de todo el país.\n\nTrabajamos con exclusividad por categoría. En la industria de panadería, repostería y snacks empaquetados, solo habrá una marca aliada en el escenario.\n\n¿Tiene 15 minutos esta semana o la próxima para conversar?\n\nSaludos,\n\nEdward Jiménez\nPartner Relationship Manager · EXMA Global\nedward@exmaglobal.com\nexmaglobal.com/miami'}, {'destinatario': 'Luis Restrepo', 'empresa': 'Taco Bell', 'email': 'luis.restrepo@yum.com', 'tz': 'PDT', 'location': 'Irvine, CA', 'tipo': 'VALID', 'asunto': '2.500 líderes hispanos en Miami. Una sola marca de QSR juvenil.', 'cuerpo': 'Hola Luis:\n\nTaco Bell ha demostrado una maestría única en conectar la cultura con el entretenimiento, el humor y la conversación juvenil a escala global.\n\nEl 4 y 5 de diciembre, EXMA reúne en Downtown Event Center, Fort Lauderdale (área de Miami) a 2.500 líderes, creadores y ejecutivos hispanos que definen las tendencias de marketing en el mercado hispano de Estados Unidos.\n\nTrabajamos con exclusividad por categoría. En fast food juvenil e innovador, solo habrá una marca aliada en el escenario y en las experiencias del festival.\n\n¿Tiene 15 minutos esta semana o la próxima para conversar?\n\nSaludos,\n\nEdward Jiménez\nPartner Relationship Manager · EXMA Global\nedward@exmaglobal.com\nexmaglobal.com/miami'}, {'destinatario': 'Frank Cooper III', 'empresa': 'Visa Inc.', 'email': 'fcooper@visa.com', 'tz': 'PDT', 'location': 'San Francisco, CA', 'tipo': 'VALID', 'asunto': '2.500 líderes hispanos en Miami. Una sola red global de pagos.', 'cuerpo': 'Hola Frank:\n\nLa adopción de pagos digitales, comercio transfronterizo y transacciones móviles dentro de la comunidad hispana en Estados Unidos crece a un ritmo superior a la media nacional.\n\nEl 4 y 5 de diciembre, EXMA reúne en Downtown Event Center, Fort Lauderdale (área de Miami) a 2.500 líderes de negocio y ejecutivos hispanos que están construyendo la economía del futuro.\n\nTrabajamos con exclusividad por categoría. En redes globales de pago y tecnología financiera, solo habrá una marca aliada en el escenario principal.\n\n¿Tiene 15 minutos esta semana o la próxima para conversar?\n\nSaludos,\n\nEdward Jiménez\nPartner Relationship Manager · EXMA Global\nedward@exmaglobal.com\nexmaglobal.com/miami'}]

def generate_followup_body(p):
    first_name = p['destinatario'].split()[0]
    asunto_orig = p['asunto']
    cuerpo_orig = p['cuerpo']
    empresa = p['empresa']
    
    cat = 'su categoría'
    if 'aerolínea' in asunto_orig: cat = 'aerolíneas y conectividad aérea'
    elif 'retail' in asunto_orig: cat = 'retail y tiendas de conveniencia'
    elif 'tortillas' in asunto_orig or 'maíz' in asunto_orig: cat = 'alimentos y productos tradicionales'
    elif 'ferretería' in asunto_orig or 'hogar' in asunto_orig: cat = 'mejoras del hogar y materiales'
    elif 'cerveza' in asunto_orig: cat = 'cerveza y hospitalidad'
    elif 'financiero' in asunto_orig or 'tarjeta' in asunto_orig or 'financiera' in asunto_orig: cat = 'servicios financieros y pagos'
    elif 'comercio digital' in asunto_orig or 'e-commerce' in asunto_orig: cat = 'comercio electrónico y plataformas de venta'
    elif 'restaurante' in asunto_orig or 'sabor' in asunto_orig: cat = 'restaurantes de servicio rápido'
    elif 'marketing' in asunto_orig or 'crm' in asunto_orig: cat = 'software de marketing y CRM'
    elif 'panadería' in asunto_orig or 'pan' in asunto_orig: cat = 'panificación y alimentos empacados'
    elif 'pagos' in asunto_orig or 'red de pagos' in asunto_orig: cat = 'tecnología de pagos globales'

    body = f"""Hola {first_name}:

Quería asegurarme de que mi correo de la semana pasada no se hubiera traspapelado entre sus pendientes.

Como le comentaba, el 4 y 5 de diciembre reunimos en Miami (Downtown Event Center, Fort Lauderdale) a 2.500 dueños de negocio, ejecutivos y líderes hispanos en la cumbre EXMA Miami 2026.

Trabajamos con exclusividad de una sola marca por categoría. En {cat}, queremos confirmar si {empresa} tiene interés en liderar esa presencia preferente antes de abrir conversaciones con otros actores del sector.

¿Tiene 15 minutos este jueves o viernes para conversar brevemente?

Saludos cordiales,

{signature}

--- Mensaje original ---
De: Edward Jiménez · EXMA Global <edward@exmaglobal.com>
Fecha: 30 de septiembre de 2026
Asunto: {asunto_orig}
Para: {p['destinatario']} <{p['email']}>

{cuerpo_orig}"""
    return body

def run_campaign(dry_run=False):
    total = len(prospects)
    print(f"==================================================")
    print(f"🚀 INICIANDO TOQUE 2 SEGUIMIENTO MARTES 6-OCT ({total} CORREOS)")
    print(f"Modo: {'SIMULACIÓN (DRY RUN)' if dry_run else 'ENVÍO EN VIVO'}")
    print(f"Hora actual: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"==================================================")

    if not dry_run:
        send_alert(f"🚀 [EXMA Outreach] Arrancó el Toque 2 de Seguimiento Martes ({total} correos)",
                   f"Despachando seguimiento a 4 días hábiles para prospectos del Miércoles 30-Sep 100% VALIDADOS en EmailAwesome.")

    server = None
    if not dry_run:
        server = get_smtp_connection()

    success = 0
    errors = 0

    for idx, p in enumerate(prospects, 1):
        to_email = p['email'].strip()
        nombre_dest = p['destinatario'].strip()
        empresa = p['empresa'].strip()
        subject_reply = f"RE: {p['asunto']}"
        body = generate_followup_body(p)

        if dry_run:
            print(f"[{idx}/{total}] [SIMULADO] {nombre_dest} ({empresa}) <{to_email}>")
            print(f"    Asunto: {subject_reply}")
            success += 1
            continue

        msg = MIMEText(body, 'plain', 'utf-8')
        msg['Subject'] = subject_reply
        msg['From'] = formataddr(('Edward Jiménez · EXMA Global', u))
        msg['To'] = formataddr((nombre_dest, to_email))
        msg['Reply-To'] = 'edward@exmaglobal.com'
        msg['Message-ID'] = make_msgid(domain='agenciaprosperia.com')

        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        sent_ok = False

        for attempt in range(2):
            try:
                server.sendmail(u, [to_email], msg.as_string())
                print(f"[{idx}/{total}] ✅ {timestamp} [SEGUIMIENTO VALIDADO] ENVIADO: {nombre_dest} ({empresa}) <{to_email}>", flush=True)
                success += 1
                sent_ok = True
                update_databases_on_followup(empresa, to_email)
                break
            except Exception as e:
                print(f"⚠️ Reintentando conexión SMTP para {to_email}... ({e})", flush=True)
                try:
                    server = get_smtp_connection()
                    server.sendmail(u, [to_email], msg.as_string())
                    print(f"[{idx}/{total}] ✅ {timestamp} [REINTENTO OK] ENVIADO: {nombre_dest} ({empresa}) <{to_email}>", flush=True)
                    success += 1
                    sent_ok = True
                    update_databases_on_followup(empresa, to_email)
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
        summary_msg = f"Seguimiento Martes finalizado: {success}/{total} enviados. Errores: {errors}"
        send_alert(f"🎉 [EXMA Outreach] Toque 2 Martes COMPLETADO ({success}/{total})", summary_msg)

    print(f"Finalizado: {success}/{total} enviados. Errores: {errors}")

if __name__ == '__main__':
    dry = '--dry-run' in sys.argv
    run_campaign(dry_run=dry)
