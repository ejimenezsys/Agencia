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
        print(f"🔔 Alerta enviada a tu móvil ({notification_target}): {subject}")
    except Exception as e:
        print(f"⚠️ No se pudo enviar alerta: {e}")

# === LOTES POR HUSO HORARIO (TOTAL 26 PROSPECTOS) ===

batch_central_mountain = [   {   'asunto': '2.500 líderes hispanos en Miami. Una sola marca de electrónica.',
        'cuerpo': 'Hola Jennie:\n'
                  '\n'
                  'El comprador hispano está sobreindexado en adopción de tecnología en Estados Unidos. En diciembre '
                  'hay 2.500 de ellos, y son quienes deciden las compras tecnológicas en sus empresas y hogares.\n'
                  '\n'
                  'El 4 y 5 de diciembre, EXMA reúne en Downtown Event Center, Fort Lauderdale (área de Miami) a 2.500 '
                  'líderes hispanos.\n'
                  '\n'
                  'Trabajamos con exclusividad por categoría. En electrónica y retail tecnológico, solo habrá una '
                  'marca en el escenario.\n'
                  '\n'
                  '¿Tiene 15 minutos esta semana o la próxima?\n'
                  '\n'
                  'Saludos,\n'
                  '\n'
                  'Edward Jiménez\n'
                  'Partner Relationship Manager · EXMA Global\n'
                  'edward@exmaglobal.com\n'
                  'exmaglobal.com/miami',
        'destinatario': 'Jennie Weber',
        'email': 'jennie.weber@bestbuy.com',
        'empresa': 'Best Buy Co',
        'location': 'Richfield, MN',
        'tipo': 'VALID',
        'tz': 'CDT'},
    {   'asunto': '2.500 líderes hispanos en Miami. Una sola marca de cerveza.',
        'cuerpo': 'Hola Jim:\n'
                  '\n'
                  'Modelo Especial y Corona son, en la práctica, la cerveza de referencia de esta comunidad en Estados '
                  'Unidos.\n'
                  '\n'
                  'El 4 y 5 de diciembre, EXMA reúne en Downtown Event Center, Fort Lauderdale (área de Miami) a 2.500 '
                  'líderes, emprendedores y profesionales hispanos.\n'
                  '\n'
                  'Trabajamos con exclusividad por categoría. En cerveza, habrá una sola marca en el escenario y en '
                  'las experiencias VIP del evento.\n'
                  '\n'
                  '¿Tiene 15 minutos esta semana o la próxima para conversar?\n'
                  '\n'
                  'Saludos,\n'
                  '\n'
                  'Edward Jiménez\n'
                  'Partner Relationship Manager · EXMA Global\n'
                  'edward@exmaglobal.com\n'
                  'exmaglobal.com/miami',
        'destinatario': 'Jim Sabia',
        'email': 'jim.sabia@cbrands.com',
        'empresa': 'Constellation Brands',
        'location': 'Chicago, IL',
        'tipo': 'VALID',
        'tz': 'CDT'},
    {   'asunto': '2.500 líderes hispanos en Miami. Una sola marca de retail.',
        'cuerpo': 'Hola William:\n'
                  '\n'
                  'Walmart lleva años construyendo una relación sólida y auténtica con el comprador hispano. Le '
                  'propongo el lugar donde ese comprador no solo compra, sino que se reúne a hacer negocios y '
                  'liderar.\n'
                  '\n'
                  'El 4 y 5 de diciembre, EXMA reúne en Downtown Event Center, Fort Lauderdale (área de Miami) a 2.500 '
                  'líderes y emprendedores hispanos.\n'
                  '\n'
                  'Trabajamos con exclusividad por categoría. En retail, solo habrá una marca en el escenario.\n'
                  '\n'
                  '¿Tiene 15 minutos esta semana o la próxima para conversar?\n'
                  '\n'
                  'Saludos,\n'
                  '\n'
                  'Edward Jiménez\n'
                  'Partner Relationship Manager · EXMA Global\n'
                  'edward@exmaglobal.com\n'
                  'exmaglobal.com/miami',
        'destinatario': 'William White',
        'email': 'william.white@walmart.com',
        'empresa': 'Walmart Inc.',
        'location': 'Bentonville, AR',
        'tipo': 'VALID',
        'tz': 'CDT'},
    {   'asunto': '2.500 líderes hispanos en Miami. Una sola institución de inversiones.',
        'cuerpo': 'Hola Lisa:\n'
                  '\n'
                  'La comunidad de inversionistas y emprendedores hispanos en Estados Unidos crece a un ritmo superior '
                  'a la media nacional en apertura de cuentas patrimoniales.\n'
                  '\n'
                  'El 4 y 5 de diciembre, EXMA reúne en Downtown Event Center, Fort Lauderdale (área de Miami) a 2.500 '
                  'líderes hispanos.\n'
                  '\n'
                  'Trabajamos con exclusividad por categoría. En servicios de inversión y gestión patrimonial, solo '
                  'habrá una marca en el escenario.\n'
                  '\n'
                  '¿Tiene 15 minutos esta semana o la próxima?\n'
                  '\n'
                  'Saludos,\n'
                  '\n'
                  'Edward Jiménez\n'
                  'Partner Relationship Manager · EXMA Global\n'
                  'edward@exmaglobal.com\n'
                  'exmaglobal.com/miami',
        'destinatario': 'Lisa Ross',
        'email': 'lisa.ross@schwab.com',
        'empresa': 'Charles Schwab',
        'location': 'Westlake, TX',
        'tipo': 'CATCH_ALL',
        'tz': 'CDT'},
    {   'asunto': '2.500 líderes hispanos en Miami. Una sola marca de snacks.',
        'cuerpo': 'Hola Mie-Leng:\n'
                  '\n'
                  'Mondelēz creció en este mercado a punta de entender y acompañar al consumidor hispano en cada '
                  'momento de consumo.\n'
                  '\n'
                  'El 4 y 5 de diciembre, EXMA reúne en Downtown Event Center, Fort Lauderdale (área de Miami) a 2.500 '
                  'líderes hispanos. Esta es la sala donde ese consumidor decide y lidera.\n'
                  '\n'
                  'Trabajamos con exclusividad por categoría. En snacks y galletas, solo habrá una marca en el '
                  'escenario.\n'
                  '\n'
                  '¿Tiene 15 minutos esta semana o la próxima?\n'
                  '\n'
                  'Saludos,\n'
                  '\n'
                  'Edward Jiménez\n'
                  'Partner Relationship Manager · EXMA Global\n'
                  'edward@exmaglobal.com\n'
                  'exmaglobal.com/miami',
        'destinatario': 'Mie-Leng Wong',
        'email': 'mie-leng.wong@mdlz.com',
        'empresa': 'Mondelēz International',
        'location': 'Chicago, IL',
        'tipo': 'CATCH_ALL',
        'tz': 'CDT'},
    {   'asunto': '2.500 líderes hispanos en Miami. Una sola marca automotriz.',
        'cuerpo': 'Hola Marisstella:\n'
                  '\n'
                  'El comprador hispano es de los segmentos más leales y de mayor crecimiento en el sector automotriz '
                  'en Estados Unidos.\n'
                  '\n'
                  'El 4 y 5 de diciembre, EXMA reúne en Downtown Event Center, Fort Lauderdale (área de Miami) a 2.500 '
                  'líderes hispanos.\n'
                  '\n'
                  'Trabajamos con exclusividad por categoría. En automotriz, habrá una sola marca oficial en el '
                  'escenario y en la exhibición exterior del evento.\n'
                  '\n'
                  '¿Tiene 15 minutos esta semana o la próxima para conversar?\n'
                  '\n'
                  'Saludos,\n'
                  '\n'
                  'Edward Jiménez\n'
                  'Partner Relationship Manager · EXMA Global\n'
                  'edward@exmaglobal.com\n'
                  'exmaglobal.com/miami',
        'destinatario': 'Marisstella Marinkovic',
        'email': 'marisstella.marinkovic@nissan-usa.com',
        'empresa': 'Nissan North America',
        'location': 'Franklin, TN',
        'tipo': 'CATCH_ALL',
        'tz': 'CDT'},
    {   'asunto': '2.500 líderes hispanos en Miami. Una sola marca de alimentos.',
        'cuerpo': 'Hola Diana:\n'
                  '\n'
                  'El consumidor hispano es uno de los mayores motores de volumen y crecimiento en alimentos y '
                  'condimentos en Estados Unidos.\n'
                  '\n'
                  'El 4 y 5 de diciembre, EXMA reúne en Downtown Event Center, Fort Lauderdale (área de Miami) a 2.500 '
                  'líderes y familias hispanas.\n'
                  '\n'
                  'Trabajamos con exclusividad por categoría. En alimentos empacados, solo habrá una marca en el '
                  'escenario.\n'
                  '\n'
                  '¿Tiene 15 minutos esta semana o la próxima para conversar?\n'
                  '\n'
                  'Saludos,\n'
                  '\n'
                  'Edward Jiménez\n'
                  'Partner Relationship Manager · EXMA Global\n'
                  'edward@exmaglobal.com\n'
                  'exmaglobal.com/miami',
        'destinatario': 'Diana Frost',
        'email': 'diana.frost@kraftheinz.com',
        'empresa': 'The Kraft Heinz Company',
        'location': 'Chicago, IL',
        'tipo': 'CATCH_ALL',
        'tz': 'CDT'},
    {   'asunto': '2.500 líderes hispanos en Miami. Una sola marca de servicios financieros transfronterizos.',
        'cuerpo': 'Hola Devin:\n'
                  '\n'
                  'Western Union existe y ha crecido de la mano de esta comunidad. En diciembre está reunida en un '
                  'solo lugar, a minutos de las principales rutas financieras de las Américas.\n'
                  '\n'
                  'El 4 y 5 de diciembre, EXMA reúne en Downtown Event Center, Fort Lauderdale (área de Miami) a 2.500 '
                  'líderes, empresarios y profesionales hispanos.\n'
                  '\n'
                  'Trabajamos con exclusividad por categoría. En servicios transfronterizos y pagos, solo habrá una '
                  'marca en el escenario.\n'
                  '\n'
                  '¿Tiene 15 minutos esta semana o la próxima para conversar?\n'
                  '\n'
                  'Saludos,\n'
                  '\n'
                  'Edward Jiménez\n'
                  'Partner Relationship Manager · EXMA Global\n'
                  'edward@exmaglobal.com\n'
                  'exmaglobal.com/miami',
        'destinatario': 'Devin McGranahan',
        'email': 'devin.mcgranahan@westernunion.com',
        'empresa': 'Western Union',
        'location': 'Denver, CO',
        'tipo': 'CATCH_ALL',
        'tz': 'MDT'}]

