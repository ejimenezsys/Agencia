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

log_file_path = '/Users/ejimenezsys/Desktop/sitiosweb/agencia/campaign_miercoles_seguimiento.log'
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

# 10 PROSPECTOS 100% VALIDADOS EN EMAILAWESOME
prospects = [{'destinatario': 'Kim Lefko', 'empresa': 'Ace Hardware', 'email': 'klefko@acehardware.com', 'tz': 'CDT', 'location': 'Oak Brook, IL', 'tipo': 'VALID', 'asunto': '2.500 líderes hispanos en Miami. Una sola marca de ferretería y hogar.', 'cuerpo': 'Hola Kim:\n\nLos negocios locales y los contratistas hispanos en Estados Unidos tienen en Ace Hardware su aliado de confianza y proximidad en cada vecindario.\n\nEl 4 y 5 de diciembre, EXMA reúne en Downtown Event Center, Fort Lauderdale (área de Miami) a 2.500 dueños de negocio, contratistas y ejecutivos hispanos que toman decisiones diarias de compra y mejoras.\n\nTrabajamos con exclusividad por categoría. En ferretería, mejoras del hogar y tiendas de proximidad, solo habrá una marca en el escenario y en los espacios del evento.\n\n¿Tiene 15 minutos esta semana o la próxima para conversar?\n\nSaludos,\n\nEdward Jiménez\nPartner Relationship Manager · EXMA Global\nedward@exmaglobal.com\nexmaglobal.com/miami'}, {'destinatario': 'Bob Rupczynski', 'empresa': 'Boost Mobile (Dish Wireless)', 'email': 'bob.rupczynski@dish.com', 'tz': 'MDT', 'location': 'Denver, CO', 'tipo': 'VALID', 'asunto': '2.500 líderes hispanos en Miami. Una sola red móvil prepago e innovadora.', 'cuerpo': 'Hola Bob:\n\nEl mercado hispano en Estados Unidos ha sido históricamente la base más leal, dinámica y demandante de conectividad inalámbrica accesible y de alto rendimiento.\n\nEl 4 y 5 de diciembre, EXMA reúne en Downtown Event Center, Fort Lauderdale (área metropolitana de Miami) a 2.500 profesionales, creadores y empresarios hispanos conectados al 100% en sus dispositivos móviles.\n\nTrabajamos con exclusividad por categoría. En telefonía móvil inalámbrica de valor, habrá una sola marca aliada con visibilidad prioritaria en el evento.\n\n¿Tiene 15 minutos esta semana o la próxima para conversar?\n\nSaludos,\n\nEdward Jiménez\nPartner Relationship Manager · EXMA Global\nedward@exmaglobal.com\nexmaglobal.com/miami'}, {'destinatario': 'Alicia Tillman', 'empresa': 'Delta Air Lines', 'email': 'alicia.tillman@delta.com', 'tz': 'EDT', 'location': 'Atlanta, GA', 'tipo': 'VALID', 'asunto': '2.500 líderes hispanos en Miami. Una sola aerolínea aliada.', 'cuerpo': 'Hola Alicia:\n\nLa conexión de negocios entre el sur de la Florida, Latinoamérica y los principales centros financieros de Estados Unidos tiene en Delta una experiencia de viaje preferida por el viajero corporativo frecuente.\n\nEl 4 y 5 de diciembre, EXMA celebra su cumbre en Downtown Event Center, Fort Lauderdale (área de Miami), reuniendo a 2.500 tomadores de decisión y empresarios hispanos con alto volumen de viajes comerciales.\n\nTrabajamos con exclusividad total por categoría. En aviación comercial y programas de lealtad para ejecutivos, solo habrá una aerolínea oficial presente.\n\n¿Tiene 15 minutos esta semana o la próxima para conversar?\n\nSaludos,\n\nEdward Jiménez\nPartner Relationship Manager · EXMA Global\nedward@exmaglobal.com\nexmaglobal.com/miami'}, {'destinatario': 'Mark Kirkham', 'empresa': 'PepsiCo', 'email': 'mark.kirkham@pepsico.com', 'tz': 'EDT', 'location': 'Purchase, NY', 'tipo': 'VALID', 'asunto': '2.500 líderes hispanos en Miami. Una sola marca de bebidas refrescantes.', 'cuerpo': 'Hola Mark:\n\nPepsiCo comprende como pocos el dinamismo cultural, la música y la pasión que mueven al consumidor hispano en Estados Unidos y a nivel internacional.\n\nEl 4 y 5 de diciembre, EXMA reúne en Downtown Event Center, Fort Lauderdale (área de Miami) a 2.500 líderes, ejecutivos y creadores de contenido hispanos.\n\nTrabajamos bajo exclusividad de categoría. En bebidas refrescantes y experiencias de hidratación, solo habrá una marca en el escenario y en los espacios VIP del festival.\n\n¿Tiene 15 minutos esta semana o la próxima para conversar?\n\nSaludos,\n\nEdward Jiménez\nPartner Relationship Manager · EXMA Global\nedward@exmaglobal.com\nexmaglobal.com/miami'}, {'destinatario': 'Luis Fernández', 'empresa': 'Telemundo (NBCUniversal)', 'email': 'luis.fernandez@nbcuni.com', 'tz': 'EDT', 'location': 'Miami, FL', 'tipo': 'VALID', 'asunto': '2.500 líderes hispanos en Miami. Un solo socio líder de televisión hispana.', 'cuerpo': 'Hola Luis:\n\nTelemundo es el referente periodístico, de entretenimiento y de conexión comunitaria más influyente de la televisión hispana en Estados Unidos, con su sede principal aquí en Miami.\n\nEl 4 y 5 de diciembre, EXMA reúne en Downtown Event Center, Fort Lauderdale (área de Miami) a 2.500 líderes empresariales, comunicadores y figuras públicas hispanas del país.\n\nTrabajamos con exclusividad por categoría. En televisión abierta y medios de comunicación en español, buscamos al aliado mediático principal del encuentro.\n\n¿Tiene 15 minutos esta semana o la próxima para conversar sobre esta sinergia?\n\nSaludos,\n\nEdward Jiménez\nPartner Relationship Manager · EXMA Global\nedward@exmaglobal.com\nexmaglobal.com/miami'}, {'destinatario': 'Duarte Figueira', 'empresa': 'Universal Music Latino', 'email': 'duarte.figueira@umusic.com', 'tz': 'EDT', 'location': 'Miami, FL', 'tipo': 'VALID', 'asunto': '2.500 líderes hispanos en Miami. Una sola disquera líder en entretenimiento.', 'cuerpo': 'Hola Duarte:\n\nLa música latina hoy define la cultura global y las marcas están desesperadas por entender cómo vincularse auténticamente con el poder de nuestros artistas y creadores.\n\nEl 4 y 5 de diciembre, EXMA reúne en Downtown Event Center, Fort Lauderdale (área de Miami) a 2.500 ejecutivos, marcas corporativas y emprendedores hispanos en un festival que combina negocios, cultura y entretenimiento.\n\nTrabajamos con exclusividad por categoría. En industria de la música, entretenimiento y management artístico, solo habrá una disquera líder aliada.\n\n¿Tiene 15 minutos esta semana o la próxima para conversar?\n\nSaludos,\n\nEdward Jiménez\nPartner Relationship Manager · EXMA Global\nedward@exmaglobal.com\nexmaglobal.com/miami'}, {'destinatario': 'David Wrubleski', 'empresa': 'The Hershey Company', 'email': 'dwrubleski@hersheys.com', 'tz': 'EDT', 'location': 'Hershey, PA', 'tipo': 'VALID', 'asunto': '2.500 líderes hispanos en Miami. Una sola marca de chocolates y confitería.', 'cuerpo': 'Hola David:\n\nThe Hershey Company representa momentos de unión, celebración y tradición en los hogares hispanos, con una presencia omnicanal ejemplar en todo Estados Unidos.\n\nEl 4 y 5 de diciembre, EXMA reúne en Downtown Event Center, Fort Lauderdale (área de Miami) a 2.500 ejecutivos, compradores y familias empresarias hispanas de todo el país.\n\nTrabajamos con exclusividad por categoría. En chocolates, dulces y confitería de consumo masivo, solo habrá una marca presente en las experiencias del evento.\n\n¿Tiene 15 minutos esta semana o la próxima para conversar?\n\nSaludos,\n\nEdward Jiménez\nPartner Relationship Manager · EXMA Global\nedward@exmaglobal.com\nexmaglobal.com/miami'}, {'destinatario': 'David Joyner', 'empresa': 'CVS Health', 'email': 'david.joyner@cvshealth.com', 'tz': 'EDT', 'location': 'Woonsocket, RI', 'tipo': 'VALID', 'asunto': '2.500 líderes hispanos en Miami. Una sola marca de farmacia y salud preventiva.', 'cuerpo': 'Hola David:\n\nEl bienestar y la salud preventiva de las familias y profesionales hispanos en Estados Unidos encuentran en CVS su punto de contacto diario en miles de comunidades.\n\nEl 4 y 5 de diciembre, EXMA reúne en Downtown Event Center, Fort Lauderdale (área de Miami) a 2.500 líderes empresariales y cabezas de hogar hispanos con alta conciencia de salud integral.\n\nTrabajamos con exclusividad por categoría. En farmacia comunitaria, bienestar y servicios de salud, solo habrá una organización aliada en el escenario.\n\n¿Tiene 15 minutos esta semana o la próxima para conversar?\n\nSaludos,\n\nEdward Jiménez\nPartner Relationship Manager · EXMA Global\nedward@exmaglobal.com\nexmaglobal.com/miami'}, {'destinatario': 'Sean Summers', 'empresa': 'Mercado Libre', 'email': 'sean.summers@mercadolibre.com', 'tz': 'EDT', 'location': 'Miami, FL / LatAm', 'tipo': 'VALID', 'asunto': '2.500 líderes hispanos en Miami. Una sola potencia de comercio y fintech.', 'cuerpo': 'Hola Sean:\n\nMercado Libre es el mayor orgullo tecnológico y de comercio digital de nuestra región, transformando la vida de millones de emprendedores y compradores a escala continental.\n\nEl 4 y 5 de diciembre, EXMA celebra en Downtown Event Center, Fort Lauderdale (área metropolitana de Miami) su cumbre anual ante 2.500 fundadores, directores de marketing y líderes de negocio hispanos y latinoamericanos.\n\nTrabajamos con exclusividad por categoría. En ecosistemas de e-commerce y pagos transfronterizos latinoamericanos, solo habrá una compañía en el escenario principal.\n\n¿Tiene 15 minutos esta semana o la próxima para conversar?\n\nSaludos,\n\nEdward Jiménez\nPartner Relationship Manager · EXMA Global\nedward@exmaglobal.com\nexmaglobal.com/miami'}, {'destinatario': 'Mike Katz', 'empresa': 'T-Mobile US', 'email': 'mike.katz@t-mobile.com', 'tz': 'PDT', 'location': 'Bellevue, WA', 'tipo': 'VALID', 'asunto': '2.500 líderes hispanos en Miami. Una sola red móvil 5G sin fronteras.', 'cuerpo': 'Hola Mike:\n\nLa propuesta de valor de T-Mobile, eliminando tarifas de roaming en viajes y entregando la mejor experiencia 5G, resuena profundamente con la comunidad hispana y sus lazos binacionales.\n\nEl 4 y 5 de diciembre, EXMA reúne en Downtown Event Center, Fort Lauderdale (área de Miami) a 2.500 líderes de negocio y ejecutivos hispanos que dependen de la conectividad móvil para liderar sus organizaciones.\n\nTrabajamos con exclusividad por categoría. En redes 5G y telecomunicaciones corporativas y de consumo, solo habrá una marca en el escenario principal.\n\n¿Tiene 15 minutos esta semana o la próxima para conversar?\n\nSaludos,\n\nEdward Jiménez\nPartner Relationship Manager · EXMA Global\nedward@exmaglobal.com\nexmaglobal.com/miami'}]

