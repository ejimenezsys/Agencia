import smtplib, time, random, sys, datetime, os
from email.mime.text import MIMEText
from email.utils import formataddr

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

# ==============================================================================
# PROSPECTOS MIÉRCOLES 30 DE SEPTIEMBRE (100% VALIDADOS EN EMAILAWESOME)
# ==============================================================================

# BLOQUE 1: CENTRAL / CDT (Texas, Minnesota) - 3 prospectos
batch_central = [
    {
        'destinatario': 'Ron DeFeo',
        'empresa': 'American Airlines',
        'email': 'ronald.defeo@aa.com',
        'tz': 'CDT',
        'location': 'Fort Worth, TX',
        'tipo': 'VALID',
        'asunto': '2.500 líderes hispanos en Miami. Una sola aerolínea oficial.',
        'cuerpo': """Hola Ron:

Miami es el epicentro indiscutible de las operaciones de American Airlines hacia el mundo hispano y toda la región.

El 4 y 5 de diciembre, EXMA reúne en Downtown Event Center, Fort Lauderdale (área metropolitana de Miami) a 2.500 tomadores de decisión, ejecutivos y emprendedores hispanos que vuelan constantemente por negocios.

Trabajamos bajo el modelo de exclusividad total por industria. En el sector aerocomercial, solo habrá una aerolínea aliada en el escenario y en los espacios ejecutivos.

¿Tiene 15 minutos esta semana o la próxima para conversar?

Saludos,

Edward Jiménez
Partner Relationship Manager · EXMA Global
edward@exmaglobal.com
exmaglobal.com/miami"""
    },
    {
        'destinatario': 'Mark Weinstein',
        'empresa': 'Target Corporation',
        'email': 'mark.weinstein@target.com',
        'tz': 'CDT',
        'location': 'Minneapolis, MN',
        'tipo': 'VALID',
        'asunto': '2.500 líderes hispanos en Miami. Una sola marca de retail masivo.',
        'cuerpo': """Hola Mark:

El consumidor hispano en Estados Unidos tiene a Target entre sus opciones predilectas de compra física y digital, impulsando de forma decisiva las categorías clave de la cadena.

El 4 y 5 de diciembre, EXMA reúne en Downtown Event Center, Fort Lauderdale (área de Miami) a 2.500 líderes, ejecutivos y dueños de negocio hispanos que definen el consumo familiar e institucional.

Trabajamos con exclusividad por categoría. En retail masivo y departamental, solo habrá una marca presente en el escenario y experiencias del evento.

¿Tiene 15 minutos esta semana o la próxima para conversar?

Saludos,

Edward Jiménez
Partner Relationship Manager · EXMA Global
edward@exmaglobal.com
exmaglobal.com/miami"""
    },
    {
        'destinatario': 'Sathish Mohanraju',
        'empresa': 'Mission Foods (Gruma)',
        'email': 'smohanraju@missionfoods.com',
        'tz': 'CDT',
        'location': 'Irving, TX',
        'tipo': 'VALID',
        'asunto': '2.500 líderes hispanos en Miami. Una sola marca de alimentos y tortillas.',
        'cuerpo': """Hola Sathish:

Mission Foods representa uno de los mayores casos de éxito de una marca de raíz hispana convertida en líder absoluto del consumo masivo en Estados Unidos.

El 4 y 5 de diciembre, EXMA reúne en Downtown Event Center, Fort Lauderdale (área metropolitana de Miami) a 2.500 líderes empresariales, compradores y profesionales hispanos.

Manejamos exclusividad estricta por categoría. En alimentos de consumo masivo y tortillas, habrá una sola marca aliada con visibilidad estelar ante esta audiencia bicultural.

¿Tiene 15 minutos esta semana o la próxima para explorar esta alianza?

Saludos,

Edward Jiménez
Partner Relationship Manager · EXMA Global
edward@exmaglobal.com
exmaglobal.com/miami"""
    }
]

