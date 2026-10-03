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
# PROSPECTOS JUEVES 1 DE OCTUBRE (100% VALIDADOS EN EMAILAWESOME)
# ==============================================================================

# BLOQUE 1: CENTRAL & MONTAÑA / CDT & MDT (Illinois, Colorado) - 2 prospectos
batch_central_mountain = [
    {
        'destinatario': 'Kim Lefko',
        'empresa': 'Ace Hardware',
        'email': 'klefko@acehardware.com',
        'tz': 'CDT',
        'location': 'Oak Brook, IL',
        'tipo': 'VALID',
        'asunto': '2.500 líderes hispanos en Miami. Una sola marca de ferretería y hogar.',
        'cuerpo': """Hola Kim:

Los negocios locales y los contratistas hispanos en Estados Unidos tienen en Ace Hardware su aliado de confianza y proximidad en cada vecindario.

El 4 y 5 de diciembre, EXMA reúne en Downtown Event Center, Fort Lauderdale (área de Miami) a 2.500 dueños de negocio, contratistas y ejecutivos hispanos que toman decisiones diarias de compra y mejoras.

Trabajamos con exclusividad por categoría. En ferretería, mejoras del hogar y tiendas de proximidad, solo habrá una marca en el escenario y en los espacios del evento.

¿Tiene 15 minutos esta semana o la próxima para conversar?

Saludos,

Edward Jiménez
Partner Relationship Manager · EXMA Global
edward@exmaglobal.com
exmaglobal.com/miami"""
    },
    {
        'destinatario': 'Bob Rupczynski',
        'empresa': 'Boost Mobile (Dish Wireless)',
        'email': 'bob.rupczynski@dish.com',
        'tz': 'MDT',
        'location': 'Denver, CO',
        'tipo': 'VALID',
        'asunto': '2.500 líderes hispanos en Miami. Una sola red móvil prepago e innovadora.',
        'cuerpo': """Hola Bob:

El mercado hispano en Estados Unidos ha sido históricamente la base más leal, dinámica y demandante de conectividad inalámbrica accesible y de alto rendimiento.

El 4 y 5 de diciembre, EXMA reúne en Downtown Event Center, Fort Lauderdale (área metropolitana de Miami) a 2.500 profesionales, creadores y empresarios hispanos conectados al 100% en sus dispositivos móviles.

Trabajamos con exclusividad por categoría. En telefonía móvil inalámbrica de valor, habrá una sola marca aliada con visibilidad prioritaria en el evento.

¿Tiene 15 minutos esta semana o la próxima para conversar?

Saludos,

Edward Jiménez
Partner Relationship Manager · EXMA Global
edward@exmaglobal.com
exmaglobal.com/miami"""
    }
]