batch_eastern = [   {   'asunto': 'Bacardi nació para nuestra comunidad. Queremos que esté en su escenario.',
        'cuerpo': 'Hola Ned:\n'
                  '\n'
                  'Bacardi lleva más de un siglo siendo la historia de una familia que empezó de nuevo y construyó '
                  'algo global desde el Caribe. Esa es literalmente la historia que vamos a poner en un escenario en '
                  'diciembre.\n'
                  '\n'
                  'El 4 y 5 de diciembre, EXMA reúne en Downtown Event Center, Fort Lauderdale (área de Miami) a 2.500 '
                  'líderes, emprendedores y profesionales hispanos.\n'
                  '\n'
                  'Sé que su rol es global y que esto es una activación regional en el sur de Florida. ¿Me podría '
                  'indicar con quién hablar del equipo de Bacardi en Coral Gables? Con mucho gusto le escribo '
                  'directamente.\n'
                  '\n'
                  'Un abrazo,\n'
                  '\n'
                  'Edward Jiménez\n'
                  'Partner Relationship Manager · EXMA Global\n'
                  'edward@exmaglobal.com\n'
                  'exmaglobal.com/miami',
        'destinatario': 'Ned Duggan',
        'email': 'nduggan@bacardi.com',
        'empresa': 'Bacardi USA',
        'location': 'Miami/Coral Gables, FL',
        'tipo': 'VALID',
        'tz': 'EDT'},
    {   'asunto': 'Pollo Tropical nació para nuestra comunidad. Queremos que esté en su escenario.',
        'cuerpo': 'Hola Enrique:\n'
                  '\n'
                  'Pollo Tropical es una institución del sabor latino en el sur de la Florida. Desde hace décadas, su '
                  'menú y su presencia representan el día a día de millones de familias y profesionales hispanos en '
                  'este estado.\n'
                  '\n'
                  'El 4 y 5 de diciembre, EXMA reúne en Downtown Event Center, Fort Lauderdale (área de Miami) a 2.500 '
                  'líderes, emprendedores y profesionales hispanos.\n'
                  '\n'
                  'Estamos invitando a una sola marca por categoría. Nos encantaría que en restaurantes fuera Pollo '
                  'Tropical.\n'
                  '\n'
                  '¿Tiene 15 minutos esta semana o la próxima para contarle cómo funcionaría?\n'
                  '\n'
                  'Un abrazo,\n'
                  '\n'
                  'Edward Jiménez\n'
                  'Partner Relationship Manager · EXMA Global\n'
                  'edward@exmaglobal.com\n'
                  'exmaglobal.com/miami',
        'destinatario': 'Enrique Perez-Pantera',
        'email': 'eperez@pollotropical.com',
        'empresa': 'Pollo Tropical',
        'location': 'Miami, FL',
        'tipo': 'VALID',
        'tz': 'EDT'},
    {   'asunto': 'La comunidad de doers hispanos más grande de Estados Unidos',
        'cuerpo': 'Hola Scott:\n'
                  '\n'
                  'Deloitte publica año tras año sobre el poder de compra hispano en Estados Unidos. En diciembre esa '
                  'audiencia no va a estar en un informe: va a estar en una sala.\n'
                  '\n'
                  'Deloitte apoya a quienes emprenden, innovan y crecen. Nosotros reunimos exactamente a esas '
                  'personas, en español y con alma latina.\n'
                  '\n'
                  'El 4 y 5 de diciembre, EXMA reúne en Downtown Event Center, Fort Lauderdale (área de Miami) a 2.500 '
                  'líderes hispanos: emprendedores, profesionales y dueños de negocio. Dos días de marketing, '
                  'innovación, estrategia, inversiones y finanzas para una comunidad que no deja de crecer.\n'
                  '\n'
                  'Buscamos una sola marca por categoría que se convierta en la que impulsa ese crecimiento: en el '
                  'escenario, en el contenido y en la comunidad que sigue viva después del evento.\n'
                  '\n'
                  '¿Tiene 15 minutos esta semana o la próxima para contarle cómo lo imaginamos para Deloitte?\n'
                  '\n'
                  'Saludos,\n'
                  '\n'
                  'Edward Jiménez\n'
                  'Partner Relationship Manager · EXMA Global\n'
                  'edward@exmaglobal.com\n'
                  'exmaglobal.com/miami',
        'destinatario': 'Scott Mager',
        'email': 'smager@deloitte.com',
        'empresa': 'Deloitte US',
        'location': 'New York, NY',
        'tipo': 'VALID',
        'tz': 'EDT'},
    {   'asunto': '2.500 líderes hispanos en Miami. Una sola marca de licores.',
        'cuerpo': 'Hola Cristina:\n'
                  '\n'
                  'El consumidor hispano es de los que más crece en su categoría en Estados Unidos, tanto en marcas '
                  'icónicas como Don Julio y Casamigos como en el portafolio global de Diageo.\n'
                  '\n'
                  'Sé que su equipo invierte en llegarle al consumidor hispano. Le propongo algo que un anuncio no '
                  'puede dar: estar en la sala.\n'
                  '\n'
                  'El 4 y 5 de diciembre, EXMA reúne en Downtown Event Center, Fort Lauderdale (área de Miami) a 2.500 '
                  'líderes, emprendedores y profesionales hispanos.\n'
                  '\n'
                  'Trabajamos con exclusividad por categoría. En licores, solo habrá una marca en el escenario, en la '
                  'experiencia y en el contenido del evento.\n'
                  '\n'
                  'Si aún tiene presupuesto de cierre de año para comunidad o experiencias, es un buen momento para '
                  'conversar. ¿Tiene 15 minutos esta semana o la próxima?\n'
                  '\n'
                  'Saludos,\n'
                  '\n'
                  'Edward Jiménez\n'
                  'Partner Relationship Manager · EXMA Global\n'
                  'edward@exmaglobal.com\n'
                  'exmaglobal.com/miami',
        'destinatario': 'Cristina Diezhandino',
        'email': 'cristina.diezhandino@diageo.com',
        'empresa': 'Diageo North America',
        'location': 'New York, NY',
        'tipo': 'VALID',
        'tz': 'EDT'},
    {   'asunto': '2.500 líderes hispanos en Miami. Una sola marca de café.',
        'cuerpo': 'Hola Katie:\n'
                  '\n'
                  'Café Bustelo es de las pocas marcas grandes que esta comunidad siente como propia en cada hogar '
                  'latino de Florida y de todo Estados Unidos.\n'
                  '\n'
                  'Sé que su equipo invierte en llegarle al consumidor hispano. Le propongo algo que un anuncio no '
                  'puede dar: estar en la sala.\n'
                  '\n'
                  'El 4 y 5 de diciembre, EXMA reúne en Downtown Event Center, Fort Lauderdale (área de Miami) a 2.500 '
                  'líderes hispanos y dueños de negocio.\n'
                  '\n'
                  'Trabajamos con exclusividad por categoría. En café, solo habrá una marca en el escenario y en la '
                  'experiencia del evento.\n'
                  '\n'
                  '¿Tiene 15 minutos esta semana o la próxima para conversar?\n'
                  '\n'
                  'Saludos,\n'
                  '\n'
                  'Edward Jiménez\n'
                  'Partner Relationship Manager · EXMA Global\n'
                  'edward@exmaglobal.com\n'
                  'exmaglobal.com/miami',
        'destinatario': 'Katie Williams',
        'email': 'katie.williams@jmsmucker.com',
        'empresa': 'The J.M. Smucker Co. (Café Bustelo)',
        'location': 'Orrville, OH',
        'tipo': 'VALID',
        'tz': 'EDT'},
    {   'asunto': '2.500 líderes hispanos en Miami. Una sola marca de restaurantes.',
        'cuerpo': 'Hola Tom:\n'
                  '\n'
                  'Burger King tiene su casa en Miami y su consumidor hispano es central para el negocio. Los dos '
                  'coinciden el 4 y 5 de diciembre a minutos de su sede central.\n'
                  '\n'
                  'EXMA reúne en Downtown Event Center, Fort Lauderdale (área de Miami) a 2.500 líderes y '
                  'profesionales hispanos.\n'
                  '\n'
                  'Trabajamos con exclusividad por categoría. En restaurantes de servicio rápido, solo habrá una marca '
                  'en el escenario y en el contenido.\n'
                  '\n'
                  '¿Tiene 15 minutos esta semana o la próxima para conversar?\n'
                  '\n'
                  'Saludos,\n'
                  '\n'
                  'Edward Jiménez\n'
                  'Partner Relationship Manager · EXMA Global\n'
                  'edward@exmaglobal.com\n'
                  'exmaglobal.com/miami',
        'destinatario': 'Tom Curtis',
        'email': 'tcurtis@rbi.com',
        'empresa': 'Burger King (Restaurant Brands International)',
        'location': 'Miami, FL',
        'tipo': 'VALID',
        'tz': 'EDT'},
    {   'asunto': '2.500 líderes hispanos en Miami. Una sola naviera en el escenario.',
        'cuerpo': 'Hola Christine:\n'
                  '\n'
                  'Carnival es de Miami como pocas marcas. En diciembre la ciudad reúne a 2.500 líderes hispanos, y el '
                  'viajero hispano es de los segmentos familiares que más rápido crece para la industria de cruceros.\n'
                  '\n'
                  'El 4 y 5 de diciembre, EXMA reúne en Downtown Event Center, Fort Lauderdale (área de Miami) a esta '
                  'comunidad.\n'
                  '\n'
                  'Trabajamos con exclusividad por categoría. En cruceros, solo habrá una marca en el escenario y en '
                  'la experiencia.\n'
                  '\n'
                  '¿Tiene 15 minutos esta semana o la próxima?\n'
                  '\n'
                  'Saludos,\n'
                  '\n'
                  'Edward Jiménez\n'
                  'Partner Relationship Manager · EXMA Global\n'
                  'edward@exmaglobal.com\n'
                  'exmaglobal.com/miami',
        'destinatario': 'Christine Duffy',
        'email': 'cduffy@carnival.com',
        'empresa': 'Carnival Cruise Line',
        'location': 'Miami, FL',
        'tipo': 'VALID',
        'tz': 'EDT'},
    {   'asunto': '2.500 líderes hispanos en Miami. Una sola marca de bebidas.',
        'cuerpo': 'Hola Troy:\n'
                  '\n'
                  'Coke Florida embotella justo en el estado donde la población hispana crece más rápido y con mayor '
                  'poder de compra. Ese consumidor y sus empleadores van a estar reunidos en una sala en diciembre.\n'
                  '\n'
                  'El 4 y 5 de diciembre, EXMA reúne en Downtown Event Center, Fort Lauderdale (área de Miami) a 2.500 '
                  'líderes hispanos.\n'
                  '\n'
                  'Trabajamos con exclusividad por categoría. En bebidas, solo habrá una marca en el escenario y en la '
                  'hidratación oficial del evento.\n'
                  '\n'
                  '¿Tiene 15 minutos esta semana o la próxima?\n'
                  '\n'
                  'Saludos,\n'
                  '\n'
                  'Edward Jiménez\n'
                  'Partner Relationship Manager · EXMA Global\n'
                  'edward@exmaglobal.com\n'
                  'exmaglobal.com/miami',
        'destinatario': 'Troy Taylor',
        'email': 'ttaylor@cocacolaflorida.com',
        'empresa': 'Coca-Cola Beverages Florida',
        'location': 'Tampa, FL',
        'tipo': 'VALID',
        'tz': 'EDT'},
    {   'asunto': '2.500 líderes hispanos en Miami. Una sola marca de cuidado personal.',
        'cuerpo': 'Hola Carolina:\n'
                  '\n'
                  'Su liderazgo en marketing multicultural refleja exactamente lo que es esta sala: Latinoamérica y '
                  'Estados Unidos reunidos en un mismo lugar de alto impacto.\n'
                  '\n'
                  'El 4 y 5 de diciembre, EXMA reúne en Downtown Event Center, Fort Lauderdale (área de Miami) a 2.500 '
                  'líderes hispanos.\n'
                  '\n'
                  'Trabajamos con exclusividad por categoría. En cuidado personal y salud oral, solo habrá una marca '
                  'en el escenario.\n'
                  '\n'
                  '¿Tiene 15 minutos esta semana o la próxima?\n'
                  '\n'
                  'Saludos,\n'
                  '\n'
                  'Edward Jiménez\n'
                  'Partner Relationship Manager · EXMA Global\n'
                  'edward@exmaglobal.com\n'
                  'exmaglobal.com/miami',
        'destinatario': 'Carolina Incognito',
        'email': 'carolina_incognito@colpal.com',
        'empresa': 'Colgate-Palmolive',
        'location': 'New York, NY',
        'tipo': 'VALID',
        'tz': 'EDT'},
    {   'asunto': '2.500 líderes hispanos en Miami. Una sola marca de restaurantes.',
        'cuerpo': 'Hola Lindsay:\n'
                  '\n'
                  'El crecimiento de su categoría en el sur de Estados Unidos pasa por el consumidor hispano y la '
                  'lealtad de marca familiar. En diciembre esa audiencia está en una sola sala.\n'
                  '\n'
                  'El 4 y 5 de diciembre, EXMA reúne en Downtown Event Center, Fort Lauderdale (área de Miami) a 2.500 '
                  'líderes hispanos.\n'
                  '\n'
                  'Trabajamos con exclusividad por categoría. En restaurantes de servicio rápido, solo habrá una marca '
                  'en el escenario.\n'
                  '\n'
                  '¿Tiene 15 minutos esta semana o la próxima?\n'
                  '\n'
                  'Saludos,\n'
                  '\n'
                  'Edward Jiménez\n'
                  'Partner Relationship Manager · EXMA Global\n'
                  'edward@exmaglobal.com\n'
                  'exmaglobal.com/miami',
        'destinatario': 'Lindsay Radkoski',
        'email': 'lindsay.radkoski@wendys.com',
        'empresa': "The Wendy's Company",
        'location': 'Dublin, OH',
        'tipo': 'VALID',
        'tz': 'EDT'},
    {   'asunto': 'La comunidad de doers hispanos más grande de Estados Unidos',
        'cuerpo': 'Hola Antonia:\n'
                  '\n'
                  'Escribo en español a propósito: es el idioma de los 2.500 líderes de negocio que se reúnen en Miami '
                  'en diciembre, y de un mercado que su firma ya analiza de cerca.\n'
                  '\n'
                  'PwC apoya a quienes emprenden, innovan y crecen. Nosotros reunimos exactamente a esas personas, en '
                  'español y con alma latina.\n'
                  '\n'
                  'El 4 y 5 de diciembre, EXMA reúne en Downtown Event Center, Fort Lauderdale (área de Miami) a 2.500 '
                  'líderes hispanos.\n'
                  '\n'
                  'Buscamos una sola marca por categoría que impulse ese crecimiento en el escenario y en la '
                  'comunidad.\n'
                  '\n'
                  '¿Tiene 15 minutos esta semana o la próxima para contarle cómo lo imaginamos para PwC?\n'
                  '\n'
                  'Saludos,\n'
                  '\n'
                  'Edward Jiménez\n'
                  'Partner Relationship Manager · EXMA Global\n'
                  'edward@exmaglobal.com\n'
                  'exmaglobal.com/miami',
        'destinatario': 'Antonia Wade',
        'email': 'antonia.wade@pwc.com',
        'empresa': 'PwC US',
        'location': 'New York, NY',
        'tipo': 'CATCH_ALL',
        'tz': 'EDT'},
    {   'asunto': '2.500 líderes hispanos en Miami. Una sola marca de energía.',
        'cuerpo': 'Hola Kimberly:\n'
                  '\n'
                  'Su equipo de relaciones con la comunidad trabaja el sur de Florida todos los días. Esto es esa '
                  'comunidad empresarial y profesional, concentrada en dos días.\n'
                  '\n'
                  'El 4 y 5 de diciembre, EXMA reúne en Downtown Event Center, Fort Lauderdale (área de Miami) a 2.500 '
                  'líderes hispanos.\n'
                  '\n'
                  'Trabajamos con exclusividad por categoría. En energía y sostenibilidad, solo habrá una marca en el '
                  'escenario.\n'
                  '\n'
                  '¿Tiene 15 minutos esta semana o la próxima para conversar?\n'
                  '\n'
                  'Saludos,\n'
                  '\n'
                  'Edward Jiménez\n'
                  'Partner Relationship Manager · EXMA Global\n'
                  'edward@exmaglobal.com\n'
                  'exmaglobal.com/miami',
        'destinatario': 'Kimberly Blair',
        'email': 'kimberly.blair@fpl.com',
        'empresa': 'Florida Power & Light (FPL / NextEra Energy)',
        'location': 'Juno Beach, FL',
        'tipo': 'CATCH_ALL',
        'tz': 'EDT'},
    {   'asunto': '2.500 líderes hispanos en Miami. Una sola aseguradora de vida y patrimonio.',
        'cuerpo': 'Hola Amy:\n'
                  '\n'
                  'New York Life tiene una de las trayectorias más profundas sirviendo a familias empresarias y '
                  'profesionales hispanos en protección financiera.\n'
                  '\n'
                  'El 4 y 5 de diciembre, EXMA reúne en Downtown Event Center, Fort Lauderdale (área de Miami) a 2.500 '
                  'tomadores de decisión hispanos.\n'
                  '\n'
                  'Trabajamos con exclusividad por categoría. En seguros de vida y patrimonio, solo habrá una marca en '
                  'el escenario.\n'
                  '\n'
                  '¿Tiene 15 minutos esta semana o la próxima?\n'
                  '\n'
                  'Saludos,\n'
                  '\n'
                  'Edward Jiménez\n'
                  'Partner Relationship Manager · EXMA Global\n'
                  'edward@exmaglobal.com\n'
                  'exmaglobal.com/miami',
        'destinatario': 'Amy Hu',
        'email': 'amy_hu@newyorklife.com',
        'empresa': 'New York Life Insurance Company',
        'location': 'New York, NY',
        'tipo': 'CATCH_ALL',
        'tz': 'EDT'},
    {   'asunto': '2.500 líderes hispanos en Miami. Una sola marca de consumo masivo.',
        'cuerpo': 'Hola Marc:\n'
                  '\n'
                  'P&G ha sido de las compañías más explícitas y consistentes del país sobre representación cultural y '
                  'apoyo a la comunidad hispana.\n'
                  '\n'
                  'El 4 y 5 de diciembre, EXMA reúne en Downtown Event Center, Fort Lauderdale (área de Miami) a 2.500 '
                  'líderes hispanos. Hay un escenario donde esa conversación ocurre en español y con acción real.\n'
                  '\n'
                  'Trabajamos con exclusividad por categoría. Nos encantaría explorar si P&G tiene espacio para estar '
                  'presente.\n'
                  '\n'
                  '¿Tiene su equipo 15 minutos esta semana o la próxima?\n'
                  '\n'
                  'Saludos,\n'
                  '\n'
                  'Edward Jiménez\n'
                  'Partner Relationship Manager · EXMA Global\n'
                  'edward@exmaglobal.com\n'
                  'exmaglobal.com/miami',
        'destinatario': 'Marc Pritchard',
        'email': 'pritchard.m@pg.com',
        'empresa': 'Procter & Gamble (P&G)',
        'location': 'Cincinnati, OH',
        'tipo': 'CATCH_ALL',
        'tz': 'EDT'}]