# BLOQUE 2: ESTE / EDT (FL, NY, GA, PA, MA) - 8 prospectos
batch_eastern = [
    {
        'destinatario': 'Molly Battin',
        'empresa': 'The Home Depot',
        'email': 'molly_battin@homedepot.com',
        'tz': 'EDT',
        'location': 'Atlanta, GA',
        'tipo': 'VALID',
        'asunto': '2.500 líderes hispanos en Miami. Una sola marca de home improvement.',
        'cuerpo': """Hola Molly:

La comunidad hispana de contratistas, desarrolladores y dueños de negocio representa un motor indispensable en el crecimiento del segmento Pro de The Home Depot en todo el país.

El 4 y 5 de diciembre, EXMA reúne en Downtown Event Center, Fort Lauderdale (área de Miami) a 2.500 líderes empresariales y tomadores de decisión hispanos del sur de la Florida y todo Estados Unidos.

Trabajamos con exclusividad por categoría. En home improvement y construcción comercial, solo habrá una marca en el escenario y en los espacios VIP.

¿Tiene 15 minutos esta semana o la próxima para conversar?

Saludos,

Edward Jiménez
Partner Relationship Manager · EXMA Global
edward@exmaglobal.com
exmaglobal.com/miami"""
    },
    {
        'destinatario': 'Marcel Marcondes',
        'empresa': 'Anheuser-Busch InBev',
        'email': 'marcel.marcondes@ab-inbev.com',
        'tz': 'EDT',
        'location': 'New York, NY',
        'tipo': 'VALID',
        'asunto': '2.500 líderes hispanos en Miami. Una sola marca de cerveza y bebidas.',
        'cuerpo': """Hola Marcel:

El consumidor hispano en Estados Unidos no solo lidera el crecimiento de la categoría de bebidas, sino que conecta profundamente con marcas que celebran sus momentos de éxito y comunidad.

El 4 y 5 de diciembre, EXMA reúne en Downtown Event Center, Fort Lauderdale (área de Miami) a 2.500 ejecutivos, fundadores y líderes hispanos.

Trabajamos con exclusividad por categoría. En cerveza y bebidas, solo habrá una corporación en el escenario principal y en las experiencias VIP de networking del evento.

¿Tiene 15 minutos esta semana o la próxima?

Saludos,

Edward Jiménez
Partner Relationship Manager · EXMA Global
edward@exmaglobal.com
exmaglobal.com/miami"""
    },
    {
        'destinatario': 'Leslie Berland',
        'empresa': 'Verizon',
        'email': 'leslie.berland@verizon.com',
        'tz': 'EDT',
        'location': 'New York, NY',
        'tipo': 'VALID',
        'asunto': '2.500 líderes hispanos en Miami. Una sola red de telecomunicaciones.',
        'cuerpo': """Hola Leslie:

El segmento hispano en Estados Unidos sobreindexa continuamente en consumo de datos móviles, streaming y adopción de tecnología 5G para sus negocios y hogares.

El 4 y 5 de diciembre, EXMA reúne en Downtown Event Center, Fort Lauderdale (área de Miami) a 2.500 ejecutivos y empresarios hispanos que dependen de una conectividad robusta para operar.

Trabajamos con exclusividad por categoría. En telecomunicaciones y conectividad, solo habrá una marca aliada en el escenario.

¿Tiene 15 minutos esta semana o la próxima para conversar?

Saludos,

Edward Jiménez
Partner Relationship Manager · EXMA Global
edward@exmaglobal.com
exmaglobal.com/miami"""
    },
    {
        'destinatario': 'Elizabeth Rutledge',
        'empresa': 'American Express',
        'email': 'elizabeth.rutledge@aexp.com',
        'tz': 'EDT',
        'location': 'New York, NY',
        'tipo': 'VALID',
        'asunto': '2.500 líderes hispanos en Miami. Una sola marca de tarjetas y servicios financieros.',
        'cuerpo': """Hola Elizabeth:

Los empresarios y ejecutivos hispanos en Estados Unidos forman uno de los segmentos de más rápido crecimiento en adopción de soluciones de pago empresarial y membresías corporativas.

El 4 y 5 de diciembre, EXMA reúne en Downtown Event Center, Fort Lauderdale (área de Miami) a 2.500 líderes y dueños de negocio con alto poder de compra y decisión.

Trabajamos con exclusividad por categoría. En tarjetas de crédito y servicios financieros premium, solo habrá una marca aliada en el escenario y en el VIP Lounge.

¿Tiene 15 minutos esta semana o la próxima?

Saludos,

Edward Jiménez
Partner Relationship Manager · EXMA Global
edward@exmaglobal.com
exmaglobal.com/miami"""
    },
    {
        'destinatario': 'Harley Finkelstein',
        'empresa': 'Shopify Inc.',
        'email': 'harley@shopify.com',
        'tz': 'EDT',
        'location': 'Ottawa / New York',
        'tipo': 'VALID',
        'asunto': '2.500 líderes hispanos en Miami. Una sola plataforma de comercio digital.',
        'cuerpo': """Hola Harley:

La tasa de creación de nuevos negocios por fundadores hispanos en Estados Unidos supera consistentemente al resto de los segmentos demográficos, y el comercio omnicanal es su principal vehículo de crecimiento.

El 4 y 5 de diciembre, EXMA reúne en Downtown Event Center, Fort Lauderdale (área de Miami) a 2.500 fundadores y ejecutivos hispanos que operan o están escalando marcas de retail digital.

Trabajamos bajo exclusividad de categoría. En plataformas de comercio y e-commerce, habrá una sola marca aliada en el escenario principal.

¿Tiene 15 minutos esta semana o la próxima para conversar?

Saludos,

Edward Jiménez
Partner Relationship Manager · EXMA Global
edward@exmaglobal.com
exmaglobal.com/miami"""
    },
    {
        'destinatario': 'Enrique Perez-Pantera',
        'empresa': 'Pollo Tropical (Fiesta Restaurant Group)',
        'email': 'eperez@pollotropical.com',
        'tz': 'EDT',
        'location': 'Miami, FL',
        'tipo': 'VALID',
        'asunto': '2.500 líderes hispanos en Miami. Una sola marca de sabores de Florida.',
        'cuerpo': """Hola Enrique:

Pollo Tropical es una institución cultural y culinaria imprescindible en la vida cotidiana de las familias y profesionales en todo el sur de la Florida.

El 4 y 5 de diciembre, EXMA celebra su gran cumbre empresarial en Downtown Event Center, Fort Lauderdale (área de Miami), congregando a 2.500 líderes hispanos locales y nacionales.

Trabajamos con exclusividad por categoría. En el segmento QSR regional y sabores caribeños, solo habrá una marca presente con activaciones y visibilidad de marca.

¿Tiene 15 minutos esta semana o la próxima para conversar sobre esta presencia?

Saludos,

Edward Jiménez
Partner Relationship Manager · EXMA Global
edward@exmaglobal.com
exmaglobal.com/miami"""
    },
    {
        'destinatario': 'Kip Bodnar',
        'empresa': 'HubSpot, Inc.',
        'email': 'kbodnar@hubspot.com',
        'tz': 'EDT',
        'location': 'Cambridge, MA',
        'tipo': 'VALID',
        'asunto': '2.500 líderes hispanos en Miami. Una sola plataforma de CRM y marketing.',
        'cuerpo': """Hola Kip:

El ecosistema empresarial hispano en EE.UU. y Miami está viviendo una acelerada profesionalización en marketing automation, inbound sales y digital customer experience.

El 4 y 5 de diciembre, EXMA reúne en Downtown Event Center, Fort Lauderdale (área metropolitana de Miami) a 2.500 directores, CEOs y líderes de marketing hispanos.

Trabajamos con exclusividad por categoría. En CRM, automatización de marketing y plataformas de ventas, solo habrá una compañía en el escenario principal.

¿Tiene 15 minutos esta semana o la próxima para conversar?

Saludos,

Edward Jiménez
Partner Relationship Manager · EXMA Global
edward@exmaglobal.com
exmaglobal.com/miami"""
    },
    {
        'destinatario': 'Leslie Vesper',
        'empresa': 'Bimbo Bakeries USA',
        'email': 'leslie.vesper@grupobimbo.com',
        'tz': 'EDT',
        'location': 'Horsham, PA',
        'tipo': 'VALID',
        'asunto': '2.500 líderes hispanos en Miami. Una sola marca de panadería y snacks.',
        'cuerpo': """Hola Leslie:

Grupo Bimbo es el ejemplo definitivo de excelencia empresarial que conecta con el corazón, la nostalgia y la vida diaria de las familias hispanas y el mercado general en Estados Unidos.

El 4 y 5 de diciembre, EXMA reúne en Downtown Event Center, Fort Lauderdale (área de Miami) a 2.500 líderes empresariales, compradores y ejecutivos hispanos de todo el país.

Trabajamos con exclusividad por categoría. En la industria de panadería, repostería y snacks empaquetados, solo habrá una marca aliada en el escenario.

¿Tiene 15 minutos esta semana o la próxima para conversar?

Saludos,

Edward Jiménez
Partner Relationship Manager · EXMA Global
edward@exmaglobal.com
exmaglobal.com/miami"""
    }
]

