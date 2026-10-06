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

log_file_path = '/Users/ejimenezsys/Desktop/sitiosweb/agencia/campaign_lunes_seguimiento.log'
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

# 25 PROSPECTOS CONFIRMADOS DEL MARTES 29 DE SEPTIEMBRE
prospects = [{'asunto': '2.500 líderes hispanos en Miami. Una sola marca de electrónica.', 'cuerpo': 'Hola Jennie:\n\nEl comprador hispano está sobreindexado en adopción de tecnología en Estados Unidos. En diciembre hay 2.500 de ellos, y son quienes deciden las compras tecnológicas en sus empresas y hogares.\n\nEl 4 y 5 de diciembre, EXMA reúne en Downtown Event Center, Fort Lauderdale (área de Miami) a 2.500 líderes hispanos.\n\nTrabajamos con exclusividad por categoría. En electrónica y retail tecnológico, solo habrá una marca en el escenario.\n\n¿Tiene 15 minutos esta semana o la próxima?\n\nSaludos,\n\nEdward Jiménez\nPartner Relationship Manager · EXMA Global\nedward@exmaglobal.com\nexmaglobal.com/miami', 'destinatario': 'Jennie Weber', 'email': 'jennie.weber@bestbuy.com', 'empresa': 'Best Buy Co', 'location': 'Richfield, MN', 'tipo': 'VALID', 'tz': 'CDT'}, {'asunto': '2.500 líderes hispanos en Miami. Una sola marca de cerveza.', 'cuerpo': 'Hola Jim:\n\nModelo Especial y Corona son, en la práctica, la cerveza de referencia de esta comunidad en Estados Unidos.\n\nEl 4 y 5 de diciembre, EXMA reúne en Downtown Event Center, Fort Lauderdale (área de Miami) a 2.500 líderes, emprendedores y profesionales hispanos.\n\nTrabajamos con exclusividad por categoría. En cerveza, habrá una sola marca en el escenario y en las experiencias VIP del evento.\n\n¿Tiene 15 minutos esta semana o la próxima para conversar?\n\nSaludos,\n\nEdward Jiménez\nPartner Relationship Manager · EXMA Global\nedward@exmaglobal.com\nexmaglobal.com/miami', 'destinatario': 'Jim Sabia', 'email': 'jim.sabia@cbrands.com', 'empresa': 'Constellation Brands', 'location': 'Chicago, IL', 'tipo': 'VALID', 'tz': 'CDT'}, {'asunto': '2.500 líderes hispanos en Miami. Una sola marca de retail.', 'cuerpo': 'Hola William:\n\nWalmart lleva años construyendo una relación sólida y auténtica con el comprador hispano. Le propongo el lugar donde ese comprador no solo compra, sino que se reúne a hacer negocios y liderar.\n\nEl 4 y 5 de diciembre, EXMA reúne en Downtown Event Center, Fort Lauderdale (área de Miami) a 2.500 líderes y emprendedores hispanos.\n\nTrabajamos con exclusividad por categoría. En retail, solo habrá una marca en el escenario.\n\n¿Tiene 15 minutos esta semana o la próxima para conversar?\n\nSaludos,\n\nEdward Jiménez\nPartner Relationship Manager · EXMA Global\nedward@exmaglobal.com\nexmaglobal.com/miami', 'destinatario': 'William White', 'email': 'william.white@walmart.com', 'empresa': 'Walmart Inc.', 'location': 'Bentonville, AR', 'tipo': 'VALID', 'tz': 'CDT'}, {'asunto': '2.500 líderes hispanos en Miami. Una sola institución de inversiones.', 'cuerpo': 'Hola Lisa:\n\nLa comunidad de inversionistas y emprendedores hispanos en Estados Unidos crece a un ritmo superior a la media nacional en apertura de cuentas patrimoniales.\n\nEl 4 y 5 de diciembre, EXMA reúne en Downtown Event Center, Fort Lauderdale (área de Miami) a 2.500 líderes hispanos.\n\nTrabajamos con exclusividad por categoría. En servicios de inversión y gestión patrimonial, solo habrá una marca en el escenario.\n\n¿Tiene 15 minutos esta semana o la próxima?\n\nSaludos,\n\nEdward Jiménez\nPartner Relationship Manager · EXMA Global\nedward@exmaglobal.com\nexmaglobal.com/miami', 'destinatario': 'Lisa Ross', 'email': 'lisa.ross@schwab.com', 'empresa': 'Charles Schwab', 'location': 'Westlake, TX', 'tipo': 'CATCH_ALL', 'tz': 'CDT'}, {'asunto': '2.500 líderes hispanos en Miami. Una sola marca de snacks.', 'cuerpo': 'Hola Mie-Leng:\n\nMondelēz creció en este mercado a punta de entender y acompañar al consumidor hispano en cada momento de consumo.\n\nEl 4 y 5 de diciembre, EXMA reúne en Downtown Event Center, Fort Lauderdale (área de Miami) a 2.500 líderes hispanos. Esta es la sala donde ese consumidor decide y lidera.\n\nTrabajamos con exclusividad por categoría. En snacks y galletas, solo habrá una marca en el escenario.\n\n¿Tiene 15 minutos esta semana o la próxima?\n\nSaludos,\n\nEdward Jiménez\nPartner Relationship Manager · EXMA Global\nedward@exmaglobal.com\nexmaglobal.com/miami', 'destinatario': 'Mie-Leng Wong', 'email': 'mie-leng.wong@mdlz.com', 'empresa': 'Mondelēz International', 'location': 'Chicago, IL', 'tipo': 'CATCH_ALL', 'tz': 'CDT'}, {'asunto': '2.500 líderes hispanos en Miami. Una sola marca automotriz.', 'cuerpo': 'Hola Marisstella:\n\nEl comprador hispano es de los segmentos más leales y de mayor crecimiento en el sector automotriz en Estados Unidos.\n\nEl 4 y 5 de diciembre, EXMA reúne en Downtown Event Center, Fort Lauderdale (área de Miami) a 2.500 líderes hispanos.\n\nTrabajamos con exclusividad por categoría. En automotriz, habrá una sola marca oficial en el escenario y en la exhibición exterior del evento.\n\n¿Tiene 15 minutos esta semana o la próxima para conversar?\n\nSaludos,\n\nEdward Jiménez\nPartner Relationship Manager · EXMA Global\nedward@exmaglobal.com\nexmaglobal.com/miami', 'destinatario': 'Marisstella Marinkovic', 'email': 'marisstella.marinkovic@nissan-usa.com', 'empresa': 'Nissan North America', 'location': 'Franklin, TN', 'tipo': 'CATCH_ALL', 'tz': 'CDT'}, {'asunto': '2.500 líderes hispanos en Miami. Una sola marca de alimentos.', 'cuerpo': 'Hola Diana:\n\nEl consumidor hispano es uno de los mayores motores de volumen y crecimiento en alimentos y condimentos en Estados Unidos.\n\nEl 4 y 5 de diciembre, EXMA reúne en Downtown Event Center, Fort Lauderdale (área de Miami) a 2.500 líderes y familias hispanas.\n\nTrabajamos con exclusividad por categoría. En alimentos empacados, solo habrá una marca en el escenario.\n\n¿Tiene 15 minutos esta semana o la próxima para conversar?\n\nSaludos,\n\nEdward Jiménez\nPartner Relationship Manager · EXMA Global\nedward@exmaglobal.com\nexmaglobal.com/miami', 'destinatario': 'Diana Frost', 'email': 'diana.frost@kraftheinz.com', 'empresa': 'The Kraft Heinz Company', 'location': 'Chicago, IL', 'tipo': 'CATCH_ALL', 'tz': 'CDT'}, {'asunto': '2.500 líderes hispanos en Miami. Una sola marca de servicios financieros transfronterizos.', 'cuerpo': 'Hola Devin:\n\nWestern Union existe y ha crecido de la mano de esta comunidad. En diciembre está reunida en un solo lugar, a minutos de las principales rutas financieras de las Américas.\n\nEl 4 y 5 de diciembre, EXMA reúne en Downtown Event Center, Fort Lauderdale (área de Miami) a 2.500 líderes, empresarios y profesionales hispanos.\n\nTrabajamos con exclusividad por categoría. En servicios transfronterizos y pagos, solo habrá una marca en el escenario.\n\n¿Tiene 15 minutos esta semana o la próxima para conversar?\n\nSaludos,\n\nEdward Jiménez\nPartner Relationship Manager · EXMA Global\nedward@exmaglobal.com\nexmaglobal.com/miami', 'destinatario': 'Devin McGranahan', 'email': 'devin.mcgranahan@westernunion.com', 'empresa': 'Western Union', 'location': 'Denver, CO', 'tipo': 'CATCH_ALL', 'tz': 'MDT'}, {'asunto': 'Bacardi nació para nuestra comunidad. Queremos que esté en su escenario.', 'cuerpo': 'Hola Ned:\n\nBacardi lleva más de un siglo siendo la historia de una familia que empezó de nuevo y construyó algo global desde el Caribe. Esa es literalmente la historia que vamos a poner en un escenario en diciembre.\n\nEl 4 y 5 de diciembre, EXMA reúne en Downtown Event Center, Fort Lauderdale (área de Miami) a 2.500 líderes, emprendedores y profesionales hispanos.\n\nSé que su rol es global y que esto es una activación regional en el sur de Florida. ¿Me podría indicar con quién hablar del equipo de Bacardi en Coral Gables? Con mucho gusto le escribo directamente.\n\nUn abrazo,\n\nEdward Jiménez\nPartner Relationship Manager · EXMA Global\nedward@exmaglobal.com\nexmaglobal.com/miami', 'destinatario': 'Ned Duggan', 'email': 'nduggan@bacardi.com', 'empresa': 'Bacardi USA', 'location': 'Miami/Coral Gables, FL', 'tipo': 'VALID', 'tz': 'EDT'}, {'asunto': 'La comunidad de doers hispanos más grande de Estados Unidos', 'cuerpo': 'Hola Scott:\n\nDeloitte publica año tras año sobre el poder de compra hispano en Estados Unidos. En diciembre esa audiencia no va a estar en un informe: va a estar en una sala.\n\nDeloitte apoya a quienes emprenden, innovan y crecen. Nosotros reunimos exactamente a esas personas, en español y con alma latina.\n\nEl 4 y 5 de diciembre, EXMA reúne en Downtown Event Center, Fort Lauderdale (área de Miami) a 2.500 líderes hispanos: emprendedores, profesionales y dueños de negocio. Dos días de marketing, innovación, estrategia, inversiones y finanzas para una comunidad que no deja de crecer.\n\nBuscamos una sola marca por categoría que se convierta en la que impulsa ese crecimiento: en el escenario, en el contenido y en la comunidad que sigue viva después del evento.\n\n¿Tiene 15 minutos esta semana o la próxima para contarle cómo lo imaginamos para Deloitte?\n\nSaludos,\n\nEdward Jiménez\nPartner Relationship Manager · EXMA Global\nedward@exmaglobal.com\nexmaglobal.com/miami', 'destinatario': 'Scott Mager', 'email': 'smager@deloitte.com', 'empresa': 'Deloitte US', 'location': 'New York, NY', 'tipo': 'VALID', 'tz': 'EDT'}, {'asunto': '2.500 líderes hispanos en Miami. Una sola marca de licores.', 'cuerpo': 'Hola Cristina:\n\nEl consumidor hispano es de los que más crece en su categoría en Estados Unidos, tanto en marcas icónicas como Don Julio y Casamigos como en el portafolio global de Diageo.\n\nSé que su equipo invierte en llegarle al consumidor hispano. Le propongo algo que un anuncio no puede dar: estar en la sala.\n\nEl 4 y 5 de diciembre, EXMA reúne en Downtown Event Center, Fort Lauderdale (área de Miami) a 2.500 líderes, emprendedores y profesionales hispanos.\n\nTrabajamos con exclusividad por categoría. En licores, solo habrá una marca en el escenario, en la experiencia y en el contenido del evento.\n\nSi aún tiene presupuesto de cierre de año para comunidad o experiencias, es un buen momento para conversar. ¿Tiene 15 minutos esta semana o la próxima?\n\nSaludos,\n\nEdward Jiménez\nPartner Relationship Manager · EXMA Global\nedward@exmaglobal.com\nexmaglobal.com/miami', 'destinatario': 'Cristina Diezhandino', 'email': 'cristina.diezhandino@diageo.com', 'empresa': 'Diageo North America', 'location': 'New York, NY', 'tipo': 'VALID', 'tz': 'EDT'}, {'asunto': '2.500 líderes hispanos en Miami. Una sola marca de café.', 'cuerpo': 'Hola Katie:\n\nCafé Bustelo es de las pocas marcas grandes que esta comunidad siente como propia en cada hogar latino de Florida y de todo Estados Unidos.\n\nSé que su equipo invierte en llegarle al consumidor hispano. Le propongo algo que un anuncio no puede dar: estar en la sala.\n\nEl 4 y 5 de diciembre, EXMA reúne en Downtown Event Center, Fort Lauderdale (área de Miami) a 2.500 líderes hispanos y dueños de negocio.\n\nTrabajamos con exclusividad por categoría. En café, solo habrá una marca en el escenario y en la experiencia del evento.\n\n¿Tiene 15 minutos esta semana o la próxima para conversar?\n\nSaludos,\n\nEdward Jiménez\nPartner Relationship Manager · EXMA Global\nedward@exmaglobal.com\nexmaglobal.com/miami', 'destinatario': 'Katie Williams', 'email': 'katie.williams@jmsmucker.com', 'empresa': 'The J.M. Smucker Co. (Café Bustelo)', 'location': 'Orrville, OH', 'tipo': 'VALID', 'tz': 'EDT'}, {'asunto': '2.500 líderes hispanos en Miami. Una sola marca de restaurantes.', 'cuerpo': 'Hola Tom:\n\nBurger King tiene su casa en Miami y su consumidor hispano es central para el negocio. Los dos coinciden el 4 y 5 de diciembre a minutos de su sede central.\n\nEXMA reúne en Downtown Event Center, Fort Lauderdale (área de Miami) a 2.500 líderes y profesionales hispanos.\n\nTrabajamos con exclusividad por categoría. En restaurantes de servicio rápido, solo habrá una marca en el escenario y en el contenido.\n\n¿Tiene 15 minutos esta semana o la próxima para conversar?\n\nSaludos,\n\nEdward Jiménez\nPartner Relationship Manager · EXMA Global\nedward@exmaglobal.com\nexmaglobal.com/miami', 'destinatario': 'Tom Curtis', 'email': 'tcurtis@rbi.com', 'empresa': 'Burger King (Restaurant Brands International)', 'location': 'Miami, FL', 'tipo': 'VALID', 'tz': 'EDT'}, {'asunto': '2.500 líderes hispanos en Miami. Una sola naviera en el escenario.', 'cuerpo': 'Hola Christine:\n\nCarnival es de Miami como pocas marcas. En diciembre la ciudad reúne a 2.500 líderes hispanos, y el viajero hispano es de los segmentos familiares que más rápido crece para la industria de cruceros.\n\nEl 4 y 5 de diciembre, EXMA reúne en Downtown Event Center, Fort Lauderdale (área de Miami) a esta comunidad.\n\nTrabajamos con exclusividad por categoría. En cruceros, solo habrá una marca en el escenario y en la experiencia.\n\n¿Tiene 15 minutos esta semana o la próxima?\n\nSaludos,\n\nEdward Jiménez\nPartner Relationship Manager · EXMA Global\nedward@exmaglobal.com\nexmaglobal.com/miami', 'destinatario': 'Christine Duffy', 'email': 'cduffy@carnival.com', 'empresa': 'Carnival Cruise Line', 'location': 'Miami, FL', 'tipo': 'VALID', 'tz': 'EDT'}, {'asunto': '2.500 líderes hispanos en Miami. Una sola marca de bebidas.', 'cuerpo': 'Hola Troy:\n\nCoke Florida embotella justo en el estado donde la población hispana crece más rápido y con mayor poder de compra. Ese consumidor y sus empleadores van a estar reunidos en una sala en diciembre.\n\nEl 4 y 5 de diciembre, EXMA reúne en Downtown Event Center, Fort Lauderdale (área de Miami) a 2.500 líderes hispanos.\n\nTrabajamos con exclusividad por categoría. En bebidas, solo habrá una marca en el escenario y en la hidratación oficial del evento.\n\n¿Tiene 15 minutos esta semana o la próxima?\n\nSaludos,\n\nEdward Jiménez\nPartner Relationship Manager · EXMA Global\nedward@exmaglobal.com\nexmaglobal.com/miami', 'destinatario': 'Troy Taylor', 'email': 'ttaylor@cocacolaflorida.com', 'empresa': 'Coca-Cola Beverages Florida', 'location': 'Tampa, FL', 'tipo': 'VALID', 'tz': 'EDT'}, {'asunto': '2.500 líderes hispanos en Miami. Una sola marca de cuidado personal.', 'cuerpo': 'Hola Carolina:\n\nSu liderazgo en marketing multicultural refleja exactamente lo que es esta sala: Latinoamérica y Estados Unidos reunidos en un mismo lugar de alto impacto.\n\nEl 4 y 5 de diciembre, EXMA reúne en Downtown Event Center, Fort Lauderdale (área de Miami) a 2.500 líderes hispanos.\n\nTrabajamos con exclusividad por categoría. En cuidado personal y salud oral, solo habrá una marca en el escenario.\n\n¿Tiene 15 minutos esta semana o la próxima?\n\nSaludos,\n\nEdward Jiménez\nPartner Relationship Manager · EXMA Global\nedward@exmaglobal.com\nexmaglobal.com/miami', 'destinatario': 'Carolina Incognito', 'email': 'carolina_incognito@colpal.com', 'empresa': 'Colgate-Palmolive', 'location': 'New York, NY', 'tipo': 'VALID', 'tz': 'EDT'}, {'asunto': '2.500 líderes hispanos en Miami. Una sola marca de restaurantes.', 'cuerpo': 'Hola Lindsay:\n\nEl crecimiento de su categoría en el sur de Estados Unidos pasa por el consumidor hispano y la lealtad de marca familiar. En diciembre esa audiencia está en una sola sala.\n\nEl 4 y 5 de diciembre, EXMA reúne en Downtown Event Center, Fort Lauderdale (área de Miami) a 2.500 líderes hispanos.\n\nTrabajamos con exclusividad por categoría. En restaurantes de servicio rápido, solo habrá una marca en el escenario.\n\n¿Tiene 15 minutos esta semana o la próxima?\n\nSaludos,\n\nEdward Jiménez\nPartner Relationship Manager · EXMA Global\nedward@exmaglobal.com\nexmaglobal.com/miami', 'destinatario': 'Lindsay Radkoski', 'email': 'lindsay.radkoski@wendys.com', 'empresa': "The Wendy's Company", 'location': 'Dublin, OH', 'tipo': 'VALID', 'tz': 'EDT'}, {'asunto': 'La comunidad de doers hispanos más grande de Estados Unidos', 'cuerpo': 'Hola Antonia:\n\nEscribo en español a propósito: es el idioma de los 2.500 líderes de negocio que se reúnen en Miami en diciembre, y de un mercado que su firma ya analiza de cerca.\n\nPwC apoya a quienes emprenden, innovan y crecen. Nosotros reunimos exactamente a esas personas, en español y con alma latina.\n\nEl 4 y 5 de diciembre, EXMA reúne en Downtown Event Center, Fort Lauderdale (área de Miami) a 2.500 líderes hispanos.\n\nBuscamos una sola marca por categoría que impulse ese crecimiento en el escenario y en la comunidad.\n\n¿Tiene 15 minutos esta semana o la próxima para contarle cómo lo imaginamos para PwC?\n\nSaludos,\n\nEdward Jiménez\nPartner Relationship Manager · EXMA Global\nedward@exmaglobal.com\nexmaglobal.com/miami', 'destinatario': 'Antonia Wade', 'email': 'antonia.wade@pwc.com', 'empresa': 'PwC US', 'location': 'New York, NY', 'tipo': 'CATCH_ALL', 'tz': 'EDT'}, {'asunto': '2.500 líderes hispanos en Miami. Una sola marca de energía.', 'cuerpo': 'Hola Kimberly:\n\nSu equipo de relaciones con la comunidad trabaja el sur de Florida todos los días. Esto es esa comunidad empresarial y profesional, concentrada en dos días.\n\nEl 4 y 5 de diciembre, EXMA reúne en Downtown Event Center, Fort Lauderdale (área de Miami) a 2.500 líderes hispanos.\n\nTrabajamos con exclusividad por categoría. En energía y sostenibilidad, solo habrá una marca en el escenario.\n\n¿Tiene 15 minutos esta semana o la próxima para conversar?\n\nSaludos,\n\nEdward Jiménez\nPartner Relationship Manager · EXMA Global\nedward@exmaglobal.com\nexmaglobal.com/miami', 'destinatario': 'Kimberly Blair', 'email': 'kimberly.blair@fpl.com', 'empresa': 'Florida Power & Light (FPL / NextEra Energy)', 'location': 'Juno Beach, FL', 'tipo': 'CATCH_ALL', 'tz': 'EDT'}, {'asunto': '2.500 líderes hispanos en Miami. Una sola aseguradora de vida y patrimonio.', 'cuerpo': 'Hola Amy:\n\nNew York Life tiene una de las trayectorias más profundas sirviendo a familias empresarias y profesionales hispanos en protección financiera.\n\nEl 4 y 5 de diciembre, EXMA reúne en Downtown Event Center, Fort Lauderdale (área de Miami) a 2.500 tomadores de decisión hispanos.\n\nTrabajamos con exclusividad por categoría. En seguros de vida y patrimonio, solo habrá una marca en el escenario.\n\n¿Tiene 15 minutos esta semana o la próxima?\n\nSaludos,\n\nEdward Jiménez\nPartner Relationship Manager · EXMA Global\nedward@exmaglobal.com\nexmaglobal.com/miami', 'destinatario': 'Amy Hu', 'email': 'amy_hu@newyorklife.com', 'empresa': 'New York Life Insurance Company', 'location': 'New York, NY', 'tipo': 'CATCH_ALL', 'tz': 'EDT'}, {'asunto': '2.500 líderes hispanos en Miami. Una sola marca de consumo masivo.', 'cuerpo': 'Hola Marc:\n\nP&G ha sido de las compañías más explícitas y consistentes del país sobre representación cultural y apoyo a la comunidad hispana.\n\nEl 4 y 5 de diciembre, EXMA reúne en Downtown Event Center, Fort Lauderdale (área de Miami) a 2.500 líderes hispanos. Hay un escenario donde esa conversación ocurre en español y con acción real.\n\nTrabajamos con exclusividad por categoría. Nos encantaría explorar si P&G tiene espacio para estar presente.\n\n¿Tiene su equipo 15 minutos esta semana o la próxima?\n\nSaludos,\n\nEdward Jiménez\nPartner Relationship Manager · EXMA Global\nedward@exmaglobal.com\nexmaglobal.com/miami', 'destinatario': 'Marc Pritchard', 'email': 'pritchard.m@pg.com', 'empresa': 'Procter & Gamble (P&G)', 'location': 'Cincinnati, OH', 'tipo': 'CATCH_ALL', 'tz': 'EDT'}, {'asunto': 'Cacique nació para nuestra comunidad. Queremos que esté en su escenario.', 'cuerpo': 'Hola Pedro:\n\nVi su llegada a Cacique el año pasado después de Mondelēz. Tomar una marca familiar hispana y llevarla a otra escala es un tipo de reto distinto al de una multinacional, y es justo la conversación que vamos a tener en diciembre.\n\nCacique es de esas marcas que nacieron aquí para servir a nuestra gente. Por eso le escribo.\n\nEl 4 y 5 de diciembre, EXMA reúne en Downtown Event Center, Fort Lauderdale (área de Miami) a 2.500 líderes, emprendedores y profesionales hispanos.\n\nEstamos invitando a una sola marca por categoría. Nos encantaría que en su categoría fuera Cacique.\n\n¿Tiene 15 minutos esta semana o la próxima?\n\nUn abrazo,\n\nEdward Jiménez\nPartner Relationship Manager · EXMA Global\nedward@exmaglobal.com\nexmaglobal.com/miami', 'destinatario': 'Pedro Silveira', 'email': 'psilveira@caciqueinc.com', 'empresa': 'Cacique Foods', 'location': 'Monrovia, CA', 'tipo': 'VALID', 'tz': 'PDT'}, {'asunto': 'Gaviña nació para nuestra comunidad. Queremos que esté en su escenario.', 'cuerpo': 'Hola Leonor:\n\nVi el lanzamiento de las cápsulas reciclables de Café La Llave. Que una marca que empezó con una familia cubana llegando a Los Ángeles esté hoy marcando la pauta en su categoría es exactamente la historia que nos interesa contar.\n\nGaviña es de esas marcas que nacieron aquí para servir a nuestra gente. Por eso le escribo.\n\nEl 4 y 5 de diciembre, EXMA reúne en Downtown Event Center, Fort Lauderdale (área de Miami) a 2.500 líderes, emprendedores y profesionales hispanos. Es el primer gran evento de una plataforma que celebra a hispanos ordinarios haciendo cosas extraordinarias.\n\nEstamos invitando a una sola marca por categoría. Nos encantaría que en café fuera Gaviña.\n\n¿Tiene 15 minutos esta semana o la próxima?\n\nUn abrazo,\n\nEdward Jiménez\nPartner Relationship Manager · EXMA Global\nedward@exmaglobal.com\nexmaglobal.com/miami', 'destinatario': 'Leonor Gaviña-Valls', 'email': 'leonor.gavina@gavina.com', 'empresa': 'F. Gaviña & Sons (Café La Llave)', 'location': 'Vernon, CA', 'tipo': 'VALID', 'tz': 'PDT'}, {'asunto': 'La comunidad de doers hispanos más grande de Estados Unidos', 'cuerpo': 'Hola Thomas:\n\nQuickBooks vive de los dueños de negocio pequeños, y el segmento que más rápido crece en ese universo es el hispano. En diciembre hay 2.500 de ellos en una sala.\n\nIntuit apoya a quienes emprenden, innovan y crecen. Nosotros reunimos exactamente a esas personas, en español y con alma latina.\n\nEl 4 y 5 de diciembre, EXMA reúne en Downtown Event Center, Fort Lauderdale (área de Miami) a 2.500 líderes hispanos: emprendedores, profesionales y dueños de negocio. Dos días de marketing, innovación, estrategia, inversiones y finanzas para una comunidad que no deja de crecer.\n\nBuscamos una sola marca por categoría que se convierta en la que impulsa ese crecimiento: en el escenario, en el contenido y en la comunidad que sigue viva después del evento.\n\n¿Tiene 15 minutos esta semana o la próxima para contarle cómo lo imaginamos para Intuit?\n\nSaludos,\n\nEdward Jiménez\nPartner Relationship Manager · EXMA Global\nedward@exmaglobal.com\nexmaglobal.com/miami', 'destinatario': 'Thomas Ranese', 'email': 'thomas_ranese@intuit.com', 'empresa': 'Intuit', 'location': 'Mountain View, CA', 'tipo': 'VALID', 'tz': 'PDT'}, {'asunto': 'La comunidad de doers hispanos más grande de Estados Unidos', 'cuerpo': 'Hola Emma:\n\nEl 54% de los asistentes a EXMA Miami son corporativos y el resto emprendedores. Es, literalmente, la sala de sus dos compradores a la vez.\n\nWorkday apoya a quienes emprenden, innovan y crecen. Nosotros reunimos exactamente a esas personas, en español y con alma latina.\n\nEl 4 y 5 de diciembre, EXMA reúne en Downtown Event Center, Fort Lauderdale (área de Miami) a 2.500 líderes hispanos.\n\n¿Tiene 15 minutos esta semana o la próxima para contarle cómo lo imaginamos para Workday?\n\nSaludos,\n\nEdward Jiménez\nPartner Relationship Manager · EXMA Global\nedward@exmaglobal.com\nexmaglobal.com/miami', 'destinatario': 'Emma Chalwin', 'email': 'emma.chalwin@workday.com', 'empresa': 'Workday', 'location': 'Pleasanton, CA', 'tipo': 'CATCH_ALL', 'tz': 'PDT'}]


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