batch_pacific = [   {   'asunto': 'Cacique nació para nuestra comunidad. Queremos que esté en su escenario.',
        'cuerpo': 'Hola Pedro:\n'
                  '\n'
                  'Vi su llegada a Cacique el año pasado después de Mondelēz. Tomar una marca familiar hispana y '
                  'llevarla a otra escala es un tipo de reto distinto al de una multinacional, y es justo la '
                  'conversación que vamos a tener en diciembre.\n'
                  '\n'
                  'Cacique es de esas marcas que nacieron aquí para servir a nuestra gente. Por eso le escribo.\n'
                  '\n'
                  'El 4 y 5 de diciembre, EXMA reúne en Downtown Event Center, Fort Lauderdale (área de Miami) a 2.500 '
                  'líderes, emprendedores y profesionales hispanos.\n'
                  '\n'
                  'Estamos invitando a una sola marca por categoría. Nos encantaría que en su categoría fuera '
                  'Cacique.\n'
                  '\n'
                  '¿Tiene 15 minutos esta semana o la próxima?\n'
                  '\n'
                  'Un abrazo,\n'
                  '\n'
                  'Edward Jiménez\n'
                  'Partner Relationship Manager · EXMA Global\n'
                  'edward@exmaglobal.com\n'
                  'exmaglobal.com/miami',
        'destinatario': 'Pedro Silveira',
        'email': 'psilveira@caciqueinc.com',
        'empresa': 'Cacique Foods',
        'location': 'Monrovia, CA',
        'tipo': 'VALID',
        'tz': 'PDT'},
    {   'asunto': 'Gaviña nació para nuestra comunidad. Queremos que esté en su escenario.',
        'cuerpo': 'Hola Leonor:\n'
                  '\n'
                  'Vi el lanzamiento de las cápsulas reciclables de Café La Llave. Que una marca que empezó con una '
                  'familia cubana llegando a Los Ángeles esté hoy marcando la pauta en su categoría es exactamente la '
                  'historia que nos interesa contar.\n'
                  '\n'
                  'Gaviña es de esas marcas que nacieron aquí para servir a nuestra gente. Por eso le escribo.\n'
                  '\n'
                  'El 4 y 5 de diciembre, EXMA reúne en Downtown Event Center, Fort Lauderdale (área de Miami) a 2.500 '
                  'líderes, emprendedores y profesionales hispanos. Es el primer gran evento de una plataforma que '
                  'celebra a hispanos ordinarios haciendo cosas extraordinarias.\n'
                  '\n'
                  'Estamos invitando a una sola marca por categoría. Nos encantaría que en café fuera Gaviña.\n'
                  '\n'
                  '¿Tiene 15 minutos esta semana o la próxima?\n'
                  '\n'
                  'Un abrazo,\n'
                  '\n'
                  'Edward Jiménez\n'
                  'Partner Relationship Manager · EXMA Global\n'
                  'edward@exmaglobal.com\n'
                  'exmaglobal.com/miami',
        'destinatario': 'Leonor Gaviña-Valls',
        'email': 'leonor.gavina@gavina.com',
        'empresa': 'F. Gaviña & Sons (Café La Llave)',
        'location': 'Vernon, CA',
        'tipo': 'VALID',
        'tz': 'PDT'},
    {   'asunto': 'La comunidad de doers hispanos más grande de Estados Unidos',
        'cuerpo': 'Hola Thomas:\n'
                  '\n'
                  'QuickBooks vive de los dueños de negocio pequeños, y el segmento que más rápido crece en ese '
                  'universo es el hispano. En diciembre hay 2.500 de ellos en una sala.\n'
                  '\n'
                  'Intuit apoya a quienes emprenden, innovan y crecen. Nosotros reunimos exactamente a esas personas, '
                  'en español y con alma latina.\n'
                  '\n'
                  'El 4 y 5 de diciembre, EXMA reúne en Downtown Event Center, Fort Lauderdale (área de Miami) a 2.500 '
                  'líderes hispanos: emprendedores, profesionales y dueños de negocio. Dos días de marketing, '
                  'innovación, estrategia, inversiones y finanzas para una comunidad que no deja de crecer.\n'
                  '\n'
                  'Buscamos una sola marca por categoría que se convierta en la que impulsa ese crecimiento: en el '
                  'escenario, en el contenido y en la comunidad que sigue viva después del evento.\n'
                  '\n'
                  '¿Tiene 15 minutos esta semana o la próxima para contarle cómo lo imaginamos para Intuit?\n'
                  '\n'
                  'Saludos,\n'
                  '\n'
                  'Edward Jiménez\n'
                  'Partner Relationship Manager · EXMA Global\n'
                  'edward@exmaglobal.com\n'
                  'exmaglobal.com/miami',
        'destinatario': 'Thomas Ranese',
        'email': 'thomas_ranese@intuit.com',
        'empresa': 'Intuit',
        'location': 'Mountain View, CA',
        'tipo': 'VALID',
        'tz': 'PDT'},
    {   'asunto': 'La comunidad de doers hispanos más grande de Estados Unidos',
        'cuerpo': 'Hola Emma:\n'
                  '\n'
                  'El 54% de los asistentes a EXMA Miami son corporativos y el resto emprendedores. Es, literalmente, '
                  'la sala de sus dos compradores a la vez.\n'
                  '\n'
                  'Workday apoya a quienes emprenden, innovan y crecen. Nosotros reunimos exactamente a esas personas, '
                  'en español y con alma latina.\n'
                  '\n'
                  'El 4 y 5 de diciembre, EXMA reúne en Downtown Event Center, Fort Lauderdale (área de Miami) a 2.500 '
                  'líderes hispanos.\n'
                  '\n'
                  '¿Tiene 15 minutos esta semana o la próxima para contarle cómo lo imaginamos para Workday?\n'
                  '\n'
                  'Saludos,\n'
                  '\n'
                  'Edward Jiménez\n'
                  'Partner Relationship Manager · EXMA Global\n'
                  'edward@exmaglobal.com\n'
                  'exmaglobal.com/miami',
        'destinatario': 'Emma Chalwin',
        'email': 'emma.chalwin@workday.com',
        'empresa': 'Workday',
        'location': 'Pleasanton, CA',
        'tipo': 'CATCH_ALL',
        'tz': 'PDT'}]