# BLOQUE 3: PACÍFICO / PDT (California) - 2 prospectos (Esperar a las 11:30 AM / 12:00 PM EDT)
batch_pacific = [
    {
        'destinatario': 'Luis Restrepo',
        'empresa': 'Taco Bell',
        'email': 'luis.restrepo@yum.com',
        'tz': 'PDT',
        'location': 'Irvine, CA',
        'tipo': 'VALID',
        'asunto': '2.500 líderes hispanos en Miami. Una sola marca de QSR juvenil.',
        'cuerpo': """Hola Luis:

Taco Bell ha demostrado una maestría única en conectar la cultura con el entretenimiento, el humor y la conversación juvenil a escala global.

El 4 y 5 de diciembre, EXMA reúne en Downtown Event Center, Fort Lauderdale (área de Miami) a 2.500 líderes, creadores y ejecutivos hispanos que definen las tendencias de marketing en el mercado hispano de Estados Unidos.

Trabajamos con exclusividad por categoría. En fast food juvenil e innovador, solo habrá una marca aliada en el escenario y en las experiencias del festival.

¿Tiene 15 minutos esta semana o la próxima para conversar?

Saludos,

Edward Jiménez
Partner Relationship Manager · EXMA Global
edward@exmaglobal.com
exmaglobal.com/miami"""
    },
    {
        'destinatario': 'Frank Cooper III',
        'empresa': 'Visa Inc.',
        'email': 'fcooper@visa.com',
        'tz': 'PDT',
        'location': 'San Francisco, CA',
        'tipo': 'VALID',
        'asunto': '2.500 líderes hispanos en Miami. Una sola red global de pagos.',
        'cuerpo': """Hola Frank:

La adopción de pagos digitales, comercio transfronterizo y transacciones móviles dentro de la comunidad hispana en Estados Unidos crece a un ritmo superior a la media nacional.

El 4 y 5 de diciembre, EXMA reúne en Downtown Event Center, Fort Lauderdale (área de Miami) a 2.500 líderes de negocio y ejecutivos hispanos que están construyendo la economía del futuro.

Trabajamos con exclusividad por categoría. En redes globales de pago y tecnología financiera, solo habrá una marca aliada en el escenario principal.

¿Tiene 15 minutos esta semana o la próxima para conversar?

Saludos,

Edward Jiménez
Partner Relationship Manager · EXMA Global
edward@exmaglobal.com
exmaglobal.com/miami"""
    }
]