def generate_followup_body(p):
    first_name = p['destinatario'].split()[0]
    asunto_orig = p['asunto']
    cuerpo_orig = p['cuerpo']
    empresa = p['empresa']
    
    # Extraer categoría si es posible del asunto
    cat = 'su sector'
    if 'electrónica' in asunto_orig: cat = 'tecnología y electrónica para el hogar'
    elif 'cerveza' in asunto_orig: cat = 'cerveza y bebidas'
    elif 'retail' in asunto_orig: cat = 'retail y consumo'
    elif 'inversiones' in asunto_orig: cat = 'servicios de inversión y patrimonio'
    elif 'snacks' in asunto_orig: cat = 'snacks y confitería'
    elif 'automotriz' in asunto_orig: cat = 'la industria automotriz'
    elif 'alimentos' in asunto_orig: cat = 'alimentos'
    elif 'servicios financieros' in asunto_orig: cat = 'servicios financieros transfronterizos'
    elif 'licores' in asunto_orig: cat = 'espirituosos y licores'
    elif 'café' in asunto_orig: cat = 'café tradicional y de consumo'
    elif 'restaurantes' in asunto_orig: cat = 'restaurantes y hospitalidad'
    elif 'naviera' in asunto_orig: cat = 'cruceros y turismo'
    elif 'bebidas' in asunto_orig: cat = 'bebidas y refrescos'
    elif 'cuidado personal' in asunto_orig: cat = 'cuidado personal y del hogar'
    elif 'energía' in asunto_orig: cat = 'energía e infraestructura'
    elif 'aseguradora' in asunto_orig: cat = 'seguros de vida y patrimonio'
    elif 'consumo masivo' in asunto_orig: cat = 'consumo masivo'
    
    body = f"""Hola {first_name}:

Quería asegurarme de que mi correo de la semana pasada no se hubiera traspapelado entre sus pendientes.

Como le mencionaba, el 4 y 5 de diciembre reunimos en Miami (Downtown Event Center, Fort Lauderdale) a 2.500 líderes, ejecutivos y empresarios hispanos en la cumbre EXMA Miami 2026.

Trabajamos con exclusividad de una sola marca por categoría. En {cat}, queremos confirmar si {empresa} tiene interés en liderar esa presencia en el escenario y en los espacios del evento antes de avanzar conversaciones con otros aliados del sector.

¿Tiene 15 minutos este jueves o viernes para una breve llamada?

Saludos cordiales,

{signature}

--- Mensaje original ---
De: Edward Jiménez · EXMA Global <edward@exmaglobal.com>
Fecha: 29 de septiembre de 2026
Asunto: {asunto_orig}
Para: {p['destinatario']} <{p['email']}>

{cuerpo_orig}"""
    return body