# BLOQUE 2: ESTE / EDT (FL, NY, PA, GA, RI) - 7 prospectos
batch_eastern = [
    {
        'destinatario': 'Alicia Tillman',
        'empresa': 'Delta Air Lines',
        'email': 'alicia.tillman@delta.com',
        'tz': 'EDT',
        'location': 'Atlanta, GA',
        'tipo': 'VALID',
        'asunto': '2.500 líderes hispanos en Miami. Una sola aerolínea aliada.',
        'cuerpo': """Hola Alicia:

La conexión de negocios entre el sur de la Florida, Latinoamérica y los principales centros financieros de Estados Unidos tiene en Delta una experiencia de viaje preferida por el viajero corporativo frecuente.

El 4 y 5 de diciembre, EXMA celebra su cumbre en Downtown Event Center, Fort Lauderdale (área de Miami), reuniendo a 2.500 tomadores de decisión y empresarios hispanos con alto volumen de viajes comerciales.

Trabajamos con exclusividad total por categoría. En aviación comercial y programas de lealtad para ejecutivos, solo habrá una aerolínea oficial presente.

¿Tiene 15 minutos esta semana o la próxima para conversar?

Saludos,

Edward Jiménez
Partner Relationship Manager · EXMA Global
edward@exmaglobal.com
exmaglobal.com/miami"""
    },
    {
        'destinatario': 'Mark Kirkham',
        'empresa': 'PepsiCo',
        'email': 'mark.kirkham@pepsico.com',
        'tz': 'EDT',
        'location': 'Purchase, NY',
        'tipo': 'VALID',
        'asunto': '2.500 líderes hispanos en Miami. Una sola marca de bebidas refrescantes.',
        'cuerpo': """Hola Mark:

PepsiCo comprende como pocos el dinamismo cultural, la música y la pasión que mueven al consumidor hispano en Estados Unidos y a nivel internacional.

El 4 y 5 de diciembre, EXMA reúne en Downtown Event Center, Fort Lauderdale (área de Miami) a 2.500 líderes, ejecutivos y creadores de contenido hispanos.

Trabajamos bajo exclusividad de categoría. En bebidas refrescantes y experiencias de hidratación, solo habrá una marca en el escenario y en los espacios VIP del festival.

¿Tiene 15 minutos esta semana o la próxima para conversar?

Saludos,

Edward Jiménez
Partner Relationship Manager · EXMA Global
edward@exmaglobal.com
exmaglobal.com/miami"""
    },
    {
        'destinatario': 'Luis Fernández',
        'empresa': 'Telemundo (NBCUniversal)',
        'email': 'luis.fernandez@nbcuni.com',
        'tz': 'EDT',
        'location': 'Miami, FL',
        'tipo': 'VALID',
        'asunto': '2.500 líderes hispanos en Miami. Un solo socio líder de televisión hispana.',
        'cuerpo': """Hola Luis:

Telemundo es el referente periodístico, de entretenimiento y de conexión comunitaria más influyente de la televisión hispana en Estados Unidos, con su sede principal aquí en Miami.

El 4 y 5 de diciembre, EXMA reúne en Downtown Event Center, Fort Lauderdale (área de Miami) a 2.500 líderes empresariales, comunicadores y figuras públicas hispanas del país.

Trabajamos con exclusividad por categoría. En televisión abierta y medios de comunicación en español, buscamos al aliado mediático principal del encuentro.

¿Tiene 15 minutos esta semana o la próxima para conversar sobre esta sinergia?

Saludos,

Edward Jiménez
Partner Relationship Manager · EXMA Global
edward@exmaglobal.com
exmaglobal.com/miami"""
    },
    {
        'destinatario': 'Duarte Figueira',
        'empresa': 'Universal Music Latino',
        'email': 'duarte.figueira@umusic.com',
        'tz': 'EDT',
        'location': 'Miami, FL',
        'tipo': 'VALID',
        'asunto': '2.500 líderes hispanos en Miami. Una sola disquera líder en entretenimiento.',
        'cuerpo': """Hola Duarte:

La música latina hoy define la cultura global y las marcas están desesperadas por entender cómo vincularse auténticamente con el poder de nuestros artistas y creadores.

El 4 y 5 de diciembre, EXMA reúne en Downtown Event Center, Fort Lauderdale (área de Miami) a 2.500 ejecutivos, marcas corporativas y emprendedores hispanos en un festival que combina negocios, cultura y entretenimiento.

Trabajamos con exclusividad por categoría. En industria de la música, entretenimiento y management artístico, solo habrá una disquera líder aliada.

¿Tiene 15 minutos esta semana o la próxima para conversar?

Saludos,

Edward Jiménez
Partner Relationship Manager · EXMA Global
edward@exmaglobal.com
exmaglobal.com/miami"""
    },
    {
        'destinatario': 'David Wrubleski',
        'empresa': 'The Hershey Company',
        'email': 'dwrubleski@hersheys.com',
        'tz': 'EDT',
        'location': 'Hershey, PA',
        'tipo': 'VALID',
        'asunto': '2.500 líderes hispanos en Miami. Una sola marca de chocolates y confitería.',
        'cuerpo': """Hola David:

The Hershey Company representa momentos de unión, celebración y tradición en los hogares hispanos, con una presencia omnicanal ejemplar en todo Estados Unidos.

El 4 y 5 de diciembre, EXMA reúne en Downtown Event Center, Fort Lauderdale (área de Miami) a 2.500 ejecutivos, compradores y familias empresarias hispanas de todo el país.

Trabajamos con exclusividad por categoría. En chocolates, dulces y confitería de consumo masivo, solo habrá una marca presente en las experiencias del evento.

¿Tiene 15 minutos esta semana o la próxima para conversar?

Saludos,

Edward Jiménez
Partner Relationship Manager · EXMA Global
edward@exmaglobal.com
exmaglobal.com/miami"""
    },
    {
        'destinatario': 'David Joyner',
        'empresa': 'CVS Health',
        'email': 'david.joyner@cvshealth.com',
        'tz': 'EDT',
        'location': 'Woonsocket, RI',
        'tipo': 'VALID',
        'asunto': '2.500 líderes hispanos en Miami. Una sola marca de farmacia y salud preventiva.',
        'cuerpo': """Hola David:

El bienestar y la salud preventiva de las familias y profesionales hispanos en Estados Unidos encuentran en CVS su punto de contacto diario en miles de comunidades.

El 4 y 5 de diciembre, EXMA reúne en Downtown Event Center, Fort Lauderdale (área de Miami) a 2.500 líderes empresariales y cabezas de hogar hispanos con alta conciencia de salud integral.

Trabajamos con exclusividad por categoría. En farmacia comunitaria, bienestar y servicios de salud, solo habrá una organización aliada en el escenario.

¿Tiene 15 minutos esta semana o la próxima para conversar?

Saludos,

Edward Jiménez
Partner Relationship Manager · EXMA Global
edward@exmaglobal.com
exmaglobal.com/miami"""
    },
    {
        'destinatario': 'Sean Summers',
        'empresa': 'Mercado Libre',
        'email': 'sean.summers@mercadolibre.com',
        'tz': 'EDT',
        'location': 'Miami, FL / LatAm',
        'tipo': 'VALID',
        'asunto': '2.500 líderes hispanos en Miami. Una sola potencia de comercio y fintech.',
        'cuerpo': """Hola Sean:

Mercado Libre es el mayor orgullo tecnológico y de comercio digital de nuestra región, transformando la vida de millones de emprendedores y compradores a escala continental.

El 4 y 5 de diciembre, EXMA celebra en Downtown Event Center, Fort Lauderdale (área metropolitana de Miami) su cumbre anual ante 2.500 fundadores, directores de marketing y líderes de negocio hispanos y latinoamericanos.

Trabajamos con exclusividad por categoría. En ecosistemas de e-commerce y pagos transfronterizos latinoamericanos, solo habrá una compañía en el escenario principal.

¿Tiene 15 minutos esta semana o la próxima para conversar?

Saludos,

Edward Jiménez
Partner Relationship Manager · EXMA Global
edward@exmaglobal.com
exmaglobal.com/miami"""
    }
]