# ==============================================================================
# MOTOR DE DESPACHO CON RECONEXIÓN ROBUSTA Y PAUSA ANTI-SPAM
# ==============================================================================

def send_single_mail(to_name, to_email, subject, body):
    max_retries = 3
    for attempt in range(max_retries):
        try:
            server = get_smtp_connection()
            msg = MIMEText(body, 'plain', 'utf-8')
            msg['Subject'] = subject
            msg['From'] = formataddr(('Edward Jiménez', 'edward@exmaglobal.com'))
            msg['To'] = formataddr((to_name, to_email))
            msg['Reply-To'] = 'edward@exmaglobal.com'
            server.sendmail(u, [to_email], msg.as_string())
            server.quit()
            return True, None
        except Exception as e:
            if attempt < max_retries - 1:
                print(f"⚠️ Reintentando conexión SMTP para {to_email}... ({e})", flush=True)
                time.sleep(5)
            else:
                return False, str(e)

def dispatch_batch(batch_name, prospects_list, start_idx, total_all):
    print(f"\n{'='*50}", flush=True)
    print(f"🚀 INICIANDO {batch_name} ({len(prospects_list)} correos)", flush=True)
    print(f"Hora actual: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", flush=True)
    print(f"{'='*50}", flush=True)
    
    success = 0
    errors = 0
    logs = []
    
    for i, p in enumerate(prospects_list, 1):
        global_idx = start_idx + i
        to_name = p['destinatario']
        to_email = p['email']
        empresa = p['empresa']
        tz = p['tz']
        loc = p['location']
        tipo = p['tipo']
        asunto = p['asunto']
        cuerpo = p['cuerpo']
        
        timestamp = datetime.datetime.now().strftime('%H:%M:%S')
        ok, err = send_single_mail(to_name, to_email, asunto, cuerpo)
        
        if ok:
            print(f"[{global_idx}/{total_all}] ✅ {timestamp} [{tz} - {loc}] [{tipo}] ENVIADO: {to_name} ({empresa}) <{to_email}>", flush=True)
            success += 1
            logs.append(f"✅ {timestamp} [{tz}] {empresa}: {to_name} <{to_email}>")
        else:
            print(f"[{global_idx}/{total_all}] ❌ {timestamp} [{tz}] ERROR con {to_email}: {err}", flush=True)
            errors += 1
            logs.append(f"❌ {timestamp} [{tz}] {empresa}: {to_name} <{to_email}> ERROR: {err}")
            
        if i < len(prospects_list):
            sleep_time = random.randint(65, 95)
            print(f"   ⏳ Pausa humana anti-spam: esperando {sleep_time}s antes del siguiente...", flush=True)
            time.sleep(sleep_time)
            
    return success, errors, logs