def run_followup_campaign(dry_run=False):
    total = len(prospects)
    print(f"==================================================")
    print(f"🚀 INICIANDO TOQUE 2 (SEGUIMIENTO 4 DÍAS HÁBILES)")
    print(f"Total prospectos a contactar: {total}")
    print(f"Modo: {'SIMULACIÓN (DRY RUN)' if dry_run else 'ENVÍO EN VIVO'}")
    print(f"Hora actual: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"==================================================")

    if not dry_run:
        send_alert("🚀 [EXMA Outreach] Arrancó el Toque 2 de Seguimiento (25 correos)", 
                   f"Iniciando el seguimiento a 4 días hábiles para los 25 prospectos del Martes 29-Sep.")

    server = None
    if not dry_run:
        server = get_smtp_connection()

    success = 0
    errors = 0
    sent_list = []

    for idx, p in enumerate(prospects, 1):
        to_email = p['email'].strip()
        nombre_dest = p['destinatario'].strip()
        empresa = p['empresa'].strip()
        subject_reply = f"RE: {p['asunto']}"
        body = generate_followup_body(p)

        if dry_run:
            print(f"[{idx}/{total}] [SIMULADO] {nombre_dest} ({empresa}) <{to_email}>")
            print(f"    Asunto: {subject_reply}")
            print(f"    Primeras 2 líneas: {body.splitlines()[0]} | {body.splitlines()[2][:60]}...")
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
                print(f"[{idx}/{total}] ✅ {timestamp} [SEGUIMIENTO TOQUE 2] ENVIADO: {nombre_dest} ({empresa}) <{to_email}>", flush=True)
                success += 1
                sent_ok = True
                sent_list.append((empresa, nombre_dest, to_email))
                break
            except Exception as e:
                print(f"⚠️ Reintentando conexión SMTP para {to_email}... ({e})", flush=True)
                try:
                    server = get_smtp_connection()
                    server.sendmail(u, [to_email], msg.as_string())
                    print(f"[{idx}/{total}] ✅ {timestamp} [REINTENTO OK] ENVIADO: {nombre_dest} ({empresa}) <{to_email}>", flush=True)
                    success += 1
                    sent_ok = True
                    sent_list.append((empresa, nombre_dest, to_email))
                    break
                except Exception as e2:
                    print(f"[{idx}/{total}] ❌ {timestamp} ERROR con {to_email}: {e2}", flush=True)

        if sent_ok:
            update_databases_on_followup(empresa, to_email)
        else:
            errors += 1

        if idx < total:
            wait_s = random.randint(60, 90)
            print(f"   ⏳ Pausa humana anti-spam: esperando {wait_s}s antes del siguiente...", flush=True)
            time.sleep(wait_s)

    if server:
        try: server.quit()
        except: pass

    if not dry_run:
        summary_msg = f"Campaña de Seguimiento finalizada: {success}/{total}. Errores: {errors}."
        send_alert(f"🎉 [EXMA Outreach] Toque 2 COMPLETADO ({success}/{total})", summary_msg)
    print(f"Finalizado: {success}/{total} enviados. Errores: {errors}")

if __name__ == "__main__":
    dry = "--dry-run" in sys.argv
    run_followup_campaign(dry_run=dry)