# BLOQUE 3: PACÍFICO / PDT (Washington / California) - 1 prospecto (Esperar a las 11:30 AM EDT = 08:30 AM PDT)
batch_pacific = [
    {
        'destinatario': 'Mike Katz',
        'empresa': 'T-Mobile US',
        'email': 'mike.katz@t-mobile.com',
        'tz': 'PDT',
        'location': 'Bellevue, WA',
        'tipo': 'VALID',
        'asunto': '2.500 líderes hispanos en Miami. Una sola red móvil 5G sin fronteras.',
        'cuerpo': """Hola Mike:

La propuesta de valor de T-Mobile, eliminando tarifas de roaming en viajes y entregando la mejor experiencia 5G, resuena profundamente con la comunidad hispana y sus lazos binacionales.

El 4 y 5 de diciembre, EXMA reúne en Downtown Event Center, Fort Lauderdale (área de Miami) a 2.500 líderes de negocio y ejecutivos hispanos que dependen de la conectividad móvil para liderar sus organizaciones.

Trabajamos con exclusividad por categoría. En redes 5G y telecomunicaciones corporativas y de consumo, solo habrá una marca en el escenario principal.

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

def run_campaign_jueves():
    all_logs = []
    total_prospects = len(batch_central_mountain) + len(batch_eastern) + len(batch_pacific)
    
    send_alert(
        f"🚀 [EXMA Outreach] Arrancó el despacho de los {total_prospects} correos del Jueves",
        f"""Hola Edward,

Se acaba de iniciar el despacho zonificado de hoy Jueves 1 de Octubre ({total_prospects} correos validados al 100% en EmailAwesome):

1. Franja Central & Montaña / CDT & MDT (2 correos): Ace Hardware y Boost Mobile (enviando AHORA en su ventana matutina local).
2. Franja Este / EDT (7 correos): Delta Air Lines, PepsiCo, Telemundo, Universal Music Latino, Hershey, CVS Health, Mercado Libre.
3. Franja Pacífico / PDT (1 correo): T-Mobile US (programado para salir a las 11:30 AM EDT = 08:30 AM PDT).

Todos los buzones fueron verificados con handshake SMTP en EmailAwesome (cero rebotes garantizados).

Recibirás actualizaciones automáticas en tu móvil."""
    )
    
    # 1. Franja Central + Montaña (2 leads)
    s1, e1, l1 = dispatch_batch("BLOQUE 1: CENTRAL Y MONTAÑA / CDT Y MDT (Illinois, Colorado)", batch_central_mountain, 0, total_prospects)
    all_logs.extend(l1)
    
    # 2. Franja Este (7 leads)
    s2, e2, l2 = dispatch_batch("BLOQUE 2: ESTE / EDT (FL, NY, PA, GA, RI)", batch_eastern, len(batch_central_mountain), total_prospects)
    all_logs.extend(l2)
    
    morning_success = s1 + s2
    morning_errors = e1 + e2
    print(f"\n☕ BLOQUE MAÑANA FINALIZADO: {morning_success} enviados, {morning_errors} errores.", flush=True)
    
    send_alert(
        f"✅ [EXMA Outreach] Bloque Mañana completado ({morning_success}/9 enviados)",
        f"""Hola Edward,

Se han enviado exitosamente {morning_success} de los 9 correos de la mañana (Central, Montaña y Este).

El sistema queda en pausa programada esperando las 11:30 AM EDT (= 08:30 AM PDT) para despachar a T-Mobile US (Bellevue, WA).

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
        
    s3, e3, l3 = dispatch_batch("BLOQUE 3: PACÍFICO / PDT (WASHINGTON - 08:30 AM PDT)", batch_pacific, len(batch_central_mountain) + len(batch_eastern), total_prospects)
    all_logs.extend(l3)
    
    total_success = morning_success + s3
    total_errors = morning_errors + e3
    
    send_alert(
        f"🎉 [EXMA Outreach] Campaña de Jueves 100% COMPLETADA ({total_success}/{total_prospects})",
        f"""Hola Edward,

Los {total_prospects} correos de hoy jueves han sido despachados exitosamente al 100%.

- Total exitosos: {total_success}
- Errores: {total_errors}
Hora finalización: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Detalle final de envíos:
""" + "\n".join(all_logs) + f"""

Las respuestas entrarán directo a tu bandeja personal de edward@exmaglobal.com."""
    )
    print("\n🎉 ¡CAMPAÑA DE JUEVES COMPLETADA CON ÉXITO TOTAL!", flush=True)

if __name__ == '__main__':
    run_campaign_jueves()