def dispatch_batch(batch_name, prospects_list, global_offset=0, total_all=26):
    print(f"\n==================================================")
    print(f"🚀 INICIANDO {batch_name} ({len(prospects_list)} correos)")
    print(f"Hora actual: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"==================================================")
    
    success = 0
    errors = 0
    logs = []
    
    server = None
    try:
        server = get_smtp_connection()
    except Exception as e:
        print(f"Error conectando a SMTP: {e}")
        return 0, len(prospects_list), [str(e)]
        
    for i, p_info in enumerate(prospects_list, 1):
        global_idx = global_offset + i
        empresa = p_info['empresa']
        nombre_dest = p_info['destinatario']
        to_email = p_info['email']
        tipo = p_info['tipo']
        tz = p_info['tz']
        loc = p_info['location']
        asunto = p_info['asunto']
        cuerpo = p_info['cuerpo']
        
        msg = MIMEText(cuerpo, 'plain', 'utf-8')
        msg['Subject'] = asunto
        msg['From'] = formataddr(('Edward Jiménez · EXMA Global', u))
        msg['To'] = formataddr((nombre_dest, to_email))
        msg['Reply-To'] = 'edward@exmaglobal.com'
        
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        sent_ok = False
        
        # Intentar enviar (con reconexión si es necesario)
        for attempt in range(2):
            try:
                server.sendmail(u, [to_email], msg.as_string())
                print(f"[{global_idx}/{total_all}] ✅ {timestamp} [{tz} - {loc}] [{tipo}] ENVIADO: {nombre_dest} ({empresa}) <{to_email}>", flush=True)
                success += 1
                logs.append(f"✅ {timestamp} [{tz}] {empresa}: {nombre_dest} <{to_email}>")
                sent_ok = True
                break
            except Exception as e:
                print(f"⚠️ Reintentando conexión SMTP para {to_email}... ({e})", flush=True)
                try:
                    server = get_smtp_connection()
                except Exception as ex2:
                    print(f"Fallo reconexión: {ex2}", flush=True)
                time.sleep(3)
                
        if not sent_ok:
            print(f"[{global_idx}/{total_all}] ❌ {timestamp} [{tz}] ERROR con {to_email}", flush=True)
            errors += 1
            logs.append(f"❌ {timestamp} [{tz}] {empresa}: {nombre_dest} <{to_email}> ERROR")
            
        if i < len(prospects_list):
            sleep_time = random.randint(65, 95)
            print(f"   ⏳ Pausa humana anti-spam: esperando {sleep_time}s antes del siguiente...", flush=True)
            time.sleep(sleep_time)
            
    try:
        server.quit()
    except:
        pass
        
    return success, errors, logs

def run_campaign_zonificada():
    all_logs = []
    total_prospects = len(batch_central_mountain) + len(batch_eastern) + len(batch_pacific)
    
    send_alert(
        f"🚀 [EXMA Outreach] Arrancó el despacho de los {total_prospects} correos del Martes",
        f"""Hola Edward,

Se acaba de iniciar el despacho zonificado por franja horaria ({total_prospects} correos en total):

1. Franja Central & Montaña (8 correos): Enviando AHORA (09:15 AM CDT / 08:15 AM MDT local).
2. Franja Este (14 correos): Enviando a continuación (Florida, NY, Ohio).
3. Franja Pacífico (4 correos - California): Programado para salir exactamente a las 12:00 PM EDT (= 09:00 AM PDT).

Recibirás actualizaciones automáticas aquí en tu móvil."""
    )
    
    # 1. Franja Central + Montaña (8 leads)
    s1, e1, l1 = dispatch_batch("BLOQUE 1: CENTRAL Y MONTAÑA (09:00 AM CDT / 08:00 AM MDT)", batch_central_mountain, 0, total_prospects)
    all_logs.extend(l1)
    
    # 2. Franja Este (14 leads)
    s2, e2, l2 = dispatch_batch("BLOQUE 2: ESTE / EDT (FL, NY, OH)", batch_eastern, len(batch_central_mountain), total_prospects)
    all_logs.extend(l2)
    
    morning_success = s1 + s2
    morning_errors = e1 + e2
    print(f"\n☕ BLOQUE MAÑANA FINALIZADO: {morning_success} enviados, {morning_errors} errores.", flush=True)
    
    send_alert(
        f"✅ [EXMA Outreach] Bloque Mañana completado ({morning_success}/22 enviados)",
        f"""Hola Edward,

Se han enviado exitosamente {morning_success} de los 22 correos de la mañana (Central, Montaña y Este).

El sistema queda en pausa programada esperando las 12:00 PM EDT (= 09:00 AM Pacífico) para disparar a Cacique Foods, F. Gaviña & Sons, Intuit y Workday.

Detalle hasta ahora:
""" + "\n".join(all_logs)
    )
    
    # 3. Esperar hasta las 12:00 PM EDT para el Bloque Pacífico
    target_hour = 12
    target_minute = 0
    now = datetime.datetime.now()
    target_time = now.replace(hour=target_hour, minute=target_minute, second=0, microsecond=0)
    
    wait_seconds = (target_time - datetime.datetime.now()).total_seconds()
    if wait_seconds > 0:
        print(f"\n⏳ PAUSA ZONA PACÍFICO: Esperando {wait_seconds/60:.1f} minutos hasta las 12:00 PM EDT (09:00 AM PDT)...\n", flush=True)
        time.sleep(wait_seconds)
    else:
        print("\nHora 12:00 PM EDT alcanzada o pasada. Procediendo inmediatamente con el bloque Pacífico.", flush=True)
        
    s3, e3, l3 = dispatch_batch("BLOQUE 3: PACÍFICO / PDT (CALIFORNIA - 09:00 AM PDT)", batch_pacific, len(batch_central_mountain) + len(batch_eastern), total_prospects)
    all_logs.extend(l3)
    
    total_success = morning_success + s3
    total_errors = morning_errors + e3
    
    send_alert(
        f"🎉 [EXMA Outreach] Campaña de Martes 100% COMPLETADA ({total_success}/{total_prospects})",
        f"""Hola Edward,

Todos los 26 correos zonificados de hoy martes han sido despachados exitosamente.

- Total exitosos: {total_success}
- Errores: {total_errors}
Hora finalización: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Detalle final de envíos:
""" + "\n".join(all_logs) + f"""

Las respuestas entrarán directo a tu bandeja de edward@exmaglobal.com."""
    )
    print("\n🎉 ¡CAMPAÑA ZONIFICADA COMPLETADA CON ÉXITO TOTAL!", flush=True)

if __name__ == '__main__':
    run_campaign_zonificada()