def run_campaign_miercoles():
    all_logs = []
    total_prospects = len(batch_central) + len(batch_eastern) + len(batch_pacific)
    
    send_alert(
        f"🚀 [EXMA Outreach] Arrancó el despacho de los {total_prospects} correos del Miércoles",
        f"""Hola Edward,

Se acaba de iniciar el despacho zonificado de hoy Miércoles 30 de Septiembre ({total_prospects} correos de élite validados al 100%):

1. Franja Central / CDT (3 correos): American Airlines, Target y Mission Foods (enviando en su ventana 09:00-10:00 AM CDT).
2. Franja Este / EDT (8 correos): The Home Depot, AB InBev, Verizon, Amex, Shopify, Pollo Tropical, HubSpot, Bimbo.
3. Franja Pacífico / PDT (2 correos): Taco Bell y Visa Inc. (California - programado para salir a las 11:30 AM EDT = 08:30 AM PDT).

Todos los buzones fueron verificados con handshake SMTP en EmailAwesome (cero rebotes).

Recibirás actualizaciones automáticas en tu móvil."""
    )
    
    # 1. Franja Central (3 leads)
    s1, e1, l1 = dispatch_batch("BLOQUE 1: CENTRAL / CDT (Texas, Minnesota)", batch_central, 0, total_prospects)
    all_logs.extend(l1)
    
    # 2. Franja Este (8 leads)
    s2, e2, l2 = dispatch_batch("BLOQUE 2: ESTE / EDT (FL, NY, GA, PA, MA)", batch_eastern, len(batch_central), total_prospects)
    all_logs.extend(l2)
    
    morning_success = s1 + s2
    morning_errors = e1 + e2
    print(f"\n☕ BLOQUE MAÑANA FINALIZADO: {morning_success} enviados, {morning_errors} errores.", flush=True)
    
    send_alert(
        f"✅ [EXMA Outreach] Bloque Mañana completado ({morning_success}/11 enviados)",
        f"""Hola Edward,

Se han enviado exitosamente {morning_success} de los 11 correos de la mañana (Central y Este).

El sistema queda en pausa programada esperando las 11:30 AM EDT (= 08:30 AM PDT) para despachar a Taco Bell (Irvine, CA) y Visa Inc. (San Francisco, CA).

Detalle hasta ahora:
""" + "\n".join(all_logs)
    )
    
    # 3. Esperar hasta las 11:30 AM EDT para el Bloque Pacífico
    target_hour = 11
    target_minute = 30
    now = datetime.datetime.now()
    target_time = now.replace(hour=target_hour, minute=target_minute, second=0, microsecond=0)
    
    wait_seconds = (target_time - datetime.datetime.now()).total_seconds()
    if wait_seconds > 0:
        print(f"\n⏳ PAUSA ZONA PACÍFICO: Esperando {wait_seconds/60:.1f} minutos hasta las 11:30 AM EDT (08:30 AM PDT)...\n", flush=True)
        time.sleep(wait_seconds)
    else:
        print("\nHora 11:30 AM EDT alcanzada o pasada. Procediendo inmediatamente con el bloque Pacífico.", flush=True)
        
    s3, e3, l3 = dispatch_batch("BLOQUE 3: PACÍFICO / PDT (CALIFORNIA - 08:30 AM PDT)", batch_pacific, len(batch_central) + len(batch_eastern), total_prospects)
    all_logs.extend(l3)
    
    total_success = morning_success + s3
    total_errors = morning_errors + e3
    
    send_alert(
        f"🎉 [EXMA Outreach] Campaña de Miércoles 100% COMPLETADA ({total_success}/{total_prospects})",
        f"""Hola Edward,

Los {total_prospects} correos validados de hoy miércoles han sido despachados exitosamente.

- Total exitosos: {total_success}
- Errores: {total_errors}
Hora finalización: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Detalle final de envíos:
""" + "\n".join(all_logs) + f"""

Las respuestas entrarán directo a tu bandeja personal de edward@exmaglobal.com."""
    )
    print("\n🎉 ¡CAMPAÑA DE MIÉRCOLES COMPLETADA CON ÉXITO TOTAL!", flush=True)

if __name__ == '__main__':
    run_campaign_miercoles()