def generate_followup_body(p):
    first_name = p['destinatario'].split()[0]
    asunto_orig = p['asunto']
    cuerpo_orig = p['cuerpo']
    empresa = p['empresa']
    
    cat = 'su sector'
    if 'ferretería' in asunto_orig or 'hogar' in asunto_orig: cat = 'ferretería y mejoras del hogar'
    elif 'prepago' in asunto_orig or 'móvil' in asunto_orig: cat = 'telefonía y conectividad móvil'
    elif 'aerolínea' in asunto_orig: cat = 'aerolíneas y viajes de negocios'
    elif 'bebidas' in asunto_orig: cat = 'bebidas y refrescos'
    elif 'televisión' in asunto_orig or 'socio' in asunto_orig: cat = 'medios y televisión hispana'
    elif 'disquera' in asunto_orig or 'entretenimiento' in asunto_orig: cat = 'música y entretenimiento'
    elif 'chocolates' in asunto_orig or 'confitería' in asunto_orig: cat = 'confitería y snacks dulces'
    elif 'farmacia' in asunto_orig or 'salud' in asunto_orig: cat = 'salud preventiva y farmacias'
    elif 'comercio' in asunto_orig or 'fintech' in asunto_orig: cat = 'comercio electrónico y fintech'
    elif '5g' in asunto_orig or 'red móvil' in asunto_orig: cat = 'telecomunicaciones y red 5G'

    body = f"""Hola {first_name}:

Quería asegurarme de que mi correo de la semana pasada no se hubiera traspapelado entre sus pendientes.

Como le mencionaba, el 4 y 5 de diciembre reunimos en Miami (Downtown Event Center, Fort Lauderdale) a 2.500 dueños de negocio, ejecutivos C-Level y líderes hispanos en la cumbre EXMA Miami 2026.

Trabajamos con exclusividad de una sola marca por categoría. En {cat}, queremos confirmar si {empresa} tiene interés en liderar esa presencia preferente en el escenario y en el evento antes de abrir conversaciones con otros aliados de la industria.

¿Tiene 15 minutos este jueves o viernes para conversar brevemente?

Saludos cordiales,

{signature}

--- Mensaje original ---
De: Edward Jiménez · EXMA Global <edward@exmaglobal.com>
Fecha: 1 de octubre de 2026
Asunto: {asunto_orig}
Para: {p['destinatario']} <{p['email']}>

{cuerpo_orig}"""
    return body

def run_campaign(dry_run=False):
    total = len(prospects)
    print(f"==================================================")
    print(f"🚀 INICIANDO TOQUE 2 SEGUIMIENTO MIÉRCOLES 7-OCT ({total} CORREOS)")
    print(f"Modo: {'SIMULACIÓN (DRY RUN)' if dry_run else 'ENVÍO EN VIVO'}")
    print(f"Hora actual: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"==================================================")

    if not dry_run:
        send_alert(f"🚀 [EXMA Outreach] Arrancó el Toque 2 de Seguimiento Miércoles ({total} correos)",
                   f"Despachando seguimiento a 4 días hábiles para los 10 prospectos del Jueves 01-Oct 100% VALIDADOS en EmailAwesome.")

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
        summary_msg = f"Seguimiento Miércoles finalizado: {success}/{total} enviados. Errores: {errors}"
        send_alert(f"🎉 [EXMA Outreach] Toque 2 Miércoles COMPLETADO ({success}/{total})", summary_msg)

    print(f"Finalizado: {success}/{total} enviados. Errores: {errors}")

if __name__ == '__main__':
    dry = '--dry-run' in sys.argv
    run_campaign(dry_run=dry)
